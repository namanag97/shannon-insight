"""Main analysis command — unified through InsightKernel."""

import json
import subprocess
from collections import OrderedDict
from contextlib import nullcontext
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
from ._finding_display import MAX_FILES_PER_GROUP
from ._scoped_output import _output_scoped_json, _output_scoped_rich
from ._ux import (
    AnalysisTimer,
    ExitCode,
    GitHubActionsFormatter,
    compact_summary,
    is_first_run,
    is_github_actions,
    severity_label,
    show_first_run_hint,
)
from .tui import run_tui

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
# Auto-detect optional features
# ---------------------------------------------------------------------------


def _pyarrow_available() -> bool:
    """Return True if pyarrow is importable."""
    try:
        import pyarrow  # noqa: F401

        return True
    except ImportError:
        return False


def _duckdb_available() -> bool:
    """Return True if duckdb is importable."""
    try:
        import duckdb  # noqa: F401

        return True
    except ImportError:
        return False


def _parquet_data_exists(repo_path: str) -> bool:
    """Return True if .shannon/parquet/ has any .parquet files."""
    parquet_dir = Path(repo_path) / ".shannon" / "parquet"
    if not parquet_dir.is_dir():
        return False
    return any(parquet_dir.glob("*.parquet"))


def _output_signals_mode(
    target: Path, signals_arg: str, changed: bool, since: Optional[str]
) -> None:
    """Show raw signals table for --signals mode.

    Args:
        target: Path to analyze
        signals_arg: File path or empty string for all files
        changed: Whether --changed flag was set
        since: Git ref for --since flag
    """
    from ._signal_display import render_signals_table

    # Run analysis first to get signals
    settings = resolve_settings(config=None, no_cache=False, workers=None, verbose=False)

    with console.status("[cyan]Analyzing..."):
        kernel = InsightKernel(str(target), language="auto", settings=settings)
        result, snapshot = kernel.run(max_findings=0)

    # Render signals
    file_path = signals_arg if signals_arg else None
    output = render_signals_table(snapshot, file_path)
    console.print(output)


def _output_hotspots_mode(result: InsightResult, snapshot: TensorSnapshot) -> None:
    """Show hotspots ranking for --hotspots mode."""
    from ._hotspots import render_hotspots_table

    output = render_hotspots_table(snapshot, result.findings, n=20)
    console.print()
    console.print(output)
    console.print()


def _output_preview(target: Path, changed: bool, since: Optional[str], save: bool) -> None:
    """Show what would be analyzed without running analysis.

    Dry-run mode that helps users understand scope before committing to full analysis.
    """
    console.print()
    console.print("[bold cyan]PREVIEW MODE[/bold cyan] — showing what would be analyzed")
    console.print()

    skip_dirs = {"venv", ".venv", "node_modules", "__pycache__", ".git", "dist", "build", "target"}
    code_exts = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".go",
        ".java",
        ".rs",
        ".rb",
        ".c",
        ".cpp",
        ".cc",
        ".h",
    }

    # Count source files
    all_files = []
    for fp in target.rglob("*"):
        if fp.is_file() and fp.suffix.lower() in code_exts:
            if not any(part in skip_dirs for part in fp.parts):
                all_files.append(fp)

    total_lines = 0
    by_language: dict[str, int] = {}

    for fp in all_files:
        try:
            content = fp.read_text(encoding="utf-8", errors="ignore")
            lines = content.count("\n")
            total_lines += lines
        except Exception:
            lines = 0

        ext = fp.suffix.lower()
        lang = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".go": "Go",
            ".java": "Java",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".c": "C",
            ".cpp": "C++",
            ".cc": "C++",
            ".h": "C/C++",
        }.get(ext, "Other")
        by_language[lang] = by_language.get(lang, 0) + 1

    # Git status
    git_available = (target / ".git").exists()
    commit_count = 0
    if git_available:
        try:
            result = subprocess.run(
                ["git", "-C", str(target), "rev-list", "--count", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                commit_count = int(result.stdout.strip())
        except Exception:
            pass

    # Scoped files
    scoped_files = []
    if changed or since:
        ref = since if since else _auto_detect_changed_ref(str(target))
        scoped_files = get_changed_files(str(target), ref)

    # Output
    console.print(f"  [bold]Target:[/bold] {target}")
    console.print(f"  [bold]Files:[/bold] {len(all_files)}")
    console.print(f"  [bold]Lines:[/bold] {total_lines:,}")

    if by_language:
        langs = ", ".join(
            f"{k}: {v}" for k, v in sorted(by_language.items(), key=lambda x: -x[1])[:5]
        )
        console.print(f"  [bold]Languages:[/bold] {langs}")

    if git_available:
        console.print(f"  [bold]Git:[/bold] ✓ ({commit_count} commits)")
    else:
        console.print("  [bold]Git:[/bold] ✗ (temporal analysis disabled)")

    if changed or since:
        if scoped_files:
            console.print(f"  [bold]Scoped to:[/bold] {len(scoped_files)} changed files")
            for f in scoped_files[:5]:
                console.print(f"    • {f}")
            if len(scoped_files) > 5:
                console.print(f"    [dim]... and {len(scoped_files) - 5} more[/dim]")
        else:
            console.print("  [bold]Scoped to:[/bold] [yellow]No changed files detected[/yellow]")

    console.print()

    # What would happen
    console.print("[bold]Would:[/bold]")
    if save:
        console.print(f"  • Save snapshot to [cyan]{target / '.shannon'}[/cyan]")
    else:
        console.print("  • [dim]Not saving snapshot (--no-save)[/dim]")

    if _pyarrow_available():
        console.print(f"  • Export Parquet to [cyan]{target / '.shannon' / 'parquet'}[/cyan]")

    console.print()
    console.print("[dim]Run without --preview to execute analysis.[/dim]")
    console.print()


# ---------------------------------------------------------------------------
# Main callback
# ---------------------------------------------------------------------------


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
        True,
        "--save/--no-save",
        help="Save snapshot to .shannon/ (default: yes)",
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
    no_tui: bool = typer.Option(
        False,
        "--no-tui",
        help="Disable interactive TUI (use classic output)",
    ),
    journey: bool = typer.Option(
        False,
        "--journey",
        help="Show developer journey view: health score, progress, actionable next steps",
    ),
    debug_export: Optional[Path] = typer.Option(
        None,
        "--debug-export",
        help="Export pipeline state at each stage to JSON files in this directory",
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--output-format",
        "-f",
        help="Output format: default | github | compact",
        click_type=click.Choice(["default", "github", "compact"], case_sensitive=False),
    ),
    preview: bool = typer.Option(
        False,
        "--preview",
        help="Show what would be analyzed without running full analysis",
    ),
    signals: Optional[str] = typer.Option(
        None,
        "--signals",
        help="Show raw signals table (optionally for specific file)",
    ),
    hotspots: bool = typer.Option(
        False,
        "--hotspots",
        help="Show files ranked by combined risk signals",
    ),
    concerns: bool = typer.Option(
        False,
        "--concerns",
        help="Show concerns view (findings grouped by category) instead of focus point",
    ),
    cli_mode: bool = typer.Option(
        False,
        "--cli",
        help="Force CLI output instead of opening dashboard",
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
    try:
        target = Path(path).resolve()
    except (FileNotFoundError, OSError):
        # If current directory doesn't exist, use absolute path
        target = Path(path).absolute()
    ctx.ensure_object(dict)
    ctx.obj["path"] = target

    if ctx.invoked_subcommand is not None:
        return

    from .. import __version__

    # Handle flags that should always use CLI mode (before dashboard check)
    if version:
        console.print(
            f"[bold cyan]Shannon Insight[/bold cyan] version [green]{__version__}[/green]"
        )
        raise typer.Exit(0)

    # Preview mode: show what would be analyzed without running
    if preview:
        _output_preview(target, changed, since, save)
        raise typer.Exit(0)

    # Signals mode: show raw signals table
    if signals is not None:
        _output_signals_mode(target, signals, changed, since)
        raise typer.Exit(0)

    # Launch dashboard by default (unless --cli flag is set or other CLI-only flags)
    # These flags force CLI mode regardless of --cli
    force_cli = (
        json_output
        or no_tui
        or hotspots
        or journey
        or concerns
        or changed
        or since is not None
        or fail_on is not None
        or output_format is not None
        or debug_export is not None
    )

    if not cli_mode and not force_cli:
        # Check if serve dependencies are available
        try:
            from ..server import _check_deps

            _check_deps()

            from ..server.lifecycle import launch_server

            settings = resolve_settings(config=config, workers=workers, verbose=verbose)

            if verbose:
                import logging as _logging

                _logging.basicConfig(level=_logging.DEBUG)
            else:
                import logging as _logging

                _logging.basicConfig(level=_logging.WARNING)

            launch_server(
                root_dir=str(target),
                settings=settings,
                console=console,
                host="127.0.0.1",
                port=8765,
                no_browser=False,
                verbose=verbose,
            )
            return
        except ImportError:
            # If serve dependencies not available, fall back to CLI mode
            console.print(
                "[yellow]Dashboard dependencies not installed. "
                "Install with: pip install shannon-codebase-insight[server][/yellow]"
            )
            console.print("[dim]Falling back to CLI mode...[/dim]\n")

    logger = setup_logging(verbose=verbose)

    # Auto-detect optional features (no flags needed)
    parquet = _pyarrow_available()
    use_tensordb = _duckdb_available()

    # Start timing
    timer = AnalysisTimer.start()
    first_run = is_first_run(target)

    # Auto-detect GitHub Actions for output format
    effective_format = output_format
    if effective_format is None and is_github_actions():
        effective_format = "github"

    try:
        settings = resolve_settings(
            config=config,
            no_cache=False,
            workers=workers,
            verbose=verbose,
        )

        # Determine if we are in scoped mode
        scoped_mode = since is not None or changed

        # Use TUI for interactive, non-JSON, non-scoped, non-journey analysis
        import sys

        use_tui = (
            not json_output
            and not no_tui
            and not scoped_mode
            and not journey
            and effective_format not in ("github", "compact")
            and sys.stdin.isatty()
        )

        if use_tui:
            # Run TUI walkthrough
            result, snapshot = run_tui(target, settings, console)

            repo_path = str(target.resolve())

            if save and settings.enable_history:
                _save_snapshot(repo_path, snapshot, logger)

            if save and parquet:
                _save_parquet(repo_path, snapshot, logger)

            if use_tensordb and _parquet_data_exists(repo_path):
                result = _overlay_sql_findings(repo_path, result, logger)

            if fail_on is not None:
                should_fail = _check_fail_condition_full(fail_on, result)
                if should_fail:
                    raise typer.Exit(1)

            raise typer.Exit(0)

        kernel = InsightKernel(
            str(target),
            language="auto",
            settings=settings,
            debug_export_dir=debug_export,
        )

        max_findings = settings.insights_max_findings

        # Progress spinner — only visible in Rich (non-JSON) mode
        show_progress = not json_output
        status_ctx = (
            console.status("[cyan]Initializing...", spinner="dots")
            if show_progress
            else nullcontext()
        )

        with status_ctx as status:

            def _on_progress(msg: str) -> None:
                if show_progress and status is not None:
                    status.update(f"[cyan]{msg}")

            if scoped_mode:
                # -- Scoped analysis path --
                repo_path = str(target.resolve())

                _on_progress("Detecting changed files...")
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

                result, snapshot = kernel.run(
                    max_findings=max_findings,
                    on_progress=_on_progress,
                )

                if save and settings.enable_history:
                    _on_progress("Saving snapshot...")
                    _save_snapshot(repo_path, snapshot, logger)

                if save and parquet:
                    _on_progress("Exporting Parquet...")
                    _save_parquet(repo_path, snapshot, logger)

                if use_tensordb and _parquet_data_exists(repo_path):
                    _on_progress("Running SQL finders...")
                    result = _overlay_sql_findings(str(target.resolve()), result, logger)

                report = build_scoped_report(changed_files, snapshot)

            else:
                # -- Full analysis path --
                result, snapshot = kernel.run(
                    max_findings=max_findings,
                    on_progress=_on_progress,
                )

                repo_path_full = str(target.resolve())

                if save and settings.enable_history:
                    _on_progress("Saving snapshot...")
                    _save_snapshot(repo_path_full, snapshot, logger)

                if save and parquet:
                    _on_progress("Exporting Parquet...")
                    _save_parquet(repo_path_full, snapshot, logger)

                if use_tensordb and _parquet_data_exists(repo_path_full):
                    _on_progress("Running SQL finders...")
                    result = _overlay_sql_findings(repo_path_full, result, logger)

                report = None

        # -- Spinner is now cleared; render output --
        # Update timer with actual counts
        timer.file_count = result.store_summary.total_files
        timer.module_count = result.store_summary.total_modules or 0
        timer.commit_count = result.store_summary.commits_analyzed or 0

        if scoped_mode:
            assert report is not None  # Always set in scoped_mode
            if json_output:
                _output_scoped_json(report, result)
            elif effective_format == "github":
                _output_github(
                    result, scoped_findings=report.direct_findings + report.blast_findings
                )
            else:
                _output_scoped_rich(report, result, verbose=verbose)

            if fail_on is not None:
                should_fail = _check_fail_condition_scoped(fail_on, report)
                if should_fail:
                    raise typer.Exit(
                        ExitCode.HIGH_SEVERITY if fail_on == "high" else ExitCode.FINDINGS_EXIST
                    )
        else:
            if hotspots:
                # Hotspots-only view: ranked files by risk signals
                _output_hotspots_mode(result, snapshot)
            elif journey:
                # Developer journey view: health, progress, actionable steps
                from .journey import render_journey, render_journey_json

                if json_output:
                    journey_data = render_journey_json(result, snapshot)
                    print(json.dumps(journey_data, indent=2))
                else:
                    output = render_journey(result, snapshot)
                    console.print(output)
            elif json_output:
                _output_json(result)
            elif effective_format == "github":
                _output_github(result)
            elif effective_format == "compact":
                _output_compact(result, timer)
            elif concerns:
                # Legacy concerns view: findings grouped by category
                _output_rich_legacy(
                    result, snapshot, verbose=verbose, timer=timer, first_run=first_run
                )
            else:
                # Default: Focus Point First (answers "what should I do?")
                _output_rich(result, snapshot, verbose=verbose, timer=timer, first_run=first_run)

            if fail_on is not None:
                should_fail = _check_fail_condition_full(fail_on, result)
                if should_fail:
                    raise typer.Exit(
                        ExitCode.HIGH_SEVERITY if fail_on == "high" else ExitCode.FINDINGS_EXIST
                    )

    except typer.Exit:
        raise

    except ShannonInsightError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        console.print("\n[yellow]Analysis interrupted[/yellow]")
        # Clean up any partial snapshot data to avoid corruption
        try:
            shannon_dir = target / ".shannon"
            if shannon_dir.exists():
                # Remove partial parquet files (they may be incomplete)
                parquet_dir = shannon_dir / "parquet"
                if parquet_dir.exists():
                    for partial in parquet_dir.glob("*.parquet.tmp"):
                        partial.unlink(missing_ok=True)
                        logger.debug("Removed partial file: %s", partial)
                # Note: SQLite handles interrupted writes via WAL/rollback
        except Exception as cleanup_err:
            logger.debug("Cleanup after interrupt failed: %s", cleanup_err)
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
            logger.debug("No Parquet data available for TensorDB SQL finders")
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

        # Apply subsumption to remove redundant findings
        from ..insights.ranking import deduplicate_findings

        all_findings = deduplicate_findings(all_findings)
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
        logger.debug("duckdb not available for SQL finders, skipping")
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
        logger.debug("pyarrow not available for Parquet export, skipping")
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


def _output_rich(
    result: InsightResult,
    snapshot: TensorSnapshot,
    verbose: bool = False,
    timer: Optional[AnalysisTimer] = None,
    first_run: bool = False,
):
    """Human-readable Rich terminal output with Focus Point First pattern.

    Theory: docs/research/OUTPUT_UX_THEORY.md

    The output follows the decision hierarchy:
    1. VERDICT - One-line health status (answers "should I care?")
    2. FOCUS POINT - Single most actionable file (answers "what should I do?")
    3. ALSO CONSIDER - Alternative files (escape hatch if #1 isn't right)
    4. PATTERNS - Broader context (for understanding, not deciding)
    """
    from ._focus import get_verdict, identify_focus_point

    summary = result.store_summary
    console.print()

    # Extract health score
    global_signals = getattr(snapshot, "global_signals", {}) or {}
    health_raw = global_signals.get("codebase_health", 0.5)

    # Compute focus point and alternatives
    focus, alternatives = identify_focus_point(snapshot, result.findings, n_alternatives=4)

    # ══════════════════════════════════════════════════════════════════════════
    # 1. VERDICT - The one-line answer to "should I care?"
    # ══════════════════════════════════════════════════════════════════════════

    if timer:
        elapsed = timer.elapsed()
        console.print(
            f"[green]✓[/green] Analyzed [bold]{summary.total_files}[/bold] files "
            f"in [bold]{elapsed:.1f}s[/bold]"
        )
        console.print()

    verdict_text, verdict_color = get_verdict(health_raw, focus, len(result.findings))
    console.print(f"[bold {verdict_color}]{verdict_text}[/]")

    if not summary.git_available:
        console.print("[dim]  (no git history — temporal analysis skipped)[/dim]")

    console.print()

    # ══════════════════════════════════════════════════════════════════════════
    # 2. FOCUS POINT - The single most actionable file
    # ══════════════════════════════════════════════════════════════════════════

    if focus is None:
        console.print("[bold green]No actionable hotspots detected.[/bold green]")
        console.print()
        if first_run:
            show_first_run_hint(console)
        else:
            console.print()
        return

    # Focus point header
    console.print("[bold]START HERE[/bold]")

    # Truncate long paths for display
    display_path = focus.path
    if len(display_path) > 50:
        display_path = "..." + display_path[-47:]

    # Color based on actionability
    if focus.actionability > 0.15:
        focus_color = "red"
    elif focus.actionability > 0.05:
        focus_color = "yellow"
    else:
        focus_color = "cyan"

    console.print(f"  [bold {focus_color}]{display_path}[/]")

    # WHY this file?
    why = focus.why_summary()
    console.print(f"  [dim]Why:[/dim] {why}")

    # Key signals as evidence
    signals_parts = []
    if focus.blast_radius > 0:
        signals_parts.append(f"blast={focus.blast_radius}")
    if focus.total_changes > 0:
        signals_parts.append(f"changes={focus.total_changes}")
    if focus.churn_cv > 0.5:
        signals_parts.append(f"cv={focus.churn_cv:.1f}")
    if focus.lines > 0:
        signals_parts.append(f"lines={focus.lines}")
    if signals_parts:
        console.print(f"  [dim]Data:[/dim] {', '.join(signals_parts)}")

    # Show findings on this file (if any)
    if focus.findings:
        finding_types = list({f.finding_type.replace("_", " ") for f in focus.findings})
        if len(finding_types) <= 3:
            console.print(f"  [dim]Issues:[/dim] {', '.join(finding_types)}")
        else:
            console.print(
                f"  [dim]Issues:[/dim] {', '.join(finding_types[:3])}, +{len(finding_types) - 3} more"
            )

    console.print()

    # ══════════════════════════════════════════════════════════════════════════
    # 3. ALSO CONSIDER - Alternatives if #1 isn't right for user's context
    # ══════════════════════════════════════════════════════════════════════════

    if alternatives:
        console.print("[bold]ALSO CONSIDER[/bold]")
        for alt in alternatives:
            alt_path = alt.path
            if len(alt_path) > 40:
                alt_path = "..." + alt_path[-37:]

            # Color based on actionability
            if alt.actionability > 0.15:
                alt_color = "red"
            elif alt.actionability > 0.05:
                alt_color = "yellow"
            else:
                alt_color = "dim"

            why_short = alt.why_summary()
            if len(why_short) > 35:
                why_short = why_short[:32] + "..."

            console.print(
                f"  [{alt_color}]#{alt.rank}[/{alt_color}]  {alt_path}  [dim]{why_short}[/dim]"
            )

        console.print()

    # ══════════════════════════════════════════════════════════════════════════
    # 4. PATTERNS - Broader context (collapsed unless verbose)
    # ══════════════════════════════════════════════════════════════════════════

    if verbose:
        # Show full concerns breakdown in verbose mode
        from ._concerns import organize_by_concerns

        concern_reports = organize_by_concerns(result.findings, global_signals)
        active_concerns = [r for r in concern_reports if r.findings]

        if active_concerns:
            console.print(
                f"[bold]PATTERNS[/bold] — {len(result.findings)} issues across {len(active_concerns)} areas"
            )
            console.print()

            for report in active_concerns:
                concern = report.concern
                finding_count = len(report.findings)
                console.print(
                    f"  {concern.icon} [bold]{concern.name}[/bold]: "
                    f"{finding_count} issue{'s' if finding_count != 1 else ''}"
                )

            console.print()
    else:
        # Compact pattern summary
        if result.findings:
            # Group by broad category
            categories: dict[str, int] = {}
            for f in result.findings:
                cat = _categorize_finding(f.finding_type)
                categories[cat] = categories.get(cat, 0) + 1

            if categories:
                parts = [
                    f"{count} {cat}"
                    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:4]
                ]
                console.print(f"[dim]Patterns: {', '.join(parts)}[/dim]")
                console.print()

    # ══════════════════════════════════════════════════════════════════════════
    # Footer
    # ══════════════════════════════════════════════════════════════════════════

    console.print(f"[dim]Drill down: shannon-insight explain {focus.path}[/dim]")

    if first_run:
        show_first_run_hint(console)
    else:
        console.print()


def _categorize_finding(finding_type: str) -> str:
    """Categorize a finding type into a broad category for compact display."""
    structural = {
        "god_file",
        "orphan_code",
        "phantom_imports",
        "hollow_code",
        "dead_dependency",
        "flat_architecture",
        "copy_paste_clone",
        "naming_drift",
        "incomplete_implementation",
    }
    coupling = {
        "hidden_coupling",
        "accidental_coupling",
        "boundary_mismatch",
    }
    architecture = {
        "layer_violation",
        "zone_of_pain",
        "architecture_erosion",
    }
    temporal = {
        "unstable_file",
        "chronic_problem",
        "thrashing_code",
    }
    team = {
        "knowledge_silo",
        "review_blindspot",
        "truck_factor",
        "conway_violation",
        "bus_factor",
    }
    risk = {
        "high_risk_hub",
        "bug_attractor",
        "weak_link",
        "bug_magnet",
        "directory_hotspot",
    }

    if finding_type in structural:
        return "structural"
    if finding_type in coupling:
        return "coupling"
    if finding_type in architecture:
        return "architecture"
    if finding_type in temporal:
        return "churn"
    if finding_type in team:
        return "team"
    if finding_type in risk:
        return "risk"
    return "other"


def _output_rich_legacy(
    result: InsightResult,
    snapshot: TensorSnapshot,
    verbose: bool = False,
    timer: Optional[AnalysisTimer] = None,
    first_run: bool = False,
):
    """Legacy output format (concerns-first). Use --concerns flag to access."""
    from ._finding_display import get_display_config, get_severity_display

    summary = result.store_summary
    console.print()

    # Extract health score from snapshot
    global_signals = getattr(snapshot, "global_signals", {}) or {}
    health_raw = global_signals.get("codebase_health", 0.5)
    health_display = round(health_raw * 9 + 1, 1)  # Convert 0-1 to 1-10 scale

    # Health color and status
    if health_display >= 8:
        health_color, health_status = "green", "Healthy"
    elif health_display >= 6:
        health_color, health_status = "yellow", "Moderate"
    elif health_display >= 4:
        health_color, health_status = "orange1", "At Risk"
    else:
        health_color, health_status = "red", "Critical"

    # Timing + Health header
    if timer:
        elapsed = timer.elapsed()
        console.print(
            f"[green]✓[/green] Analyzed [bold]{summary.total_files}[/bold] files "
            f"in [bold]{elapsed:.1f}s[/bold]"
        )
        console.print()

    # Big health display
    health_bar = "█" * int(health_display) + "░" * (10 - int(health_display))
    console.print(
        f"[bold]CODEBASE HEALTH[/bold]  [{health_color}]{health_bar}[/{health_color}]  [{health_color}]{health_display}/10[/{health_color}] {health_status}"
    )
    console.print()

    # Concerns section
    from ._concerns import organize_by_concerns

    if not summary.git_available:
        console.print("[dim]ℹ No git history — temporal findings skipped[/dim]")
        console.print()

    if not result.findings:
        console.print("[bold green]✓ No issues detected[/bold green]")
        console.print()
        return

    # Organize findings by concern (dimension of health)
    concern_reports = organize_by_concerns(result.findings, global_signals)

    # Only show concerns that have findings
    active_concerns = [r for r in concern_reports if r.findings]

    if not active_concerns:
        console.print("[bold green]✓ No issues detected[/bold green]")
        console.print()
        return

    console.print(
        f"[bold]CONCERNS[/bold] — {len(result.findings)} issue{'s' if len(result.findings) != 1 else ''} in {len(active_concerns)} area{'s' if len(active_concerns) != 1 else ''}:"
    )
    console.print()

    # Render each concern
    from ._finding_display import format_finding_data

    for report in active_concerns:
        concern = report.concern
        finding_count = len(report.findings)

        # Concern header: icon + name + score + file count
        score_bar = "█" * int(report.score) + "░" * (10 - int(report.score))
        console.print(
            f"{concern.icon} [bold]{concern.name}[/bold]  "
            f"[{report.color}]{score_bar}[/{report.color}] "
            f"[{report.color}]{report.score}/10[/{report.color}]  "
            f"[dim]({finding_count} issue{'s' if finding_count != 1 else ''}, {report.file_count} file{'s' if report.file_count != 1 else ''})[/dim]"
        )

        # Description
        console.print(f"  [dim]{concern.description}[/dim]")

        # Attributes (key metrics for this concern) - only in verbose
        if verbose and report.attributes:
            attr_strs = [f"{k}={v:.2f}" for k, v in report.attributes.items()]
            console.print(f"  [dim]Metrics: {', '.join(attr_strs)}[/dim]")

        console.print()

        # Root causes (findings)
        shown = report.findings[:MAX_FILES_PER_GROUP]
        for f in shown:
            display = get_display_config(f.finding_type)
            sev_icon, sev_color, _ = get_severity_display(f.severity)
            icon = display.get("icon", "•")

            # File path(s)
            if not f.files:
                file_str = "(codebase)"
            elif len(f.files) == 1:
                file_str = f.files[0]
            else:
                file_str = " ↔ ".join(f.files[:2])
                if len(f.files) > 2:
                    file_str += f" +{len(f.files) - 2}"

            console.print(f"  {icon} [{sev_color}]{file_str}[/{sev_color}]")

            # Data points - show raw signals, not prescriptions
            data_line = format_finding_data(f)
            if data_line:
                # Truncate to fit nicely
                if len(data_line) > 70:
                    data_line = data_line[:67] + "..."
                console.print(f"      [dim]{data_line}[/dim]")

        remaining = finding_count - MAX_FILES_PER_GROUP
        if remaining > 0:
            console.print(f"  [dim]... and {remaining} more[/dim]")

        # Interpretation (informative, not prescriptive)
        interp = display.get("interpretation", "")
        if interp:
            console.print(f"  [dim italic]{interp}[/dim italic]")

        console.print()

    # Footer
    console.print("[dim]Run 'shannon-insight explain <file>' for file details[/dim]")

    if first_run:
        show_first_run_hint(console)
    else:
        console.print()


def _output_github(result: InsightResult, scoped_findings: Optional[list] = None):
    """GitHub Actions workflow command output.

    Produces annotations that appear inline on PR diffs:
    ::warning file=path,line=1::HIGH_RISK_HUB: Many dependents...
    """
    findings = scoped_findings if scoped_findings is not None else result.findings

    if not findings:
        print("::notice::No significant findings detected")
        return

    gh = GitHubActionsFormatter

    # Group by severity for summary
    high_count = sum(1 for f in findings if f.severity >= 0.8)
    med_count = sum(1 for f in findings if 0.6 <= f.severity < 0.8)

    print(
        gh.group(
            f"Shannon Insight: {len(findings)} findings ({high_count} high, {med_count} medium)"
        )
    )

    for f in sorted(findings, key=lambda x: x.severity, reverse=True):
        label, _ = severity_label(f.severity)
        path = f.files[0] if f.files else "unknown"

        # Build message with evidence
        message = f"{f.finding_type.upper()}: {f.title}"
        if f.evidence:
            top_evidence = f.evidence[0]
            message += f" ({top_evidence.description})"
        if f.suggestion:
            message += f" → {f.suggestion}"

        # Output as warning (high) or notice (medium/low)
        if f.severity >= 0.8:
            print(gh.error(path, message))
        elif f.severity >= 0.6:
            print(gh.warning(path, message))
        else:
            print(gh.notice(path, message))

    print(gh.endgroup())

    # Summary line
    summary = result.store_summary
    print(
        f"::notice::Analyzed {summary.total_files} files, "
        f"{summary.total_modules or 0} modules, "
        f"{summary.commits_analyzed or 0} commits"
    )


def _output_compact(result: InsightResult, timer: AnalysisTimer):
    """Compact one-line output for scripting and CI logs.

    Examples:
        ✓ 234 files • 0 issues • 0.8s
        ⚠ 234 files • 12 issues (3 high) • 1.2s
    """
    high_count = sum(1 for f in result.findings if f.severity >= 0.8)

    line = compact_summary(
        file_count=result.store_summary.total_files,
        finding_count=len(result.findings),
        elapsed_secs=timer.elapsed(),
        high_severity_count=high_count,
    )
    print(line)
