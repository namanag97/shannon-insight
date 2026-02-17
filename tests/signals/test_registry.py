"""Tests for v2 Signal registry (64 signals)."""

import pytest

from shannon_insight.signals.registry import (
    REGISTRY,
    Signal,
    SignalMeta,
    percentileable_signals,
    register,
    signals_by_phase,
    signals_by_scope,
)


class TestSignalEnum:
    """Test Signal enum has all 64 signals."""

    def test_signal_count(self):
        """Must have exactly 64 signals (from spec)."""
        assert len(Signal) == 64

    def test_per_file_scanning_signals(self):
        """IR1 scanning signals (#1-7)."""
        assert Signal.LINES.value == "lines"
        assert Signal.FUNCTION_COUNT.value == "function_count"
        assert Signal.CLASS_COUNT.value == "class_count"
        assert Signal.MAX_NESTING.value == "max_nesting"
        assert Signal.IMPL_GINI.value == "impl_gini"
        assert Signal.STUB_RATIO.value == "stub_ratio"
        assert Signal.IMPORT_COUNT.value == "import_count"

    def test_per_file_semantic_signals(self):
        """IR2 semantic signals (#8-13)."""
        assert Signal.ROLE.value == "role"
        assert Signal.CONCEPT_COUNT.value == "concept_count"
        assert Signal.CONCEPT_ENTROPY.value == "concept_entropy"
        assert Signal.NAMING_DRIFT.value == "naming_drift"
        assert Signal.TODO_DENSITY.value == "todo_density"
        assert Signal.DOCSTRING_COVERAGE.value == "docstring_coverage"

    def test_per_file_graph_signals(self):
        """IR3 graph signals (#14-26)."""
        assert Signal.PAGERANK.value == "pagerank"
        assert Signal.BETWEENNESS.value == "betweenness"
        assert Signal.IN_DEGREE.value == "in_degree"
        assert Signal.OUT_DEGREE.value == "out_degree"
        assert Signal.BLAST_RADIUS_SIZE.value == "blast_radius_size"
        assert Signal.DEPTH.value == "depth"
        assert Signal.IS_ORPHAN.value == "is_orphan"
        assert Signal.PHANTOM_IMPORT_COUNT.value == "phantom_import_count"
        assert Signal.BROKEN_CALL_COUNT.value == "broken_call_count"
        assert Signal.COMMUNITY.value == "community"
        assert Signal.COMPRESSION_RATIO.value == "compression_ratio"
        assert Signal.SEMANTIC_COHERENCE.value == "semantic_coherence"
        assert Signal.COGNITIVE_LOAD.value == "cognitive_load"

    def test_per_file_temporal_signals(self):
        """IR5t temporal signals (#27-34)."""
        assert Signal.TOTAL_CHANGES.value == "total_changes"
        assert Signal.CHURN_TRAJECTORY.value == "churn_trajectory"
        assert Signal.CHURN_SLOPE.value == "churn_slope"
        assert Signal.CHURN_CV.value == "churn_cv"
        assert Signal.BUS_FACTOR.value == "bus_factor"
        assert Signal.AUTHOR_ENTROPY.value == "author_entropy"
        assert Signal.FIX_RATIO.value == "fix_ratio"
        assert Signal.REFACTOR_RATIO.value == "refactor_ratio"

    def test_per_file_composite_signals(self):
        """Composite signals (#35-36a)."""
        assert Signal.RISK_SCORE.value == "risk_score"
        assert Signal.WIRING_QUALITY.value == "wiring_quality"
        assert Signal.FILE_HEALTH_SCORE.value == "file_health_score"

    def test_per_module_signals(self):
        """Module signals (#37-51)."""
        assert Signal.COHESION.value == "cohesion"
        assert Signal.COUPLING.value == "coupling"
        assert Signal.INSTABILITY.value == "instability"
        assert Signal.ABSTRACTNESS.value == "abstractness"
        assert Signal.MAIN_SEQ_DISTANCE.value == "main_seq_distance"
        assert Signal.BOUNDARY_ALIGNMENT.value == "boundary_alignment"
        assert Signal.LAYER_VIOLATION_COUNT.value == "layer_violation_count"
        assert Signal.ROLE_CONSISTENCY.value == "role_consistency"
        assert Signal.VELOCITY.value == "velocity"
        assert Signal.COORDINATION_COST.value == "coordination_cost"
        assert Signal.KNOWLEDGE_GINI.value == "knowledge_gini"
        assert Signal.MODULE_BUS_FACTOR.value == "module_bus_factor"
        assert Signal.MEAN_COGNITIVE_LOAD.value == "mean_cognitive_load"
        assert Signal.FILE_COUNT.value == "file_count"
        assert Signal.HEALTH_SCORE.value == "health_score"

    def test_global_signals(self):
        """Global signals (#52-62)."""
        assert Signal.MODULARITY.value == "modularity"
        assert Signal.FIEDLER_VALUE.value == "fiedler_value"
        assert Signal.SPECTRAL_GAP.value == "spectral_gap"
        assert Signal.CYCLE_COUNT.value == "cycle_count"
        assert Signal.CENTRALITY_GINI.value == "centrality_gini"
        assert Signal.ORPHAN_RATIO.value == "orphan_ratio"
        assert Signal.PHANTOM_RATIO.value == "phantom_ratio"
        assert Signal.GLUE_DEFICIT.value == "glue_deficit"
        assert Signal.WIRING_SCORE.value == "wiring_score"
        assert Signal.ARCHITECTURE_HEALTH.value == "architecture_health"
        assert Signal.CODEBASE_HEALTH.value == "codebase_health"


class TestSignalMeta:
    """Test SignalMeta dataclass."""

    def test_pagerank_metadata(self):
        """PAGERANK has correct metadata."""
        meta = REGISTRY[Signal.PAGERANK]
        assert meta.signal == Signal.PAGERANK
        assert meta.dtype == float
        assert meta.scope == "file"
        assert meta.percentileable is True
        assert meta.polarity == "high_is_bad"
        assert meta.phase == 0

    def test_community_not_percentileable(self):
        """COMMUNITY is not percentileable (assignment ID)."""
        meta = REGISTRY[Signal.COMMUNITY]
        assert meta.percentileable is False

    def test_role_not_percentileable(self):
        """ROLE is not percentileable (enum)."""
        meta = REGISTRY[Signal.ROLE]
        assert meta.percentileable is False
        assert meta.dtype == str

    def test_is_orphan_boolean(self):
        """IS_ORPHAN is a boolean."""
        meta = REGISTRY[Signal.IS_ORPHAN]
        assert meta.dtype == bool
        assert meta.percentileable is False

    def test_bus_factor_polarity_good(self):
        """BUS_FACTOR: high is GOOD."""
        meta = REGISTRY[Signal.BUS_FACTOR]
        assert meta.polarity == "high_is_good"

    def test_semantic_coherence_polarity_good(self):
        """SEMANTIC_COHERENCE: high is GOOD."""
        meta = REGISTRY[Signal.SEMANTIC_COHERENCE]
        assert meta.polarity == "high_is_good"

    def test_instability_neutral_polarity(self):
        """INSTABILITY has neutral polarity (not inherently good or bad)."""
        meta = REGISTRY[Signal.INSTABILITY]
        # Instability can be None for isolated modules (Ca+Ce=0),
        # but nullable is not tracked in SignalMeta - handled in code
        assert meta.polarity == "neutral"


class TestRegistry:
    """Test registry functions."""

    def test_all_signals_registered(self):
        """Every Signal enum value is in REGISTRY."""
        for sig in Signal:
            assert sig in REGISTRY, f"Signal {sig} not registered"

    def test_single_owner_rule(self):
        """Cannot register same signal from different producer."""
        # Try to register PAGERANK again from different producer
        with pytest.raises(ValueError, match="already registered"):
            register(
                SignalMeta(
                    signal=Signal.PAGERANK,
                    dtype=float,
                    scope="file",
                    percentileable=True,
                    polarity="high_is_bad",
                    absolute_threshold=None,
                    produced_by="different/producer",
                    phase=0,
                )
            )

    def test_idempotent_same_producer(self):
        """Same producer can re-register (idempotent)."""
        meta = REGISTRY[Signal.PAGERANK]
        register(meta)  # Should not raise

    def test_percentileable_signals(self):
        """percentileable_signals() returns correct set."""
        pctl = percentileable_signals()
        assert Signal.PAGERANK in pctl
        assert Signal.COMMUNITY not in pctl
        assert Signal.ROLE not in pctl
        assert Signal.IS_ORPHAN not in pctl
        assert Signal.CHURN_TRAJECTORY not in pctl

    def test_signals_by_phase(self):
        """signals_by_phase() returns correct sets."""
        phase0 = signals_by_phase(0)
        assert Signal.LINES in phase0
        assert Signal.PAGERANK in phase0
        assert Signal.MAX_NESTING not in phase0  # Phase 1

        phase1 = signals_by_phase(1)
        assert Signal.MAX_NESTING in phase1
        assert Signal.IMPL_GINI in phase1

        phase2 = signals_by_phase(2)
        assert Signal.ROLE in phase2
        assert Signal.CONCEPT_ENTROPY in phase2

        phase3 = signals_by_phase(3)
        assert Signal.DEPTH in phase3
        assert Signal.BUS_FACTOR in phase3

        phase4 = signals_by_phase(4)
        assert Signal.COHESION in phase4
        assert Signal.INSTABILITY in phase4

        phase5 = signals_by_phase(5)
        assert Signal.RISK_SCORE in phase5
        assert Signal.CODEBASE_HEALTH in phase5

    def test_signals_by_scope(self):
        """signals_by_scope() returns correct sets."""
        file_signals = signals_by_scope("file")
        assert Signal.PAGERANK in file_signals
        assert Signal.COHESION not in file_signals

        module_signals = signals_by_scope("module")
        assert Signal.COHESION in module_signals
        assert Signal.PAGERANK not in module_signals

        global_signals = signals_by_scope("global")
        assert Signal.MODULARITY in global_signals
        assert Signal.CODEBASE_HEALTH in global_signals


class TestSignalCounts:
    """Verify signal count breakdown from spec."""

    def test_file_signal_count(self):
        """Per-file signals: 38."""
        file_signals = signals_by_scope("file")
        assert len(file_signals) == 38

    def test_module_signal_count(self):
        """Per-module signals: 15."""
        module_signals = signals_by_scope("module")
        assert len(module_signals) == 15

    def test_global_signal_count(self):
        """Global signals: 11."""
        global_signals = signals_by_scope("global")
        assert len(global_signals) == 11

    def test_non_percentileable_count(self):
        """Non-percentileable signals: role, community, is_orphan, depth, churn_trajectory, composites."""
        pctl = percentileable_signals()
        non_pctl = set(Signal) - pctl
        # Enums: role, churn_trajectory
        # Bool: is_orphan
        # Assignment: community
        # Special: depth (can be -1)
        # Composites (already normalized): risk_score, wiring_quality, file_health_score, health_score
        # Global (single value): modularity, fiedler_value, spectral_gap, cycle_count,
        #                        centrality_gini, orphan_ratio, phantom_ratio, glue_deficit,
        #                        wiring_score, architecture_health, codebase_health
        assert len(non_pctl) == 20  # Exact count for V2
