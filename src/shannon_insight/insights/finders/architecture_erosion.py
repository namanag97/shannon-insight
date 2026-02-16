"""ArchitectureErosionFinder — violation_rate increasing over 3+ snapshots.

Detects when architectural health is degrading over time by tracking
the violation_rate global signal across snapshots.
"""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from ...persistence.queries import get_global_signal_time_series
from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store import AnalysisStore


class ArchitectureErosionFinder:
    """Identifies architecture degradation from violation_rate trends.

    Architecture erosion occurs when the violation_rate (ratio of
    layer/boundary violations) increases across 3+ consecutive snapshots.
    This indicates the codebase is accumulating architectural debt.

    Attributes
    ----------
    name : str
        Finder identifier.
    requires : set[str]
        Required store slots (none for this finder).
    min_snapshots : int
        Minimum snapshots required to detect trend (default 3).
    erosion_threshold : float
        Minimum total increase to trigger (default 0.05 = 5%).
    """

    name = "architecture_erosion"
    requires: set[str] = set()  # Uses persistence layer, not store

    def __init__(self, min_snapshots: int = 3, erosion_threshold: float = 0.05):
        self.min_snapshots = min_snapshots
        self.erosion_threshold = erosion_threshold

    def find(
        self,
        store: AnalysisStore,
        db_conn: sqlite3.Connection | None = None,
    ) -> list[Finding]:
        """Find architecture erosion from violation_rate trends.

        Parameters
        ----------
        store:
            The analysis store (not used, but part of interface).
        db_conn:
            Optional database connection. If not provided, returns empty list.

        Returns
        -------
        list[Finding]
            Single finding if erosion detected, empty list otherwise.
        """
        if db_conn is None:
            return []

        # Get violation_rate time series
        points = get_global_signal_time_series(
            db_conn, "violation_rate", limit=self.min_snapshots + 2
        )

        if len(points) < self.min_snapshots:
            return []

        # Check for consistent increase
        values = [p.value for p in points]
        increasing_count = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])

        # Need most transitions to be increasing
        if increasing_count < self.min_snapshots - 1:
            return []

        # Check total increase exceeds threshold
        total_increase = values[-1] - values[0]
        if total_increase < self.erosion_threshold:
            return []

        # Calculate severity based on rate of erosion
        erosion_rate = total_increase / len(values)
        severity = min(1.0, 0.65 + erosion_rate * 2)  # Base 0.65, scale with rate

        evidence = [
            Evidence(
                signal="violation_rate",
                value=values[-1],
                percentile=100.0,
                description=f"increased from {values[0]:.2%} to {values[-1]:.2%} over {len(values)} snapshots",
            ),
            Evidence(
                signal="erosion_rate",
                value=erosion_rate,
                percentile=100.0,
                description=f"average increase of {erosion_rate:.2%} per snapshot",
            ),
        ]

        return [
            Finding(
                finding_type="architecture_erosion",
                severity=severity,
                title=f"Architecture erosion: violation rate increased {total_increase:.1%} over {len(values)} snapshots",
                files=[],  # Codebase-level finding
                evidence=evidence,
                suggestion=self._build_suggestion(values, increasing_count),
                confidence=min(1.0, increasing_count / len(values)),
                effort="HIGH",
                scope="CODEBASE",
            )
        ]

    def _build_suggestion(self, values: list[float], increasing_count: int) -> str:
        """Build actionable suggestion for architecture erosion."""
        current_rate = values[-1]

        if current_rate > 0.2:  # >20% violations is severe
            urgency = "Critical"
            action = (
                "Immediately halt new feature development and focus on fixing "
                "layer violations. Consider adding pre-commit hooks to prevent "
                "new violations from being introduced."
            )
        elif current_rate > 0.1:  # >10% is concerning
            urgency = "High"
            action = (
                "Schedule dedicated time each sprint to address layer violations. "
                "Add CI checks to fail on new violations and document the "
                "intended layer architecture."
            )
        else:
            urgency = "Medium"
            action = (
                "The violation rate is still low but trending upward. "
                "Add monitoring to track violations and address them before "
                "they accumulate. Consider adding architecture tests."
            )

        return (
            f"[{urgency} Priority] Architecture integrity is degrading. "
            f"The violation rate has increased consistently across {increasing_count} snapshots. "
            f"{action}"
        )
