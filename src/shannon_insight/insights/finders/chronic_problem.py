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
        current_findings: list | None = None,
    ) -> list[Finding]:
        """Find chronic problems from persistence data.

        Parameters
        ----------
        store:
            The analysis store for validating against current signals.
        db_conn:
            Optional database connection. If not provided, returns empty list.
        current_findings:
            Findings from the current analysis run. Used to add +1 to
            persistence_count for findings that are still detected.

        Returns
        -------
        list[Finding]
            Chronic problem findings, one per persistent finding.
        """
        if db_conn is None:
            return []

        # Build set of identity keys from current findings for O(1) lookup
        current_keys = self._build_current_keys(current_findings or [])

        chronic = get_chronic_findings(db_conn, min_persistence=max(1, self.min_persistence - 1))
        if not chronic:
            return []

        findings = []
        for info in chronic:
            # Skip fixtures and test data
            if info.files and any(self._is_fixture(f) for f in info.files):
                continue

            # Calculate effective persistence count:
            # If finding is also in current findings, add 1 (current run counts)
            effective_count = info.persistence_count
            if info.identity_key in current_keys:
                effective_count += 1

            # Only flag if effective count meets threshold
            if effective_count < self.min_persistence:
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
            persistence_boost = min(0.15, effective_count * 0.01)
            enhanced_severity = min(0.85, current_risk + persistence_boost)

            # Files come directly from ChronicFindingInfo (joined from findings table)
            files = info.files

            # Build evidence
            evidence = [
                Evidence(
                    signal="persistence_count",
                    value=float(effective_count),
                    percentile=100.0,  # By definition, these are the most persistent
                    description=f"persisted across {effective_count} snapshots",
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
        from shannon_insight.file_ops import is_fixture_or_test_data

        return is_fixture_or_test_data(path)

    def _has_impact(self, store, files: list[str]) -> bool:
        """Check if any file has actual impact (connectivity, churn, blast radius).

        Files with zero impact should not be surfaced as chronic problems,
        even if findings persist.
        """
        if not store or not files:
            return False

        # Check if we have the fact_store (v2 infrastructure)
        fact_store = getattr(store, "fact_store", None)
        if not fact_store:
            return True  # Can't verify, assume has impact

        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.signals import Signal

        for path in files:
            entity_id = EntityId(EntityType.FILE, path)

            # Check for any meaningful signal
            pagerank = fact_store.get_signal(entity_id, Signal.PAGERANK, 0)
            blast_radius = fact_store.get_signal(entity_id, Signal.BLAST_RADIUS_SIZE, 0)
            total_changes = fact_store.get_signal(entity_id, Signal.TOTAL_CHANGES, 0)
            in_degree = fact_store.get_signal(entity_id, Signal.IN_DEGREE, 0)

            # Has impact if any signal is meaningful
            if pagerank > 0.01 or blast_radius > 1 or total_changes > 5 or in_degree > 0:
                return True

        return False

    def _get_current_risk(self, store, files: list[str]) -> float:
        """Get current risk score for files based on CURRENT signals.

        Returns the max risk_score across files, or 0 if can't determine.
        """
        if not store or not files:
            return 0.0

        # Check for signal_field slot
        if hasattr(store, "signal_field") and store.signal_field.available:
            signal_field = store.signal_field.value
            max_risk = 0.0
            for path in files:
                if path in signal_field.per_file:
                    fs = signal_field.per_file[path]
                    max_risk = max(max_risk, getattr(fs, "risk_score", 0.0))
            return max_risk

        # Fallback: check fact_store
        fact_store = getattr(store, "fact_store", None)
        if not fact_store:
            return 0.3  # Default moderate risk if can't determine

        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.signals import Signal

        max_risk = 0.0
        for path in files:
            entity_id = EntityId(EntityType.FILE, path)
            risk = fact_store.get_signal(entity_id, Signal.RISK_SCORE, 0.0)
            max_risk = max(max_risk, risk)

        return max_risk

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
