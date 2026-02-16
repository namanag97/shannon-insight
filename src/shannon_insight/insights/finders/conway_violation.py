"""CONWAY_VIOLATION — coupled modules maintained by different teams.

Scope: MODULE_PAIR
Severity: 0.55
Hotspot: NO (social/structural)

Conway's Law says system structure mirrors org structure.
A violation occurs when:
- Two modules have high structural coupling (depend on each other)
- But the author teams are different (high author distance)

This creates coordination cost and knowledge gaps.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store import AnalysisStore


class ConwayViolationFinder:
    """Detects coupled modules with different author teams."""

    name = "conway_violation"
    api_version = "2.0"
    requires = frozenset({"author_distances", "architecture"})
    error_mode = "skip"
    hotspot_filtered = False  # Social/structural
    tier_minimum = "BAYESIAN"  # Needs modules + 3+ authors
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    AUTHOR_DISTANCE_THRESHOLD = 0.8
    COUPLING_THRESHOLD = 0.3
    BASE_SEVERITY = 0.55

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect Conway violations between module pairs.

        Returns:
            List of findings for Conway violations.
        """
        if not store.author_distances.available:
            return []
        if not store.architecture.available:
            return []

        author_distances = store.author_distances.value
        architecture = store.architecture.value

        # Build module coupling map from architecture
        # module_graph is dict[source_module][target_module] = edge_count
        module_coupling: dict[tuple[str, str], float] = {}
        if hasattr(architecture, "module_graph") and architecture.module_graph:
            for src, targets in architecture.module_graph.items():
                for tgt, weight in targets.items():
                    key = tuple(sorted([src, tgt]))
                    module_coupling[key] = max(module_coupling.get(key, 0), float(weight))

        findings: list[Finding] = []

        for dist_entry in author_distances:
            # Access attributes (adapt to actual model)
            mod_a = getattr(
                dist_entry, "module_a", dist_entry[0] if isinstance(dist_entry, tuple) else None
            )
            mod_b = getattr(
                dist_entry, "module_b", dist_entry[1] if isinstance(dist_entry, tuple) else None
            )
            author_dist = getattr(
                dist_entry, "distance", dist_entry[2] if isinstance(dist_entry, tuple) else 0.0
            )

            if mod_a is None or mod_b is None:
                continue

            # Check author distance threshold
            if author_dist <= self.AUTHOR_DISTANCE_THRESHOLD:
                continue  # Same team

            # Check structural coupling
            key = tuple(sorted([mod_a, mod_b]))
            coupling = module_coupling.get(key, 0.0)
            if coupling <= self.COUPLING_THRESHOLD:
                continue  # Not coupled enough

            # Compute confidence
            confidence = compute_confidence(
                [
                    ("author_distance", author_dist, self.AUTHOR_DISTANCE_THRESHOLD, "high_is_bad"),
                    ("coupling", coupling, self.COUPLING_THRESHOLD, "high_is_bad"),
                ]
            )

            # Build evidence
            evidence = [
                Evidence(
                    signal="author_distance",
                    value=author_dist,
                    percentile=0.0,
                    description=f"Author distance = {author_dist:.2f} (different teams)",
                ),
                Evidence(
                    signal="structural_coupling",
                    value=coupling,
                    percentile=0.0,
                    description=f"Structural coupling = {coupling:.2f}",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Conway violation: {mod_a} <-> {mod_b}",
                    files=[],  # MODULE_PAIR scope
                    evidence=evidence,
                    suggestion="Coupled modules maintained by different teams. Align team boundaries.",
                    confidence=confidence,
                    effort="HIGH",
                    scope="MODULE_PAIR",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
