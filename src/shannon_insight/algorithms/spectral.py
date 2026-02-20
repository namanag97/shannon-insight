"""Spectral graph analysis."""
from __future__ import annotations

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh


def spectral_analysis(
    A: sparse.csr_matrix,
    k: int = 10,
) -> tuple[float, float, np.ndarray]:
    """
    Compute spectral properties of graph.

    Args:
        A: Adjacency matrix
        k: Number of eigenvalues to compute

    Returns:
        - fiedler_value: Second smallest eigenvalue (algebraic connectivity)
        - spectral_gap: λ₃ - λ₂
        - eigenvalues: First k eigenvalues
    """
    n = A.shape[0]
    if n < 3:
        return 0.0, 0.0, np.array([])

    # Compute Laplacian
    D = sparse.diags(np.array(A.sum(axis=1)).flatten())
    L = D - A

    # Compute smallest eigenvalues
    k = min(k, n - 1)
    try:
        eigenvalues, _ = eigsh(L, k=k, which='SM')
        eigenvalues = np.sort(eigenvalues)
    except Exception:
        return 0.0, 0.0, np.array([])

    # Fiedler value (λ₂)
    fiedler = eigenvalues[1] if len(eigenvalues) > 1 else 0.0

    # Spectral gap (λ₃ - λ₂)
    gap = (eigenvalues[2] - eigenvalues[1]) if len(eigenvalues) > 2 else 0.0

    return fiedler, gap, eigenvalues
