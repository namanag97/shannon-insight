"""Backward-compatible re-export of AnalysisStore.

The canonical implementation now lives in store_v2.py. This module exists
solely to keep old import paths (``from shannon_insight.insights.store import
AnalysisStore``) working during the v1 → v2 migration.
"""

from .store_v2 import AnalysisStore

__all__ = ["AnalysisStore"]
