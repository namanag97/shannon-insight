"""HOLLOW_CODE — files with too many stubs and uneven implementation.

Scope: FILE
Severity: 0.71
Hotspot: NO (structural-only)

A hollow file has stub_ratio > 0.5 (more than half functions are stubs)
and impl_gini > 0.6 (implementation sizes are very uneven).
Common in AI-generated code where boilerplate is filled but logic is missing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class HollowCodeFinder:
    """Detects files with high stub ratio and uneven implementation."""

    name = "hollow_code"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"  # Works in all tiers
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    STUB_THRESHOLD = 0.5
    GINI_THRESHOLD = 0.6
    BASE_SEVERITY = 0.71

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect hollow files with stubs and uneven implementation.

        Returns:
            List of findings sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Need functions to compute stub_ratio and impl_gini
            if fs.function_count == 0:
                continue

            # Check condition: stub_ratio > 0.5 AND impl_gini > 0.6
            if fs.stub_ratio <= self.STUB_THRESHOLD:
                continue
            if fs.impl_gini <= self.GINI_THRESHOLD:
                continue

            # Compute confidence based on how far above thresholds
            confidence = compute_confidence(
                [
                    ("stub_ratio", fs.stub_ratio, self.STUB_THRESHOLD, "high_is_bad"),
                    ("impl_gini", fs.impl_gini, self.GINI_THRESHOLD, "high_is_bad"),
                ]
            )

            # Build evidence
            evidence = [
                Evidence(
                    signal="stub_ratio",
                    value=fs.stub_ratio,
                    percentile=fs.percentiles.get("stub_ratio", 0.0) * 100,
                    description=f"{fs.stub_ratio * 100:.0f}% of functions are stubs",
                ),
                Evidence(
                    signal="impl_gini",
                    value=fs.impl_gini,
                    percentile=fs.percentiles.get("impl_gini", 0.0) * 100,
                    description=f"Gini={fs.impl_gini:.2f} (very uneven implementation)",
                ),
                Evidence(
                    signal="function_count",
                    value=float(fs.function_count),
                    percentile=0.0,
                    description=f"{fs.function_count} functions total",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Hollow code: {path} ({fs.stub_ratio * 100:.0f}% stubs)",
                    files=[path],
                    evidence=evidence,
                    suggestion="Implement the stub functions. Priority: functions called by other files.",
                    confidence=confidence,
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
