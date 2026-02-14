"""Tests for the Signal enum and registry (infrastructure/signals.py).

Validates the single source of truth for all 62 signals:
- Enum completeness and value uniqueness
- Registry completeness and metadata correctness
- Collision detection (single-owner rule)
- Helper function correctness
- Polarity, scope, and phase invariants
- Cross-reference with known signal properties from registry/signals.md
"""

from __future__ import annotations

import pytest

from shannon_insight.infrastructure.signals import (
    REGISTRY,
    Signal,
    SignalMeta,
    get_signal_meta,
    percentileable_signals,
    register,
    signals_by_phase,
    signals_by_polarity,
    signals_by_scope,
)


# ---------------------------------------------------------------------------
# Enum completeness
# ---------------------------------------------------------------------------


class TestSignalEnum:
    """Tests for the Signal enum itself."""

    def test_total_signal_count(self) -> None:
        """There are exactly 62 signals in the enum."""
        assert len(Signal) == 62

    def test_all_values_are_strings(self) -> None:
        """Every Signal value is a non-empty string."""
        for signal in Signal:
            assert isinstance(signal.value, str)
            assert len(signal.value) > 0

    def test_values_are_unique(self) -> None:
        """No two Signal members share the same string value."""
        values = [s.value for s in Signal]
        assert len(values) == len(set(values)), (
            f"Duplicate values found: "
            f"{[v for v in values if values.count(v) > 1]}"
        )

    def test_values_are_snake_case(self) -> None:
        """All signal values use snake_case (lowercase, underscores)."""
        for signal in Signal:
            assert signal.value == signal.value.lower(), (
                f"{signal.name} has non-lowercase value '{signal.value}'"
            )
            assert " " not in signal.value, (
                f"{signal.name} has spaces in value '{signal.value}'"
            )

    def test_names_are_uppercase(self) -> None:
        """All Signal member names are UPPER_CASE."""
        for signal in Signal:
            assert signal.name == signal.name.upper(), (
                f"Signal name '{signal.name}' is not UPPER_CASE"
            )

    def test_known_ir1_signals_exist(self) -> None:
        """IR1 (syntactic scanning) signals are present."""
        ir1 = {
            Signal.LINES, Signal.FUNCTION_COUNT, Signal.CLASS_COUNT,
            Signal.MAX_NESTING, Signal.IMPL_GINI, Signal.STUB_RATIO,
            Signal.IMPORT_COUNT,
        }
        assert len(ir1) == 7

    def test_known_ir2_signals_exist(self) -> None:
        """IR2 (semantic) signals are present."""
        ir2 = {
            Signal.ROLE, Signal.CONCEPT_COUNT, Signal.CONCEPT_ENTROPY,
            Signal.NAMING_DRIFT, Signal.TODO_DENSITY, Signal.DOCSTRING_COVERAGE,
        }
        assert len(ir2) == 6

    def test_known_ir3_signals_exist(self) -> None:
        """IR3 (graph) signals are present."""
        ir3 = {
            Signal.PAGERANK, Signal.BETWEENNESS, Signal.IN_DEGREE,
            Signal.OUT_DEGREE, Signal.BLAST_RADIUS_SIZE, Signal.DEPTH,
            Signal.IS_ORPHAN, Signal.PHANTOM_IMPORT_COUNT,
            Signal.BROKEN_CALL_COUNT, Signal.COMMUNITY,
            Signal.COMPRESSION_RATIO, Signal.SEMANTIC_COHERENCE,
            Signal.COGNITIVE_LOAD,
        }
        assert len(ir3) == 13

    def test_known_temporal_signals_exist(self) -> None:
        """IR5t (temporal) signals are present."""
        temporal = {
            Signal.TOTAL_CHANGES, Signal.CHURN_TRAJECTORY, Signal.CHURN_SLOPE,
            Signal.CHURN_CV, Signal.BUS_FACTOR, Signal.AUTHOR_ENTROPY,
            Signal.FIX_RATIO, Signal.REFACTOR_RATIO,
        }
        assert len(temporal) == 8

    def test_known_composite_signals_exist(self) -> None:
        """Per-file composite signals are present."""
        composites = {Signal.RISK_SCORE, Signal.WIRING_QUALITY}
        assert len(composites) == 2

    def test_known_module_signals_exist(self) -> None:
        """Per-module signals are present."""
        module = {
            Signal.COHESION, Signal.COUPLING, Signal.INSTABILITY,
            Signal.ABSTRACTNESS, Signal.MAIN_SEQ_DISTANCE,
            Signal.BOUNDARY_ALIGNMENT, Signal.LAYER_VIOLATION_COUNT,
            Signal.ROLE_CONSISTENCY, Signal.VELOCITY,
            Signal.COORDINATION_COST, Signal.KNOWLEDGE_GINI,
            Signal.MODULE_BUS_FACTOR, Signal.MEAN_COGNITIVE_LOAD,
            Signal.FILE_COUNT, Signal.HEALTH_SCORE,
        }
        assert len(module) == 15

    def test_known_global_signals_exist(self) -> None:
        """Global signals are present."""
        global_sigs = {
            Signal.MODULARITY, Signal.FIEDLER_VALUE, Signal.SPECTRAL_GAP,
            Signal.CYCLE_COUNT, Signal.CENTRALITY_GINI, Signal.ORPHAN_RATIO,
            Signal.PHANTOM_RATIO, Signal.GLUE_DEFICIT, Signal.WIRING_SCORE,
            Signal.ARCHITECTURE_HEALTH, Signal.CODEBASE_HEALTH,
        }
        assert len(global_sigs) == 11

    def test_signal_scope_counts_add_up(self) -> None:
        """36 file + 15 module + 11 global = 62 total."""
        # 7 IR1 + 6 IR2 + 13 IR3 + 8 IR5t + 2 composites = 36 file
        # 15 module + 11 global = 26
        # 36 + 26 = 62
        assert len(Signal) == 62


# ---------------------------------------------------------------------------
# Registry completeness
# ---------------------------------------------------------------------------


class TestRegistry:
    """Tests for the REGISTRY dict and registration."""

    def test_all_signals_registered(self) -> None:
        """Every Signal enum member has a corresponding entry in REGISTRY."""
        for signal in Signal:
            assert signal in REGISTRY, (
                f"Signal '{signal.value}' is not registered in REGISTRY"
            )

    def test_registry_count(self) -> None:
        """REGISTRY has exactly 62 entries."""
        assert len(REGISTRY) == 62

    def test_no_extra_entries(self) -> None:
        """REGISTRY has no entries that aren't Signal enum members."""
        for key in REGISTRY:
            assert isinstance(key, Signal)

    def test_signal_meta_signal_matches_key(self) -> None:
        """Every SignalMeta.signal matches its key in REGISTRY."""
        for signal, meta in REGISTRY.items():
            assert meta.signal is signal, (
                f"REGISTRY key {signal} has meta.signal={meta.signal}"
            )


# ---------------------------------------------------------------------------
# SignalMeta invariants
# ---------------------------------------------------------------------------


class TestSignalMeta:
    """Tests for SignalMeta dataclass invariants."""

    def test_all_scopes_valid(self) -> None:
        """Every signal has a valid scope."""
        valid_scopes = {"file", "module", "global"}
        for signal, meta in REGISTRY.items():
            assert meta.scope in valid_scopes, (
                f"{signal.value} has invalid scope '{meta.scope}'"
            )

    def test_all_polarities_valid(self) -> None:
        """Every signal has a valid polarity."""
        valid_polarities = {"high_is_bad", "high_is_good", "neutral"}
        for signal, meta in REGISTRY.items():
            assert meta.polarity in valid_polarities, (
                f"{signal.value} has invalid polarity '{meta.polarity}'"
            )

    def test_all_phases_in_range(self) -> None:
        """Every signal has a phase between 0 and 5."""
        for signal, meta in REGISTRY.items():
            assert 0 <= meta.phase <= 5, (
                f"{signal.value} has phase {meta.phase}, expected 0-5"
            )

    def test_all_dtypes_are_types(self) -> None:
        """Every signal has a valid Python type for dtype."""
        valid_types = {int, float, str, bool}
        for signal, meta in REGISTRY.items():
            assert meta.dtype in valid_types, (
                f"{signal.value} has dtype={meta.dtype}, expected one of {valid_types}"
            )

    def test_absolute_threshold_type(self) -> None:
        """absolute_threshold is either None or a numeric value."""
        for signal, meta in REGISTRY.items():
            if meta.absolute_threshold is not None:
                assert isinstance(meta.absolute_threshold, (int, float)), (
                    f"{signal.value} has non-numeric threshold "
                    f"{meta.absolute_threshold}"
                )

    def test_produced_by_is_nonempty(self) -> None:
        """Every signal has a non-empty produced_by string."""
        for signal, meta in REGISTRY.items():
            assert len(meta.produced_by) > 0, (
                f"{signal.value} has empty produced_by"
            )

    def test_frozen_dataclass(self) -> None:
        """SignalMeta instances are immutable."""
        meta = REGISTRY[Signal.PAGERANK]
        with pytest.raises(AttributeError):
            meta.polarity = "neutral"  # type: ignore[misc]

    def test_invalid_scope_rejected(self) -> None:
        """SignalMeta rejects invalid scope at construction."""
        with pytest.raises(ValueError, match="Invalid scope"):
            SignalMeta(
                signal=Signal.LINES,
                dtype=int,
                scope="invalid",
                percentileable=True,
                polarity="high_is_bad",
                absolute_threshold=None,
                produced_by="test",
                phase=0,
            )

    def test_invalid_polarity_rejected(self) -> None:
        """SignalMeta rejects invalid polarity at construction."""
        with pytest.raises(ValueError, match="Invalid polarity"):
            SignalMeta(
                signal=Signal.LINES,
                dtype=int,
                scope="file",
                percentileable=True,
                polarity="bad",
                absolute_threshold=None,
                produced_by="test",
                phase=0,
            )

    def test_invalid_phase_rejected(self) -> None:
        """SignalMeta rejects out-of-range phase at construction."""
        with pytest.raises(ValueError, match="Invalid phase"):
            SignalMeta(
                signal=Signal.LINES,
                dtype=int,
                scope="file",
                percentileable=True,
                polarity="high_is_bad",
                absolute_threshold=None,
                produced_by="test",
                phase=6,
            )


# ---------------------------------------------------------------------------
# Collision detection (single-owner rule)
# ---------------------------------------------------------------------------


class TestCollisionDetection:
    """Tests for the register() function's single-owner enforcement."""

    def test_duplicate_same_producer_is_idempotent(self) -> None:
        """Re-registering a signal from the same producer is silently accepted."""
        original_meta = REGISTRY[Signal.PAGERANK]
        # Should not raise
        register(original_meta)
        assert REGISTRY[Signal.PAGERANK] is original_meta

    def test_duplicate_different_producer_raises(self) -> None:
        """Registering a signal from a different producer raises ValueError."""
        conflicting = SignalMeta(
            signal=Signal.PAGERANK,
            dtype=float,
            scope="file",
            percentileable=True,
            polarity="high_is_bad",
            absolute_threshold=None,
            produced_by="some_other_module",
            phase=0,
        )
        with pytest.raises(ValueError, match="already registered"):
            register(conflicting)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    """Tests for get_signal_meta, percentileable_signals, etc."""

    def test_get_signal_meta_returns_correct_meta(self) -> None:
        """get_signal_meta returns the correct SignalMeta for a known signal."""
        meta = get_signal_meta(Signal.PAGERANK)
        assert meta.signal is Signal.PAGERANK
        assert meta.dtype is float
        assert meta.scope == "file"
        assert meta.percentileable is True
        assert meta.polarity == "high_is_bad"
        assert meta.produced_by == "graph/algorithms"
        assert meta.phase == 0

    def test_get_signal_meta_all_signals(self) -> None:
        """get_signal_meta works for every registered signal."""
        for signal in Signal:
            meta = get_signal_meta(signal)
            assert meta.signal is signal

    def test_percentileable_signals_excludes_enums(self) -> None:
        """Enum-typed signals (role, churn_trajectory) are not percentileable."""
        pctl = percentileable_signals()
        assert Signal.ROLE not in pctl
        assert Signal.CHURN_TRAJECTORY not in pctl

    def test_percentileable_signals_excludes_bools(self) -> None:
        """Boolean signals (is_orphan) are not percentileable."""
        pctl = percentileable_signals()
        assert Signal.IS_ORPHAN not in pctl

    def test_percentileable_signals_excludes_community(self) -> None:
        """Assignment ID signals (community) are not percentileable."""
        pctl = percentileable_signals()
        assert Signal.COMMUNITY not in pctl

    def test_percentileable_signals_excludes_composites(self) -> None:
        """Per-file composites are not percentileable (already normalized)."""
        pctl = percentileable_signals()
        assert Signal.RISK_SCORE not in pctl
        assert Signal.WIRING_QUALITY not in pctl

    def test_percentileable_signals_excludes_global(self) -> None:
        """Global signals (single values) are not percentileable."""
        pctl = percentileable_signals()
        global_signals = signals_by_scope("global")
        for sig in global_signals:
            assert sig not in pctl, (
                f"Global signal {sig.value} should not be percentileable"
            )

    def test_percentileable_signals_excludes_module_composites(self) -> None:
        """Module composite (health_score) is not percentileable."""
        pctl = percentileable_signals()
        assert Signal.HEALTH_SCORE not in pctl

    def test_percentileable_signals_excludes_depth(self) -> None:
        """depth (-1 sentinel) is not percentileable."""
        pctl = percentileable_signals()
        assert Signal.DEPTH not in pctl

    def test_percentileable_signals_includes_numeric_file_signals(self) -> None:
        """Standard numeric file signals are percentileable."""
        pctl = percentileable_signals()
        expected_pctl = {
            Signal.LINES, Signal.FUNCTION_COUNT, Signal.CLASS_COUNT,
            Signal.MAX_NESTING, Signal.IMPL_GINI, Signal.STUB_RATIO,
            Signal.IMPORT_COUNT, Signal.CONCEPT_COUNT, Signal.CONCEPT_ENTROPY,
            Signal.NAMING_DRIFT, Signal.TODO_DENSITY, Signal.DOCSTRING_COVERAGE,
            Signal.PAGERANK, Signal.BETWEENNESS, Signal.IN_DEGREE,
            Signal.OUT_DEGREE, Signal.BLAST_RADIUS_SIZE,
            Signal.PHANTOM_IMPORT_COUNT, Signal.BROKEN_CALL_COUNT,
            Signal.COMPRESSION_RATIO, Signal.SEMANTIC_COHERENCE,
            Signal.COGNITIVE_LOAD, Signal.TOTAL_CHANGES, Signal.CHURN_SLOPE,
            Signal.CHURN_CV, Signal.BUS_FACTOR, Signal.AUTHOR_ENTROPY,
            Signal.FIX_RATIO, Signal.REFACTOR_RATIO,
        }
        for sig in expected_pctl:
            assert sig in pctl, (
                f"Signal {sig.value} should be percentileable"
            )

    def test_percentileable_signals_includes_module_metrics(self) -> None:
        """Module-level Martin metrics and aggregates are percentileable."""
        pctl = percentileable_signals()
        expected = {
            Signal.COHESION, Signal.COUPLING, Signal.INSTABILITY,
            Signal.ABSTRACTNESS, Signal.MAIN_SEQ_DISTANCE,
            Signal.BOUNDARY_ALIGNMENT, Signal.LAYER_VIOLATION_COUNT,
            Signal.ROLE_CONSISTENCY, Signal.VELOCITY,
            Signal.COORDINATION_COST, Signal.KNOWLEDGE_GINI,
            Signal.MODULE_BUS_FACTOR, Signal.MEAN_COGNITIVE_LOAD,
            Signal.FILE_COUNT,
        }
        for sig in expected:
            assert sig in pctl, (
                f"Module signal {sig.value} should be percentileable"
            )

    def test_signals_by_phase_0(self) -> None:
        """Phase 0 includes scanning + graph basics + global graph metrics."""
        phase0 = signals_by_phase(0)
        expected_in_phase0 = {
            Signal.LINES, Signal.FUNCTION_COUNT, Signal.CLASS_COUNT,
            Signal.IMPORT_COUNT, Signal.PAGERANK, Signal.BETWEENNESS,
            Signal.IN_DEGREE, Signal.OUT_DEGREE, Signal.BLAST_RADIUS_SIZE,
            Signal.COMMUNITY, Signal.COMPRESSION_RATIO,
            Signal.MODULARITY, Signal.FIEDLER_VALUE, Signal.SPECTRAL_GAP,
            Signal.CYCLE_COUNT,
        }
        for sig in expected_in_phase0:
            assert sig in phase0, (
                f"Signal {sig.value} should be in phase 0"
            )

    def test_signals_by_phase_5_is_all(self) -> None:
        """Phase 5 includes all 62 signals."""
        phase5 = signals_by_phase(5)
        assert phase5 == set(Signal)

    def test_signals_by_phase_monotonic(self) -> None:
        """Each phase is a superset of the previous phase."""
        prev = set()
        for p in range(6):
            current = signals_by_phase(p)
            assert prev.issubset(current), (
                f"Phase {p} is not a superset of phase {p-1}: "
                f"missing {prev - current}"
            )
            prev = current

    def test_signals_by_scope_file(self) -> None:
        """File-scope signals include the expected count."""
        file_signals = signals_by_scope("file")
        assert len(file_signals) == 36

    def test_signals_by_scope_module(self) -> None:
        """Module-scope signals include the expected count."""
        module_signals = signals_by_scope("module")
        assert len(module_signals) == 15

    def test_signals_by_scope_global(self) -> None:
        """Global-scope signals include the expected count."""
        global_signals = signals_by_scope("global")
        assert len(global_signals) == 11

    def test_signals_by_scope_covers_all(self) -> None:
        """File + module + global = all 62 signals."""
        file_s = signals_by_scope("file")
        module_s = signals_by_scope("module")
        global_s = signals_by_scope("global")
        assert file_s | module_s | global_s == set(Signal)
        # No overlaps
        assert len(file_s) + len(module_s) + len(global_s) == 62

    def test_signals_by_polarity_coverage(self) -> None:
        """Every signal has exactly one polarity that is accounted for."""
        bad = signals_by_polarity("high_is_bad")
        good = signals_by_polarity("high_is_good")
        neutral = signals_by_polarity("neutral")
        assert bad | good | neutral == set(Signal)
        assert len(bad) + len(good) + len(neutral) == 62


# ---------------------------------------------------------------------------
# Specific signal metadata verification (cross-reference with signals.md)
# ---------------------------------------------------------------------------


class TestSpecificSignalMetadata:
    """Spot-check specific signals against the spec in signals.md."""

    def test_lines_metadata(self) -> None:
        """Signal #1: lines."""
        m = get_signal_meta(Signal.LINES)
        assert m.dtype is int
        assert m.scope == "file"
        assert m.percentileable is True
        assert m.polarity == "high_is_bad"
        assert m.absolute_threshold == 500.0
        assert m.phase == 0

    def test_role_metadata(self) -> None:
        """Signal #8: role (enum, not percentileable)."""
        m = get_signal_meta(Signal.ROLE)
        assert m.dtype is str
        assert m.scope == "file"
        assert m.percentileable is False
        assert m.polarity == "neutral"
        assert m.absolute_threshold is None
        assert m.phase == 2

    def test_pagerank_metadata(self) -> None:
        """Signal #14: pagerank."""
        m = get_signal_meta(Signal.PAGERANK)
        assert m.dtype is float
        assert m.scope == "file"
        assert m.percentileable is True
        assert m.polarity == "high_is_bad"
        assert m.phase == 0

    def test_is_orphan_metadata(self) -> None:
        """Signal #20: is_orphan (bool, not percentileable)."""
        m = get_signal_meta(Signal.IS_ORPHAN)
        assert m.dtype is bool
        assert m.scope == "file"
        assert m.percentileable is False
        assert m.polarity == "high_is_bad"
        assert m.phase == 3

    def test_community_metadata(self) -> None:
        """Signal #23: community (assignment ID, not percentileable)."""
        m = get_signal_meta(Signal.COMMUNITY)
        assert m.dtype is int
        assert m.percentileable is False
        assert m.polarity == "neutral"

    def test_semantic_coherence_metadata(self) -> None:
        """Signal #25: semantic_coherence (high is GOOD)."""
        m = get_signal_meta(Signal.SEMANTIC_COHERENCE)
        assert m.polarity == "high_is_good"
        assert m.percentileable is True

    def test_bus_factor_metadata(self) -> None:
        """Signal #31: bus_factor (high is GOOD, absolute threshold 1.0)."""
        m = get_signal_meta(Signal.BUS_FACTOR)
        assert m.polarity == "high_is_good"
        assert m.absolute_threshold == 1.0
        assert m.phase == 3

    def test_docstring_coverage_metadata(self) -> None:
        """Signal #13: docstring_coverage (high is GOOD)."""
        m = get_signal_meta(Signal.DOCSTRING_COVERAGE)
        assert m.polarity == "high_is_good"
        assert m.percentileable is True

    def test_refactor_ratio_metadata(self) -> None:
        """Signal #34: refactor_ratio (high is GOOD)."""
        m = get_signal_meta(Signal.REFACTOR_RATIO)
        assert m.polarity == "high_is_good"

    def test_risk_score_metadata(self) -> None:
        """Signal #35: risk_score (composite, not percentileable)."""
        m = get_signal_meta(Signal.RISK_SCORE)
        assert m.scope == "file"
        assert m.percentileable is False
        assert m.polarity == "high_is_bad"
        assert m.phase == 5

    def test_instability_metadata(self) -> None:
        """Signal #39: instability (neutral polarity, module scope)."""
        m = get_signal_meta(Signal.INSTABILITY)
        assert m.scope == "module"
        assert m.polarity == "neutral"
        assert m.percentileable is True

    def test_health_score_metadata(self) -> None:
        """Signal #51: health_score (module composite, high is good)."""
        m = get_signal_meta(Signal.HEALTH_SCORE)
        assert m.scope == "module"
        assert m.polarity == "high_is_good"
        assert m.percentileable is False
        assert m.phase == 5

    def test_modularity_metadata(self) -> None:
        """Signal #52: modularity (global, high is good)."""
        m = get_signal_meta(Signal.MODULARITY)
        assert m.scope == "global"
        assert m.polarity == "high_is_good"
        assert m.percentileable is False

    def test_codebase_health_metadata(self) -> None:
        """Signal #62: codebase_health (the one number)."""
        m = get_signal_meta(Signal.CODEBASE_HEALTH)
        assert m.scope == "global"
        assert m.polarity == "high_is_good"
        assert m.percentileable is False
        assert m.phase == 5

    def test_depth_metadata(self) -> None:
        """Signal #19: depth (not percentileable, -1 sentinel)."""
        m = get_signal_meta(Signal.DEPTH)
        assert m.percentileable is False
        assert m.polarity == "neutral"
        assert m.phase == 3

    def test_churn_trajectory_metadata(self) -> None:
        """Signal #28: churn_trajectory (enum, not percentileable)."""
        m = get_signal_meta(Signal.CHURN_TRAJECTORY)
        assert m.dtype is str
        assert m.percentileable is False
        assert m.polarity == "neutral"

    def test_fix_ratio_metadata(self) -> None:
        """Signal #33: fix_ratio (high is bad, threshold 0.4)."""
        m = get_signal_meta(Signal.FIX_RATIO)
        assert m.polarity == "high_is_bad"
        assert m.absolute_threshold == 0.4

    def test_stub_ratio_metadata(self) -> None:
        """Signal #6: stub_ratio (threshold 0.5)."""
        m = get_signal_meta(Signal.STUB_RATIO)
        assert m.absolute_threshold == 0.5
        assert m.polarity == "high_is_bad"
        assert m.phase == 1

    def test_concept_entropy_metadata(self) -> None:
        """Signal #10: concept_entropy (threshold 1.5)."""
        m = get_signal_meta(Signal.CONCEPT_ENTROPY)
        assert m.absolute_threshold == 1.5
        assert m.polarity == "high_is_bad"

    def test_churn_cv_metadata(self) -> None:
        """Signal #30: churn_cv (threshold 1.0)."""
        m = get_signal_meta(Signal.CHURN_CV)
        assert m.absolute_threshold == 1.0
        assert m.polarity == "high_is_bad"


# ---------------------------------------------------------------------------
# Polarity correctness (cross-reference with signals.md polarity table)
# ---------------------------------------------------------------------------


class TestPolarityCorrectness:
    """Verify polarity for every signal matches the spec."""

    def test_high_is_good_signals(self) -> None:
        """Signals where high is good (quality indicators)."""
        expected_good = {
            Signal.DOCSTRING_COVERAGE,
            Signal.SEMANTIC_COHERENCE,
            Signal.BUS_FACTOR,
            Signal.AUTHOR_ENTROPY,
            Signal.REFACTOR_RATIO,
            Signal.WIRING_QUALITY,
            Signal.COHESION,
            Signal.BOUNDARY_ALIGNMENT,
            Signal.ROLE_CONSISTENCY,
            Signal.MODULE_BUS_FACTOR,
            Signal.HEALTH_SCORE,
            Signal.MODULARITY,
            Signal.FIEDLER_VALUE,
            Signal.SPECTRAL_GAP,
            Signal.WIRING_SCORE,
            Signal.ARCHITECTURE_HEALTH,
            Signal.CODEBASE_HEALTH,
        }
        good = signals_by_polarity("high_is_good")
        assert good == expected_good, (
            f"Extra in actual: {good - expected_good}, "
            f"Missing from actual: {expected_good - good}"
        )

    def test_neutral_signals(self) -> None:
        """Signals with neutral polarity (no inherent quality direction)."""
        expected_neutral = {
            Signal.CLASS_COUNT,
            Signal.IMPORT_COUNT,
            Signal.ROLE,
            Signal.IN_DEGREE,
            Signal.OUT_DEGREE,
            Signal.DEPTH,
            Signal.COMMUNITY,
            Signal.COMPRESSION_RATIO,
            Signal.CHURN_TRAJECTORY,
            Signal.INSTABILITY,
            Signal.ABSTRACTNESS,
            Signal.VELOCITY,
            Signal.FILE_COUNT,
        }
        neutral = signals_by_polarity("neutral")
        assert neutral == expected_neutral, (
            f"Extra in actual: {neutral - expected_neutral}, "
            f"Missing from actual: {expected_neutral - neutral}"
        )

    def test_high_is_bad_is_remainder(self) -> None:
        """All other signals are high_is_bad."""
        good = signals_by_polarity("high_is_good")
        neutral = signals_by_polarity("neutral")
        bad = signals_by_polarity("high_is_bad")
        expected_bad = set(Signal) - good - neutral
        assert bad == expected_bad


# ---------------------------------------------------------------------------
# Single-owner invariant
# ---------------------------------------------------------------------------


class TestSingleOwner:
    """Verify the single-owner invariant across all signals."""

    def test_no_producer_collision(self) -> None:
        """No two signals share the same value (which would indicate a registration bug)."""
        values = {}
        for signal, meta in REGISTRY.items():
            if meta.signal.value in values:
                other = values[meta.signal.value]
                pytest.fail(
                    f"Duplicate value '{meta.signal.value}': "
                    f"{signal.name} and {other.name}"
                )
            values[meta.signal.value] = signal

    def test_known_producers(self) -> None:
        """All produced_by values are recognized module paths."""
        known_producers = {
            "scanning",
            "semantics",
            "semantics/roles",
            "graph/algorithms",
            "graph/measurements",
            "signals",
            "signals/fusion",
            "temporal/churn",
            "architecture",
        }
        actual_producers = {m.produced_by for m in REGISTRY.values()}
        unknown = actual_producers - known_producers
        assert not unknown, (
            f"Unknown producers: {unknown}. If intentional, add to known_producers."
        )
