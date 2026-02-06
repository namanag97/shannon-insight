"""Descriptive and inferential statistics: z-scores, Mahalanobis, Grubbs' test."""

import math
import statistics as stdlib_stats
from typing import List, Optional, Tuple

import numpy as np


class Statistics:
    """Statistical analysis methods."""

    @staticmethod
    def mean(values: List[float]) -> float:
        """Compute arithmetic mean."""
        if not values:
            return 0.0
        return stdlib_stats.mean(values)

    @staticmethod
    def stdev(values: List[float]) -> float:
        """Compute sample standard deviation."""
        if len(values) < 2:
            return 0.0
        return stdlib_stats.stdev(values)

    @staticmethod
    def z_scores(values: List[float]) -> List[float]:
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
    def grubbs_test(values: List[float], alpha: float = 0.05) -> Optional[Tuple[int, float]]:
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
        from scipy import stats as sp_stats  # type: ignore[import-untyped]

        return float(sp_stats.t.ppf(1 - alpha, df))

    @staticmethod
    def confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float]:
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
