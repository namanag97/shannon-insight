"""Unit tests for graph/builder.py and graph/algorithms.py."""

from collections import Counter

from shannon_insight.graph.algorithms import (
    compute_blast_radius,
    louvain,
    run_graph_algorithms,
    tarjan_scc,
)
from shannon_insight.graph.builder import build_dependency_graph
from shannon_insight.graph.models import DependencyGraph
from shannon_insight.scanning.models import FileMetrics


def _fm(path: str, imports: list[str] | None = None) -> FileMetrics:
    """Shortcut to build a minimal FileMetrics."""
    return FileMetrics(
        path=path,
        lines=10,
        tokens=50,
        imports=imports or [],
        exports=[],
        functions=1,
        interfaces=0,
        structs=0,
        complexity_score=1.0,
        nesting_depth=1,
        ast_node_types=Counter(),
        last_modified=0.0,
    )


# ── build_dependency_graph ────────────────────────────────────────


class TestBuildDependencyGraph:
    def test_empty_input(self):
        graph = build_dependency_graph([])
        assert graph.edge_count == 0
        assert graph.all_nodes == set()

    def test_single_file_no_imports(self):
        graph = build_dependency_graph([_fm("a.py")])
        assert graph.edge_count == 0
        assert graph.all_nodes == {"a.py"}
        assert graph.adjacency["a.py"] == []

    def test_resolved_import(self):
        metrics = [
            _fm("src/pkg/a.py", imports=[".b"]),
            _fm("src/pkg/b.py"),
        ]
        graph = build_dependency_graph(metrics)
        assert graph.edge_count == 1
        assert "src/pkg/b.py" in graph.adjacency["src/pkg/a.py"]
        assert "src/pkg/a.py" in graph.reverse["src/pkg/b.py"]

    def test_unresolved_import_ignored(self):
        metrics = [_fm("a.py", imports=["os", "pathlib"])]
        graph = build_dependency_graph(metrics)
        assert graph.edge_count == 0

    def test_self_import_ignored(self):
        metrics = [_fm("src/pkg/a.py", imports=[".a"])]
        graph = build_dependency_graph(metrics)
        assert graph.edge_count == 0


# ── tarjan_scc ────────────────────────────────────────────────────


class TestTarjanSCC:
    def test_no_cycles(self):
        adj = {"a": ["b"], "b": ["c"], "c": []}
        sccs = tarjan_scc(adj, {"a", "b", "c"})
        # Every node is its own SCC (no multi-node components)
        assert all(len(s) == 1 for s in sccs)

    def test_simple_cycle(self):
        adj = {"a": ["b"], "b": ["a"]}
        sccs = tarjan_scc(adj, {"a", "b"})
        cycles = [s for s in sccs if len(s) > 1]
        assert len(cycles) == 1
        assert cycles[0] == {"a", "b"}

    def test_triangle_cycle(self):
        adj = {"a": ["b"], "b": ["c"], "c": ["a"]}
        sccs = tarjan_scc(adj, {"a", "b", "c"})
        cycles = [s for s in sccs if len(s) > 1]
        assert len(cycles) == 1
        assert cycles[0] == {"a", "b", "c"}

    def test_two_separate_cycles(self):
        adj = {"a": ["b"], "b": ["a"], "c": ["d"], "d": ["c"]}
        sccs = tarjan_scc(adj, {"a", "b", "c", "d"})
        cycles = [s for s in sccs if len(s) > 1]
        assert len(cycles) == 2

    def test_empty_graph(self):
        sccs = tarjan_scc({}, set())
        assert sccs == []

    def test_single_node(self):
        sccs = tarjan_scc({"a": []}, {"a"})
        assert len(sccs) == 1
        assert sccs[0] == {"a"}

    def test_deep_chain_no_stack_overflow(self):
        """Iterative Tarjan should handle deep chains without recursion limit."""
        n = 1000
        nodes = {f"n{i}" for i in range(n)}
        adj = {f"n{i}": [f"n{i+1}"] for i in range(n - 1)}
        adj[f"n{n-1}"] = []
        sccs = tarjan_scc(adj, nodes)
        assert len(sccs) == n  # each node is its own SCC


# ── compute_blast_radius ──────────────────────────────────────────


class TestComputeBlastRadius:
    def test_empty(self):
        assert compute_blast_radius({}) == {}

    def test_no_dependents(self):
        reverse = {"a": [], "b": [], "c": []}
        blast = compute_blast_radius(reverse)
        assert all(len(v) == 0 for v in blast.values())

    def test_chain(self):
        # a imports b imports c → reverse: c->[b], b->[a]
        reverse = {"a": [], "b": ["a"], "c": ["b"]}
        blast = compute_blast_radius(reverse)
        assert blast["c"] == {"b", "a"}  # changing c affects b and a
        assert blast["b"] == {"a"}
        assert blast["a"] == set()

    def test_diamond(self):
        # a,b both import c → reverse: c->[a,b]
        reverse = {"a": [], "b": [], "c": ["a", "b"]}
        blast = compute_blast_radius(reverse)
        assert blast["c"] == {"a", "b"}


# ── louvain ───────────────────────────────────────────────────────


class TestLouvain:
    def test_empty(self):
        communities, node_comm, modularity = louvain({}, set())
        assert communities == []
        assert node_comm == {}
        assert modularity == 0.0

    def test_disconnected_nodes(self):
        adj = {"a": [], "b": [], "c": []}
        communities, node_comm, modularity = louvain(adj, {"a", "b", "c"})
        # Each node in its own community
        assert len(communities) == 3
        assert modularity == 0.0

    def test_two_clusters(self):
        # Two tight clusters: {a,b} and {c,d} with one bridge
        adj = {
            "a": ["b"],
            "b": ["a"],
            "c": ["d"],
            "d": ["c"],
            "a": ["b", "c"],  # bridge
            "b": ["a"],
            "c": ["d", "a"],
            "d": ["c"],
        }
        communities, node_comm, modularity = louvain(adj, {"a", "b", "c", "d"})
        assert len(communities) >= 1
        # Modularity should be non-negative for any partition
        assert modularity >= 0.0


# ── run_graph_algorithms (integration) ────────────────────────────


class TestRunGraphAlgorithms:
    def test_basic_graph(self):
        graph = DependencyGraph(
            adjacency={"a": ["b"], "b": ["c"], "c": []},
            reverse={"a": [], "b": ["a"], "c": ["b"]},
            all_nodes={"a", "b", "c"},
            edge_count=2,
        )
        analysis = run_graph_algorithms(graph)
        assert len(analysis.pagerank) == 3
        assert len(analysis.betweenness) == 3
        assert analysis.out_degree["a"] == 1
        assert analysis.in_degree["c"] == 1
        assert len(analysis.cycles) == 0  # no cycles
        assert len(analysis.blast_radius) == 3

    def test_with_cycle(self):
        graph = DependencyGraph(
            adjacency={"a": ["b"], "b": ["a"]},
            reverse={"a": ["b"], "b": ["a"]},
            all_nodes={"a", "b"},
            edge_count=2,
        )
        analysis = run_graph_algorithms(graph)
        assert len(analysis.cycles) == 1
        assert analysis.cycles[0].nodes == {"a", "b"}
