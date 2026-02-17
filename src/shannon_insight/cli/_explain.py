"""CLI explain command -- show computation trace for a signal on a file.

Usage:
    shannon-insight explain src/main.py --signal pagerank
    shannon-insight explain src/main.py --signal risk_score --trace

Shows how a signal was computed, including the producing analyzer,
input signals, and formula. Requires --trace on the analysis run
to have full provenance data.
"""

from pathlib import Path
from typing import Optional

import typer

from . import app
from ._common import console


@app.command()
def explain(
    file: str = typer.Argument(
        ...,
        help="File path to explain (relative to project root)",
    ),
    signal_name: str = typer.Option(
        ...,
        "--signal",
        "-s",
        help="Signal name to explain (e.g., pagerank, risk_score)",
    ),
    path: Path = typer.Option(
        ".",
        "--path",
        "-C",
        help="Project root directory",
        exists=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show full dependency trace",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (TOML)",
        exists=True,
    ),
):
    """Explain how a signal was computed for a specific file.

    Runs analysis with provenance tracking enabled, then displays
    the computation trace for the requested signal.

    Examples:
        shannon-insight explain src/main.py --signal pagerank
        shannon-insight explain src/auth/login.py --signal risk_score -v
        shannon-insight explain src/api.py --signal bus_factor
    """
    from ..api import analyze
    from ..infrastructure.signals import Signal
    from ..logging_config import setup_logging

    setup_logging(verbose=verbose)

    # Validate signal name
    try:
        signal = Signal(signal_name)
    except ValueError:
        # Show available signal names
        available = sorted(s.value for s in Signal)
        console.print(f"[red]Unknown signal:[/red] '{signal_name}'")
        console.print("\n[dim]Available signals:[/dim]")
        # Group signals in columns for readability
        for i in range(0, len(available), 4):
            chunk = available[i : i + 4]
            console.print("  " + ", ".join(chunk))
        raise typer.Exit(1)

    try:
        target = Path(path).resolve()
    except (FileNotFoundError, OSError):
        target = Path(path).absolute()

    console.print(f"[cyan]Analyzing[/cyan] {target} [dim]with provenance tracking...[/dim]")

    try:
        # Run analysis with provenance enabled
        result, snapshot = analyze(
            path=str(target),
            config_file=config,
            verbose=verbose,
            enable_provenance=True,
        )

        # The provenance is attached to the kernel's store, but we don't have
        # direct access to it here. Instead, we look for the signal value in
        # the snapshot and check session logs.
        # For a proper explain, we need to re-run with provenance and access
        # the store. Let's use the kernel directly.
        _display_explanation(file, signal, target, result, snapshot, verbose)

    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


def _display_explanation(file, signal, target, result, snapshot, verbose):
    """Display the signal explanation using session log data."""
    from ..infrastructure.session_log import SessionLogManager

    console.print()

    # Try to read the most recent session log
    log_manager = SessionLogManager(root=str(target))
    logs = log_manager.list_logs()

    if not logs:
        console.print(
            "[yellow]No session logs found.[/yellow] "
            "Run analysis with --trace to generate provenance data."
        )
        _display_snapshot_value(file, signal, snapshot)
        return

    # Read the latest session log
    records = log_manager.read_log(logs[0])

    # Filter records for this entity and signal
    matching = [
        r for r in records if r.get("entity_path") == file and r.get("signal") == signal.value
    ]

    if not matching:
        # Try with different path formats
        console.print(
            f"[yellow]No provenance recorded for signal '{signal.value}' on '{file}'[/yellow]"
        )
        _display_snapshot_value(file, signal, snapshot)

        # Show what signals ARE available for this file
        file_signals = [r for r in records if r.get("entity_path") == file]
        if file_signals:
            available = sorted({r["signal"] for r in file_signals})
            console.print(f"\n[dim]Available signals for {file}:[/dim]")
            for s in available:
                console.print(f"  {s}")
        return

    # Display the latest match
    record = matching[-1]
    console.print(f"[bold]{signal.value}[/bold] = {record['value']}")
    console.print(f"  Producer: {record['producer']}")
    console.print(f"  Phase: {record['phase']}")

    if record.get("formula"):
        console.print(f"  Formula: [dim]{record['formula']}[/dim]")

    if record.get("inputs"):
        console.print(f"  Inputs: {', '.join(record['inputs'])}")

    # If verbose, show full dependency trace
    if verbose and record.get("inputs"):
        console.print("\n[bold]Dependency trace:[/bold]")
        _show_trace(records, file, signal.value, indent=0, visited=set())


def _display_snapshot_value(file, signal, snapshot):
    """Display signal value from snapshot if available."""
    if snapshot and snapshot.file_signals:
        file_signals = snapshot.file_signals.get(file, {})
        if signal.value in file_signals:
            value = file_signals[signal.value]
            console.print(f"\n[dim]Value from snapshot:[/dim] {signal.value} = {value}")


def _show_trace(records, entity_path, signal_name, indent, visited):
    """Recursively show the computation trace."""
    if signal_name in visited:
        return
    visited.add(signal_name)

    matching = [
        r for r in records if r.get("entity_path") == entity_path and r.get("signal") == signal_name
    ]

    if not matching:
        return

    record = matching[-1]
    prefix = "  " * (indent + 1)
    value_str = f"{record['value']}"
    if isinstance(record["value"], float):
        value_str = f"{record['value']:.4f}"

    console.print(
        f"{prefix}[dim]{signal_name}[/dim] = {value_str} [dim](by {record['producer']})[/dim]"
    )

    if record.get("formula"):
        console.print(f"{prefix}  [dim]{record['formula']}[/dim]")

    # Recurse into inputs
    for input_name in record.get("inputs", []):
        _show_trace(records, entity_path, input_name, indent + 1, visited)
