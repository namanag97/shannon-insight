# Level 4: Cross-Layer & Trajectory Signals

## Overview

Level 4 computes signals spanning ACROSS graphs or ACROSS time.

## Cross-Layer Signals

### Per-Node
| Signal | Formula | Meaning |
|--------|---------|---------|
| `hidden_coupling_count` | \|N_cochange(v) \ N_import(v)\| | Undeclared deps |
| `dead_import_count` | \|N_import(v) \ N_cochange(v)\| | Unused deps |
| `conway_violation_count` | \|N_import(v) \ N_author(v)\| | Cross-team deps |
| `neighborhood_coherence` | \|N_import ∩ N_cochange\| / \|N_import ∪ N_cochange\| | Alignment |

### Global (Mutual Information)
| Signal | Formula | Meaning |
|--------|---------|---------|
| `behavioral_coherence` | I(G_import; G_cochange) | Structure predicts behavior |
| `conway_alignment` | I(G_import; G_author) | Structure matches teams |
| `semantic_alignment` | I(G_import; G_semantic) | Imports match concepts |

## Graph Mutual Information

```
I(G₁; G₂) = H_b(p₁) + H_b(p₂) - H_s(P₁₂)

P₁₂ = contingency table:
  n₁₁ = edges in both
  n₁₀ = only in G₁
  n₀₁ = only in G₂
  n₀₀ = in neither

NMI = 2×I / (H(G₁) + H(G₂))
```

## Trajectory Signals

### Per-Node
| Signal | Formula | Meaning |
|--------|---------|---------|
| `pagerank_velocity` | d(pagerank)/dt | Centrality change |
| `community_changes` | count(c(t) ≠ c(t-1)) | Cluster instability |
| `community_stability` | 1 - changes/observations | Cluster stability |

### Global
| Signal | Formula | Meaning |
|--------|---------|---------|
| `graph_velocity` | mean(\|ΔG(t)\|) | Topology change rate |
| `fiedler_trend` | trend(fiedler) | Connectivity trend |
| `modularity_trend` | trend(modularity) | Community evolution |
| `topology_stability` | 1/(1+graph_velocity) | Overall stability |

## Current Implementation

**Files:**
- `src/shannon_insight/temporal/cochange.py` - Co-change with lift
- `src/shannon_insight/insights/finders/patterns/cross_dimensional.py`

**Status:** Partial. Missing: formal MI computation, trajectory snapshots.
