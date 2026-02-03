"""
Anomaly detection using rigorous statistical methods.

Implements:
- Mahalanobis distance for multivariate outliers
- Robust Z-scores (MAD-based)
- Grubbs' test for single outliers
- Statistical significance testing
"""

from typing import Dict, List, Tuple
import numpy as np

from ..models import Primitives
from ..logging_config import get_logger
from ..exceptions import InvalidConfigError, InsufficientDataError
from ..math import Statistics, RobustStatistics

logger = get_logger(__name__)


class AnomalyDetector:
    """
    Detect anomalies using statistically rigorous methods.
    """

    MIN_FILES_FOR_MAHALANOBIS = 10
    MIN_FILES_FOR_Z_SCORE = 5

    def __init__(
        self,
        primitives: Dict[str, Primitives],
        threshold: float = 1.5,
        use_multivariate: bool = True,
    ):
        """
        Initialize anomaly detector.

        Args:
            primitives: Dictionary mapping file paths to primitives
            threshold: Detection threshold (default 1.5 for z-scores)
            use_multivariate: Use Mahalanobis distance for multivariate detection

        Raises:
            InvalidConfigError: If threshold is invalid
            InsufficientDataError: If too few files for analysis
        """
        if threshold <= 0 or threshold >= 10:
            raise InvalidConfigError(
                "threshold", threshold, "Threshold must be between 0.0 and 10.0"
            )

        if len(primitives) < 3:
            raise InsufficientDataError(
                "Too few files for reliable analysis", minimum_required=3
            )

        self.primitives = primitives
        self.threshold = threshold
        self.use_multivariate = use_multivariate and len(primitives) >= self.MIN_FILES_FOR_MAHALANOBIS

        logger.debug(
            f"Initialized AnomalyDetector with threshold={threshold}, "
            f"multivariate={self.use_multivariate}, files={len(primitives)}"
        )

    def normalize(self) -> Dict[str, Primitives]:
        """
        Normalize all primitives using robust statistical methods.

        For small samples (<10): Uses modified Z-scores (MAD-based)
        For larger samples: Uses standard Z-scores

        Returns:
            Dictionary mapping file paths to normalized primitives
        """
        normalized = {}

        if self.use_multivariate:
            return self._normalize_multivariate(normalized)

        # Extract each primitive into separate lists
        entropy_vals = [p.structural_entropy for p in self.primitives.values()]
        centrality_vals = [p.network_centrality for p in self.primitives.values()]
        volatility_vals = [p.churn_volatility for p in self.primitives.values()]
        coherence_vals = [p.semantic_coherence for p in self.primitives.values()]
        load_vals = [p.cognitive_load for p in self.primitives.values()]

        # Use robust z-scores for small samples
        if len(self.primitives) < self.MIN_FILES_FOR_Z_SCORE:
            entropy_z = RobustStatistics.modified_z_score(entropy_vals)
            centrality_z = RobustStatistics.modified_z_score(centrality_vals)
            volatility_z = RobustStatistics.modified_z_score(volatility_vals)
            coherence_z = RobustStatistics.modified_z_score(coherence_vals)
            load_z = RobustStatistics.modified_z_score(load_vals)
        else:
            # Use standard z-scores for larger samples
            entropy_z = Statistics.z_scores(entropy_vals)
            centrality_z = Statistics.z_scores(centrality_vals)
            volatility_z = Statistics.z_scores(volatility_vals)
            coherence_z = Statistics.z_scores(coherence_vals)
            load_z = Statistics.z_scores(load_vals)

        # Build normalized primitives
        paths = list(self.primitives.keys())
        for i, path in enumerate(paths):
            normalized[path] = Primitives(
                structural_entropy=entropy_z[i],
                network_centrality=centrality_z[i],
                churn_volatility=volatility_z[i],
                semantic_coherence=coherence_z[i],
                cognitive_load=load_z[i],
            )

        return normalized

    def _normalize_multivariate(
        self, normalized: Dict[str, Primitives]
    ) -> Dict[str, Primitives]:
        """
        Normalize using Mahalanobis distance for multivariate analysis.

        Considers correlations between primitives, not just individual values.
        """
        # Build feature matrix
        paths = list(self.primitives.keys())
        n = len(paths)

        features = np.array(
            [
                [
                    self.primitives[path].structural_entropy,
                    self.primitives[path].network_centrality,
                    self.primitives[path].churn_volatility,
                    self.primitives[path].semantic_coherence,
                    self.primitives[path].cognitive_load,
                ]
                for path in paths
            ]
        )

        # Compute mean and covariance
        mean_vec = np.mean(features, axis=0)
        cov_matrix = np.cov(features, rowvar=False)

        # Compute Mahalanobis distance for each file
        mahalanobis_distances = []
        for i in range(n):
            dist = Statistics.mahalanobis_distance(features[i], mean_vec, cov_matrix)
            mahalanobis_distances.append(dist)

        # Convert distances to z-like scores
        # MD² follows chi-squared distribution with k degrees of freedom
        k = 5  # number of dimensions
        from scipy import stats

        # Convert MD² to p-values
        p_values = [
            1 - stats.chi2.cdf(dist, k) for dist in mahalanobis_distances
        ]

        # Convert to z-scores via inverse CDF.
        # p ≈ 0 means maximally significant (large z), p ≈ 1 means no anomaly.
        z_scores = []
        for p in p_values:
            if p <= 0:
                z_scores.append(10.0)  # practical cap for extreme significance
            elif p >= 1:
                z_scores.append(0.0)
            else:
                z_scores.append(stats.norm.ppf(1 - p))

        # Normalize each primitive separately for reporting
        entropy_vals = features[:, 0]
        centrality_vals = features[:, 1]
        volatility_vals = features[:, 2]
        coherence_vals = features[:, 3]
        load_vals = features[:, 4]

        entropy_z = Statistics.z_scores(entropy_vals.tolist())
        centrality_z = Statistics.z_scores(centrality_vals.tolist())
        volatility_z = Statistics.z_scores(volatility_vals.tolist())
        coherence_z = Statistics.z_scores(coherence_vals.tolist())
        load_z = Statistics.z_scores(load_vals.tolist())

        # Build normalized primitives
        for i, path in enumerate(paths):
            normalized[path] = Primitives(
                structural_entropy=entropy_z[i],
                network_centrality=centrality_z[i],
                churn_volatility=volatility_z[i],
                semantic_coherence=coherence_z[i],
                cognitive_load=load_z[i],
            )

        # Store Mahalanobis scores for later use
        self.mahalanobis_scores = {paths[i]: z_scores[i] for i in range(n)}

        return normalized

    def detect_anomalies(
        self, normalized: Dict[str, Primitives]
    ) -> Dict[str, List[str]]:
        """
        Detect which primitives are anomalous.

        For multivariate mode: Uses Mahalanobis distance
        For univariate mode: Uses individual z-scores

        Returns:
            Dictionary mapping file paths to list of anomaly flags
        """
        anomalies = {}

        if self.use_multivariate and hasattr(self, "mahalanobis_scores"):
            return self._detect_multivariate_anomalies(normalized)

        # Univariate detection
        for path, prims in normalized.items():
            flags = []

            if abs(prims.structural_entropy) > self.threshold:
                direction = "high" if prims.structural_entropy > 0 else "low"
                flags.append(f"structural_entropy_{direction}")

            if prims.network_centrality > self.threshold:
                flags.append("high_centrality")

            if abs(prims.churn_volatility) > self.threshold:
                flags.append("high_volatility")

            if abs(prims.semantic_coherence) > self.threshold:
                direction = "low" if prims.semantic_coherence < 0 else "high"
                flags.append(f"semantic_coherence_{direction}")

            if prims.cognitive_load > self.threshold:
                flags.append("high_cognitive_load")

            if flags:
                anomalies[path] = flags

        return anomalies

    def _detect_multivariate_anomalies(
        self, normalized: Dict[str, Primitives]
    ) -> Dict[str, List[str]]:
        """
        Detect anomalies using Mahalanobis distance.

        Also identifies which specific primitives contribute to the anomaly.
        """
        anomalies = {}

        # Use chi-squared critical value for significance
        k = 5  # number of dimensions
        from scipy import stats

        critical_value = stats.chi2.ppf(0.95, k)  # 95% confidence

        for path, mahalanobis_z in self.mahalanobis_scores.items():
            if abs(mahalanobis_z) > self.threshold:
                prims = normalized[path]
                flags = []

                # Identify which primitives are most anomalous.
                # TODO: The 0.5 multiplier on threshold is a heuristic that
                # relaxes per-primitive thresholds in multivariate mode.
                # A rigorous alternative: decompose Mahalanobis D² into
                # per-variable contributions via (x_i - mu_i)^2 * [Sigma^-1]_ii
                # and compare each to its marginal chi-squared critical value.
                if abs(prims.structural_entropy) > self.threshold * 0.5:
                    direction = "high" if prims.structural_entropy > 0 else "low"
                    flags.append(f"structural_entropy_{direction}")

                if prims.network_centrality > self.threshold * 0.5:
                    flags.append("high_centrality")

                if abs(prims.churn_volatility) > self.threshold * 0.5:
                    flags.append("high_volatility")

                if abs(prims.semantic_coherence) > self.threshold * 0.5:
                    direction = "low" if prims.semantic_coherence < 0 else "high"
                    flags.append(f"semantic_coherence_{direction}")

                if prims.cognitive_load > self.threshold * 0.5:
                    flags.append("high_cognitive_load")

                if flags:
                    anomalies[path] = flags

        return anomalies

    def detect_outliers(
        self, values: List[float], method: str = "grubbs"
    ) -> List[int]:
        """
        Detect outliers in a univariate dataset.

        Args:
            values: List of values
            method: Detection method ('grubbs', 'iqr', 'mad')

        Returns:
            List of outlier indices
        """
        if method == "grubbs":
            result = Statistics.grubbs_test(values)
            if result:
                return [result[0]]
            return []
        elif method == "iqr":
            outliers = RobustStatistics.iqr_outliers(values)
            return [i for i, is_outlier in enumerate(outliers) if is_outlier]
        elif method == "mad":
            modified_z = RobustStatistics.modified_z_score(values)
            return [i for i, z in enumerate(modified_z) if abs(z) > 3.5]
        else:
            raise ValueError(f"Unknown method: {method}")
