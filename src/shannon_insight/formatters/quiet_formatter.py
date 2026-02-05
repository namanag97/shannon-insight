"""Quiet formatter — file paths only."""

from typing import List

from ..models import AnalysisContext, AnomalyReport
from .base import BaseFormatter


class QuietFormatter(BaseFormatter):
    """Render just file paths, one per line."""

    def render(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        print(self.format(reports, context))

    def format(self, reports: List[AnomalyReport], context: AnalysisContext) -> str:
        return "\n".join(r.file for r in reports)
