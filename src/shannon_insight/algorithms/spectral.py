"""Spectral graph analysis."""

from __future__ import annotations

import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh


def spectral_analysis(
    A: sparse.csr_matrix,
    k: int = 10,
) -> tuple[float, float, np.ndarray, float]:
    """
    Compute spectral properties of graph.

    For disconnected graphs, analysis is performed on the largest connected
    component so that the Fiedler value reflects meaningful algebraic
    connectivity instead of being trivially 0.0.

    Args:
        A: Adjacency matrix
        k: Number of eigenvalues to compute

    Returns:
        - fiedler_value: Second smallest eigenvalue (algebraic connectivity)
        - spectral_gap: λ₃ - λ₂
        - eigenvalues: First k eigenvalues
        - component_ratio: Fraction of nodes in the analysed component
          (1.0 when the graph is connected)
    """
    n = A.shape[0]
    if n < 3:
        return 0.0, 0.0, np.array([]), 0.0

    # --- Largest connected component extraction --------------------------
    n_components, labels = connected_components(A, directed=False, connection="weak")

    if n_components > 1:
        # Find largest component
        component_sizes = np.bincount(labels)
        largest = np.argmax(component_sizes)
        mask = labels == largest
        indices = np.where(mask)[0]

        # Extract submatrix for largest component
        A_component = A[np.ix_(indices, indices)]
    else:
        A_component = A
        indices = np.arange(n)

    component_ratio = len(indices) / n

    # Check that the component itself is large enough
    n_comp = A_component.shape[0]
    if n_comp < 3:
        return 0.0, 0.0, np.array([]), component_ratio

    # --- Compute Laplacian on the component ------------------------------
    D = sparse.diags(np.array(A_component.sum(axis=1)).flatten())
    L = D - A_component

    # Compute smallest eigenvalues
    k_eff = min(k, n_comp - 1)
    try:
        eigenvalues, _ = eigsh(L, k=k_eff, which="SM")
        eigenvalues = np.sort(eigenvalues)
    except Exception:
        return 0.0, 0.0, np.array([]), component_ratio

    # Fiedler value (λ₂)
    fiedler = eigenvalues[1] if len(eigenvalues) > 1 else 0.0

    # Spectral gap (λ₃ - λ₂)
    gap = (eigenvalues[2] - eigenvalues[1]) if len(eigenvalues) > 2 else 0.0

    return fiedler, gap, eigenvalues, component_ratio
