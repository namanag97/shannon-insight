"""Information theory: Shannon entropy, KL divergence, joint entropy."""

import math
from collections.abc import Mapping
from typing import Union


class Entropy:
    """Information entropy calculations."""

    @staticmethod
    def shannon(distribution: Mapping[str, Union[int, float]]) -> float:
        """
        Compute Shannon entropy H(X) = -Σ p(x) log₂ p(x).

        Args:
            distribution: Dictionary with event -> count mapping

        Returns:
            Entropy in bits
        """
        total = sum(distribution.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in distribution.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    @staticmethod
    def normalized(distribution: Mapping[str, Union[int, float]]) -> float:
        """
        Normalize entropy by maximum possible entropy.

        H_norm = H / log₂(N) where N is number of unique events

        Returns:
            Normalized entropy in [0, 1]
        """
        h = Entropy.shannon(distribution)
        n = len(distribution)
        if n <= 1:
            return 0.0
        max_h = math.log2(n)
        return h / max_h if max_h > 0 else 0.0

    @staticmethod
    def kl_divergence(
        p: Mapping[str, Union[int, float]], q: Mapping[str, Union[int, float]]
    ) -> float:
        """
        Compute Kullback-Leibler divergence D_KL(P || Q).

        D_KL(P || Q) = Σ P(x) log₂(P(x) / Q(x))

        Args:
            p: Observed distribution
            q: Expected distribution

        Returns:
            KL divergence in bits (lower = more similar)
        """
        total_p = sum(p.values())
        total_q = sum(q.values())

        if total_p == 0 or total_q == 0:
            return 0.0

        kl_div = 0.0
        for key, count_p in p.items():
            prob_p = count_p / total_p
            prob_q = q.get(key, 0) / total_q if key in q else 0

            if prob_p > 0 and prob_q == 0:
                # D_KL is undefined (infinite) when P(x)>0 but Q(x)=0
                return float("inf")
            if prob_p > 0 and prob_q > 0:
                kl_div += prob_p * math.log2(prob_p / prob_q)

        return kl_div

    @staticmethod
    def joint_entropy(joint_distribution: Mapping[tuple, Union[int, float]]) -> float:
        """
        Compute joint entropy H(X, Y, ...) from a joint distribution.

        H(X,Y) = -Σ_x Σ_y p(x,y) log₂ p(x,y)

        The joint distribution must be keyed by tuples representing
        joint outcomes, e.g. {("a", "b"): 5, ("a", "c"): 3, ...}.

        Args:
            joint_distribution: Dictionary mapping outcome tuples to counts

        Returns:
            Joint entropy in bits

        Reference:
            Cover & Thomas, *Elements of Information Theory*, 2nd ed.,
            Chapter 2 (Theorem 2.6.6).
        """
        # Delegate to shannon() — the formula is identical, only the
        # sample space changes from singleton events to joint events.
        return Entropy.shannon(joint_distribution)  # type: ignore[arg-type]

    @staticmethod
    def pooled_entropy(*distributions: Mapping[str, Union[int, float]]) -> float:
        """
        Compute entropy of the pooled (merged) sample from multiple distributions.

        This is NOT the same as joint entropy. It merges all counts into a
        single distribution and computes H of the mixture. Useful when you
        want the entropy of the combined observation set.

        H_pooled = H(merge(X₁, X₂, ...))

        Args:
            *distributions: Multiple count distributions to pool

        Returns:
            Entropy of the pooled distribution in bits
        """
        merged: dict = {}
        for dist in distributions:
            for key, count in dist.items():
                merged[key] = merged.get(key, 0) + count

        return Entropy.shannon(merged)
