"""Tests for Phase 3 graph models."""

from shannon_insight.graph.models import (
    AuthorDistance,
    ClonePair,
    DependencyGraph,
    FileAnalysis,
    GraphAnalysis,
)


class TestGraphAnalysisPhase3Fields:
    """Test Phase 3 additions to GraphAnalysis."""

    def test_depth_field_exists(self):
        ga = GraphAnalysis()
        assert ga.depth == {}

    def test_is_orphan_field_exists(self):
        ga = GraphAnalysis()
        assert ga.is_orphan == {}

    def test_centrality_gini_field_exists(self):
        ga = GraphAnalysis()
        assert ga.centrality_gini == 0.0

    def test_spectral_gap_field_exists(self):
        ga = GraphAnalysis()
        assert ga.spectral_gap == 0.0


class TestFileAnalysisPhase3Fields:
    """Test Phase 3 additions to FileAnalysis."""

    def test_depth_default(self):
        fa = FileAnalysis(path="test.py")
        assert fa.depth == -1

    def test_is_orphan_default(self):
        fa = FileAnalysis(path="test.py")
        assert fa.is_orphan is False

    def test_phantom_import_count_default(self):
        fa = FileAnalysis(path="test.py")
        assert fa.phantom_import_count == 0


class TestDependencyGraphUnresolvedImports:
    """Test unresolved_imports field on DependencyGraph."""

    def test_default_empty(self):
        dg = DependencyGraph()
        assert dg.unresolved_imports == {}

    def test_can_store_unresolved(self):
        dg = DependencyGraph(unresolved_imports={"a.py": ["missing_module", "another_missing"]})
        assert dg.unresolved_imports["a.py"] == ["missing_module", "another_missing"]


class TestClonePair:
    """Test ClonePair model."""

    def test_clone_pair_fields(self):
        cp = ClonePair(
            file_a="a.py",
            file_b="b.py",
            ncd=0.15,
            size_a=1000,
            size_b=1200,
        )
        assert cp.file_a == "a.py"
        assert cp.file_b == "b.py"
        assert cp.ncd == 0.15
        assert cp.size_a == 1000
        assert cp.size_b == 1200


class TestAuthorDistance:
    """Test AuthorDistance model."""

    def test_author_distance_fields(self):
        ad = AuthorDistance(
            file_a="a.py",
            file_b="b.py",
            distance=0.3,
        )
        assert ad.file_a == "a.py"
        assert ad.file_b == "b.py"
        assert ad.distance == 0.3

    def test_identical_authors_zero_distance(self):
        # This is a conceptual test - actual computation is elsewhere
        ad = AuthorDistance(file_a="a.py", file_b="b.py", distance=0.0)
        assert ad.distance == 0.0

    def test_no_shared_authors_full_distance(self):
        ad = AuthorDistance(file_a="a.py", file_b="b.py", distance=1.0)
        assert ad.distance == 1.0
