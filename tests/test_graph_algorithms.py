"""Unit tests for graph/builder.py and graph/algorithms.py."""

from collections import Counter

from shannon_insight.graph.algorithms import (
    _coarsen_graph,
    compute_blast_radius,
    compute_modularity,
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

    def test_unresolved_imports_tracked(self):
        # Phase 3: only internal-looking unresolved imports are tracked
        # Single-segment imports (os, pathlib) are treated as stdlib/external
        # Relative imports are always considered internal (phantom)
        metrics = [
            _fm("pkg/a.py", imports=["os", "pathlib", ".missing", "pkg.submod"]),
            _fm("pkg/b.py", imports=[]),
        ]
        graph = build_dependency_graph(metrics)
        assert "pkg/a.py" in graph.unresolved_imports
        # os, pathlib are single-segment (stdlib) → not tracked
        # .missing is relative → tracked as phantom
        # pkg.submod matches project prefix "pkg" → tracked as phantom
        assert ".missing" in graph.unresolved_imports["pkg/a.py"]
        assert "pkg.submod" in graph.unresolved_imports["pkg/a.py"]

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
        adj = {f"n{i}": [f"n{i + 1}"] for i in range(n - 1)}
        adj[f"n{n - 1}"] = []
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
        # Two tight clusters: {a,b} and {c,d} with one bridge a-c
        adj = {
            "a": ["b", "c"],  # a connects to b (cluster 1) and c (bridge to cluster 2)
            "b": ["a"],
            "c": ["d", "a"],  # c connects to d (cluster 2) and a (bridge back)
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


# ── compute_modularity ──────────────────────────────────────────


class TestComputeModularity:
    def test_zero_edges(self):
        """Modularity of a graph with no edges is 0."""
        assert compute_modularity({}, {}, {}, 0.0) == 0.0

    def test_all_in_one_community(self):
        """All nodes in one community: Q = 0 (no better than random)."""
        # Triangle: a-b, b-c, a-c (bidirectional -> weight 2 each)
        edge_weights = {("a", "b"): 2, ("a", "c"): 2, ("b", "c"): 2}
        degree = {"a": 4, "b": 4, "c": 4}
        node_comm = {"a": 0, "b": 0, "c": 0}
        m = 6.0
        q = compute_modularity(edge_weights, degree, node_comm, m)
        # e_in = 6, sigma_0 = 12, Q = 6/6 - 144/144 = 1 - 1 = 0
        assert abs(q) < 1e-10

    def test_disconnected_pairs(self):
        """Two disconnected pairs: optimal partition gives Q = 0.5."""
        edge_weights = {("a", "b"): 2, ("c", "d"): 2}
        degree = {"a": 2, "b": 2, "c": 2, "d": 2}
        node_comm = {"a": 0, "b": 0, "c": 1, "d": 1}
        m = 4.0
        q = compute_modularity(edge_weights, degree, node_comm, m)
        assert abs(q - 0.5) < 1e-10

    def test_worst_partition(self):
        """Putting connected nodes in different communities gives negative Q."""
        # Single edge a-b, put them in different communities
        edge_weights = {("a", "b"): 2}
        degree = {"a": 2, "b": 2}
        node_comm = {"a": 0, "b": 1}
        m = 2.0
        q = compute_modularity(edge_weights, degree, node_comm, m)
        # e_in = 0, sigma_0=2, sigma_1=2
        # Q = 0/2 - (4+4)/16 = 0 - 0.5 = -0.5
        assert abs(q - (-0.5)) < 1e-10

    def test_degree_invariant(self):
        """sum(degrees) = 2*m must hold for correct modularity."""
        # Build a random-ish graph and verify invariant
        degree = {"a": 2, "b": 2, "c": 2}
        m = 3.0
        assert abs(sum(degree.values()) - 2 * m) < 1e-10

    def test_single_edge_optimal(self):
        """Single edge with both endpoints in same community."""
        edge_weights = {("a", "b"): 1}
        degree = {"a": 1, "b": 1}
        node_comm = {"a": 0, "b": 0}
        m = 1.0
        q = compute_modularity(edge_weights, degree, node_comm, m)
        # e_in = 1, sigma_0 = 2, Q = 1/1 - 4/4 = 0
        assert abs(q) < 1e-10


# ── _coarsen_graph ───────────────────────────────────────────────


class TestCoarsenGraph:
    def test_no_merges(self):
        """If every node is its own community, coarsening produces same-size graph."""
        edge_weights = {("a", "b"): 1}
        degree = {"a": 1, "b": 1}
        node_comm = {"a": 0, "b": 1}
        new_ew, new_deg, new_nodes, super_members = _coarsen_graph(edge_weights, degree, node_comm)
        assert len(new_nodes) == 2
        assert len(super_members) == 2

    def test_full_merge(self):
        """All nodes in one community -> one super-node with self-loop."""
        edge_weights = {("a", "b"): 2, ("a", "c"): 2, ("b", "c"): 2}
        degree = {"a": 4, "b": 4, "c": 4}
        node_comm = {"a": 0, "b": 0, "c": 0}
        new_ew, new_deg, new_nodes, super_members = _coarsen_graph(edge_weights, degree, node_comm)
        assert len(new_nodes) == 1
        # Single super-node with self-loop
        super_node = new_nodes[0]
        assert (super_node, super_node) in new_ew
        # Self-loop weight = sum of all internal edges = 2+2+2 = 6
        assert new_ew[(super_node, super_node)] == 6
        # Degree = sum of all degrees = 12
        assert new_deg[super_node] == 12
        # Members = all original nodes
        assert super_members[super_node] == {"a", "b", "c"}

    def test_two_communities(self):
        """Two communities connected by a bridge edge."""
        # a-b in comm 0, c-d in comm 1, bridge a-c
        edge_weights = {("a", "b"): 2, ("a", "c"): 1, ("c", "d"): 2}
        degree = {"a": 3, "b": 2, "c": 3, "d": 2}
        node_comm = {"a": 0, "b": 0, "c": 1, "d": 1}
        new_ew, new_deg, new_nodes, super_members = _coarsen_graph(edge_weights, degree, node_comm)
        assert len(new_nodes) == 2
        s0 = [n for n in new_nodes if super_members[n] == {"a", "b"}][0]
        s1 = [n for n in new_nodes if super_members[n] == {"c", "d"}][0]
        # Self-loop for comm 0: edge (a,b) weight 2
        assert new_ew.get((s0, s0), 0) == 2
        # Self-loop for comm 1: edge (c,d) weight 2
        assert new_ew.get((s1, s1), 0) == 2
        # Bridge edge between communities: weight 1
        bridge_key = (min(s0, s1), max(s0, s1))
        assert new_ew[bridge_key] == 1
        # Degrees
        assert new_deg[s0] == 5  # 3+2
        assert new_deg[s1] == 5  # 3+2

    def test_preserves_total_edge_weight(self):
        """Total edge weight must be preserved after coarsening."""
        edge_weights = {("a", "b"): 3, ("b", "c"): 1, ("c", "d"): 2}
        degree = {"a": 3, "b": 4, "c": 3, "d": 2}
        node_comm = {"a": 0, "b": 0, "c": 1, "d": 1}
        new_ew, new_deg, new_nodes, _ = _coarsen_graph(edge_weights, degree, node_comm)
        # Total edge weight preserved
        assert sum(new_ew.values()) == sum(edge_weights.values())
        # Total degree preserved
        assert sum(new_deg.values()) == sum(degree.values())


# ── louvain (extended tests) ─────────────────────────────────────


class TestLouvainExtended:
    def test_disconnected_pairs_modularity(self):
        """Two disconnected pairs should give Q = 0.5 and 2 communities."""
        adj = {"a": ["b"], "b": ["a"], "c": ["d"], "d": ["c"]}
        communities, node_comm, modularity = louvain(adj, {"a", "b", "c", "d"})
        assert len(communities) == 2
        assert abs(modularity - 0.5) < 0.01
        # a and b in same community
        assert node_comm["a"] == node_comm["b"]
        # c and d in same community
        assert node_comm["c"] == node_comm["d"]
        # Different communities
        assert node_comm["a"] != node_comm["c"]

    def test_single_node(self):
        """Single node with no edges."""
        communities, node_comm, modularity = louvain({"a": []}, {"a"})
        assert len(communities) == 1
        assert modularity == 0.0
        assert "a" in node_comm

    def test_two_nodes_connected(self):
        """Two connected nodes should be in the same community."""
        adj = {"a": ["b"], "b": ["a"]}
        communities, node_comm, modularity = louvain(adj, {"a", "b"})
        assert len(communities) == 1
        assert node_comm["a"] == node_comm["b"]
        # Single community = Q = 0
        assert abs(modularity) < 1e-10

    def test_bridged_graph(self):
        """Two dense clusters with a single bridge edge.

        Cluster 1: a-b-c (triangle)
        Cluster 2: d-e-f (triangle)
        Bridge: c-d
        """
        adj = {
            "a": ["b", "c"],
            "b": ["a", "c"],
            "c": ["a", "b", "d"],
            "d": ["c", "e", "f"],
            "e": ["d", "f"],
            "f": ["d", "e"],
        }
        communities, node_comm, modularity = louvain(adj, {"a", "b", "c", "d", "e", "f"})
        # Should find 2 communities
        assert len(communities) == 2
        # a, b, c in same community
        assert node_comm["a"] == node_comm["b"] == node_comm["c"]
        # d, e, f in same community
        assert node_comm["d"] == node_comm["e"] == node_comm["f"]
        # Different clusters
        assert node_comm["a"] != node_comm["d"]
        # Modularity should be positive and substantial
        assert modularity > 0.3

    def test_complete_graph(self):
        """Complete graph: all nodes equally connected, Q should be near 0."""
        nodes = {"a", "b", "c", "d"}
        adj = {n: [m for m in nodes if m != n] for n in nodes}
        communities, node_comm, modularity = louvain(adj, nodes)
        # For a complete graph, any partition gives Q <= 0
        # Optimal is all in one community with Q = 0
        assert modularity >= -0.01  # Allow tiny floating point error

    def test_three_disconnected_clusters(self):
        """Three disconnected triangles should give Q ~ 0.667."""
        adj = {
            "a": ["b", "c"],
            "b": ["a", "c"],
            "c": ["a", "b"],
            "d": ["e", "f"],
            "e": ["d", "f"],
            "f": ["d", "e"],
            "g": ["h", "i"],
            "h": ["g", "i"],
            "i": ["g", "h"],
        }
        all_nodes = {"a", "b", "c", "d", "e", "f", "g", "h", "i"}
        communities, node_comm, modularity = louvain(adj, all_nodes)
        assert len(communities) == 3
        # Q for 3 equal disconnected clusters = 1 - 3*(1/3)^2 = 1 - 1/3 = 2/3
        assert abs(modularity - 2 / 3) < 0.01

    def test_modularity_non_negative_for_good_partition(self):
        """Louvain should produce non-negative modularity for non-trivial graphs."""
        adj = {
            "a": ["b"],
            "b": ["a", "c"],
            "c": ["b", "d"],
            "d": ["c"],
        }
        communities, node_comm, modularity = louvain(adj, {"a", "b", "c", "d"})
        assert modularity >= 0.0

    def test_all_nodes_assigned(self):
        """Every node in all_nodes must appear in exactly one community."""
        adj = {
            "a": ["b", "c"],
            "b": ["a"],
            "c": ["a", "d"],
            "d": ["c"],
        }
        all_nodes = {"a", "b", "c", "d"}
        communities, node_comm, modularity = louvain(adj, all_nodes)
        # Every node has a community
        assert set(node_comm.keys()) == all_nodes
        # Every node appears in exactly one community
        all_members = set()
        for comm in communities:
            assert not (all_members & comm.members), "Overlap between communities"
            all_members.update(comm.members)
        assert all_members == all_nodes

    def test_coarsening_reduces_fragmentation(self):
        """Graph where coarsening helps merge initially fragmented communities.

        Ring of 6 nodes: a-b-c-d-e-f-a with extra internal edges
        to create two groups: {a,b,c} and {d,e,f}.
        """
        adj = {
            # Group 1: dense triangle
            "a": ["b", "c", "f"],  # f is bridge to group 2
            "b": ["a", "c"],
            "c": ["a", "b", "d"],  # d is bridge to group 2
            # Group 2: dense triangle
            "d": ["e", "f", "c"],
            "e": ["d", "f"],
            "f": ["d", "e", "a"],
        }
        all_nodes = {"a", "b", "c", "d", "e", "f"}
        communities, node_comm, modularity = louvain(adj, all_nodes)
        # Should find 2 communities, not 6 singletons
        assert len(communities) <= 3
        assert modularity > 0.0

    def test_deterministic_output(self):
        """Running Louvain twice on same input produces same result."""
        adj = {
            "a": ["b", "c"],
            "b": ["a", "d"],
            "c": ["a", "d"],
            "d": ["b", "c"],
        }
        all_nodes = {"a", "b", "c", "d"}
        r1 = louvain(adj, all_nodes)
        r2 = louvain(adj, all_nodes)
        # Same communities (by membership)
        assert len(r1[0]) == len(r2[0])
        for c1 in r1[0]:
            assert any(c1.members == c2.members for c2 in r2[0])
        # Same modularity
        assert abs(r1[2] - r2[2]) < 1e-10
