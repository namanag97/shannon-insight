"""HiddenCouplingFinder — co-change without structural dependency.

Scope: FILE_PAIR
Severity: 0.9
Hotspot: YES (requires temporal data)

Files that always change together but have no import relationship.
This suggests an implicit contract that should be made explicit.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from ...math.statistics import Statistics
from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store import AnalysisStore

_MIN_LIFT = 2.0
_MIN_CONFIDENCE = 0.5
_MIN_MI = 0.05  # Minimum mutual information in bits
_MIN_COCHANGE = 3  # Minimum co-occurrences
_MAX_FINDINGS = 20  # Finder-level cap


class HiddenCouplingFinder:
    """Detects file pairs that co-change without structural dependency."""

    name = "hidden_coupling"
    api_version = "2.0"
    requires = frozenset({"structural", "cochange"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "ABSOLUTE"  # Works with any tier
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.9

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect hidden coupling between files."""
        if not store.structural.available or not store.cochange.available:
            return []

        structural = store.structural.value
        cochange = store.cochange.value
        graph = structural.graph
        findings = []

        total_commits = cochange.total_commits

        for (file_a, file_b), pair in cochange.pairs.items():
            # Skip __init__.py pairs (noise)
            if file_a.endswith("__init__.py") or file_b.endswith("__init__.py"):
                continue

            # Minimum co-occurrences to avoid noise from small history
            if pair.cochange_count < _MIN_COCHANGE:
                continue

            # Check lift and confidence thresholds
            if pair.lift < _MIN_LIFT:
                continue
            max_conf = max(pair.confidence_a_b, pair.confidence_b_a)
            if max_conf < _MIN_CONFIDENCE:
                continue

            # Mutual Information filter — captures full joint distribution
            # If both files change in every commit (bulk refactor), MI ≈ 0
            total_a = cochange.file_change_counts.get(file_a, 0)
            total_b = cochange.file_change_counts.get(file_b, 0)
            joint = pair.cochange_count
            only_a = total_a - joint
            only_b = total_b - joint
            neither = max(0, total_commits - total_a - total_b + joint)

            mi = Statistics.mutual_information(joint, only_a, only_b, neither)
            if mi < _MIN_MI:
                continue

            # Check there is NO structural dependency between the pair
            a_deps = set(graph.adjacency.get(file_a, []))
            b_deps = set(graph.adjacency.get(file_b, []))
            if file_b in a_deps or file_a in b_deps:
                continue  # structural dep exists — not hidden

            # Severity based on lift, confidence, and MI
            strength = min(1.0, max(0.1, (pair.lift / 10.0 + max_conf + mi) / 3))
            severity = self.BASE_SEVERITY * strength

            # Determine if they share a parent directory
            same_package = str(PurePosixPath(file_a).parent) == str(PurePosixPath(file_b).parent)

            # Build human-readable descriptions
            conf_desc = self._describe_confidence(pair, file_a, file_b)

            suggestion = self._build_suggestion(
                file_a,
                file_b,
                pair,
                same_package,
            )

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"{file_a} and {file_b} always change together",
                    files=[file_a, file_b],
                    evidence=[
                        Evidence(
                            signal="cochange_count",
                            value=float(pair.cochange_count),
                            percentile=0,
                            description=conf_desc,
                        ),
                        Evidence(
                            signal="cochange_lift",
                            value=pair.lift,
                            percentile=0,
                            description=f"{pair.lift:.1f}x more often than expected by chance",
                        ),
                        Evidence(
                            signal="mutual_information",
                            value=mi,
                            percentile=0,
                            description=f"MI = {mi:.3f} bits (genuine coupling signal)",
                        ),
                        Evidence(
                            signal="no_import",
                            value=0.0,
                            percentile=0,
                            description="neither file imports the other",
                        ),
                    ],
                    suggestion=suggestion,
                    confidence=0.8,
                    effort="LOW",
                    scope="FILE_PAIR",
                )
            )

        # Sort by MI × severity descending, cap at _MAX_FINDINGS
        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings[:_MAX_FINDINGS]

    def _describe_confidence(self, pair, file_a, file_b) -> str:
        """Describe co-change in plain terms."""
        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name
        if pair.confidence_a_b >= pair.confidence_b_a:
            return (
                f"when {a_name} changed, {b_name} also changed "
                f"{pair.cochange_count} of {pair.total_a} times "
                f"({pair.confidence_a_b * 100:.0f}%)"
            )
        return (
            f"when {b_name} changed, {a_name} also changed "
            f"{pair.cochange_count} of {pair.total_b} times "
            f"({pair.confidence_b_a * 100:.0f}%)"
        )

    def _build_suggestion(self, file_a, file_b, pair, same_package) -> str:
        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name

        if same_package:
            return (
                f"{a_name} and {b_name} are in the same package and "
                f"always change together, but neither imports the other. "
                f"Make this explicit: add an import or extract shared logic."
            )
        return (
            "These files live in different packages but always change together. "
            "Find what ties them and make it explicit via import or shared module."
        )
