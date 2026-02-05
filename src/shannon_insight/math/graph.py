"""Graph theory: PageRank, betweenness centrality, eigenvector centrality."""

import math
from typing import Dict, List


class GraphMetrics:
    """Graph theory calculations for dependency graphs."""

    @staticmethod
    def pagerank(
        adjacency: Dict[str, List[str]],
        damping: float = 0.85,
        iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> Dict[str, float]:
        """
        Compute PageRank using power iteration.

        PR(A) = (1 - d) + d * Σ (PR(Ti) / C(Ti))

        Args:
            adjacency: Node -> list of neighbors
            damping: Damping factor (0.85 is standard)
            iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dictionary mapping nodes to PageRank scores
        """
        # Work on a copy to avoid mutating the caller's data structure.
        adj: Dict[str, List[str]] = {k: list(v) for k, v in adjacency.items()}

        nodes = set(adj.keys())
        for neighbors in adj.values():
            nodes.update(neighbors)

        if not nodes:
            return {}

        N = len(nodes)
        rank = dict.fromkeys(nodes, 1.0 / N)

        # Identify dangling nodes (no outgoing edges).
        # Standard treatment: redistribute their mass uniformly to all nodes.
        # Reference: Langville & Meyer, "Google's PageRank and Beyond" (2006), Ch. 3.
        dangling = [node for node in nodes if node not in adj or len(adj[node]) == 0]

        # Ensure every node has an adjacency entry (possibly empty).
        for node in nodes:
            if node not in adj:
                adj[node] = []

        out_degree = {node: len(neighbors) for node, neighbors in adj.items()}

        reverse: Dict[str, List[str]] = {node: [] for node in nodes}
        for src, neighbors in adj.items():
            for tgt in neighbors:
                if tgt in reverse:
                    reverse[tgt].append(src)

        for _ in range(iterations):
            new_rank = {}
            max_diff = 0.0

            # Sum of rank mass sitting on dangling nodes.
            dangling_sum = sum(rank[node] for node in dangling)

            for node in nodes:
                # Teleportation + dangling-node redistribution.
                new_rank[node] = (1 - damping) / N + damping * dangling_sum / N

                for src in reverse[node]:
                    if out_degree[src] > 0:
                        new_rank[node] += damping * (rank[src] / out_degree[src])

                diff = abs(new_rank[node] - rank[node])
                max_diff = max(max_diff, diff)

            rank = new_rank

            if max_diff < tolerance:
                break

        return rank

    @staticmethod
    def betweenness_centrality(
        adjacency: Dict[str, List[str]], normalize: bool = True
    ) -> Dict[str, float]:
        """
        Compute betweenness centrality using Brandes' algorithm.

        C_B(v) = Σ (σ_st(v) / σ_st) where s != v != t

        Args:
            adjacency: Node -> list of neighbors
            normalize: Normalize by (n-1)(n-2)/2 for undirected graphs

        Returns:
            Dictionary mapping nodes to betweenness centrality
        """
        nodes = set(adjacency.keys())
        for neighbors in adjacency.values():
            nodes.update(neighbors)

        betweenness = dict.fromkeys(nodes, 0.0)

        for s in nodes:
            stack: List[str] = []
            predecessors: Dict[str, List[str]] = {v: [] for v in nodes}
            sigma = dict.fromkeys(nodes, 0)
            sigma[s] = 1

            dist = dict.fromkeys(nodes, -1)
            dist[s] = 0

            queue = [s]

            while queue:
                v = queue.pop(0)
                stack.append(v)

                for w in adjacency.get(v, []):
                    if dist[w] < 0:
                        dist[w] = dist[v] + 1
                        queue.append(w)

                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        predecessors[w].append(v)

            delta = dict.fromkeys(nodes, 0.0)

            while stack:
                w = stack.pop()
                for v in predecessors[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]

        if normalize:
            n = len(nodes)
            if n > 2:
                # Directed graph: normalize by (n-1)(n-2).
                # The BFS follows directed edges, so the factor-of-2 used
                # for undirected graphs does not apply here.
                # Reference: Brandes (2001), Section 4.
                scale = 1.0 / ((n - 1) * (n - 2))
                betweenness = {k: v * scale for k, v in betweenness.items()}

        return betweenness

    @staticmethod
    def eigenvector_centrality(
        adjacency: Dict[str, List[str]], iterations: int = 100, tolerance: float = 1e-6
    ) -> Dict[str, float]:
        """
        Compute eigenvector centrality using power iteration.

        x_i = (1/lambda) Σ A_ij x_j

        Args:
            adjacency: Node -> list of neighbors
            iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Dictionary mapping nodes to eigenvector centrality
        """
        # Collect ALL nodes — including those that appear only as targets.
        nodes_set = set(adjacency.keys())
        for neighbors in adjacency.values():
            nodes_set.update(neighbors)
        nodes = list(nodes_set)

        if not nodes:
            return {}

        # TODO: Eigenvector centrality is ill-defined for disconnected graphs.
        # The Perron-Frobenius theorem guarantees a unique positive leading
        # eigenvector only for strongly connected (or irreducible) graphs.
        # For disconnected graphs, smaller components may converge to zero.
        # Consider falling back to PageRank or warning the caller.
        # Reference: Newman, "Networks: An Introduction" (2010), Section 7.2.

        x = dict.fromkeys(nodes, 1.0)

        for _ in range(iterations):
            new_x = {}
            max_diff = 0.0

            for node in nodes:
                sum_neighbors = sum(x.get(nbr, 0.0) for nbr in adjacency.get(node, []))
                new_x[node] = sum_neighbors

            norm = math.sqrt(sum(v * v for v in new_x.values()))
            if norm > 0:
                new_x = {k: v / norm for k, v in new_x.items()}

            for node in nodes:
                diff = abs(new_x[node] - x[node])
                max_diff = max(max_diff, diff)

            x = new_x
            if max_diff < tolerance:
                break

        return x
