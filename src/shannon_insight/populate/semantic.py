"""Populate SEMANTIC layer (R=3) from TF-IDF concept vectors.

Computes pairwise cosine similarity between TF-IDF vectors.  Only edges
with similarity >= *min_cosine* are kept, and each file retains at most
*max_neighbors* nearest neighbours (ranked by similarity).
"""

from __future__ import annotations

import math
from typing import Any

from ..tensor.core import SEMANTIC


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Cosine similarity between two sparse vectors represented as dicts."""
    if not vec_a or not vec_b:
        return 0.0

    common = vec_a.keys() & vec_b.keys()
    if not common:
        return 0.0

    dot = sum(vec_a[k] * vec_b[k] for k in common)

    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def populate_semantic(
    tensor: Any,
    tfidf_vectors: dict[str, dict[str, float]],
    min_cosine: float = 0.3,
    max_neighbors: int = 10,
) -> None:
    """Fill T[:,:,t,SEMANTIC] with cosine similarity.

    Args:
        tensor: A ``RelationTensor`` instance.
        tfidf_vectors: ``{path: {term: tfidf_score}}`` sparse vectors.
        min_cosine: Minimum cosine similarity threshold.
        max_neighbors: Maximum number of most-similar neighbours per file.
    """
    files = list(tfidf_vectors.keys())
    t = tensor.n_windows - 1

    for a in files:
        vec_a = tfidf_vectors[a]
        if not vec_a:
            continue

        # Collect all similarities above threshold
        similarities: list[tuple[str, float]] = []
        for b in files:
            if a == b:
                continue
            vec_b = tfidf_vectors[b]
            if not vec_b:
                continue

            sim = _cosine_similarity(vec_a, vec_b)
            if sim >= min_cosine:
                similarities.append((b, sim))

        # Keep top-k neighbours
        similarities.sort(key=lambda x: -x[1])
        for b, sim in similarities[:max_neighbors]:
            tensor.add_edge(a, b, t, SEMANTIC, weight=sim)
