"""Trend CLI command -- show how a file's metrics change over time."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from . import app
from ._common import console


def _sparkline(values: list) -> str:
    """Generate an ASCII sparkline from a list of numeric values."""
    if not values:
        return ""
    blocks = " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
    mn, mx = min(values), max(values)
    if mx == mn:
        return blocks[4] * len(values)
    return "".join(
        blocks[min(8, int((v - mn) / (mx - mn) * 8))] for v in values
    )


@app.command()
def trend(
    filepath: str = typer.Argument(
        ..., help="File path to show trends for"
    ),
    path: Path = typer.Argument(
        Path("."),
        help="Project root (where .shannon/ lives)",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    metric: str = typer.Option(
        "cognitive_load",
        "--metric",
        "-m",
        help="Metric to trend (e.g. cognitive_load, semantic_coherence)",
    ),
    last_n: int = typer.Option(
        20,
        "--last",
        "-n",
        help="Number of recent snapshots to include",
        min=2,
        max=200,
    ),
    fmt: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich (table) or json",
    ),
):
    """
    Show how a file's metrics have changed over time.

    Queries .shannon/history.db for the given file and metric, showing a
    sparkline and per-snapshot delta table.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight . trend src/engine.py

      shannon-insight . trend src/engine.py --metric semantic_coherence

      shannon-insight . trend src/engine.py --last 10 --format json
    """
    from ..storage import HistoryDB
    from ..storage.queries import HistoryQuery

    resolved = Path(path).resolve()
    db_path = resolved / ".shannon" / "history.db"

    if not db_path.exists():
        console.print(
            "[yellow]No history found.[/yellow] "
            "Run [bold]shannon-insight . insights[/bold] first to create snapshots."
        )
        raise typer.Exit(0)

    with HistoryDB(str(resolved)) as db:
        query = HistoryQuery(db.conn)
        points = query.file_trend(filepath, metric, last_n)

    if not points:
        console.print(
            f"[yellow]No trend data for[/yellow] {filepath} / {metric}"
        )
        raise typer.Exit(0)

    # ── JSON output ───────────────────────────────────────────────────
    if fmt == "json":
        print(
            json.dumps(
                [
                    {
                        "snapshot_id": p.snapshot_id,
                        "commit": p.commit_sha,
                        "timestamp": p.timestamp,
                        "value": p.value,
                    }
                    for p in points
                ],
                indent=2,
            )
        )
        return

    # ── Rich output ───────────────────────────────────────────────────
    values = [p.value for p in points]
    spark = _sparkline(values)

    console.print()
    console.print(
        f"[bold cyan]Trend:[/bold cyan] {filepath} "
        f"-- {metric} (last {len(points)} snapshots)"
    )
    console.print(f"  {spark}")
    console.print()

    table = Table(show_header=True, show_lines=False, pad_edge=True)
    table.add_column("Commit", style="dim", max_width=8)
    table.add_column("Date")
    table.add_column("Value", justify="right")
    table.add_column("Delta", justify="right")

    prev: Optional[float] = None
    for p in points:
        commit = (p.commit_sha or "")[:7]
        delta_str = ""
        if prev is not None:
            d = p.value - prev
            if abs(d) > 0.001:
                color = "red" if d > 0 else "green"
                delta_str = f"[{color}]{d:+.4f}[/{color}]"
        table.add_row(commit, p.timestamp[:10], f"{p.value:.4f}", delta_str)
        prev = p.value

    console.print(table)
    console.print()
