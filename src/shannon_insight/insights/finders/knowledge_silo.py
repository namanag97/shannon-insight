"""KNOWLEDGE_SILO — high-centrality files with single owner.

Scope: FILE
Severity: 0.70
Hotspot: YES (temporal)

A knowledge silo is a file that:
- Has high PageRank (many dependents)
- Has bus_factor <= 1.5 (single owner)

This is a single point of knowledge failure - if the owner leaves,
critical knowledge about this central code is lost.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..helpers import compute_hotspot_median
from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class KnowledgeSiloFinder:
    """Detects high-centrality files owned by a single person."""

    name = "knowledge_silo"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True  # Uses temporal signals
    tier_minimum = "BAYESIAN"  # Needs percentiles
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    BUS_FACTOR_THRESHOLD = 1.5
    PAGERANK_PCTL_THRESHOLD = 0.75
    PAGERANK_ABSOLUTE_THRESHOLD = 0.005  # For ABSOLUTE tier
    BASE_SEVERITY = 0.70

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect knowledge silos.

        Returns:
            List of findings sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        tier = field.tier

        # Skip in ABSOLUTE tier (needs percentiles)
        if tier == "ABSOLUTE":
            return []

        # Skip for solo projects — bus_factor=1 is tautological
        if field.global_signals.team_size <= 1:
            return []

        # Compute hotspot filter median
        median_changes = compute_hotspot_median(field)

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Apply hotspot filter (temporal-aware finder)
            if fs.total_changes <= median_changes:
                continue

            # Check bus factor condition
            if fs.bus_factor > self.BUS_FACTOR_THRESHOLD:
                continue  # Has multiple owners

            # Check pagerank percentile
            pctl_pr = fs.percentiles.get("pagerank", 0.0)
            if pctl_pr <= self.PAGERANK_PCTL_THRESHOLD:
                continue  # Not central enough

            # Compute confidence
            confidence = compute_confidence(
                [
                    ("pagerank", pctl_pr, self.PAGERANK_PCTL_THRESHOLD, "high_is_bad"),
                    ("bus_factor", fs.bus_factor, self.BUS_FACTOR_THRESHOLD, "high_is_good"),
                ]
            )

            # Build evidence
            evidence = [
                Evidence(
                    signal="bus_factor",
                    value=fs.bus_factor,
                    percentile=fs.percentiles.get("bus_factor", 0.0) * 100,
                    description=f"Bus factor = {fs.bus_factor:.1f} (single point of failure)",
                ),
                Evidence(
                    signal="pagerank",
                    value=fs.pagerank,
                    percentile=pctl_pr * 100,
                    description=f"Top {(1 - pctl_pr) * 100:.0f}% by centrality",
                ),
                Evidence(
                    signal="author_entropy",
                    value=fs.author_entropy,
                    percentile=0.0,
                    description=f"Author entropy = {fs.author_entropy:.2f}",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Knowledge silo: {path} (bus factor = {fs.bus_factor:.1f})",
                    files=[path],
                    evidence=evidence,
                    suggestion="Pair-program or rotate ownership. Single point of knowledge failure.",
                    confidence=confidence,
                    effort="LOW",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
