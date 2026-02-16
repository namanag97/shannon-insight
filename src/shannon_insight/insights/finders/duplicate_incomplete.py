"""DUPLICATE_INCOMPLETE — Clone pairs where both files are incomplete.

Scope: FILE_PAIR
Severity: HIGH (0.75)
Hotspot: NO

Detects duplicate incomplete implementations:
- Both files are clones (NCD < 0.3)
- Both have stub_ratio > 0.3 OR phantom_import_count > 0
- Both are likely abandoned

This identifies when incomplete code was copy-pasted, multiplying
the problem.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store import AnalysisStore


class DuplicateIncompleteFinder:
    """Detects duplicate incomplete implementations."""

    name = "duplicate_incomplete"
    api_version = "2.0"
    requires = frozenset({"clone_pairs", "signal_field"})
    error_mode = "skip"
    hotspot_filtered = False
    tier_minimum = "ABSOLUTE"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.75
    STUB_RATIO_THRESHOLD = 0.3
    PHANTOM_IMPORT_THRESHOLD = 0

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect duplicate incomplete implementations."""
        if not store.clone_pairs.available or not store.signal_field.available:
            return []

        clone_pairs = store.clone_pairs.value
        field = store.signal_field.value

        findings: list[Finding] = []

        for pair in clone_pairs:
            path_a, path_b = pair.file_a, pair.file_b

            fs_a = field.per_file.get(path_a)
            fs_b = field.per_file.get(path_b)

            if not fs_a or not fs_b:
                continue

            # Both files must be incomplete
            incomplete_a = (
                fs_a.stub_ratio > self.STUB_RATIO_THRESHOLD
                or fs_a.phantom_import_count > self.PHANTOM_IMPORT_THRESHOLD
            )
            incomplete_b = (
                fs_b.stub_ratio > self.STUB_RATIO_THRESHOLD
                or fs_b.phantom_import_count > self.PHANTOM_IMPORT_THRESHOLD
            )

            if not (incomplete_a and incomplete_b):
                continue

            # Adjust severity based on how incomplete
            severity = self.BASE_SEVERITY
            if fs_a.stub_ratio > 0.5 and fs_b.stub_ratio > 0.5:
                severity += 0.1
            if fs_a.phantom_import_count > 0 and fs_b.phantom_import_count > 0:
                severity += 0.1
            severity = min(0.90, severity)

            evidence = [
                Evidence(
                    signal="ncd",
                    value=pair.ncd,
                    percentile=0.0,
                    description=f"Clone similarity: {pair.ncd:.2f}",
                ),
                Evidence(
                    signal="stub_ratio",
                    value=fs_a.stub_ratio,
                    percentile=fs_a.percentiles.get("stub_ratio", 0.0) * 100,
                    description=f"{path_a}: {fs_a.stub_ratio * 100:.0f}% stubs",
                ),
                Evidence(
                    signal="stub_ratio",
                    value=fs_b.stub_ratio,
                    percentile=fs_b.percentiles.get("stub_ratio", 0.0) * 100,
                    description=f"{path_b}: {fs_b.stub_ratio * 100:.0f}% stubs",
                ),
                Evidence(
                    signal="phantom_import_count",
                    value=float(fs_a.phantom_import_count + fs_b.phantom_import_count),
                    percentile=0.0,
                    description=f"Total phantom imports: {fs_a.phantom_import_count + fs_b.phantom_import_count}",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Duplicate incomplete: {path_a} ≈ {path_b}",
                    files=[path_a, path_b],
                    evidence=evidence,
                    suggestion="Both files are incomplete copies. Complete one implementation and delete the duplicate.",
                    confidence=0.90,
                    effort="HIGH",
                    scope="FILE_PAIR",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
