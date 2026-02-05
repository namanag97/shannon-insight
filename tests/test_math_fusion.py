"""Tests for shannon_insight.math.fusion module."""

import pytest

from shannon_insight.math.fusion import SignalFusion


class TestBayesianFusion:
    """Tests for Bayesian evidence combination."""

    def test_mismatched_lengths_raises(self):
        """Mismatched priors and likelihoods raise ValueError."""
        with pytest.raises(ValueError, match="same length"):
            SignalFusion.bayesian_fusion([0.5, 0.5], [0.1])

    def test_zero_evidence_returns_uniform(self):
        """Zero evidence returns uniform posterior and zero confidence."""
        max_post, confidence = SignalFusion.bayesian_fusion([0.5, 0.5], [0.0, 0.0])
        assert abs(max_post - 0.5) < 1e-10  # 1/n
        assert confidence == 0.0

    def test_strong_likelihood_high_posterior(self):
        """Strong likelihood concentrates posterior."""
        priors = [0.5, 0.5]
        likelihoods = [0.99, 0.01]
        max_post, confidence = SignalFusion.bayesian_fusion(priors, likelihoods)
        assert max_post > 0.9
        assert confidence > 0.5

    def test_uniform_priors_with_equal_likelihoods(self):
        """Equal likelihoods with uniform priors give uniform posterior."""
        priors = [0.25, 0.25, 0.25, 0.25]
        likelihoods = [1.0, 1.0, 1.0, 1.0]
        max_post, confidence = SignalFusion.bayesian_fusion(priors, likelihoods)
        assert abs(max_post - 0.25) < 1e-10
        assert abs(confidence) < 1e-10  # Maximum entropy = minimum confidence

    def test_single_hypothesis(self):
        """Single hypothesis has posterior 1.0 and confidence 1.0."""
        max_post, confidence = SignalFusion.bayesian_fusion([1.0], [0.5])
        assert abs(max_post - 1.0) < 1e-10
        assert abs(confidence - 1.0) < 1e-10

    def test_posterior_sums_to_one(self):
        """The posteriors (implicitly) sum to 1."""
        priors = [0.3, 0.3, 0.4]
        likelihoods = [0.2, 0.5, 0.8]
        # Just verify it doesn't crash and returns valid values
        max_post, confidence = SignalFusion.bayesian_fusion(priors, likelihoods)
        assert 0.0 <= max_post <= 1.0
        assert 0.0 <= confidence <= 1.0


class TestDempsterShaferCombination:
    """Tests for Dempster-Shafer evidence combination."""

    def test_empty_input(self):
        """Empty input returns empty dict."""
        result = SignalFusion.dempster_shafer_combination([])
        assert result == {}

    def test_single_source(self):
        """Single source returns same mass function."""
        m = {frozenset({"a"}): 0.6, frozenset({"b"}): 0.4}
        result = SignalFusion.dempster_shafer_combination([m])
        assert abs(result[frozenset({"a"})] - 0.6) < 1e-10
        assert abs(result[frozenset({"b"})] - 0.4) < 1e-10

    def test_agreeing_sources(self):
        """Two agreeing sources strengthen the hypothesis."""
        m1 = {frozenset({"a"}): 0.8, frozenset({"a", "b"}): 0.2}
        m2 = {frozenset({"a"}): 0.7, frozenset({"a", "b"}): 0.3}
        result = SignalFusion.dempster_shafer_combination([m1, m2])
        # Mass on {a} should be high
        assert result.get(frozenset({"a"}), 0) > 0.7

    def test_conflicting_sources(self):
        """Conflicting sources redistribute mass after normalization."""
        m1 = {frozenset({"a"}): 0.9, frozenset({"b"}): 0.1}
        m2 = {frozenset({"b"}): 0.9, frozenset({"a"}): 0.1}
        result = SignalFusion.dempster_shafer_combination([m1, m2])
        # Both {a} and {b} should have positive mass
        assert result.get(frozenset({"a"}), 0) > 0
        assert result.get(frozenset({"b"}), 0) > 0
        # Mass should sum to ~1
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-10

    def test_mass_sums_to_one(self):
        """Combined mass always sums to 1.0 (after normalization)."""
        m1 = {frozenset({"a"}): 0.5, frozenset({"b"}): 0.3, frozenset({"a", "b"}): 0.2}
        m2 = {frozenset({"a"}): 0.6, frozenset({"b"}): 0.2, frozenset({"a", "b"}): 0.2}
        result = SignalFusion.dempster_shafer_combination([m1, m2])
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-10

    def test_three_sources(self):
        """Three sources can be combined sequentially."""
        m1 = {frozenset({"a"}): 0.6, frozenset({"a", "b"}): 0.4}
        m2 = {frozenset({"a"}): 0.7, frozenset({"a", "b"}): 0.3}
        m3 = {frozenset({"a"}): 0.5, frozenset({"b"}): 0.5}
        result = SignalFusion.dempster_shafer_combination([m1, m2, m3])
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-10
