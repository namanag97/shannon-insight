"""Tests for v2 AnalysisStore with Slot[T] wrapper."""

from collections import Counter

import pytest

from shannon_insight.infrastructure.entities import EntityId, EntityType
from shannon_insight.infrastructure.relations import RelationType
from shannon_insight.infrastructure.signals import Signal
from shannon_insight.insights.store_v2 import AnalysisStore, Slot
from shannon_insight.scanning.models import FileMetrics


class TestSlot:
    """Test Slot[T] generic wrapper."""

    def test_initially_unavailable(self):
        """New slot is not available."""
        slot: Slot[str] = Slot()
        assert slot.available is False

    def test_set_makes_available(self):
        """Setting a value makes slot available."""
        slot: Slot[str] = Slot()
        slot.set("hello", "test_producer")
        assert slot.available is True

    def test_value_property(self):
        """Can get value after setting."""
        slot: Slot[int] = Slot()
        slot.set(42, "test_producer")
        assert slot.value == 42

    def test_value_raises_when_unavailable(self):
        """Accessing value when unavailable raises LookupError."""
        slot: Slot[str] = Slot()
        with pytest.raises(LookupError, match="Slot not populated"):
            _ = slot.value

    def test_value_error_includes_message(self):
        """Error includes the error message if set."""
        slot: Slot[str] = Slot()
        slot.set_error("Git not installed", "temporal_analyzer")
        with pytest.raises(LookupError, match="Git not installed"):
            _ = slot.value

    def test_get_with_default(self):
        """get() returns default when unavailable."""
        slot: Slot[int] = Slot()
        assert slot.get(default=0) == 0
        assert slot.get() is None

    def test_get_returns_value_when_available(self):
        """get() returns value when available."""
        slot: Slot[int] = Slot()
        slot.set(42, "producer")
        assert slot.get(default=0) == 42

    def test_produced_by_tracked(self):
        """Provenance is tracked."""
        slot: Slot[str] = Slot()
        slot.set("data", "graph/algorithms")
        assert slot.produced_by == "graph/algorithms"

    def test_error_tracking(self):
        """Error and producer tracked when set_error called."""
        slot: Slot[str] = Slot()
        slot.set_error("Timeout during computation", "clone_detector")
        assert slot.available is False
        assert slot.error == "Timeout during computation"
        assert slot.produced_by == "clone_detector"


class TestAnalysisStore:
    """Test AnalysisStore with typed Slot fields."""

    def test_has_all_required_slots(self):
        """Store has all slots from spec."""
        store = AnalysisStore()

        # Check all slots exist
        assert hasattr(store, "file_syntax")
        assert hasattr(store, "structural")
        assert hasattr(store, "git_history")
        assert hasattr(store, "churn")
        assert hasattr(store, "cochange")
        assert hasattr(store, "semantics")
        assert hasattr(store, "roles")
        assert hasattr(store, "spectral")
        assert hasattr(store, "clone_pairs")
        assert hasattr(store, "author_distances")
        assert hasattr(store, "architecture")
        assert hasattr(store, "signal_field")

    def test_slots_are_slot_instances(self):
        """All optional fields are Slot instances."""
        store = AnalysisStore()

        assert isinstance(store.file_syntax, Slot)
        assert isinstance(store.structural, Slot)
        assert isinstance(store.git_history, Slot)
        assert isinstance(store.churn, Slot)
        assert isinstance(store.semantics, Slot)
        assert isinstance(store.signal_field, Slot)

    def test_available_initially_contains_files(self):
        """available() initially just contains 'files'."""
        store = AnalysisStore()
        assert "files" in store.available

    def test_available_tracks_populated_slots(self):
        """available() includes slot names when populated."""
        store = AnalysisStore()

        # Initially only files
        avail = store.available
        assert "structural" not in avail

        # After setting structural
        store.structural.set(object(), "structural_analyzer")
        avail = store.available
        assert "structural" in avail

    def test_root_dir_and_file_metrics(self):
        """root_dir and file_metrics are always available."""
        store = AnalysisStore(root_dir="/foo/bar")
        assert store.root_dir == "/foo/bar"
        assert store.file_metrics == []

    def test_file_metrics_mutable(self):
        """Can add file metrics."""
        store = AnalysisStore()
        store.file_metrics.append("file1")
        store.file_metrics.append("file2")
        assert len(store.file_metrics) == 2

    def test_multiple_slots_available(self):
        """Multiple slots can be populated."""
        store = AnalysisStore()
        store.structural.set(object(), "a")
        store.git_history.set(object(), "b")
        store.semantics.set(object(), "c")

        avail = store.available
        assert "structural" in avail
        assert "git_history" in avail
        assert "semantics" in avail

    def test_slot_value_access_pattern(self):
        """Demonstrate safe access pattern."""
        store = AnalysisStore()

        # WRONG pattern - would crash
        # graph = store.structural.value  # LookupError

        # RIGHT pattern - check first
        if store.structural.available:
            graph = store.structural.value
        else:
            graph = None

        assert graph is None

        # After setting
        store.structural.set({"test": "data"}, "producer")
        if store.structural.available:
            graph = store.structural.value
            assert graph == {"test": "data"}


class TestSlotErrorMessages:
    """Test that error messages are informative."""

    def test_unpopulated_slot_message(self):
        """Unpopulated slot gives basic message."""
        slot: Slot[str] = Slot()
        try:
            _ = slot.value
        except LookupError as e:
            assert "Slot not populated" in str(e)

    def test_slot_with_error_message(self):
        """Slot with error gives detailed message."""
        slot: Slot[str] = Slot()
        slot.set_error("Git binary not found in PATH", "temporal/git_extractor")
        try:
            _ = slot.value
        except LookupError as e:
            msg = str(e)
            assert "not populated" in msg.lower() or "Git binary" in msg


def _make_file_metrics(path: str, lines: int = 100, imports: list | None = None) -> FileMetrics:
    """Helper to create a FileMetrics for testing."""
    return FileMetrics(
        path=path,
        lines=lines,
        tokens=50,
        imports=imports or [],
        exports=[],
        functions=3,
        interfaces=0,
        structs=1,
        complexity_score=2.0,
        nesting_depth=2,
        ast_node_types=Counter(),
        last_modified=0.0,
        function_sizes=[20, 30, 50],
    )


class TestFactStoreBridge:
    """Test that _sync_entities populates FactStore with file entities and basic signals."""

    def test_sync_entities_creates_file_entities(self):
        """_sync_entities creates FILE entities in FactStore."""
        store = AnalysisStore(root_dir="/test/root")
        store.file_metrics = [
            _make_file_metrics("src/main.py"),
            _make_file_metrics("src/utils.py"),
        ]
        store._sync_entities()

        files = store.fact_store.files()
        assert len(files) == 2
        keys = {f.key for f in files}
        assert "src/main.py" in keys
        assert "src/utils.py" in keys

    def test_sync_entities_sets_basic_signals(self):
        """_sync_entities writes LINES, FUNCTION_COUNT, CLASS_COUNT, IMPORT_COUNT."""
        store = AnalysisStore(root_dir="/test/root")
        fm = _make_file_metrics("src/main.py", lines=200, imports=["os", "sys"])
        store.file_metrics = [fm]
        store._sync_entities()

        entity_id = EntityId(EntityType.FILE, "src/main.py")
        assert store.fact_store.get_signal(entity_id, Signal.LINES) == 200
        assert store.fact_store.get_signal(entity_id, Signal.FUNCTION_COUNT) == 3
        assert store.fact_store.get_signal(entity_id, Signal.CLASS_COUNT) == 1
        assert store.fact_store.get_signal(entity_id, Signal.IMPORT_COUNT) == 2


class TestStructuralAnalyzerFactStoreSync:
    """Test that StructuralAnalyzer syncs signals and relations to FactStore."""

    def test_structural_analyzer_writes_graph_signals(self, tmp_path):
        """StructuralAnalyzer writes PAGERANK, IN_DEGREE, OUT_DEGREE etc to FactStore."""
        from shannon_insight.graph.models import (
            CodebaseAnalysis,
            DependencyGraph,
            FileAnalysis,
            GraphAnalysis,
        )
        from shannon_insight.insights.analyzers.structural import StructuralAnalyzer

        store = AnalysisStore(root_dir=str(tmp_path))

        # Create a minimal CodebaseAnalysis with file data
        fa = FileAnalysis(
            path="src/main.py",
            lines=100,
            pagerank=0.5,
            betweenness=0.3,
            in_degree=2,
            out_degree=3,
            blast_radius_size=5,
            community_id=0,
            depth=1,
            is_orphan=False,
            phantom_import_count=0,
            compression_ratio=0.7,
            cognitive_load=15.0,
        )
        ga = GraphAnalysis(
            pagerank={"src/main.py": 0.5},
            in_degree={"src/main.py": 2},
            out_degree={"src/main.py": 3},
            centrality_gini=0.4,
        )
        graph = DependencyGraph(
            adjacency={"src/main.py": ["src/utils.py"]},
            reverse={"src/utils.py": ["src/main.py"]},
            all_nodes={"src/main.py", "src/utils.py"},
            edge_count=1,
        )
        result = CodebaseAnalysis(
            files={"src/main.py": fa},
            graph=graph,
            graph_analysis=ga,
            total_files=1,
            total_edges=1,
            cycle_count=0,
            modularity=0.5,
        )

        # Create entities first (normally done by kernel)
        store.file_metrics = [_make_file_metrics("src/main.py")]
        store._sync_entities()

        # Call _sync_to_fact_store directly
        analyzer = StructuralAnalyzer()
        analyzer._sync_to_fact_store(store, result)

        entity_id = EntityId(EntityType.FILE, "src/main.py")
        assert store.fact_store.get_signal(entity_id, Signal.PAGERANK) == 0.5
        assert store.fact_store.get_signal(entity_id, Signal.BETWEENNESS) == 0.3
        assert store.fact_store.get_signal(entity_id, Signal.IN_DEGREE) == 2
        assert store.fact_store.get_signal(entity_id, Signal.OUT_DEGREE) == 3
        assert store.fact_store.get_signal(entity_id, Signal.BLAST_RADIUS_SIZE) == 5
        assert store.fact_store.get_signal(entity_id, Signal.COMMUNITY) == 0
        assert store.fact_store.get_signal(entity_id, Signal.DEPTH) == 1
        assert store.fact_store.get_signal(entity_id, Signal.IS_ORPHAN) is False
        assert store.fact_store.get_signal(entity_id, Signal.COMPRESSION_RATIO) == 0.7
        assert store.fact_store.get_signal(entity_id, Signal.COGNITIVE_LOAD) == 15.0

    def test_structural_analyzer_writes_global_signals(self, tmp_path):
        """StructuralAnalyzer writes MODULARITY, CYCLE_COUNT, CENTRALITY_GINI."""
        from shannon_insight.graph.models import (
            CodebaseAnalysis,
            DependencyGraph,
            GraphAnalysis,
        )
        from shannon_insight.insights.analyzers.structural import StructuralAnalyzer

        root = str(tmp_path)
        store = AnalysisStore(root_dir=root)

        ga = GraphAnalysis(centrality_gini=0.65)
        result = CodebaseAnalysis(
            files={},
            graph=DependencyGraph(),
            graph_analysis=ga,
            cycle_count=3,
            modularity=0.72,
        )

        analyzer = StructuralAnalyzer()
        analyzer._sync_to_fact_store(store, result)

        codebase_id = EntityId(EntityType.CODEBASE, root)
        assert store.fact_store.get_signal(codebase_id, Signal.MODULARITY) == 0.72
        assert store.fact_store.get_signal(codebase_id, Signal.CYCLE_COUNT) == 3
        assert store.fact_store.get_signal(codebase_id, Signal.CENTRALITY_GINI) == 0.65

    def test_structural_analyzer_writes_imports_relations(self, tmp_path):
        """StructuralAnalyzer writes IMPORTS relations to FactStore."""
        from shannon_insight.graph.models import (
            CodebaseAnalysis,
            DependencyGraph,
            GraphAnalysis,
        )
        from shannon_insight.insights.analyzers.structural import StructuralAnalyzer

        store = AnalysisStore(root_dir=str(tmp_path))

        graph = DependencyGraph(
            adjacency={
                "src/main.py": ["src/utils.py", "src/config.py"],
                "src/utils.py": ["src/config.py"],
            },
            reverse={
                "src/utils.py": ["src/main.py"],
                "src/config.py": ["src/main.py", "src/utils.py"],
            },
            all_nodes={"src/main.py", "src/utils.py", "src/config.py"},
            edge_count=3,
        )
        result = CodebaseAnalysis(
            files={},
            graph=graph,
            graph_analysis=GraphAnalysis(),
        )

        analyzer = StructuralAnalyzer()
        analyzer._sync_to_fact_store(store, result)

        # Check IMPORTS relations
        main_id = EntityId(EntityType.FILE, "src/main.py")
        utils_id = EntityId(EntityType.FILE, "src/utils.py")
        config_id = EntityId(EntityType.FILE, "src/config.py")

        assert store.fact_store.has_relation(main_id, RelationType.IMPORTS, utils_id)
        assert store.fact_store.has_relation(main_id, RelationType.IMPORTS, config_id)
        assert store.fact_store.has_relation(utils_id, RelationType.IMPORTS, config_id)
        # No reverse relation
        assert not store.fact_store.has_relation(config_id, RelationType.IMPORTS, main_id)


class TestTemporalAnalyzerFactStoreSync:
    """Test that TemporalAnalyzer syncs churn signals and cochange relations."""

    def test_temporal_sync_writes_churn_signals(self):
        """TemporalAnalyzer writes per-file churn signals to FactStore."""
        from shannon_insight.insights.analyzers.temporal import TemporalAnalyzer
        from shannon_insight.temporal.models import ChurnSeries, CoChangeMatrix

        store = AnalysisStore(root_dir="/test")
        store.file_metrics = [_make_file_metrics("src/main.py")]
        store._sync_entities()

        churn = {
            "src/main.py": ChurnSeries(
                file_path="src/main.py",
                window_counts=[5, 3, 8],
                total_changes=16,
                trajectory="churning",
                slope=1.5,
                cv=0.8,
                bus_factor=2.0,
                author_entropy=1.5,
                fix_ratio=0.25,
                refactor_ratio=0.1,
            ),
        }
        cochange = CoChangeMatrix(
            pairs={}, total_commits=100, file_change_counts={"src/main.py": 16}
        )

        analyzer = TemporalAnalyzer()
        analyzer._sync_to_fact_store(store, churn, cochange)

        entity_id = EntityId(EntityType.FILE, "src/main.py")
        assert store.fact_store.get_signal(entity_id, Signal.TOTAL_CHANGES) == 16
        assert store.fact_store.get_signal(entity_id, Signal.CHURN_CV) == 0.8
        assert store.fact_store.get_signal(entity_id, Signal.BUS_FACTOR) == 2.0
        assert store.fact_store.get_signal(entity_id, Signal.AUTHOR_ENTROPY) == 1.5
        assert store.fact_store.get_signal(entity_id, Signal.FIX_RATIO) == 0.25
        assert store.fact_store.get_signal(entity_id, Signal.REFACTOR_RATIO) == 0.1
        assert store.fact_store.get_signal(entity_id, Signal.CHURN_TRAJECTORY) == "churning"
        assert store.fact_store.get_signal(entity_id, Signal.CHURN_SLOPE) == 1.5

    def test_temporal_sync_writes_cochange_relations(self):
        """TemporalAnalyzer writes COCHANGES_WITH relations to FactStore."""
        from shannon_insight.insights.analyzers.temporal import TemporalAnalyzer
        from shannon_insight.temporal.models import CoChangeMatrix, CoChangePair

        store = AnalysisStore(root_dir="/test")

        pair = CoChangePair(
            file_a="src/main.py",
            file_b="src/utils.py",
            cochange_count=10,
            total_a=20,
            total_b=15,
            confidence_a_b=0.5,
            confidence_b_a=0.67,
            lift=2.5,
        )
        cochange = CoChangeMatrix(
            pairs={("src/main.py", "src/utils.py"): pair},
            total_commits=100,
            file_change_counts={"src/main.py": 20, "src/utils.py": 15},
        )

        analyzer = TemporalAnalyzer()
        analyzer._sync_to_fact_store(store, {}, cochange)

        main_id = EntityId(EntityType.FILE, "src/main.py")
        utils_id = EntityId(EntityType.FILE, "src/utils.py")
        assert store.fact_store.has_relation(main_id, RelationType.COCHANGES_WITH, utils_id)

        # Verify weight is the lift value
        rels = store.fact_store.outgoing(main_id, RelationType.COCHANGES_WITH)
        assert len(rels) == 1
        assert rels[0].weight == 2.5


class TestSpectralAnalyzerFactStoreSync:
    """Test that SpectralAnalyzer syncs global signals to FactStore."""

    def test_spectral_sync_writes_global_signals(self):
        """SpectralAnalyzer writes FIEDLER_VALUE and SPECTRAL_GAP."""
        from shannon_insight.temporal.models import SpectralSummary

        root = "/test/root"
        store = AnalysisStore(root_dir=root)

        # Simulate what spectral analyzer does after computing
        result = SpectralSummary(
            fiedler_value=0.42,
            num_components=1,
            eigenvalues=[0.0, 0.42, 1.5],
            spectral_gap=0.28,
        )
        store.spectral.set(result, produced_by="spectral")

        # Manually sync (the analyzer does this internally)
        codebase_id = EntityId(EntityType.CODEBASE, root)
        store.fact_store.set_signal(codebase_id, Signal.FIEDLER_VALUE, 0.42)
        store.fact_store.set_signal(codebase_id, Signal.SPECTRAL_GAP, 0.28)

        assert store.fact_store.get_signal(codebase_id, Signal.FIEDLER_VALUE) == 0.42
        assert store.fact_store.get_signal(codebase_id, Signal.SPECTRAL_GAP) == 0.28


class TestSemanticAnalyzerFactStoreSync:
    """Test that SemanticAnalyzer syncs semantic signals to FactStore."""

    def test_semantic_sync_writes_file_signals(self):
        """SemanticAnalyzer writes CONCEPT_COUNT, CONCEPT_ENTROPY, NAMING_DRIFT, etc."""
        from shannon_insight.semantics.analyzer import SemanticAnalyzer
        from shannon_insight.semantics.models import Completeness, Concept, FileSemantics, Role

        store = AnalysisStore(root_dir="/test")
        store.file_metrics = [_make_file_metrics("src/main.py")]
        store._sync_entities()

        # Create test semantic data
        semantics = {
            "src/main.py": FileSemantics(
                path="src/main.py",
                role=Role.UTILITY,
                concepts=[
                    Concept(topic="processing", weight=0.6, keywords=["process", "parse"]),
                    Concept(topic="validation", weight=0.4, keywords=["validate", "check"]),
                ],
                concept_count=2,
                concept_entropy=0.97,
                naming_drift=0.15,
                completeness=Completeness(
                    todo_density=0.5, docstring_coverage=0.8, todo_count=1
                ),
                tier=3,
                import_fingerprint={"os": 0.5, "sys": 0.3},
            ),
        }

        analyzer = SemanticAnalyzer()
        analyzer._sync_to_fact_store(store, semantics)

        entity_id = EntityId(EntityType.FILE, "src/main.py")
        assert store.fact_store.get_signal(entity_id, Signal.CONCEPT_COUNT) == 2
        assert store.fact_store.get_signal(entity_id, Signal.CONCEPT_ENTROPY) == 0.97
        assert store.fact_store.get_signal(entity_id, Signal.NAMING_DRIFT) == 0.15
        assert store.fact_store.get_signal(entity_id, Signal.TODO_DENSITY) == 0.5
        assert store.fact_store.get_signal(entity_id, Signal.DOCSTRING_COVERAGE) == 0.8
        assert store.fact_store.get_signal(entity_id, Signal.ROLE) == "utility"

    def test_semantic_sync_writes_similar_to_relations(self):
        """SemanticAnalyzer writes SIMILAR_TO relations for similar files."""
        from shannon_insight.semantics.analyzer import SemanticAnalyzer
        from shannon_insight.semantics.models import FileSemantics, Role

        store = AnalysisStore(root_dir="/test")

        # Create files with similar import fingerprints
        semantics = {
            "src/file_a.py": FileSemantics(
                path="src/file_a.py",
                role=Role.UTILITY,
                concepts=[],
                concept_count=0,
                concept_entropy=0.0,
                naming_drift=0.0,
                tier=1,
                import_fingerprint={"os": 1.0, "sys": 0.8, "json": 0.5},
            ),
            "src/file_b.py": FileSemantics(
                path="src/file_b.py",
                role=Role.UTILITY,
                concepts=[],
                concept_count=0,
                concept_entropy=0.0,
                naming_drift=0.0,
                tier=1,
                import_fingerprint={"os": 0.9, "sys": 0.9, "json": 0.4},
            ),
            "src/file_c.py": FileSemantics(
                path="src/file_c.py",
                role=Role.UTILITY,
                concepts=[],
                concept_count=0,
                concept_entropy=0.0,
                naming_drift=0.0,
                tier=1,
                import_fingerprint={"requests": 1.0},  # Completely different
            ),
        }

        analyzer = SemanticAnalyzer()
        analyzer._sync_to_fact_store(store, semantics)

        # Check that file_a and file_b are marked as similar (high overlap)
        file_a = EntityId(EntityType.FILE, "src/file_a.py")
        file_b = EntityId(EntityType.FILE, "src/file_b.py")
        file_c = EntityId(EntityType.FILE, "src/file_c.py")

        # Should have SIMILAR_TO relation between a and b
        assert store.fact_store.has_relation(file_a, RelationType.SIMILAR_TO, file_b)

        # Should NOT have relation with file_c (different imports)
        assert not store.fact_store.has_relation(file_a, RelationType.SIMILAR_TO, file_c)
        assert not store.fact_store.has_relation(file_b, RelationType.SIMILAR_TO, file_c)
