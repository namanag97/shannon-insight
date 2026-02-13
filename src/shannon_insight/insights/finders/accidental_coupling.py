"""ACCIDENTAL_COUPLING — structurally connected but semantically unrelated.

Scope: FILE_PAIR
Severity: 0.50
Hotspot: NO (structural + semantic)

Detected when:
- A structural edge exists (import dependency)
- But combined similarity (import fingerprint + concept overlap) < 0.15
- Neither file is an infrastructure file (models, __init__, config, etc.)

Uses import fingerprint cosine similarity (weighted by import surprise)
combined with Jaccard concept overlap for robust detection.
"""

from __future__ import annotations

import math
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore

# Roles that are DESIGNED for broad import — coupling to them is expected
_INFRASTRUCTURE_ROLES = frozenset(
    {"model", "config", "interface", "exception", "constant", "utility"}
)

# Filename stems that are infrastructure by convention
_INFRASTRUCTURE_STEMS = frozenset(
    {
        "models",
        "model",
        "schemas",
        "schema",
        "types",
        "exceptions",
        "errors",
        "constants",
        "protocols",
        "interfaces",
        # Common utility/infrastructure files
        "logging",
        "logging_config",
        "logger",
        "log",
        "config",
        "settings",
        "utils",
        "util",
        "helpers",
        "helper",
        "common",
        "base",
        "core",
        "_common",
    }
)


def _concept_overlap(concepts_a: set[str], concepts_b: set[str]) -> float:
    """Compute Jaccard similarity between concept sets."""
    if not concepts_a or not concepts_b:
        return 0.0
    intersection = concepts_a & concepts_b
    union = concepts_a | concepts_b
    return len(intersection) / len(union) if union else 0.0


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    if not vec_a or not vec_b:
        return 0.0

    keys = set(vec_a) & set(vec_b)
    if not keys:
        return 0.0

    dot = sum(vec_a[k] * vec_b[k] for k in keys)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def _is_infrastructure(path: str, roles: dict[str, str]) -> bool:
    """Check if a file is infrastructure (designed for broad import)."""
    if path.endswith("__init__.py"):
        return True

    stem = PurePosixPath(path).stem.lower()
    if stem in _INFRASTRUCTURE_STEMS:
        return True

    role = roles.get(path, "unknown").lower()
    return role in _INFRASTRUCTURE_ROLES


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

    COMBINED_THRESHOLD = 0.15
    BASE_SEVERITY = 0.50
    MAX_FINDINGS = 20

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect accidental coupling between file pairs."""
        if not store.structural.available:
            return []
        if not store.semantics.available:
            return []

        structural = store.structural.value
        semantics = store.semantics.value

        # Get role lookup
        roles: dict[str, str] = {}
        if store.roles.available:
            roles = store.roles.value

        # Build concept set and import fingerprint lookups
        file_concepts: dict[str, set[str]] = {}
        file_fingerprints: dict[str, dict[str, float]] = {}

        for path, sem in semantics.items():
            if hasattr(sem, "concepts"):
                topics = {c.topic if hasattr(c, "topic") else str(c) for c in sem.concepts}
                file_concepts[path] = topics
            else:
                file_concepts[path] = set()

            if hasattr(sem, "import_fingerprint"):
                file_fingerprints[path] = sem.import_fingerprint
            else:
                file_fingerprints[path] = {}

        findings: list[Finding] = []
        seen_pairs: set[tuple[str, str]] = set()

        if hasattr(structural, "graph") and hasattr(structural.graph, "adjacency"):
            for source, targets in structural.graph.adjacency.items():
                # Skip if source is infrastructure
                if _is_infrastructure(source, roles):
                    continue

                concepts_a = file_concepts.get(source, set())
                fp_a = file_fingerprints.get(source, {})

                for target in targets:
                    # Skip if target is infrastructure
                    if _is_infrastructure(target, roles):
                        continue

                    pair = tuple(sorted([source, target]))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)

                    concepts_b = file_concepts.get(target, set())
                    fp_b = file_fingerprints.get(target, {})

                    # Skip if no data at all for either side
                    if not concepts_a and not fp_a:
                        continue
                    if not concepts_b and not fp_b:
                        continue

                    # Compute combined similarity
                    import_sim = _cosine_similarity(fp_a, fp_b)
                    concept_sim = _concept_overlap(concepts_a, concepts_b)
                    combined = 0.6 * import_sim + 0.4 * concept_sim

                    if combined >= self.COMBINED_THRESHOLD:
                        continue  # Related enough

                    # Compute confidence
                    confidence = compute_confidence(
                        [
                            (
                                "combined_similarity",
                                combined,
                                self.COMBINED_THRESHOLD,
                                "high_is_good",
                            ),
                        ]
                    )

                    evidence = [
                        Evidence(
                            signal="combined_similarity",
                            value=combined,
                            percentile=0.0,
                            description=f"Combined similarity = {combined:.2f} (import: {import_sim:.2f}, concept: {concept_sim:.2f})",
                        ),
                        Evidence(
                            signal="structural_edge",
                            value=1.0,
                            percentile=0.0,
                            description=f"Import dependency: {source} -> {target}",
                        ),
                    ]

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

        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings[: self.MAX_FINDINGS]
