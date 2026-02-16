"""Main analysis command - simplified and clean."""

from pathlib import Path
from typing import Optional

import typer

from ..api import analyze
from ..logging_config import setup_logging
from . import app
from ._common import console


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
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in machine-readable JSON format",
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
        help="Exit 1 if findings meet threshold: high | medium | any",
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
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
    ),
):
    """
    Analyze codebase quality using multi-signal structural analysis.

    Combines dependency graphs, git history, and per-file signals to produce
    prioritized, evidence-backed findings.

    Examples:
        shannon-insight
        shannon-insight /path/to/code
        shannon-insight --verbose --max-findings 100
        shannon-insight --json --fail-on high
    """
    # Handle version
    if version:
        from .. import __version__
        console.print(f"Shannon Insight v{__version__}")
        raise typer.Exit(0)

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

    try:
        # Run analysis using new API
        result, snapshot = analyze(
            path=str(target),
            config_file=config,
            verbose=verbose,
            workers=workers,
            max_findings=max_findings,
        )

        # Output results
        if json_output:
            _output_json(result, snapshot)
        else:
            _output_rich(result, snapshot, verbose=verbose)

        # Handle fail-on threshold for CI/CD
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
            }
            for f in result.findings
        ],
        "summary": {
            "total_files": snapshot.metadata.total_files,
            "total_findings": len(result.findings),
        },
    }
    console.print(json.dumps(output, indent=2))


def _output_rich(result, snapshot, verbose: bool = False):
    """Output results in rich text format."""
    from rich.table import Table

    console.print()
    console.print(
        f"[bold cyan]Analysis Complete[/bold cyan] - "
        f"{snapshot.metadata.total_files} files analyzed"
    )
    console.print()

    if not result.findings:
        console.print("[green]✓ No significant issues found[/green]")
        return

    console.print(f"[yellow]Found {len(result.findings)} findings:[/yellow]\n")

    for i, finding in enumerate(result.findings, 1):
        severity_color = "red" if finding.severity > 0.7 else "yellow"
        console.print(
            f"[{severity_color}]{i}. {finding.title}[/{severity_color}]"
        )
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
