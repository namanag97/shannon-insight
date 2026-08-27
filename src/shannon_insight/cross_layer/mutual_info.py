"""Mutual information between graph layers."""

from __future__ import annotations

from typing import cast

import numpy as np
from scipy import sparse


def edge_mutual_info(
    A1: sparse.csr_matrix,
    A2: sparse.csr_matrix,
    bins: int = 10,
) -> float:
    """
    Compute mutual information between two graphs based on edge co-occurrence.

    Args:
        A1, A2: Adjacency matrices (same shape)
        bins: Number of bins for discretization

    Returns:
        Mutual information in bits
    """
    n = A1.shape[0]
    if n < 2:
        return 0.0

    # Flatten to edge vectors
    v1 = A1.toarray().flatten()
    v2 = A2.toarray().flatten()

    # Discretize
    def discretize(v: np.ndarray) -> np.ndarray:
        if v.max() == v.min():
            return np.zeros_like(v, dtype=int)
        return cast(np.ndarray, np.digitize(v, np.linspace(v.min(), v.max(), bins)))

    d1 = discretize(v1)
    d2 = discretize(v2)

    # Joint histogram
    joint = np.zeros((bins + 1, bins + 1))
    for i in range(len(d1)):
        joint[d1[i], d2[i]] += 1
    joint /= joint.sum()

    # Marginals
    p1 = joint.sum(axis=1)
    p2 = joint.sum(axis=0)

    # MI
    mi = 0.0
    for i in range(bins + 1):
        for j in range(bins + 1):
            if joint[i, j] > 0 and p1[i] > 0 and p2[j] > 0:
                mi += joint[i, j] * np.log2(joint[i, j] / (p1[i] * p2[j]))

    return float(mi)
