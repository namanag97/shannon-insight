"""Louvain community detection.

NOTE: The _modularity_gain helper is O(n) per node per iteration, making
the overall algorithm O(n²) per pass. For large graphs (>5000 nodes) consider
using the python-louvain or igraph libraries instead.
"""
from __future__ import annotations

import numpy as np
from scipy import sparse
from collections import defaultdict


def louvain(
    A: sparse.csr_matrix,
    resolution: float = 1.0,
) -> tuple[dict[int, int], float]:
    """
    Louvain community detection.

    Args:
        A: Adjacency matrix (symmetric, weighted)
        resolution: Resolution parameter (higher = smaller communities)

    Returns:
        - community: {node_idx: community_id}
        - modularity: Q score
    """
    n = A.shape[0]
    if n == 0:
        return {}, 0.0

    # Make symmetric
    A = (A + A.T) / 2

    # Total edge weight
    m = A.sum() / 2
    if m == 0:
        return {i: i for i in range(n)}, 0.0

    # Degree
    k = np.array(A.sum(axis=1)).flatten()

    # Initialize: each node in own community
    community = {i: i for i in range(n)}

    # Phase 1: Local moving
    improved = True
    while improved:
        improved = False
        nodes = list(range(n))
        np.random.shuffle(nodes)

        for i in nodes:
            current_comm = community[i]

            # Find neighbors' communities
            neighbors = A[i].nonzero()[1]
            neighbor_comms = set(community[j] for j in neighbors)
            neighbor_comms.add(current_comm)

            best_comm = current_comm
            best_delta = 0.0

            for c in neighbor_comms:
                if c == current_comm:
                    continue

                # Compute modularity gain
                delta = _modularity_gain(A, k, m, i, c, community, resolution)
                if delta > best_delta:
                    best_delta = delta
                    best_comm = c

            if best_comm != current_comm:
                community[i] = best_comm
                improved = True

    # Renumber communities
    unique_comms = sorted(set(community.values()))
    comm_map = {c: i for i, c in enumerate(unique_comms)}
    community = {i: comm_map[c] for i, c in community.items()}

    # Compute final modularity
    Q = _compute_modularity(A, k, m, community, resolution)

    return community, Q


def _modularity_gain(A, k, m, i, target_comm, community, resolution):
    """Compute modularity gain from moving node i to target_comm."""
    # Sum of weights from i to target community
    k_i_in = sum(A[i, j] for j in range(A.shape[0]) if community[j] == target_comm)

    # Sum of degrees in target community
    sum_tot = sum(k[j] for j in range(A.shape[0]) if community[j] == target_comm)

    return k_i_in - resolution * k[i] * sum_tot / (2 * m)


def _compute_modularity(A, k, m, community, resolution):
    """Compute modularity Q."""
    Q = 0.0
    for i in range(A.shape[0]):
        for j in range(A.shape[0]):
            if community[i] == community[j]:
                Q += A[i, j] - resolution * k[i] * k[j] / (2 * m)
    return Q / (2 * m)
