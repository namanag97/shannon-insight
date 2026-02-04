"""Insight engine — cross-references structural, temporal, and per-file signals."""

from .models import Finding, Evidence, InsightResult
from .kernel import InsightKernel

__all__ = [
    "Finding",
    "Evidence",
    "InsightResult",
    "InsightKernel",
]
