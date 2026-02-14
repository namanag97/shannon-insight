"""Evidence fusion: Bayesian combination, Dempster-Shafer theory."""


def _compute_pairwise_combination(
    m1: dict[frozenset, float], m2: dict[frozenset, float]
) -> tuple[dict[frozenset, float], float]:
    """
    Compute pairwise Dempster-Shafer combination of two mass functions.

    Iterates over all focal sets in m1 and m2, computing their intersection.
    If the intersection is non-empty, accumulates the product of masses.
    If empty, accumulates to conflict coefficient.

    Args:
        m1: First mass function {frozenset(hypotheses): mass}
        m2: Second mass function {frozenset(hypotheses): mass}

    Returns:
        Tuple of (combined_mass, total_conflict)
        - combined_mass: Unnormalized combined mass function
        - total_conflict: Sum of masses for conflicting focal sets (empty intersection)
    """
    combined: dict[frozenset, float] = {}
    total_conflict = 0.0

    for a, ma in m1.items():
        for b, mb in m2.items():
            intersection = a & b
            if intersection:
                combined[intersection] = combined.get(intersection, 0.0) + ma * mb
            else:
                total_conflict += ma * mb

    return combined, total_conflict


def _normalize_mass_function(
    combined: dict[frozenset, float], conflict: float
) -> dict[frozenset, float]:
    """
    Normalize a mass function by the conflict coefficient.

    In Dempster-Shafer theory, after combining two mass functions,
    we normalize by (1 - K) where K is the total conflict mass.
    This redistributes the conflicting mass among the remaining focal sets.

    Args:
        combined: Unnormalized mass function
        conflict: Total conflict coefficient K

    Returns:
        Normalized mass function where masses sum to 1.0
        If normalization factor is 0 (total conflict), returns empty dict.
    """
    normalization = 1.0 - conflict
    if normalization > 0:
        return {k: v / normalization for k, v in combined.items()}
    return {}


class SignalFusion:
    """Evidence-theoretic signal fusion methods."""

    @staticmethod
    def bayesian_fusion(priors: list[float], likelihoods: list[float]) -> tuple[float, float]:
        """
        Bayesian evidence combination: P(H|E) = P(E|H) * P(H) / P(E).

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
        import math as _math

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
        # When all mass is on one hypothesis, entropy = 0 -> confidence = 1.
        # When posteriors are uniform, entropy = log2(n) -> confidence = 0.
        n = len(posteriors)
        if n <= 1:
            confidence = 1.0
        else:
            entropy = -sum(p * _math.log2(p) for p in posteriors if p > 0)
            max_entropy = _math.log2(n)
            confidence = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 1.0

        return float(max_posterior), float(confidence)

    @staticmethod
    def dempster_shafer_combination(
        mass_functions: list[dict[frozenset, float]],
    ) -> dict[frozenset, float]:
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
            new_combined: dict[frozenset, float] = {}
            total_conflict = 0.0

            for a, ma in combined.items():
                for b, mb in m2.items():
                    intersection = a & b  # proper set intersection
                    if intersection:
                        new_combined[intersection] = new_combined.get(intersection, 0.0) + ma * mb
                    else:
                        total_conflict += ma * mb

            normalization = 1.0 - total_conflict
            if normalization > 0:
                new_combined = {k: v / normalization for k, v in new_combined.items()}

            combined = new_combined

        return combined
