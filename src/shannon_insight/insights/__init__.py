"""Insight engine — cross-references structural, temporal, and per-file signals."""

from .kernel import InsightKernel
from .models import Evidence, Finding, InsightResult

__all__ = [
    "Finding",
    "Evidence",
    "InsightResult",
    "InsightKernel",
]
