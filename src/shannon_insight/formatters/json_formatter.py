"""JSON formatter for Shannon Insight."""

import json
from dataclasses import asdict
from typing import List

from .base import BaseFormatter
from ..models import AnomalyReport, AnalysisContext


class JsonFormatter(BaseFormatter):
    """Render reports as JSON."""

    def render(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        print(self.format(reports, context))

    def format(self, reports: List[AnomalyReport], context: AnalysisContext) -> str:
        data = [asdict(r) for r in reports]
        return json.dumps(data, indent=2)
