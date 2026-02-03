"""
Advanced signal fusion with mathematical rigor.

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

logger = get_logger(__name__)


class SignalFusion:
    """
    Fuse multiple signals with statistical confidence quantification.

    Uses advanced methods from evidence theory and statistics.
    """

    def __init__(
        self,
        primitives: Dict[str, Primitives],
        normalized: Dict[str, Primitives],
        weights: Optional[List[float]] = None,
    ):
        """
        Initialize signal fusion.

        Args:
            primitives: Raw primitives
            normalized: Normalized primitives (z-scores)
            weights: Fusion weights [entropy, centrality, churn, coherence, cognitive]
        """
        self.primitives = primitives
        self.normalized = normalized
        self.weights = weights or [0.2, 0.25, 0.2, 0.15, 0.2]
        logger.debug(f"Initialized SignalFusion with weights={self.weights}")

    def fuse(self) -> Dict[str, Tuple[float, float]]:
        """
        Fuse signals with consistency weighting.

        Uses coefficient of variation on absolute values for consistency,
        and applies confidence-based weighting.

        Returns:
            Dictionary mapping paths to (score, confidence) tuples
        """
        results = {}

        for path in self.primitives.keys():
            norm = self.normalized[path]

            # Extract z-scores
            scores = [
                norm.structural_entropy,
                norm.network_centrality,
                norm.churn_volatility,
                norm.semantic_coherence,
                norm.cognitive_load,
            ]

            # Compute multiple consistency measures
            cv_consistency = self._coefficient_of_variation_consistency(scores)
            correlation_consistency = self._correlation_consistency(scores)
            entropy_consistency = self._entropy_consistency(scores)

            # Combine consistency measures (weighted geometric mean)
            overall_consistency = (
                cv_consistency ** 0.4
                * correlation_consistency ** 0.3
                * entropy_consistency ** 0.3
            )

            # Weighted average of signals
            fused_score = sum(s * w for s, w in zip(scores, self.weights))

            # Final score = consistency * |weighted_average|
            # This penalizes inconsistent signals
            final_score = overall_consistency * abs(fused_score)

            results[path] = (final_score, overall_consistency)

        return results

    def _coefficient_of_variation_consistency(self, z_scores: List[float]) -> float:
        """
        Compute consistency using coefficient of variation on absolute values.

        CV = σ/μ, lower CV means more consistent signals.

        Consistency = 1 / (1 + CV)
        """
        abs_scores = [abs(s) for s in z_scores]
        mean_abs = statistics.mean(abs_scores)

        if mean_abs == 0:
            return 1.0

        std_abs = statistics.stdev(abs_scores) if len(abs_scores) > 1 else 0

        # Coefficient of variation
        cv = std_abs / mean_abs if mean_abs > 0 else 0

        # Convert to consistency: CV=0 -> 1.0, CV=inf -> 0
        consistency = 1.0 / (1.0 + cv)

        return consistency

    def _correlation_consistency(self, z_scores: List[float]) -> float:
        """
        Compute consistency based on signal correlation.

        For a truly anomalous file, we expect most signals to point in the same direction.
        """
        # Convert to signs (+1 or -1)
        signs = [1 if s > 0 else -1 for s in z_scores if s != 0]

        if len(signs) < 2:
            return 1.0

        # Count how many agree with the majority
        majority_sign = statistics.mode(signs)
        agreement_count = sum(1 for s in signs if s == majority_sign)

        # Consistency = proportion of signals that agree
        consistency = agreement_count / len(signs)

        return consistency

    def _entropy_consistency(self, z_scores: List[float]) -> float:
        """
        Compute consistency using entropy of signal distribution.

        Lower entropy means signals are more clustered (more consistent).
        """
        # Convert to probability distribution
        abs_scores = [abs(s) for s in z_scores]
        total = sum(abs_scores)

        if total == 0:
            return 1.0

        # Normalize to probabilities
        probs = [s / total for s in abs_scores]

        # Compute Shannon entropy
        entropy_val = 0.0
        for p in probs:
            if p > 0:
                entropy_val -= p * math.log2(p)

        # Maximum possible entropy
        max_entropy = math.log2(len(probs)) if len(probs) > 1 else 1.0

        # Normalize entropy to [0, 1]
        normalized_entropy_val = entropy_val / max_entropy if max_entropy > 0 else 0

        # Consistency = 1 - normalized_entropy
        # Low entropy (clustered signals) = high consistency
        consistency = 1.0 - normalized_entropy_val

        return consistency

    def bayesian_fusion(
        self, priors: List[float], likelihoods: List[float]
    ) -> Tuple[float, float]:
        """
        Bayesian evidence combination.

        P(H|E) = P(E|H) * P(H) / P(E)

        Computes the posterior for each hypothesis, normalizes by total
        evidence, and returns the maximum posterior along with an
        entropy-based confidence measure.

        Args:
            priors: Prior probabilities for each hypothesis (should sum to 1)
            likelihoods: Likelihoods P(E|H_i) for each hypothesis

        Returns:
            Tuple of (max_posterior, confidence)
            confidence is 1 - normalized_entropy of the posterior distribution,
            bounded in [0, 1].

        Reference:
            Bayes' theorem; Bishop, "Pattern Recognition and Machine Learning"
            (2006), Chapter 1.2.
        """
        if len(priors) != len(likelihoods):
            raise ValueError("priors and likelihoods must have the same length")

        # Unnormalized posteriors: P(E|H_i) * P(H_i)
        unnormalized = [p * l for p, l in zip(priors, likelihoods)]
        evidence = sum(unnormalized)

        if evidence <= 0:
            n = len(priors)
            return 1.0 / n if n > 0 else 0.0, 0.0

        posteriors = [u / evidence for u in unnormalized]
        max_posterior = max(posteriors)

        # Confidence = 1 - normalized entropy of the posterior distribution.
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
        """
        Combine evidence using Dempster-Shafer theory.

        m(A) = Σ(B∩C=A) m1(B) * m2(C) / (1 - K)

        Where K is conflict coefficient.

        Keys must be frozensets representing hypothesis sets.

        Args:
            mass_functions: List of mass functions {frozenset(hypotheses): mass}

        Returns:
            Combined mass function
        """
        if not mass_functions:
            return {}

        combined = mass_functions[0].copy()

        for i in range(1, len(mass_functions)):
            m2 = mass_functions[i]
            new_combined: Dict[frozenset, float] = {}
            total_conflict = 0.0

            for a, ma in combined.items():
                for b, mb in m2.items():
                    intersection = a & b  # proper set intersection
                    if intersection:
                        new_combined[intersection] = (
                            new_combined.get(intersection, 0.0) + ma * mb
                        )
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
        """
        Multivariate fusion considering signal correlations.

        Uses Mahalanobis distance to account for correlations between signals.

        Args:
            z_scores: Z-score vector (1D array)
            covariance: Covariance matrix of signals

        Returns:
            Fused score (z-equivalent via chi-squared conversion)
        """
        z = np.atleast_1d(z_scores).astype(float)
        k = len(z)

        # Check if covariance is invertible via condition number
        try:
            cond = np.linalg.cond(covariance)
            if cond > 1e12:
                return float(np.linalg.norm(z))
            inv_cov = np.linalg.inv(covariance)
        except np.linalg.LinAlgError:
            return float(np.linalg.norm(z))

        # D^2 = z^T Sigma^-1 z
        md_squared = float(z @ inv_cov @ z)

        from scipy import stats

        p_value = 1 - stats.chi2.cdf(md_squared, k)

        # p ≈ 0 means maximally significant — map to a large z-score.
        # p ≈ 1 means no anomaly — map to z = 0.
        if p_value <= 0:
            z_equiv = 10.0  # practical upper bound for extreme significance
        elif p_value >= 1:
            z_equiv = 0.0
        else:
            z_equiv = stats.norm.ppf(1 - p_value)

        return float(z_equiv)

    def adaptive_fusion(
        self, z_scores: List[float], signal_reliabilities: List[float]
    ) -> float:
        """
        Adaptive fusion that weights signals by reliability.

        Final score = Σ (reliability_i * score_i) / Σ reliability_i

        Args:
            z_scores: Z-scores of signals
            signal_reliabilities: Reliability of each signal [0, 1]

        Returns:
            Fused score
        """
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
        """
        Fusion with explicit confidence weighting.

        Args:
            z_scores: Z-scores of signals
            confidences: Confidence in each signal [0, 1]

        Returns:
            Tuple of (fused_score, overall_confidence)
        """
        if len(z_scores) != len(confidences):
            raise ValueError("z_scores and confidences must have same length")

        # Weighted average
        total_weight = sum(confidences)
        if total_weight == 0:
            return statistics.mean(z_scores), 0.5

        weighted_score = sum(
            conf * score for conf, score in zip(confidences, z_scores)
        ) / total_weight

        # Overall confidence using geometric mean
        # More sensitive to low confidence values
        overall_confidence = math.prod(confidences) ** (1.0 / len(confidences))

        return float(weighted_score), float(overall_confidence)
