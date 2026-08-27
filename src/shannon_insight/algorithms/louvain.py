"""Louvain community detection with directed modularity.

Uses the directed modularity formula:
    Q = (1/m) * sum_{i,j} [A_ij - (k_i^out * k_j^in) / m] * delta(c_i, c_j)

where m = total edge weight, k_i^out = out-degree of i, k_j^in = in-degree of j.

NOTE: The _modularity_gain helper is O(n) per node per iteration, making
the overall algorithm O(n^2) per pass. For large graphs (>5000 nodes) consider
using the python-louvain or igraph libraries instead.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse


def louvain(
    A: sparse.csr_matrix,
    resolution: float = 1.0,
) -> tuple[dict[int, int], float]:
    """
    Louvain community detection using directed modularity.

    Args:
        A: Adjacency matrix (directed, weighted). A[i,j] = weight of edge i -> j.
        resolution: Resolution parameter (higher = smaller communities)

    Returns:
        - community: {node_idx: community_id}
        - modularity: Q score
    """
    n = A.shape[0]
    if n == 0:
        return {}, 0.0

    # Total edge weight (sum of all entries for directed graph)
    m = A.sum()
    if m == 0:
        return {i: i for i in range(n)}, 0.0

    # Out-degree: sum of row i (edges leaving i)
    k_out = np.array(A.sum(axis=1)).flatten()
    # In-degree: sum of column j (edges entering j)
    k_in = np.array(A.sum(axis=0)).flatten()

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

            # Find neighbors' communities (both in- and out-neighbors)
            out_neighbors = A[i].nonzero()[1]
            in_neighbors = A[:, i].nonzero()[0]
            neighbor_comms = {community[j] for j in out_neighbors}
            neighbor_comms.update(community[j] for j in in_neighbors)
            neighbor_comms.add(current_comm)

            best_comm = current_comm
            best_delta = 0.0

            # Compute gain of removing i from current community
            delta_remove = _modularity_gain_remove(
                A, k_out, k_in, m, i, current_comm, community, resolution
            )

            for c in neighbor_comms:
                if c == current_comm:
                    continue

                # Compute gain of adding i to community c
                delta_add = _modularity_gain_add(A, k_out, k_in, m, i, c, community, resolution)

                delta = delta_remove + delta_add
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
    Q = _compute_modularity(A, k_out, k_in, m, community, resolution)

    return community, Q


def _modularity_gain_remove(A, k_out, k_in, m, i, current_comm, community, resolution):
    """
    Compute the modularity gain from removing node i from its current community.

    This is the negative of the "contribution" of i being in current_comm,
    excluding self-loops (i's connection to itself doesn't change).

    gain_remove = -[sum_{j in C, j!=i} (A_ij + A_ji) / m
                    - resolution * (k_i^out * sum_{j in C, j!=i} k_j^in
                                  + k_i^in * sum_{j in C, j!=i} k_j^out) / m^2]
    """
    n = A.shape[0]
    # Edges from i to current community (excluding i itself)
    # and edges from current community to i (excluding i itself)
    edges_i_to_C = 0.0
    edges_C_to_i = 0.0
    sum_C_k_in = 0.0
    sum_C_k_out = 0.0

    for j in range(n):
        if j == i:
            continue
        if community[j] == current_comm:
            edges_i_to_C += A[i, j]
            edges_C_to_i += A[j, i]
            sum_C_k_in += k_in[j]
            sum_C_k_out += k_out[j]

    gain = -(
        (edges_i_to_C + edges_C_to_i) / m
        - resolution * (k_out[i] * sum_C_k_in + k_in[i] * sum_C_k_out) / (m * m)
    )
    return gain


def _modularity_gain_add(A, k_out, k_in, m, i, target_comm, community, resolution):
    """
    Compute the modularity gain from adding node i to target_comm.

    gain_add = [sum_{j in C} (A_ij + A_ji) / m
                - resolution * (k_i^out * sum_{j in C} k_j^in
                              + k_i^in * sum_{j in C} k_j^out) / m^2]
    """
    n = A.shape[0]
    edges_i_to_C = 0.0
    edges_C_to_i = 0.0
    sum_C_k_in = 0.0
    sum_C_k_out = 0.0

    for j in range(n):
        if community[j] == target_comm:
            edges_i_to_C += A[i, j]
            edges_C_to_i += A[j, i]
            sum_C_k_in += k_in[j]
            sum_C_k_out += k_out[j]

    gain = (edges_i_to_C + edges_C_to_i) / m - resolution * (
        k_out[i] * sum_C_k_in + k_in[i] * sum_C_k_out
    ) / (m * m)
    return gain


def _compute_modularity(A, k_out, k_in, m, community, resolution):
    """
    Compute directed modularity Q.

    Q = (1/m) * sum_{i,j} [A_ij - resolution * k_i^out * k_j^in / m] * delta(c_i, c_j)
    """
    Q = 0.0
    n = A.shape[0]
    for i in range(n):
        for j in range(n):
            if community[i] == community[j]:
                Q += A[i, j] - resolution * k_out[i] * k_in[j] / m
    return Q / m
