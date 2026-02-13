"""Tests for cli/_signal_display.py - raw signal formatting utilities."""

from shannon_insight.cli._signal_display import (
    SIGNAL_CATEGORIES,
    SIGNAL_TO_CATEGORY,
    format_signal_value,
    format_signal_with_percentile,
    get_signal_label,
    interpret_signal,
)


class TestSignalValueFormatting:
    """Test format_signal_value function."""

    def test_format_none(self):
        """None values should return dash."""
        assert format_signal_value("any", None) == "—"

    def test_format_bool_true(self):
        """Boolean true should return 'yes'."""
        assert format_signal_value("is_orphan", True) == "yes"

    def test_format_bool_false(self):
        """Boolean false should return 'no'."""
        assert format_signal_value("is_orphan", False) == "no"

    def test_format_string(self):
        """String values should pass through."""
        assert format_signal_value("churn_trajectory", "CHURNING") == "CHURNING"

    def test_format_int(self):
        """Integers should be formatted with commas."""
        assert format_signal_value("lines", 1234) == "1,234"

    def test_format_pagerank(self):
        """PageRank should be formatted to 3 decimal places."""
        assert format_signal_value("pagerank", 0.12345) == "0.123"

    def test_format_ratio_as_percentage(self):
        """Ratio values should be formatted as percentages."""
        assert format_signal_value("stub_ratio", 0.5) == "50.0%"
        assert format_signal_value("fix_ratio", 0.333) == "33.3%"

    def test_format_cognitive_load(self):
        """Cognitive load should be formatted to 1 decimal place."""
        assert format_signal_value("cognitive_load", 12.567) == "12.6"

    def test_format_bus_factor(self):
        """Bus factor should show 'authors' suffix."""
        assert format_signal_value("bus_factor", 2.5) == "2.5 authors"


class TestSignalWithPercentile:
    """Test format_signal_with_percentile function."""

    def test_with_percentile(self):
        """Value with percentile should show both."""
        result = format_signal_with_percentile("pagerank", 0.5, 95.0)
        assert "0.500" in result
        assert "95th pctl" in result

    def test_without_percentile(self):
        """Value without percentile should show just value."""
        result = format_signal_with_percentile("lines", 100, None)
        assert "100" in result
        assert "pctl" not in result

    def test_bool_no_percentile(self):
        """Boolean values should never show percentile."""
        result = format_signal_with_percentile("is_orphan", True, 90.0)
        assert "yes" in result
        assert "pctl" not in result


class TestSignalLabels:
    """Test signal labeling."""

    def test_known_signal_label(self):
        """Known signals should have readable labels."""
        assert get_signal_label("pagerank") == "PageRank centrality"
        assert get_signal_label("blast_radius_size") == "Blast radius (files affected)"

    def test_unknown_signal_label(self):
        """Unknown signals should be title-cased."""
        assert get_signal_label("some_new_signal") == "Some New Signal"

    def test_all_categories_have_signals(self):
        """All categories should define signals."""
        for cat in SIGNAL_CATEGORIES:
            assert len(cat.signals) > 0, f"Category {cat.key} has no signals"


class TestSignalCategories:
    """Test signal categorization."""

    def test_signal_to_category_mapping(self):
        """Signals should map to their categories."""
        # Check some known mappings
        assert SIGNAL_TO_CATEGORY["pagerank"].key == "structure"
        assert SIGNAL_TO_CATEGORY["total_changes"].key == "temporal"
        assert SIGNAL_TO_CATEGORY["risk_score"].key == "risk"

    def test_category_structure(self):
        """Categories should have required fields."""
        for cat in SIGNAL_CATEGORIES:
            assert cat.key, "Category needs key"
            assert cat.name, "Category needs name"
            assert cat.icon, "Category needs icon"
            assert cat.description, "Category needs description"


class TestSignalInterpretation:
    """Test interpret_signal function."""

    def test_high_pagerank(self):
        """High PageRank should indicate central position."""
        interp = interpret_signal("pagerank", 0.15)
        assert "central" in interp.lower() or "depend" in interp.lower()

    def test_low_pagerank(self):
        """Low PageRank should indicate peripheral position."""
        interp = interpret_signal("pagerank", 0.01)
        assert "peripheral" in interp.lower()

    def test_high_churn_cv(self):
        """High churn CV should indicate variability."""
        interp = interpret_signal("churn_cv", 2.0)
        assert "variable" in interp.lower() or "spiky" in interp.lower()

    def test_unknown_signal(self):
        """Unknown signals should return empty string."""
        interp = interpret_signal("unknown_signal", 0.5)
        assert interp == ""

    def test_high_bus_factor(self):
        """High bus factor should indicate multiple contributors."""
        interp = interpret_signal("bus_factor", 4.0)
        assert "multiple" in interp.lower() or "contributors" in interp.lower()

    def test_low_bus_factor(self):
        """Low bus factor should indicate single contributor."""
        interp = interpret_signal("bus_factor", 1.0)
        assert "single" in interp.lower()
