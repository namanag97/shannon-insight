"""Naming drift detection.

Measures how well the filename reflects the file content.
naming_drift = 1 - cosine(filename_tokens, content_concept_tokens)

Range [0, 1]:
- 0.0 = filename perfectly matches content (or generic filename)
- 1.0 = filename completely unrelated to content
"""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

from .concepts import split_identifier
from .models import GENERIC_FILENAMES, Concept

if TYPE_CHECKING:
    pass


def compute_naming_drift(
    path: str,
    concepts: list[Concept],
    tier: int,
) -> float:
    """Compute naming drift between filename and content.

    Args:
        path: File path
        concepts: Extracted concepts from content
        tier: Concept extraction tier (1, 2, or 3)

    Returns:
        Naming drift [0, 1]. Returns 0.0 for:
        - Generic filenames (utils.py, helpers.py, etc.)
        - Files below Tier 3 (not enough data)
    """
    # Get filename without extension
    filename = Path(path).stem.lower()

    # Generic filenames don't drift
    if filename in GENERIC_FILENAMES:
        return 0.0

    # Tier 1 and 2 don't have enough data for meaningful comparison
    if tier < 3:
        return 0.0

    # Extract tokens from filename
    filename_tokens = split_identifier(filename)
    if not filename_tokens:
        return 0.0

    # Get content tokens from concepts
    content_tokens: list[str] = []
    for concept in concepts:
        content_tokens.extend(concept.keywords)

    if not content_tokens:
        return 0.0

    # Compute cosine similarity
    similarity = cosine_similarity(filename_tokens, content_tokens)

    # Drift is inverse of similarity
    return 1.0 - similarity


def cosine_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    """Compute cosine similarity between two token lists.

    Args:
        tokens_a: First list of tokens
        tokens_b: Second list of tokens

    Returns:
        Cosine similarity [0, 1]
    """
    if not tokens_a or not tokens_b:
        return 0.0

    # Build term frequency vectors
    counter_a = Counter(t.lower() for t in tokens_a)
    counter_b = Counter(t.lower() for t in tokens_b)

    # Get all unique terms
    all_terms = set(counter_a.keys()) | set(counter_b.keys())

    # Compute dot product and magnitudes
    dot_product = 0.0
    mag_a = 0.0
    mag_b = 0.0

    for term in all_terms:
        a_val = counter_a.get(term, 0)
        b_val = counter_b.get(term, 0)
        dot_product += a_val * b_val
        mag_a += a_val * a_val
        mag_b += b_val * b_val

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (math.sqrt(mag_a) * math.sqrt(mag_b))
