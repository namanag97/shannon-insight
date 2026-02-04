"""Diff formatter — shows score deltas between current and baseline."""

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .base import BaseFormatter
from ..models import AnomalyReport, AnalysisContext, DiffReport

console = Console(stderr=True)

_STATUS_STYLE = {
    "regressed": "[red]regressed[/red]",
    "new": "[yellow]new[/yellow]",
    "improved": "[green]improved[/green]",
    "modified": "[blue]modified[/blue]",
}

_DELTA_ARROWS = {
    "regressed": "[red]+{delta:.3f} ↑[/red]",
    "improved": "[green]{delta:.3f} ↓[/green]",
    "new": "[yellow]—[/yellow]",
    "modified": "[dim]{delta:.3f}[/dim]",
}


class DiffFormatter(BaseFormatter):
    """Rich terminal output showing diff results."""

    def render(self, reports, context: AnalysisContext) -> None:
        # ``reports`` here is List[DiffReport]
        diff_reports: List[DiffReport] = reports
        self._print_diff_table(diff_reports, context)

    def format(self, reports, context: AnalysisContext) -> str:
        self.render(reports, context)
        return ""

    def _print_diff_table(self, diffs: List[DiffReport], context: AnalysisContext) -> None:
        # Summary counts
        counts = {}
        for d in diffs:
            counts[d.status] = counts.get(d.status, 0) + 1

        parts = []
        for status in ("regressed", "new", "modified", "improved"):
            if counts.get(status, 0) > 0:
                parts.append(f"{_STATUS_STYLE[status]}: {counts[status]}")
        summary = "  |  ".join(parts) if parts else "No changes"

        console.print(Panel(summary, title="[bold cyan]Diff Summary[/bold cyan]", expand=False))
        console.print()

        if not diffs:
            console.print("[green]No score changes detected.[/green]")
            return

        table = Table(title="Score Deltas", expand=True)
        table.add_column("File", style="yellow", no_wrap=False, ratio=3)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Delta", justify="right", width=14)
        table.add_column("Status", justify="center", width=12)

        for d in diffs:
            delta_str = _DELTA_ARROWS.get(d.status, "—")
            if d.score_delta is not None:
                delta_str = delta_str.format(delta=d.score_delta)

            table.add_row(
                d.file,
                f"{d.current.overall_score:.3f}",
                delta_str,
                _STATUS_STYLE.get(d.status, d.status),
            )

        console.print(table)
        console.print()
