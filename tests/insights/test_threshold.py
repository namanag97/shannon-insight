"""Tests for ThresholdCheck tier-aware threshold strategy."""

from shannon_insight.insights.threshold import ThresholdCheck
from shannon_insight.signals.registry import Signal


class MockFileSignals:
    """Mock file signals for testing."""

    def __init__(
        self,
        pagerank: float = 0.5,
        bus_factor: float = 2.0,
        stub_ratio: float = 0.3,
        percentiles: dict | None = None,
    ):
        self.pagerank = pagerank
        self.bus_factor = bus_factor
        self.stub_ratio = stub_ratio
        self.percentiles = percentiles or {}


class MockSignalField:
    """Mock signal field for testing."""

    def __init__(self, tier: str = "FULL"):
        self.tier = tier


class TestThresholdCheckAbove:
    """Test above() method for high_is_bad signals."""

    def test_full_tier_uses_percentile(self):
        """FULL tier uses percentile threshold."""
        field = MockSignalField(tier="FULL")
        check = ThresholdCheck(field)
        fs = MockFileSignals(pagerank=0.01, percentiles={"pagerank": 0.95})
        # Percentile 0.95 > 0.90 threshold
        assert check.above(fs, Signal.PAGERANK, 0.90) is True

    def test_full_tier_below_threshold(self):
        """FULL tier returns False when below threshold."""
        field = MockSignalField(tier="FULL")
        check = ThresholdCheck(field)
        fs = MockFileSignals(pagerank=0.01, percentiles={"pagerank": 0.50})
        # Percentile 0.50 < 0.90 threshold
        assert check.above(fs, Signal.PAGERANK, 0.90) is False

    def test_bayesian_tier_uses_percentile(self):
        """BAYESIAN tier uses percentile threshold."""
        field = MockSignalField(tier="BAYESIAN")
        check = ThresholdCheck(field)
        fs = MockFileSignals(percentiles={"pagerank": 0.92})
        assert check.above(fs, Signal.PAGERANK, 0.90) is True

    def test_absolute_tier_uses_absolute_threshold(self):
        """ABSOLUTE tier uses absolute threshold from registry."""
        field = MockSignalField(tier="ABSOLUTE")
        check = ThresholdCheck(field)
        # STUB_RATIO has absolute_threshold=0.5
        fs = MockFileSignals(stub_ratio=0.6)  # 0.6 > 0.5
        assert check.above(fs, Signal.STUB_RATIO, 0.90) is True

    def test_absolute_tier_below_absolute_threshold(self):
        """ABSOLUTE tier returns False when below absolute threshold."""
        field = MockSignalField(tier="ABSOLUTE")
        check = ThresholdCheck(field)
        fs = MockFileSignals(stub_ratio=0.4)  # 0.4 < 0.5
        assert check.above(fs, Signal.STUB_RATIO, 0.90) is False

    def test_absolute_tier_no_threshold_returns_false(self):
        """ABSOLUTE tier returns False when signal has no absolute threshold."""
        field = MockSignalField(tier="ABSOLUTE")
        check = ThresholdCheck(field)
        fs = MockFileSignals(pagerank=0.99)
        # PAGERANK has no absolute threshold in registry
        assert check.above(fs, Signal.PAGERANK, 0.90) is False


class TestThresholdCheckBelow:
    """Test below() method for high_is_good signals."""

    def test_full_tier_uses_percentile(self):
        """FULL tier uses percentile threshold for below check."""
        field = MockSignalField(tier="FULL")
        check = ThresholdCheck(field)
        fs = MockFileSignals(bus_factor=3.0, percentiles={"bus_factor": 0.15})
        # Percentile 0.15 < 0.20 threshold (bad bus factor)
        assert check.below(fs, Signal.BUS_FACTOR, 0.20) is True

    def test_full_tier_above_threshold(self):
        """FULL tier returns False when above threshold."""
        field = MockSignalField(tier="FULL")
        check = ThresholdCheck(field)
        fs = MockFileSignals(bus_factor=5.0, percentiles={"bus_factor": 0.80})
        # Percentile 0.80 > 0.20 threshold (good bus factor)
        assert check.below(fs, Signal.BUS_FACTOR, 0.20) is False

    def test_absolute_tier_uses_absolute_threshold(self):
        """ABSOLUTE tier uses absolute threshold for below check."""
        field = MockSignalField(tier="ABSOLUTE")
        check = ThresholdCheck(field)
        # BUS_FACTOR has absolute_threshold=1.0
        fs = MockFileSignals(bus_factor=0.8)  # 0.8 < 1.0 = bad
        assert check.below(fs, Signal.BUS_FACTOR, 0.20) is True

    def test_absolute_tier_above_absolute_threshold(self):
        """ABSOLUTE tier returns False when above absolute threshold."""
        field = MockSignalField(tier="ABSOLUTE")
        check = ThresholdCheck(field)
        fs = MockFileSignals(bus_factor=3.0)  # 3.0 > 1.0 = good
        assert check.below(fs, Signal.BUS_FACTOR, 0.20) is False


class TestMissingPercentile:
    """Test handling of missing percentile values."""

    def test_above_with_missing_percentile_defaults_to_zero(self):
        """Missing percentile defaults to 0 (below any threshold)."""
        field = MockSignalField(tier="FULL")
        check = ThresholdCheck(field)
        fs = MockFileSignals(percentiles={})  # No pagerank percentile
        assert check.above(fs, Signal.PAGERANK, 0.90) is False

    def test_below_with_missing_percentile_defaults_to_one(self):
        """Missing percentile defaults to 1.0 for below check (above any threshold)."""
        field = MockSignalField(tier="FULL")
        check = ThresholdCheck(field)
        fs = MockFileSignals(percentiles={})  # No bus_factor percentile
        assert check.below(fs, Signal.BUS_FACTOR, 0.20) is False


class TestIntegrationWithRegistry:
    """Test integration with signal registry."""

    def test_reads_absolute_threshold_from_registry(self):
        """ThresholdCheck reads absolute_threshold from registry."""
        field = MockSignalField(tier="ABSOLUTE")
        check = ThresholdCheck(field)
        # FIX_RATIO has absolute_threshold=0.4
        fs = MockFileSignals()
        fs.fix_ratio = 0.5  # > 0.4
        assert check.above(fs, Signal.FIX_RATIO, 0.90) is True

    def test_respects_signal_not_having_threshold(self):
        """Signals without absolute_threshold return False in ABSOLUTE tier."""
        field = MockSignalField(tier="ABSOLUTE")
        check = ThresholdCheck(field)
        fs = MockFileSignals()
        fs.betweenness = 0.99  # High value but no absolute threshold
        assert check.above(fs, Signal.BETWEENNESS, 0.90) is False
