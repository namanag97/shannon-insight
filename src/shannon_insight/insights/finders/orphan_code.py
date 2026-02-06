"""ORPHAN_CODE — files with no imports and not entry points.

Scope: FILE
Severity: 0.55
Hotspot: NO (structural-only)

An orphan file has in_degree=0 and is neither an entry point nor a test.
These files may be dead code or missing integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class OrphanCodeFinder:
    """Detects orphan files that no other code imports."""

    name = "orphan_code"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"  # Works in all tiers
    deprecated = False
    deprecation_note = None

    # Constants
    BASE_SEVERITY = 0.55

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect orphan files.

        Returns:
            List of findings for orphan files, sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            if not fs.is_orphan:
                continue

            # Build evidence
            evidence = [
                Evidence(
                    signal="in_degree",
                    value=float(fs.in_degree),
                    percentile=0.0,
                    description="No files import this",
                ),
                Evidence(
                    signal="role",
                    value=0.0,
                    percentile=0.0,
                    description=f"Classified as {fs.role}",
                ),
            ]
            if fs.depth == -1:
                evidence.append(
                    Evidence(
                        signal="depth",
                        value=-1.0,
                        percentile=0.0,
                        description="Unreachable from entry points",
                    )
                )

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Orphan file: {path}",
                    files=[path],
                    evidence=evidence,
                    suggestion="Wire into dependency graph or remove if unused.",
                    confidence=1.0,  # Boolean condition, full confidence
                    effort="LOW",
                    scope="FILE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
