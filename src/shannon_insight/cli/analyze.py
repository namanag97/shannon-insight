"""Main analysis command — unified through InsightKernel."""

import json
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Optional

import click
import typer

from ..exceptions import ShannonInsightError
from ..insights import InsightKernel, InsightResult
from ..logging_config import setup_logging
from ..persistence import HistoryDB
from ..persistence.models import TensorSnapshot
from ..persistence.scope import (
    ChangeScopedReport,
    build_scoped_report,
    get_changed_files,
)
from . import app
from ._common import console, display_score, resolve_settings
from ._finding_display import FINDING_DISPLAY, MAX_FILES_PER_GROUP
from ._scoped_output import _output_scoped_json, _output_scoped_rich

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
    parquet: bool = typer.Option(
        False,
        "--parquet",
        help="Also export snapshot as Parquet files (requires [tensordb] extra)",
    ),
    use_tensordb: bool = typer.Option(
        False,
        "--use-tensordb",
        help="Use DuckDB/Parquet SQL finders (requires [tensordb] extra and --parquet data)",
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

    # --use-tensordb implies --parquet (need data to query)
    if use_tensordb:
        parquet = True

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

            if parquet:
                _save_parquet(repo_path, snapshot, logger)

            if use_tensordb:
                result = _overlay_sql_findings(str(target.resolve()), result, logger)

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

            if parquet:
                _save_parquet(str(target.resolve()), snapshot, logger)

            if use_tensordb:
                result = _overlay_sql_findings(str(target.resolve()), result, logger)

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


def _save_snapshot(repo_path: str, snapshot: TensorSnapshot, logger) -> None:
    """Save v2 snapshot to .shannon/ history database."""
    try:
        from ..persistence.writer import save_tensor_snapshot

        with HistoryDB(repo_path) as db:
            sid = save_tensor_snapshot(db.conn, snapshot)
            logger.info(f"Snapshot saved (id={sid})")
    except Exception as e:
        logger.warning(f"Failed to save snapshot: {e}")


def _overlay_sql_findings(
    repo_path: str,
    result: InsightResult,
    logger,
) -> InsightResult:
    """Replace findings for SQL-implemented finder types with SQL results.

    For finder types that have SQL implementations (high_risk_hub, orphan_code,
    hidden_coupling), the SQL results replace the original Python results.
    All other finding types are kept unchanged.

    This allows side-by-side validation during the migration period.
    """
    try:
        from ..query.engine import QueryEngine
        from ..query.finders.runner import SQLFinderRunner

        engine = QueryEngine(repo_path)
        if not engine.available:
            logger.warning("No Parquet data available for --use-tensordb")
            return result

        engine.load()
        runner = SQLFinderRunner(engine)
        sql_findings = runner.run_all()
        engine.close()

        # SQL-implemented finder types (all 22 finders)
        sql_types = {
            "high_risk_hub",
            "orphan_code",
            "hidden_coupling",
            "phantom_imports",
            "hollow_code",
            "unstable_file",
            "god_file",
            "naming_drift",
            "flat_architecture",
            "dead_dependency",
            "zone_of_pain",
            "boundary_mismatch",
            "layer_violation",
            "copy_paste_clone",
            "weak_link",
            "knowledge_silo",
            "review_blindspot",
            "bug_attractor",
            "conway_violation",
            "accidental_coupling",
            "chronic_problem",
            "architecture_erosion",
        }

        # Keep non-SQL findings from original result
        kept_findings = [f for f in result.findings if f.finding_type not in sql_types]

        # Add SQL findings
        all_findings = kept_findings + sql_findings
        all_findings.sort(key=lambda f: f.severity, reverse=True)

        sql_count = len(sql_findings)
        original_sql_count = sum(1 for f in result.findings if f.finding_type in sql_types)
        logger.info(
            "TensorDB overlay: replaced %d findings with %d SQL findings for types: %s",
            original_sql_count,
            sql_count,
            ", ".join(sorted(sql_types)),
        )

        return InsightResult(
            findings=all_findings,
            store_summary=result.store_summary,
            diagnostic_report=result.diagnostic_report,
        )

    except ImportError:
        logger.warning(
            "--use-tensordb requires duckdb. "
            "Install with: pip install shannon-codebase-insight[tensordb]"
        )
        console.print(
            "[yellow]--use-tensordb requires duckdb.[/yellow] "
            "Install: pip install shannon-codebase-insight[tensordb]"
        )
        return result
    except Exception as e:
        logger.warning("TensorDB overlay failed: %s", e)
        return result


def _save_parquet(repo_path: str, snapshot: TensorSnapshot, logger) -> None:
    """Export snapshot to Parquet files alongside SQLite.

    Requires the [tensordb] optional dependency (pyarrow).
    Writes to .shannon/parquet/ directory.
    """
    try:
        from ..events.emitter import snapshot_to_events
        from ..storage.writer import ParquetWriter

        events = snapshot_to_events(snapshot)
        writer = ParquetWriter(repo_path)
        paths = writer.write_events(events)
        logger.info(f"Parquet export: {len(paths)} tables written to .shannon/parquet/")
    except ImportError:
        logger.warning(
            "Parquet export requires pyarrow. "
            "Install with: pip install shannon-codebase-insight[tensordb]"
        )
        console.print(
            "[yellow]--parquet requires pyarrow.[/yellow] "
            "Install: pip install shannon-codebase-insight[tensordb]"
        )
    except Exception as e:
        logger.warning(f"Failed to export Parquet: {e}")


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
                "severity": display_score(f.severity),
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
                    "severity": display_score(f.severity),
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

    # Show diagnostics in verbose mode
    if verbose and hasattr(result, "diagnostic_report") and result.diagnostic_report:
        diag = result.diagnostic_report
        if diag.has_issues:
            console.print()
            console.print("[bold dim]ANALYSIS DIAGNOSTICS[/bold dim]")
            for issue in diag.issues:
                icon = "[yellow]![/yellow]" if issue.severity == "warning" else "[dim]i[/dim]"
                console.print(f"  {icon} {issue.message}")
                if issue.detail:
                    console.print(f"    [dim]{issue.detail}[/dim]")
            console.print()

    console.print("[dim]Run 'shannon-insight explain <file>' for details.[/dim]")
    console.print()
