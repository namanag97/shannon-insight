"""Helper functions for finders."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shannon_insight.signals.models import SignalField


def compute_hotspot_median(field: SignalField) -> int:
    """Compute median of total_changes across non-test files.

    Excludes TEST role files to avoid skewing by test churn.
    Used by hotspot-filtered finders to skip dormant files.

    Args:
        field: SignalField with per_file signals

    Returns:
        Median total_changes value (int, not float)
    """
    changes = [
        fs.total_changes
        for fs in field.per_file.values()
        if fs.role != "TEST" and fs.total_changes > 0
    ]
    if not changes:
        return 0
    changes_sorted = sorted(changes)
    n = len(changes_sorted)
    # Use lower median for even-length lists (conservative)
    return changes_sorted[n // 2] if n % 2 == 1 else changes_sorted[n // 2 - 1]


# Finders that are structural-only (no hotspot filter)
STRUCTURAL_ONLY_FINDERS = frozenset(
    {
        "orphan_code",
        "hollow_code",
        "phantom_imports",
        "copy_paste_clone",
        "flat_architecture",
        "naming_drift",
    }
)
