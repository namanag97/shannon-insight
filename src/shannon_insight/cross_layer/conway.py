"""Conway's law analysis."""
from __future__ import annotations

from ..tensor.core import RelationTensor, IMPORT, AUTHOR


def find_conway_violations(
    tensor: RelationTensor,
    t: int = -1,
    min_import_weight: float = 0.5,
    max_author_overlap: float = 0.2,
) -> list[tuple[int, int]]:
    """
    Find imports across team boundaries.

    Returns:
        List of (src, dst) edges with low author overlap
    """
    if t == -1:
        t = tensor.n_windows - 1

    A_import = tensor.slice(t, IMPORT)
    A_author = tensor.slice(t, AUTHOR)

    violations = []

    cx = A_import.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if v >= min_import_weight:
            author_overlap = A_author[i, j]
            if author_overlap < max_author_overlap:
                violations.append((int(i), int(j)))

    return violations


def conway_alignment(tensor: RelationTensor, t: int = -1) -> float:
    """
    Compute overall Conway alignment score.

    Returns:
        Score in [0, 1] where 1 = perfect alignment
    """
    violations = find_conway_violations(tensor, t)
    resolved_t = t if t >= 0 else tensor.n_windows - 1
    A_import = tensor.slice(resolved_t, IMPORT)

    total_imports = A_import.nnz
    if total_imports == 0:
        return 1.0

    return 1 - len(violations) / total_imports
