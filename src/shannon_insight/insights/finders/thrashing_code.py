"""THRASHING_CODE — Files with erratic, unstable change patterns.

Scope: FILE
Severity: HIGH (0.75)
Hotspot: YES

A thrashing file has:
- churn_trajectory = "SPIKING" OR churn_cv > 1.5
- Recent activity (not dormant)
- Non-trivial code

This identifies code that can't seem to stabilize - constant rework.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..helpers import compute_hotspot_median
from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store import AnalysisStore


class ThrashingCodeFinder:
    """Detects files with erratic change patterns."""

    name = "thrashing_code"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "BAYESIAN"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.75
    CV_THRESHOLD = 1.5  # Coefficient of variation threshold

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect thrashing files.

        Criteria:
        - churn_trajectory = "SPIKING" OR churn_cv > 1.5
        - total_changes >= 3 (need enough data)
        - lines > 30 (non-trivial)
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

            # Need enough history and size
            if fs.total_changes < 3 or fs.lines < 30:
                continue

            is_spiking = fs.churn_trajectory == "SPIKING"
            is_erratic = fs.churn_cv > self.CV_THRESHOLD

            if not (is_spiking or is_erratic):
                continue

            # Calculate severity and confidence
            severity = self.BASE_SEVERITY
            confidence_conditions = []

            if is_spiking and is_erratic:
                severity = 0.90  # Both signals = very bad
            elif is_spiking:
                severity = 0.80
            elif fs.churn_cv > 2.0:
                severity = 0.85

            if is_erratic:
                confidence_conditions.append(
                    ("churn_cv", fs.churn_cv, self.CV_THRESHOLD, "high_is_bad")
                )

            confidence = (
                compute_confidence(confidence_conditions) if confidence_conditions else 0.75
            )

            evidence = [
                Evidence(
                    signal="churn_trajectory",
                    value=0,  # Categorical
                    percentile=0,
                    description=f"change pattern: {fs.churn_trajectory}",
                ),
                Evidence(
                    signal="churn_cv",
                    value=fs.churn_cv,
                    percentile=fs.percentiles.get("churn_cv", 0) * 100,
                    description=f"change variability {fs.churn_cv:.2f} (>{self.CV_THRESHOLD} is erratic)",
                ),
                Evidence(
                    signal="total_changes",
                    value=fs.total_changes,
                    percentile=fs.percentiles.get("total_changes", 0) * 100,
                    description=f"changed {fs.total_changes} times with no stable pattern",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Thrashing code: {path}",
                    files=[path],
                    evidence=evidence,
                    suggestion="This code can't stabilize. Review recent changes for conflicting requirements or unclear specs. Consider a design review.",
                    confidence=max(0.70, confidence),
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        return findings
