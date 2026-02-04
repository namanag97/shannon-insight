"""DeadDependencyFinder — structural dep without co-change."""

from pathlib import PurePosixPath
from typing import List, Set

from ..models import Evidence, Finding
from ..store import AnalysisStore

_MIN_HISTORY_COMMITS = 50


class DeadDependencyFinder:
    name = "dead_dependency"
    requires: Set[str] = {"structural", "temporal"}
    BASE_SEVERITY = 0.4

    def find(self, store: AnalysisStore) -> List[Finding]:
        if not store.structural or not store.cochange or not store.git_history:
            return []

        # Need sufficient history for absence of co-change to be meaningful
        if store.git_history.total_commits < _MIN_HISTORY_COMMITS:
            return []

        graph = store.structural.graph
        cochange = store.cochange
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

                findings.append(Finding(
                    finding_type="dead_dependency",
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
                                f"across {store.git_history.total_commits} commits, "
                                f"{src_name} changed {src_changes} times and "
                                f"{tgt_name} changed {tgt_changes} times — "
                                f"but never in the same commit"
                            ),
                        ),
                    ],
                    suggestion=(
                        f"The import of {tgt_name} in {src_name} may be "
                        f"unused or vestigial. Check whether {src_name} "
                        f"actually uses anything from {tgt_name} — "
                        f"if not, removing it will simplify the dependency graph."
                    ),
                ))

        return findings
