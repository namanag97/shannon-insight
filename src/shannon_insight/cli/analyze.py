"""Main analysis command — unified through InsightKernel."""

import json
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Optional

import click
import typer

from ..diff.scope import (
    ChangeScopedReport,
    build_scoped_report,
    get_changed_files,
)
from ..exceptions import ShannonInsightError
from ..insights import Finding, InsightKernel, InsightResult
from ..logging_config import setup_logging
from ..snapshot.models import FindingRecord, Snapshot
from ..storage import HistoryDB
from ..storage.writer import save_snapshot
from . import app
from ._common import console, resolve_settings

# ---------------------------------------------------------------------------
# Auto-detect changed ref helper
# ---------------------------------------------------------------------------


def _auto_detect_changed_ref(repo_path: str) -> str:
    """Detect the right comparison ref based on current branch."""
    try:
        branch = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        return "HEAD~1"

    if branch in ("main", "master", "HEAD"):
        return "HEAD~1"

    # On a feature branch: find merge-base with main or master
    for default in ("main", "master"):
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "merge-base", "HEAD", default],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            continue

    return "HEAD~1"


# ---------------------------------------------------------------------------
# Grouped finding display configuration
# ---------------------------------------------------------------------------


def _hub_oneliner(finding: Finding) -> str:
    blast = next(
        (e for e in finding.evidence if "affected" in e.description.lower() or "blast" in e.signal),
        None,
    )
    importers = next(
        (e for e in finding.evidence if "import" in e.description.lower()),
        None,
    )
    if blast:
        return blast.description
    if importers:
        return importers.description
    return finding.title


def _god_oneliner(finding: Finding) -> str:
    desc = next(
        (
            e
            for e in finding.evidence
            if "function" in e.description.lower() or "complex" in e.description.lower()
        ),
        None,
    )
    return desc.description if desc else finding.title


def _coupling_oneliner(finding: Finding) -> str:
    cochange = next(
        (e for e in finding.evidence if "changed" in e.description.lower()),
        None,
    )
    files_str = " \u2194 ".join(finding.files)
    return f"{files_str} \u2014 {cochange.description}" if cochange else files_str


def _boundary_oneliner(finding: Finding) -> str:
    cluster = next(
        (
            e
            for e in finding.evidence
            if "cluster" in e.description.lower() or "distinct" in e.description.lower()
        ),
        None,
    )
    return cluster.description if cluster else finding.title


def _unstable_oneliner(finding: Finding) -> str:
    return finding.evidence[0].description if finding.evidence else finding.title


def _dead_dep_oneliner(finding: Finding) -> str:
    return (
        " \u2192 ".join(finding.files)
        + " \u2014 "
        + (finding.evidence[0].description if finding.evidence else "never co-changed")
    )


FINDING_DISPLAY = {
    "high_risk_hub": {
        "label": "HIGH RISK HUBS",
        "color": "red",
        "summary": "These files have many dependents. A bug ripples widely.",
        "suggestion": "Split into smaller modules or add interfaces to reduce coupling.",
        "oneliner": _hub_oneliner,
    },
    "god_file": {
        "label": "GOD FILES",
        "color": "magenta",
        "summary": "These files are complex and unfocused \u2014 too many responsibilities.",
        "suggestion": "Extract clusters of related functions into separate modules.",
        "oneliner": _god_oneliner,
    },
    "hidden_coupling": {
        "label": "HIDDEN COUPLING",
        "color": "yellow",
        "summary": "These file pairs always change together but share no import.",
        "suggestion": "Make the dependency explicit or extract shared logic.",
        "oneliner": _coupling_oneliner,
    },
    "boundary_mismatch": {
        "label": "BOUNDARY MISMATCHES",
        "color": "cyan",
        "summary": "These directories don't match actual dependency patterns.",
        "suggestion": "Reorganize files to match how they're actually connected.",
        "oneliner": _boundary_oneliner,
    },
    "unstable_file": {
        "label": "UNSTABLE FILES",
        "color": "yellow",
        "summary": "These files keep changing without stabilizing.",
        "suggestion": "Stabilize the interface or split volatile parts.",
        "oneliner": _unstable_oneliner,
    },
    "dead_dependency": {
        "label": "DEAD DEPENDENCIES",
        "color": "dim",
        "summary": "These imports exist but the files never actually change together.",
        "suggestion": "Verify the import is still needed; remove if dead.",
        "oneliner": _dead_dep_oneliner,
    },
}

MAX_FILES_PER_GROUP = 5


# ---------------------------------------------------------------------------
# Main callback
# ---------------------------------------------------------------------------


@app.callback(invoke_without_command=True, no_args_is_help=False)
def main(
    ctx: typer.Context,
    path: Optional[Path] = typer.Option(
        None,
        "-C",
        "--path",
        help="Project root to analyze (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    changed: bool = typer.Option(
        False,
        "--changed",
        help="Scope to files changed on this branch (auto-detects base)",
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Scope to files changed since a git ref (e.g. HEAD~3, abc123)",
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
        help="Show detailed evidence per finding",
    ),
    save: bool = typer.Option(
        False,
        "--save",
        help="Save snapshot to .shannon/ for history tracking",
    ),
    fail_on: Optional[str] = typer.Option(
        None,
        "--fail-on",
        help="Exit 1 if findings meet threshold: any | high",
        click_type=click.Choice(["any", "high"], case_sensitive=False),
    ),
    config: Optional[Path] = typer.Option(
        None,
        "-c",
        "--config",
        help="Configuration file (TOML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        hidden=True,
    ),
    workers: Optional[int] = typer.Option(
        None,
        "-w",
        "--workers",
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
    Analyze codebase quality using structural, temporal, and spectral analysis.

    Cross-references dependency graphs, git history, per-file quality signals,
    and spectral analysis to produce prioritized, evidence-backed findings.

    Works with or without git. Without git, temporal findings are skipped.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight

      shannon-insight --json

      shannon-insight --verbose

      shannon-insight --changed

      shannon-insight -C /path/to/project --json --fail-on high
    """
    # Store resolved path in context for subcommands
    target = Path(path) if path else Path.cwd()
    ctx.ensure_object(dict)
    ctx.obj["path"] = target

    if ctx.invoked_subcommand is not None:
        return

    from .. import __version__

    if version:
        console.print(
            f"[bold cyan]Shannon Insight[/bold cyan] version [green]{__version__}[/green]"
        )
        raise typer.Exit(0)

    logger = setup_logging(verbose=verbose)

    try:
        settings = resolve_settings(
            config=config,
            no_cache=False,
            workers=workers,
            verbose=verbose,
        )

        kernel = InsightKernel(
            str(target),
            language="auto",
            settings=settings,
        )

        max_findings = settings.insights_max_findings

        # Determine if we are in scoped mode
        scoped_mode = since is not None or changed

        if scoped_mode:
            # -- Scoped analysis path --
            repo_path = str(target.resolve())

            if since:
                changed_files = get_changed_files(repo_path, since)
            elif changed:
                ref = _auto_detect_changed_ref(repo_path)
                changed_files = get_changed_files(repo_path, ref)
            else:
                changed_files = []

            if not changed_files:
                console.print(
                    "[yellow]No changed files detected.[/yellow] Check the ref or branch name."
                )
                raise typer.Exit(0)

            result, snapshot = kernel.run(max_findings=max_findings)

            if save and settings.enable_history:
                _save_snapshot(repo_path, snapshot, logger)

            report = build_scoped_report(changed_files, snapshot)

            if json_output:
                _output_scoped_json(report, result)
            else:
                _output_scoped_rich(report, result, verbose=verbose)

            if fail_on is not None:
                should_fail = _check_fail_condition_scoped(fail_on, report)
                if should_fail:
                    raise typer.Exit(1)

        else:
            # -- Full analysis path --
            result, snapshot = kernel.run(max_findings=max_findings)

            if save and settings.enable_history:
                _save_snapshot(str(target.resolve()), snapshot, logger)

            if json_output:
                _output_json(result)
            else:
                _output_rich(result, verbose=verbose)

            if fail_on is not None:
                should_fail = _check_fail_condition_full(fail_on, result)
                if should_fail:
                    raise typer.Exit(1)

    except typer.Exit:
        raise

    except ShannonInsightError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        console.print("\n[yellow]Analysis interrupted[/yellow]")
        raise typer.Exit(130)

    except Exception as e:
        logger.exception("Unexpected error during analysis")
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
    """Check if the fail-on condition is met for full (unscoped) analysis."""
    if fail_on == "any" and result.findings:
        console.print(f"[red]--fail-on any:[/red] {len(result.findings)} finding(s) detected")
        return True
    if fail_on == "high":
        high_findings = [f for f in result.findings if f.severity > 0.8]
        if high_findings:
            console.print(
                f"[red]--fail-on high:[/red] {len(high_findings)} high-severity finding(s) detected"
            )
            return True
    return False


def _check_fail_condition_scoped(fail_on: str, report: ChangeScopedReport) -> bool:
    """Check if the fail-on condition is met for scoped analysis."""
    all_scoped = report.direct_findings + report.blast_findings

    if fail_on == "any" and all_scoped:
        console.print(f"[red]--fail-on any:[/red] {len(all_scoped)} finding(s) in change scope")
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
                f"[red]--fail-on high:[/red] risk level is critical: {report.risk_reason}"
            )
            return True
    return False


# ---------------------------------------------------------------------------
# Full analysis output (grouped by finding type)
# ---------------------------------------------------------------------------


def _output_json(result: InsightResult):
    """Machine-readable JSON output."""
    summary = result.store_summary

    # Build grouped structure
    grouped: dict = OrderedDict()
    for f in result.findings:
        grouped.setdefault(f.finding_type, []).append(f)

    output = {
        "summary": {
            "total_files": summary.total_files,
            "total_modules": summary.total_modules,
            "commits_analyzed": summary.commits_analyzed,
            "git_available": summary.git_available,
            "fiedler_value": (
                round(summary.fiedler_value, 4) if summary.fiedler_value is not None else None
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
        "grouped": {
            ftype: [
                {
                    "type": f.finding_type,
                    "severity": round(f.severity, 3),
                    "title": f.title,
                    "files": f.files,
                }
                for f in findings
            ]
            for ftype, findings in grouped.items()
        },
    }
    print(json.dumps(output, indent=2))


def _output_rich(result: InsightResult, verbose: bool = False):
    """Human-readable Rich terminal output — findings grouped by type."""
    summary = result.store_summary
    console.print()

    # Header
    parts = [f"[bold]{summary.total_files}[/bold] files"]
    if summary.total_modules:
        parts.append(f"[bold]{summary.total_modules}[/bold] modules")
    if summary.commits_analyzed:
        parts.append(f"[bold]{summary.commits_analyzed}[/bold] commits")
    console.print(f"[bold cyan]SHANNON INSIGHT[/bold cyan] \u2014 {', '.join(parts)} analyzed")

    if not summary.git_available:
        console.print(
            "  [dim]No git history \u2014 "
            "temporal findings (hidden coupling, unstable files) skipped[/dim]"
        )

    console.print()

    if not result.findings:
        console.print("[bold green]No significant findings.[/bold green]")
        console.print()
        return

    # Group findings by type
    groups: dict = OrderedDict()
    for f in result.findings:
        groups.setdefault(f.finding_type, []).append(f)

    # Render each group
    for ftype, findings in groups.items():
        display = FINDING_DISPLAY.get(
            ftype,
            {
                "label": ftype.upper().replace("_", " ") + "S",
                "color": "white",
                "summary": "",
                "suggestion": findings[0].suggestion if findings else "",
                "oneliner": lambda f: f.title,
            },
        )

        color = display["color"]
        count = len(findings)
        console.print(
            f"[bold {color}]{display['label']}[/bold {color}] "
            f"\u2014 {count} file{'s' if count != 1 else ''}"
        )
        if display["summary"]:
            console.print(f"  [dim]{display['summary']}[/dim]")
        console.print()

        shown = findings[:MAX_FILES_PER_GROUP]
        for f in shown:
            file_label = f.files[0] if len(f.files) == 1 else " \u2194 ".join(f.files)
            oneliner = display["oneliner"](f)
            console.print(f"  {file_label}")
            console.print(f"    {oneliner}")

            if verbose:
                for e in f.evidence:
                    pct_str = f", p{e.percentile:.0f}" if e.percentile > 0 else ""
                    console.print(f"    [dim]{e.signal}={e.value:.4f}{pct_str}[/dim]")

        remaining = count - MAX_FILES_PER_GROUP
        if remaining > 0:
            console.print(f"  [dim]... and {remaining} more[/dim]")

        console.print(f"\n  [italic]\u2192 {display['suggestion']}[/italic]")
        console.print()

    total = sum(len(fs) for fs in groups.values())
    console.print(f"{total} finding{'s' if total != 1 else ''} from {summary.total_files} files.")
    console.print("[dim]Run 'shannon-insight explain <file>' for details.[/dim]")
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
                round(summary.fiedler_value, 4) if summary.fiedler_value is not None else None
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
        "direct_findings": [_finding_record_to_dict(f) for f in report.direct_findings],
        "blast_findings": [_finding_record_to_dict(f) for f in report.blast_findings],
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

    console.print(
        "[bold cyan]SHANNON INSIGHT[/bold cyan] \u2014 [bold]Change-Scoped Analysis[/bold]"
    )
    parts = [f"[bold]{summary.total_files}[/bold] files"]
    if summary.total_modules:
        parts.append(f"[bold]{summary.total_modules}[/bold] modules")
    if summary.commits_analyzed:
        parts.append(f"[bold]{summary.commits_analyzed}[/bold] commits")
    console.print(f"  Full codebase: {', '.join(parts)} analyzed")
    console.print()

    risk_color = _RISK_COLORS.get(report.risk_level, "white")
    console.print(f"  Risk Level: [{risk_color}]{report.risk_level.upper()}[/{risk_color}]")
    console.print(f"  [dim]{report.risk_reason}[/dim]")
    console.print()

    console.print(f"  [bold]Changed files:[/bold] {len(report.changed_files)}")
    for fp in report.changed_files:
        console.print(f"    [dim]\u2022[/dim] {fp}")
    console.print()

    if report.blast_radius_files:
        console.print(
            f"  [bold]Blast radius:[/bold] "
            f"{len(report.blast_radius_files)} additional file(s) affected"
        )
        if verbose:
            for fp in report.blast_radius_files:
                console.print(f"    [dim]\u2022[/dim] {fp}")
        else:
            shown = report.blast_radius_files[:5]
            for fp in shown:
                console.print(f"    [dim]\u2022[/dim] {fp}")
            remaining = len(report.blast_radius_files) - len(shown)
            if remaining > 0:
                console.print(
                    f"    [dim]... and {remaining} more (use --verbose to show all)[/dim]"
                )
        console.print()

    if verbose and report.file_risk:
        console.print("  [bold]Per-file risk:[/bold]")
        for fr in report.file_risk:
            dep_str = (
                f"{fr.dependents_count} dependent(s)" if fr.dependents_count else "no dependents"
            )
            finding_str = f"{fr.findings_count} finding(s)" if fr.findings_count else "no findings"
            console.print(f"    [bold]{fr.filepath}[/bold] \u2014 {dep_str}, {finding_str}")
            if fr.percentiles:
                top_signals = sorted(
                    fr.percentiles.items(),
                    key=lambda kv: kv[1],
                    reverse=True,
                )[:3]
                for sig_name, pct in top_signals:
                    val = fr.signals.get(sig_name, 0.0)
                    console.print(f"      [dim]{sig_name}={val:.4f} (p{pct:.0f})[/dim]")
        console.print()

    # Group scoped findings
    all_scoped_findings = report.direct_findings + report.blast_findings
    if all_scoped_findings:
        console.print(f"  [bold]Findings in scope ({len(all_scoped_findings)}):[/bold]")
        console.print()
        for i, finding in enumerate(all_scoped_findings):
            _render_finding_record(finding, verbose, i + 1)
    else:
        console.print("  [bold green]No findings involve changed files.[/bold green]")
        console.print()

    total_scoped = len(all_scoped_findings)
    console.print(
        f"[dim]{total_scoped} scoped finding(s) from "
        f"{len(report.changed_files)} changed file(s) "
        f"(blast radius: {len(report.blast_radius_files)} file(s)).[/dim]"
    )
    if not verbose:
        console.print("[dim]Use --verbose for per-file risk details and full blast radius.[/dim]")
    console.print()


def _render_finding_record(
    finding: FindingRecord,
    verbose: bool,
    index: int,
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

    console.print(f"  [bold {color}]{index}. {label}[/bold {color}]")

    if len(finding.files) == 2:
        console.print(
            f"     [bold]{finding.files[0]}[/bold] \u2194 [bold]{finding.files[1]}[/bold]"
        )
    elif len(finding.files) > 2:
        console.print(f"     [bold]{finding.files[0]}[/bold]")
        for f in finding.files[1:]:
            console.print(f"     [bold]{f}[/bold]")
    else:
        console.print(f"     [bold]{finding.files[0]}[/bold]")

    for e in finding.evidence:
        console.print(f"     [dim]\u2022[/dim] {e.description}")

    if verbose:
        for e in finding.evidence:
            pct_str = f", p{e.percentile:.0f}" if e.percentile > 0 else ""
            console.print(f"       [dim]{e.signal}={e.value:.4f}{pct_str}[/dim]")

    suggestion_lines = finding.suggestion.split("\n")
    console.print(f"     [green]\u2192 {suggestion_lines[0]}[/green]")
    for line in suggestion_lines[1:]:
        console.print(f"     [green]  {line}[/green]")

    console.print()
