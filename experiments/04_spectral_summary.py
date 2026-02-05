#!/usr/bin/env python3
"""Experiment 04 — Spectral Graph Theory: Dependency Graph Eigenanalysis.

Computes the Laplacian eigenvalues of the dependency graph and extracts
structural insights: connected components, algebraic connectivity,
spectral gap, Fiedler bipartition vs Louvain comparison.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import load_analysis


def ascii_histogram(values, bins=20, width=50, label=""):
    """Render a simple ASCII histogram."""
    if not len(values):
        return "  (no data)"

    lo, hi = float(min(values)), float(max(values))
    if lo == hi:
        return f"  All values = {lo:.4f}"

    bin_edges = np.linspace(lo, hi, bins + 1)
    counts, _ = np.histogram(values, bins=bin_edges)
    max_count = max(counts) if max(counts) > 0 else 1

    lines = []
    if label:
        lines.append(f"  {label}")
    for i, count in enumerate(counts):
        bar_len = int(count / max_count * width)
        bar = "#" * bar_len
        lines.append(f"  [{bin_edges[i]:>8.4f}, {bin_edges[i+1]:>8.4f}) |{bar} ({count})")
    return "\n".join(lines)


def main():
    codebase = sys.argv[1] if len(sys.argv) > 1 else "."
    result, file_metrics = load_analysis(codebase)

    graph = result.graph
    ga = result.graph_analysis
    nodes = sorted(graph.all_nodes)
    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    print("=" * 72)
    print("EXPERIMENT 04 — SPECTRAL GRAPH SUMMARY")
    print("=" * 72)
    print()
    print(f"Graph: {n} nodes, {graph.edge_count} directed edges")
    print()

    if n < 2:
        print("Graph too small for spectral analysis.")
        return

    # ── Build adjacency matrix (undirected) ─────────────────────
    A = np.zeros((n, n), dtype=float)
    for src, targets in graph.adjacency.items():
        i = node_idx.get(src)
        if i is None:
            continue
        for tgt in targets:
            j = node_idx.get(tgt)
            if j is not None:
                A[i, j] = 1.0
                A[j, i] = 1.0  # Treat as undirected

    # ── Laplacian: L = D - A ────────────────────────────────────
    D = np.diag(A.sum(axis=1))
    L = D - A

    # ── Eigendecomposition ──────────────────────────────────────
    eigenvalues, eigenvectors = np.linalg.eigh(L)

    # Sort by eigenvalue (should already be sorted, but ensure)
    order = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    # ── Report ──────────────────────────────────────────────────
    print("1. EIGENVALUE SUMMARY")
    print("-" * 72)

    # Connected components = number of zero eigenvalues
    zero_threshold = 1e-8
    n_zero = np.sum(np.abs(eigenvalues) < zero_threshold)
    print(f"  Zero eigenvalues: {n_zero} (= number of connected components)")

    # Fiedler value (2nd smallest eigenvalue)
    fiedler_val = eigenvalues[1] if n >= 2 else 0
    print(f"  Fiedler value (lambda_2): {fiedler_val:.6f}")
    if fiedler_val < 0.01:
        print("    -> Near zero: graph is barely connected or has bottleneck")
    elif fiedler_val < 0.5:
        print("    -> Moderate: graph has some clear cluster separation")
    else:
        print("    -> High: graph is well-connected, hard to partition")

    # Spectral gap
    if n >= 3 and eigenvalues[2] > zero_threshold:
        spectral_gap = eigenvalues[1] / eigenvalues[2]
        print(f"  Spectral gap (lambda_2 / lambda_3): {spectral_gap:.4f}")
        if spectral_gap > 0.8:
            print("    -> Close to 1: no strong 2-way split")
        elif spectral_gap > 0.3:
            print("    -> Moderate: some 2-community structure")
        else:
            print("    -> Small: strong 2-community separation")
    else:
        spectral_gap = 0
        print("  Spectral gap: N/A (lambda_3 is zero)")

    # Largest eigenvalue
    print(f"  Largest eigenvalue: {eigenvalues[-1]:.4f}")
    print(f"  Trace (sum of eigenvalues): {sum(eigenvalues):.4f} (= 2 * edges in undirected)")
    print()

    # ── Eigenvalue histogram ────────────────────────────────────
    print("2. EIGENVALUE DISTRIBUTION")
    print("-" * 72)
    # Filter out the zero eigenvalues for a better histogram
    nonzero_eigs = eigenvalues[eigenvalues > zero_threshold]
    if len(nonzero_eigs) > 0:
        n_bins = min(20, len(nonzero_eigs))
        print(ascii_histogram(nonzero_eigs, bins=n_bins, label="Non-zero eigenvalues"))
    else:
        print("  All eigenvalues are zero (fully disconnected graph).")
    print()

    # ── Top eigenvalues ─────────────────────────────────────────
    print("3. FIRST 10 EIGENVALUES")
    print("-" * 72)
    for i in range(min(10, n)):
        marker = " <-- Fiedler" if i == 1 else ""
        print(f"  lambda_{i:<3} = {eigenvalues[i]:>10.6f}{marker}")
    print()

    # ── Fiedler Vector Bipartition ──────────────────────────────
    print("4. FIEDLER VECTOR BIPARTITION")
    print("-" * 72)

    if n < 2:
        print("  Too few nodes for bipartition.")
    else:
        fiedler_vec = eigenvectors[:, 1]

        # Partition by sign
        group_pos = [nodes[i] for i in range(n) if fiedler_vec[i] >= 0]
        group_neg = [nodes[i] for i in range(n) if fiedler_vec[i] < 0]

        print(f"  Positive partition: {len(group_pos)} files")
        print(f"  Negative partition: {len(group_neg)} files")
        print()

        # Compare with Louvain communities
        print("5. FIEDLER vs LOUVAIN COMPARISON")
        print("-" * 72)

        louvain_map = ga.node_community  # file -> community_id

        # Map Fiedler partition to labels
        fiedler_labels = {}
        for node in group_pos:
            fiedler_labels[node] = 0
        for node in group_neg:
            fiedler_labels[node] = 1

        # For each Louvain community, see how it splits across Fiedler partitions
        louvain_comms = {}
        for node, cid in louvain_map.items():
            louvain_comms.setdefault(cid, []).append(node)

        # Compute overlap: for each Louvain community, what fraction is in one
        # Fiedler partition?
        total_agreement = 0
        total_nodes_checked = 0
        print(f"  {'Louvain Community':<20} {'Size':>5} {'Fiedler+':>9} {'Fiedler-':>9} {'Purity':>8}")
        print(f"  {'-'*20} {'-----':>5} {'---------':>9} {'---------':>9} {'--------':>8}")

        for cid in sorted(louvain_comms.keys()):
            members = louvain_comms[cid]
            in_pos = sum(1 for m in members if fiedler_labels.get(m, 0) == 0)
            in_neg = len(members) - in_pos
            purity = max(in_pos, in_neg) / len(members)
            total_agreement += max(in_pos, in_neg)
            total_nodes_checked += len(members)
            print(f"  Community {cid:<10} {len(members):>5} {in_pos:>9} {in_neg:>9} {purity:>8.2f}")

        if total_nodes_checked > 0:
            overall = total_agreement / total_nodes_checked
            print()
            print(f"  Overall purity (how well Fiedler matches Louvain): {overall:.2%}")
            if overall > 0.8:
                print("  -> High agreement: community structure is fundamentally 2-way.")
            elif overall > 0.6:
                print("  -> Moderate: Louvain finds sub-structure within Fiedler halves.")
            else:
                print("  -> Low: community structure is multi-way, not captured by 2-partition.")

    print()


if __name__ == "__main__":
    main()
