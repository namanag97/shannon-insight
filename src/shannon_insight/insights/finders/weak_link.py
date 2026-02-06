"""WEAK_LINK — files much worse than their neighbors.

Scope: FILE
Severity: 0.75
Hotspot: YES (cross-dimensional)

Uses the health Laplacian (Phase 5) to detect files that are significantly
worse than their neighbors in the dependency graph.

Δh(f) = risk(f) - mean(risk(neighbors))

If Δh > 0.4, the file is a "weak link" dragging down its healthy neighborhood.

IMPORTANT: Uses raw_risk (pre-percentile), NOT percentiles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..helpers import compute_hotspot_median
from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class WeakLinkFinder:
    """Detects files much worse than their neighbors."""

    name = "weak_link"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True  # Cross-dimensional
    tier_minimum = "BAYESIAN"  # Needs raw_risk computation
    deprecated = False
    deprecation_note = None

    # Thresholds from registry - ABSOLUTE threshold (not percentile)
    DELTA_H_THRESHOLD = 0.4
    BASE_SEVERITY = 0.75

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect weak link files using health Laplacian.

        Returns:
            List of findings sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        tier = field.tier

        # Skip in ABSOLUTE tier (needs raw_risk)
        if tier == "ABSOLUTE":
            return []

        # Compute hotspot filter median
        median_changes = compute_hotspot_median(field)

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Apply hotspot filter
            if fs.total_changes <= median_changes:
                continue

            # Get delta_h from SignalField
            delta_h = field.delta_h.get(path, 0.0)

            # Check ABSOLUTE threshold (not percentile!)
            if delta_h <= self.DELTA_H_THRESHOLD:
                continue

            # Orphan files have delta_h = 0.0 by design
            if fs.is_orphan:
                continue

            # Compute confidence based on margin above threshold
            confidence = compute_confidence(
                [
                    ("delta_h", delta_h, self.DELTA_H_THRESHOLD, "high_is_bad"),
                ]
            )

            # Severity scales with delta_h
            # delta_h 0.4 → 0.75, delta_h 0.8 → 0.85
            severity = min(0.85, self.BASE_SEVERITY + (delta_h - self.DELTA_H_THRESHOLD) * 0.25)

            # Build evidence
            evidence = [
                Evidence(
                    signal="delta_h",
                    value=delta_h,
                    percentile=0.0,  # Not a percentile
                    description=f"Δh = {delta_h:.2f} (much worse than neighbors)",
                ),
                Evidence(
                    signal="raw_risk",
                    value=fs.raw_risk,
                    percentile=0.0,
                    description=f"Raw risk = {fs.raw_risk:.2f}",
                ),
                Evidence(
                    signal="risk_score",
                    value=fs.risk_score,
                    percentile=fs.percentiles.get("risk_score", 0.0) * 100,
                    description=f"Risk score = {fs.risk_score:.2f}",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Weak link: {path} (Δh = {delta_h:.2f})",
                    files=[path],
                    evidence=evidence,
                    suggestion="This file drags down its healthy neighborhood. Prioritize improvement.",
                    confidence=confidence,
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
