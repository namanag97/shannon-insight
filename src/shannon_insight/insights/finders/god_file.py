"""GodFileFinder — high cognitive load + low coherence."""

from typing import List, Set

from ..models import Evidence, Finding
from ..ranking import compute_percentiles
from ..store import AnalysisStore

_MIN_FILES = 5


class GodFileFinder:
    name = "god_file"
    requires: Set[str] = {"file_signals"}
    BASE_SEVERITY = 0.8

    def find(self, store: AnalysisStore) -> List[Finding]:
        if not store.file_signals:
            return []
        if len(store.file_signals) < _MIN_FILES:
            return []

        # Extract cognitive load and coherence signals
        cognitive = {
            p: signals.get("cognitive_load", 0) for p, signals in store.file_signals.items()
        }
        coherence = {
            p: signals.get("semantic_coherence", 0) for p, signals in store.file_signals.items()
        }

        cg_pct = compute_percentiles(cognitive)
        co_pct = compute_percentiles(coherence)

        # Get structural data if available for richer descriptions
        structural_files = store.structural.files if store.structural else {}

        findings = []
        for path in store.file_signals:
            cg_p = cg_pct.get(path, 0)
            co_p = co_pct.get(path, 100)

            # Top 10% cognitive load AND bottom 20% coherence
            if cg_p >= 90 and co_p <= 20:
                avg_pct = (cg_p + (100 - co_p)) / 2
                strength = max(0.1, min(1.0, avg_pct / 100))
                severity = self.BASE_SEVERITY * strength

                fa = structural_files.get(path)
                cg_desc = self._describe_complexity(fa, cg_p)
                co_desc = self._describe_coherence(co_p)
                suggestion = self._build_suggestion(path, fa)

                findings.append(
                    Finding(
                        finding_type="god_file",
                        severity=severity,
                        title=f"{path} does too many things",
                        files=[path],
                        evidence=[
                            Evidence(
                                signal="cognitive_load",
                                value=cognitive[path],
                                percentile=cg_p,
                                description=cg_desc,
                            ),
                            Evidence(
                                signal="semantic_coherence",
                                value=coherence[path],
                                percentile=co_p,
                                description=co_desc,
                            ),
                        ],
                        suggestion=suggestion,
                    )
                )

        return findings

    def _describe_complexity(self, fa, cg_p: float) -> str:
        if fa and fa.function_count > 0:
            parts = [f"{fa.function_count} functions"]
            if fa.lines > 0:
                parts.append(f"{fa.lines} lines")
            if fa.nesting_depth > 3:
                parts.append(f"nesting depth {fa.nesting_depth}")
            return f"complex ({', '.join(parts)}) — harder to read than {cg_p:.0f}% of files"
        return f"harder to read than {cg_p:.0f}% of files in this codebase"

    def _describe_coherence(self, co_p: float) -> str:
        return (
            f"unfocused — variable/function names suggest "
            f"multiple unrelated concerns (less focused than "
            f"{100 - co_p:.0f}% of files)"
        )

    def _build_suggestion(self, path: str, fa) -> str:
        if fa and fa.function_count > 5:
            return (
                f"This file has {fa.function_count} functions handling "
                f"unrelated concerns. "
                f"Identify clusters of related functions and extract "
                f"each group into its own module. A good heuristic: "
                f"if you can't describe what the file does in one sentence, "
                f"it should be split."
            )
        return (
            "This file is complex and mixes multiple responsibilities. "
            "Look for groups of functions that work on the same data "
            "or concept, and extract each group into a focused module."
        )
