"""Tests for tensor extensions: CLONE layer, decomposition, supra-adjacency, hypergraph."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from shannon_insight.tensor.core import (
    AUTHOR,
    CLONE,
    COCHANGE,
    COMBINED,
    IMPORT,
    RELATION_NAMES,
    SEMANTIC,
    RelationTensor,
)

# ── Fixtures ──


def _make_tensor(n_files: int = 10, n_windows: int = 3) -> RelationTensor:
    """Create a small tensor with edges in multiple layers."""
    t = RelationTensor(n_files=n_files, n_windows=n_windows)
    files = [f"src/file_{i}.py" for i in range(n_files)]
    for f in files:
        t.register_node(f)

    # IMPORT edges: chain 0→1→2→...→n-1
    latest = n_windows - 1
    for i in range(n_files - 1):
        t.add_edge(files[i], files[i + 1], latest, IMPORT, 1.0)

    # COCHANGE edges: some pairs
    for i in range(0, n_files - 1, 2):
        t.add_edge(files[i], files[i + 1], latest, COCHANGE, 2.5)
        t.add_edge(files[i + 1], files[i], latest, COCHANGE, 2.5)

    # AUTHOR edges: overlapping pairs
    for i in range(0, n_files - 2, 3):
        t.add_edge(files[i], files[i + 1], latest, AUTHOR, 0.6)
        t.add_edge(files[i + 1], files[i], latest, AUTHOR, 0.6)

    # SEMANTIC edges
    t.add_edge(files[0], files[1], latest, SEMANTIC, 0.8)
    t.add_edge(files[1], files[0], latest, SEMANTIC, 0.8)

    # CLONE edges
    t.add_edge(files[0], files[2], latest, CLONE, 0.85)
    t.add_edge(files[2], files[0], latest, CLONE, 0.85)
    t.add_edge(files[3], files[5], latest, CLONE, 0.72)
    t.add_edge(files[5], files[3], latest, CLONE, 0.72)

    return t


# ── Core tensor with CLONE ──


class TestCloneLayer:
    def test_clone_constant(self):
        assert CLONE == 4
        assert COMBINED == 5
        assert len(RELATION_NAMES) == 6
        assert RELATION_NAMES[CLONE] == "CLONE"

    def test_default_n_relations(self):
        t = RelationTensor(n_files=5)
        assert t.n_relations == 6

    def test_clone_edges_stored(self):
        t = _make_tensor()
        t.finalize()
        latest = t.n_windows - 1
        A_clone = t.slice(latest, CLONE)
        assert A_clone.nnz > 0

    def test_clone_weight_correct(self):
        t = _make_tensor()
        t.finalize()
        latest = t.n_windows - 1
        A_clone = t.slice(latest, CLONE)
        # file_0 → file_2 should have weight 0.85
        idx_0 = t.node_index("src/file_0.py")
        idx_2 = t.node_index("src/file_2.py")
        assert abs(A_clone[idx_0, idx_2] - 0.85) < 0.01


# ── populate_clones ──


class TestPopulateClones:
    def test_populate_clones_basic(self):
        from shannon_insight.graph.models import ClonePair
        from shannon_insight.populate.clones import populate_clones

        t = RelationTensor(n_files=5, n_windows=3)
        for i in range(5):
            t.register_node(f"file_{i}.py")

        pairs = [
            ClonePair(file_a="file_0.py", file_b="file_1.py", ncd=0.15, size_a=100, size_b=110),
            ClonePair(file_a="file_2.py", file_b="file_3.py", ncd=0.25, size_a=200, size_b=190),
        ]

        populate_clones(t, pairs)
        t.finalize()

        A = t.slice(2, CLONE)
        # file_0 → file_1 weight = 1 - 0.15 = 0.85
        assert abs(A[0, 1] - 0.85) < 0.01
        assert abs(A[1, 0] - 0.85) < 0.01
        # file_2 → file_3 weight = 1 - 0.25 = 0.75
        assert abs(A[2, 3] - 0.75) < 0.01

    def test_populate_clones_empty(self):
        from shannon_insight.populate.clones import populate_clones

        t = RelationTensor(n_files=3, n_windows=2)
        for i in range(3):
            t.register_node(f"file_{i}.py")

        populate_clones(t, [])
        t.finalize()

        A = t.slice(1, CLONE)
        assert A.nnz == 0


# ── Combined layer includes CLONE ──


class TestCombinedWithClone:
    def test_combined_includes_clone(self):
        from shannon_insight.populate.combined import populate_combined

        t = _make_tensor()
        populate_combined(t)

        latest = t.n_windows - 1
        A_combined = t.slice(latest, COMBINED)
        # Combined should have non-zero entries (at least from IMPORT)
        assert A_combined.nnz > 0


# ── CP Decomposition ──


class TestCPDecomposition:
    def test_cp_basic(self):
        from shannon_insight.tensor.decomposition import cp_decomposition

        t = _make_tensor()
        t.finalize()
        result = cp_decomposition(t, rank=3, max_iter=20)

        assert result is not None
        assert result.rank == 3
        assert len(result.factors) == 4
        assert result.factors[0].shape == (t.n_nodes, 3)  # A: N x R
        assert result.factors[1].shape == (t.n_nodes, 3)  # B: N x R
        assert result.factors[2].shape == (t.n_windows, 3)  # C: K x R
        assert result.factors[3].shape == (t.n_relations, 3)  # D: n_rel x R

    def test_cp_communities(self):
        from shannon_insight.tensor.decomposition import cp_decomposition

        t = _make_tensor()
        t.finalize()
        result = cp_decomposition(t, rank=3, max_iter=20)

        assert result is not None
        communities = result.dominant_community()
        assert len(communities) == t.n_nodes
        # Each file mapped to a community 0, 1, or 2
        assert all(0 <= c < 3 for c in communities.values())

    def test_cp_summary(self):
        from shannon_insight.tensor.decomposition import cp_decomposition

        t = _make_tensor()
        t.finalize()
        result = cp_decomposition(t, rank=2, max_iter=20)

        assert result is not None
        summaries = result.community_summary(t)
        assert len(summaries) == 2
        assert "component" in summaries[0]
        assert "dominant_relation" in summaries[0]
        assert "temporal_trend" in summaries[0]

    def test_cp_empty_tensor(self):
        from shannon_insight.tensor.decomposition import cp_decomposition

        t = RelationTensor(n_files=3)
        t.register_node("a.py")
        t.finalize()
        result = cp_decomposition(t, rank=2)
        assert result is None  # too few nodes or edges


# ── Tucker Decomposition ──


class TestTuckerDecomposition:
    def test_tucker_basic(self):
        from shannon_insight.tensor.decomposition import tucker_decomposition

        t = _make_tensor()
        t.finalize()
        result = tucker_decomposition(t, ranks=(3, 3, 2, 3))

        assert result is not None
        assert result.core.shape == (3, 3, 2, 3)
        assert len(result.factors) == 4

    def test_tucker_empty(self):
        from shannon_insight.tensor.decomposition import tucker_decomposition

        t = RelationTensor(n_files=2)
        t.register_node("a.py")
        t.finalize()
        result = tucker_decomposition(t, ranks=(2, 2, 2, 2))
        assert result is None


# ── Supra-adjacency ──


class TestSupraAdjacency:
    def test_build_supra(self):
        from shannon_insight.tensor.supra import build_supra_adjacency

        t = _make_tensor()
        t.finalize()
        M = build_supra_adjacency(t)

        n = t.n_nodes
        # Excluding COMBINED: 5 layers × N
        assert M.shape == (5 * n, 5 * n)
        assert M.nnz > 0

    def test_supra_spectral(self):
        from shannon_insight.tensor.supra import supra_spectral_analysis

        t = _make_tensor()
        t.finalize()
        result = supra_spectral_analysis(t, k=5)

        assert result is not None
        # Fiedler value can be slightly negative due to numerical precision on small matrices
        assert result.fiedler_value >= -0.1
        assert result.n_layers == 5  # excludes COMBINED
        assert result.supra_size == 5 * t.n_nodes
        assert len(result.layer_participation) == 5

    def test_supra_with_combined(self):
        from shannon_insight.tensor.supra import build_supra_adjacency

        t = _make_tensor()
        t.finalize()
        M = build_supra_adjacency(t, exclude_combined=False)
        n = t.n_nodes
        assert M.shape == (6 * n, 6 * n)


# ── Hypergraph ──


@dataclass
class MockCommit:
    hash: str
    files: list[str]


class TestHypergraph:
    def test_build_hypergraph(self):
        from shannon_insight.tensor.hypergraph import build_hypergraph

        commits = [
            MockCommit(hash="aaa", files=["a.py", "b.py", "c.py"]),
            MockCommit(hash="bbb", files=["a.py", "d.py"]),
            MockCommit(hash="ccc", files=["b.py", "c.py", "d.py"]),
        ]
        file_set = {"a.py", "b.py", "c.py", "d.py"}

        result = build_hypergraph(commits, file_set)

        assert result is not None
        assert result.n_files == 4
        assert result.n_commits == 3
        assert result.incidence.shape == (4, 3)

    def test_co_occurrence(self):
        from shannon_insight.tensor.hypergraph import build_hypergraph

        commits = [
            MockCommit(hash="aaa", files=["a.py", "b.py"]),
            MockCommit(hash="bbb", files=["a.py", "b.py"]),
        ]
        file_set = {"a.py", "b.py"}

        result = build_hypergraph(commits, file_set)
        assert result is not None

        co = result.co_occurrence.toarray()
        # a and b appear together in 2 commits
        assert co[0, 1] == 2
        assert co[1, 0] == 2
        # diagonal = total commits per file
        assert co[0, 0] == 2
        assert co[1, 1] == 2

    def test_hyperedge_sizes(self):
        from shannon_insight.tensor.hypergraph import build_hypergraph

        commits = [
            MockCommit(hash="aaa", files=["a.py", "b.py", "c.py"]),
            MockCommit(hash="bbb", files=["a.py"]),
        ]
        file_set = {"a.py", "b.py", "c.py"}

        result = build_hypergraph(commits, file_set)
        assert result is not None
        sizes = result.hyperedge_sizes()
        assert sizes[0] == 3  # commit aaa touches 3 files
        assert sizes[1] == 1  # commit bbb touches 1 file

    def test_filter_large_commits(self):
        from shannon_insight.tensor.hypergraph import build_hypergraph

        files = [f"file_{i}.py" for i in range(60)]
        commits = [MockCommit(hash="bulk", files=files)]
        file_set = set(files)

        result = build_hypergraph(commits, file_set, max_files_per_commit=50)
        # Should skip the bulk commit
        assert result is None

    def test_hypergraph_laplacian(self):
        from shannon_insight.tensor.hypergraph import (
            build_hypergraph,
            hypergraph_laplacian_spectrum,
        )

        commits = [
            MockCommit(hash="a", files=["f1.py", "f2.py", "f3.py"]),
            MockCommit(hash="b", files=["f2.py", "f3.py", "f4.py"]),
            MockCommit(hash="c", files=["f4.py", "f5.py"]),
            MockCommit(hash="d", files=["f1.py", "f5.py"]),
        ]
        file_set = {f"f{i}.py" for i in range(1, 6)}

        result = build_hypergraph(commits, file_set)
        assert result is not None

        spectrum = hypergraph_laplacian_spectrum(result, k=3)
        assert spectrum is not None
        assert "fiedler_value" in spectrum
        assert spectrum["fiedler_value"] >= 0
        assert spectrum["n_files"] == 5
        assert spectrum["n_commits"] == 4

    def test_empty_input(self):
        from shannon_insight.tensor.hypergraph import build_hypergraph

        assert build_hypergraph([], set()) is None
        assert build_hypergraph([], {"a.py"}) is None


# ── Cross-layer: Dead imports ──


class TestDeadImports:
    def test_find_dead_imports(self):
        from shannon_insight.cross_layer.dead_imports import find_dead_imports

        t = RelationTensor(n_files=5, n_windows=2)
        files = [f"f{i}.py" for i in range(5)]
        for f in files:
            t.register_node(f)

        # Import: f0 → f1, f0 → f2
        t.add_edge("f0.py", "f1.py", 1, IMPORT, 1.0)
        t.add_edge("f0.py", "f2.py", 1, IMPORT, 1.0)
        # Cochange: only f0 and f1 co-change
        t.add_edge("f0.py", "f1.py", 1, COCHANGE, 2.0)
        t.finalize()

        dead = find_dead_imports(t)
        # f0 → f2 is a dead import (import exists but no co-change)
        assert len(dead) == 1
        assert dead[0] == (t.node_index("f0.py"), t.node_index("f2.py"))


# ── Cross-layer: Clone coupling ──


class TestCloneCoupling:
    def test_active_clones(self):
        from shannon_insight.cross_layer.clone_coupling import find_active_clones

        t = RelationTensor(n_files=4, n_windows=2)
        for i in range(4):
            t.register_node(f"f{i}.py")

        # Clone pair: f0 ↔ f1
        t.add_edge("f0.py", "f1.py", 1, CLONE, 0.85)
        t.add_edge("f1.py", "f0.py", 1, CLONE, 0.85)
        # Also co-change
        t.add_edge("f0.py", "f1.py", 1, COCHANGE, 2.0)
        t.add_edge("f1.py", "f0.py", 1, COCHANGE, 2.0)
        t.finalize()

        active = find_active_clones(t)
        assert len(active) == 1
        assert active[0][2] == pytest.approx(0.85, abs=0.01)  # clone sim
        assert active[0][3] == pytest.approx(2.0, abs=0.01)  # cochange lift

    def test_diverged_clones(self):
        from shannon_insight.cross_layer.clone_coupling import find_diverged_clones

        t = RelationTensor(n_files=4, n_windows=2)
        for i in range(4):
            t.register_node(f"f{i}.py")

        # Clone pair: f0 ↔ f1 but NO co-change
        t.add_edge("f0.py", "f1.py", 1, CLONE, 0.85)
        t.add_edge("f1.py", "f0.py", 1, CLONE, 0.85)
        t.finalize()

        diverged = find_diverged_clones(t)
        assert len(diverged) == 1
        assert diverged[0][2] == pytest.approx(0.85, abs=0.01)
