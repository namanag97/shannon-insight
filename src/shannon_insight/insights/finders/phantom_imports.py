"""PHANTOM_IMPORTS — files importing modules that don't exist.

Scope: FILE
Severity: 0.65
Hotspot: NO (structural-only)

A file has phantom imports when it imports modules that cannot be resolved
in the codebase. These may be:
- Typos in import statements
- Missing modules that were never created
- AI-generated code referencing non-existent modules
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore

_MAX_FINDINGS = 10  # Cap output to avoid flooding


class PhantomImportsFinder:
    """Detects files with unresolved imports."""

    name = "phantom_imports"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"  # Works in all tiers
    deprecated = False
    deprecation_note = None

    # Constants
    BASE_SEVERITY = 0.65

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect files with phantom imports.

        Returns:
            List of findings sorted by severity desc.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            if fs.phantom_import_count <= 0:
                continue

            # Compute severity based on count (more phantoms = worse)
            # Scale: 1 phantom = 0.65, 5+ = 0.80
            severity = min(0.80, self.BASE_SEVERITY + 0.03 * (fs.phantom_import_count - 1))

            # Compute phantom ratio for context
            phantom_ratio = fs.phantom_import_count / max(fs.import_count, 1)

            # Build evidence
            evidence = [
                Evidence(
                    signal="phantom_import_count",
                    value=float(fs.phantom_import_count),
                    percentile=0.0,
                    description=f"{fs.phantom_import_count} unresolved import(s)",
                ),
                Evidence(
                    signal="import_count",
                    value=float(fs.import_count),
                    percentile=0.0,
                    description=f"{fs.import_count} total imports",
                ),
                Evidence(
                    signal="phantom_ratio",
                    value=phantom_ratio,
                    percentile=0.0,
                    description=f"{phantom_ratio * 100:.0f}% of imports are phantom",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Phantom imports: {path} ({fs.phantom_import_count} unresolved)",
                    files=[path],
                    evidence=evidence,
                    suggestion="Create missing module or replace with existing library.",
                    confidence=1.0,  # Boolean condition (count > 0)
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings[:_MAX_FINDINGS]
