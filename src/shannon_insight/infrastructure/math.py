"""Core mathematical functions for Shannon Insight v2.

Provides verified implementations of information-theoretic and statistical
formulas used throughout the signal pipeline.
"""

from __future__ import annotations

import math as _math


def compute_gini(values: list[float]) -> float:
    """Compute the Gini coefficient of inequality.

    G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n

    where x_i sorted ascending, i is 1-indexed.

    Returns:
        0.0 for perfect equality, approaches 1.0 for maximum inequality.
    """
    if not values or sum(values) == 0:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)
    total = sum(sorted_values)

    # i is 1-indexed: enumerate gives 0-based, so use (i + 1)
    weighted_sum = sum((i + 1) * v for i, v in enumerate(sorted_values))

    return (2 * weighted_sum) / (n * total) - (n + 1) / n


def compute_entropy(counts: dict[str, int]) -> float:
    """Compute Shannon entropy in bits.

    H = -sum(p(x) * log2(p(x)))

    Returns:
        0.0 for single value (certainty), log2(n) for uniform distribution.
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * _math.log2(p)

    return entropy


def compute_bus_factor(author_commits: dict[str, int]) -> float:
    """Compute bus factor from author commit distribution.

    bus_factor = 2^H where H = author entropy.

    Returns:
        1.0 for single author, k for k equal authors.
    """
    h = compute_entropy(author_commits)
    return 2**h


def compute_percentile(value: float, all_values: list[float]) -> float:
    """Compute the percentile rank of a value within a distribution.

    pctl(signal, f) = |{v : signal(v) <= signal(f)}| / |all_files|

    Uses <= (not <) for consistent ordering.

    Returns:
        Fraction in [0, 1]. Returns 0.0 for empty input.
    """
    if not all_values:
        return 0.0
    count_le = sum(1 for v in all_values if v <= value)
    return count_le / len(all_values)
