"""Main analysis command - simplified and clean."""

from pathlib import Path
from typing import Optional

import typer

from ..api import analyze
from ..logging_config import setup_logging
from . import app
from ._common import console


def _version_callback(value: bool) -> None:
    """Handle --version flag (eager callback)."""
    if value:
        from .. import __version__

        console.print(f"Shannon Insight v{__version__}")
        raise typer.Exit(0)


@app.callback(invoke_without_command=True, no_args_is_help=False)
def main(
    ctx: typer.Context,
    path: Path = typer.Argument(
        ".",
        help="Project root to analyze (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    cli: bool = typer.Option(
        False,
        "--cli",
        help="Output to terminal instead of opening dashboard",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in machine-readable JSON format (implies --cli)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    max_findings: int = typer.Option(
        50,
        "--max-findings",
        "-n",
        help="Maximum findings to return",
        min=1,
        max=500,
    ),
    fail_on: Optional[str] = typer.Option(
        None,
        "--fail-on",
        help="Exit 1 if findings meet threshold: high | medium | any (implies --cli)",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (TOML)",
        exists=True,
    ),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Parallel workers (default: auto-detect)",
        min=1,
        max=32,
        hidden=True,
    ),
    port: int = typer.Option(
        8765,
        "--port",
        "-p",
        help="Port for dashboard server",
    ),
    no_browser: bool = typer.Option(
        False,
        "--no-browser",
        help="Don't open browser automatically",
    ),
    trace: bool = typer.Option(
        False,
        "--trace",
        help="Enable provenance tracking for signal computation",
    ),
    save: bool = typer.Option(
        False,
        "--save",
        help="Save snapshot to .shannon/history.db for trend tracking",
    ),
    use_facts: bool = typer.Option(
        False,
        "--use-facts",
        help="Enable persistent fact store for caching and identity resolution (.shannon/facts.db)",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    Analyze codebase quality — finds risky files, coupling, team gaps, and dead code.

    [bold]Quick start:[/bold]

        [cyan]shannon-insight .[/cyan]              Open interactive dashboard (default)
        [cyan]shannon-insight . --cli[/cyan]        Terminal output, no browser
        [cyan]shannon-insight . --json[/cyan]       JSON output for CI/scripts
        [cyan]shannon-insight . --fail-on high[/cyan]   Exit 1 if high-severity issues exist

    [bold]PATH[/bold] defaults to the current directory. Flags can go before or after PATH:

        shannon-insight --cli .            Works
        shannon-insight . --cli            Also works

    [bold]Common flags:[/bold]

        --cli          Print findings to terminal
        --json         Machine-readable JSON (implies --cli)
        --fail-on      CI gate: [yellow]high[/yellow] | [yellow]medium[/yellow] | [yellow]any[/yellow]
        --no-browser   Start dashboard server without opening browser
        -n 100         Show up to 100 findings (default: 50)
        -v             Verbose output
    """
    # version and help_flag are handled by callbacks

    # Store path in context for subcommands
    ctx.obj = ctx.obj or {}
    try:
        target = Path(path).resolve()
    except (FileNotFoundError, OSError):
        target = Path(path).absolute()
    ctx.obj["path"] = target

    # If subcommand invoked, don't run analysis
    if ctx.invoked_subcommand:
        return

    # Setup logging
    setup_logging(verbose=verbose)

    # Determine mode: --json and --fail-on imply CLI mode
    use_cli = cli or json_output or fail_on

    if use_cli:
        # CLI mode: terminal output
        try:
            result, snapshot = analyze(
                path=str(target),
                config_file=config,
                verbose=verbose,
                workers=workers,
                max_findings=max_findings,
                enable_provenance=trace,
                use_fact_store=use_facts,
            )

            if save:
                _save_snapshot(snapshot, target)

            if json_output:
                _output_json(result, snapshot)
            else:
                _output_rich(result, snapshot, verbose=verbose)

            if fail_on:
                exit_code = _check_fail_threshold(result, fail_on)
                if exit_code != 0:
                    raise typer.Exit(exit_code)

        except KeyboardInterrupt:
            console.print("\n[yellow]Analysis interrupted[/yellow]")
            raise typer.Exit(130)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            if verbose:
                import traceback

                console.print(traceback.format_exc())
            raise typer.Exit(1)
    else:
        # Dashboard mode (default)
        _launch_dashboard(
            target=target,
            config=config,
            workers=workers,
            verbose=verbose,
            port=port,
            no_browser=no_browser,
        )


def _output_json(result, snapshot):
    """Output results in JSON format."""
    import json

    output = {
        "findings": [
            {
                "type": f.finding_type,
                "severity": f.severity,
                "title": f.title,
                "files": f.files,
                "suggestion": f.suggestion,
                "confidence": f.confidence,
                "evidence": [
                    {
                        "signal": e.signal,
                        "value": e.value,
                        "percentile": e.percentile,
                        "description": e.description,
                    }
                    for e in f.evidence
                ],
            }
            for f in result.findings
        ],
        "summary": {
            "total_files": snapshot.file_count,
            "total_findings": len(result.findings),
        },
    }
    # Use print() instead of console.print() to avoid Rich formatting/wrapping
    print(json.dumps(output, indent=2))


def _output_rich(result, snapshot, verbose: bool = False):
    """Output results in rich text format."""

    console.print()
    console.print(
        f"[bold cyan]Analysis Complete[/bold cyan] - {snapshot.file_count} files analyzed"
    )
    console.print()

    if not result.findings:
        console.print("[green]✓ No significant issues found[/green]")
        return

    console.print(f"[yellow]Found {len(result.findings)} findings:[/yellow]\n")

    for i, finding in enumerate(result.findings, 1):
        severity_color = "red" if finding.severity > 0.7 else "yellow"
        console.print(f"[{severity_color}]{i}. {finding.title}[/{severity_color}]")
        console.print(f"   Files: {', '.join(finding.files[:3])}")
        if len(finding.files) > 3:
            console.print(f"   ... and {len(finding.files) - 3} more")
        console.print(f"   Severity: {finding.severity:.2f}")

        if verbose and finding.evidence:
            console.print("   Evidence:")
            for ev in finding.evidence[:3]:
                console.print(f"     - {ev.description}")

        console.print()


def _check_fail_threshold(result, threshold: str) -> int:
    """Check if findings exceed fail threshold.

    Args:
        result: Analysis result
        threshold: 'high', 'medium', or 'any'

    Returns:
        0 if pass, 1 if fail
    """
    if threshold == "any" and result.findings:
        return 1

    if threshold == "high":
        high_findings = [f for f in result.findings if f.severity > 0.7]
        if high_findings:
            console.print(f"[red]Failing: {len(high_findings)} high-severity findings[/red]")
            return 1

    if threshold == "medium":
        medium_findings = [f for f in result.findings if f.severity > 0.4]
        if medium_findings:
            console.print(f"[red]Failing: {len(medium_findings)} medium+ severity findings[/red]")
            return 1

    return 0


def _launch_dashboard(
    target: Path,
    config: Optional[Path],
    workers: Optional[int],
    verbose: bool,
    port: int,
    no_browser: bool,
) -> None:
    """Launch the interactive dashboard."""
    import logging

    # Check dependencies
    try:
        from ..server import _check_deps

        _check_deps()
    except ImportError as exc:
        console.print(f"[red]{exc}[/red]")
        console.print()
        console.print("[dim]Tip: Use --cli for terminal output without server dependencies[/dim]")
        raise typer.Exit(1)

    from ..server.lifecycle import launch_server
    from ._common import resolve_settings

    settings = resolve_settings(config=config, workers=workers, verbose=verbose)

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    launch_server(
        root_dir=str(target),
        settings=settings,
        console=console,
        host="127.0.0.1",
        port=port,
        no_browser=no_browser,
        verbose=verbose,
    )
