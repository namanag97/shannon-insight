# Level 3: Graph Algorithms

## Overview

Executes 12 graph theory algorithms on dependency graphs to compute structural signals.

**Depends on:** Level 2 (AdjacencyMatrix for each graph type)
**Produces:** Per-node signals (10) + Global signals (9)

---

## Per-Node Signals (10)

| Signal | Type | Range | Purpose |
|--------|------|-------|---------|
| `pagerank` | float | [0, 1] | Network importance |
| `betweenness` | float | [0, 1] | Bottleneck detection |
| `in_degree` | int | [0, N) | Fan-in |
| `out_degree` | int | [0, N) | Fan-out |
| `depth` | int | [-1, max] | BFS distance from entry |
| `blast_radius_size` | int | [0, N) | Transitive impact |
| `community_id` | int | [0, k) | Louvain membership |
| `is_orphan` | bool | T/F | Never imported + not special |
| `cycle_member` | bool | T/F | In circular dependency |
| `clustering_coeff` | float | [0, 1] | Local density |

## Global Signals (9)

| Signal | Type | Range | Purpose |
|--------|------|-------|---------|
| `node_count` | int | [1, ∞) | Graph size |
| `edge_count` | int | [0, ∞) | Dependencies |
| `density` | float | [0, 1] | edge_count / n(n-1) |
| `centrality_gini` | float | [0, 1] | PageRank inequality |
| `fiedler` | float | [0, ∞) | Laplacian λ₂ |
| `spectral_gap` | float | [0, ∞) | λ₃ - λ₂ |
| `scc_count` | int | [1, N] | SCC count |
| `largest_scc_size` | int | [1, N] | Max cycle size |
| `modularity_score` | float | [0, 1] | Louvain quality |

---

## Algorithm Specifications

### 1. PageRank (Power Iteration)

```
PR(v) = (1-d)/N + d × Σᵤ PR(u)/out_degree(u) + d/N × dangling_mass

d = 0.85 (damping)
Dangling nodes: out_degree = 0 → redistribute mass
Iterations: ~20 until convergence (Δ < 1e-6)
Time: O(I × E)
```

### 2. Betweenness Centrality (Brandes)

```
CB(v) = Σ_{s≠t≠v} σ_st(v) / σ_st

σ_st = # shortest paths from s to t
σ_st(v) = # shortest paths through v
Time: O(N × E)
Output: [0, 1] normalized
```

### 3. DAG Depth (Multi-Source BFS)

**Entry point fallback chain:**
1. role = ENTRY_POINT (from Phase 2)
2. `__init__.py` files with imports
3. Root importers: in_degree=0 AND out_degree>0
4. All files: depth=0 (if no entry points)

```
BFS from all entry points:
  depth[entry] = 0
  depth[neighbor] = depth[parent] + 1
  depth[unreachable] = -1

Time: O(N + E)
```

### 4. Blast Radius (Transitive Closure)

```
blast_radius(v) = {all files affected by changing v}
                = BFS on reverse graph from v

Time: O(N × (N + E)) worst case
Output: Dict[str, Set[str]]
```

### 5. Orphan Detection

```
is_orphan[file] = (in_degree == 0)
              AND role NOT IN {ENTRY_POINT, TEST, CONFIG, INTERFACE, EXCEPTION}

Time: O(N)
```

### 6. SCC Detection (Tarjan's Algorithm)

```
Iterative Tarjan (avoids recursion limits):
  - index[], lowlink[], stack, on_stack
  - Explicit call stack for DFS
  - lowlink[v] == index[v] → v is SCC root

Time: O(N + E)
Output: List[Set[str]] where len > 1 (real cycles)
```

### 7. Louvain Community Detection

```
Maximize modularity: Q = Σ_c [L_c/m - (Σ_c/2m)²]

Phase 1: Local Moving
  - Each node starts in own community
  - Greedily move to best neighbor community
  - Repeat until no improvement

Phase 2: Coarsening
  - Collapse communities into super-nodes
  - Repeat Phase 1

IMPORTANT: Sort nodes before iteration (determinism)
Time: O(I × (N + E)) where I ≈ 3-5 levels
```

### 8. Gini Coefficient

```
G = (2 × Σᵢ i × xᵢ) / (n × Σxᵢ) - (n+1)/n

Where xᵢ sorted ascending, i is 1-indexed.

Applied to PageRank:
  G < 0.30: healthy distribution
  G 0.30-0.50: moderate concentration
  G > 0.70: severe hub dominance

Time: O(N log N)
```

### 9. Spectral Properties

```
Laplacian: L = D - A
  D = diagonal degree matrix
  A = adjacency matrix

fiedler (λ₂) = second smallest eigenvalue
  λ₂ > 0: connected
  λ₂ ≈ 0: nearly disconnected

spectral_gap = λ₃ - λ₂

Time: O(N³) dense, O(N) iterative sparse
```

---

## Data Models

```python
@dataclass
class DependencyGraph:  # Input
    adjacency: dict[str, list[str]]
    reverse: dict[str, list[str]]
    all_nodes: set[str]
    edge_count: int
    unresolved_imports: dict[str, list[str]]

@dataclass
class GraphAnalysis:  # Output
    # Per-node
    pagerank: dict[str, float]
    betweenness: dict[str, float]
    in_degree: dict[str, int]
    out_degree: dict[str, int]
    depth: dict[str, int]
    blast_radius: dict[str, set[str]]
    is_orphan: dict[str, bool]

    # Structures
    cycles: list[CycleGroup]
    communities: list[Community]
    node_community: dict[str, int]

    # Global
    centrality_gini: float
    modularity_score: float
    fiedler_value: float
    spectral_gap: float

@dataclass
class CycleGroup:
    nodes: set[str]
    internal_edge_count: int

@dataclass
class Community:
    id: int
    members: set[str]
```

---

## Algorithm × Graph Matrix

| Algorithm | G_import | G_cochange | G_author | G_semantic | G_clone |
|-----------|----------|------------|----------|------------|---------|
| Degree | ✓ | ✓ | ✓ | ✓ | ✓ |
| PageRank | ✓ | ✓ | ✓ | ✓ | ✓ |
| Betweenness | ✓ | — | — | — | — |
| Depth (BFS) | ✓ | — | — | — | — |
| Blast Radius | ✓ | — | — | — | — |
| SCC (Tarjan) | ✓ | — | — | — | — |
| Louvain | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gini | ✓ | — | — | — | — |
| Spectral | ✓ | ✓ | — | — | — |

---

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Empty graph | All = 0/empty |
| Single node | pagerank=1.0, orphan=false |
| Disconnected | depth=-1 for unreachable |
| Tree (acyclic) | cycles=[], scc_count=N |
| Dangling nodes | Redistribute PageRank mass |

---

## Performance Targets (10K files)

| Algorithm | Time |
|-----------|------|
| Degree | < 100ms |
| PageRank | < 500ms |
| Betweenness | < 2s |
| Blast Radius | < 1s |
| Tarjan SCC | < 200ms |
| Louvain | < 1s |
| Spectral | < 5s |
