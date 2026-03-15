"""Populate AUTHOR layer (R=2) from git history using Jaccard similarity.

For every pair of files that share at least one author, the Jaccard index
|A inter B| / |A union B| is computed over each file's author set.
Only edges with Jaccard >= *min_jaccard* are stored.  The relation is
symmetric, so both (a,b) and (b,a) are added.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any

from ..tensor.core import AUTHOR


def populate_authors(
    tensor: Any,
    git_history: Any,
    min_jaccard: float = 0.1,
) -> None:
    """Fill T[:,:,t,AUTHOR] with Jaccard similarity of author sets.

    Args:
        tensor: A ``RelationTensor`` instance.
        git_history: Object with a ``.commits`` list.  Each commit has
            ``.files`` (iterable of paths) and ``.author`` (str).
        min_jaccard: Minimum Jaccard similarity to emit an edge.
    """
    # Build author sets per file
    authors_per_file: dict[str, set[str]] = defaultdict(set)

    for commit in git_history.commits:
        for f in commit.files:
            authors_per_file[f].add(commit.author)

    # Pairwise Jaccard
    files = list(authors_per_file.keys())
    t = tensor.n_windows - 1

    for a, b in combinations(files, 2):
        authors_a = authors_per_file[a]
        authors_b = authors_per_file[b]

        intersection = len(authors_a & authors_b)
        if intersection == 0:
            continue

        union = len(authors_a | authors_b)
        jaccard = intersection / union

        if jaccard >= min_jaccard:
            tensor.add_edge(a, b, t, AUTHOR, weight=jaccard)
            tensor.add_edge(b, a, t, AUTHOR, weight=jaccard)  # symmetric
