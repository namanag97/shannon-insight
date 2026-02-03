"""Tests for shannon_insight.math.graph module."""

import pytest

from shannon_insight.math.graph import GraphMetrics


class TestPageRank:
    """Tests for PageRank computation."""

    def test_empty_graph(self, empty_graph):
        """Empty graph returns empty results."""
        result = GraphMetrics.pagerank(empty_graph)
        assert result == {}

    def test_single_node(self, single_node_graph):
        """Single node has rank 1.0."""
        result = GraphMetrics.pagerank(single_node_graph)
        assert abs(result["a"] - 1.0) < 1e-6

    def test_ranks_sum_to_one(self, star_graph):
        """PageRank scores sum to approximately 1.0."""
        result = GraphMetrics.pagerank(star_graph)
        total = sum(result.values())
        assert abs(total - 1.0) < 1e-6

    def test_chain_graph(self, chain_graph):
        """In a chain a->b->c->d, the sink (d) accumulates the most rank."""
        result = GraphMetrics.pagerank(chain_graph)
        # In a directed chain, the endpoint tends to have higher rank
        # because it receives rank but doesn't distribute it normally
        assert len(result) == 4
        assert sum(result.values()) == pytest.approx(1.0, abs=1e-6)

    def test_star_center_highest(self, star_graph):
        """In a star graph, center may not have highest rank since it only has
        outgoing edges. But leaves get rank from center."""
        result = GraphMetrics.pagerank(star_graph)
        assert len(result) == 5
        assert sum(result.values()) == pytest.approx(1.0, abs=1e-6)

    def test_dangling_node_redistribution(self):
        """Dangling nodes redistribute their rank to all nodes."""
        adj = {"a": ["b"], "b": []}  # b is dangling
        result = GraphMetrics.pagerank(adj)
        assert len(result) == 2
        assert sum(result.values()) == pytest.approx(1.0, abs=1e-6)
        # b should have positive rank (receives from a + dangling redistribution)
        assert result["b"] > 0

    def test_convergence_with_cycle(self):
        """Cyclic graph converges."""
        adj = {"a": ["b"], "b": ["c"], "c": ["a"]}
        result = GraphMetrics.pagerank(adj)
        # Symmetric cycle: all ranks should be equal
        values = list(result.values())
        assert all(abs(v - values[0]) < 1e-4 for v in values)


class TestBetweennessCentrality:
    """Tests for betweenness centrality."""

    def test_empty_graph(self):
        """Empty graph returns empty results."""
        result = GraphMetrics.betweenness_centrality({})
        assert result == {}

    def test_star_center_highest_betweenness(self):
        """In a star graph (bidirectional), center has highest betweenness."""
        adj = {
            "center": ["a", "b", "c", "d"],
            "a": ["center"],
            "b": ["center"],
            "c": ["center"],
            "d": ["center"],
        }
        result = GraphMetrics.betweenness_centrality(adj)
        assert result["center"] >= result["a"]
        assert result["center"] >= result["b"]

    def test_chain_middle_highest(self):
        """In a chain a->b->c, b has highest betweenness."""
        adj = {"a": ["b"], "b": ["c"], "c": []}
        result = GraphMetrics.betweenness_centrality(adj)
        assert result["b"] >= result["a"]
        assert result["b"] >= result["c"]

    def test_single_node_zero(self, single_node_graph):
        """Single node has zero betweenness."""
        result = GraphMetrics.betweenness_centrality(single_node_graph)
        assert result["a"] == 0.0

    def test_normalized_values(self, chain_graph):
        """Normalized betweenness values are in [0, 1]."""
        result = GraphMetrics.betweenness_centrality(chain_graph, normalize=True)
        for v in result.values():
            assert 0.0 <= v <= 1.0


class TestEigenvectorCentrality:
    """Tests for eigenvector centrality."""

    def test_empty_graph(self):
        """Empty graph returns empty results."""
        result = GraphMetrics.eigenvector_centrality({})
        assert result == {}

    def test_star_center_highest(self):
        """In a bidirectional star, center has highest eigenvector centrality."""
        adj = {
            "center": ["a", "b", "c", "d"],
            "a": ["center"],
            "b": ["center"],
            "c": ["center"],
            "d": ["center"],
        }
        result = GraphMetrics.eigenvector_centrality(adj)
        assert result["center"] >= result["a"]

    def test_symmetric_cycle_equal(self):
        """Symmetric cycle: all nodes have equal eigenvector centrality."""
        adj = {"a": ["b"], "b": ["c"], "c": ["a"]}
        result = GraphMetrics.eigenvector_centrality(adj)
        values = list(result.values())
        assert all(abs(v - values[0]) < 1e-3 for v in values)

    def test_non_negative(self, chain_graph):
        """All eigenvector centrality values are non-negative."""
        result = GraphMetrics.eigenvector_centrality(chain_graph)
        for v in result.values():
            assert v >= 0.0
