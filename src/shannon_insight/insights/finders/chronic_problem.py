"""ChronicProblemFinder — findings persisting across 3+ snapshots.

This is a meta-finder that wraps other findings when they persist too long.
It queries the finding_lifecycle table to identify chronic issues.
"""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from ...persistence.queries import get_chronic_findings
from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store import AnalysisStore


class ChronicProblemFinder:
    """Identifies findings that have persisted across multiple snapshots.

    A chronic problem is any finding that has appeared in 3+ consecutive
    snapshots without being resolved. This suggests the issue is being
    ignored or is particularly difficult to fix.

    Attributes
    ----------
    name : str
        Finder identifier.
    requires : set[str]
        Required store slots (none for this finder).
    min_persistence : int
        Minimum snapshots a finding must persist (default 3).
    severity_multiplier : float
        Multiply base severity by this for chronic findings (default 1.25).
    """

    name = "chronic_problem"
    requires: set[str] = set()  # Doesn't need store data, uses persistence layer

    def __init__(self, min_persistence: int = 3, severity_multiplier: float = 1.25):
        self.min_persistence = min_persistence
        self.severity_multiplier = severity_multiplier

    def find(
        self,
        store: AnalysisStore,
        db_conn: sqlite3.Connection | None = None,
    ) -> list[Finding]:
        """Find chronic problems from persistence data.

        Parameters
        ----------
        store:
            The analysis store (not used, but part of interface).
        db_conn:
            Optional database connection. If not provided, returns empty list.

        Returns
        -------
        list[Finding]
            Chronic problem findings, one per persistent finding.
        """
        if db_conn is None:
            return []

        chronic = get_chronic_findings(db_conn, min_persistence=self.min_persistence)
        if not chronic:
            return []

        findings = []
        for info in chronic:
            # Skip fixtures and test data
            if info.files and any(self._is_fixture(f) for f in info.files):
                continue

            # Skip files with no actual impact (zero connectivity, zero churn)
            # These are stale findings that shouldn't be surfaced
            if not self._has_impact(store, info.files):
                continue

            # Compute severity based on CURRENT signals, not historical
            # Base severity should reflect actual current risk
            current_risk = self._get_current_risk(store, info.files)
            if current_risk < 0.1:
                continue  # File no longer risky, skip

            # Enhance based on persistence (but cap reasonably)
            persistence_boost = min(0.15, info.persistence_count * 0.01)
            enhanced_severity = min(0.85, current_risk + persistence_boost)

            # Files come directly from ChronicFindingInfo (joined from findings table)
            files = info.files

            # Build evidence
            evidence = [
                Evidence(
                    signal="persistence_count",
                    value=float(info.persistence_count),
                    percentile=100.0,  # By definition, these are the most persistent
                    description=f"persisted across {info.persistence_count} snapshots",
                ),
            ]

            # Build suggestion based on original finding type
            suggestion = self._build_suggestion(info.finding_type, info.persistence_count)

            # Build title with files
            file_str = files[0] if files else "unknown"
            title = f"Chronic problem ({info.persistence_count} snapshots): {info.finding_type.replace('_', ' ')} in {file_str}"

            findings.append(
                Finding(
                    finding_type="chronic_problem",
                    severity=enhanced_severity,
                    title=title,
                    files=files,
                    evidence=evidence,
                    suggestion=suggestion,
                    confidence=1.0,  # High confidence for persisting issues
                    effort="HIGH",  # Chronic problems are typically harder to fix
                    scope="FILE",  # Inherits scope from wrapped finding
                )
            )

        return findings

    def _is_fixture(self, path: str) -> bool:
        """Check if path is a test fixture or sample data."""
        path_lower = path.lower()
        exclude_patterns = [
            "tests/fixtures/",
            "test/fixtures/",
            "fixtures/",
            "testdata/",
            "test_data/",
            "__fixtures__/",
            "__mocks__/",
            "samples/",
            "sample_",
            "experiments/",
            "_bootstrap.py",
        ]
        return any(p in path_lower for p in exclude_patterns)

    def _build_suggestion(self, finding_type: str, persistence_count: int) -> str:
        """Build actionable suggestion for chronic problem."""
        base = f"This issue has persisted for {persistence_count} snapshots. Consider: "

        if finding_type in ("high_risk_hub", "god_file"):
            return base + (
                "This is likely a systemic architectural issue. "
                "Schedule dedicated refactoring time or create a tech debt ticket "
                "with a specific deadline. Break the file into smaller pieces incrementally."
            )
        elif finding_type in ("hidden_coupling", "dead_dependency"):
            return base + (
                "Coupling issues that persist often indicate unclear ownership. "
                "Define clear module boundaries and enforce them with linting rules "
                "or import restrictions."
            )
        elif finding_type in ("unstable_file", "bug_attractor"):
            return base + (
                "Files that remain unstable over time may need fundamental redesign. "
                "Consider adding comprehensive tests before refactoring, "
                "or isolate the instability behind a stable interface."
            )
        else:
            return base + (
                "Create a tech debt ticket and prioritize based on the file's "
                "centrality and change frequency. "
                "Consider blocking new features until this is addressed."
            )
