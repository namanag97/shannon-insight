"""HiddenCouplingFinder — co-change without structural dependency."""

from pathlib import PurePosixPath
from typing import List, Set

from ..models import Evidence, Finding
from ..store import AnalysisStore

_MIN_LIFT = 2.0
_MIN_CONFIDENCE = 0.5


class HiddenCouplingFinder:
    name = "hidden_coupling"
    requires: Set[str] = {"structural", "temporal"}
    BASE_SEVERITY = 0.9

    def find(self, store: AnalysisStore) -> List[Finding]:
        if not store.structural or not store.cochange:
            return []

        graph = store.structural.graph
        findings = []

        for (file_a, file_b), pair in store.cochange.pairs.items():
            # Skip __init__.py pairs (noise)
            if file_a.endswith("__init__.py") or file_b.endswith("__init__.py"):
                continue

            # Check lift and confidence thresholds
            if pair.lift < _MIN_LIFT:
                continue
            max_conf = max(pair.confidence_a_b, pair.confidence_b_a)
            if max_conf < _MIN_CONFIDENCE:
                continue

            # Check there is NO structural dependency between the pair
            a_deps = set(graph.adjacency.get(file_a, []))
            b_deps = set(graph.adjacency.get(file_b, []))
            if file_b in a_deps or file_a in b_deps:
                continue  # structural dep exists — not hidden

            # Severity based on lift and confidence
            strength = min(1.0, max(0.1, (pair.lift / 10.0 + max_conf) / 2))
            severity = self.BASE_SEVERITY * strength

            # Determine if they share a parent directory
            same_package = (
                str(PurePosixPath(file_a).parent)
                == str(PurePosixPath(file_b).parent)
            )

            # Build human-readable descriptions
            conf_desc = self._describe_confidence(pair, file_a, file_b)

            suggestion = self._build_suggestion(
                file_a, file_b, pair, same_package,
            )

            findings.append(Finding(
                finding_type="hidden_coupling",
                severity=severity,
                title=f"{file_a} and {file_b} always change together",
                files=[file_a, file_b],
                evidence=[
                    Evidence(
                        signal="cochange_count",
                        value=float(pair.cochange_count),
                        percentile=0,
                        description=conf_desc,
                    ),
                    Evidence(
                        signal="cochange_lift",
                        value=pair.lift,
                        percentile=0,
                        description=(
                            f"{pair.lift:.1f}x more often than expected "
                            f"by chance"
                        ),
                    ),
                    Evidence(
                        signal="no_import",
                        value=0.0,
                        percentile=0,
                        description=(
                            "neither file imports the other"
                        ),
                    ),
                ],
                suggestion=suggestion,
            ))

        return findings

    def _describe_confidence(self, pair, file_a, file_b) -> str:
        """Describe co-change in plain terms."""
        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name
        # Use the higher-confidence direction
        if pair.confidence_a_b >= pair.confidence_b_a:
            return (
                f"when {a_name} changed, {b_name} also changed "
                f"{pair.cochange_count} of {pair.total_a} times "
                f"({pair.confidence_a_b * 100:.0f}%)"
            )
        return (
            f"when {b_name} changed, {a_name} also changed "
            f"{pair.cochange_count} of {pair.total_b} times "
            f"({pair.confidence_b_a * 100:.0f}%)"
        )

    def _build_suggestion(self, file_a, file_b, pair, same_package) -> str:
        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name

        if same_package:
            return (
                f"{a_name} and {b_name} are in the same package and "
                f"always change together, but neither imports the other. "
                f"They likely share an implicit contract — a data format, "
                f"naming convention, or config. Make this explicit: either "
                f"add an import, or extract the shared concept into a "
                f"common module."
            )
        return (
            f"These files live in different packages but always change "
            f"together. This suggests a hidden dependency — perhaps "
            f"a shared data format, duplicated logic, or an untracked "
            f"protocol. Find what ties them and either: "
            f"(1) make it an explicit import, or "
            f"(2) extract it into a shared module both can reference."
        )
