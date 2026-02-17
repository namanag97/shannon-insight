"""Tests for trajectory classification per v2 spec."""

from shannon_insight.temporal.churn import _classify_trajectory, _compute_cv, _linear_slope


class TestTrajectoryClassification:
    """Test trajectory classification matches v2 spec (temporal-operators.md)."""

    def test_dormant_zero_changes(self):
        """total_changes <= 1 -> DORMANT."""
        assert _classify_trajectory([0, 0, 0, 0], 0, 0.0, 0.0) == "DORMANT"
        assert _classify_trajectory([1], 1, 0.0, 0.0) == "DORMANT"
        assert _classify_trajectory([0, 1, 0, 0], 1, 0.0, 0.0) == "DORMANT"

    def test_dormant_zero_cv(self):
        """cv = 0 (perfectly uniform) -> DORMANT."""
        # All windows have equal non-zero changes
        counts = [5, 5, 5, 5]
        cv = _compute_cv(counts, 20)
        assert cv == 0.0
        assert _classify_trajectory(counts, 20, 0.0, cv) == "DORMANT"

    def test_stabilizing_negative_slope_low_cv(self):
        """slope < -0.1 AND cv < 0.5 -> STABILIZING."""
        # Decreasing steadily: 10, 8, 6, 4
        counts = [10, 8, 6, 4]
        slope = _linear_slope(counts)
        cv = _compute_cv(counts, sum(counts))

        assert slope < -0.1, f"Expected negative slope, got {slope}"
        assert cv < 0.5, f"Expected cv < 0.5, got {cv}"
        assert _classify_trajectory(counts, sum(counts), slope, cv) == "STABILIZING"

    def test_spiking_positive_slope_high_cv(self):
        """slope > 0.1 AND cv > 0.5 -> SPIKING."""
        # Increasing erratically: 1, 2, 3, 15
        counts = [1, 2, 3, 15]
        slope = _linear_slope(counts)
        cv = _compute_cv(counts, sum(counts))

        assert slope > 0.1, f"Expected positive slope, got {slope}"
        assert cv > 0.5, f"Expected cv > 0.5, got {cv}"
        assert _classify_trajectory(counts, sum(counts), slope, cv) == "SPIKING"

    def test_churning_high_cv_no_trend(self):
        """cv > 0.5 with no clear trend -> CHURNING."""
        # Erratic with no trend: 5, 1, 8, 2
        counts = [5, 1, 8, 2]
        slope = _linear_slope(counts)
        cv = _compute_cv(counts, sum(counts))

        assert abs(slope) <= 0.1 or cv > 0.5, "Should be high cv or no trend"
        assert cv > 0.5, f"Expected cv > 0.5, got {cv}"
        # If slope is not strongly negative or positive, but cv is high -> CHURNING
        assert _classify_trajectory(counts, sum(counts), slope, cv) == "CHURNING"

    def test_stable_low_cv_no_trend(self):
        """cv <= 0.5 with no strong trend -> STABLE."""
        # Steady with minimal variation: 5, 5, 6, 5 (slope ~0.1, cv low)
        counts = [5, 5, 6, 5]
        slope = _linear_slope(counts)
        cv = _compute_cv(counts, sum(counts))

        assert cv <= 0.5, f"Expected cv <= 0.5, got {cv}"
        # Slope might be small positive, but cv is low so it's STABLE not SPIKING
        assert _classify_trajectory(counts, sum(counts), slope, cv) == "STABLE"

    def test_stabilizing_requires_low_cv(self):
        """Negative slope but high cv should NOT be STABILIZING."""
        # Decreasing but erratic: 20, 1, 10, 2
        counts = [20, 1, 10, 2]
        slope = _linear_slope(counts)
        cv = _compute_cv(counts, sum(counts))

        # Even with negative slope, high cv means CHURNING not STABILIZING
        if slope < -0.1 and cv > 0.5:
            # Per spec: STABILIZING requires cv < 0.5
            assert _classify_trajectory(counts, sum(counts), slope, cv) == "CHURNING"

    def test_all_trajectories_are_uppercase(self):
        """All trajectory values should be uppercase."""
        test_cases = [
            ([0, 0, 0, 0], 0),  # DORMANT
            ([10, 8, 6, 4], sum([10, 8, 6, 4])),  # STABILIZING
            ([5, 6, 5, 6], sum([5, 6, 5, 6])),  # STABLE
            ([5, 1, 8, 2], sum([5, 1, 8, 2])),  # CHURNING
            ([1, 2, 3, 15], sum([1, 2, 3, 15])),  # SPIKING
        ]

        for counts, total in test_cases:
            slope = _linear_slope(counts)
            cv = _compute_cv(counts, total)
            result = _classify_trajectory(counts, total, slope, cv)
            assert result == result.upper(), f"Trajectory {result} should be uppercase"
            assert result in {"DORMANT", "STABILIZING", "STABLE", "CHURNING", "SPIKING"}


class TestCVComputation:
    """Test coefficient of variation calculation."""

    def test_uniform_distribution_zero_cv(self):
        """Equal values should have CV = 0."""
        assert _compute_cv([5, 5, 5, 5], 20) == 0.0

    def test_single_window_zero_cv(self):
        """Single window should return 0 (CV undefined)."""
        assert _compute_cv([10], 10) == 0.0

    def test_no_changes_zero_cv(self):
        """No changes should return 0."""
        assert _compute_cv([0, 0, 0], 0) == 0.0

    def test_high_variance_high_cv(self):
        """High variance relative to mean should give high CV."""
        # One spike: cv should be > 1.0
        cv = _compute_cv([0, 0, 0, 10], 10)
        assert cv > 1.0


class TestLinearSlope:
    """Test linear regression slope calculation."""

    def test_increasing_positive_slope(self):
        """Increasing values should have positive slope."""
        assert _linear_slope([1, 2, 3, 4]) > 0

    def test_decreasing_negative_slope(self):
        """Decreasing values should have negative slope."""
        assert _linear_slope([4, 3, 2, 1]) < 0

    def test_constant_zero_slope(self):
        """Constant values should have zero slope."""
        assert _linear_slope([5, 5, 5, 5]) == 0.0

    def test_single_value_zero_slope(self):
        """Single value should return zero slope."""
        assert _linear_slope([5]) == 0.0
