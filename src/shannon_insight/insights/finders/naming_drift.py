"""NAMING_DRIFT — files whose name doesn't match their content.

Scope: FILE
Severity: 0.45
Hotspot: NO (structural-only)

A file has naming drift when its filename tokens don't match the
concepts extracted from its content. E.g., "utils.py" containing
only authentication logic, or "auth.py" containing mostly logging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class NamingDriftFinder:
    """Detects files whose name doesn't match their content concepts."""

    name = "naming_drift"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"  # Works in all tiers
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    DRIFT_THRESHOLD = 0.7
    BASE_SEVERITY = 0.45

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect files with naming drift.

        Returns:
            List of findings sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Check condition: naming_drift > 0.7
            if fs.naming_drift <= self.DRIFT_THRESHOLD:
                continue

            # Confidence based on how far above threshold
            confidence = compute_confidence(
                [
                    ("naming_drift", fs.naming_drift, self.DRIFT_THRESHOLD, "high_is_bad"),
                ]
            )

            # Build evidence
            evidence = [
                Evidence(
                    signal="naming_drift",
                    value=fs.naming_drift,
                    percentile=fs.percentiles.get("naming_drift", 0.0) * 100,
                    description=f"Drift score = {fs.naming_drift:.2f} (filename vs content mismatch)",
                ),
                Evidence(
                    signal="concept_count",
                    value=float(fs.concept_count),
                    percentile=0.0,
                    description=f"{fs.concept_count} concepts in content",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Naming drift: {path} (content doesn't match name)",
                    files=[path],
                    evidence=evidence,
                    suggestion="Rename file to match its actual content, or extract mismatched logic.",
                    confidence=confidence,
                    effort="LOW",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
