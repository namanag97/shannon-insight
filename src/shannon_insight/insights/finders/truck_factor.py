"""TRUCK_FACTOR — Critical code owned by single person.

Scope: FILE
Severity: HIGH (0.85)
Hotspot: YES

A truck factor file has:
- bus_factor = 1.0 (single author)
- High centrality (pagerank > p70) OR high blast_radius
- Non-trivial code (lines > 50)

This identifies code where if ONE person leaves, the team is stuck.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class TruckFactorFinder:
    """Detects critical code owned by a single person."""

    name = "truck_factor"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "BAYESIAN"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.85

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect truck factor files.

        Criteria:
        - bus_factor = 1.0 (only one person has touched this file)
        - High importance: pagerank > p70 OR blast_radius_size > 3
        - Non-trivial: lines > 50
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        if field.tier == "ABSOLUTE":
            return []

        # Skip for solo projects - bus_factor=1 is tautological
        if field.global_signals.team_size <= 1:
            return []

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Skip trivial files
            if fs.lines < 50:
                continue

            # Must have single author
            if fs.bus_factor > 1.0:
                continue

            # Must have change history
            if fs.total_changes == 0:
                continue

            pctl = fs.percentiles

            # Must be important (high centrality OR high blast radius)
            pagerank_pctl = pctl.get("pagerank", 0)
            is_central = pagerank_pctl >= 0.70
            has_blast = fs.blast_radius_size >= 3

            if not (is_central or has_blast):
                continue

            # Calculate severity and confidence based on importance
            severity = self.BASE_SEVERITY
            confidence_conditions = []

            if is_central and has_blast:
                severity = min(0.95, severity + 0.10)

            if is_central:
                confidence_conditions.append(("pagerank", pagerank_pctl, 0.70, "high_is_bad"))
            if has_blast:
                confidence_conditions.append(
                    ("blast_radius_size", fs.blast_radius_size / 10.0, 0.3, "high_is_bad")
                )

            confidence = compute_confidence(confidence_conditions) if confidence_conditions else 0.8

            evidence = [
                Evidence(
                    signal="bus_factor",
                    value=fs.bus_factor,
                    percentile=0,
                    description="only 1 person has ever modified this file",
                ),
                Evidence(
                    signal="pagerank",
                    value=fs.pagerank,
                    percentile=pagerank_pctl * 100,
                    description=f"more central than {pagerank_pctl * 100:.0f}% of files",
                ),
            ]

            if has_blast:
                evidence.append(
                    Evidence(
                        signal="blast_radius_size",
                        value=fs.blast_radius_size,
                        percentile=pctl.get("blast_radius_size", 0) * 100,
                        description=f"changes here affect {fs.blast_radius_size} other files",
                    )
                )

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Truck factor risk: {path}",
                    files=[path],
                    evidence=evidence,
                    suggestion="Document this code and have another team member review it. Consider pair programming sessions.",
                    confidence=max(
                        0.7, confidence
                    ),  # Floor at 0.7 since bus_factor=1 is definitive
                    effort="LOW",
                    scope="FILE",
                )
            )

        return findings
