"""Statistical metrics."""
from __future__ import annotations

import numpy as np


def gini(values: np.ndarray) -> float:
    """
    Compute Gini coefficient.

    Args:
        values: Array of non-negative values

    Returns:
        Gini coefficient in [0, 1]
    """
    if len(values) == 0:
        return 0.0

    values = np.sort(values)
    n = len(values)
    total = values.sum()

    if total == 0:
        return 0.0

    # G = (2 × Σ i × x_i) / (n × Σ x_i) - (n+1)/n
    weighted_sum = sum(i * v for i, v in enumerate(values, 1))
    gini_value = (2 * weighted_sum) / (n * total) - (n + 1) / n
    return max(0.0, min(1.0, gini_value))


def entropy(distribution: dict[str, float]) -> float:
    """
    Compute Shannon entropy.

    Args:
        distribution: {category: count/weight}

    Returns:
        Entropy in bits
    """
    total = sum(distribution.values())
    if total == 0:
        return 0.0

    H = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            H -= p * np.log2(p)

    return H
