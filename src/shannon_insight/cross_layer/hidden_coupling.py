"""Hidden coupling detection."""
from __future__ import annotations

from ..tensor.core import RelationTensor, IMPORT, COCHANGE


def find_hidden_coupling(
    tensor: RelationTensor,
    t: int = -1,
    threshold: float = 1.5,
) -> list[tuple[int, int, float]]:
    """
    Find file pairs that co-change but don't import.

    Returns:
        List of (src, dst, lift) tuples
    """
    if t == -1:
        t = tensor.n_windows - 1

    A_import = tensor.slice(t, IMPORT)
    A_cochange = tensor.slice(t, COCHANGE)

    hidden = []

    # Find edges in cochange but not import
    cx = A_cochange.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if v >= threshold and A_import[i, j] == 0:
            hidden.append((int(i), int(j), float(v)))

    return hidden


def hidden_coupling_count(
    tensor: RelationTensor,
    t: int = -1,
) -> dict[int, int]:
    """Count hidden coupling edges per node."""
    hidden = find_hidden_coupling(tensor, t)

    counts: dict[int, int] = {}
    for i, j, _ in hidden:
        counts[i] = counts.get(i, 0) + 1
        counts[j] = counts.get(j, 0) + 1

    return counts
