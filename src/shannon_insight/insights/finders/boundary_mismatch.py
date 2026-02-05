"""BoundaryMismatchFinder — repackages existing boundary analysis."""

from pathlib import PurePosixPath
from typing import List, Set

from ..models import Evidence, Finding
from ..store import AnalysisStore


class BoundaryMismatchFinder:
    name = "boundary_mismatch"
    requires: Set[str] = {"structural"}
    BASE_SEVERITY = 0.6

    def find(self, store: AnalysisStore) -> List[Finding]:
        if not store.structural:
            return []

        findings = []
        for bm in store.structural.boundary_mismatches:
            # Only include mismatches with actionable suggestions
            useful_misplaced = [
                (f, s)
                for f, s in bm.misplaced_files
                if s and s != bm.module_path and s != "unknown"
            ]
            if not useful_misplaced:
                continue

            module = store.structural.modules.get(bm.module_path)
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
                s_name = PurePosixPath(s).name or s
                relocations.append(f"  {f_name} is more connected to {s}/")

            reloc_text = "\n".join(relocations)
            if len(useful_misplaced) > 4:
                reloc_text += f"\n  ...and {len(useful_misplaced) - 4} more"

            n_communities = len(bm.community_distribution)
            mod_name = bm.module_path

            findings.append(
                Finding(
                    finding_type="boundary_mismatch",
                    severity=severity,
                    title=(f"{mod_name}/ groups files that don't actually work together"),
                    files=[f for f, _ in useful_misplaced],
                    evidence=[
                        Evidence(
                            signal="boundary_alignment",
                            value=alignment,
                            percentile=0,
                            description=(
                                f"only {alignment * 100:.0f}% of files in this "
                                f"directory import each other — "
                                f"the rest are more connected elsewhere"
                            ),
                        ),
                        Evidence(
                            signal="community_count",
                            value=float(n_communities),
                            percentile=0,
                            description=(
                                f"dependency analysis found {n_communities} "
                                f"distinct clusters inside this one directory"
                            ),
                        ),
                    ],
                    suggestion=(
                        f"The files in {mod_name}/ belong to "
                        f"{n_communities} separate dependency clusters. "
                        f"Based on actual import patterns:\n{reloc_text}\n"
                        f"Moving these files would make the package "
                        f"boundaries match real usage."
                    ),
                )
            )

        return findings
