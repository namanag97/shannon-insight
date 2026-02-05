"""Health CLI command -- show codebase health trends over time."""

import json
from pathlib import Path

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
    return "".join(blocks[min(8, int((v - mn) / (mx - mn) * 8))] for v in values)


# Direction metadata for health metrics — developer-friendly labels.
_HEALTH_METRICS = {
    "active_findings": ("Issues found", "lower_better", "findings"),
    "cycle_count": ("Circular dependencies", "lower_better", "cycles"),
    "modularity": ("Module separation", "higher_better", "boundaries"),
    "fiedler_value": ("Connectivity", "higher_better", "connectivity"),
    "total_edges": ("Dependencies", "neutral", "dependencies"),
}


@app.command()
def health(
    ctx: typer.Context,
    last_n: int = typer.Option(
        20,
        "--last",
        "-n",
        help="Number of recent snapshots to include",
        min=2,
        max=200,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output in machine-readable JSON format",
    ),
):
    """
    Show codebase health trends over time.

    Queries .shannon/history.db for codebase-level signals and shows a
    sparkline trend plus a directional assessment for each metric.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight health

      shannon-insight health --last 10

      shannon-insight health --json
    """
    from ..storage import HistoryDB
    from ..storage.queries import HistoryQuery

    resolved = ctx.obj.get("path", Path.cwd()).resolve()
    db_path = resolved / ".shannon" / "history.db"

    if not db_path.exists():
        console.print(
            "[yellow]No history found.[/yellow] "
            "Run [bold]shannon-insight --save[/bold] first to create snapshots."
        )
        raise typer.Exit(0)

    with HistoryDB(str(resolved)) as db:
        query = HistoryQuery(db.conn)
        points = query.codebase_health(last_n)

    if not points:
        console.print("[yellow]No health data available. Run the analysis first.[/yellow]")
        raise typer.Exit(0)

    # -- JSON output --
    if json_output:
        print(
            json.dumps(
                [
                    {
                        "snapshot_id": p.snapshot_id,
                        "timestamp": p.timestamp,
                        "metrics": p.metrics,
                    }
                    for p in points
                ],
                indent=2,
            )
        )
        return

    # -- Rich output --
    console.print()
    console.print(f"[bold cyan]CODEBASE HEALTH[/bold cyan] -- {len(points)} snapshots")
    console.print()

    table = Table(show_header=True, show_lines=False, pad_edge=True)
    table.add_column("Metric", min_width=24)
    table.add_column("Current", justify="right")
    table.add_column("Trend", min_width=15)
    table.add_column("Direction")

    for metric_key, (label, direction, _aspect) in _HEALTH_METRICS.items():
        # Collect non-None values for this metric across all snapshots.
        values = [p.metrics.get(metric_key) for p in points]
        values = [v for v in values if v is not None]
        if not values:
            continue

        current = values[-1]
        spark = _sparkline(values)

        # Determine trend direction by comparing first vs second half.
        if len(values) >= 2:
            half = len(values) // 2
            first_half_avg = sum(values[:half]) / max(1, half)
            second_half_avg = sum(values[half:]) / max(1, len(values) - half)
            delta = second_half_avg - first_half_avg

            if abs(delta) < 0.001:
                dir_str = "[dim]stable[/dim]"
            elif direction == "higher_better":
                dir_str = "[green]improving[/green]" if delta > 0 else "[red]declining[/red]"
            elif direction == "lower_better":
                dir_str = "[green]improving[/green]" if delta < 0 else "[red]worsening[/red]"
            else:
                dir_str = "[dim]changing[/dim]"
        else:
            dir_str = "[dim]--[/dim]"

        # Format the current value: integers for counts, decimals for floats.
        if isinstance(current, float) and current != int(current):
            current_str = f"{current:.4f}"
        else:
            current_str = str(int(current))

        table.add_row(label, current_str, spark, dir_str)

    console.print(table)
    console.print()
