"""BUG_MAGNET — Files where most changes are bug fixes.

Scope: FILE
Severity: HIGH (0.80)
Hotspot: YES

A bug magnet file has:
- fix_ratio > 0.4 (40%+ of changes are bug fixes)
- Enough history (total_changes >= 5)
- Currently active (not dormant)

This identifies code that keeps breaking - a sign of fundamental design issues.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..helpers import compute_hotspot_median
from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store import AnalysisStore


class BugMagnetFinder:
    """Detects files that attract bugs."""

    name = "bug_magnet"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "BAYESIAN"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.80
    FIX_RATIO_THRESHOLD = 0.4
    MIN_CHANGES = 5

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect bug magnet files.

        Criteria:
        - fix_ratio > 0.4 (40%+ commits mention 'fix')
        - total_changes >= 5 (enough history to judge)
        - Not dormant (has recent activity)
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        if field.tier == "ABSOLUTE":
            return []

        # Compute hotspot median for filtering
        median_changes = compute_hotspot_median(field)

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Hotspot gate: skip dormant files
            if fs.total_changes <= median_changes:
                continue

            # Need enough history
            if fs.total_changes < self.MIN_CHANGES:
                continue

            # High fix ratio
            if fs.fix_ratio < self.FIX_RATIO_THRESHOLD:
                continue

            # Calculate severity and confidence - higher fix ratio = worse
            severity = self.BASE_SEVERITY + (fs.fix_ratio - 0.4) * 0.3
            severity = min(0.95, severity)

            confidence = compute_confidence(
                [
                    ("fix_ratio", fs.fix_ratio, self.FIX_RATIO_THRESHOLD, "high_is_bad"),
                ]
            )

            fix_count = int(fs.total_changes * fs.fix_ratio)

            evidence = [
                Evidence(
                    signal="fix_ratio",
                    value=fs.fix_ratio,
                    percentile=fs.percentiles.get("fix_ratio", 0) * 100,
                    description=f"{fs.fix_ratio * 100:.0f}% of changes ({fix_count}/{fs.total_changes}) are bug fixes",
                ),
                Evidence(
                    signal="total_changes",
                    value=fs.total_changes,
                    percentile=fs.percentiles.get("total_changes", 0) * 100,
                    description=f"changed {fs.total_changes} times",
                ),
            ]

            # Add cognitive load if high (complex + buggy = bad)
            if fs.cognitive_load > 30:
                evidence.append(
                    Evidence(
                        signal="cognitive_load",
                        value=fs.cognitive_load,
                        percentile=fs.percentiles.get("cognitive_load", 0) * 100,
                        description=f"cognitive load {fs.cognitive_load:.1f} (complex code)",
                    )
                )
                severity = min(0.95, severity + 0.05)

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Bug magnet: {path}",
                    files=[path],
                    evidence=evidence,
                    suggestion="This file keeps breaking. Consider refactoring or adding more tests. Look for root cause patterns in git history.",
                    confidence=max(0.75, confidence),
                    effort="HIGH",
                    scope="FILE",
                )
            )

        return findings
