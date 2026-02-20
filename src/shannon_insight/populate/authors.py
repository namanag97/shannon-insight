"""Populate AUTHOR layer (R=2)."""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from ..tensor.core import RelationTensor, AUTHOR
from ..extract.models import GitHistory


def populate_authors(
    tensor: RelationTensor,
    git_history: GitHistory,
    min_jaccard: float = 0.1,
):
    """Fill T[:,:,t,AUTHOR] with Jaccard similarity."""
    # Build author sets per file
    authors_per_file: dict[str, set[str]] = defaultdict(set)

    for commit in git_history.commits:
        for f in commit.files:
            authors_per_file[f].add(commit.author)

    # Compute pairwise Jaccard
    files = list(authors_per_file.keys())
    t = tensor.n_windows - 1

    for a, b in combinations(files, 2):
        authors_a = authors_per_file[a]
        authors_b = authors_per_file[b]

        intersection = len(authors_a & authors_b)
        union = len(authors_a | authors_b)

        if union == 0:
            continue

        jaccard = intersection / union

        if jaccard >= min_jaccard:
            tensor.add_edge(a, b, t, AUTHOR, weight=jaccard)
            tensor.add_edge(b, a, t, AUTHOR, weight=jaccard)
