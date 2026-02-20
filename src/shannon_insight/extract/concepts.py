"""Concept extraction using TF-IDF."""
from __future__ import annotations

import math
import re
from collections import Counter


def tokenize_identifiers(identifiers: frozenset[str]) -> list[str]:
    """Split identifiers into tokens."""
    tokens = []
    for ident in identifiers:
        # Split camelCase
        parts = re.sub(r'([a-z])([A-Z])', r'\1_\2', ident)
        # Split on underscores
        for part in parts.split("_"):
            if part and len(part) > 1:
                tokens.append(part.lower())
    return tokens


def compute_tfidf(
    documents: dict[str, frozenset[str]]
) -> tuple[dict[str, dict[str, float]], dict[str, list[tuple[str, float]]]]:
    """
    Compute TF-IDF vectors for documents.

    Returns:
        - tfidf_vectors: {path: {term: score}}
        - concepts: {path: [(term, score), ...]}  # Top 10
    """
    # Tokenize all documents
    doc_tokens: dict[str, list[str]] = {}
    for path, identifiers in documents.items():
        doc_tokens[path] = tokenize_identifiers(identifiers)

    # Compute document frequencies
    df: Counter[str] = Counter()
    for tokens in doc_tokens.values():
        df.update(set(tokens))

    n_docs = len(documents)
    idf = {term: math.log(n_docs / count) for term, count in df.items() if count > 0}

    # Compute TF-IDF
    tfidf_vectors: dict[str, dict[str, float]] = {}
    concepts: dict[str, list[tuple[str, float]]] = {}

    for path, tokens in doc_tokens.items():
        if not tokens:
            tfidf_vectors[path] = {}
            concepts[path] = []
            continue

        tf = Counter(tokens)
        total = len(tokens)

        tfidf = {}
        for term, count in tf.items():
            tfidf[term] = (count / total) * idf.get(term, 0)

        tfidf_vectors[path] = tfidf

        # Top 10 concepts
        sorted_terms = sorted(tfidf.items(), key=lambda x: -x[1])[:10]
        concepts[path] = sorted_terms

    return tfidf_vectors, concepts


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    if not vec_a or not vec_b:
        return 0.0

    # Dot product
    common = set(vec_a.keys()) & set(vec_b.keys())
    dot = sum(vec_a[k] * vec_b[k] for k in common)

    # Norms
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)
