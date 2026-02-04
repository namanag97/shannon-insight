"""CSV formatter for Shannon Insight."""

import csv
import io
from typing import List

from .base import BaseFormatter
from ..models import AnomalyReport, AnalysisContext


class CsvFormatter(BaseFormatter):
    """Render reports as CSV."""

    def render(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        print(self.format(reports, context), end="")

    def format(self, reports: List[AnomalyReport], context: AnalysisContext) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "file", "overall_score", "confidence",
            "structural_entropy", "network_centrality",
            "churn_volatility", "semantic_coherence", "cognitive_load",
            "anomaly_flags",
        ])
        for r in reports:
            writer.writerow([
                r.file, f"{r.overall_score:.4f}", f"{r.confidence:.4f}",
                f"{r.primitives.structural_entropy:.4f}",
                f"{r.primitives.network_centrality:.4f}",
                f"{r.primitives.churn_volatility:.4f}",
                f"{r.primitives.semantic_coherence:.4f}",
                f"{r.primitives.cognitive_load:.4f}",
                ";".join(r.anomaly_flags),
            ])
        return output.getvalue()
