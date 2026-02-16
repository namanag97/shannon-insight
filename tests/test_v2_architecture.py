"""
V2 Architecture Acceptance Tests

These tests define the contract for the v2 architecture.
The new implementation MUST pass all these tests.

Structure:
1. Entity Model Tests
2. Signal Model Tests
3. Relation Model Tests
4. Store Tests
5. Pipeline Tests
6. Pattern Tests
"""

from enum import Enum

import pytest

# =============================================================================
# PART 1: ENTITY MODEL TESTS
# =============================================================================


class TestEntityTypes:
    """Entity types must exist and be enumerable."""

    def test_entity_type_enum_exists(self):
        from shannon_insight.infrastructure.entities import EntityType

        assert isinstance(EntityType, type)
        assert issubclass(EntityType, Enum)

    def test_all_six_entity_types_exist(self):
        from shannon_insight.infrastructure.entities import EntityType

        expected = {"CODEBASE", "MODULE", "FILE", "SYMBOL", "AUTHOR", "COMMIT"}
        actual = {e.name for e in EntityType}
        assert actual == expected, f"Missing: {expected - actual}, Extra: {actual - expected}"

    def test_entity_id_is_hashable(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType

        e1 = EntityId(EntityType.FILE, "src/foo.py")
        e2 = EntityId(EntityType.FILE, "src/foo.py")
        e3 = EntityId(EntityType.FILE, "src/bar.py")

        # Same entity should be equal and have same hash
        assert e1 == e2
        assert hash(e1) == hash(e2)

        # Different entity should not be equal
        assert e1 != e3

        # Should work in sets/dicts
        s = {e1, e2, e3}
        assert len(s) == 2

    def test_entity_has_parent(self):
        from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType

        codebase = Entity(
            id=EntityId(EntityType.CODEBASE, "/repo"),
            parent=None,
        )
        module = Entity(
            id=EntityId(EntityType.MODULE, "auth"),
            parent=EntityId(EntityType.CODEBASE, "/repo"),
        )
        file = Entity(
            id=EntityId(EntityType.FILE, "src/auth/login.py"),
            parent=EntityId(EntityType.MODULE, "auth"),
        )

        assert codebase.parent is None
        assert module.parent == EntityId(EntityType.CODEBASE, "/repo")
        assert file.parent == EntityId(EntityType.MODULE, "auth")


# =============================================================================
# PART 2: SIGNAL MODEL TESTS
# =============================================================================


class TestSignalEnum:
    """Signal enum must have all 62 signals."""

    def test_signal_enum_exists(self):
        from shannon_insight.infrastructure.signals import Signal

        assert isinstance(Signal, type)
        assert issubclass(Signal, Enum)

    def test_signal_count_is_62(self):
        from shannon_insight.infrastructure.signals import Signal

        assert len(Signal) == 62, f"Expected 62 signals, got {len(Signal)}"

    def test_per_file_signals_exist(self):
        """Signals 1-36 (per-file)."""
        from shannon_insight.infrastructure.signals import Signal

        per_file = [
            "LINES",
            "FUNCTION_COUNT",
            "CLASS_COUNT",
            "MAX_NESTING",
            "IMPL_GINI",
            "STUB_RATIO",
            "IMPORT_COUNT",
            "ROLE",
            "CONCEPT_COUNT",
            "CONCEPT_ENTROPY",
            "NAMING_DRIFT",
            "TODO_DENSITY",
            "DOCSTRING_COVERAGE",
            "PAGERANK",
            "BETWEENNESS",
            "IN_DEGREE",
            "OUT_DEGREE",
            "BLAST_RADIUS_SIZE",
            "DEPTH",
            "IS_ORPHAN",
            "PHANTOM_IMPORT_COUNT",
            "BROKEN_CALL_COUNT",
            "COMMUNITY",
            "COMPRESSION_RATIO",
            "SEMANTIC_COHERENCE",
            "COGNITIVE_LOAD",
            "TOTAL_CHANGES",
            "CHURN_TRAJECTORY",
            "CHURN_SLOPE",
            "CHURN_CV",
            "BUS_FACTOR",
            "AUTHOR_ENTROPY",
            "FIX_RATIO",
            "REFACTOR_RATIO",
            "RISK_SCORE",
            "WIRING_QUALITY",
        ]
        for name in per_file:
            assert hasattr(Signal, name), f"Missing signal: {name}"

    def test_per_module_signals_exist(self):
        """Signals 37-51 (per-module)."""
        from shannon_insight.infrastructure.signals import Signal

        per_module = [
            "COHESION",
            "COUPLING",
            "INSTABILITY",
            "ABSTRACTNESS",
            "MAIN_SEQ_DISTANCE",
            "BOUNDARY_ALIGNMENT",
            "LAYER_VIOLATION_COUNT",
            "ROLE_CONSISTENCY",
            "VELOCITY",
            "COORDINATION_COST",
            "KNOWLEDGE_GINI",
            "MODULE_BUS_FACTOR",
            "MEAN_COGNITIVE_LOAD",
            "FILE_COUNT",
            "HEALTH_SCORE",
        ]
        for name in per_module:
            assert hasattr(Signal, name), f"Missing signal: {name}"

    def test_global_signals_exist(self):
        """Signals 52-62 (global)."""
        from shannon_insight.infrastructure.signals import Signal

        global_signals = [
            "MODULARITY",
            "FIEDLER_VALUE",
            "SPECTRAL_GAP",
            "CYCLE_COUNT",
            "CENTRALITY_GINI",
            "ORPHAN_RATIO",
            "PHANTOM_RATIO",
            "GLUE_DEFICIT",
            "WIRING_SCORE",
            "ARCHITECTURE_HEALTH",
            "CODEBASE_HEALTH",
        ]
        for name in global_signals:
            assert hasattr(Signal, name), f"Missing signal: {name}"


class TestSignalRegistry:
    """Signal registry must have metadata for all signals."""

    def test_registry_exists(self):
        from shannon_insight.infrastructure.signals import SIGNAL_REGISTRY

        assert isinstance(SIGNAL_REGISTRY, dict)

    def test_all_signals_registered(self):
        from shannon_insight.infrastructure.signals import SIGNAL_REGISTRY, Signal

        for signal in Signal:
            assert signal in SIGNAL_REGISTRY, f"Signal {signal} not in registry"

    def test_signal_spec_has_required_fields(self):
        from shannon_insight.infrastructure.signals import SIGNAL_REGISTRY, SignalSpec

        required_fields = {
            "signal",
            "scope",
            "dtype",
            "polarity",
            "phase",
            "source",
            "percentileable",
        }

        for signal, spec in SIGNAL_REGISTRY.items():
            assert isinstance(spec, SignalSpec), f"{signal} spec is not SignalSpec"
            for field in required_fields:
                assert hasattr(spec, field), f"{signal} missing field: {field}"

    def test_polarity_values(self):
        from shannon_insight.infrastructure.signals import SIGNAL_REGISTRY, Polarity

        for signal, spec in SIGNAL_REGISTRY.items():
            assert spec.polarity in Polarity, f"{signal} has invalid polarity: {spec.polarity}"

    def test_percentileable_signals_correct(self):
        """Non-percentileable signals: role, churn_trajectory, is_orphan, community, depth."""
        from shannon_insight.infrastructure.signals import SIGNAL_REGISTRY, Signal

        non_percentileable = {
            Signal.ROLE,
            Signal.CHURN_TRAJECTORY,
            Signal.IS_ORPHAN,
            Signal.COMMUNITY,
            Signal.DEPTH,
        }
        for signal, spec in SIGNAL_REGISTRY.items():
            if signal in non_percentileable:
                assert not spec.percentileable, f"{signal} should not be percentileable"


class TestSignalStore:
    """SignalStore must support entity × signal × time storage."""

    def test_signal_store_exists(self):
        from shannon_insight.infrastructure.signals import SignalStore

        store = SignalStore()
        assert store is not None

    def test_set_and_get(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.signals import Signal, SignalStore

        store = SignalStore()
        entity = EntityId(EntityType.FILE, "src/foo.py")

        store.set(entity, Signal.LINES, 100)
        assert store.get(entity, Signal.LINES) == 100

    def test_has_signal(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.signals import Signal, SignalStore

        store = SignalStore()
        entity = EntityId(EntityType.FILE, "src/foo.py")

        assert not store.has(entity, Signal.LINES)
        store.set(entity, Signal.LINES, 100)
        assert store.has(entity, Signal.LINES)

    def test_all_values_for_signal(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.signals import Signal, SignalStore

        store = SignalStore()
        e1 = EntityId(EntityType.FILE, "a.py")
        e2 = EntityId(EntityType.FILE, "b.py")

        store.set(e1, Signal.LINES, 100)
        store.set(e2, Signal.LINES, 200)

        values = store.all_values(Signal.LINES)
        assert len(values) == 2
        assert (e1, 100) in values
        assert (e2, 200) in values


# =============================================================================
# PART 3: RELATION MODEL TESTS
# =============================================================================


class TestRelationTypes:
    """Relation types must exist."""

    def test_relation_type_enum_exists(self):
        from shannon_insight.infrastructure.relations import RelationType

        assert isinstance(RelationType, type)
        assert issubclass(RelationType, Enum)

    def test_all_eight_relation_types_exist(self):
        from shannon_insight.infrastructure.relations import RelationType

        expected = {
            "IMPORTS",
            "COCHANGES_WITH",
            "SIMILAR_TO",
            "AUTHORED_BY",
            "IN_MODULE",
            "CONTAINS",
            "DEPENDS_ON",
            "CLONED_FROM",
        }
        actual = {r.name for r in RelationType}
        assert actual == expected, f"Missing: {expected - actual}, Extra: {actual - expected}"


class TestRelation:
    """Relation dataclass must work correctly."""

    def test_relation_creation(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.relations import Relation, RelationType

        rel = Relation(
            type=RelationType.IMPORTS,
            source=EntityId(EntityType.FILE, "a.py"),
            target=EntityId(EntityType.FILE, "b.py"),
            weight=1.0,
        )
        assert rel.type == RelationType.IMPORTS
        assert rel.weight == 1.0


class TestRelationGraph:
    """RelationGraph must support querying."""

    def test_relation_graph_exists(self):
        from shannon_insight.infrastructure.relations import RelationGraph

        graph = RelationGraph()
        assert graph is not None

    def test_add_and_query(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.relations import Relation, RelationGraph, RelationType

        graph = RelationGraph()
        e1 = EntityId(EntityType.FILE, "a.py")
        e2 = EntityId(EntityType.FILE, "b.py")

        rel = Relation(RelationType.IMPORTS, e1, e2, 1.0)
        graph.add(rel)

        assert graph.has(e1, RelationType.IMPORTS, e2)
        assert not graph.has(e2, RelationType.IMPORTS, e1)

    def test_outgoing_incoming(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.relations import Relation, RelationGraph, RelationType

        graph = RelationGraph()
        e1 = EntityId(EntityType.FILE, "a.py")
        e2 = EntityId(EntityType.FILE, "b.py")
        e3 = EntityId(EntityType.FILE, "c.py")

        graph.add(Relation(RelationType.IMPORTS, e1, e2, 1.0))
        graph.add(Relation(RelationType.IMPORTS, e1, e3, 1.0))

        outgoing = graph.outgoing(e1, RelationType.IMPORTS)
        assert len(outgoing) == 2

        incoming = graph.incoming(e2, RelationType.IMPORTS)
        assert len(incoming) == 1
        assert incoming[0].source == e1


# =============================================================================
# PART 4: FACT STORE TESTS
# =============================================================================


class TestFactStore:
    """FactStore must unify entities, signals, and relations."""

    def test_fact_store_exists(self):
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(root="/repo")
        assert store is not None

    def test_fact_store_has_entities(self):
        from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(root="/repo")
        entity = Entity(EntityId(EntityType.FILE, "a.py"))

        store.add_entity(entity)
        assert store.get_entity(entity.id) == entity

    def test_fact_store_has_signals(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.signals import Signal
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(root="/repo")
        entity = EntityId(EntityType.FILE, "a.py")

        store.set_signal(entity, Signal.LINES, 100)
        assert store.get_signal(entity, Signal.LINES) == 100

    def test_fact_store_has_relations(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.relations import Relation, RelationType
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(root="/repo")
        e1 = EntityId(EntityType.FILE, "a.py")
        e2 = EntityId(EntityType.FILE, "b.py")

        rel = Relation(RelationType.IMPORTS, e1, e2, 1.0)
        store.add_relation(rel)

        assert store.has_relation(e1, RelationType.IMPORTS, e2)


# =============================================================================
# PART 5: PIPELINE TESTS
# =============================================================================


class TestPipeline:
    """Pipeline must execute stages in order."""

    def test_runtime_context_exists(self):
        from shannon_insight.infrastructure.runtime import RuntimeContext

        ctx = RuntimeContext(root="/repo")
        assert ctx.root == "/repo"

    def test_runtime_context_has_tier(self):
        from shannon_insight.infrastructure.runtime import RuntimeContext, Tier

        ctx = RuntimeContext(root="/repo")
        assert ctx.tier in Tier

    def test_tier_enum_exists(self):
        from shannon_insight.infrastructure.runtime import Tier

        assert Tier.ABSOLUTE is not None
        assert Tier.BAYESIAN is not None
        assert Tier.FULL is not None


# =============================================================================
# PART 6: PATTERN TESTS
# =============================================================================


class TestPatternModel:
    """Pattern model for declarative finders."""

    def test_pattern_scope_enum_exists(self):
        from shannon_insight.infrastructure.patterns import PatternScope

        expected = {"FILE", "FILE_PAIR", "MODULE", "MODULE_PAIR", "CODEBASE"}
        actual = {p.name for p in PatternScope}
        assert actual == expected

    def test_pattern_has_required_fields(self):
        from shannon_insight.infrastructure.patterns import Pattern, PatternScope

        # Pattern should be creatable with required fields (canonical v2 model)
        pattern = Pattern(
            name="test_pattern",
            scope=PatternScope.FILE,
            severity=0.5,
            requires={"signals"},
            condition="test_signal > 0.5",
            predicate=lambda store, entity: True,
            severity_fn=lambda store, entity: 0.5,
            evidence_fn=lambda store, entity: {"test": "evidence"},
            description="Test pattern",
            remediation="Fix it",
        )
        assert pattern.name == "test_pattern"
        assert pattern.scope == PatternScope.FILE
        assert pattern.severity == 0.5
        assert pattern.condition == "test_signal > 0.5"
        assert pattern.hotspot_filtered is False  # default


class TestFindingModel:
    """Finding model."""

    def test_finding_creation(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.patterns import Finding, PatternScope

        finding = Finding(
            pattern="test_pattern",
            scope=PatternScope.FILE,
            target=EntityId(EntityType.FILE, "a.py"),
            severity=0.8,
            confidence=0.9,
            evidence={"lines": 1000},
        )
        assert finding.severity == 0.8
        assert finding.confidence == 0.9

    def test_finding_has_stable_id(self):
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.patterns import Finding, PatternScope

        finding = Finding(
            pattern="god_file",
            scope=PatternScope.FILE,
            target=EntityId(EntityType.FILE, "a.py"),
            severity=0.8,
            confidence=0.9,
            evidence={},
        )
        # Stable ID for tracking across snapshots
        assert finding.id == "god_file:a.py"


# =============================================================================
# PART 7: INTEGRATION TESTS
# =============================================================================


class TestFullPipeline:
    """Integration tests for the full pipeline."""

    @pytest.fixture
    def sample_codebase(self, tmp_path):
        """Create a minimal codebase for testing."""
        # Create sample files
        (tmp_path / "main.py").write_text("import auth\n\ndef main():\n    pass\n")
        (tmp_path / "auth.py").write_text("def login():\n    pass\n\ndef logout():\n    pass\n")
        (tmp_path / "utils.py").write_text("def helper():\n    pass\n")
        return tmp_path

    def test_pipeline_produces_fact_store(self, sample_codebase):
        """Pipeline should produce a populated FactStore."""
        from shannon_insight.api import analyze

        result = run_pipeline(str(sample_codebase))

        assert result.store is not None
        assert len(result.store.files()) >= 3

    def test_pipeline_computes_signals(self, sample_codebase):
        """Pipeline should compute signals for all files."""
        from shannon_insight.api import analyze
        from shannon_insight.infrastructure.signals import Signal

        result = run_pipeline(str(sample_codebase))

        for file_entity in result.store.files():
            # Basic signals should exist
            assert result.store.get_signal(file_entity, Signal.LINES) is not None
            assert result.store.get_signal(file_entity, Signal.FUNCTION_COUNT) is not None

    def test_pipeline_detects_findings(self, sample_codebase):
        """Pipeline should produce findings."""
        from shannon_insight.api import analyze

        result = run_pipeline(str(sample_codebase))

        # Result should have findings list (may be empty for clean code)
        assert hasattr(result, "findings")
        assert isinstance(result.findings, list)


# =============================================================================
# PART 8: MATH FORMULA TESTS
# =============================================================================


class TestMathFormulas:
    """Mathematical formulas must be correct."""

    def test_gini_coefficient(self):
        from shannon_insight.infrastructure.math import compute_gini

        # Perfect equality
        assert compute_gini([1, 1, 1, 1]) == pytest.approx(0.0)

        # Maximum inequality (one has everything)
        assert compute_gini([0, 0, 0, 10]) == pytest.approx(0.75)

        # Empty or zero sum
        assert compute_gini([]) == 0.0
        assert compute_gini([0, 0, 0]) == 0.0

    def test_shannon_entropy(self):

        from shannon_insight.infrastructure.math import compute_entropy

        # Single value (certainty)
        assert compute_entropy({"a": 10}) == 0.0

        # Uniform distribution
        assert compute_entropy({"a": 1, "b": 1}) == pytest.approx(1.0)
        assert compute_entropy({"a": 1, "b": 1, "c": 1, "d": 1}) == pytest.approx(2.0)

    def test_bus_factor(self):
        from shannon_insight.infrastructure.math import compute_bus_factor

        # Single author
        assert compute_bus_factor({"alice": 100}) == pytest.approx(1.0)

        # Two equal authors
        assert compute_bus_factor({"alice": 50, "bob": 50}) == pytest.approx(2.0)

    def test_percentile(self):
        from shannon_insight.infrastructure.math import compute_percentile

        values = [10, 20, 30, 40, 50]

        # Minimum value
        assert compute_percentile(10, values) == pytest.approx(0.2)  # 1/5

        # Maximum value
        assert compute_percentile(50, values) == pytest.approx(1.0)  # 5/5


# =============================================================================
# PART 9: BACKWARD COMPATIBILITY TESTS
# =============================================================================


class TestBackwardCompatibility:
    """v2 should not break existing v1 functionality."""

    def test_insight_kernel_still_works(self):
        """InsightKernel should still be importable and functional."""
        from shannon_insight.insights.kernel import InsightKernel

        assert InsightKernel is not None

    def test_old_store_fields_accessible(self):
        """Old store fields should still be accessible for migration."""
        from shannon_insight.insights.store import AnalysisStore

        store = AnalysisStore()

        # Old fields should exist
        assert hasattr(store, "file_metrics")
        assert hasattr(store, "structural")
        assert hasattr(store, "git_history")

    def test_old_finders_still_work(self):
        """Existing finders should still be importable."""
        from shannon_insight.insights.finders import (
            GodFileFinder,
            HiddenCouplingFinder,
            HighRiskHubFinder,
        )

        assert HighRiskHubFinder is not None
        assert HiddenCouplingFinder is not None
        assert GodFileFinder is not None
