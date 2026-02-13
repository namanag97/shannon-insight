"""INCOMPLETE_IMPLEMENTATION — Files with phantom imports/broken calls or high stub ratio.

Scope: FILE
Severity: HIGH (0.80)
Hotspot: NO

Incomplete implementation indicators:
- phantom_import_count > 0 (imports don't exist)
- broken_call_count > 0 (calls to undefined things)
- stub_ratio > 0.5 (50%+ functions are stubs)
- impl_gini < 0.2 (very uniform function sizes = AI-generated boilerplate)
- Low total_changes (never updated/finished)

This identifies code that was never completed, whether by AI or humans.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class IncompleteImplementationFinder:
    """Detects incomplete or abandoned implementations."""

    name = "incomplete_implementation"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False
    tier_minimum = "ABSOLUTE"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.80
    STUB_RATIO_THRESHOLD = 0.6  # Tightened from 0.5
    IMPL_GINI_THRESHOLD = 0.15  # Tightened from 0.2
    MIN_ISSUES = 2  # Require at least 2 signals to fire

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect incomplete implementations."""
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            issues: list[tuple[str, float]] = []

            # Broken imports
            if fs.phantom_import_count > 0:
                issues.append(("phantom_import_count", 0.3))

            # Broken calls
            if fs.broken_call_count > 0:
                issues.append(("broken_call_count", 0.4))

            # High stub ratio
            if fs.stub_ratio > self.STUB_RATIO_THRESHOLD:
                issues.append(("stub_ratio", 0.2))

            # Uniform function sizes (AI pattern or incomplete) - only flag if ALSO has high stub ratio
            if (
                fs.impl_gini < self.IMPL_GINI_THRESHOLD
                and fs.function_count > 5
                and fs.stub_ratio > 0.3
            ):
                issues.append(("impl_gini", 0.1))

            # Require strong signals to trigger:
            # - phantom_import OR broken_call is enough alone (runtime errors)
            # - otherwise need at least 2 issues
            has_runtime_issue = any(
                i[0] in ("phantom_import_count", "broken_call_count") for i in issues
            )
            if not has_runtime_issue and len(issues) < self.MIN_ISSUES:
                continue

            # Adjust severity based on count/severity of issues
            severity = self.BASE_SEVERITY
            severity += len(issues) * 0.05
            if any("phantom_import_count" in i or "broken_call_count" in i for i in issues):
                severity += 0.1  # Runtime errors are worse
            severity = min(0.95, severity)

            evidence = [
                Evidence(
                    signal="phantom_import_count",
                    value=float(fs.phantom_import_count),
                    percentile=0.0,
                    description=f"{fs.phantom_import_count} imports not found",
                ),
                Evidence(
                    signal="broken_call_count",
                    value=float(fs.broken_call_count),
                    percentile=0.0,
                    description=f"{fs.broken_call_count} calls to undefined symbols",
                ),
                Evidence(
                    signal="stub_ratio",
                    value=fs.stub_ratio,
                    percentile=fs.percentiles.get("stub_ratio", 0.0) * 100,
                    description=f"{fs.stub_ratio * 100:.0f}% of functions are stubs",
                ),
                Evidence(
                    signal="impl_gini",
                    value=fs.impl_gini,
                    percentile=fs.percentiles.get("impl_gini", 0.0) * 100,
                    description=f"function size gini: {fs.impl_gini:.2f} (uniform = incomplete)",
                ),
                Evidence(
                    signal="total_changes",
                    value=float(fs.total_changes),
                    percentile=fs.percentiles.get("total_changes", 0.0) * 100,
                    description=f"{fs.total_changes} total changes (never finished?)",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Incomplete implementation: {path}",
                    files=[path],
                    evidence=evidence,
                    suggestion="This file has broken dependencies and/or stub functions. Fix imports, implement stubs, or remove dead code.",
                    confidence=0.90,
                    effort="HIGH",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
