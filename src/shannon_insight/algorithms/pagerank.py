"""PageRank algorithm."""

from __future__ import annotations

import numpy as np
from scipy import sparse


def pagerank(
    A: sparse.csr_matrix,
    damping: float = 0.85,
    max_iterations: int = 50,
    tolerance: float = 1e-6,
) -> np.ndarray:
    """
    Compute PageRank scores.

    Args:
        A: Adjacency matrix (N x N)
        damping: Damping factor (default 0.85)
        max_iterations: Maximum iterations
        tolerance: Convergence threshold

    Returns:
        Array of PageRank scores (length N)
    """
    n = A.shape[0]
    if n == 0:
        return np.array([])

    # Out-degree
    out_degree = np.array(A.sum(axis=1)).flatten()
    dangling = out_degree == 0
    out_degree[dangling] = 1  # Avoid division by zero

    # Row-normalize
    D_inv = sparse.diags(1.0 / out_degree)
    M = D_inv @ A

    # Initialize
    pr: np.ndarray = np.asarray(np.ones(n) / n, dtype=float)

    for _ in range(max_iterations):
        # Dangling node contribution
        dangling_sum = pr[dangling].sum() / n

        # PageRank iteration
        pr_new: np.ndarray = np.asarray(
            (1 - damping) / n + damping * (M.T @ pr + dangling_sum), dtype=float
        )

        # Check convergence
        if np.max(np.abs(pr_new - pr)) < tolerance:
            break

        pr = pr_new

    return np.asarray(pr, dtype=float)
