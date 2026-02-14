"""Tests for ThresholdCheck — tier-aware threshold checking for finders.

Tests cover:
    - FULL tier: percentile-based above/below
    - BAYESIAN tier: percentile-based (same logic as FULL)
    - ABSOLUTE tier: registry absolute_threshold fallback
    - ABSOLUTE tier with no absolute_threshold defined
    - Raw value checks (tier-independent)
    - Hotspot median computation
    - Hotspot filtering helper
    - Edge cases: empty signal field, missing percentiles, missing attributes
"""

from __future__ import annotations

import pytest
from shannon_insight.infrastructure.thresholds import (
    ThresholdCheck,
    compute_hotspot_median,
    is_hotspot,
)
from shannon_insight.signals.models import FileSignals, SignalField
from shannon_insight.signals.registry_v2 import REGISTRY, Signal


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def full_field() -> SignalField:
    """SignalField with FULL tier and sample files."""
    return SignalField(tier="FULL")


@pytest.fixture
def bayesian_field() -> SignalField:
    """SignalField with BAYESIAN tier."""
    return SignalField(tier="BAYESIAN")


@pytest.fixture
def absolute_field() -> SignalField:
    """SignalField with ABSOLUTE tier (no percentiles)."""
    return SignalField(tier="ABSOLUTE")


def _make_fs(
    path: str = "src/main.py",
    pagerank: float = 0.01,
    cognitive_load: float = 5.0,
    bus_factor: float = 1.0,
    fix_ratio: float = 0.5,
    lines: int = 200,
    semantic_coherence: float = 0.3,
    total_changes: int = 10,
    function_count: int = 5,
    max_nesting: int = 3,
    churn_cv: float = 0.8,
    role: str = "LOGIC",
    percentiles: dict | None = None,
) -> FileSignals:
    """Create a FileSignals with common defaults for testing."""
    fs = FileSignals(
        path=path,
        pagerank=pagerank,
        cognitive_load=cognitive_load,
        bus_factor=bus_factor,
        fix_ratio=fix_ratio,
        lines=lines,
        semantic_coherence=semantic_coherence,
        total_changes=total_changes,
        function_count=function_count,
        max_nesting=max_nesting,
        churn_cv=churn_cv,
        role=role,
    )
    if percentiles is not None:
        fs.percentiles = percentiles
    return fs


# ── ThresholdCheck.above() Tests ──────────────────────────────────────


class TestAboveFull:
    """Test above() with FULL/BAYESIAN tiers (percentile-based)."""

    def test_above_threshold_returns_true(self, full_field: SignalField):
        """Percentile above threshold triggers."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"pagerank": 0.92})
        assert check.above(fs, Signal.PAGERANK, 0.90) is True

    def test_at_threshold_returns_false(self, full_field: SignalField):
        """Percentile exactly at threshold does NOT trigger (strictly above)."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"pagerank": 0.90})
        assert check.above(fs, Signal.PAGERANK, 0.90) is False

    def test_below_threshold_returns_false(self, full_field: SignalField):
        """Percentile below threshold does not trigger."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"pagerank": 0.50})
        assert check.above(fs, Signal.PAGERANK, 0.80) is False

    def test_missing_percentile_defaults_to_zero(self, full_field: SignalField):
        """Missing percentile key defaults to 0, so above() returns False."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={})  # No pagerank percentile
        assert check.above(fs, Signal.PAGERANK, 0.80) is False

    def test_bayesian_tier_uses_percentiles(self, bayesian_field: SignalField):
        """BAYESIAN tier uses same percentile logic as FULL."""
        check = ThresholdCheck(bayesian_field)
        fs = _make_fs(percentiles={"cognitive_load": 0.95})
        assert check.above(fs, Signal.COGNITIVE_LOAD, 0.80) is True


class TestAboveAbsolute:
    """Test above() with ABSOLUTE tier (no percentiles, uses registry)."""

    def test_above_absolute_threshold_returns_true(self, absolute_field: SignalField):
        """Raw value above registry absolute_threshold triggers."""
        check = ThresholdCheck(absolute_field)
        # LINES has absolute_threshold=500 in registry
        fs = _make_fs(lines=600)
        assert check.above(fs, Signal.LINES, 0.90) is True

    def test_below_absolute_threshold_returns_false(self, absolute_field: SignalField):
        """Raw value below registry absolute_threshold does not trigger."""
        check = ThresholdCheck(absolute_field)
        # LINES has absolute_threshold=500
        fs = _make_fs(lines=400)
        assert check.above(fs, Signal.LINES, 0.90) is False

    def test_at_absolute_threshold_returns_false(self, absolute_field: SignalField):
        """Raw value exactly at registry absolute_threshold does NOT trigger (strictly above)."""
        check = ThresholdCheck(absolute_field)
        # LINES has absolute_threshold=500
        fs = _make_fs(lines=500)
        assert check.above(fs, Signal.LINES, 0.90) is False

    def test_no_absolute_threshold_returns_false(self, absolute_field: SignalField):
        """Signal with no absolute_threshold in registry always returns False in ABSOLUTE tier."""
        check = ThresholdCheck(absolute_field)
        # PAGERANK has absolute_threshold=None in registry
        meta = REGISTRY.get(Signal.PAGERANK)
        assert meta is not None
        assert meta.absolute_threshold is None
        fs = _make_fs(pagerank=0.99)
        assert check.above(fs, Signal.PAGERANK, 0.50) is False

    def test_fix_ratio_absolute_threshold(self, absolute_field: SignalField):
        """FIX_RATIO has absolute_threshold=0.4 in registry."""
        check = ThresholdCheck(absolute_field)
        meta = REGISTRY.get(Signal.FIX_RATIO)
        assert meta is not None
        assert meta.absolute_threshold == 0.4
        fs = _make_fs(fix_ratio=0.5)
        assert check.above(fs, Signal.FIX_RATIO, 0.80) is True
        fs_low = _make_fs(fix_ratio=0.3)
        assert check.above(fs_low, Signal.FIX_RATIO, 0.80) is False

    def test_max_nesting_absolute_threshold(self, absolute_field: SignalField):
        """MAX_NESTING has absolute_threshold=4 in registry."""
        check = ThresholdCheck(absolute_field)
        meta = REGISTRY.get(Signal.MAX_NESTING)
        assert meta is not None
        assert meta.absolute_threshold == 4
        fs = _make_fs(max_nesting=5)
        assert check.above(fs, Signal.MAX_NESTING, 0.90) is True
        fs_low = _make_fs(max_nesting=3)
        assert check.above(fs_low, Signal.MAX_NESTING, 0.90) is False


# ── ThresholdCheck.below() Tests ──────────────────────────────────────


class TestBelowFull:
    """Test below() with FULL/BAYESIAN tiers (percentile-based)."""

    def test_below_threshold_returns_true(self, full_field: SignalField):
        """Percentile below threshold triggers for high-is-good signals."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"semantic_coherence": 0.15})
        assert check.below(fs, Signal.SEMANTIC_COHERENCE, 0.20) is True

    def test_at_threshold_returns_false(self, full_field: SignalField):
        """Percentile exactly at threshold does NOT trigger (strictly below)."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"bus_factor": 0.30})
        assert check.below(fs, Signal.BUS_FACTOR, 0.30) is False

    def test_above_threshold_returns_false(self, full_field: SignalField):
        """Percentile above threshold does not trigger for below()."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"bus_factor": 0.80})
        assert check.below(fs, Signal.BUS_FACTOR, 0.30) is False

    def test_missing_percentile_defaults_to_one(self, full_field: SignalField):
        """Missing percentile defaults to 1.0 for below(), so it returns False."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={})  # No bus_factor percentile
        assert check.below(fs, Signal.BUS_FACTOR, 0.30) is False

    def test_bayesian_below(self, bayesian_field: SignalField):
        """BAYESIAN tier uses same logic as FULL for below()."""
        check = ThresholdCheck(bayesian_field)
        fs = _make_fs(percentiles={"semantic_coherence": 0.10})
        assert check.below(fs, Signal.SEMANTIC_COHERENCE, 0.20) is True


class TestBelowAbsolute:
    """Test below() with ABSOLUTE tier."""

    def test_below_absolute_threshold_returns_true(self, absolute_field: SignalField):
        """Raw value below registry absolute_threshold triggers."""
        check = ThresholdCheck(absolute_field)
        # BUS_FACTOR has absolute_threshold=1.0
        meta = REGISTRY.get(Signal.BUS_FACTOR)
        assert meta is not None
        assert meta.absolute_threshold == 1.0
        fs = _make_fs(bus_factor=0.8)
        assert check.below(fs, Signal.BUS_FACTOR, 0.30) is True

    def test_above_absolute_threshold_returns_false(self, absolute_field: SignalField):
        """Raw value above registry absolute_threshold returns False for below()."""
        check = ThresholdCheck(absolute_field)
        # BUS_FACTOR has absolute_threshold=1.0
        fs = _make_fs(bus_factor=2.0)
        assert check.below(fs, Signal.BUS_FACTOR, 0.30) is False

    def test_no_absolute_threshold_returns_false(self, absolute_field: SignalField):
        """Signal without absolute_threshold returns False in ABSOLUTE tier for below()."""
        check = ThresholdCheck(absolute_field)
        # PAGERANK has absolute_threshold=None
        fs = _make_fs(pagerank=0.0001)
        assert check.below(fs, Signal.PAGERANK, 0.10) is False


# ── ThresholdCheck.above_raw() / below_raw() Tests ───────────────────


class TestRawChecks:
    """Test raw value checks (tier-independent)."""

    def test_above_raw_true(self, full_field: SignalField):
        """Raw value above fixed threshold returns True."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(fix_ratio=0.5)
        assert check.above_raw(fs, Signal.FIX_RATIO, 0.4) is True

    def test_above_raw_false(self, full_field: SignalField):
        """Raw value below fixed threshold returns False."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(fix_ratio=0.3)
        assert check.above_raw(fs, Signal.FIX_RATIO, 0.4) is False

    def test_above_raw_at_threshold(self, full_field: SignalField):
        """Raw value at threshold returns False (strictly above)."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(fix_ratio=0.4)
        assert check.above_raw(fs, Signal.FIX_RATIO, 0.4) is False

    def test_below_raw_true(self, full_field: SignalField):
        """Raw value below fixed threshold returns True."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(bus_factor=1.2)
        assert check.below_raw(fs, Signal.BUS_FACTOR, 1.5) is True

    def test_below_raw_false(self, full_field: SignalField):
        """Raw value above fixed threshold returns False."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(bus_factor=2.5)
        assert check.below_raw(fs, Signal.BUS_FACTOR, 1.5) is False

    def test_below_raw_at_threshold(self, full_field: SignalField):
        """Raw value at threshold returns False (strictly below)."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(bus_factor=1.5)
        assert check.below_raw(fs, Signal.BUS_FACTOR, 1.5) is False

    def test_raw_ignores_tier(self, absolute_field: SignalField):
        """Raw checks work the same regardless of tier."""
        check = ThresholdCheck(absolute_field)
        fs = _make_fs(fix_ratio=0.5)
        assert check.above_raw(fs, Signal.FIX_RATIO, 0.4) is True

    def test_raw_missing_attribute_defaults_to_zero(self, full_field: SignalField):
        """If signal attribute is missing from FileSignals, getattr returns 0."""
        check = ThresholdCheck(full_field)
        fs = _make_fs()
        # BROKEN_CALL_COUNT defaults to 0 on FileSignals
        assert check.above_raw(fs, Signal.BROKEN_CALL_COUNT, 0.0) is False


# ── Edge Cases ────────────────────────────────────────────────────────


class TestEdgeCases:
    """Test edge cases and defensive behavior."""

    def test_above_with_zero_percentile(self, full_field: SignalField):
        """Percentile of 0 never triggers above()."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"pagerank": 0.0})
        assert check.above(fs, Signal.PAGERANK, 0.0) is False  # 0 > 0 is False

    def test_below_with_one_percentile(self, full_field: SignalField):
        """Percentile of 1.0 never triggers below()."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(percentiles={"bus_factor": 1.0})
        assert check.below(fs, Signal.BUS_FACTOR, 1.0) is False

    def test_multiple_signals_on_same_filesignals(self, full_field: SignalField):
        """ThresholdCheck can check multiple signals on the same FileSignals."""
        check = ThresholdCheck(full_field)
        fs = _make_fs(
            percentiles={
                "pagerank": 0.95,
                "cognitive_load": 0.85,
                "bus_factor": 0.10,
            }
        )
        assert check.above(fs, Signal.PAGERANK, 0.90) is True
        assert check.above(fs, Signal.COGNITIVE_LOAD, 0.80) is True
        assert check.below(fs, Signal.BUS_FACTOR, 0.20) is True

    def test_absolute_tier_consistent_with_registry(self, absolute_field: SignalField):
        """All signals with absolute_threshold in registry should work."""
        check = ThresholdCheck(absolute_field)
        # Test several signals that have absolute thresholds
        signals_with_thresholds = {
            s: m for s, m in REGISTRY.items()
            if m.absolute_threshold is not None and m.scope == "file"
        }
        assert len(signals_with_thresholds) > 0, "Registry should have signals with absolute thresholds"

        # Every signal with an absolute threshold should be evaluable
        for signal, _meta in signals_with_thresholds.items():
            fs = _make_fs()
            # Should not raise
            check.above(fs, signal, 0.90)
            check.below(fs, signal, 0.10)


# ── compute_hotspot_median() Tests ────────────────────────────────────


class TestComputeHotspotMedian:
    """Test hotspot median computation."""

    def test_odd_count(self):
        """Odd number of active files: median is the middle value."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "a.py": _make_fs(path="a.py", total_changes=5),
            "b.py": _make_fs(path="b.py", total_changes=10),
            "c.py": _make_fs(path="c.py", total_changes=20),
        }
        median = compute_hotspot_median(field)
        assert median == 10

    def test_even_count_uses_lower_median(self):
        """Even number of active files: uses lower median (conservative)."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "a.py": _make_fs(path="a.py", total_changes=5),
            "b.py": _make_fs(path="b.py", total_changes=10),
            "c.py": _make_fs(path="c.py", total_changes=20),
            "d.py": _make_fs(path="d.py", total_changes=30),
        }
        # Sorted: [5, 10, 20, 30], n=4, lower median = changes[1] = 10
        median = compute_hotspot_median(field)
        assert median == 10

    def test_excludes_zero_change_files(self):
        """Files with total_changes=0 are excluded from median."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "zero.py": _make_fs(path="zero.py", total_changes=0),
            "a.py": _make_fs(path="a.py", total_changes=5),
            "b.py": _make_fs(path="b.py", total_changes=15),
            "c.py": _make_fs(path="c.py", total_changes=25),
        }
        # Only [5, 15, 25] (n=3), median = 15
        median = compute_hotspot_median(field)
        assert median == 15

    def test_excludes_test_files(self):
        """Files with role=TEST are excluded from median."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "test_a.py": _make_fs(path="test_a.py", total_changes=100, role="TEST"),
            "a.py": _make_fs(path="a.py", total_changes=5),
            "b.py": _make_fs(path="b.py", total_changes=10),
            "c.py": _make_fs(path="c.py", total_changes=20),
        }
        # Only non-TEST with changes>0: [5, 10, 20], median = 10
        median = compute_hotspot_median(field)
        assert median == 10

    def test_all_zero_changes_returns_zero(self):
        """All files have 0 changes: median is 0."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "a.py": _make_fs(path="a.py", total_changes=0),
            "b.py": _make_fs(path="b.py", total_changes=0),
        }
        median = compute_hotspot_median(field)
        assert median == 0

    def test_empty_signal_field_returns_zero(self):
        """Empty per_file dict: median is 0."""
        field = SignalField(tier="FULL")
        median = compute_hotspot_median(field)
        assert median == 0

    def test_single_active_file(self):
        """Single active file: median is that file's changes."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "only.py": _make_fs(path="only.py", total_changes=42),
        }
        median = compute_hotspot_median(field)
        assert median == 42

    def test_all_test_files_returns_zero(self):
        """All files are TEST role: median is 0."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "test_a.py": _make_fs(path="test_a.py", total_changes=50, role="TEST"),
            "test_b.py": _make_fs(path="test_b.py", total_changes=30, role="TEST"),
        }
        median = compute_hotspot_median(field)
        assert median == 0


# ── is_hotspot() Tests ────────────────────────────────────────────────


class TestIsHotspot:
    """Test hotspot filter helper."""

    def test_above_median_is_hotspot(self):
        """File with total_changes > median is a hotspot."""
        fs = _make_fs(total_changes=20)
        assert is_hotspot(fs, median_changes=10) is True

    def test_at_median_is_not_hotspot(self):
        """File with total_changes = median is NOT a hotspot (strictly above)."""
        fs = _make_fs(total_changes=10)
        assert is_hotspot(fs, median_changes=10) is False

    def test_below_median_is_not_hotspot(self):
        """File with total_changes < median is not a hotspot."""
        fs = _make_fs(total_changes=5)
        assert is_hotspot(fs, median_changes=10) is False

    def test_zero_median_allows_any_active_file(self):
        """When median is 0, any file with changes > 0 is a hotspot."""
        fs = _make_fs(total_changes=1)
        assert is_hotspot(fs, median_changes=0) is True

    def test_zero_changes_never_hotspot(self):
        """File with 0 changes is never a hotspot, even with median=0."""
        fs = _make_fs(total_changes=0)
        assert is_hotspot(fs, median_changes=0) is False


# ── Integration-Style Tests ───────────────────────────────────────────


class TestThresholdIntegration:
    """Test typical finder-like usage patterns."""

    def test_bug_attractor_pattern(self):
        """Simulate BugAttractorFinder's threshold checks."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "risky.py": _make_fs(
                path="risky.py",
                fix_ratio=0.5,
                pagerank=0.01,
                total_changes=50,
                percentiles={"pagerank": 0.85, "fix_ratio": 0.90},
            ),
            "safe.py": _make_fs(
                path="safe.py",
                fix_ratio=0.1,
                pagerank=0.001,
                total_changes=5,
                percentiles={"pagerank": 0.30, "fix_ratio": 0.20},
            ),
        }
        check = ThresholdCheck(field)
        median = compute_hotspot_median(field)

        # risky.py should trigger
        risky = field.per_file["risky.py"]
        assert is_hotspot(risky, median)
        assert check.above_raw(risky, Signal.FIX_RATIO, 0.4)
        assert check.above(risky, Signal.PAGERANK, 0.80)

        # safe.py should not trigger
        safe = field.per_file["safe.py"]
        assert not check.above_raw(safe, Signal.FIX_RATIO, 0.4)
        assert not check.above(safe, Signal.PAGERANK, 0.80)

    def test_god_file_pattern(self):
        """Simulate GodFileFinder's threshold checks (high-is-bad + high-is-good)."""
        field = SignalField(tier="FULL")
        field.per_file = {
            "god.py": _make_fs(
                path="god.py",
                cognitive_load=15.0,
                semantic_coherence=0.1,
                function_count=20,
                total_changes=30,
                percentiles={
                    "cognitive_load": 0.92,
                    "semantic_coherence": 0.15,
                },
            ),
        }
        check = ThresholdCheck(field)

        god = field.per_file["god.py"]
        # High complexity (above 80th percentile)
        assert check.above(god, Signal.COGNITIVE_LOAD, 0.80)
        # Low coherence (below 30th percentile)
        assert check.below(god, Signal.SEMANTIC_COHERENCE, 0.30)

    def test_knowledge_silo_pattern_absolute_tier(self):
        """Knowledge silo detection in ABSOLUTE tier falls back to registry."""
        field = SignalField(tier="ABSOLUTE")
        field.per_file = {
            "silo.py": _make_fs(
                path="silo.py",
                bus_factor=0.8,
                pagerank=0.01,
            ),
        }
        check = ThresholdCheck(field)

        silo = field.per_file["silo.py"]
        # BUS_FACTOR has absolute_threshold=1.0 in registry
        # bus_factor=0.8 < 1.0 -> below() should return True
        assert check.below(silo, Signal.BUS_FACTOR, 0.30)
        # PAGERANK has absolute_threshold=None -> above() returns False
        assert not check.above(silo, Signal.PAGERANK, 0.80)

    def test_all_three_tiers_produce_results(self):
        """Verify threshold checks work across all three tiers."""
        for tier in ("FULL", "BAYESIAN", "ABSOLUTE"):
            field = SignalField(tier=tier)
            check = ThresholdCheck(field)

            fs = _make_fs(
                lines=600,  # Above LINES absolute_threshold=500
                fix_ratio=0.5,  # Above FIX_RATIO absolute_threshold=0.4
                percentiles={
                    "lines": 0.95,
                    "fix_ratio": 0.92,
                },
            )

            if tier == "ABSOLUTE":
                # Uses registry thresholds
                assert check.above(fs, Signal.LINES, 0.90) is True
                assert check.above(fs, Signal.FIX_RATIO, 0.80) is True
            else:
                # Uses percentiles
                assert check.above(fs, Signal.LINES, 0.90) is True
                assert check.above(fs, Signal.FIX_RATIO, 0.80) is True
