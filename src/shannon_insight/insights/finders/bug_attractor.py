"""BUG_ATTRACTOR — central files with high fix ratio.

Scope: FILE
Severity: 0.70
Hotspot: YES (temporal)

A bug attractor is a file where:
- fix_ratio > 0.4 (40%+ of changes are bug fixes)
- pctl(pagerank) > 0.75 (high centrality)

These files attract bugs and, due to their centrality,
propagate issues across the codebase.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..helpers import compute_hotspot_median
from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store import AnalysisStore


class BugAttractorFinder:
    """Detects central files with high bug fix ratio."""

    name = "bug_attractor"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True  # Uses temporal signals
    tier_minimum = "BAYESIAN"  # Needs percentiles
    deprecated = False
    deprecation_note = None

    # Thresholds (tightened)
    FIX_RATIO_THRESHOLD = 0.4
    PAGERANK_PCTL_THRESHOLD = 0.80  # Was 0.75 — tighter to reduce noise
    PAGERANK_ABSOLUTE_THRESHOLD = 0.005  # For ABSOLUTE tier
    BASE_SEVERITY = 0.70

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect bug attractor files.

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

        # Compute hotspot filter median
        median_changes = compute_hotspot_median(field)

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Apply hotspot filter
            if fs.total_changes <= median_changes:
                continue

            # Check fix ratio (absolute threshold)
            if fs.fix_ratio <= self.FIX_RATIO_THRESHOLD:
                continue

            # Check pagerank percentile
            pctl_pr = fs.percentiles.get("pagerank", 0.0)
            if pctl_pr <= self.PAGERANK_PCTL_THRESHOLD:
                continue

            # Compute confidence
            confidence = compute_confidence(
                [
                    ("fix_ratio", fs.fix_ratio, self.FIX_RATIO_THRESHOLD, "high_is_bad"),
                    ("pagerank", pctl_pr, self.PAGERANK_PCTL_THRESHOLD, "high_is_bad"),
                ]
            )

            # Build evidence
            evidence = [
                Evidence(
                    signal="fix_ratio",
                    value=fs.fix_ratio,
                    percentile=fs.percentiles.get("fix_ratio", 0.0) * 100,
                    description=f"{fs.fix_ratio * 100:.0f}% of changes are bug fixes",
                ),
                Evidence(
                    signal="pagerank",
                    value=fs.pagerank,
                    percentile=pctl_pr * 100,
                    description=f"Top {(1 - pctl_pr) * 100:.0f}% by centrality",
                ),
                Evidence(
                    signal="total_changes",
                    value=float(fs.total_changes),
                    percentile=0.0,
                    description=f"{fs.total_changes} total changes",
                ),
                Evidence(
                    signal="blast_radius_size",
                    value=float(fs.blast_radius_size),
                    percentile=0.0,
                    description=f"Blast radius: {fs.blast_radius_size} files",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Bug attractor: {path} ({fs.fix_ratio * 100:.0f}% fixes)",
                    files=[path],
                    evidence=evidence,
                    suggestion="40%+ of changes are bug fixes in a central file. Root-cause analysis needed.",
                    confidence=confidence,
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
