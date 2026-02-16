"""DIRECTORY_HOTSPOT — Entire directories that are problematic.

Scope: DIRECTORY (new!)
Severity: HIGH (0.80)
Hotspot: YES

A directory hotspot has:
- Multiple files with high risk
- High average churn across the directory
- Poor health indicators

This identifies systemic issues at the folder level, not just individual files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store import AnalysisStore


class DirectoryHotspotFinder:
    """Detects problematic directories (not just files)."""

    name = "directory_hotspot"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False  # Directory-level, different logic
    tier_minimum = "BAYESIAN"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.80
    MIN_FILES = 3  # Need enough files to judge

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect directory hotspots.

        Criteria:
        - Directory has >= 3 files
        - high_risk_file_count >= 2 OR hotspot_file_count > 50%
        - Not a test directory
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value

        if field.tier == "ABSOLUTE":
            return []

        findings: list[Finding] = []

        for dir_path, ds in sorted(field.per_directory.items()):
            # Skip root directory - not a meaningful directory
            if dir_path == "." or dir_path == "":
                continue

            # Need enough files
            if ds.file_count < self.MIN_FILES:
                continue

            # Skip test directories
            if "test" in dir_path.lower():
                continue

            # Check for hotspot conditions
            high_risk_pct = ds.high_risk_file_count / ds.file_count
            hotspot_pct = ds.hotspot_file_count / ds.file_count

            is_high_risk = ds.high_risk_file_count >= 2
            is_hotspot = hotspot_pct > 0.5

            if not (is_high_risk or is_hotspot):
                continue

            # Calculate severity and confidence
            severity = self.BASE_SEVERITY
            confidence_conditions = []

            if is_high_risk and is_hotspot:
                severity = 0.90
            elif high_risk_pct > 0.5:
                severity = 0.88

            if is_high_risk:
                confidence_conditions.append(("high_risk_pct", high_risk_pct, 0.3, "high_is_bad"))
            if is_hotspot:
                confidence_conditions.append(("hotspot_pct", hotspot_pct, 0.5, "high_is_bad"))

            confidence = compute_confidence(confidence_conditions) if confidence_conditions else 0.8

            evidence = [
                Evidence(
                    signal="high_risk_file_count",
                    value=ds.high_risk_file_count,
                    percentile=0,
                    description=f"{ds.high_risk_file_count}/{ds.file_count} files are high-risk",
                ),
                Evidence(
                    signal="hotspot_file_count",
                    value=ds.hotspot_file_count,
                    percentile=0,
                    description=f"{ds.hotspot_file_count}/{ds.file_count} files are active hotspots",
                ),
                Evidence(
                    signal="avg_complexity",
                    value=ds.avg_complexity,
                    percentile=0,
                    description=f"average cognitive load {ds.avg_complexity:.1f}",
                ),
                Evidence(
                    signal="avg_churn",
                    value=ds.avg_churn,
                    percentile=0,
                    description=f"average {ds.avg_churn:.1f} changes per file",
                ),
            ]

            # Get the specific high-risk files
            high_risk_files = []
            for fpath, fs in field.per_file.items():
                if fs.parent_dir == dir_path and fs.risk_score > 0.7:
                    high_risk_files.append(fpath)

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Directory hotspot: {dir_path}/",
                    files=high_risk_files[:5] if high_risk_files else [dir_path],
                    evidence=evidence,
                    suggestion=f"This entire directory has systemic issues. Consider refactoring {dir_path}/ as a whole rather than individual files.",
                    confidence=max(0.75, confidence),
                    effort="HIGH",
                    scope="MODULE",  # Directory-level
                )
            )

        return findings
