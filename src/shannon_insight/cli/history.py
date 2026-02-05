"""History CLI command -- list past analysis snapshots."""

import json
from pathlib import Path

import typer

from ..storage import HistoryDB
from ..storage.reader import list_snapshots
from . import app
from ._common import console


@app.command()
def history(
    ctx: typer.Context,
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Maximum number of snapshots to list",
        min=1,
        max=1000,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in machine-readable JSON format",
    ),
):
    """
    List past analysis runs stored in .shannon/history.db.

    Shows snapshot ID, commit SHA, timestamp, file count, and finding count
    for each recorded analysis run.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight history

      shannon-insight history --json

      shannon-insight history --limit 5
    """
    resolved = ctx.obj.get("path", Path.cwd()).resolve()
    db_path = resolved / ".shannon" / "history.db"

    if not db_path.exists():
        console.print(
            "[yellow]No history found.[/yellow] "
            "Run [bold]shannon-insight --save[/bold] first to create a snapshot."
        )
        raise typer.Exit(0)

    try:
        with HistoryDB(str(resolved)) as db:
            # Check for baseline to mark it in output
            baseline_id = db.get_baseline_snapshot_id()
            snapshots = list_snapshots(db.conn, limit=limit)

        if not snapshots:
            console.print("[yellow]No snapshots recorded yet.[/yellow]")
            raise typer.Exit(0)

        if json_output:
            _output_json(snapshots, baseline_id)
        else:
            _output_rich(snapshots, baseline_id)

    except Exception as e:
        console.print(f"[red]Error reading history:[/red] {e}")
        raise typer.Exit(1)


def _output_json(snapshots, baseline_id=None):
    """Machine-readable JSON output."""
    for s in snapshots:
        s["is_baseline"] = s["id"] == baseline_id if baseline_id else False
    print(json.dumps(snapshots, indent=2))


def _output_rich(snapshots, baseline_id=None):
    """Human-readable Rich table output."""
    from rich.table import Table

    table = Table(
        title="Analysis History",
        show_lines=False,
        pad_edge=True,
    )
    table.add_column("ID", style="bold", justify="right")
    table.add_column("Commit", style="cyan")
    table.add_column("Timestamp", style="green")
    table.add_column("Files", justify="right")
    table.add_column("Findings", justify="right", style="yellow")
    table.add_column("", style="dim")  # baseline marker

    for s in snapshots:
        commit = s["commit_sha"][:8] if s["commit_sha"] else "-"
        # Trim timestamp to just date + time (no microseconds/timezone)
        ts = s["timestamp"]
        if "T" in ts:
            ts = ts.replace("T", " ")
        if "+" in ts:
            ts = ts[: ts.index("+")]
        if "." in ts:
            ts = ts[: ts.index(".")]

        marker = "* baseline" if (baseline_id and s["id"] == baseline_id) else ""

        table.add_row(
            str(s["id"]),
            commit,
            ts,
            str(s["file_count"]),
            str(s["finding_count"]),
            marker,
        )

    console.print()
    console.print(table)
    console.print()
