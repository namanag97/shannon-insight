"""Insights CLI command — actionable findings from cross-referencing signals."""

import json
import sys
from pathlib import Path
from typing import List, Optional

import typer

from . import app
from ._common import console, resolve_settings
from ..diff.scope import (
    ChangeScopedReport,
    build_scoped_report,
    get_changed_files,
    get_merge_base_files,
)
from ..insights import InsightKernel, InsightResult, Finding
from ..logging_config import setup_logging
from ..exceptions import ShannonInsightError
from ..snapshot.models import FindingRecord, Snapshot
from ..storage import HistoryDB
from ..storage.writer import save_snapshot


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
    save: bool = typer.Option(
        True, "--save/--no-save",
        help="Save analysis snapshot to .shannon/ history",
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
    scope: Optional[str] = typer.Option(
        None, "--scope",
        help="Focus on files changed since ref (e.g., HEAD~1, abc1234)",
    ),
    pr: bool = typer.Option(
        False, "--pr",
        help="PR mode: focus on files changed vs base branch",
    ),
    base_branch: str = typer.Option(
        "main", "--base-branch",
        help="Base branch for --pr mode",
    ),
    fail_on: Optional[str] = typer.Option(
        None, "--fail-on",
        help="Exit 1 if condition met: 'new' (new findings), 'high' (severity>0.8), 'any' (any finding)",
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

      shannon-insight . insights --scope HEAD~3

      shannon-insight . insights --pr --base-branch develop

      shannon-insight . insights --pr --fail-on high
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

        # Determine if we are in scoped mode
        scoped_mode = scope is not None or pr

        if scoped_mode:
            # ── Scoped analysis path ──────────────────────────────────
            repo_path = str(Path(path).resolve())

            # Determine changed files
            if pr:
                changed_files = get_merge_base_files(repo_path, base_branch)
            else:
                # scope is not None here (checked via scoped_mode)
                changed_files = get_changed_files(repo_path, scope)  # type: ignore[arg-type]

            if not changed_files:
                console.print(
                    "[yellow]No changed files detected.[/yellow] "
                    "Check the ref or branch name."
                )
                raise typer.Exit(0)

            # Run full analysis (we need the complete snapshot for context)
            result, snapshot = kernel.run_and_capture(max_findings=max_findings)

            # Persist snapshot if requested
            if save and settings.enable_history:
                _save_snapshot(repo_path, snapshot, logger)

            # Build change-scoped report
            report = build_scoped_report(changed_files, snapshot)

            if fmt == "json":
                _output_scoped_json(report, result)
            else:
                _output_scoped_rich(report, result, verbose=verbose)

            # Check fail-on condition for scoped mode
            if fail_on is not None:
                should_fail = _check_fail_condition_scoped(fail_on, report)
                if should_fail:
                    raise typer.Exit(1)

        else:
            # ── Full analysis path ────────────────────────────────────
            if save and settings.enable_history:
                result, snapshot = kernel.run_and_capture(
                    max_findings=max_findings,
                )
                _save_snapshot(str(Path(path).resolve()), snapshot, logger)
            else:
                result = kernel.run(max_findings=max_findings)

            if fmt == "json":
                _output_json(result)
            else:
                _output_rich(result, verbose=verbose)

            # Check fail-on condition for full mode
            if fail_on is not None:
                should_fail = _check_fail_condition_full(fail_on, result)
                if should_fail:
                    raise typer.Exit(1)

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


# ---------------------------------------------------------------------------
# Snapshot persistence helper
# ---------------------------------------------------------------------------


def _save_snapshot(repo_path: str, snapshot: Snapshot, logger) -> None:
    """Save snapshot to .shannon/ history database."""
    try:
        with HistoryDB(repo_path) as db:
            sid = save_snapshot(db.conn, snapshot)
            logger.info(f"Snapshot saved (id={sid})")
    except Exception as e:
        logger.warning(f"Failed to save snapshot: {e}")


# ---------------------------------------------------------------------------
# Fail-on condition checkers
# ---------------------------------------------------------------------------


def _check_fail_condition_full(fail_on: str, result: InsightResult) -> bool:
    """Check if the fail-on condition is met for full (unscoped) analysis.

    Parameters
    ----------
    fail_on:
        Condition string: ``"any"``, ``"new"``, or ``"high"``.
    result:
        The insight result from the full analysis.

    Returns
    -------
    bool
        True if the condition is met and the CLI should exit with code 1.
    """
    if fail_on == "any" and result.findings:
        console.print(
            f"[red]--fail-on any:[/red] {len(result.findings)} finding(s) detected"
        )
        return True
    if fail_on == "new" and result.findings:
        # In full mode without history comparison, "new" acts like "any"
        console.print(
            f"[red]--fail-on new:[/red] {len(result.findings)} finding(s) detected"
        )
        return True
    if fail_on == "high":
        high_findings = [f for f in result.findings if f.severity > 0.8]
        if high_findings:
            console.print(
                f"[red]--fail-on high:[/red] "
                f"{len(high_findings)} high-severity finding(s) detected"
            )
            return True
    return False


def _check_fail_condition_scoped(
    fail_on: str, report: ChangeScopedReport
) -> bool:
    """Check if the fail-on condition is met for scoped analysis.

    Parameters
    ----------
    fail_on:
        Condition string: ``"any"``, ``"new"``, or ``"high"``.
    report:
        The change-scoped report.

    Returns
    -------
    bool
        True if the condition is met and the CLI should exit with code 1.
    """
    all_scoped = report.direct_findings + report.blast_findings

    if fail_on == "any" and all_scoped:
        console.print(
            f"[red]--fail-on any:[/red] "
            f"{len(all_scoped)} finding(s) in change scope"
        )
        return True
    if fail_on == "new" and report.direct_findings:
        console.print(
            f"[red]--fail-on new:[/red] "
            f"{len(report.direct_findings)} finding(s) directly involve changed files"
        )
        return True
    if fail_on == "high":
        high_findings = [f for f in all_scoped if f.severity > 0.8]
        if high_findings:
            console.print(
                f"[red]--fail-on high:[/red] "
                f"{len(high_findings)} high-severity finding(s) in change scope"
            )
            return True
        if report.risk_level == "critical":
            console.print(
                f"[red]--fail-on high:[/red] "
                f"risk level is critical: {report.risk_reason}"
            )
            return True
    return False


# ---------------------------------------------------------------------------
# Full analysis output (original)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Scoped analysis output
# ---------------------------------------------------------------------------


_RISK_COLORS = {
    "low": "green",
    "medium": "yellow",
    "high": "red",
    "critical": "bold red",
}


def _output_scoped_json(report: ChangeScopedReport, result: InsightResult):
    """Machine-readable JSON output for a change-scoped report."""
    summary = result.store_summary
    output = {
        "mode": "scoped",
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
        "scope": {
            "changed_files": report.changed_files,
            "blast_radius_files": report.blast_radius_files,
            "blast_radius_count": len(report.blast_radius_files),
            "risk_level": report.risk_level,
            "risk_reason": report.risk_reason,
        },
        "direct_findings": [
            _finding_record_to_dict(f) for f in report.direct_findings
        ],
        "blast_findings": [
            _finding_record_to_dict(f) for f in report.blast_findings
        ],
        "file_risk": [
            {
                "filepath": fr.filepath,
                "signals": {k: round(v, 4) for k, v in fr.signals.items()},
                "percentiles": {k: round(v, 1) for k, v in fr.percentiles.items()},
                "dependents_count": fr.dependents_count,
                "findings_count": fr.findings_count,
            }
            for fr in report.file_risk
        ],
    }
    print(json.dumps(output, indent=2))


def _finding_record_to_dict(f: FindingRecord) -> dict:
    """Convert a FindingRecord to a JSON-serializable dict."""
    return {
        "type": f.finding_type,
        "identity_key": f.identity_key,
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


def _output_scoped_rich(
    report: ChangeScopedReport,
    result: InsightResult,
    verbose: bool = False,
):
    """Human-readable Rich terminal output for a change-scoped report."""
    summary = result.store_summary
    console.print()

    # ── Header ────────────────────────────────────────────────────────
    console.print(
        f"[bold cyan]SHANNON INSIGHT[/bold cyan] \u2014 "
        f"[bold]Change-Scoped Analysis[/bold]"
    )
    parts = [f"[bold]{summary.total_files}[/bold] files"]
    if summary.total_modules:
        parts.append(f"[bold]{summary.total_modules}[/bold] modules")
    if summary.commits_analyzed:
        parts.append(f"[bold]{summary.commits_analyzed}[/bold] commits")
    console.print(f"  Full codebase: {', '.join(parts)} analyzed")
    console.print()

    # ── Risk level banner ─────────────────────────────────────────────
    risk_color = _RISK_COLORS.get(report.risk_level, "white")
    console.print(
        f"  Risk Level: [{risk_color}]{report.risk_level.upper()}[/{risk_color}]"
    )
    console.print(f"  [dim]{report.risk_reason}[/dim]")
    console.print()

    # ── Changed files ─────────────────────────────────────────────────
    console.print(
        f"  [bold]Changed files:[/bold] {len(report.changed_files)}"
    )
    for fp in report.changed_files:
        console.print(f"    [dim]\u2022[/dim] {fp}")
    console.print()

    # ── Blast radius ──────────────────────────────────────────────────
    if report.blast_radius_files:
        console.print(
            f"  [bold]Blast radius:[/bold] "
            f"{len(report.blast_radius_files)} additional file(s) affected"
        )
        if verbose:
            for fp in report.blast_radius_files:
                console.print(f"    [dim]\u2022[/dim] {fp}")
        else:
            # Show up to 5 files with an ellipsis
            shown = report.blast_radius_files[:5]
            for fp in shown:
                console.print(f"    [dim]\u2022[/dim] {fp}")
            remaining = len(report.blast_radius_files) - len(shown)
            if remaining > 0:
                console.print(
                    f"    [dim]... and {remaining} more "
                    f"(use --verbose to show all)[/dim]"
                )
        console.print()

    # ── Per-file risk summaries ───────────────────────────────────────
    if verbose and report.file_risk:
        console.print("  [bold]Per-file risk:[/bold]")
        for fr in report.file_risk:
            dep_str = (
                f"{fr.dependents_count} dependent(s)"
                if fr.dependents_count
                else "no dependents"
            )
            finding_str = (
                f"{fr.findings_count} finding(s)"
                if fr.findings_count
                else "no findings"
            )
            console.print(
                f"    [bold]{fr.filepath}[/bold] "
                f"\u2014 {dep_str}, {finding_str}"
            )
            # Show top 3 highest-percentile signals
            if fr.percentiles:
                top_signals = sorted(
                    fr.percentiles.items(),
                    key=lambda kv: kv[1],
                    reverse=True,
                )[:3]
                for sig_name, pct in top_signals:
                    val = fr.signals.get(sig_name, 0.0)
                    console.print(
                        f"      [dim]{sig_name}={val:.4f} "
                        f"(p{pct:.0f})[/dim]"
                    )
        console.print()

    # ── Direct findings ───────────────────────────────────────────────
    if report.direct_findings:
        console.print(
            f"  [bold red]Direct findings "
            f"({len(report.direct_findings)}):[/bold red] "
            f"involve changed files"
        )
        console.print()
        for i, finding in enumerate(report.direct_findings):
            _render_finding_record(finding, verbose, i + 1)
    else:
        console.print(
            "  [bold green]No findings directly involve changed files.[/bold green]"
        )
        console.print()

    # ── Blast findings ────────────────────────────────────────────────
    if report.blast_findings:
        console.print(
            f"  [bold yellow]Blast radius findings "
            f"({len(report.blast_findings)}):[/bold yellow] "
            f"involve files in the blast radius"
        )
        console.print()
        for i, finding in enumerate(report.blast_findings):
            _render_finding_record(finding, verbose, i + 1)

    # ── Summary footer ────────────────────────────────────────────────
    total_scoped = len(report.direct_findings) + len(report.blast_findings)
    console.print(
        f"[dim]{total_scoped} scoped finding(s) from "
        f"{len(report.changed_files)} changed file(s) "
        f"(blast radius: {len(report.blast_radius_files)} file(s)).[/dim]"
    )
    if not verbose:
        console.print(
            "[dim]Use --verbose for per-file risk details "
            "and full blast radius.[/dim]"
        )
    console.print()


def _render_finding_record(
    finding: FindingRecord, verbose: bool, index: int,
):
    """Render a single FindingRecord (from the snapshot layer)."""
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

    label = type_labels.get(finding.finding_type, finding.finding_type.upper())
    color = type_colors.get(finding.finding_type, "white")

    # Header: number + type label
    console.print(
        f"  [bold {color}]{index}. {label}[/bold {color}]"
    )

    # File(s) involved
    if len(finding.files) == 2:
        console.print(
            f"     [bold]{finding.files[0]}[/bold] "
            f"\u2194 [bold]{finding.files[1]}[/bold]"
        )
    elif len(finding.files) > 2:
        console.print(f"     [bold]{finding.files[0]}[/bold]")
        for f in finding.files[1:]:
            console.print(f"     [bold]{f}[/bold]")
    else:
        console.print(f"     [bold]{finding.files[0]}[/bold]")

    # Evidence: one line per piece, plain English
    for e in finding.evidence:
        console.print(f"     [dim]\u2022[/dim] {e.description}")

    # Verbose: raw signal values
    if verbose:
        for e in finding.evidence:
            pct_str = f", p{e.percentile:.0f}" if e.percentile > 0 else ""
            console.print(
                f"       [dim]{e.signal}={e.value:.4f}{pct_str}[/dim]"
            )

    # Suggestion
    suggestion_lines = finding.suggestion.split("\n")
    console.print(f"     [green]\u2192 {suggestion_lines[0]}[/green]")
    for line in suggestion_lines[1:]:
        console.print(f"     [green]  {line}[/green]")

    console.print()
