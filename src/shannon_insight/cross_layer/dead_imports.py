"""Dead import detection — imports without co-change evidence.

Finds import edges that have no corresponding co-change activity,
suggesting the dependency may be unused or vestigial.
"""

from __future__ import annotations

from ..tensor.core import COCHANGE, IMPORT, RelationTensor


def find_dead_imports(
    tensor: RelationTensor,
    t: int = -1,
    min_import_weight: float = 0.5,
) -> list[tuple[int, int]]:
    """Find imports with no co-change evidence.

    An import edge (i→j) is "dead" if files i and j never change together,
    suggesting the dependency exists in code but has no behavioral evidence.

    Args:
        tensor: RelationTensor with IMPORT and COCHANGE layers.
        t: Time window (-1 for latest).
        min_import_weight: Minimum import weight to consider.

    Returns:
        List of (src_idx, dst_idx) edges.
    """
    if t == -1:
        t = tensor.n_windows - 1

    A_import = tensor.slice(t, IMPORT)
    A_cochange = tensor.slice(t, COCHANGE)

    dead = []

    cx = A_import.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if v >= min_import_weight and A_cochange[i, j] == 0:
            dead.append((int(i), int(j)))

    return dead


def dead_import_count(
    tensor: RelationTensor,
    t: int = -1,
) -> dict[int, int]:
    """Count dead import edges per node."""
    dead = find_dead_imports(tensor, t)

    counts: dict[int, int] = {}
    for i, j in dead:
        counts[i] = counts.get(i, 0) + 1

    return counts
