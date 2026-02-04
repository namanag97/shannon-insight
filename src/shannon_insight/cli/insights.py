"""Insights CLI command — actionable findings from cross-referencing signals."""

import json
from pathlib import Path
from typing import Optional

import typer

from . import app
from ._common import console, resolve_settings
from ..insights import InsightKernel, InsightResult, Finding
from ..logging_config import setup_logging
from ..exceptions import ShannonInsightError


@app.command()
def insights(
    path: Path = typer.Argument(
        Path("."),
        help="Path to the codebase directory",
        exists=True, file_okay=False, dir_okay=True,
    ),
    language: str = typer.Option(
        "auto", "--language", "-l",
        help="Programming language (auto, python, go, typescript, etc.)",
    ),
    fmt: str = typer.Option(
        "rich", "--format", "-f",
        help="Output format: rich (human-readable) or json",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show full evidence for each finding",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q",
        help="Suppress logging",
    ),
    max_findings: int = typer.Option(
        10, "--max-findings", "-n",
        help="Maximum findings to show",
        min=1, max=50,
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Configuration file (TOML)",
        exists=True, file_okay=True, dir_okay=False,
    ),
    workers: Optional[int] = typer.Option(
        None, "--workers", "-w",
        help="Parallel workers",
        min=1, max=32,
    ),
):
    """
    Actionable codebase insights from structural + temporal analysis.

    Cross-references dependency graphs, git history, per-file quality signals,
    and spectral analysis to produce prioritized, evidence-backed findings.

    Works with or without git. Without git, temporal findings are skipped.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight . insights

      shannon-insight . insights --format json

      shannon-insight . insights --verbose --max-findings 20
    """
    logger = setup_logging(verbose=verbose, quiet=quiet)

    try:
        settings = resolve_settings(
            config=config, no_cache=False,
            workers=workers, verbose=verbose, quiet=quiet,
        )

        kernel = InsightKernel(
            str(path), language=language, settings=settings,
        )
        result = kernel.run(max_findings=max_findings)

        if fmt == "json":
            _output_json(result)
        else:
            _output_rich(result, verbose=verbose)

    except typer.Exit:
        raise
    except ShannonInsightError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


def _output_json(result: InsightResult):
    """Machine-readable JSON output."""
    summary = result.store_summary
    output = {
        "summary": {
            "total_files": summary.total_files,
            "total_modules": summary.total_modules,
            "commits_analyzed": summary.commits_analyzed,
            "git_available": summary.git_available,
            "fiedler_value": (
                round(summary.fiedler_value, 4)
                if summary.fiedler_value is not None
                else None
            ),
            "signals_available": summary.signals_available,
        },
        "findings": [
            {
                "type": f.finding_type,
                "severity": round(f.severity, 3),
                "title": f.title,
                "files": f.files,
                "evidence": [
                    {
                        "signal": e.signal,
                        "value": round(e.value, 4),
                        "percentile": round(e.percentile, 1),
                        "description": e.description,
                    }
                    for e in f.evidence
                ],
                "suggestion": f.suggestion,
            }
            for f in result.findings
        ],
    }
    print(json.dumps(output, indent=2))


def _output_rich(result: InsightResult, verbose: bool = False):
    """Human-readable Rich terminal output."""
    summary = result.store_summary
    console.print()

    # Header
    parts = [f"[bold]{summary.total_files}[/bold] files"]
    if summary.total_modules:
        parts.append(f"[bold]{summary.total_modules}[/bold] modules")
    if summary.commits_analyzed:
        parts.append(f"[bold]{summary.commits_analyzed}[/bold] commits")
    console.print(
        f"[bold cyan]SHANNON INSIGHT[/bold cyan] \u2014 "
        f"{', '.join(parts)} analyzed"
    )

    if not summary.git_available:
        console.print(
            "  [dim]No git history \u2014 "
            "temporal findings (hidden coupling, unstable files) skipped[/dim]"
        )

    if summary.fiedler_value is not None and verbose:
        console.print(
            f"  [dim]Algebraic connectivity (Fiedler): "
            f"{summary.fiedler_value:.4f}[/dim]"
        )

    console.print()

    if not result.findings:
        console.print("[bold green]No significant findings.[/bold green]")
        console.print()
        return

    type_colors = {
        "high_risk_hub": "red",
        "hidden_coupling": "yellow",
        "god_file": "magenta",
        "unstable_file": "yellow",
        "boundary_mismatch": "cyan",
        "dead_dependency": "dim",
    }

    type_labels = {
        "high_risk_hub": "HIGH RISK HUB",
        "hidden_coupling": "HIDDEN COUPLING",
        "god_file": "GOD FILE",
        "unstable_file": "UNSTABLE FILE",
        "boundary_mismatch": "BOUNDARY MISMATCH",
        "dead_dependency": "DEAD DEPENDENCY",
    }

    for i, finding in enumerate(result.findings):
        label = type_labels.get(
            finding.finding_type, finding.finding_type.upper()
        )
        color = type_colors.get(finding.finding_type, "white")
        _render_finding(finding, label, color, verbose, i + 1)

    console.print(
        f"[dim]{len(result.findings)} finding(s) from "
        f"{summary.total_files} files.[/dim]"
    )
    if not verbose:
        console.print(
            "[dim]Use --verbose for raw signal values.[/dim]"
        )
    console.print()


def _render_finding(
    finding: Finding, label: str, color: str, verbose: bool, index: int,
):
    """Render a single finding."""
    # Header: number + type label
    console.print(
        f"[bold {color}]{index}. {label}[/bold {color}]"
    )

    # File(s) involved
    if len(finding.files) == 2:
        console.print(
            f"   [bold]{finding.files[0]}[/bold] "
            f"\u2194 [bold]{finding.files[1]}[/bold]"
        )
    elif len(finding.files) > 2:
        console.print(f"   [bold]{finding.files[0]}[/bold]")
        for f in finding.files[1:]:
            console.print(f"   [bold]{f}[/bold]")
    else:
        console.print(f"   [bold]{finding.files[0]}[/bold]")

    # Evidence: one line per piece, plain English
    for e in finding.evidence:
        console.print(f"   [dim]\u2022[/dim] {e.description}")

    # Verbose: raw signal values
    if verbose:
        for e in finding.evidence:
            pct_str = f", p{e.percentile:.0f}" if e.percentile > 0 else ""
            console.print(
                f"     [dim]{e.signal}={e.value:.4f}{pct_str}[/dim]"
            )

    # Suggestion: the actionable part, clearly separated
    # Handle multi-line suggestions (boundary_mismatch uses \n)
    suggestion_lines = finding.suggestion.split("\n")
    console.print(f"   [green]\u2192 {suggestion_lines[0]}[/green]")
    for line in suggestion_lines[1:]:
        console.print(f"   [green]  {line}[/green]")

    console.print()
