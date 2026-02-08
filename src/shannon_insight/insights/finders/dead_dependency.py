"""DeadDependencyFinder — structural dep without co-change.

Scope: FILE_PAIR
Severity: 0.4
Hotspot: YES (requires temporal data)

An import exists but the files never change together,
suggesting the import may be unused or vestigial.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from ..models import Evidence, Finding

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore

_MIN_HISTORY_COMMITS = 50


class DeadDependencyFinder:
    """Detects structural dependencies with no co-change evidence."""

    name = "dead_dependency"
    api_version = "2.0"
    requires = frozenset({"structural", "cochange", "git_history"})
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "ABSOLUTE"
    deprecated = False
    deprecation_note = None

    BASE_SEVERITY = 0.4

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect dead dependencies."""
        if not store.structural.available:
            return []
        if not store.cochange.available:
            return []
        if not store.git_history.available:
            return []

        git_history = store.git_history.value

        # Need sufficient history for absence of co-change to be meaningful
        if git_history.total_commits < _MIN_HISTORY_COMMITS:
            return []

        structural = store.structural.value
        cochange = store.cochange.value
        graph = structural.graph
        change_counts = cochange.file_change_counts
        findings = []

        for src, targets in graph.adjacency.items():
            for tgt in targets:
                # Both files must have been changed at least once
                src_changes = change_counts.get(src, 0)
                tgt_changes = change_counts.get(tgt, 0)
                if src_changes == 0 or tgt_changes == 0:
                    continue

                # Check co-change count is 0
                pair_key = (min(src, tgt), max(src, tgt))
                if pair_key in cochange.pairs:
                    continue  # they do co-change

                severity = self.BASE_SEVERITY * 0.7

                src_name = PurePosixPath(src).name
                tgt_name = PurePosixPath(tgt).name

                findings.append(
                    Finding(
                        finding_type=self.name,
                        severity=severity,
                        title=f"{src} imports {tgt} but they never change together",
                        files=[src, tgt],
                        evidence=[
                            Evidence(
                                signal="structural_dep",
                                value=1.0,
                                percentile=0,
                                description=f"{src_name} has an import statement for {tgt_name}",
                            ),
                            Evidence(
                                signal="cochange_count",
                                value=0.0,
                                percentile=0,
                                description=(
                                    f"across {git_history.total_commits} commits, "
                                    f"{src_name} changed {src_changes} times and "
                                    f"{tgt_name} changed {tgt_changes} times — "
                                    f"but never in the same commit"
                                ),
                            ),
                        ],
                        suggestion=(
                            f"The import of {tgt_name} in {src_name} may be "
                            f"unused or vestigial. Check if it can be removed."
                        ),
                        confidence=0.6,
                        effort="LOW",
                        scope="FILE_PAIR",
                    )
                )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
