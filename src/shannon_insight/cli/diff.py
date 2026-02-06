"""Diff CLI command — compare snapshots and manage baselines.

Provides:
- ``diff``: Show what changed since a previous analysis run.
- ``diff --pin``: Pin the current snapshot as baseline.
- ``diff --unpin``: Clear the pinned baseline.
"""

from pathlib import Path
from typing import Optional

import typer

from ..exceptions import ShannonInsightError
from ..logging_config import setup_logging
from . import app
from ._common import console, resolve_settings


@app.command(name="diff")
def diff_cmd(
    ctx: typer.Context,
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
    pin: bool = typer.Option(
        False,
        "--pin",
        help="Pin the current (most recent) snapshot as baseline",
    ),
    unpin: bool = typer.Option(
        False,
        "--unpin",
        help="Clear the pinned baseline",
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
        help="Show full per-file metric details",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (TOML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        hidden=True,
    ),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Parallel workers",
        min=1,
        max=32,
        hidden=True,
    ),
) -> None:
    """Show what changed since a previous analysis run.

    Runs a fresh analysis and compares the resulting snapshot against
    either the pinned baseline (--baseline), a specific snapshot/commit
    (--ref), or the most recent previous snapshot.

    File renames are detected automatically when both snapshots have
    commit SHAs.

    Use --pin to pin the current snapshot as baseline, or --unpin to clear it.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight diff

      shannon-insight diff --baseline

      shannon-insight diff --ref 5

      shannon-insight diff --json --verbose

      shannon-insight diff --pin

      shannon-insight diff --unpin
    """
    resolved = ctx.obj.get("path", Path.cwd()).resolve()
    logger = setup_logging(verbose=verbose)

    from ..persistence import HistoryDB
    from ..persistence.reader import list_snapshots, load_snapshot

    resolved_str = str(resolved)

    try:
        # ── Handle baseline management first (no analysis needed) ─────
        if pin:
            with HistoryDB(resolved_str) as db:
                snapshots = list_snapshots(db.conn, limit=1)
                if not snapshots:
                    console.print(
                        "[yellow]No snapshots found. "
                        "Run 'shannon-insight --save' first to create one.[/yellow]"
                    )
                    raise typer.Exit(1)
                snapshot_id = snapshots[0]["id"]
                db.set_baseline(snapshot_id)
                snap = load_snapshot(db.conn, snapshot_id)
                console.print(f"[green]Baseline set to snapshot {snapshot_id}[/green]")
                console.print(f"  commit: {snap.commit_sha or '(none)'}")
                console.print(f"  timestamp: {snap.timestamp}")
                console.print(f"  files: {snap.file_count}, findings: {len(snap.findings)}")
            return

        if unpin:
            with HistoryDB(resolved_str) as db:
                db.clear_baseline()
                console.print("[green]Baseline cleared.[/green]")
            return

        # ── Normal diff flow ──────────────────────────────────────────
        from ..insights import InsightKernel
        from ..persistence.diff_engine import diff_snapshots
        from ..persistence.rename import detect_renames
        from ..persistence.writer import save_snapshot
        from ._diff_output import InsightDiffFormatter

        settings = resolve_settings(
            config=config,
            no_cache=False,
            workers=workers,
            verbose=verbose,
        )

        max_findings = settings.insights_max_findings

        # ── Step 1: Run current analysis and capture snapshot ────────
        kernel = InsightKernel(
            resolved_str,
            language="auto",
            settings=settings,
        )
        result, new_snapshot = kernel.run(
            max_findings=max_findings,
        )

        # ── Step 2: Save current snapshot ────────────────────────────
        with HistoryDB(resolved_str) as db:
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
                console.print("[yellow]No previous snapshot found to compare against.[/yellow]")
                console.print(
                    "[dim]Run the analysis with --save at least twice, or set a baseline "
                    "with 'diff --pin'.[/dim]"
                )
                raise typer.Exit(0)

            # ── Step 4: Detect renames ───────────────────────────────
            renames = {}
            if old_snapshot.commit_sha and new_snapshot.commit_sha:
                if old_snapshot.commit_sha != new_snapshot.commit_sha:
                    renames = detect_renames(
                        resolved_str,
                        old_snapshot.commit_sha,
                        new_snapshot.commit_sha,
                    )
                    if renames:
                        logger.info("Detected %d rename(s)", len(renames))

            # ── Step 5: Compute diff ─────────────────────────────────
            diff = diff_snapshots(
                old_snapshot,
                new_snapshot,
                renames=renames if renames else None,
            )

            # ── Step 6: Render ───────────────────────────────────────
            formatter = InsightDiffFormatter(console=console)
            fmt = "json" if json_output else "rich"
            formatter.render(diff, fmt=fmt, verbose=verbose)

    except typer.Exit:
        raise
    except ShannonInsightError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Unexpected error in diff")
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
    from ..persistence.reader import list_snapshots, load_snapshot, load_snapshot_by_commit

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

        console.print(f"[yellow]Could not find snapshot for ref '{ref}'.[/yellow]")
        return None

    if use_baseline:
        baseline_id = db.get_baseline_snapshot_id()
        if baseline_id is None:
            console.print("[yellow]No baseline set. Use 'diff --pin' first.[/yellow]")
            return None
        try:
            return load_snapshot(db.conn, baseline_id)
        except ValueError:
            console.print(f"[yellow]Baseline snapshot {baseline_id} no longer exists.[/yellow]")
            return None

    # Default: most recent snapshot before the current one
    snapshots = list_snapshots(db.conn, limit=5)
    for snap_info in snapshots:
        if snap_info["id"] != current_snapshot_id:
            return load_snapshot(db.conn, snap_info["id"])

    return None
