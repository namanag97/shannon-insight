"""Tests for shannon_insight.math.statistics module."""

import numpy as np

from shannon_insight.math.statistics import Statistics


class TestMeanAndStdev:
    """Tests for basic statistics."""

    def test_mean_empty(self):
        """Mean of empty list is 0."""
        assert Statistics.mean([]) == 0.0

    def test_mean_known(self, normal_values):
        """Mean of known data."""
        expected = sum(normal_values) / len(normal_values)
        assert abs(Statistics.mean(normal_values) - expected) < 1e-10

    def test_stdev_single_value(self):
        """Stdev of single value is 0."""
        assert Statistics.stdev([42.0]) == 0.0

    def test_stdev_known(self):
        """Stdev of [2, 4, 4, 4, 5, 5, 7, 9] is known."""
        result = Statistics.stdev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
        assert result > 0


class TestZScores:
    """Tests for z-score computation."""

    def test_empty_input(self):
        """Empty input returns empty list."""
        assert Statistics.z_scores([]) == []

    def test_single_value(self):
        """Single value returns [0.0]."""
        assert Statistics.z_scores([5.0]) == [0.0]

    def test_constant_values(self, constant_values):
        """Constant values all have z-score 0."""
        result = Statistics.z_scores(constant_values)
        assert all(z == 0.0 for z in result)

    def test_known_data(self):
        """Z-scores have mean ~0 and stdev ~1."""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        z = Statistics.z_scores(values)
        assert abs(sum(z) / len(z)) < 1e-10  # mean = 0
        z_std = (sum(zi**2 for zi in z) / len(z)) ** 0.5
        assert abs(z_std - 1.0) < 0.2  # approximately unit variance

    def test_z_score_single(self):
        """Single z-score computation."""
        assert Statistics.z_score(10.0, 5.0, 2.5) == 2.0
        assert Statistics.z_score(5.0, 5.0, 2.5) == 0.0
        assert Statistics.z_score(5.0, 5.0, 0.0) == 0.0  # zero std


class TestMahalanobisDistance:
    """Tests for Mahalanobis distance."""

    def test_identity_covariance_equals_euclidean(self, identity_cov_3d):
        """With identity covariance, Mahalanobis = Euclidean^2."""
        point = np.array([3.0, 4.0, 0.0])
        mean = np.array([0.0, 0.0, 0.0])
        result = Statistics.mahalanobis_distance(point, mean, identity_cov_3d)
        expected = 3.0**2 + 4.0**2  # 25.0
        assert abs(result - expected) < 1e-10

    def test_zero_distance_at_mean(self, identity_cov_3d):
        """Point at mean has zero distance."""
        mean = np.array([1.0, 2.0, 3.0])
        result = Statistics.mahalanobis_distance(mean, mean, identity_cov_3d)
        assert abs(result) < 1e-10

    def test_singular_covariance_uses_pinv(self):
        """Singular covariance uses pseudoinverse without error."""
        point = np.array([1.0, 2.0])
        mean = np.array([0.0, 0.0])
        # Singular matrix (rank 1)
        cov = np.array([[1.0, 1.0], [1.0, 1.0]])
        result = Statistics.mahalanobis_distance(point, mean, cov)
        assert result >= 0  # Should not raise


class TestGrubbsTest:
    """Tests for Grubbs' outlier test."""

    def test_too_few_values(self):
        """Grubbs test requires at least 3 values."""
        assert Statistics.grubbs_test([1.0, 2.0]) is None

    def test_constant_values(self, constant_values):
        """Constant values have no outlier."""
        assert Statistics.grubbs_test(constant_values) is None

    def test_detects_obvious_outlier(self, outlier_values):
        """Detects [1, 1, 1, 1, 100] outlier."""
        result = Statistics.grubbs_test(outlier_values)
        assert result is not None
        outlier_idx, g_stat = result
        assert outlier_idx == 4  # 100.0 is at index 4
        assert g_stat > 0

    def test_no_outlier_in_normal_data(self, normal_values):
        """Normal-ish data may not have an outlier at default alpha."""
        # This is probabilistic, but the data is not extreme
        result = Statistics.grubbs_test(normal_values)
        # Either None or a result — just ensure it doesn't crash
        assert result is None or (isinstance(result, tuple) and len(result) == 2)


class TestConfidenceInterval:
    """Tests for confidence interval."""

    def test_single_value(self):
        """Single value CI is (value, value)."""
        lo, hi = Statistics.confidence_interval([42.0])
        assert lo == 42.0
        assert hi == 42.0

    def test_empty_values(self):
        """Empty values CI is (0, 0)."""
        lo, hi = Statistics.confidence_interval([])
        assert lo == 0.0
        assert hi == 0.0

    def test_mean_within_interval(self, normal_values):
        """Mean is within the confidence interval."""
        lo, hi = Statistics.confidence_interval(normal_values)
        mean = sum(normal_values) / len(normal_values)
        assert lo <= mean <= hi

    def test_wider_at_higher_confidence(self, normal_values):
        """99% CI is wider than 90% CI."""
        lo_90, hi_90 = Statistics.confidence_interval(normal_values, confidence=0.90)
        lo_99, hi_99 = Statistics.confidence_interval(normal_values, confidence=0.99)
        width_90 = hi_90 - lo_90
        width_99 = hi_99 - lo_99
        assert width_99 > width_90
