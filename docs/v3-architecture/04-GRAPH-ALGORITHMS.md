# Level 3: Graph Algorithms

## Overview

Level 3 runs standard graph algorithms on each adjacency matrix from Level 2.

## Per-Node Signals

| Signal | Formula | Complexity |
|--------|---------|------------|
| `pagerank` | Stationary distribution, d=0.85 | O(E×iter) |
| `betweenness` | σ_st(v)/σ_st (Brandes) | O(VE) |
| `depth` | BFS from entry points | O(V+E) |
| `blast_radius` | \|transitive_closure\| | O(V×E) |
| `community` | Louvain cluster | O(E log V) |
| `is_orphan` | in_degree == 0 | O(1) |
| `cycle_member` | Tarjan SCC | O(V+E) |

## Global Signals

| Signal | Formula |
|--------|---------|
| `fiedler` | λ₂ of Laplacian |
| `spectral_gap` | λ₃ - λ₂ |
| `modularity` | Q from Louvain |
| `centrality_gini` | Gini(pagerank values) |
| `scc_count` | \|SCCs with size > 1\| |

## Key Formulas

### PageRank
```
PR(v) = (1-d)/N + d × Σᵤ PR(u)/out_degree(u)
d = 0.85, iterate until Δ < 1e-6
```

### Louvain Modularity
```
Q = (1/2m) Σᵢⱼ [Aᵢⱼ - kᵢkⱼ/2m] × δ(cᵢ, cⱼ)
```

### Gini Coefficient
```
G = (2×Σᵢ i×xᵢ)/(n×Σxᵢ) - (n+1)/n
x sorted ascending, i is 1-indexed
```

## Current Implementation

**Files:**
- `src/shannon_insight/graph/algorithms.py` - All algorithms (836 lines)
- `src/shannon_insight/graph/models.py` - GraphAnalysis model

**Status:** ~90% complete. Missing: spectral analysis (Fiedler), clustering coefficient.
