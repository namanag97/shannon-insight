"""GOD_FILE — high cognitive load + low coherence.

Scope: FILE
Severity: 0.8
Hotspot: YES (requires meaningful code)

A god file has:
- High cognitive load (top 10%)
- Low semantic coherence (bottom 20%)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store import AnalysisStore

_MIN_FILES = 5


class GodFileFinder:
    """Detects files that do too many unrelated things."""

    name = "god_file"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "BAYESIAN"  # Needs percentiles
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.8

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect god files.

        A god file has high complexity AND low coherence - it does too much.

        Criteria:
        - High cognitive load (top 20%) OR many functions (>10)
        - AND low semantic coherence (bottom 30%)
        - AND has enough content (function_count >= 3)
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        if len(field.per_file) < _MIN_FILES:
            return []

        # In ABSOLUTE tier, percentiles don't exist
        if field.tier == "ABSOLUTE":
            return []

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Hotspot gate: must have change activity
            if fs.total_changes == 0:
                continue

            # Minimum function count to avoid flagging trivial files
            if fs.function_count < 3:
                continue

            pctl = fs.percentiles

            cog_pctl = pctl.get("cognitive_load", 0)
            coh_pctl = pctl.get("semantic_coherence", 1.0)

            # High complexity: top 20% cognitive load OR many functions
            has_high_complexity = cog_pctl >= 0.80 or fs.function_count > 10

            # Low coherence: bottom 30%
            has_low_coherence = coh_pctl <= 0.30

            if has_high_complexity and has_low_coherence:
                # Severity scales with how extreme the signals are
                avg_pctl = (cog_pctl + (1 - coh_pctl)) / 2
                severity = self.BASE_SEVERITY * max(0.5, avg_pctl)

                evidence = [
                    Evidence(
                        signal="cognitive_load",
                        value=fs.cognitive_load,
                        percentile=cog_pctl,
                        description=self._describe_complexity(fs, cog_pctl),
                    ),
                    Evidence(
                        signal="semantic_coherence",
                        value=fs.semantic_coherence,
                        percentile=coh_pctl,
                        description=self._describe_coherence(coh_pctl),
                    ),
                ]

                findings.append(
                    Finding(
                        finding_type=self.name,
                        severity=severity,
                        title=f"God file: {path}",
                        files=[path],
                        evidence=evidence,
                        suggestion=self._build_suggestion(fs),
                        confidence=0.85,
                        effort="HIGH",
                        scope="FILE",
                    )
                )

        return sorted(findings, key=lambda f: f.severity, reverse=True)

    def _describe_complexity(self, fs, cog_pctl: float) -> str:
        """Describe why the file is complex."""
        parts = []
        if fs.function_count > 0:
            parts.append(f"{fs.function_count} functions")
        if fs.lines > 0:
            parts.append(f"{fs.lines} lines")
        if fs.max_nesting > 3:
            parts.append(f"nesting depth {fs.max_nesting}")

        if parts:
            return (
                f"complex ({', '.join(parts)}) — harder to read than {cog_pctl * 100:.0f}% of files"
            )
        return f"harder to read than {cog_pctl * 100:.0f}% of files"

    def _describe_coherence(self, coh_pctl: float) -> str:
        """Describe why the file lacks coherence."""
        return (
            f"unfocused — code suggests multiple unrelated concerns "
            f"(less focused than {(1 - coh_pctl) * 100:.0f}% of files)"
        )

    def _build_suggestion(self, fs) -> str:
        """Build actionable suggestion."""
        if fs.function_count > 5:
            return (
                f"This file has {fs.function_count} functions handling "
                f"unrelated concerns. Identify clusters of related functions "
                f"and extract each group into its own module."
            )
        return (
            "This file is complex and mixes multiple responsibilities. "
            "Look for groups of functions that work on the same data "
            "and extract each group into a focused module."
        )
