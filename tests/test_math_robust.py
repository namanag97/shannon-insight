"""Tests for shannon_insight.math.robust module."""

import numpy as np

from shannon_insight.math.robust import RobustStatistics


class TestMedianAbsoluteDeviation:
    """Tests for MAD computation."""

    def test_constant_values(self, constant_values):
        """MAD of constant values is 0."""
        result = RobustStatistics.median_absolute_deviation(constant_values)
        assert result == 0.0

    def test_known_values(self):
        """MAD of [1, 1, 2, 2, 4, 6, 9] = MAD around median 2."""
        values = [1.0, 1.0, 2.0, 2.0, 4.0, 6.0, 9.0]
        result = RobustStatistics.median_absolute_deviation(values)
        # median = 2.0, deviations = [1, 1, 0, 0, 2, 4, 7], median of deviations = 1.0
        assert abs(result - 1.0) < 1e-10

    def test_robust_to_single_outlier(self):
        """MAD is robust to a single outlier."""
        normal = [1.0, 2.0, 3.0, 4.0, 5.0]
        with_outlier = [1.0, 2.0, 3.0, 4.0, 1000.0]
        mad_normal = RobustStatistics.median_absolute_deviation(normal)
        mad_outlier = RobustStatistics.median_absolute_deviation(with_outlier)
        # MAD should not change dramatically with one outlier
        assert abs(mad_outlier - mad_normal) < mad_normal * 2

    def test_numpy_array_input(self):
        """Works with numpy arrays."""
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = RobustStatistics.median_absolute_deviation(values)
        assert result > 0


class TestModifiedZScore:
    """Tests for modified z-score computation."""

    def test_constant_values(self, constant_values):
        """Modified z-scores of constant values are all 0."""
        result = RobustStatistics.modified_z_score(constant_values)
        assert all(z == 0.0 for z in result)

    def test_known_values(self):
        """Modified z-score with known data."""
        # [0, 0, 0, 0, 10]: median=0, MAD=0 -> all zeros
        result = RobustStatistics.modified_z_score([0.0, 0.0, 0.0, 0.0, 10.0])
        assert all(z == 0.0 for z in result)  # MAD = 0

    def test_symmetric_values(self):
        """Symmetric data has symmetric z-scores."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = RobustStatistics.modified_z_score(values)
        # z-scores should be symmetric around 0
        assert abs(result[0] + result[4]) < 1e-10
        assert abs(result[1] + result[3]) < 1e-10

    def test_correct_length(self, normal_values):
        """Output length matches input length."""
        result = RobustStatistics.modified_z_score(normal_values)
        assert len(result) == len(normal_values)


class TestIQROutliers:
    """Tests for IQR outlier detection."""

    def test_no_outliers_in_normal_data(self):
        """Normal-range data has no outliers."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        result = RobustStatistics.iqr_outliers(values)
        assert not any(result)

    def test_detects_extreme_values(self, outlier_values):
        """IQR flags extreme values."""
        result = RobustStatistics.iqr_outliers(outlier_values)
        assert result[4] is True  # 100.0 is the outlier

    def test_multiplier_sensitivity(self):
        """Higher multiplier is less sensitive."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 20.0]
        strict = RobustStatistics.iqr_outliers(values, multiplier=1.0)
        lenient = RobustStatistics.iqr_outliers(values, multiplier=3.0)
        # Strict should flag at least as many as lenient
        assert sum(strict) >= sum(lenient)

    def test_correct_length(self, normal_values):
        """Output length matches input length."""
        result = RobustStatistics.iqr_outliers(normal_values)
        assert len(result) == len(normal_values)

    def test_all_same_no_outliers(self, constant_values):
        """Constant values have no outliers."""
        result = RobustStatistics.iqr_outliers(constant_values)
        assert not any(result)
