"""Tests for shannon_insight.math.entropy module."""

import math

from shannon_insight.math.entropy import Entropy


class TestShannonEntropy:
    """Tests for Shannon entropy computation."""

    def test_empty_distribution(self, empty_distribution):
        """Empty distribution has zero entropy."""
        assert Entropy.shannon(empty_distribution) == 0.0

    def test_single_event(self, single_event_distribution):
        """Single event (certainty) has zero entropy."""
        assert Entropy.shannon(single_event_distribution) == 0.0

    def test_uniform_distribution_equals_log2_n(self, uniform_distribution):
        """Uniform distribution over N events has entropy = log2(N)."""
        expected = math.log2(4)  # 2.0 bits
        result = Entropy.shannon(uniform_distribution)
        assert abs(result - expected) < 1e-10

    def test_fair_coin(self, known_distribution):
        """Fair coin has entropy = 1.0 bit."""
        result = Entropy.shannon(known_distribution)
        assert abs(result - 1.0) < 1e-10

    def test_skewed_distribution_less_than_uniform(self, skewed_distribution, uniform_distribution):
        """Skewed distribution has less entropy than uniform."""
        skewed_h = Entropy.shannon(skewed_distribution)
        uniform_h = Entropy.shannon(uniform_distribution)
        assert skewed_h < uniform_h

    def test_entropy_non_negative(self):
        """Entropy is always non-negative."""
        distributions = [
            {"a": 1},
            {"a": 99, "b": 1},
            {"x": 10, "y": 20, "z": 30},
        ]
        for dist in distributions:
            assert Entropy.shannon(dist) >= 0.0


class TestNormalizedEntropy:
    """Tests for normalized entropy."""

    def test_single_event_normalized(self, single_event_distribution):
        """Single event: normalized entropy = 0."""
        assert Entropy.normalized(single_event_distribution) == 0.0

    def test_uniform_normalized_equals_one(self, uniform_distribution):
        """Uniform distribution: normalized entropy = 1.0."""
        result = Entropy.normalized(uniform_distribution)
        assert abs(result - 1.0) < 1e-10

    def test_normalized_in_unit_interval(self, skewed_distribution):
        """Normalized entropy is in [0, 1]."""
        result = Entropy.normalized(skewed_distribution)
        assert 0.0 <= result <= 1.0


class TestKLDivergence:
    """Tests for Kullback-Leibler divergence."""

    def test_self_divergence_is_zero(self, uniform_distribution):
        """KL divergence of a distribution with itself is 0."""
        result = Entropy.kl_divergence(uniform_distribution, uniform_distribution)
        assert abs(result) < 1e-10

    def test_infinite_when_q_zero(self):
        """KL is infinite when P(x) > 0 but Q(x) = 0."""
        p = {"a": 50, "b": 50}
        q = {"a": 100}  # Q has no mass on "b"
        result = Entropy.kl_divergence(p, q)
        assert result == float("inf")

    def test_kl_non_negative(self):
        """KL divergence is non-negative (Gibbs' inequality)."""
        p = {"a": 70, "b": 20, "c": 10}
        q = {"a": 40, "b": 30, "c": 30}
        result = Entropy.kl_divergence(p, q)
        assert result >= 0.0

    def test_empty_distributions(self):
        """KL of empty distributions is 0."""
        assert Entropy.kl_divergence({}, {}) == 0.0
        assert Entropy.kl_divergence({"a": 1}, {}) == 0.0


class TestJointEntropy:
    """Tests for joint entropy."""

    def test_independent_events(self):
        """Joint entropy of independent events >= individual entropies."""
        joint = {
            ("a", "x"): 25,
            ("a", "y"): 25,
            ("b", "x"): 25,
            ("b", "y"): 25,
        }
        result = Entropy.joint_entropy(joint)
        # For independent uniform: H(X,Y) = H(X) + H(Y) = 1 + 1 = 2
        assert abs(result - 2.0) < 1e-10

    def test_empty_joint(self):
        """Empty joint distribution has zero entropy."""
        assert Entropy.joint_entropy({}) == 0.0


class TestPooledEntropy:
    """Tests for pooled entropy."""

    def test_pooling_identical_distributions(self):
        """Pooling identical distributions gives same entropy."""
        dist = {"a": 50, "b": 50}
        single_h = Entropy.shannon(dist)
        pooled_h = Entropy.pooled_entropy(dist, dist)
        assert abs(pooled_h - single_h) < 1e-10

    def test_pooling_disjoint_increases_entropy(self):
        """Pooling disjoint distributions increases entropy."""
        d1 = {"a": 100}
        d2 = {"b": 100}
        pooled_h = Entropy.pooled_entropy(d1, d2)
        assert pooled_h > Entropy.shannon(d1)
        assert abs(pooled_h - 1.0) < 1e-10  # Fair coin

    def test_pooling_empty(self):
        """Pooling empty distributions gives zero entropy."""
        assert Entropy.pooled_entropy({}, {}) == 0.0
