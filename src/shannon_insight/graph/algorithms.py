"""Graph algorithms: centrality, SCC, blast radius, community detection."""

from collections import defaultdict, deque

from ..math.gini import Gini
from ..math.graph import GraphMetrics
from .models import Community, CycleGroup, DependencyGraph, GraphAnalysis


def run_graph_algorithms(graph: DependencyGraph) -> GraphAnalysis:
    """Execute all graph algorithms on a dependency graph."""
    analysis = GraphAnalysis()

    # Centrality (reuse existing math)
    analysis.pagerank = GraphMetrics.pagerank(graph.adjacency)
    analysis.betweenness = GraphMetrics.betweenness_centrality(graph.adjacency)

    # Degree
    for node in graph.all_nodes:
        analysis.out_degree[node] = len(graph.adjacency.get(node, []))
        analysis.in_degree[node] = len(graph.reverse.get(node, []))

    # Strongly connected components (Tarjan's algorithm)
    sccs = tarjan_scc(graph.adjacency, graph.all_nodes)
    for scc in sccs:
        if len(scc) > 1:  # Only real cycles
            internal_edges = sum(
                1 for n in scc for neighbor in graph.adjacency.get(n, []) if neighbor in scc
            )
            analysis.cycles.append(CycleGroup(nodes=scc, internal_edge_count=internal_edges))

    # Blast radius (transitive closure on reverse graph)
    analysis.blast_radius = compute_blast_radius(graph.reverse)

    # Community detection (Louvain)
    communities, node_community, modularity = louvain(graph.adjacency, graph.all_nodes)
    analysis.communities = communities
    analysis.node_community = node_community
    analysis.modularity_score = modularity

    return analysis


def tarjan_scc(adjacency: dict[str, list[str]], all_nodes: set[str]) -> list[set[str]]:
    """Tarjan's algorithm for strongly connected components (iterative).

    Uses an explicit call stack to avoid Python recursion limits on deep
    dependency chains.
    """
    counter = 0
    scc_stack: list[str] = []
    on_stack: set[str] = set()
    index: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    result: list[set[str]] = []

    for root in all_nodes:
        if root in index:
            continue

        # Explicit call stack: each frame is (node, neighbor_iterator, caller)
        call_stack: list[tuple] = []
        # "Enter" root
        index[root] = lowlink[root] = counter
        counter += 1
        scc_stack.append(root)
        on_stack.add(root)
        neighbors = [w for w in adjacency.get(root, []) if w in all_nodes]
        call_stack.append((root, iter(neighbors)))

        while call_stack:
            v, it = call_stack[-1]
            pushed = False
            for w in it:
                if w not in index:
                    # "Recurse" into w
                    index[w] = lowlink[w] = counter
                    counter += 1
                    scc_stack.append(w)
                    on_stack.add(w)
                    w_neighbors = [n for n in adjacency.get(w, []) if n in all_nodes]
                    call_stack.append((w, iter(w_neighbors)))
                    pushed = True
                    break
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], index[w])

            if not pushed:
                # All neighbors processed — "return" from v
                call_stack.pop()
                if call_stack:
                    caller = call_stack[-1][0]
                    lowlink[caller] = min(lowlink[caller], lowlink[v])

                # If v is an SCC root, pop the component
                if lowlink[v] == index[v]:
                    component: set[str] = set()
                    while True:
                        w = scc_stack.pop()
                        on_stack.discard(w)
                        component.add(w)
                        if w == v:
                            break
                    result.append(component)

    return result


def compute_blast_radius(reverse_adj: dict[str, list[str]]) -> dict[str, set[str]]:
    """Compute blast radius: for each file, what files are transitively affected.

    Uses BFS on the reverse graph. If A imports B, then changing B
    affects A. So we follow reverse edges from each node.
    """
    blast: dict[str, set[str]] = {}

    for start_node in reverse_adj:
        visited: set[str] = set()
        queue: deque[str] = deque(reverse_adj.get(start_node, []))
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            queue.extend(n for n in reverse_adj.get(node, []) if n not in visited)
        blast[start_node] = visited

    return blast


def _phase1_local_moving(
    nodes: list[str],
    edge_weights: dict[tuple[str, str], float],
    degree: dict[str, float],
    m: float,
    max_passes: int = 20,
) -> tuple[dict[str, int], bool]:
    """Phase 1 of Louvain: greedily move nodes to maximize modularity.

    Each node is moved to the neighboring community that yields the
    largest positive modularity gain.  Iterates until no more moves
    improve modularity or *max_passes* is reached.

    Args:
        nodes: Sorted list of node identifiers in the current graph.
        edge_weights: Canonical (min,max) -> weight for undirected edges.
        degree: Weighted degree per node (sum(degrees) = 2*m).
        m: Total edge weight (sum of canonical edge weights).
        max_passes: Safety limit on iteration count.

    Returns:
        (node_comm, improved) where *node_comm* maps each node to its
        community id and *improved* is True if any node was moved.
    """
    two_m = 2.0 * m

    # Initialize: each node in its own community
    node_comm: dict[str, int] = {n: i for i, n in enumerate(nodes)}

    # Precompute: sum of degrees per community
    sigma_tot: dict[int, float] = {i: degree.get(n, 0) for i, n in enumerate(nodes)}

    # Build neighbor adjacency (node -> {neighbor: weight})
    neighbors: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for (a, b), w in edge_weights.items():
        neighbors[a][b] += w
        neighbors[b][a] += w

    any_moved = False
    for _pass in range(max_passes):
        moved = False
        for node in nodes:
            current_comm = node_comm[node]
            ki = degree.get(node, 0)

            # Weights from node to each neighboring community
            comm_edge_weights: dict[int, float] = defaultdict(float)
            for neighbor, w in neighbors[node].items():
                comm_edge_weights[node_comm[neighbor]] += w

            # Weight from node to its own community
            ki_in_current = comm_edge_weights.get(current_comm, 0.0)

            # Cost of removing node from current community
            sigma_current = sigma_tot.get(current_comm, 0) - ki
            remove_cost = ki_in_current / two_m - (sigma_current * ki) / (two_m * two_m)

            best_comm = current_comm
            best_gain = 0.0

            for comm_id, ki_in_target in comm_edge_weights.items():
                if comm_id == current_comm:
                    continue

                sigma_target = sigma_tot.get(comm_id, 0)
                add_gain = ki_in_target / two_m - (sigma_target * ki) / (two_m * two_m)
                net_gain = add_gain - remove_cost

                if net_gain > best_gain:
                    best_gain = net_gain
                    best_comm = comm_id

            if best_comm != current_comm:
                # Update sigma_tot
                sigma_tot[current_comm] = sigma_tot.get(current_comm, 0) - ki
                sigma_tot[best_comm] = sigma_tot.get(best_comm, 0) + ki

                # Move node
                node_comm[node] = best_comm
                moved = True
                any_moved = True

        if not moved:
            break

    return node_comm, any_moved


def _coarsen_graph(
    edge_weights: dict[tuple[str, str], float],
    degree: dict[str, float],
    node_comm: dict[str, int],
) -> tuple[dict[tuple[str, str], float], dict[str, float], list[str], dict[str, set[str]]]:
    """Phase 2 of Louvain: collapse communities into super-nodes.

    Each community becomes a single super-node.  Edge weights between
    communities are summed.  Self-loops (edges within a community) are
    kept as canonical self-loop entries (c, c) so that Phase 1 can
    account for internal density on the next round.

    Args:
        edge_weights: Canonical undirected edge weights from current level.
        degree: Weighted degree per node at current level.
        node_comm: Mapping of node -> community id from Phase 1.

    Returns:
        (new_edge_weights, new_degree, new_nodes, super_members)
        where super_members maps super-node name -> set of member nodes.
    """
    # Collect unique community ids
    communities: dict[int, set[str]] = defaultdict(set)
    for node, comm in node_comm.items():
        communities[comm].add(node)

    # Name super-nodes by their community id (as string for consistency)
    comm_name: dict[int, str] = {cid: f"__super_{cid}" for cid in communities}

    # Build super-graph edge weights
    new_edge_weights: dict[tuple[str, str], float] = defaultdict(float)
    for (a, b), w in edge_weights.items():
        ca = comm_name[node_comm[a]]
        cb = comm_name[node_comm[b]]
        key = (min(ca, cb), max(ca, cb))
        new_edge_weights[key] += w

    # Degree of super-node = sum of degrees of its members
    new_degree: dict[str, float] = {}
    for cid, members in communities.items():
        name = comm_name[cid]
        new_degree[name] = sum(degree.get(n, 0) for n in members)

    # Super-node members mapping
    super_members: dict[str, set[str]] = {
        comm_name[cid]: members for cid, members in communities.items()
    }

    new_nodes = sorted(super_members.keys())

    return dict(new_edge_weights), new_degree, new_nodes, super_members


def louvain(
    adjacency: dict[str, list[str]],
    all_nodes: set[str],
) -> tuple[list[Community], dict[str, int], float]:
    """Louvain community detection (Phase 1 + Phase 2).

    Two-phase algorithm:
      Phase 1 — Local moving: greedily move nodes to maximize modularity.
      Phase 2 — Coarsening: collapse communities into super-nodes.

    Repeats both phases until no further improvement is possible.
    Returns (communities, node->community_id, modularity_score).
    """
    # Sort nodes for deterministic iteration across runs
    nodes = sorted(all_nodes)
    if not nodes:
        return [], {}, 0.0

    # Build undirected weighted adjacency for modularity computation
    edge_weights: dict[tuple[str, str], float] = {}
    degree: dict[str, float] = defaultdict(float)

    for src, targets in adjacency.items():
        for tgt in targets:
            if tgt not in all_nodes:
                continue
            key = (min(src, tgt), max(src, tgt))
            edge_weights[key] = edge_weights.get(key, 0) + 1
            degree[src] += 1
            degree[tgt] += 1

    m = sum(edge_weights.values())  # total edge weight
    if m == 0:
        communities = [Community(id=i, members={n}) for i, n in enumerate(nodes)]
        node_community = {n: i for i, n in enumerate(nodes)}
        return communities, node_community, 0.0

    # Track which original nodes each current-level node represents.
    # Initially each node represents only itself.
    original_members: dict[str, set[str]] = {n: {n} for n in nodes}

    max_coarsen = 10  # Prevent infinite coarsening loops

    for _coarsen_iter in range(max_coarsen):
        # Phase 1: Local moving on current graph
        node_comm, improved = _phase1_local_moving(nodes, edge_weights, degree, m)

        if not improved:
            break

        # Count distinct communities after Phase 1
        active_communities = set(node_comm.values())
        if len(active_communities) == len(nodes):
            # No merges happened — each node stayed in its own community
            break

        # Phase 2: Coarsen graph
        new_edge_weights, new_degree, new_nodes, super_members = _coarsen_graph(
            edge_weights, degree, node_comm
        )

        if len(new_nodes) == len(nodes):
            # Coarsening made no progress
            break

        # Update original_members: each super-node maps to the union of
        # original nodes from its constituent current-level nodes.
        new_original_members: dict[str, set[str]] = {}
        for super_node, level_members in super_members.items():
            orig: set[str] = set()
            for level_node in level_members:
                orig.update(original_members[level_node])
            new_original_members[super_node] = orig

        # Move to next level
        original_members = new_original_members
        edge_weights = new_edge_weights
        degree = new_degree
        nodes = new_nodes

    # Final Phase 1 result: node_comm maps current-level nodes to community ids.
    # We need to run Phase 1 one more time if we entered the loop but broke out
    # due to no improvement in coarsening (the last node_comm is already set).
    # But if we never entered the loop body, node_comm is from the first Phase 1.

    # Map back to original nodes: each current-level community -> original nodes
    comm_original: dict[int, set[str]] = defaultdict(set)
    for node, comm_id in node_comm.items():
        comm_original[comm_id].update(original_members[node])

    # Build result with renumbered community ids
    result_communities: list[Community] = []
    node_community: dict[str, int] = {}
    for new_id, (_, members) in enumerate(sorted(comm_original.items())):
        result_communities.append(Community(id=new_id, members=members))
        for orig_node in members:
            node_community[orig_node] = new_id

    # Compute modularity on the ORIGINAL graph
    # Rebuild original edge weights and degree for modularity calculation
    orig_edge_weights: dict[tuple[str, str], float] = {}
    orig_degree: dict[str, float] = defaultdict(float)
    for src, targets in adjacency.items():
        for tgt in targets:
            if tgt not in all_nodes:
                continue
            key = (min(src, tgt), max(src, tgt))
            orig_edge_weights[key] = orig_edge_weights.get(key, 0) + 1
            orig_degree[src] += 1
            orig_degree[tgt] += 1

    modularity = compute_modularity(orig_edge_weights, orig_degree, node_community, m)

    return result_communities, node_community, modularity


def compute_modularity(
    edge_weights: dict[tuple[str, str], float],
    degree: dict[str, float],
    node_comm: dict[str, int],
    m: float,
) -> float:
    """Compute modularity Q = sum_c [L_c/m - (sigma_c/2m)^2].

    Where:
      L_c = total weight of edges within community c
      sigma_c = sum of degrees of nodes in community c
      m = total edge weight (sum of canonical edge weights)

    Edge weights are stored canonically as (min, max) keys for undirected
    edges.  Each canonical entry represents one undirected edge.
    The degree dict already double-counts (each undirected edge adds 1
    to both endpoints), so sum(degrees) = 2*m.
    """
    if m == 0:
        return 0.0

    # L_c totals: sum of edge weights within each community
    e_in = 0.0
    for (a, b), w in edge_weights.items():
        if node_comm.get(a) == node_comm.get(b):
            e_in += w

    # sigma_c: sum of degrees per community
    sigma: dict[int, float] = defaultdict(float)
    for node, deg in degree.items():
        comm = node_comm.get(node)
        if comm is not None:
            sigma[comm] += deg

    # Q = e_in/m - sum(sigma_c^2) / (4*m^2)
    four_m_sq = 4.0 * m * m
    null_term = sum(s * s for s in sigma.values()) / four_m_sq
    return e_in / m - null_term


# ── Phase 3: DAG depth, orphans, centrality Gini ──────────────────────


def compute_dag_depth(
    adjacency: dict[str, list[str]],
    entry_points: set[str],
) -> dict[str, int]:
    """BFS from entry points on the forward (import) graph.

    Entry point fallback chain (if entry_points is empty):
    1. Files with role=ENTRY_POINT (from Phase 2)
    2. __init__.py files that re-export (have both imports and are imported)
    3. Root importers: in_degree=0 AND out_degree>0
    4. If still empty: depth=-1 for ALL files (flat project)

    Depth = shortest path (BFS hop count) from nearest entry point.
    Files unreachable from any entry point get depth = -1.

    Args:
        adjacency: Dependency graph adjacency list (A imports B: A -> B)
        entry_points: Set of entry point file paths

    Returns:
        Dict mapping file path to depth (-1 if unreachable)
    """
    # Collect all nodes
    all_nodes: set[str] = set(adjacency.keys())
    for targets in adjacency.values():
        all_nodes.update(targets)

    # Initialize all to -1 (unreachable)
    depth: dict[str, int] = dict.fromkeys(all_nodes, -1)

    if not entry_points:
        return depth

    # BFS from all entry points simultaneously
    queue: deque[tuple[str, int]] = deque()
    for ep in entry_points:
        if ep in all_nodes:
            queue.append((ep, 0))
            depth[ep] = 0

    while queue:
        node, d = queue.popleft()
        for neighbor in adjacency.get(node, []):
            if depth[neighbor] == -1:  # Not yet visited
                depth[neighbor] = d + 1
                queue.append((neighbor, d + 1))

    return depth


def compute_orphans(
    in_degree: dict[str, int],
    roles: dict[str, str],
) -> dict[str, bool]:
    """Detect orphan files: in_degree=0 AND role not in {ENTRY_POINT, TEST}.

    Orphan files are never imported but aren't entry points or tests.
    They may be dead code or poorly integrated modules.

    Args:
        in_degree: Mapping of file path to in-degree count
        roles: Mapping of file path to role string (from Phase 2)

    Returns:
        Dict mapping file path to is_orphan boolean
    """
    excluded_roles = {"ENTRY_POINT", "TEST", "CONFIG", "INTERFACE", "EXCEPTION"}
    return {
        path: (degree == 0 and roles.get(path, "UNKNOWN").upper() not in excluded_roles)
        for path, degree in in_degree.items()
    }


def compute_centrality_gini(pagerank: dict[str, float]) -> float:
    """Compute Gini coefficient of pagerank distribution.

    Measures inequality in centrality:
    - > 0.7: hub-dominated topology (few files are import hotspots)
    - < 0.3: relatively flat distribution

    Args:
        pagerank: Mapping of file path to pagerank score

    Returns:
        Gini coefficient in [0, 1], or 0.0 if empty/single node
    """
    if len(pagerank) <= 1:
        return 0.0

    values = list(pagerank.values())
    if all(v == 0 for v in values):
        return 0.0

    return Gini.gini_coefficient(values, bias_correction=False)
