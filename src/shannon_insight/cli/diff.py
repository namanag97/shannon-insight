"""Insight diff and baseline CLI commands.

Provides two commands:
- ``insights-baseline``: Manage the baseline snapshot used for diff comparisons.
- ``insights-diff``: Show what changed since a previous analysis run.
"""

from pathlib import Path
from typing import Optional

import typer

from . import app
from ._common import console, resolve_settings
from ..exceptions import ShannonInsightError
from ..logging_config import setup_logging


# ── insights-baseline ────────────────────────────────────────────────────────


@app.command(name="insights-baseline")
def insights_baseline(
    path: Path = typer.Argument(
        Path("."),
        help="Path to the codebase directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    action: str = typer.Option(
        "show",
        "--action",
        "-a",
        help="Action to perform: set, show, or clear",
    ),
    snapshot_id: Optional[int] = typer.Option(
        None,
        "--snapshot-id",
        "-s",
        help="Snapshot ID to set as baseline (required for 'set' action)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information",
    ),
) -> None:
    """Manage the insight baseline for diff comparisons.

    The baseline is a pinned snapshot against which ``insights-diff``
    compares the current analysis.  Only one baseline can be active at
    a time.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight . insights-baseline --action show

      shannon-insight . insights-baseline --action set --snapshot-id 3

      shannon-insight . insights-baseline --action clear
    """
    logger = setup_logging(verbose=verbose, quiet=False)

    from ..storage import HistoryDB
    from ..storage.reader import load_snapshot, list_snapshots

    resolved = str(Path(path).resolve())

    try:
        with HistoryDB(resolved) as db:
            if action == "show":
                _baseline_show(db, verbose=verbose)

            elif action == "set":
                if snapshot_id is None:
                    # Auto-select: use the most recent snapshot
                    snapshots = list_snapshots(db.conn, limit=1)
                    if not snapshots:
                        console.print(
                            "[yellow]No snapshots found. "
                            "Run 'insights' first to create one.[/yellow]"
                        )
                        raise typer.Exit(1)
                    snapshot_id = snapshots[0]["id"]
                    console.print(
                        f"[dim]Auto-selecting most recent snapshot "
                        f"(id={snapshot_id}).[/dim]"
                    )

                db.set_baseline(snapshot_id)
                snap = load_snapshot(db.conn, snapshot_id)
                console.print(
                    f"[green]Baseline set to snapshot {snapshot_id}[/green]"
                )
                console.print(
                    f"  commit: {snap.commit_sha or '(none)'}"
                )
                console.print(
                    f"  timestamp: {snap.timestamp}"
                )
                console.print(
                    f"  files: {snap.file_count}, "
                    f"findings: {len(snap.findings)}"
                )

            elif action == "clear":
                db.clear_baseline()
                console.print("[green]Baseline cleared.[/green]")

            else:
                console.print(
                    f"[red]Unknown action: {action!r}. "
                    f"Use 'set', 'show', or 'clear'.[/red]"
                )
                raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ShannonInsightError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        logger.exception("Unexpected error in insights-baseline")
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(1)


def _baseline_show(db, verbose: bool = False) -> None:
    """Display the current baseline info."""
    from ..storage.reader import load_snapshot, list_snapshots

    baseline_id = db.get_baseline_snapshot_id()

    if baseline_id is None:
        console.print("[yellow]No baseline set.[/yellow]")
        console.print(
            "[dim]Use --action set to pin a snapshot as baseline.[/dim]"
        )

        # Show recent snapshots so user knows what's available
        snapshots = list_snapshots(db.conn, limit=5)
        if snapshots:
            console.print()
            console.print("[dim]Recent snapshots:[/dim]")
            for snap in snapshots:
                console.print(
                    f"  [dim]id={snap['id']}  "
                    f"{snap['timestamp'][:19]}  "
                    f"commit={snap['commit_sha'][:8] if snap['commit_sha'] else '(none)'}  "
                    f"files={snap['file_count']}  "
                    f"findings={snap['finding_count']}[/dim]"
                )
        return

    try:
        snap = load_snapshot(db.conn, baseline_id)
    except ValueError:
        console.print(
            f"[red]Baseline references snapshot {baseline_id} "
            f"which no longer exists.[/red]"
        )
        return

    console.print(
        f"[bold cyan]Baseline:[/bold cyan] snapshot {baseline_id}"
    )
    console.print(
        f"  commit: {snap.commit_sha or '(none)'}"
    )
    console.print(f"  timestamp: {snap.timestamp}")
    console.print(
        f"  files: {snap.file_count}, "
        f"findings: {len(snap.findings)}"
    )
    if verbose:
        console.print(
            f"  analyzers: {', '.join(snap.analyzers_ran)}"
        )
        console.print(
            f"  modules: {snap.module_count}, "
            f"commits: {snap.commits_analyzed}"
        )


# ── insights-diff ────────────────────────────────────────────────────────────


@app.command(name="insights-diff")
def insights_diff(
    path: Path = typer.Argument(
        Path("."),
        help="Path to the codebase directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    ref: Optional[str] = typer.Option(
        None,
        "--ref",
        "-r",
        help="Compare against a specific snapshot ID or commit SHA",
    ),
    use_baseline: bool = typer.Option(
        False,
        "--baseline",
        "-b",
        help="Compare against the pinned baseline snapshot",
    ),
    language: str = typer.Option(
        "auto",
        "--language",
        "-l",
        help="Programming language (auto, python, go, typescript, etc.)",
    ),
    fmt: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich or json",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show full per-file metric details",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress logging",
    ),
    max_findings: int = typer.Option(
        10,
        "--max-findings",
        "-n",
        help="Maximum findings for current analysis run",
        min=1,
        max=50,
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (TOML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Parallel workers",
        min=1,
        max=32,
    ),
) -> None:
    """Show what changed since a previous analysis run.

    Runs a fresh analysis and compares the resulting snapshot against
    either the pinned baseline (--baseline), a specific snapshot/commit
    (--ref), or the most recent previous snapshot.

    File renames are detected automatically when both snapshots have
    commit SHAs.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight . insights-diff

      shannon-insight . insights-diff --baseline

      shannon-insight . insights-diff --ref 5

      shannon-insight . insights-diff --format json --verbose
    """
    logger = setup_logging(verbose=verbose, quiet=quiet)

    from ..insights import InsightKernel
    from ..storage import HistoryDB
    from ..storage.reader import load_snapshot, load_snapshot_by_commit, list_snapshots
    from ..storage.writer import save_snapshot
    from ..diff import diff_snapshots
    from ..diff.rename import detect_renames
    from ..formatters.insight_diff_formatter import InsightDiffFormatter

    resolved = str(Path(path).resolve())

    try:
        settings = resolve_settings(
            config=config,
            no_cache=False,
            workers=workers,
            verbose=verbose,
            quiet=quiet,
        )

        # ── Step 1: Run current analysis and capture snapshot ────────
        kernel = InsightKernel(
            resolved, language=language, settings=settings,
        )
        result, new_snapshot = kernel.run_and_capture(
            max_findings=max_findings,
        )

        # ── Step 2: Save current snapshot ────────────────────────────
        with HistoryDB(resolved) as db:
            new_sid = save_snapshot(db.conn, new_snapshot)
            logger.info("Current snapshot saved (id=%d)", new_sid)

            # ── Step 3: Load old snapshot ────────────────────────────
            old_snapshot = _resolve_old_snapshot(
                db=db,
                ref=ref,
                use_baseline=use_baseline,
                current_snapshot_id=new_sid,
            )

            if old_snapshot is None:
                console.print(
                    "[yellow]No previous snapshot found to compare against.[/yellow]"
                )
                console.print(
                    "[dim]Run 'insights' at least twice, or set a baseline "
                    "with 'insights-baseline --action set'.[/dim]"
                )
                raise typer.Exit(0)

            # ── Step 4: Detect renames ───────────────────────────────
            renames = {}
            if old_snapshot.commit_sha and new_snapshot.commit_sha:
                if old_snapshot.commit_sha != new_snapshot.commit_sha:
                    renames = detect_renames(
                        resolved,
                        old_snapshot.commit_sha,
                        new_snapshot.commit_sha,
                    )
                    if renames:
                        logger.info(
                            "Detected %d rename(s)", len(renames)
                        )

            # ── Step 5: Compute diff ─────────────────────────────────
            diff = diff_snapshots(
                old_snapshot,
                new_snapshot,
                renames=renames if renames else None,
            )

            # ── Step 6: Render ───────────────────────────────────────
            formatter = InsightDiffFormatter(console=console)
            formatter.render(diff, fmt=fmt, verbose=verbose)

    except typer.Exit:
        raise
    except ShannonInsightError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Unexpected error in insights-diff")
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


def _resolve_old_snapshot(
    db,
    ref: Optional[str],
    use_baseline: bool,
    current_snapshot_id: int,
):
    """Determine which old snapshot to compare against.

    Priority:
    1. If ``ref`` is specified and numeric, treat as snapshot id.
    2. If ``ref`` is specified and non-numeric, treat as commit SHA.
    3. If ``use_baseline`` is True, use the pinned baseline.
    4. Otherwise, use the most recent snapshot before the current one.
    """
    from ..storage.reader import load_snapshot, load_snapshot_by_commit, list_snapshots

    if ref is not None:
        # Try as snapshot ID first
        try:
            sid = int(ref)
            return load_snapshot(db.conn, sid)
        except ValueError:
            pass

        # Try as commit SHA
        snap = load_snapshot_by_commit(db.conn, ref)
        if snap is not None:
            return snap

        console.print(
            f"[yellow]Could not find snapshot for ref '{ref}'.[/yellow]"
        )
        return None

    if use_baseline:
        baseline_id = db.get_baseline_snapshot_id()
        if baseline_id is None:
            console.print(
                "[yellow]No baseline set. "
                "Use 'insights-baseline --action set' first.[/yellow]"
            )
            return None
        try:
            return load_snapshot(db.conn, baseline_id)
        except ValueError:
            console.print(
                f"[yellow]Baseline snapshot {baseline_id} no longer exists.[/yellow]"
            )
            return None

    # Default: most recent snapshot before the current one
    snapshots = list_snapshots(db.conn, limit=5)
    for snap_info in snapshots:
        if snap_info["id"] != current_snapshot_id:
            return load_snapshot(db.conn, snap_info["id"])

    return None
