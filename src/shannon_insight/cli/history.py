"""History CLI command -- list past analysis snapshots."""

import json
from pathlib import Path

import typer

from . import app
from ._common import console
from ..storage import HistoryDB
from ..storage.reader import list_snapshots


@app.command()
def history(
    path: Path = typer.Argument(
        Path("."),
        help="Path to the project root (where .shannon/ lives)",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Maximum number of snapshots to list",
        min=1,
        max=1000,
    ),
    fmt: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich (table) or json",
    ),
):
    """
    List past analysis runs stored in .shannon/history.db.

    Shows snapshot ID, commit SHA, timestamp, file count, and finding count
    for each recorded analysis run.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight . history

      shannon-insight . history --format json

      shannon-insight . history --limit 5
    """
    resolved = Path(path).resolve()
    db_path = resolved / ".shannon" / "history.db"

    if not db_path.exists():
        console.print(
            "[yellow]No history found.[/yellow] "
            "Run [bold]shannon-insight . insights[/bold] first to create a snapshot."
        )
        raise typer.Exit(0)

    try:
        with HistoryDB(str(resolved)) as db:
            snapshots = list_snapshots(db.conn, limit=limit)

        if not snapshots:
            console.print("[yellow]No snapshots recorded yet.[/yellow]")
            raise typer.Exit(0)

        if fmt == "json":
            _output_json(snapshots)
        else:
            _output_rich(snapshots)

    except Exception as e:
        console.print(f"[red]Error reading history:[/red] {e}")
        raise typer.Exit(1)


def _output_json(snapshots):
    """Machine-readable JSON output."""
    print(json.dumps(snapshots, indent=2))


def _output_rich(snapshots):
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

        table.add_row(
            str(s["id"]),
            commit,
            ts,
            str(s["file_count"]),
            str(s["finding_count"]),
        )

    console.print()
    console.print(table)
    console.print()
