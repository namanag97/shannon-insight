"""GitHub Actions formatter — annotations and PR comment body."""

from typing import List

from ..models import AnalysisContext, AnomalyReport, DiffReport
from .base import BaseFormatter


class GithubFormatter(BaseFormatter):
    """Output GitHub Actions ``::warning`` / ``::error`` annotations.

    Also generates a Markdown comment body suitable for ``gh pr comment``.
    """

    def render(self, reports, context: AnalysisContext) -> None:
        print(self.format(reports, context))

    def format(self, reports, context: AnalysisContext) -> str:
        # If we receive DiffReport list, use diff-aware output
        if reports and isinstance(reports[0], DiffReport):
            return self._format_diff(reports, context)
        return self._format_reports(reports, context)

    # -- standard reports --

    def _format_reports(self, reports: List[AnomalyReport], context: AnalysisContext) -> str:
        lines: list[str] = []
        for r in reports:
            level = "error" if r.overall_score >= 3.0 else "warning"
            msg = f"Score {r.overall_score:.3f} — {', '.join(r.anomaly_flags)}"
            lines.append(f"::{level} file={r.file}::{msg}")
        return "\n".join(lines)

    # -- diff reports --

    def _format_diff(self, diffs: List[DiffReport], context: AnalysisContext) -> str:
        lines: list[str] = []

        # Annotations
        for d in diffs:
            if d.status == "regressed":
                delta = f"+{d.score_delta:.3f}" if d.score_delta else ""
                lines.append(f"::warning file={d.file}::Score regressed {delta}")
            elif d.status == "new":
                lines.append(
                    f"::notice file={d.file}::New file (score {d.current.overall_score:.3f})"
                )

        # Markdown summary for PR comment
        lines.append("")
        lines.append("## Shannon Insight Diff")
        lines.append("")
        lines.append("| File | Score | Delta | Status |")
        lines.append("|------|-------|-------|--------|")
        for d in diffs:
            delta_str = f"{d.score_delta:+.3f}" if d.score_delta is not None else "—"
            lines.append(
                f"| `{d.file}` | {d.current.overall_score:.3f} | {delta_str} | {d.status} |"
            )
        lines.append("")

        counts = {}
        for d in diffs:
            counts[d.status] = counts.get(d.status, 0) + 1
        summary_parts = [f"{count} {status}" for status, count in sorted(counts.items())]
        lines.append(f"**Summary:** {', '.join(summary_parts)}")

        return "\n".join(lines)
