#!/usr/bin/env python3
"""Experiment 07 — Topology: Persistent Homology of Dependency Neighborhoods.

Defines Jaccard distance between files based on dependency neighborhoods,
computes simplified persistent homology (H0 via union-find), and compares
persistent clusters with Louvain communities.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import load_analysis


# ── Union-Find ──────────────────────────────────────────────────

class UnionFind:
    """Weighted quick-union with path compression."""

    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}
        self.n_components = len(elements)

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # Path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # Already connected
        # Union by rank
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.n_components -= 1
        return True  # Merged


def jaccard_distance(set_a, set_b):
    """Jaccard distance: 1 - |A ∩ B| / |A ∪ B|."""
    if not set_a and not set_b:
        return 1.0  # Both empty → maximally dissimilar
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return 1.0 - intersection / union if union > 0 else 1.0


def main():
    codebase = sys.argv[1] if len(sys.argv) > 1 else "."
    result, file_metrics = load_analysis(codebase)

    graph = result.graph
    ga = result.graph_analysis
    nodes = sorted(graph.all_nodes)
    n = len(nodes)

    print("=" * 72)
    print("EXPERIMENT 07 — PERSISTENT HOMOLOGY OF DEPENDENCY NEIGHBORHOODS")
    print("=" * 72)
    print()
    print(f"Files: {n}")
    print()

    if n < 3:
        print("Too few files for topological analysis.")
        return

    # ── 1. Build dependency neighborhoods ───────────────────────
    neighborhoods = {}
    for node in nodes:
        imports = set(graph.adjacency.get(node, []))
        imported_by = set(graph.reverse.get(node, []))
        neighborhoods[node] = imports | imported_by

    # ── 2. Compute distance matrix ──────────────────────────────
    node_idx = {node: i for i, node in enumerate(nodes)}
    dist_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            d = jaccard_distance(neighborhoods[nodes[i]], neighborhoods[nodes[j]])
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d

    print("1. DISTANCE MATRIX SUMMARY")
    print("-" * 72)

    # Extract upper triangle (excluding diagonal)
    upper = dist_matrix[np.triu_indices(n, k=1)]
    print(f"  Total pairwise distances: {len(upper)}")
    print(f"  Min distance: {np.min(upper):.4f}")
    print(f"  Max distance: {np.max(upper):.4f}")
    print(f"  Mean distance: {np.mean(upper):.4f}")
    print(f"  Median distance: {np.median(upper):.4f}")

    # Count pairs at distance 1.0 (completely dissimilar neighborhoods)
    n_max_dist = np.sum(upper >= 0.9999)
    n_near = np.sum(upper < 0.5)
    print(f"  Pairs at distance ~1.0 (no shared neighbors): {n_max_dist} ({n_max_dist/len(upper):.1%})")
    print(f"  Pairs at distance < 0.5 (similar neighborhoods): {n_near} ({n_near/len(upper):.1%})")
    print()

    # ── 3. Vietoris-Rips filtration (H0 via union-find) ────────
    print("2. PERSISTENT HOMOLOGY (H0 — CONNECTED COMPONENTS)")
    print("-" * 72)

    # Collect all pairwise distances and sort
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((dist_matrix[i, j], i, j))
    edges.sort()

    # Run union-find filtration
    uf = UnionFind(range(n))
    persistence_h0 = []  # (birth, death) pairs for H0 features
    component_birth = {i: 0.0 for i in range(n)}  # All born at threshold 0

    for dist_val, i, j in edges:
        ri, rj = uf.find(i), uf.find(j)
        if ri != rj:
            # One component dies (the younger one)
            merged = uf.union(i, j)
            if merged:
                # The component that dies was born at 0 and dies at dist_val
                persistence_h0.append((0.0, dist_val))

    # The final surviving component has infinite persistence
    # (born at 0, never dies)

    # Sort by persistence (death - birth), longest-lived first
    persistence_h0.sort(key=lambda x: -(x[1] - x[0]))

    print(f"  H0 features (component merges): {len(persistence_h0)}")
    if persistence_h0:
        print(f"  Most persistent (longest-lived components):")
        for i, (birth, death) in enumerate(persistence_h0[:10]):
            pers = death - birth
            bar = "#" * int(pers * 40)
            print(f"    Feature {i}: birth={birth:.3f} death={death:.3f} persistence={pers:.3f} |{bar}")

    print()

    # ── 4. Persistence Diagram (ASCII) ──────────────────────────
    print("3. PERSISTENCE DIAGRAM (ASCII)")
    print("-" * 72)
    print("  death")
    print("  1.0 |", end="")

    # Create a 20x40 grid
    rows, cols = 16, 40
    grid = [[" " for _ in range(cols)] for _ in range(rows)]

    # Plot diagonal
    for r in range(rows):
        c = int(r / rows * cols)
        if c < cols:
            grid[rows - 1 - r][c] = "."

    # Plot persistence points
    for birth, death in persistence_h0:
        r = int(death * (rows - 1))
        c = int(birth * (cols - 1))
        r = min(r, rows - 1)
        c = min(c, cols - 1)
        grid[rows - 1 - r][c] = "*"

    for r in range(rows):
        val = 1.0 - r / (rows - 1)
        if r == 0:
            print("".join(grid[r]))
        elif r == rows - 1:
            print(f"  0.0 |{''.join(grid[r])}")
        else:
            if r % 4 == 0:
                print(f"  {val:.1f} |{''.join(grid[r])}")
            else:
                print(f"      |{''.join(grid[r])}")

    print(f"      +{'-' * cols}")
    print(f"       0.0{'birth':>{cols - 3}}")
    print()
    print("  * = H0 feature (component merge)")
    print("  . = diagonal (birth = death, zero persistence)")
    print("  Points far from diagonal = real structure (long-lived features)")
    print()

    # ── 5. Cluster comparison with Louvain ──────────────────────
    print("4. PERSISTENT CLUSTERS vs LOUVAIN COMMUNITIES")
    print("-" * 72)

    # Find the "best" threshold: the one that maximizes the gap between
    # consecutive deaths (largest jump in persistence deaths)
    if len(persistence_h0) >= 2:
        deaths = sorted(set(d for _, d in persistence_h0))
        if len(deaths) >= 2:
            gaps = [(deaths[i + 1] - deaths[i], deaths[i]) for i in range(len(deaths) - 1)]
            gaps.sort(reverse=True)
            best_threshold = gaps[0][1] + gaps[0][0] / 2  # Midpoint of largest gap
        else:
            best_threshold = deaths[0] / 2
    else:
        best_threshold = 0.5

    print(f"  Chosen filtration threshold: {best_threshold:.4f}")
    print(f"  (largest gap in death times)")

    # Build clusters at this threshold
    uf_cluster = UnionFind(range(n))
    for dist_val, i, j in edges:
        if dist_val > best_threshold:
            break
        uf_cluster.union(i, j)

    topo_clusters = {}
    for i in range(n):
        root = uf_cluster.find(i)
        topo_clusters.setdefault(root, []).append(nodes[i])

    # Remove singletons for display
    topo_clusters = {k: v for k, v in topo_clusters.items() if len(v) > 1}

    n_topo = len(topo_clusters) + (n - sum(len(v) for v in topo_clusters.values()))
    print(f"  Topological clusters (non-singleton): {len(topo_clusters)}")
    print(f"  Total components at threshold: {uf_cluster.n_components}")

    # Louvain communities
    louvain_comms = {}
    for node, cid in ga.node_community.items():
        louvain_comms.setdefault(cid, []).append(node)

    print(f"  Louvain communities: {len(louvain_comms)}")
    print()

    # Compute overlap using normalized mutual information (simplified)
    # For each topological cluster, find the Louvain community with maximum overlap
    if topo_clusters:
        total_overlap = 0
        total_files_in_clusters = 0

        print(f"  {'Topo Cluster':<15} {'Size':>5} {'Best Louvain':>15} {'Overlap':>8} {'Purity':>8}")
        print(f"  {'-'*15} {'-----':>5} {'-'*15} {'--------':>8} {'--------':>8}")

        for idx, (root, members) in enumerate(
            sorted(topo_clusters.items(), key=lambda x: -len(x[1]))[:10]
        ):
            member_set = set(members)
            best_cid = -1
            best_overlap = 0

            for cid, louvain_members in louvain_comms.items():
                overlap = len(member_set & set(louvain_members))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_cid = cid

            purity = best_overlap / len(members) if members else 0
            total_overlap += best_overlap
            total_files_in_clusters += len(members)

            print(f"  Cluster {idx:<6} {len(members):>5} {'Community ' + str(best_cid):>15} {best_overlap:>8} {purity:>8.2f}")

        if total_files_in_clusters > 0:
            overall_purity = total_overlap / total_files_in_clusters
            print()
            print(f"  Overall purity: {overall_purity:.2%}")
            if overall_purity > 0.8:
                print("  -> High overlap: topological and graph-theoretic communities agree.")
                print("     The dependency structure has genuine geometric clustering.")
            elif overall_purity > 0.5:
                print("  -> Moderate overlap: topology captures some but not all Louvain structure.")
            else:
                print("  -> Low overlap: neighborhood similarity gives a different view than modularity.")
    else:
        print("  No non-singleton topological clusters formed at this threshold.")
        print("  Files have highly dissimilar dependency neighborhoods.")

    print()

    # ── Summary ─────────────────────────────────────────────────
    print("5. TOPOLOGICAL SUMMARY")
    print("-" * 72)

    if persistence_h0:
        # Count "significant" features (persistence > median)
        persistences = [d - b for b, d in persistence_h0]
        med_pers = sorted(persistences)[len(persistences) // 2]
        significant = sum(1 for p in persistences if p > med_pers)

        print(f"  Median persistence: {med_pers:.4f}")
        print(f"  Features above median: {significant}")
        print(f"  These represent genuine structural clusters in dependency space.")
        print(f"  Short-lived features (below median) are noise or weak couplings.")
    else:
        print("  No H0 features to analyze.")

    print()


if __name__ == "__main__":
    main()
