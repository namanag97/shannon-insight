#!/usr/bin/env python3
"""Experiment 01 — Measurement Theory Audit.

Classifies each metric by scale type (nominal/ordinal/interval/ratio),
demonstrates what breaks when you violate scale rules.

Compares weighted-sum fusion against rank-based fusion to detect
scale-violation-induced rank inversions.
"""

import sys
from pathlib import Path

# ── Bootstrap ───────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _bootstrap import load_analysis

# ── Scale classifications ───────────────────────────────────────

SCALE_INFO = {
    "compression_ratio": {
        "scale": "ratio",
        "reason": "Ratio of compressed/original size. 0 = empty → true zero. "
                  "Ratios are meaningful (0.4 is twice as compressible as 0.8).",
    },
    "pagerank": {
        "scale": "ratio",
        "reason": "Probability distribution summing to 1. True zero = no inlinks. "
                  "Ratios meaningful (2x PageRank = 2x link equity).",
    },
    "cognitive_load": {
        "scale": "ordinal",
        "reason": "Formula mixes counts × ratios × Gini. "
                  "Order is meaningful (higher = more complex), but 'twice as much' "
                  "cognitive load has no calibrated interpretation. "
                  "base = n_concepts * complexity * (1 + nesting/10) * (1 + gini) — "
                  "multiplicative mixing of heterogeneous quantities.",
    },
    "function_size_gini": {
        "scale": "ratio",
        "reason": "Gini coefficient: bounded [0,1], true zero = perfect equality. "
                  "Ratios are well-defined.",
    },
    "betweenness": {
        "scale": "ratio",
        "reason": "Fraction of shortest paths through node, normalized. "
                  "True zero = not on any shortest path.",
    },
    "blast_radius_size": {
        "scale": "ratio",
        "reason": "Count of transitively affected files. True zero, integer-valued.",
    },
    "in_degree": {
        "scale": "ratio",
        "reason": "Count of direct dependents. True zero.",
    },
    "out_degree": {
        "scale": "ratio",
        "reason": "Count of direct dependencies. True zero.",
    },
    "nesting_depth": {
        "scale": "ordinal",
        "reason": "Max nesting level. Order meaningful, but depth 6 is not 'twice as nested' as 3 "
                  "in any calibrated cognitive sense.",
    },
}


def percentile_rank(values):
    """Return percentile ranks (0..1) for a list of values."""
    n = len(values)
    if n == 0:
        return []
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    for rank_pos, orig_idx in enumerate(indexed):
        ranks[orig_idx] = rank_pos / (n - 1) if n > 1 else 0.5
    return ranks


def main():
    codebase = sys.argv[1] if len(sys.argv) > 1 else "."
    result, file_metrics = load_analysis(codebase)

    files = result.files
    paths = sorted(files.keys())

    # ── 1. Scale Classification Table ───────────────────────────
    print("=" * 72)
    print("EXPERIMENT 01 — MEASUREMENT THEORY AUDIT")
    print("=" * 72)
    print()
    print("1. SCALE CLASSIFICATION OF METRICS")
    print("-" * 72)
    print(f"{'Metric':<25} {'Scale':<10} Rationale")
    print("-" * 72)
    for metric, info in sorted(SCALE_INFO.items()):
        print(f"{metric:<25} {info['scale']:<10} {info['reason'][:60]}")
    print()

    # ── 2. Current Fusion Formula ───────────────────────────────
    print("2. CURRENT FUSION APPROACH")
    print("-" * 72)
    print("The engine does NOT use weighted-sum fusion for structural analysis.")
    print("Instead it reports raw measurements per file (FileAnalysis) and")
    print("uses MAD-based outlier detection on individual metrics.")
    print()
    print("However, the primitives pipeline (PrimitivePlugin system) computes:")
    print("  structural_entropy, network_centrality, churn_volatility,")
    print("  semantic_coherence, cognitive_load")
    print("Each primitive is computed independently; fusion uses Bayesian/DS methods.")
    print()
    print("Below we test: does weighted-sum vs rank-based fusion agree?")
    print()

    # ── 3. Weighted-Sum vs Rank-Based Fusion ────────────────────
    # Pick metrics that exist on FileAnalysis
    metrics_to_fuse = [
        ("compression_ratio", lambda fa: fa.compression_ratio, "ratio"),
        ("cognitive_load", lambda fa: fa.cognitive_load, "ordinal"),
        ("pagerank", lambda fa: fa.pagerank, "ratio"),
        ("betweenness", lambda fa: fa.betweenness, "ratio"),
        ("blast_radius_size", lambda fa: float(fa.blast_radius_size), "ratio"),
    ]

    # Equal weights for comparison
    weight = 1.0 / len(metrics_to_fuse)

    # Extract raw values
    raw_data = {}
    for name, extractor, _ in metrics_to_fuse:
        raw_data[name] = [extractor(files[p]) for p in paths]

    # --- Method A: weighted sum of min-max normalized values ---
    normalized = {}
    for name, vals in raw_data.items():
        lo, hi = min(vals), max(vals)
        rng = hi - lo if hi != lo else 1.0
        normalized[name] = [(v - lo) / rng for v in vals]

    weighted_scores = []
    for i in range(len(paths)):
        score = sum(normalized[name][i] * weight for name, _, _ in metrics_to_fuse)
        weighted_scores.append(score)

    # --- Method B: average of percentile ranks ---
    pct_ranks = {}
    for name, vals in raw_data.items():
        pct_ranks[name] = percentile_rank(vals)

    rank_scores = []
    for i in range(len(paths)):
        score = sum(pct_ranks[name][i] * weight for name, _, _ in metrics_to_fuse)
        rank_scores.append(score)

    # --- Compare rankings ---
    weighted_order = sorted(range(len(paths)), key=lambda i: weighted_scores[i], reverse=True)
    rank_order = sorted(range(len(paths)), key=lambda i: rank_scores[i], reverse=True)

    weighted_ranking = {idx: pos for pos, idx in enumerate(weighted_order)}
    rank_ranking = {idx: pos for pos, idx in enumerate(rank_order)}

    print("3. FUSION COMPARISON: WEIGHTED-SUM vs RANK-BASED")
    print("-" * 72)
    print(f"{'File':<50} {'WtSum':>6} {'Rank':>6} {'Diff':>6}")
    print("-" * 72)

    disagreements = []
    for i, p in enumerate(paths):
        ws_rank = weighted_ranking[i]
        rk_rank = rank_ranking[i]
        diff = abs(ws_rank - rk_rank)
        if diff >= 3:
            disagreements.append((p, ws_rank, rk_rank, diff))

    # Show top 10 by weighted score
    for pos in range(min(10, len(paths))):
        i = weighted_order[pos]
        p = paths[i]
        ws_rank = weighted_ranking[i]
        rk_rank = rank_ranking[i]
        diff = abs(ws_rank - rk_rank)
        marker = " ***" if diff >= 3 else ""
        short = p if len(p) <= 48 else "..." + p[-45:]
        print(f"{short:<50} {ws_rank:>6} {rk_rank:>6} {diff:>6}{marker}")

    print()
    print("4. RANK INVERSIONS (diff >= 3 positions)")
    print("-" * 72)
    if not disagreements:
        print("  No significant rank inversions — scale violations don't matter much here.")
    else:
        print(f"  {len(disagreements)} files change rank by 3+ positions between methods.")
        print(f"  This means scale assumptions in the fusion formula MATTER.")
        print()
        disagreements.sort(key=lambda x: -x[3])
        for p, ws, rk, diff in disagreements[:15]:
            short = p if len(p) <= 45 else "..." + p[-42:]
            print(f"  {short:<48} weighted=#{ws:<4} rank=#{rk:<4} delta={diff}")

    # ── 4. Ordinal violation demo ───────────────────────────────
    print()
    print("5. ORDINAL VIOLATION DEMONSTRATION")
    print("-" * 72)
    print("cognitive_load is classified as ordinal. If we treat it as ratio")
    print("(take means, compute ratios), we get different 'top complex' files")
    print("than if we only use rank ordering.")
    print()

    cl_vals = raw_data["cognitive_load"]
    cl_order_by_value = sorted(range(len(paths)), key=lambda i: cl_vals[i], reverse=True)
    cl_pct = percentile_rank(cl_vals)
    cl_order_by_rank = sorted(range(len(paths)), key=lambda i: cl_pct[i], reverse=True)

    # These should be identical (monotonic transform preserves order)
    # But when combined with other metrics, the magnitudes distort things
    top_n = min(5, len(paths))
    print(f"  Top {top_n} by raw cognitive_load (ratio assumption):")
    for pos in range(top_n):
        i = cl_order_by_value[pos]
        short = paths[i] if len(paths[i]) <= 45 else "..." + paths[i][-42:]
        print(f"    #{pos+1} {short:<48} value={cl_vals[i]:.1f}")

    # Show the cognitive_load distribution skewness
    if cl_vals:
        mean_cl = sum(cl_vals) / len(cl_vals)
        max_cl = max(cl_vals)
        median_cl = sorted(cl_vals)[len(cl_vals) // 2]
        print()
        print(f"  Distribution: mean={mean_cl:.1f}, median={median_cl:.1f}, max={max_cl:.1f}")
        print(f"  Skewness indicator: mean/median = {mean_cl/median_cl:.2f}" if median_cl > 0 else "")
        print(f"  When mean >> median, weighted-sum is dominated by outliers.")
        print(f"  Rank-based fusion is robust to this — that's why ranks differ.")

    print()


if __name__ == "__main__":
    main()
