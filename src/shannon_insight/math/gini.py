"""Gini coefficient for inequality measurement.

The Gini coefficient measures statistical dispersion. Applied to function
size distributions, it detects "God functions" (concentrated cognitive load).

    G = 0: perfect equality (all functions same size)
    G = 1: perfect inequality (one function has all the lines)

Reference: Gini (1912) - Variabilita e Mutabilita

Formula (for sorted values x_1 <= x_2 <= ... <= x_n):
    G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
"""

from typing import List, Union


class Gini:
    """Gini coefficient calculations for inequality measurement."""

    @staticmethod
    def gini_coefficient(
        values: Union[List[float], List[int]],
        bias_correction: bool = True,
    ) -> float:
        """Compute Gini coefficient.

        Args:
            values: List of non-negative values. Must not be empty.
            bias_correction: If True, apply n/(n-1) correction for sample data.

        Returns:
            Gini coefficient in [0, 1].

        Raises:
            ValueError: If values is empty or contains negative values.

        Calibration for Function Sizes:
            < 0.30: Generally balanced (healthy)
            0.30-0.50: Moderate inequality (some large functions)
            0.50-0.70: High inequality (likely God functions)
            >= 0.70: Severe inequality (needs refactoring)
        """
        if not values:
            raise ValueError("Cannot compute Gini for empty list")

        if len(values) == 1:
            return 0.0

        if any(v < 0 for v in values):
            raise ValueError("Gini requires non-negative values")

        total = sum(values)
        if total == 0:
            return 0.0

        sorted_vals = sorted(values)
        n = len(sorted_vals)

        # G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
        # where i is 1-indexed
        weighted_sum = sum((i + 1) * v for i, v in enumerate(sorted_vals))
        gini = (2.0 * weighted_sum) / (n * total) - (n + 1.0) / n

        # Bias correction for sample data
        if bias_correction and n > 1:
            gini *= n / (n - 1)

        return max(0.0, min(1.0, gini))
