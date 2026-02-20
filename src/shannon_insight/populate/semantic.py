"""Populate SEMANTIC layer (R=3)."""
from __future__ import annotations

from ..tensor.core import RelationTensor, SEMANTIC
from ..extract.concepts import cosine_similarity


def populate_semantic(
    tensor: RelationTensor,
    tfidf_vectors: dict[str, dict[str, float]],
    min_cosine: float = 0.3,
    max_neighbors: int = 10,
):
    """Fill T[:,:,t,SEMANTIC] with cosine similarity."""
    files = list(tfidf_vectors.keys())
    t = tensor.n_windows - 1

    # For each file, find top-k most similar
    for a in files:
        vec_a = tfidf_vectors[a]
        if not vec_a:
            continue

        similarities = []
        for b in files:
            if a == b:
                continue
            vec_b = tfidf_vectors[b]
            if not vec_b:
                continue

            sim = cosine_similarity(vec_a, vec_b)
            if sim >= min_cosine:
                similarities.append((b, sim))

        # Keep top-k
        similarities.sort(key=lambda x: -x[1])
        for b, sim in similarities[:max_neighbors]:
            tensor.add_edge(a, b, t, SEMANTIC, weight=sim)
