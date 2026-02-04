"""
Advanced signal fusion with mathematical rigor — registry-driven.

Implements:
- Dempster-Shafer evidence theory
- Bayesian evidence combination
- Consistency-weighted fusion using statistical methods
- Confidence quantification
"""

import math
import statistics
from typing import Dict, List, Tuple, Optional
import numpy as np

from ..models import Primitives
from ..logging_config import get_logger
from .registry import get_registry, default_weights

logger = get_logger(__name__)


class SignalFusion:
    """Fuse multiple signals with statistical confidence quantification."""

    def __init__(
        self,
        primitives: Dict[str, Primitives],
        normalized: Dict[str, Primitives],
        weights: Optional[List[float]] = None,
    ):
        self.primitives = primitives
        self.normalized = normalized

        # Build weights dict from registry.  If caller passes the legacy
        # List[float] (5 elements in order), convert to dict keyed by
        # registry name.  If None, use registry defaults.
        registry = get_registry()
        prim_names = [d.name for d in registry]

        if weights is not None and isinstance(weights, list):
            # Legacy list form — map positionally to registry order
            if len(weights) == len(prim_names):
                self._weights: Dict[str, float] = dict(zip(prim_names, weights))
            else:
                # fallback: use registry defaults if length mismatch
                self._weights = default_weights()
        elif weights is not None and isinstance(weights, dict):
            self._weights = weights
        else:
            self._weights = default_weights()

        self._prim_names = prim_names
        logger.debug(f"Initialized SignalFusion with weights={self._weights}")

    def fuse(self) -> Dict[str, Tuple[float, float]]:
        """Fuse signals with consistency weighting.

        Returns:
            Dictionary mapping paths to (score, confidence) tuples
        """
        results = {}

        for path in self.primitives.keys():
            norm = self.normalized[path]
            norm_d = norm.to_dict()

            scores = [norm_d.get(name, 0.0) for name in self._prim_names]
            w_list = [self._weights.get(name, 0.0) for name in self._prim_names]

            # Consistency measures
            cv_consistency = self._coefficient_of_variation_consistency(scores)
            correlation_consistency = self._correlation_consistency(scores)
            entropy_consistency = self._entropy_consistency(scores)

            overall_consistency = (
                cv_consistency ** 0.4
                * correlation_consistency ** 0.3
                * entropy_consistency ** 0.3
            )

            fused_score = sum(s * w for s, w in zip(scores, w_list))
            final_score = overall_consistency * abs(fused_score)

            results[path] = (final_score, overall_consistency)

        return results

    # ------------------------------------------------------------------
    # Consistency helpers (unchanged from original)
    # ------------------------------------------------------------------

    def _coefficient_of_variation_consistency(self, z_scores: List[float]) -> float:
        abs_scores = [abs(s) for s in z_scores]
        mean_abs = statistics.mean(abs_scores)
        if mean_abs == 0:
            return 1.0
        std_abs = statistics.stdev(abs_scores) if len(abs_scores) > 1 else 0
        cv = std_abs / mean_abs if mean_abs > 0 else 0
        return 1.0 / (1.0 + cv)

    def _correlation_consistency(self, z_scores: List[float]) -> float:
        signs = [1 if s > 0 else -1 for s in z_scores if s != 0]
        if len(signs) < 2:
            return 1.0
        majority_sign = statistics.mode(signs)
        agreement_count = sum(1 for s in signs if s == majority_sign)
        return agreement_count / len(signs)

    def _entropy_consistency(self, z_scores: List[float]) -> float:
        abs_scores = [abs(s) for s in z_scores]
        total = sum(abs_scores)
        if total == 0:
            return 1.0
        probs = [s / total for s in abs_scores]
        entropy_val = 0.0
        for p in probs:
            if p > 0:
                entropy_val -= p * math.log2(p)
        max_entropy = math.log2(len(probs)) if len(probs) > 1 else 1.0
        normalized_entropy_val = entropy_val / max_entropy if max_entropy > 0 else 0
        return 1.0 - normalized_entropy_val

    # ------------------------------------------------------------------
    # Advanced fusion methods (kept for API compatibility)
    # ------------------------------------------------------------------

    def bayesian_fusion(
        self, priors: List[float], likelihoods: List[float]
    ) -> Tuple[float, float]:
        if len(priors) != len(likelihoods):
            raise ValueError("priors and likelihoods must have the same length")
        unnormalized = [p * l for p, l in zip(priors, likelihoods)]
        evidence = sum(unnormalized)
        if evidence <= 0:
            n = len(priors)
            return 1.0 / n if n > 0 else 0.0, 0.0
        posteriors = [u / evidence for u in unnormalized]
        max_posterior = max(posteriors)
        n = len(posteriors)
        if n <= 1:
            confidence = 1.0
        else:
            entropy = -sum(p * math.log2(p) for p in posteriors if p > 0)
            max_entropy = math.log2(n)
            confidence = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 1.0
        return float(max_posterior), float(confidence)

    def dempster_shafer_combine(
        self, mass_functions: List[Dict[frozenset, float]]
    ) -> Dict[frozenset, float]:
        if not mass_functions:
            return {}
        combined = mass_functions[0].copy()
        for i in range(1, len(mass_functions)):
            m2 = mass_functions[i]
            new_combined: Dict[frozenset, float] = {}
            total_conflict = 0.0
            for a, ma in combined.items():
                for b, mb in m2.items():
                    intersection = a & b
                    if intersection:
                        new_combined[intersection] = new_combined.get(intersection, 0.0) + ma * mb
                    else:
                        total_conflict += ma * mb
            normalization = 1.0 - total_conflict
            if normalization > 0:
                new_combined = {k: v / normalization for k, v in new_combined.items()}
            combined = new_combined
        return combined

    def multivariate_fusion(
        self, z_scores: np.ndarray, covariance: np.ndarray
    ) -> float:
        z = np.atleast_1d(z_scores).astype(float)
        k = len(z)
        try:
            cond = np.linalg.cond(covariance)
            if cond > 1e12:
                return float(np.linalg.norm(z))
            inv_cov = np.linalg.inv(covariance)
        except np.linalg.LinAlgError:
            return float(np.linalg.norm(z))
        md_squared = float(z @ inv_cov @ z)
        from scipy import stats
        p_value = 1 - stats.chi2.cdf(md_squared, k)
        if p_value <= 0:
            z_equiv = 10.0
        elif p_value >= 1:
            z_equiv = 0.0
        else:
            z_equiv = stats.norm.ppf(1 - p_value)
        return float(z_equiv)

    def adaptive_fusion(
        self, z_scores: List[float], signal_reliabilities: List[float]
    ) -> float:
        if len(z_scores) != len(signal_reliabilities):
            raise ValueError("z_scores and signal_reliabilities must have same length")
        total_reliability = sum(signal_reliabilities)
        if total_reliability == 0:
            return statistics.mean(z_scores)
        weighted_sum = sum(
            rel * score for rel, score in zip(signal_reliabilities, z_scores)
        )
        return weighted_sum / total_reliability

    def confidence_weighted_fusion(
        self, z_scores: List[float], confidences: List[float]
    ) -> Tuple[float, float]:
        if len(z_scores) != len(confidences):
            raise ValueError("z_scores and confidences must have same length")
        total_weight = sum(confidences)
        if total_weight == 0:
            return statistics.mean(z_scores), 0.5
        weighted_score = sum(
            conf * score for conf, score in zip(confidences, z_scores)
        ) / total_weight
        overall_confidence = math.prod(confidences) ** (1.0 / len(confidences))
        return float(weighted_score), float(overall_confidence)
