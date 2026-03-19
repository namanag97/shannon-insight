"""Clone-coupling analysis — clones that also co-change.

Files that are clones AND co-change frequently represent high-risk
duplication: changes in one must be mirrored in the other.

Files that are clones but DON'T co-change may represent harmless
code reuse or diverged copies.
"""

from __future__ import annotations

from ..tensor.core import CLONE, COCHANGE, RelationTensor


def find_active_clones(
    tensor: RelationTensor,
    t: int = -1,
    min_clone_similarity: float = 0.7,
    min_cochange_lift: float = 1.0,
) -> list[tuple[int, int, float, float]]:
    """Find clone pairs that also co-change (high-risk duplication).

    Args:
        tensor: RelationTensor with CLONE and COCHANGE layers.
        t: Time window (-1 for latest).
        min_clone_similarity: Minimum clone similarity (1 - NCD).
        min_cochange_lift: Minimum co-change lift.

    Returns:
        List of (src, dst, clone_sim, cochange_lift) tuples.
    """
    if t == -1:
        t = tensor.n_windows - 1

    A_clone = tensor.slice(t, CLONE)
    A_cochange = tensor.slice(t, COCHANGE)

    active = []

    cx = A_clone.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if i >= j:  # skip duplicates (symmetric)
            continue
        if v >= min_clone_similarity:
            cochange = A_cochange[i, j]
            if cochange >= min_cochange_lift:
                active.append((int(i), int(j), float(v), float(cochange)))

    return active


def find_diverged_clones(
    tensor: RelationTensor,
    t: int = -1,
    min_clone_similarity: float = 0.7,
) -> list[tuple[int, int, float]]:
    """Find clone pairs that never co-change (potentially harmless).

    These are files that look similar but evolve independently,
    suggesting either intentional duplication or copies that have
    started to diverge.

    Args:
        tensor: RelationTensor with CLONE and COCHANGE layers.
        t: Time window (-1 for latest).
        min_clone_similarity: Minimum clone similarity.

    Returns:
        List of (src, dst, clone_sim) tuples.
    """
    if t == -1:
        t = tensor.n_windows - 1

    A_clone = tensor.slice(t, CLONE)
    A_cochange = tensor.slice(t, COCHANGE)

    diverged = []

    cx = A_clone.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if i >= j:
            continue
        if v >= min_clone_similarity and A_cochange[i, j] == 0:
            diverged.append((int(i), int(j), float(v)))

    return diverged
