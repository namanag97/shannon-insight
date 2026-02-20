"""Temporal cross-layer analysis — velocity and trend signals."""
from __future__ import annotations

import numpy as np
from scipy import sparse

from ..tensor.core import RelationTensor


def churn_velocity(
    tensor: RelationTensor,
    r: int,
) -> dict[int, float]:
    """
    Compute per-node edge-weight velocity (slope of sum over time windows).

    Returns:
        {node_idx: slope}  — positive = growing coupling, negative = shrinking
    """
    n = tensor.n_nodes
    k = tensor.n_windows

    if k < 2 or n == 0:
        return {i: 0.0 for i in range(n)}

    # Build time series of row sums per node
    series = np.zeros((n, k), dtype=np.float32)
    for t in range(k):
        A = tensor.slice(t, r)
        series[:, t] = np.array(A.sum(axis=1)).flatten()

    # Fit linear slope per node
    xs = np.arange(k, dtype=float)
    velocities: dict[int, float] = {}
    for i in range(n):
        if series[i].sum() == 0:
            velocities[i] = 0.0
        else:
            slope = float(np.polyfit(xs, series[i], 1)[0])
            velocities[i] = slope

    return velocities


def coupling_trend(
    tensor: RelationTensor,
    r: int,
) -> tuple[float, float]:
    """
    Overall coupling trend for a relation layer.

    Returns:
        (mean_slope, std_slope) across all nodes
    """
    velocities = churn_velocity(tensor, r)
    slopes = np.array(list(velocities.values()), dtype=float)
    if len(slopes) == 0:
        return 0.0, 0.0
    return float(slopes.mean()), float(slopes.std())
