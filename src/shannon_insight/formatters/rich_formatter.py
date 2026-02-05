"""Rich terminal formatter for Shannon Insight."""

from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models import AnalysisContext, AnomalyReport
from .base import BaseFormatter

console = Console(stderr=True)


def _severity_label(score: float) -> str:
    if score >= 3.0:
        return "[red bold]critical[/red bold]"
    elif score >= 2.0:
        return "[red]high[/red]"
    elif score >= 1.0:
        return "[yellow]moderate[/yellow]"
    else:
        return "[green]low[/green]"


def _confidence_label(conf: float) -> str:
    if conf >= 0.75:
        return "[green]high[/green]"
    elif conf >= 0.4:
        return "[yellow]moderate[/yellow]"
    else:
        return "[red]low[/red]"


def _zscore_label(z: float) -> str:
    az = abs(z)
    if az >= 3.0:
        return "[red bold]anomalous[/red bold]"
    elif az >= 1.5:
        return "[yellow]elevated[/yellow]"
    else:
        return "[dim]normal[/dim]"


class RichFormatter(BaseFormatter):
    """Rich terminal output with summary panel, table, and detailed report."""

    def render(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        self._print_summary(reports, context)
        self._print_report(reports, context)

    def format(self, reports: List[AnomalyReport], context: AnalysisContext) -> str:
        # Rich output goes directly to console; return empty string
        self.render(reports, context)
        return ""

    def render_explain(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        """Print deep-dive explanation for file(s) matching a pattern."""
        pattern = context.explain_pattern or ""
        matching = [r for r in reports if pattern in r.file]

        if not matching:
            console.print(
                f"[yellow]No files matching '{pattern}' found in analysis results.[/yellow]"
            )
            return

        threshold = (
            context.settings.z_score_threshold
            if hasattr(context.settings, "z_score_threshold")
            else 1.5
        )

        for report in matching:
            console.print(
                Panel(
                    f"[bold]{report.file}[/bold]",
                    title="[bold cyan]Deep Dive[/bold cyan]",
                    expand=False,
                )
            )
            console.print()

            console.print("[bold]Raw Primitives:[/bold]")
            for label, val, note in [
                (
                    "Structural Entropy",
                    report.primitives.structural_entropy,
                    "high = complex structure"
                    if report.primitives.structural_entropy > 0.7
                    else "within typical range",
                ),
                (
                    "Network Centrality",
                    report.primitives.network_centrality,
                    "high = heavily depended on"
                    if report.primitives.network_centrality > 0.5
                    else "within typical range",
                ),
                (
                    "Churn Volatility",
                    report.primitives.churn_volatility,
                    "high = frequently changed"
                    if report.primitives.churn_volatility > 0.5
                    else "within typical range",
                ),
                (
                    "Semantic Coherence",
                    report.primitives.semantic_coherence,
                    "low = mixed responsibilities"
                    if report.primitives.semantic_coherence < 0.3
                    else "within typical range",
                ),
                (
                    "Cognitive Load",
                    report.primitives.cognitive_load,
                    "high = hard to understand"
                    if report.primitives.cognitive_load > 0.6
                    else "within typical range",
                ),
            ]:
                console.print(f"  {label:22s}  {val:.4f}  [dim]({note})[/dim]")
            console.print()

            console.print(f"[bold]Normalized Z-Scores[/bold] (threshold: {threshold:.1f}):")
            for name, val in [
                ("Structural Entropy", report.normalized_primitives.structural_entropy),
                ("Network Centrality", report.normalized_primitives.network_centrality),
                ("Churn Volatility", report.normalized_primitives.churn_volatility),
                ("Semantic Coherence", report.normalized_primitives.semantic_coherence),
                ("Cognitive Load", report.normalized_primitives.cognitive_load),
            ]:
                marker = " [red]<< ANOMALY[/red]" if abs(val) > threshold else ""
                console.print(f"  {name:22s}  {val:+.3f}s  {_zscore_label(val)}{marker}")
            console.print()

            console.print(
                f"[bold]Overall Score:[/bold] [red]{report.overall_score:.4f}[/red] "
                f"({_severity_label(report.overall_score)})"
            )
            console.print(
                f"[bold]Confidence:[/bold]    [blue]{report.confidence:.4f}[/blue] "
                f"({_confidence_label(report.confidence)})"
            )
            console.print()

            if report.anomaly_flags:
                console.print("[bold]Anomaly Flags:[/bold]")
                for flag in report.anomaly_flags:
                    console.print(f"  [red]-[/red] {flag}")
                console.print()

            if report.root_causes:
                console.print("[bold]Root Causes:[/bold]")
                for cause in report.root_causes:
                    console.print(f"  [red]![/red] {cause}")
                console.print()

            if report.recommendations:
                console.print("[bold]Recommendations:[/bold]")
                for rec in report.recommendations:
                    console.print(f"  [green]->[/green] {rec}")
                console.print()

            console.print("[dim]" + "-" * 80 + "[/dim]")
            console.print()

    # -- private helpers --

    def _print_summary(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        top_n = context.top_n
        num_anomalies = len(reports)
        total = context.total_files_scanned
        pct = (num_anomalies / total * 100) if total > 0 else 0
        avg_confidence = (
            sum(r.confidence for r in reports) / num_anomalies if num_anomalies > 0 else 0.0
        )

        lang_display = (
            ", ".join(context.detected_languages) if context.detected_languages else "unknown"
        )
        summary_text = (
            f"Scanned [bold]{total}[/bold] files "
            f"([cyan]{lang_display}[/cyan])  |  "
            f"[yellow]{num_anomalies}[/yellow] anomalies "
            f"([yellow]{pct:.0f}%[/yellow])  |  "
            f"Avg confidence: [blue]{avg_confidence:.2f}[/blue] "
            f"({_confidence_label(avg_confidence)})"
        )
        console.print(Panel(summary_text, title="[bold cyan]Summary[/bold cyan]", expand=False))
        console.print()

        if not reports:
            return

        table = Table(
            title=f"Top {min(top_n, len(reports))} Files Requiring Attention", expand=True
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("File", style="yellow", no_wrap=False, ratio=3)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Severity", justify="center", width=10)
        table.add_column("Confidence", justify="right", width=14)
        table.add_column("Primary Issue", style="white", ratio=2)

        _short = {
            "structural_entropy_high": "entropy high",
            "structural_entropy_low": "entropy low",
            "high_centrality": "high centrality",
            "high_volatility": "high volatility",
            "semantic_coherence_low": "coherence low",
            "semantic_coherence_high": "coherence high",
            "high_cognitive_load": "high cog. load",
        }

        for i, report in enumerate(reports[:top_n], 1):
            flags = [_short.get(f, f) for f in report.anomaly_flags]
            primary = ", ".join(flags) if flags else "-"
            table.add_row(
                str(i),
                report.file,
                f"[red]{report.overall_score:.3f}[/red]",
                _severity_label(report.overall_score),
                f"[blue]{report.confidence:.2f}[/blue] ({_confidence_label(report.confidence)})",
                primary,
            )

        console.print(table)
        console.print()

    def _print_report(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        top_n = context.top_n
        console.print("[bold cyan]=" * 40)
        console.print(f"[bold cyan]TOP {min(top_n, len(reports))} FILES REQUIRING ATTENTION")
        console.print("[bold cyan]=" * 40)
        console.print()

        for i, report in enumerate(reports[:top_n], 1):
            console.print(f"[bold yellow]{i}. {report.file}[/bold yellow]")
            console.print(
                f"   Overall Score: [red]{report.overall_score:.3f}[/red] "
                f"({_severity_label(report.overall_score)})  "
                f"Confidence: [blue]{report.confidence:.2f}[/blue] "
                f"({_confidence_label(report.confidence)})"
            )
            console.print()

            console.print("   [dim]Raw Primitives:[/dim]")
            for label, val, note in [
                (
                    "Structural Entropy",
                    report.primitives.structural_entropy,
                    "high = complex structure"
                    if report.primitives.structural_entropy > 0.7
                    else "within typical range",
                ),
                (
                    "Network Centrality",
                    report.primitives.network_centrality,
                    "high = heavily depended on"
                    if report.primitives.network_centrality > 0.5
                    else "within typical range",
                ),
                (
                    "Churn Volatility",
                    report.primitives.churn_volatility,
                    "high = frequently changed"
                    if report.primitives.churn_volatility > 0.5
                    else "within typical range",
                ),
                (
                    "Semantic Coherence",
                    report.primitives.semantic_coherence,
                    "low = mixed responsibilities"
                    if report.primitives.semantic_coherence < 0.3
                    else "within typical range",
                ),
                (
                    "Cognitive Load",
                    report.primitives.cognitive_load,
                    "high = hard to understand"
                    if report.primitives.cognitive_load > 0.6
                    else "within typical range",
                ),
            ]:
                console.print(f"     - {label:22s}  {val:.3f}  [dim]({note})[/dim]")
            console.print()

            console.print("   [dim]Normalized (Z-Scores):[/dim]")
            for label, val in [
                ("Structural Entropy", report.normalized_primitives.structural_entropy),
                ("Network Centrality", report.normalized_primitives.network_centrality),
                ("Churn Volatility", report.normalized_primitives.churn_volatility),
                ("Semantic Coherence", report.normalized_primitives.semantic_coherence),
                ("Cognitive Load", report.normalized_primitives.cognitive_load),
            ]:
                console.print(f"     - {label:22s}  {val:+.2f}s  {_zscore_label(val)}")
            console.print()

            if report.root_causes:
                console.print("   [dim]Root Causes:[/dim]")
                for cause in report.root_causes:
                    console.print(f"     [red]![/red] {cause}")
                console.print()

            if report.recommendations:
                console.print("   [dim]Recommendations:[/dim]")
                for rec in report.recommendations:
                    console.print(f"     [green]->[/green] {rec}")
                console.print()

            console.print("[dim]" + "-" * 80 + "[/dim]")
            console.print()
