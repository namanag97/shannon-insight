"""ZONE_OF_PAIN — concrete, stable modules that are hard to change.

Scope: MODULE
Severity: 0.60
Hotspot: NO (architectural)

The Zone of Pain (Martin metrics) is where:
- Abstractness < 0.3 (concrete, few interfaces)
- Instability < 0.3 (stable, many dependents)

These modules are hard to change because:
1. They're concrete (must modify implementation)
2. They're stable (changes ripple to many dependents)

CRITICAL: instability can be None for isolated modules (Ca=Ce=0).
Always guard with `if ms.instability is not None`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store import AnalysisStore


class ZoneOfPainFinder:
    """Detects modules in the Zone of Pain (low A, low I)."""

    name = "zone_of_pain"
    api_version = "2.0"
    requires = frozenset({"signal_field", "architecture"})
    error_mode = "skip"
    hotspot_filtered = False  # Architectural
    tier_minimum = "BAYESIAN"  # Needs modules
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    ABSTRACTNESS_THRESHOLD = 0.3
    INSTABILITY_THRESHOLD = 0.3
    BASE_SEVERITY = 0.60

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect modules in the Zone of Pain.

        Returns:
            List of findings for Zone of Pain modules.
        """
        if not store.signal_field.available:
            return []
        if not store.architecture.available:
            return []

        field = store.signal_field.value
        findings: list[Finding] = []

        for mod_path, ms in sorted(field.per_module.items()):
            # Skip root directory - not a meaningful module
            if mod_path == "." or mod_path == "":
                continue

            # CRITICAL: Guard against instability=None (isolated modules)
            if ms.instability is None:
                continue  # Isolated module, skip

            # Check Zone of Pain condition:
            # Low abstractness (concrete) AND low instability (stable)
            if ms.abstractness >= self.ABSTRACTNESS_THRESHOLD:
                continue  # Has enough abstraction
            if ms.instability >= self.INSTABILITY_THRESHOLD:
                continue  # Volatile enough to change easily

            # Compute main sequence distance for evidence
            # D = |A + I - 1|, closer to 0 = on main sequence
            main_seq_distance = abs(ms.abstractness + ms.instability - 1)

            # Severity scales with distance from acceptable thresholds
            # Further from thresholds = worse
            severity = self.BASE_SEVERITY + 0.10 * (1 - max(ms.abstractness, ms.instability))

            # Confidence based on how far into the zone
            confidence = compute_confidence(
                [
                    ("abstractness", ms.abstractness, self.ABSTRACTNESS_THRESHOLD, "high_is_good"),
                    ("instability", ms.instability, self.INSTABILITY_THRESHOLD, "high_is_good"),
                ]
            )

            # Build evidence
            evidence = [
                Evidence(
                    signal="abstractness",
                    value=ms.abstractness,
                    percentile=0.0,
                    description=f"A={ms.abstractness:.2f} (< {self.ABSTRACTNESS_THRESHOLD} = concrete)",
                ),
                Evidence(
                    signal="instability",
                    value=ms.instability,
                    percentile=0.0,
                    description=f"I={ms.instability:.2f} (< {self.INSTABILITY_THRESHOLD} = stable)",
                ),
                Evidence(
                    signal="main_seq_distance",
                    value=main_seq_distance,
                    percentile=0.0,
                    description=f"D={main_seq_distance:.2f} (distance from main sequence)",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=min(0.70, severity),  # Cap severity
                    title=f"Zone of Pain: {mod_path}/ (A={ms.abstractness:.2f}, I={ms.instability:.2f})",
                    files=[mod_path],  # Include module path for context
                    evidence=evidence,
                    suggestion=f"Module '{mod_path}' is concrete and stable — hard to change. Extract interfaces or reduce dependents.",
                    confidence=confidence,
                    effort="HIGH",
                    scope="MODULE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
