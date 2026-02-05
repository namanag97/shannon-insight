"""Tests for Gini coefficient calculations."""

import pytest

from shannon_insight.math.gini import Gini


class TestGiniCoefficient:
    """Tests for Gini.gini_coefficient."""

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            Gini.gini_coefficient([])

    def test_single_value_zero(self):
        assert Gini.gini_coefficient([42]) == 0.0

    def test_all_zeros_returns_zero(self):
        assert Gini.gini_coefficient([0, 0, 0, 0]) == 0.0

    def test_negative_values_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            Gini.gini_coefficient([1, -1, 2])

    def test_perfect_equality(self):
        # All equal values should give Gini = 0
        assert Gini.gini_coefficient([5, 5, 5, 5]) == 0.0
        assert Gini.gini_coefficient([10, 10, 10]) == 0.0
        assert Gini.gini_coefficient([1, 1, 1, 1, 1]) == 0.0

    def test_perfect_inequality(self):
        # [0, 0, 0, 100] should give Gini close to 1.0 (with bias correction)
        gini = Gini.gini_coefficient([0, 0, 0, 100])
        assert gini > 0.9
        assert gini <= 1.0

    def test_moderate_inequality(self):
        # A known moderate inequality case
        gini = Gini.gini_coefficient([1, 2, 3, 10])
        assert 0.2 < gini < 0.7

    def test_result_in_valid_range(self):
        # Result should always be in [0, 1]
        test_cases = [
            [1, 1, 1],
            [1, 2, 3],
            [0, 0, 100],
            [1, 1, 1, 100],
            [5, 10, 15, 20, 80],
        ]
        for values in test_cases:
            gini = Gini.gini_coefficient(values)
            assert 0.0 <= gini <= 1.0, f"Gini out of range for {values}: {gini}"

    def test_without_bias_correction(self):
        gini_with = Gini.gini_coefficient([1, 2, 3, 10], bias_correction=True)
        gini_without = Gini.gini_coefficient([1, 2, 3, 10], bias_correction=False)
        # With correction should be slightly larger (n/(n-1) factor)
        assert gini_with >= gini_without

    def test_god_function_pattern(self):
        # Simulate: 8 small functions (3 lines) + 2 large ones (80 lines)
        sizes = [3, 3, 3, 3, 3, 3, 3, 3, 80, 80]
        gini = Gini.gini_coefficient(sizes)
        # This should show high inequality
        assert gini > 0.4

    def test_balanced_functions(self):
        # 10 functions of roughly equal size
        sizes = [10, 12, 11, 10, 13, 10, 11, 12, 10, 11]
        gini = Gini.gini_coefficient(sizes)
        # Should be low inequality
        assert gini < 0.15

    def test_two_values(self):
        # Simplest non-trivial case
        gini = Gini.gini_coefficient([1, 100])
        assert gini > 0.5

    def test_floats_work(self):
        gini = Gini.gini_coefficient([1.0, 2.0, 3.0, 4.0])
        assert 0.0 <= gini <= 1.0
