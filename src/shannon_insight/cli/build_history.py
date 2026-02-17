"""Build historical snapshots from git history.

This command walks through git history at regular intervals, analyzes the
codebase at each point, and saves snapshots to the history database.

This enables:
- True temporal analysis (churn trajectories based on actual historical state)
- Directory hotspot tracking over time
- Architecture erosion detection
- Chronic problem identification
"""

import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer

from ..api import analyze
from ..logging_config import get_logger
from ..persistence import HistoryDB
from . import app
from ._common import console

logger = get_logger(__name__)


@app.command("build-history")
def build_history(
    ctx: typer.Context,
    since: str = typer.Option(
        "3 months ago",
        "--since",
        "-s",
        help="How far back to analyze (e.g., '3 months ago', '2024-01-01')",
    ),
    interval: str = typer.Option(
        "weekly",
        "--interval",
        "-i",
        help="Snapshot interval: 'daily', 'weekly', 'monthly'",
    ),
    max_snapshots: int = typer.Option(
        52,
        "--max",
        "-n",
        help="Maximum number of snapshots to create",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing snapshots",
    ),
):
    """
    Build historical snapshots by analyzing the codebase at past commits.

    This walks through git history at the specified interval and creates
    analysis snapshots at each checkpoint. These snapshots enable true
    temporal analysis:

    - Churn trajectories based on actual code changes over time
    - Directory hotspot trends
    - Architecture erosion detection (violations increasing)
    - Chronic problem identification (findings persisting)

    [bold cyan]Examples:[/bold cyan]

      shannon-insight build-history

      shannon-insight build-history --since "6 months ago" --interval weekly

      shannon-insight build-history --since 2024-01-01 --interval monthly --max 12
    """
    resolved = ctx.obj.get("path", Path.cwd()).resolve()

    # Verify git repo
    if not _is_git_repo(resolved):
        console.print("[red]Error:[/red] Not a git repository")
        raise typer.Exit(1)

    # Parse interval
    interval_days = _parse_interval(interval)
    if interval_days is None:
        console.print(f"[red]Error:[/red] Invalid interval '{interval}'. Use daily, weekly, or monthly.")
        raise typer.Exit(1)

    # Find checkpoint commits
    console.print(f"[cyan]Finding checkpoints since {since}...[/cyan]")
    checkpoints = _find_checkpoints(resolved, since, interval_days, max_snapshots)

    if not checkpoints:
        console.print("[yellow]No commits found in the specified range.[/yellow]")
        raise typer.Exit(0)

    console.print(f"Found [bold]{len(checkpoints)}[/bold] checkpoints to analyze")

    # Check existing snapshots
    db_path = resolved / ".shannon"
    db_path.mkdir(exist_ok=True)

    with HistoryDB(str(resolved)) as db:
        existing_shas = set(db.get_all_snapshot_shas())

    if not force:
        new_checkpoints = [(sha, date) for sha, date in checkpoints if sha not in existing_shas]
        skipped = len(checkpoints) - len(new_checkpoints)
        if skipped > 0:
            console.print(f"[dim]Skipping {skipped} existing snapshots (use --force to overwrite)[/dim]")
        checkpoints = new_checkpoints

    if not checkpoints:
        console.print("[green]All snapshots already exist.[/green]")
        raise typer.Exit(0)

    # Create worktree for analysis
    worktree_dir = None
    try:
        worktree_dir = Path(tempfile.mkdtemp(prefix="shannon-history-"))
        console.print(f"[dim]Using temporary worktree: {worktree_dir}[/dim]")

        # Analyze each checkpoint
        for i, (sha, date) in enumerate(checkpoints, 1):
            date_str = date.strftime("%Y-%m-%d")
            console.print(f"\n[bold][{i}/{len(checkpoints)}][/bold] Analyzing {sha[:8]} ({date_str})...")

            try:
                # Checkout commit in worktree
                _checkout_worktree(resolved, worktree_dir, sha)

                # Run analysis
                result, snapshot = analyze(worktree_dir, max_findings=500)

                # Override commit_sha and timestamp with the historical values
                snapshot.commit_sha = sha
                snapshot.timestamp = date.isoformat()

                # Save to history DB
                with HistoryDB(str(resolved)) as db:
                    db.save_snapshot(snapshot)

                console.print(
                    f"  [green]✓[/green] {result.store_summary.total_files} files, "
                    f"{len(result.findings)} findings"
                )

            except Exception as e:
                console.print(f"  [red]✗[/red] Failed: {e}")
                logger.warning(f"Failed to analyze {sha}: {e}")

    finally:
        # Cleanup worktree
        if worktree_dir and worktree_dir.exists():
            _cleanup_worktree(resolved, worktree_dir)
            shutil.rmtree(worktree_dir, ignore_errors=True)

    console.print(f"\n[green]Done![/green] Created {len(checkpoints)} historical snapshots.")
    console.print("[dim]View with: shannon-insight history[/dim]")


def _is_git_repo(path: Path) -> bool:
    """Check if path is a git repository."""
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--git-dir"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _parse_interval(interval: str) -> Optional[int]:
    """Parse interval string to days."""
    intervals = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
    }
    return intervals.get(interval.lower())


def _find_checkpoints(
    repo_path: Path,
    since: str,
    interval_days: int,
    max_snapshots: int,
) -> list[tuple[str, datetime]]:
    """Find commits at regular intervals.

    Returns list of (sha, datetime) tuples, newest first.
    """
    # Get all commits since the specified date
    try:
        result = subprocess.run(
            [
                "git", "-C", str(repo_path),
                "log", "--format=%H %at", f"--since={since}",
                "--reverse",  # oldest first for processing
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                sha = parts[0]
                timestamp = int(parts[1])
                dt = datetime.fromtimestamp(timestamp)
                commits.append((sha, dt))

    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    if not commits:
        return []

    # Sample at intervals
    checkpoints = []
    last_checkpoint_date = None

    for sha, dt in commits:
        if last_checkpoint_date is None:
            checkpoints.append((sha, dt))
            last_checkpoint_date = dt
        elif (dt - last_checkpoint_date).days >= interval_days:
            checkpoints.append((sha, dt))
            last_checkpoint_date = dt

        if len(checkpoints) >= max_snapshots:
            break

    # Return newest first (reverse)
    return list(reversed(checkpoints))


def _checkout_worktree(repo_path: Path, worktree_path: Path, sha: str) -> None:
    """Checkout a commit into a worktree directory."""
    # Remove existing worktree if present
    _cleanup_worktree(repo_path, worktree_path)

    # Create new worktree
    result = subprocess.run(
        [
            "git", "-C", str(repo_path),
            "worktree", "add", "--detach", str(worktree_path), sha,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to create worktree: {result.stderr}")


def _cleanup_worktree(repo_path: Path, worktree_path: Path) -> None:
    """Remove a worktree."""
    try:
        subprocess.run(
            ["git", "-C", str(repo_path), "worktree", "remove", "--force", str(worktree_path)],
            capture_output=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
