"""Quiet formatter — file paths only."""

from typing import List

from .base import BaseFormatter
from ..models import AnomalyReport, AnalysisContext


class QuietFormatter(BaseFormatter):
    """Render just file paths, one per line."""

    def render(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        print(self.format(reports, context))

    def format(self, reports: List[AnomalyReport], context: AnalysisContext) -> str:
        return "\n".join(r.file for r in reports)
