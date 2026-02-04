"""
Anomaly detection using rigorous statistical methods — registry-driven.

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
from .registry import get_registry

logger = get_logger(__name__)


class AnomalyDetector:
    """Detect anomalies using statistically rigorous methods."""

    MIN_FILES_FOR_MAHALANOBIS = 10
    MIN_FILES_FOR_Z_SCORE = 5

    def __init__(
        self,
        primitives: Dict[str, Primitives],
        threshold: float = 1.5,
        use_multivariate: bool = True,
    ):
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
        self._registry = get_registry()
        self._prim_names = [d.name for d in self._registry]

        logger.debug(
            f"Initialized AnomalyDetector with threshold={threshold}, "
            f"multivariate={self.use_multivariate}, files={len(primitives)}"
        )

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _get_values(self, prim_name: str) -> List[float]:
        """Extract a list of values for a single primitive across all files."""
        return [self._prim_dict(p).get(prim_name, 0.0) for p in self.primitives.values()]

    @staticmethod
    def _prim_dict(p: Primitives) -> Dict[str, float]:
        return p.to_dict()

    # ------------------------------------------------------------------
    # normalize
    # ------------------------------------------------------------------

    def normalize(self) -> Dict[str, Primitives]:
        normalized: Dict[str, Primitives] = {}

        if self.use_multivariate:
            return self._normalize_multivariate(normalized)

        paths = list(self.primitives.keys())

        # Z-score each primitive independently
        z_by_name: Dict[str, List[float]] = {}
        for name in self._prim_names:
            vals = self._get_values(name)
            if len(self.primitives) < self.MIN_FILES_FOR_Z_SCORE:
                z_by_name[name] = RobustStatistics.modified_z_score(vals)
            else:
                z_by_name[name] = Statistics.z_scores(vals)

        for i, path in enumerate(paths):
            d = {name: z_by_name[name][i] for name in self._prim_names}
            normalized[path] = Primitives.from_dict(d)

        return normalized

    def _normalize_multivariate(
        self, normalized: Dict[str, Primitives]
    ) -> Dict[str, Primitives]:
        paths = list(self.primitives.keys())
        n = len(paths)
        k = len(self._prim_names)

        features = np.array([
            [self._prim_dict(self.primitives[path]).get(name, 0.0) for name in self._prim_names]
            for path in paths
        ])

        mean_vec = np.mean(features, axis=0)
        cov_matrix = np.cov(features, rowvar=False)

        mahalanobis_distances = []
        for i in range(n):
            dist = Statistics.mahalanobis_distance(features[i], mean_vec, cov_matrix)
            mahalanobis_distances.append(dist)

        from scipy import stats

        p_values = [1 - stats.chi2.cdf(dist, k) for dist in mahalanobis_distances]

        z_scores = []
        for p in p_values:
            if p <= 0:
                z_scores.append(10.0)
            elif p >= 1:
                z_scores.append(0.0)
            else:
                z_scores.append(stats.norm.ppf(1 - p))

        # Per-primitive z-scores for reporting
        z_by_name: Dict[str, List[float]] = {}
        for col, name in enumerate(self._prim_names):
            z_by_name[name] = Statistics.z_scores(features[:, col].tolist())

        for i, path in enumerate(paths):
            d = {name: z_by_name[name][i] for name in self._prim_names}
            normalized[path] = Primitives.from_dict(d)

        self.mahalanobis_scores = {paths[i]: z_scores[i] for i in range(n)}

        return normalized

    # ------------------------------------------------------------------
    # detect
    # ------------------------------------------------------------------

    def detect_anomalies(
        self, normalized: Dict[str, Primitives]
    ) -> Dict[str, List[str]]:
        anomalies: Dict[str, List[str]] = {}

        if self.use_multivariate and hasattr(self, "mahalanobis_scores"):
            return self._detect_multivariate_anomalies(normalized)

        for path, prims in normalized.items():
            flags = self._flag_primitives(prims, self.threshold)
            if flags:
                anomalies[path] = flags

        return anomalies

    def _detect_multivariate_anomalies(
        self, normalized: Dict[str, Primitives]
    ) -> Dict[str, List[str]]:
        anomalies: Dict[str, List[str]] = {}

        for path, mahalanobis_z in self.mahalanobis_scores.items():
            if abs(mahalanobis_z) > self.threshold:
                prims = normalized[path]
                flags = self._flag_primitives(prims, self.threshold * 0.5)
                if flags:
                    anomalies[path] = flags

        return anomalies

    def _flag_primitives(self, prims: Primitives, thresh: float) -> List[str]:
        """Use registry direction metadata to flag anomalous primitives."""
        prim_d = self._prim_dict(prims)
        flags: List[str] = []

        for defn in self._registry:
            z = prim_d.get(defn.name, 0.0)

            if defn.direction == "high_is_bad":
                if z > thresh:
                    flags.append(f"high_{defn.short_name}" if defn.name != "network_centrality" else "high_centrality")
                    # maintain backward-compatible flag names where possible
                    if defn.name == "churn_volatility":
                        flags[-1] = "high_volatility"
                    elif defn.name == "cognitive_load":
                        flags[-1] = "high_cognitive_load"
            elif defn.direction == "low_is_bad":
                if z < -thresh:
                    flags.append(f"{defn.name}_low")
            elif defn.direction == "both_extreme_bad":
                if abs(z) > thresh:
                    if defn.name == "structural_entropy":
                        direction = "high" if z > 0 else "low"
                        flags.append(f"structural_entropy_{direction}")
                    elif defn.name == "semantic_coherence":
                        direction = "low" if z < 0 else "high"
                        flags.append(f"semantic_coherence_{direction}")
                    else:
                        direction = "high" if z > 0 else "low"
                        flags.append(f"{defn.name}_{direction}")

        return flags

    # ------------------------------------------------------------------
    # outlier utilities (unchanged)
    # ------------------------------------------------------------------

    def detect_outliers(
        self, values: List[float], method: str = "grubbs"
    ) -> List[int]:
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
