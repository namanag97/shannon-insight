"""FLAT_ARCHITECTURE — codebase with no layering.

Scope: CODEBASE
Severity: 0.60
Hotspot: NO (structural-only)

A flat architecture has max_depth <= 1 (all files at entry level)
and glue_deficit > 0.5 (not enough coordination/orchestration code).
Indicates many independent modules but nothing to compose them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class FlatArchitectureFinder:
    """Detects flat architecture with no layering."""

    name = "flat_architecture"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"  # Works in all tiers
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    DEPTH_THRESHOLD = 1
    GLUE_DEFICIT_THRESHOLD = 0.5
    BASE_SEVERITY = 0.60

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect flat architecture at codebase level.

        Returns:
            At most one finding (CODEBASE scope).
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        global_signals = field.global_signals

        # Compute max depth from per-file signals
        depths = [fs.depth for fs in field.per_file.values() if fs.depth >= 0]
        if not depths:
            return []  # No reachable files

        max_depth = max(depths)

        # Check condition: max_depth <= 1 AND glue_deficit > 0.5
        if max_depth > self.DEPTH_THRESHOLD:
            return []  # Has layering
        if global_signals.glue_deficit <= self.GLUE_DEFICIT_THRESHOLD:
            return []  # Has enough glue code

        # Confidence based on how extreme the values are
        confidence = compute_confidence(
            [
                (
                    "glue_deficit",
                    global_signals.glue_deficit,
                    self.GLUE_DEFICIT_THRESHOLD,
                    "high_is_bad",
                ),
            ]
        )

        # Build evidence
        evidence = [
            Evidence(
                signal="max_depth",
                value=float(max_depth),
                percentile=0.0,
                description=f"Max import depth = {max_depth} (flat)",
            ),
            Evidence(
                signal="glue_deficit",
                value=global_signals.glue_deficit,
                percentile=0.0,
                description=f"Glue deficit = {global_signals.glue_deficit:.2f} (missing orchestration)",
            ),
            Evidence(
                signal="orphan_ratio",
                value=global_signals.orphan_ratio,
                percentile=0.0,
                description=f"Orphan ratio = {global_signals.orphan_ratio:.2f}",
            ),
        ]

        return [
            Finding(
                finding_type=self.name,
                severity=self.BASE_SEVERITY,
                title="Flat architecture: no layering or orchestration",
                files=[],  # CODEBASE scope
                evidence=evidence,
                suggestion="Add composition layer. Many leaf modules exist but nothing orchestrates them.",
                confidence=confidence,
                effort="HIGH",
                scope="CODEBASE",
            )
        ]
