"""Churn volatility via filesystem modification timestamps."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ...scanning.models import FileMetrics
from ..base import PrimitivePlugin


class VolatilityPrimitive(PrimitivePlugin):
    name = "churn_volatility"
    display_name = "Churn Volatility"
    short_name = "churn"
    description = "Instability of change patterns"
    direction = "high_is_bad"
    default_weight = 0.20

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        now = datetime.now().timestamp()
        ages = [now - f.last_modified for f in files]
        if not ages:
            return {}
        max_age = max(ages)
        return {
            f.path: (1 - (now - f.last_modified) / max_age) if max_age > 0 else 0 for f in files
        }

    def interpret(self, v: float) -> str:
        if v > 0.5:
            return "high = frequently changed"
        return "within typical range"
