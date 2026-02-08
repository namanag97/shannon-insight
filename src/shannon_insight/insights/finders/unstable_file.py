"""UnstableFileFinder — never-stabilizing churn.

Scope: FILE
Severity: 0.7
Hotspot: YES (requires temporal data)

Files with trajectory CHURNING or SPIKING that have
above-median change counts are unstable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore

_MIN_FILES = 5


class UnstableFileFinder:
    """Detects files with never-stabilizing churn patterns."""

    name = "unstable_file"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "ABSOLUTE"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.7

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect unstable files based on churn trajectory."""
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        if len(field.per_file) < _MIN_FILES:
            return []

        # Find median total_changes
        all_changes = sorted(fs.total_changes for fs in field.per_file.values())
        n = len(all_changes)
        median_changes = all_changes[n // 2] if n > 0 else 0

        # Get span for context
        span_weeks = 0
        if store.git_history.available:
            span_weeks = max(1, store.git_history.value.span_days // 7)

        findings = []
        for path, fs in sorted(field.per_file.items()):
            if fs.churn_trajectory not in ("CHURNING", "SPIKING"):
                continue
            if fs.total_changes <= median_changes:
                continue

            # Get percentile if available
            pctl = fs.percentiles.get("total_changes", 0.5)
            strength = max(0.3, pctl)
            severity = self.BASE_SEVERITY * strength

            # Build time-aware description
            if span_weeks > 0:
                rate_desc = f"changed {fs.total_changes} times over {span_weeks} weeks"
            else:
                rate_desc = f"changed {fs.total_changes} times"

            if fs.churn_trajectory == "SPIKING":
                trend_desc = "change rate is increasing — more edits recently"
                suggestion = (
                    "This file is being edited more frequently. "
                    "Investigate unclear requirements or missing test coverage."
                )
            else:
                trend_desc = "change rate is volatile — no sign of settling down"
                suggestion = (
                    "This file has been modified repeatedly without stabilizing. "
                    "Consider splitting it or adding tests to reduce churn."
                )

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Unstable file: {path}",
                    files=[path],
                    evidence=[
                        Evidence(
                            signal="total_changes",
                            value=float(fs.total_changes),
                            percentile=pctl,
                            description=rate_desc,
                        ),
                        Evidence(
                            signal="churn_trajectory",
                            value=fs.churn_slope,
                            percentile=0,
                            description=trend_desc,
                        ),
                    ],
                    suggestion=suggestion,
                    confidence=0.75,
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
