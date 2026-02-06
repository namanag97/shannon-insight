"""Tests for Phase 3 graph algorithms: dag_depth, orphans, centrality_gini."""

import pytest

from shannon_insight.graph.algorithms import (
    compute_centrality_gini,
    compute_dag_depth,
    compute_orphans,
    louvain,
)


class TestComputeDagDepth:
    """Test BFS depth from entry points."""

    def test_single_entry_point(self):
        # a -> b -> c
        adjacency = {"a": ["b"], "b": ["c"], "c": []}
        entry_points = {"a"}
        depth = compute_dag_depth(adjacency, entry_points)
        assert depth["a"] == 0
        assert depth["b"] == 1
        assert depth["c"] == 2

    def test_multiple_entry_points(self):
        # a -> c, b -> c -> d
        adjacency = {"a": ["c"], "b": ["c"], "c": ["d"], "d": []}
        entry_points = {"a", "b"}
        depth = compute_dag_depth(adjacency, entry_points)
        assert depth["a"] == 0
        assert depth["b"] == 0
        assert depth["c"] == 1  # shortest path from either a or b
        assert depth["d"] == 2

    def test_unreachable_files_get_minus_one(self):
        # a -> b, c is isolated
        adjacency = {"a": ["b"], "b": [], "c": []}
        entry_points = {"a"}
        depth = compute_dag_depth(adjacency, entry_points)
        assert depth["a"] == 0
        assert depth["b"] == 1
        assert depth["c"] == -1

    def test_empty_entry_points_all_minus_one(self):
        adjacency = {"a": ["b"], "b": []}
        entry_points = set()
        depth = compute_dag_depth(adjacency, entry_points)
        # No entry points means all files are unreachable
        assert all(d == -1 for d in depth.values())

    def test_cycle_handled(self):
        # a -> b -> c -> b (cycle)
        adjacency = {"a": ["b"], "b": ["c"], "c": ["b"]}
        entry_points = {"a"}
        depth = compute_dag_depth(adjacency, entry_points)
        assert depth["a"] == 0
        assert depth["b"] == 1
        assert depth["c"] == 2


class TestComputeOrphans:
    """Test orphan detection (in_degree=0 AND not entry/test)."""

    def test_orphan_detected(self):
        in_degree = {"a": 0, "b": 1, "c": 0}
        roles = {"a": "UTILITY", "b": "UTILITY", "c": "UTILITY"}
        orphans = compute_orphans(in_degree, roles)
        assert orphans["a"] is True
        assert orphans["b"] is False  # has importer
        assert orphans["c"] is True

    def test_entry_point_not_orphan(self):
        in_degree = {"a": 0, "b": 0}
        roles = {"a": "ENTRY_POINT", "b": "UTILITY"}
        orphans = compute_orphans(in_degree, roles)
        assert orphans["a"] is False  # entry points are not orphans
        assert orphans["b"] is True

    def test_test_not_orphan(self):
        in_degree = {"a": 0}
        roles = {"a": "TEST"}
        orphans = compute_orphans(in_degree, roles)
        assert orphans["a"] is False  # test files are not orphans

    def test_file_with_importer_not_orphan(self):
        in_degree = {"a": 2}
        roles = {"a": "UTILITY"}
        orphans = compute_orphans(in_degree, roles)
        assert orphans["a"] is False


class TestComputeCentralityGini:
    """Test Gini coefficient of pagerank distribution."""

    def test_equal_distribution_zero_gini(self):
        # All files have same pagerank -> Gini = 0
        pagerank = {"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25}
        gini = compute_centrality_gini(pagerank)
        assert gini == pytest.approx(0.0, abs=0.01)

    def test_max_inequality_high_gini(self):
        # One file has all the centrality
        pagerank = {"a": 1.0, "b": 0.0, "c": 0.0, "d": 0.0}
        gini = compute_centrality_gini(pagerank)
        assert gini == pytest.approx(0.75, abs=0.01)  # (n-1)/n for n=4

    def test_moderate_inequality(self):
        # Some inequality
        pagerank = {"a": 0.4, "b": 0.3, "c": 0.2, "d": 0.1}
        gini = compute_centrality_gini(pagerank)
        assert 0.1 < gini < 0.5  # moderate inequality

    def test_empty_returns_zero(self):
        gini = compute_centrality_gini({})
        assert gini == 0.0

    def test_single_file_returns_zero(self):
        gini = compute_centrality_gini({"a": 1.0})
        assert gini == 0.0


class TestLouvainDeterminism:
    """Test that Louvain produces identical results on consecutive runs."""

    def test_deterministic_communities(self):
        # Same input should produce same output every time
        adj = {
            "a": ["b", "c"],
            "b": ["a"],
            "c": ["d", "a"],
            "d": ["c"],
        }
        nodes = {"a", "b", "c", "d"}

        # Run multiple times
        results = []
        for _ in range(5):
            communities, node_comm, modularity = louvain(adj, nodes)
            # Sort communities by first member for comparison
            sorted_comms = sorted([tuple(sorted(c.members)) for c in communities])
            results.append((sorted_comms, dict(node_comm), modularity))

        # All runs should produce identical results
        first = results[0]
        for result in results[1:]:
            assert result == first, "Louvain should be deterministic"
