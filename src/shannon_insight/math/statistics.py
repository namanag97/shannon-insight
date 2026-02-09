"""Descriptive and inferential statistics: z-scores, Mahalanobis, Grubbs' test."""

import math
import statistics as stdlib_stats
from typing import Optional

import numpy as np


class Statistics:
    """Statistical analysis methods."""

    @staticmethod
    def mean(values: list[float]) -> float:
        """Compute arithmetic mean."""
        if not values:
            return 0.0
        return stdlib_stats.mean(values)

    @staticmethod
    def stdev(values: list[float]) -> float:
        """Compute sample standard deviation."""
        if len(values) < 2:
            return 0.0
        return stdlib_stats.stdev(values)

    @staticmethod
    def z_scores(values: list[float]) -> list[float]:
        """
        Compute z-scores: z = (x - mu) / sigma.

        Args:
            values: List of values

        Returns:
            List of z-scores
        """
        if not values or len(values) < 2:
            return [0.0] * len(values)

        mean_val = Statistics.mean(values)
        stdev_val = Statistics.stdev(values)

        if stdev_val == 0:
            return [0.0] * len(values)

        return [(x - mean_val) / stdev_val for x in values]

    @staticmethod
    def z_score(x: float, mean: float, std: float) -> float:
        """Compute single z-score: z = (x - mu) / sigma."""
        if std == 0:
            return 0.0
        return (x - mean) / std

    @staticmethod
    def mahalanobis_distance(point: np.ndarray, mean: np.ndarray, cov_matrix: np.ndarray) -> float:
        """
        Compute Mahalanobis distance: D^2 = (x - mu)^T Sigma^-1 (x - mu).

        Args:
            point: Observation vector
            mean: Mean vector
            cov_matrix: Covariance matrix

        Returns:
            Mahalanobis distance (squared)
        """
        diff = point - mean

        try:
            inv_cov = np.linalg.inv(cov_matrix)
        except np.linalg.LinAlgError:
            inv_cov = np.linalg.pinv(cov_matrix)

        distance = diff.T @ inv_cov @ diff
        return float(distance)

    @staticmethod
    def grubbs_test(values: list[float], alpha: float = 0.05) -> Optional[tuple[int, float]]:
        """
        Grubbs' test for detecting a single outlier.

        G = (max|x_i - x_bar|) / s

        Args:
            values: List of values
            alpha: Significance level (default 0.05)

        Returns:
            Tuple of (outlier_index, G_statistic) if outlier found, None otherwise
        """
        n = len(values)
        if n < 3:
            return None

        mean_val = float(np.mean(values))
        std_val = float(np.std(values, ddof=1))

        if std_val == 0:
            return None

        deviations = [abs(x - mean_val) for x in values]
        max_deviation = max(deviations)
        outlier_index = deviations.index(max_deviation)

        G = max_deviation / std_val

        t_critical = Statistics._t_critical_value(alpha / (2 * n), n - 2)
        G_critical = ((n - 1) / math.sqrt(n)) * math.sqrt(t_critical**2 / (n - 2 + t_critical**2))

        if G > G_critical:
            return outlier_index, float(G)

        return None

    @staticmethod
    def _t_critical_value(alpha: float, df: int) -> float:
        """Inverse t-distribution critical value."""
        from scipy import stats as sp_stats

        return float(sp_stats.t.ppf(1 - alpha, df))

    @staticmethod
    def mutual_information(
        joint_changed: int,
        only_a: int,
        only_b: int,
        neither: int,
    ) -> float:
        """Compute mutual information between two binary variables (changed/not).

        MI(A,B) = sum P(a,b) * log2(P(a,b) / (P(a)*P(b)))
        where a,b in {changed, not_changed}.

        Args:
            joint_changed: Commits where both A and B changed
            only_a: Commits where only A changed
            only_b: Commits where only B changed
            neither: Commits where neither changed

        Returns:
            Mutual information in bits. 0.0 if no information.
        """
        total = joint_changed + only_a + only_b + neither
        if total == 0:
            return 0.0

        # Joint distribution: P(a,b) for a,b in {changed, not_changed}
        cells = [
            (joint_changed, joint_changed + only_a, joint_changed + only_b),  # both changed
            (only_a, joint_changed + only_a, only_b + neither),  # A changed, B not
            (only_b, only_a + neither, joint_changed + only_b),  # B changed, A not
            (neither, only_a + neither, only_b + neither),  # neither changed
        ]

        mi = 0.0
        for joint, marginal_a, marginal_b in cells:
            p_ab = joint / total
            p_a = marginal_a / total
            p_b = marginal_b / total
            if p_ab > 0 and p_a > 0 and p_b > 0:
                mi += p_ab * math.log2(p_ab / (p_a * p_b))

        return max(0.0, mi)  # Clamp to 0 (floating-point can go slightly negative)

    @staticmethod
    def mad_z_score(values: list[float]) -> list[float]:
        """Compute MAD-based robust z-scores.

        z_MAD = 0.6745 * (x - median) / MAD

        MAD = median(|x_i - median|)
        The 0.6745 factor makes MAD consistent with std for normal distributions.

        Args:
            values: List of values

        Returns:
            List of robust z-scores
        """
        if not values or len(values) < 2:
            return [0.0] * len(values)

        med = float(stdlib_stats.median(values))
        abs_devs = [abs(x - med) for x in values]
        mad = float(stdlib_stats.median(abs_devs))

        if mad == 0:
            return [0.0] * len(values)

        return [0.6745 * (x - med) / mad for x in values]

    @staticmethod
    def otsu_threshold(values: list[float]) -> float:
        """Otsu's method: find threshold minimizing within-class variance.

        Finds the natural breakpoint in a distribution by exhaustive search
        over candidate thresholds. If the distribution is bimodal, the
        threshold falls in the valley.

        Args:
            values: List of values (at least 2)

        Returns:
            Optimal threshold value, or median if insufficient data.
        """
        if len(values) < 4:
            return float(stdlib_stats.median(values)) if values else 0.0

        sorted_vals = sorted(values)
        n = len(sorted_vals)
        best_threshold = sorted_vals[n // 2]
        best_variance = float("inf")

        # Test each unique midpoint between consecutive sorted values
        for i in range(1, n):
            if sorted_vals[i] == sorted_vals[i - 1]:
                continue

            threshold = (sorted_vals[i - 1] + sorted_vals[i]) / 2
            class0 = sorted_vals[:i]
            class1 = sorted_vals[i:]

            w0 = len(class0) / n
            w1 = len(class1) / n

            if w0 == 0 or w1 == 0:
                continue

            var0 = stdlib_stats.variance(class0) if len(class0) > 1 else 0.0
            var1 = stdlib_stats.variance(class1) if len(class1) > 1 else 0.0

            within_var = w0 * var0 + w1 * var1

            if within_var < best_variance:
                best_variance = within_var
                best_threshold = threshold

        return best_threshold

    @staticmethod
    def confidence_interval(values: list[float], confidence: float = 0.95) -> tuple[float, float]:
        """
        Confidence interval for the mean.

        CI = x_bar +/- t_(alpha/2, n-1) * s / sqrt(n)

        Args:
            values: Sample values
            confidence: Confidence level (default 0.95)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        n = len(values)
        if n < 2:
            return (values[0], values[0]) if values else (0.0, 0.0)

        mean_val = float(np.mean(values))
        std_val = float(np.std(values, ddof=1))
        alpha = 1 - confidence

        from scipy import stats as sp_stats

        t_critical = sp_stats.t.ppf(1 - alpha / 2, n - 1)
        margin = t_critical * std_val / math.sqrt(n)

        return (mean_val - margin, mean_val + margin)
