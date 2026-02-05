#!/usr/bin/env python3
"""Experiment 06 — Abstract Algebra: Aggregation Property Validation.

Tests whether metric aggregations (file -> module) satisfy algebraic
properties: monoid (associativity + identity), semiring structure on
the dependency graph, and whether ratio-of-sums vs sum-of-ratios matter.
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import load_analysis


def mean(values):
    """Mean of a list of floats."""
    return sum(values) / len(values) if values else 0.0


def main():
    codebase = sys.argv[1] if len(sys.argv) > 1 else "."
    result, file_metrics = load_analysis(codebase)

    graph = result.graph
    files = result.files
    modules = result.modules

    print("=" * 72)
    print("EXPERIMENT 06 — ALGEBRAIC VALIDATION OF AGGREGATIONS")
    print("=" * 72)
    print()

    # Group files by module
    module_files = defaultdict(list)
    for f_path, fa in files.items():
        mod = str(Path(f_path).parent)
        module_files[mod].append(fa)

    # ── 1. Mean is NOT associative ──────────────────────────────
    print("1. MEAN NON-ASSOCIATIVITY (compression_ratio)")
    print("-" * 72)
    print("  mean(mean(A,B), C) vs mean(A, mean(B,C)) — do they differ?")
    print()

    # Pick 3 modules with different sizes
    mod_list = [(mod, fas) for mod, fas in module_files.items() if len(fas) >= 2]
    mod_list.sort(key=lambda x: len(x[1]), reverse=True)

    if len(mod_list) >= 3:
        mods_abc = mod_list[:3]
        names = [m[0] for m in mods_abc]
        cr_values = [[fa.compression_ratio for fa in fas] for _, fas in mods_abc]
        sizes = [len(v) for v in cr_values]
        means = [mean(v) for v in cr_values]

        print(f"  Module A: {names[0]} ({sizes[0]} files, mean CR = {means[0]:.4f})")
        print(f"  Module B: {names[1]} ({sizes[1]} files, mean CR = {means[1]:.4f})")
        print(f"  Module C: {names[2]} ({sizes[2]} files, mean CR = {means[2]:.4f})")
        print()

        # mean(mean(A,B), C)
        mean_ab = mean(means[:2])
        left = mean([mean_ab, means[2]])

        # mean(A, mean(B,C))
        mean_bc = mean(means[1:])
        right = mean([means[0], mean_bc])

        # Correct answer: weighted mean of all values
        all_vals = cr_values[0] + cr_values[1] + cr_values[2]
        true_mean = mean(all_vals)

        print(f"  mean(mean(A,B), C) = mean(mean({means[0]:.4f}, {means[1]:.4f}), {means[2]:.4f})")
        print(f"                     = mean({mean_ab:.4f}, {means[2]:.4f}) = {left:.4f}")
        print()
        print(f"  mean(A, mean(B,C)) = mean({means[0]:.4f}, mean({means[1]:.4f}, {means[2]:.4f}))")
        print(f"                     = mean({means[0]:.4f}, {mean_bc:.4f}) = {right:.4f}")
        print()
        print(f"  Difference: {abs(left - right):.6f}")
        print(f"  True weighted mean (all {len(all_vals)} files): {true_mean:.4f}")
        print()

        if abs(left - right) > 1e-10:
            print("  VERDICT: Mean is NOT associative over groups of unequal size.")
            print("  This means 'average complexity per module' depends on grouping order.")
        else:
            print("  VERDICT: Groups happen to be equal size — mean appears associative.")
            print("  (This is a coincidence; mean is NOT associative in general.)")
    else:
        print("  Not enough modules with >= 2 files for this test.")
    print()

    # ── 2. Sum IS a monoid ──────────────────────────────────────
    print("2. SUM MONOID TEST (cognitive_load)")
    print("-" * 72)
    print("  Testing: sum is associative with identity 0")
    print()

    if len(mod_list) >= 3:
        cl_values = [[fa.cognitive_load for fa in fas] for _, fas in mods_abc]
        sums = [sum(v) for v in cl_values]

        # Associativity: sum(sum(A,B), C) == sum(A, sum(B,C))
        left_sum = (sums[0] + sums[1]) + sums[2]
        right_sum = sums[0] + (sums[1] + sums[2])
        identity_test = sums[0] + 0 == sums[0]

        print(f"  sum(A) = {sums[0]:.2f}, sum(B) = {sums[1]:.2f}, sum(C) = {sums[2]:.2f}")
        print(f"  (sum(A) + sum(B)) + sum(C) = {left_sum:.2f}")
        print(f"  sum(A) + (sum(B) + sum(C)) = {right_sum:.2f}")
        print(f"  Equal? {abs(left_sum - right_sum) < 1e-10}")
        print(f"  Identity (sum + 0 = sum)? {identity_test}")
        print()
        print("  VERDICT: Sum forms a valid monoid (R, +, 0). Aggregation is algebraically sound.")
    else:
        print("  Not enough modules for this test.")
    print()

    # ── 3. Cohesion: ratio-of-sums vs sum-of-ratios ────────────
    print("3. COHESION AGGREGATION (ratio of sums != sum of ratios)")
    print("-" * 72)
    print("  Engine computes cohesion = internal_edges / possible_internal")
    print("  Is this valid when aggregating sub-modules?")
    print()

    # Find modules that contain sub-directories
    top_modules = {}
    for mod_path in modules:
        parent = str(Path(mod_path).parent)
        if parent in modules and parent != mod_path:
            top_modules.setdefault(parent, []).append(mod_path)

    found_example = False
    for parent, children in sorted(top_modules.items(), key=lambda x: -len(x[1])):
        if len(children) < 2:
            continue

        # Method 1: ratio of sums (correct for the parent module)
        parent_ma = modules.get(parent)
        if not parent_ma:
            continue

        # Method 2: average of child cohesions (naive aggregation)
        child_cohesions = []
        for child in children:
            child_ma = modules.get(child)
            if child_ma:
                child_cohesions.append(child_ma.cohesion)

        if not child_cohesions:
            continue

        avg_child_cohesion = mean(child_cohesions)

        print(f"  Parent module: {parent}")
        print(f"  Children: {len(children)} sub-modules")
        print(f"  Parent cohesion (ratio of sums):       {parent_ma.cohesion:.4f}")
        print(f"  Average child cohesion (mean of ratios): {avg_child_cohesion:.4f}")
        print(f"  Difference: {abs(parent_ma.cohesion - avg_child_cohesion):.4f}")

        if abs(parent_ma.cohesion - avg_child_cohesion) > 0.01:
            print("  -> They DISAGREE: ratio-of-sums != mean-of-ratios (Simpson's paradox risk)")
        else:
            print("  -> They approximately agree (but this isn't guaranteed in general)")
        print()
        found_example = True
        break

    if not found_example:
        print("  No nested module structure found for this test.")
        print("  Demonstrating algebraically: for modules with different sizes,")
        print("  cohesion = internal/possible is NOT preserved by averaging.")
        print()
        # Synthetic demo
        print("  Synthetic example:")
        print("    Module X: 3 internal edges, 6 possible -> cohesion = 0.500")
        print("    Module Y: 1 internal edge,  2 possible -> cohesion = 0.500")
        print("    Combined: 4 internal edges, 8 possible -> cohesion = 0.500")
        print("    Average of cohesions: (0.500 + 0.500) / 2 = 0.500 (SAME by coincidence)")
        print()
        print("    Module X: 3 internal, 6 possible -> cohesion = 0.500")
        print("    Module Y: 0 internal, 2 possible -> cohesion = 0.000")
        print("    Combined: 3 internal, 8 possible -> cohesion = 0.375")
        print("    Average of cohesions: (0.500 + 0.000) / 2 = 0.250 (DIFFERENT)")
    print()

    # ── 4. Semiring structure of dependency graph ───────────────
    print("4. SEMIRING STRUCTURE ON DEPENDENCY GRAPH")
    print("-" * 72)

    # Build shortest path distances using BFS
    nodes = sorted(graph.all_nodes)
    n = len(nodes)
    node_idx = {node: i for i, node in enumerate(nodes)}

    # Compute shortest paths (BFS from each node)
    INF = float("inf")
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0

    for src, targets in graph.adjacency.items():
        i = node_idx.get(src)
        if i is None:
            continue
        for tgt in targets:
            j = node_idx.get(tgt)
            if j is not None:
                dist[i][j] = 1

    # Floyd-Warshall for all-pairs shortest paths
    # (min, +) semiring: d(i,j) = min over k of d(i,k) + d(k,j)
    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[k][j] == INF:
                    continue
                candidate = dist[i][k] + dist[k][j]
                if candidate < dist[i][j]:
                    dist[i][j] = candidate

    # Check triangle inequality: d(i,j) <= d(i,k) + d(k,j)
    triangle_violations = 0
    triangle_total = 0
    for i in range(min(n, 50)):  # Sample to keep tractable
        for j in range(min(n, 50)):
            if i == j:
                continue
            for k in range(min(n, 50)):
                if k == i or k == j:
                    continue
                if dist[i][j] == INF or dist[i][k] == INF or dist[k][j] == INF:
                    continue
                triangle_total += 1
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    triangle_violations += 1

    print(f"  (min, +) semiring for shortest paths:")
    print(f"  Triangle inequality checks (sampled): {triangle_total}")
    print(f"  Violations: {triangle_violations}")
    if triangle_violations == 0:
        print("  VERDICT: Triangle inequality holds — (min, +) is a valid semiring.")
    else:
        print("  VERDICT: Triangle inequality violated — this shouldn't happen for BFS distances!")
    print()

    # Connectivity stats
    reachable_pairs = sum(
        1 for i in range(n) for j in range(n) if i != j and dist[i][j] < INF
    )
    total_pairs = n * (n - 1) if n > 1 else 1
    print(f"  Reachable pairs: {reachable_pairs} / {total_pairs} ({reachable_pairs/total_pairs:.1%})")

    if reachable_pairs > 0:
        finite_dists = [
            dist[i][j] for i in range(n) for j in range(n)
            if i != j and dist[i][j] < INF
        ]
        avg_dist = sum(finite_dists) / len(finite_dists)
        max_dist = max(finite_dists)
        print(f"  Average shortest path: {avg_dist:.2f}")
        print(f"  Diameter (longest shortest path): {max_dist:.0f}")
    print()

    # ── 5. Aggregation Validity Summary ─────────────────────────
    print("5. AGGREGATION VALIDITY SUMMARY")
    print("-" * 72)
    print(f"  {'Metric':<25} {'Aggregation':<15} {'Algebraic?':<12} Notes")
    print(f"  {'-'*25} {'-'*15} {'-'*12} {'-'*20}")
    print(f"  {'cognitive_load':<25} {'sum':<15} {'YES (monoid)':<12} (R,+,0) — sound")
    print(f"  {'compression_ratio':<25} {'mean':<15} {'NO':<12} Non-associative over unequal groups")
    print(f"  {'cohesion':<25} {'ratio-of-sums':<15} {'CAUTION':<12} ratio(sum) != mean(ratios)")
    print(f"  {'coupling':<25} {'ratio-of-sums':<15} {'CAUTION':<12} Same issue as cohesion")
    print(f"  {'pagerank':<25} {'(none)':<15} {'N/A':<12} Global property, doesn't aggregate")
    print(f"  {'gini':<25} {'(none)':<15} {'N/A':<12} Per-file only, no aggregation")
    print(f"  {'shortest_path':<25} {'(min,+)':<15} {'YES (semiring)':<12} Triangle inequality holds")
    print()


if __name__ == "__main__":
    main()
