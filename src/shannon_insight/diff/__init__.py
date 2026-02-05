"""Diff layer — change-scoped analysis and snapshot diffing."""

from .models import SnapshotDiff, MetricDelta, FindingDelta, FileDelta
from .engine import diff_snapshots

__all__ = [
    "FileDelta",
    "FindingDelta",
    "MetricDelta",
    "SnapshotDiff",
    "diff_snapshots",
]

# Phase 3 change-scoped analysis (may not be present yet)
try:
    from .scope import (
        ChangeScopedReport,
        FileRiskSummary,
        build_scoped_report,
        compute_blast_radius,
        get_changed_files,
        get_merge_base_files,
    )
    __all__ += [
        "ChangeScopedReport",
        "FileRiskSummary",
        "build_scoped_report",
        "compute_blast_radius",
        "get_changed_files",
        "get_merge_base_files",
    ]
except ImportError:
    pass
