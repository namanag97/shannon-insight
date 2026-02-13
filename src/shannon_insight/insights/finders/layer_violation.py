"""LAYER_VIOLATION — backward or skip dependencies in layer ordering.

Scope: MODULE_PAIR
Severity: 0.52
Hotspot: NO (architectural)

Detected when a higher-layer module imports from a lower layer,
or when modules skip layers (e.g., presentation importing data layer).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class LayerViolationFinder:
    """Detects layer violations from architecture analysis."""

    name = "layer_violation"
    api_version = "2.0"
    requires = frozenset({"signal_field", "architecture"})
    error_mode = "skip"
    hotspot_filtered = False  # Architectural
    tier_minimum = "BAYESIAN"  # Needs modules
    deprecated = False
    deprecation_note = None

    # Constants
    BASE_SEVERITY = 0.52

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect layer violations from architecture analysis.

        Returns:
            List of findings for each violation, sorted by severity desc.
        """
        if not store.architecture.available:
            return []

        architecture = store.architecture.value
        if not hasattr(architecture, "violations") or not architecture.violations:
            return []

        findings: list[Finding] = []

        for violation in architecture.violations:
            # Access violation attributes (adapt to actual model)
            source_module = violation.source_module
            target_module = violation.target_module

            # Skip violations involving root module
            if source_module in (".", "") or target_module in (".", ""):
                continue

            source_layer = getattr(violation, "source_layer", 0)
            target_layer = getattr(violation, "target_layer", 0)
            violation_type = getattr(violation, "violation_type", "backward")

            # Build evidence
            evidence = [
                Evidence(
                    signal="source_layer",
                    value=float(source_layer),
                    percentile=0.0,
                    description=f"{source_module} at layer {source_layer}",
                ),
                Evidence(
                    signal="target_layer",
                    value=float(target_layer),
                    percentile=0.0,
                    description=f"{target_module} at layer {target_layer}",
                ),
                Evidence(
                    signal="violation_type",
                    value=0.0,
                    percentile=0.0,
                    description=f"Violation: {violation_type}",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Layer violation: {source_module}/ imports {target_module}/ (L{source_layer}→L{target_layer})",
                    files=[source_module, target_module],  # Include modules for context
                    evidence=evidence,
                    suggestion=f"'{source_module}' at layer {source_layer} imports '{target_module}' at layer {target_layer}. Inject dependency or restructure.",
                    confidence=1.0,  # Violation detected = certain
                    effort="MEDIUM",
                    scope="MODULE_PAIR",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
