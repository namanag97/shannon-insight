"""HighRiskHubFinder — central + complex + churning files.

Scope: FILE
Severity: 1.0 (highest)
Hotspot: YES (requires change activity)

A high-risk hub is a file with:
- High centrality (pagerank or blast_radius in top 10%)
- AND (high complexity OR high churn)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore

_MIN_FILES = 5


class HighRiskHubFinder:
    """Detects central, complex files that are risky to modify."""

    name = "high_risk_hub"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "BAYESIAN"  # Needs percentiles
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 1.0

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect high-risk hub files.

        Criteria (v2 spec):
        - pctl(pagerank) > 0.90 AND pctl(blast_radius_size) > 0.90
        - AND (pctl(cognitive_load) > 0.90 OR trajectory in {CHURNING, SPIKING})
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        # Need enough files for percentiles to be meaningful
        if len(field.per_file) < _MIN_FILES:
            return []

        # In ABSOLUTE tier, percentiles don't exist
        if field.tier == "ABSOLUTE":
            return []

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            pctl = fs.percentiles

            # Get percentiles (default 0 if not computed)
            pr_pctl = pctl.get("pagerank", 0)
            br_pctl = pctl.get("blast_radius_size", 0)
            cog_pctl = pctl.get("cognitive_load", 0)

            # Need high centrality (pagerank OR blast_radius in top 10%)
            has_high_centrality = pr_pctl >= 0.90 or br_pctl >= 0.90
            if not has_high_centrality:
                continue

            # Need high complexity OR high churn
            has_high_complexity = cog_pctl >= 0.90
            has_high_churn = fs.churn_trajectory in {"CHURNING", "SPIKING"}

            if not (has_high_complexity or has_high_churn):
                continue

            # Build evidence
            evidence_items: list[Evidence] = []
            pcts: list[float] = []

            if pr_pctl >= 0.90:
                pcts.append(pr_pctl)
                evidence_items.append(
                    Evidence(
                        signal="pagerank",
                        value=fs.pagerank,
                        percentile=pr_pctl,
                        description=f"{fs.in_degree} files import this directly",
                    )
                )

            if br_pctl >= 0.90:
                pcts.append(br_pctl)
                evidence_items.append(
                    Evidence(
                        signal="blast_radius_size",
                        value=float(fs.blast_radius_size),
                        percentile=br_pctl,
                        description=(
                            f"a bug here could affect {fs.blast_radius_size} of "
                            f"{len(field.per_file)} files"
                        ),
                    )
                )

            if has_high_complexity:
                pcts.append(cog_pctl)
                evidence_items.append(
                    Evidence(
                        signal="cognitive_load",
                        value=fs.cognitive_load,
                        percentile=cog_pctl,
                        description=f"harder to understand than {cog_pctl * 100:.0f}% of files",
                    )
                )

            if has_high_churn:
                evidence_items.append(
                    Evidence(
                        signal="churn_trajectory",
                        value=0.0,  # enum, use 0
                        percentile=0.0,
                        description=f"trajectory={fs.churn_trajectory}, {fs.total_changes} changes",
                    )
                )

            # Severity scales with average percentile
            avg_pctl = sum(pcts) / len(pcts) if pcts else 0.9
            severity = self.BASE_SEVERITY * max(0.5, avg_pctl)

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"High-risk hub: {path}",
                    files=[path],
                    evidence=evidence_items,
                    suggestion=self._build_suggestion(fs, has_high_complexity, has_high_churn),
                    confidence=0.9,
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)

    def _build_suggestion(self, fs, has_complexity: bool, has_churn: bool) -> str:
        """Build actionable suggestion based on which signals fired."""
        if has_complexity and has_churn:
            return (
                "This file is central, complex, and frequently modified. "
                "Split into smaller modules to reduce coupling and simplify changes."
            )
        elif has_complexity:
            return (
                "This file is central and complex. "
                "Break into smaller pieces to make changes safer and reviews easier."
            )
        else:
            return (
                "This file is central and churning. "
                "Consider stabilizing the interface or extracting frequently-changing parts."
            )
