"""Graph algorithms: centrality, SCC, blast radius, community detection."""

from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

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


def tarjan_scc(adjacency: Dict[str, List[str]], all_nodes: Set[str]) -> List[Set[str]]:
    """Tarjan's algorithm for strongly connected components (iterative).

    Uses an explicit call stack to avoid Python recursion limits on deep
    dependency chains.
    """
    counter = 0
    scc_stack: List[str] = []
    on_stack: Set[str] = set()
    index: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    result: List[Set[str]] = []

    for root in all_nodes:
        if root in index:
            continue

        # Explicit call stack: each frame is (node, neighbor_iterator, caller)
        call_stack: List[tuple] = []
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
                    component: Set[str] = set()
                    while True:
                        w = scc_stack.pop()
                        on_stack.discard(w)
                        component.add(w)
                        if w == v:
                            break
                    result.append(component)

    return result


def compute_blast_radius(reverse_adj: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    """Compute blast radius: for each file, what files are transitively affected.

    Uses BFS on the reverse graph. If A imports B, then changing B
    affects A. So we follow reverse edges from each node.
    """
    blast: Dict[str, Set[str]] = {}

    for start_node in reverse_adj:
        visited: Set[str] = set()
        queue: deque[str] = deque(reverse_adj.get(start_node, []))
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            queue.extend(n for n in reverse_adj.get(node, []) if n not in visited)
        blast[start_node] = visited

    return blast


def louvain(
    adjacency: Dict[str, List[str]],
    all_nodes: Set[str],
) -> Tuple[List[Community], Dict[str, int], float]:
    """Louvain community detection.

    Maximizes modularity Q = (1/2m) * sum[(A_ij - k_i*k_j/2m) * delta(c_i, c_j)]
    Uses the correct two-part gain: cost of removal + benefit of insertion.

    Returns (communities, node->community_id, modularity_score).
    """
    nodes = list(all_nodes)
    if not nodes:
        return [], {}, 0.0

    # Build undirected weighted adjacency for modularity computation
    edge_weights: Dict[Tuple[str, str], float] = {}
    degree: Dict[str, float] = defaultdict(float)

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

    two_m = 2.0 * m

    # Initialize: each node in its own community
    node_comm: Dict[str, int] = {n: i for i, n in enumerate(nodes)}
    comm_members: Dict[int, Set[str]] = {i: {n} for i, n in enumerate(nodes)}

    # Precompute: sum of degrees per community
    sigma_tot: Dict[int, float] = {i: degree.get(n, 0) for i, n in enumerate(nodes)}

    # Neighbor edges per node
    neighbors: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for (a, b), w in edge_weights.items():
        neighbors[a][b] += w
        neighbors[b][a] += w

    max_passes = 20  # Safety limit
    for _pass in range(max_passes):
        moved = False
        for node in nodes:
            current_comm = node_comm[node]
            ki = degree.get(node, 0)

            # Weights from node to each neighboring community
            comm_edge_weights: Dict[int, float] = defaultdict(float)
            for neighbor, w in neighbors[node].items():
                comm_edge_weights[node_comm[neighbor]] += w

            # Weight from node to its own community (excluding self-loops)
            ki_in_current = comm_edge_weights.get(current_comm, 0.0)

            # Cost of removing node from current community
            # sigma_tot of current community MINUS node's own degree
            sigma_current = sigma_tot.get(current_comm, 0) - ki
            remove_cost = ki_in_current / two_m - (sigma_current * ki) / (two_m * two_m)

            best_comm = current_comm
            best_gain = 0.0

            for comm_id, ki_in_target in comm_edge_weights.items():
                if comm_id == current_comm:
                    continue

                sigma_target = sigma_tot.get(comm_id, 0)
                # Gain of adding node to target community
                add_gain = ki_in_target / two_m - (sigma_target * ki) / (two_m * two_m)

                # Net gain = add_gain - remove_cost
                net_gain = add_gain - remove_cost

                if net_gain > best_gain:
                    best_gain = net_gain
                    best_comm = comm_id

            if best_comm != current_comm:
                # Update sigma_tot
                sigma_tot[current_comm] = sigma_tot.get(current_comm, 0) - ki
                sigma_tot[best_comm] = sigma_tot.get(best_comm, 0) + ki

                # Move node
                comm_members[current_comm].discard(node)
                if not comm_members[current_comm]:
                    del comm_members[current_comm]
                    if current_comm in sigma_tot:
                        del sigma_tot[current_comm]
                comm_members.setdefault(best_comm, set()).add(node)
                node_comm[node] = best_comm
                moved = True

        if not moved:
            break

    # Build result
    communities = [Community(id=cid, members=members) for cid, members in comm_members.items()]
    modularity = compute_modularity(edge_weights, degree, node_comm, m)

    return communities, node_comm, modularity


def compute_modularity(
    edge_weights: Dict[Tuple[str, str], float],
    degree: Dict[str, float],
    node_comm: Dict[str, int],
    m: float,
) -> float:
    """Compute modularity Q = (1/2m) * sum[(A_ij - ki*kj/2m) * delta(ci,cj)]."""
    if m == 0:
        return 0.0
    two_m = 2.0 * m
    q = 0.0
    for (a, b), w in edge_weights.items():
        if node_comm.get(a) == node_comm.get(b):
            q += w - (degree.get(a, 0) * degree.get(b, 0)) / two_m
    return q / two_m
