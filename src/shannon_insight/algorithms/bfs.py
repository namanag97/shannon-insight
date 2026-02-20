"""BFS-based algorithms.

NOTE: blast_radius() runs BFS from every node — O(n × (n+e)) time and O(n²) space.
For large codebases (>2000 files) this becomes a bottleneck. Consider sampling
or approximating blast radius instead.
"""
from __future__ import annotations

from collections import deque
import numpy as np
from scipy import sparse


def bfs_depth(
    A: sparse.csr_matrix,
    sources: set[int],
) -> dict[int, int]:
    """
    Compute shortest path distance from sources to all nodes.

    Args:
        A: Adjacency matrix
        sources: Set of source node indices

    Returns:
        {node: depth} where depth = -1 if unreachable
    """
    n = A.shape[0]
    depth = {i: -1 for i in range(n)}

    queue: deque[int] = deque()
    for s in sources:
        depth[s] = 0
        queue.append(s)

    while queue:
        u = queue.popleft()
        for v in A[u].nonzero()[1]:
            if depth[v] == -1:
                depth[v] = depth[u] + 1
                queue.append(v)

    return depth


def blast_radius(A: sparse.csr_matrix) -> dict[int, set[int]]:
    """
    Compute blast radius for each node (who is affected if this changes).

    Uses reverse edges: if A→B, then changing B affects A.
    """
    A_T = A.T.tocsr()
    n = A.shape[0]

    result: dict[int, set[int]] = {}
    for v in range(n):
        # BFS from v on reversed graph
        visited: set[int] = set()
        queue: deque[int] = deque([v])
        while queue:
            u = queue.popleft()
            for w in A_T[u].nonzero()[1]:
                if w not in visited and w != v:
                    visited.add(w)
                    queue.append(w)
        result[v] = visited

    return result
