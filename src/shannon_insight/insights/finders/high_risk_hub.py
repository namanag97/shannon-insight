"""HighRiskHubFinder — central + complex + churning files."""

from typing import List, Set

from ..models import Evidence, Finding
from ..ranking import compute_percentiles
from ..store import AnalysisStore

_MIN_FILES = 5


class HighRiskHubFinder:
    name = "high_risk_hub"
    requires: Set[str] = {"structural", "file_signals"}
    BASE_SEVERITY = 1.0

    def find(self, store: AnalysisStore) -> List[Finding]:
        if not store.structural or not store.file_signals:
            return []
        if len(store.structural.files) < _MIN_FILES:
            return []

        files = store.structural.files
        total_files = len(files)

        # Gather signals
        pageranks = {p: f.pagerank for p, f in files.items()}
        blast = {
            p: f.blast_radius_size / total_files if total_files > 0 else 0 for p, f in files.items()
        }
        cognitive = {p: store.file_signals.get(p, {}).get("cognitive_load", 0) for p in files}

        # Compute percentiles
        pr_pct = compute_percentiles(pageranks)
        bl_pct = compute_percentiles(blast)
        cg_pct = compute_percentiles(cognitive)

        # Optionally include churn if temporal available
        churn_pct = {}
        if store.churn:
            churn_vals = {p: float(store.churn[p].total_changes) for p in files if p in store.churn}
            churn_pct = compute_percentiles(churn_vals)

        findings = []
        for path in files:
            fa = files[path]
            evidence_items = []
            pcts = []

            # Track which signal categories fired
            has_connectivity = False
            has_complexity = False
            has_churn = False

            # Check PageRank (connectivity signal)
            pr_p = pr_pct.get(path, 0)
            if pr_p >= 90:
                has_connectivity = True
                pcts.append(pr_p)
                evidence_items.append(
                    Evidence(
                        signal="pagerank",
                        value=pageranks[path],
                        percentile=pr_p,
                        description=(f"{fa.in_degree} files import this directly"),
                    )
                )

            # Check blast radius (connectivity signal)
            bl_p = bl_pct.get(path, 0)
            if bl_p >= 90:
                has_connectivity = True
                pcts.append(bl_p)
                evidence_items.append(
                    Evidence(
                        signal="blast_radius_pct",
                        value=blast[path],
                        percentile=bl_p,
                        description=(
                            f"a bug here could affect "
                            f"{fa.blast_radius_size} of {total_files} files "
                            f"({blast[path] * 100:.0f}% of the codebase)"
                        ),
                    )
                )

            # Check cognitive load (complexity signal)
            cg_p = cg_pct.get(path, 0)
            if cg_p >= 90:
                has_complexity = True
                pcts.append(cg_p)
                evidence_items.append(
                    Evidence(
                        signal="cognitive_load",
                        value=cognitive[path],
                        percentile=cg_p,
                        description=(
                            f"harder to understand than {cg_p:.0f}% of files in this codebase"
                        ),
                    )
                )

            # Optional: churn (activity signal)
            if churn_pct:
                ch_p = churn_pct.get(path, 0)
                if ch_p >= 90:
                    has_churn = True
                    pcts.append(ch_p)
                    churn_val = (
                        store.churn[path].total_changes
                        if store.churn and path in store.churn
                        else 0
                    )
                    evidence_items.append(
                        Evidence(
                            signal="churn",
                            value=float(churn_val),
                            percentile=ch_p,
                            description=f"changed {churn_val} times in recent history",
                        )
                    )

            # Need 2+ high signals to qualify
            if len(pcts) < 2:
                continue

            avg_pct = sum(pcts) / len(pcts)
            severity = self.BASE_SEVERITY * max(0.1, min(1.0, avg_pct / 100))

            suggestion = self._build_suggestion(
                path,
                fa,
                total_files,
                has_connectivity,
                has_complexity,
                has_churn,
            )

            findings.append(
                Finding(
                    finding_type="high_risk_hub",
                    severity=severity,
                    title=f"{path} is a high-risk hub",
                    files=[path],
                    evidence=evidence_items,
                    suggestion=suggestion,
                )
            )

        return findings

    def _build_suggestion(
        self,
        path,
        fa,
        total_files,
        has_connectivity,
        has_complexity,
        has_churn,
    ) -> str:
        parts = []

        if has_connectivity and has_complexity:
            parts.append(
                f"This file is both heavily depended on "
                f"({fa.in_degree} direct importers, "
                f"blast radius {fa.blast_radius_size}/{total_files} files) "
                f"and complex. Split it: move distinct type groups or "
                f"utility functions into separate files so consumers "
                f"only import what they need."
            )
        elif has_connectivity:
            parts.append(
                f"Many files depend on this "
                f"({fa.in_degree} direct importers), "
                f"so any change here ripples across "
                f"{fa.blast_radius_size} files. "
                f"Reduce the blast radius by splitting into "
                f"smaller, focused modules — or introduce "
                f"interfaces so consumers aren't tightly coupled "
                f"to the implementation."
            )
        elif has_complexity and has_churn:
            parts.append(
                "This file is both complex and frequently modified. "
                "Each change carries higher risk of introducing bugs. "
                "Extract the parts that change most often into a "
                "separate, well-tested module."
            )
        elif has_complexity:
            parts.append(
                "This file is disproportionately complex. "
                "Break it into smaller pieces — each with a single "
                "clear purpose — to make changes safer and reviews easier."
            )
        else:
            parts.append(
                "Multiple risk signals converge on this file. "
                "Review whether it can be decomposed into smaller, "
                "focused modules."
            )

        return " ".join(parts)
