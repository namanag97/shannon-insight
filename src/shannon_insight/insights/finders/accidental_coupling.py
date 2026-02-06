"""ACCIDENTAL_COUPLING — structurally connected but semantically unrelated.

Scope: FILE_PAIR
Severity: 0.50
Hotspot: NO (structural + semantic)

Detected when:
- A structural edge exists (import dependency)
- But concept_overlap(A, B) < 0.2 (Jaccard similarity of concepts)

The dependency exists but the files have nothing in common conceptually.
This suggests the coupling is accidental and should be reconsidered.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


def _concept_overlap(concepts_a: set[str], concepts_b: set[str]) -> float:
    """Compute Jaccard similarity between concept sets.

    Returns 0.0 if either set is empty.
    """
    if not concepts_a or not concepts_b:
        return 0.0
    intersection = concepts_a & concepts_b
    union = concepts_a | concepts_b
    return len(intersection) / len(union) if union else 0.0


class AccidentalCouplingFinder:
    """Detects file pairs that are coupled but unrelated."""

    name = "accidental_coupling"
    api_version = "2.0"
    requires = frozenset({"structural", "semantics"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural + semantic
    tier_minimum = "BAYESIAN"  # Needs concept clusters
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    OVERLAP_THRESHOLD = 0.2
    BASE_SEVERITY = 0.50

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect accidental coupling between file pairs.

        Returns:
            List of findings sorted by severity desc.
        """
        if not store.structural.available:
            return []
        if not store.semantics.available:
            return []

        structural = store.structural.value
        semantics = store.semantics.value

        # Build concept set lookup
        file_concepts: dict[str, set[str]] = {}
        for path, sem in semantics.items():
            # Extract concept topics from FileSemantics
            if hasattr(sem, "concepts"):
                concepts = sem.concepts
                # concepts is a list of Concept objects with .topic attribute
                topics = {c.topic if hasattr(c, "topic") else str(c) for c in concepts}
                file_concepts[path] = topics
            else:
                file_concepts[path] = set()

        findings: list[Finding] = []
        seen_pairs: set[tuple[str, str]] = set()

        # Iterate over structural edges
        if hasattr(structural, "graph") and hasattr(structural.graph, "adjacency"):
            for source, targets in structural.graph.adjacency.items():
                concepts_a = file_concepts.get(source, set())
                if not concepts_a:
                    continue  # No concepts for source, skip

                for target in targets:
                    # Normalize pair (sorted for dedup)
                    pair = tuple(sorted([source, target]))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)

                    concepts_b = file_concepts.get(target, set())
                    if not concepts_b:
                        continue  # No concepts for target, skip

                    # Compute Jaccard overlap
                    overlap = _concept_overlap(concepts_a, concepts_b)

                    # Check threshold
                    if overlap >= self.OVERLAP_THRESHOLD:
                        continue  # Related enough

                    # Compute confidence (lower overlap = higher confidence)
                    confidence = compute_confidence(
                        [
                            ("concept_overlap", overlap, self.OVERLAP_THRESHOLD, "high_is_good"),
                        ]
                    )

                    # Build evidence
                    evidence = [
                        Evidence(
                            signal="concept_overlap",
                            value=overlap,
                            percentile=0.0,
                            description=f"Concept overlap = {overlap:.2f} (Jaccard similarity)",
                        ),
                        Evidence(
                            signal="structural_edge",
                            value=1.0,
                            percentile=0.0,
                            description=f"Import dependency: {source} -> {target}",
                        ),
                    ]

                    # Add concept lists (truncated)
                    concepts_a_str = ", ".join(sorted(concepts_a)[:5])
                    concepts_b_str = ", ".join(sorted(concepts_b)[:5])
                    evidence.append(
                        Evidence(
                            signal="concepts_a",
                            value=float(len(concepts_a)),
                            percentile=0.0,
                            description=f"Concepts in {source}: {concepts_a_str}",
                        )
                    )
                    evidence.append(
                        Evidence(
                            signal="concepts_b",
                            value=float(len(concepts_b)),
                            percentile=0.0,
                            description=f"Concepts in {target}: {concepts_b_str}",
                        )
                    )

                    findings.append(
                        Finding(
                            finding_type=self.name,
                            severity=self.BASE_SEVERITY,
                            title=f"Accidental coupling: {pair[0]} <-> {pair[1]}",
                            files=list(pair),
                            evidence=evidence,
                            suggestion="Connected but unrelated concepts. Consider removing or abstracting the dependency.",
                            confidence=confidence,
                            effort="MEDIUM",
                            scope="FILE_PAIR",
                        )
                    )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
