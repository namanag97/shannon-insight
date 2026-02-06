"""ChronicProblemFinder — findings persisting across 3+ snapshots.

This is a meta-finder that wraps other findings when they persist too long.
It queries the finding_lifecycle table to identify chronic issues.
"""

import sqlite3
from typing import Optional

from ...persistence.queries import get_chronic_findings
from ..models import Evidence, Finding
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
        db_conn: Optional[sqlite3.Connection] = None,
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
            # Compute enhanced severity
            base_severity = info.severity
            enhanced_severity = min(1.0, base_severity * self.severity_multiplier)

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

            findings.append(
                Finding(
                    finding_type="chronic_problem",
                    severity=enhanced_severity,
                    title=f"Chronic {info.finding_type.replace('_', ' ')}: persisted {info.persistence_count} snapshots",
                    files=[],  # Files are in the wrapped finding
                    evidence=evidence,
                    suggestion=suggestion,
                    confidence=1.0,  # High confidence for persisting issues
                    effort="HIGH",  # Chronic problems are typically harder to fix
                    scope="FILE",  # Inherits scope from wrapped finding
                )
            )

        return findings

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
