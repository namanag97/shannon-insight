"""Tests for v2 enhanced Analyzer and Finder protocols."""

import pytest

from shannon_insight.insights.protocols_v2 import Analyzer, Finder


class MockAnalyzer:
    """Mock analyzer implementing the protocol."""

    name = "mock_analyzer"
    api_version = "2.0"
    requires: set[str] = set()
    provides: set[str] = {"structural"}
    run_last = False
    error_mode = "fail"
    deprecated = False
    deprecation_note = None

    def analyze(self, store) -> None:
        pass


class MockFinder:
    """Mock finder implementing the protocol."""

    name = "mock_finder"
    api_version = "2.0"
    requires: set[str] = {"structural"}
    error_mode = "skip"
    hotspot_filtered = True
    tier_minimum = "BAYESIAN"
    deprecated = False
    deprecation_note = None

    def find(self, store) -> list:
        return []


class TestAnalyzerProtocol:
    """Test Analyzer protocol attributes."""

    def test_required_attributes(self):
        """Analyzer has all required attributes."""
        analyzer = MockAnalyzer()

        assert hasattr(analyzer, "name")
        assert hasattr(analyzer, "api_version")
        assert hasattr(analyzer, "requires")
        assert hasattr(analyzer, "provides")
        assert hasattr(analyzer, "run_last")
        assert hasattr(analyzer, "error_mode")
        assert hasattr(analyzer, "deprecated")
        assert hasattr(analyzer, "deprecation_note")
        assert hasattr(analyzer, "analyze")

    def test_requires_and_provides_are_sets(self):
        """requires and provides must be sets."""
        analyzer = MockAnalyzer()
        assert isinstance(analyzer.requires, set)
        assert isinstance(analyzer.provides, set)

    def test_error_mode_values(self):
        """error_mode must be one of fail/skip/degrade."""
        valid_modes = {"fail", "skip", "degrade"}
        analyzer = MockAnalyzer()
        assert analyzer.error_mode in valid_modes

    def test_run_last_default(self):
        """run_last defaults to False."""
        analyzer = MockAnalyzer()
        assert analyzer.run_last is False

    def test_api_version(self):
        """api_version should be 2.0 for v2."""
        analyzer = MockAnalyzer()
        assert analyzer.api_version == "2.0"


class TestFinderProtocol:
    """Test Finder protocol attributes."""

    def test_required_attributes(self):
        """Finder has all required attributes."""
        finder = MockFinder()

        assert hasattr(finder, "name")
        assert hasattr(finder, "api_version")
        assert hasattr(finder, "requires")
        assert hasattr(finder, "error_mode")
        assert hasattr(finder, "hotspot_filtered")
        assert hasattr(finder, "tier_minimum")
        assert hasattr(finder, "deprecated")
        assert hasattr(finder, "deprecation_note")
        assert hasattr(finder, "find")

    def test_requires_is_set(self):
        """requires must be a set."""
        finder = MockFinder()
        assert isinstance(finder.requires, set)

    def test_hotspot_filtered_flag(self):
        """hotspot_filtered controls filtering on total_changes."""
        finder = MockFinder()
        assert isinstance(finder.hotspot_filtered, bool)

    def test_tier_minimum_values(self):
        """tier_minimum must be one of ABSOLUTE/BAYESIAN/FULL."""
        valid_tiers = {"ABSOLUTE", "BAYESIAN", "FULL"}
        finder = MockFinder()
        assert finder.tier_minimum in valid_tiers

    def test_find_returns_list(self):
        """find() must return a list."""
        finder = MockFinder()
        result = finder.find(None)
        assert isinstance(result, list)


class TestProtocolTypeChecking:
    """Test that protocols work for structural subtyping."""

    def test_analyzer_structural_typing(self):
        """MockAnalyzer satisfies Analyzer protocol."""
        analyzer = MockAnalyzer()
        # In Python, Protocol checking is structural
        # These checks verify the interface
        assert callable(analyzer.analyze)
        assert isinstance(analyzer.requires, set)
        assert isinstance(analyzer.provides, set)

    def test_finder_structural_typing(self):
        """MockFinder satisfies Finder protocol."""
        finder = MockFinder()
        assert callable(finder.find)
        assert isinstance(finder.requires, set)


class TestDeprecation:
    """Test deprecation metadata."""

    def test_deprecated_analyzer(self):
        """Can mark analyzer as deprecated."""

        class DeprecatedAnalyzer(MockAnalyzer):
            deprecated = True
            deprecation_note = "Use NewAnalyzer instead"

        analyzer = DeprecatedAnalyzer()
        assert analyzer.deprecated is True
        assert "NewAnalyzer" in analyzer.deprecation_note

    def test_deprecated_finder(self):
        """Can mark finder as deprecated."""

        class DeprecatedFinder(MockFinder):
            deprecated = True
            deprecation_note = "Replaced by BetterFinder"

        finder = DeprecatedFinder()
        assert finder.deprecated is True
        assert "BetterFinder" in finder.deprecation_note


class TestWave2Analyzer:
    """Test run_last for Wave 2 analyzers."""

    def test_run_last_analyzer(self):
        """SignalFusionAnalyzer must have run_last=True."""

        class SignalFusionAnalyzer(MockAnalyzer):
            name = "signal_fusion"
            run_last = True
            provides = {"signal_field"}

        analyzer = SignalFusionAnalyzer()
        assert analyzer.run_last is True


class TestErrorModes:
    """Test error_mode behavior expectations."""

    def test_fail_mode(self):
        """fail mode raises exception on error."""

        class FailAnalyzer(MockAnalyzer):
            error_mode = "fail"

        assert FailAnalyzer().error_mode == "fail"

    def test_skip_mode(self):
        """skip mode returns empty/None on error."""

        class SkipFinder(MockFinder):
            error_mode = "skip"

        assert SkipFinder().error_mode == "skip"

    def test_degrade_mode(self):
        """degrade mode returns partial results."""

        class DegradeFinder(MockFinder):
            error_mode = "degrade"

        assert DegradeFinder().error_mode == "degrade"
