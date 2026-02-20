"""Strongly connected components (Tarjan's algorithm).

NOTE: The recursive implementation will hit Python's default recursion limit
(sys.setrecursionlimit default ~1000) for large dense graphs. For graphs with
>1000 nodes, consider using scipy.sparse.csgraph.connected_components instead.
"""
from __future__ import annotations

import sys
from scipy import sparse


def tarjan_scc(A: sparse.csr_matrix) -> list[set[int]]:
    """
    Find strongly connected components.

    Args:
        A: Adjacency matrix (directed)

    Returns:
        List of SCCs, each as a set of node indices
    """
    n = A.shape[0]
    if n == 0:
        return []

    index_counter = [0]
    stack: list[int] = []
    lowlinks: dict[int, int] = {}
    index: dict[int, int] = {}
    on_stack: set[int] = set()
    sccs: list[set[int]] = []

    def strongconnect(v: int) -> None:
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        # Visit successors
        for w in A[v].nonzero()[1]:
            if w not in index:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], index[w])

        # Root of SCC
        if lowlinks[v] == index[v]:
            scc: set[int] = set()
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.add(w)
                if w == v:
                    break
            sccs.append(scc)

    # Increase recursion limit temporarily for large graphs
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, n * 2 + 100))
    try:
        for v in range(n):
            if v not in index:
                strongconnect(v)
    finally:
        sys.setrecursionlimit(old_limit)

    return sccs


def find_cycles(A: sparse.csr_matrix) -> tuple[list[set[int]], dict[int, bool]]:
    """
    Find SCCs and mark nodes in cycles.

    Returns:
        - cycles: List of SCCs with size > 1
        - cycle_member: {node: True if in a cycle}
    """
    sccs = tarjan_scc(A)
    cycles = [scc for scc in sccs if len(scc) > 1]

    cycle_member: dict[int, bool] = {}
    for i in range(A.shape[0]):
        cycle_member[i] = any(i in scc for scc in cycles)

    return cycles, cycle_member
