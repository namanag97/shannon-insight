"""BoundaryMismatchFinder — package boundaries don't match usage.

Scope: MODULE
Severity: 0.6
Hotspot: NO (structural-only)

Modules where boundary_alignment < 0.7, indicating files
in the directory are more connected to files elsewhere.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store import AnalysisStore


class BoundaryMismatchFinder:
    """Detects packages whose boundaries don't match dependency patterns."""

    name = "boundary_mismatch"
    api_version = "2.0"
    requires = frozenset({"structural"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.6

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect boundary mismatches in packages."""
        if not store.structural.available:
            return []

        structural = store.structural.value
        findings = []

        for bm in structural.boundary_mismatches:
            # Skip root directory - not a meaningful module boundary
            if bm.module_path == "." or bm.module_path == "":
                continue

            # Only include mismatches with actionable suggestions
            useful_misplaced = [
                (f, s)
                for f, s in bm.misplaced_files
                if s and s != bm.module_path and s != "unknown" and s != "."
            ]
            if not useful_misplaced:
                continue

            module = structural.modules.get(bm.module_path)
            if not module or module.file_count <= 2:
                continue

            alignment = module.boundary_alignment
            if alignment >= 0.7:
                continue

            # Severity scales with how misaligned the boundary is
            strength = max(0.1, min(1.0, 1.0 - alignment))
            severity = self.BASE_SEVERITY * strength

            # Build a clear relocation list
            relocations = []
            for f, s in useful_misplaced[:4]:
                f_name = PurePosixPath(f).name
                relocations.append(f"  {f_name} is more connected to {s}/")

            reloc_text = "\n".join(relocations)
            if len(useful_misplaced) > 4:
                reloc_text += f"\n  ...and {len(useful_misplaced) - 4} more"

            n_communities = len(bm.community_distribution)
            mod_name = bm.module_path

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Boundary mismatch: {mod_name}/",
                    files=[f for f, _ in useful_misplaced],
                    evidence=[
                        Evidence(
                            signal="boundary_alignment",
                            value=alignment,
                            percentile=0,
                            description=(
                                f"only {alignment * 100:.0f}% of files in this "
                                f"directory import each other"
                            ),
                        ),
                        Evidence(
                            signal="community_count",
                            value=float(n_communities),
                            percentile=0,
                            description=(
                                f"dependency analysis found {n_communities} "
                                f"distinct clusters inside this directory"
                            ),
                        ),
                    ],
                    suggestion=(
                        f"Files in {mod_name}/ belong to {n_communities} clusters. "
                        f"Consider moving:\n{reloc_text}"
                    ),
                    confidence=0.7,
                    effort="HIGH",
                    scope="MODULE",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
