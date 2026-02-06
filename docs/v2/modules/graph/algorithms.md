# graph/algorithms.md -- Graph Algorithms

All graph algorithms executed on the `CodeGraph`. Each algorithm's formula is defined in `registry/signals.md`; this document specifies implementation details, convergence criteria, and performance characteristics.

## Current State

Today `algorithms.py` contains `run_graph_algorithms()` which calls:
- `GraphMetrics.pagerank()` (delegated to `math/graph.py`)
- `GraphMetrics.betweenness_centrality()` (delegated to `math/graph.py`)
- `tarjan_scc()` (iterative, in `algorithms.py`)
- `compute_blast_radius()` (BFS on reverse graph, in `algorithms.py`)
- `louvain()` (custom implementation, in `algorithms.py`)

v2 adds: Brandes' betweenness with normalization, DAG depth, spectral decomposition, centrality Gini.

---

## Algorithm Catalog

### 1. PageRank (exists)

**Signal**: #14 `pagerank` (see `registry/signals.md`)

**Implementation**: Power iteration.

```
PR(v) = (1-d)/N + d * sum(PR(u)/out_degree(u)) for all u -> v
```

**Parameters**:
- Damping factor `d = 0.85`
- Convergence: `max(|PR_new - PR_old|) < 1e-6` or 50 iterations
- Initialization: `PR(v) = 1/N` for all v

**Disconnected graph handling**: For each weakly connected component, run PageRank independently. Normalize within component, then scale by component size relative to total.

**Performance**: O(|E| * iterations). Typically converges in 15-25 iterations. For 10K files with 50K edges: ~50ms.

**Status**: Exists in `math/graph.py`. v2 change: move to `graph/algorithms.py` for locality; no algorithm change.

---

### 2. Betweenness Centrality (exists, v2: improved)

**Signal**: #15 `betweenness` (see `registry/signals.md`)

**Implementation**: Brandes' algorithm.

```
B(v) = sum over s != v != t of sigma(s,t|v) / sigma(s,t)

where sigma(s,t)   = number of shortest paths from s to t
      sigma(s,t|v) = number of those paths passing through v
```

**v2 improvements**:
- Proper normalization: divide by `(n-1)(n-2)` for directed graphs so B in [0, 1]
- Per-component computation for disconnected graphs

**Performance**: O(|V| * |E|). For 10K files: ~5 seconds. This is the most expensive per-node algorithm.

**Optimization for large graphs** (>5K nodes): Sample-based approximation. Run Brandes from k random source nodes (k = min(500, |V|)). Scale result by |V|/k. Error bounded by O(1/sqrt(k)).

**Status**: Exists in `math/graph.py`. v2: add normalization, per-component handling, sampling for large graphs.

---

### 3. Tarjan SCC (exists)

**Signal**: #55 `cycle_count` (global) = |SCCs with |nodes| > 1|

**Implementation**: Iterative Tarjan's algorithm (avoids Python recursion limit).

```
Uses explicit call stack with (node, neighbor_iterator) frames.
For each SCC root (lowlink[v] == index[v]), pops component from stack.
```

**Performance**: O(|V| + |E|). Linear. No optimization needed.

**Status**: Exists in `algorithms.py`. No changes for v2.

---

### 4. Blast Radius BFS (exists)

**Signal**: #18 `blast_radius_size` = |BFS(v, reverse(G))| - 1

**Implementation**: BFS on reverse adjacency from each node.

```
for each node v:
    blast_radius[v] = BFS_reachable(v, reverse_graph)
    blast_radius_size[v] = |blast_radius[v]|
```

**Performance**: O(|V| * (|V| + |E|)) worst case. In practice much faster because most files have small reverse closures.

**Optimization for large graphs**: Memoize overlapping BFS. If node A's blast radius is already computed and B is reachable from A, then `blast_radius[B] is a superset of blast_radius[A]` -- but this is the wrong direction. Instead, use transitive closure batching: compute reachability in topological order when possible.

**Status**: Exists in `algorithms.py`. No algorithm change for v2.

---

### 5. Louvain Community Detection (exists)

**Signal**: #23 `community` (per-file), #52 `modularity` (global)

**Implementation**: Custom Louvain with two-part gain formula (removal cost + insertion gain).

```
Modularity: Q = (1/2m) * sum[(A_ij - k_i*k_j/(2m)) * delta(c_i, c_j)]

For each node:
  remove_cost = ki_in_current / 2m - sigma_current * ki / (2m)^2
  add_gain = ki_in_target / 2m - sigma_target * ki / (2m)^2
  net_gain = add_gain - remove_cost
  Move node if net_gain > 0
```

**Parameters**:
- Max passes: 20 (safety limit)
- Edge weights: undirected (directed edges symmetrized)
- Convergence: no node moved in a full pass

**Performance**: O(|E| * passes). Typically 3-8 passes. For 10K files: ~100ms.

**Status**: Exists in `algorithms.py`. No algorithm change for v2.

---

### 6. DAG Depth (NEW)

**Signal**: #19 `depth` (see `registry/signals.md`)

**Implementation**: BFS from entry points on the forward graph.

```
Identify entry points: files where role == ENTRY_POINT or role == TEST
  (from IR2 semantics) or in_degree == 0

Initialize:
  depth[v] = 0 for entry points
  depth[v] = -1 for all others (unreachable until proven otherwise)

BFS from all entry points simultaneously:
  queue = all entry points
  while queue:
    u = queue.popleft()
    for v in adjacency[u]:
      candidate_depth = depth[u] + 1
      if candidate_depth > depth[v]:
        depth[v] = candidate_depth
        queue.append(v)
```

This computes the **longest** path from nearest entry point, not shortest. For cycle members, depth is set to the depth at which the cycle is first reached.

Files with `depth == -1` after BFS completes are true orphans (unreachable from any entry point).

**Performance**: O(|V| + |E|). Linear. Single pass.

---

### 7. Spectral Analysis (NEW)

**Signals**: #53 `fiedler_value`, #54 `spectral_gap` (see `registry/signals.md`)

**Implementation**: Lanczos algorithm for top-k smallest eigenvalues of the graph Laplacian.

```
Graph Laplacian: L = D - A
  where D = diagonal degree matrix
        A = adjacency matrix (undirected, symmetrized from directed edges)

Compute k smallest eigenvalues lambda_1, lambda_2, ..., lambda_k via Lanczos
  (scipy.sparse.linalg.eigsh with which='SM')

fiedler_value = lambda_2       # algebraic connectivity
spectral_gap  = lambda_2 / lambda_3   (0 if lambda_3 == 0)
```

**Parameters**:
- k = min(10, |V| - 1): compute 10 smallest eigenvalues
- Use sparse matrix representation (scipy.sparse.csr_matrix)

**Interpretation**:
- lambda_1 = 0 always (connected graph) or multiplicity = number of components
- fiedler_value (lambda_2) = 0: disconnected graph; small: bottleneck; large: well-connected
- spectral_gap: large = clear best cut; small = ambiguous community structure

**Disconnected graph handling**: If graph has k connected components, the first k eigenvalues are 0. Report `fiedler_value = 0` and note `connected_component_count = k`. Compute spectral properties per-component if useful.

**Performance**: Lanczos is O(|E| * k * iterations). For 10K files with sparse graph: ~200ms. Falls back gracefully for very small graphs (< 3 nodes: skip spectral).

**Dependency**: `scipy.sparse.linalg.eigsh`. scipy is already an optional dependency.

---

### 8. Centrality Gini (NEW)

**Signal**: #56 `centrality_gini` (see `registry/signals.md`)

**Implementation**: Gini coefficient of PageRank values.

```
values = sorted(pagerank.values())
centrality_gini = gini_coefficient(values)
```

Uses existing `math/gini.py` implementation.

**Interpretation**:
- Gini > 0.7: hub-dominated graph, a few files concentrate importance (fragile)
- Gini < 0.3: importance well-distributed (resilient)

**Performance**: O(|V| log |V|) for sorting. Trivial.

**Status**: New, but uses existing Gini implementation from `math/gini.py`.

---

## Orchestration

`run_graph_algorithms()` executes algorithms in dependency order:

```
1. Degree computation           O(|V| + |E|)     # needed by others
2. Tarjan SCC                   O(|V| + |E|)     # needed by depth
3. PageRank                     O(|E| * 25)      # independent
4. Betweenness                  O(|V| * |E|)     # independent, most expensive
5. Blast radius BFS             O(|V| * |E|)     # independent
6. Louvain                      O(|E| * 8)       # independent
7. DAG depth                    O(|V| + |E|)     # needs entry point identification
8. Spectral (Lanczos)           O(|E| * k * 50)  # needs Laplacian
9. Centrality Gini              O(|V| log |V|)   # needs PageRank
```

Steps 3, 4, 5, 6 are independent and can be parallelized. Total serial time for 10K files, 50K edges: ~6 seconds, dominated by betweenness.

---

## Global Signal Computation

After per-node algorithms, compute global signals:

```
modularity       = from Louvain (signal 52)
fiedler_value    = from spectral (signal 53)
spectral_gap     = from spectral (signal 54)
cycle_count      = |SCCs with |nodes| > 1| (signal 55)
centrality_gini  = gini(pagerank values) (signal 56)
orphan_ratio     = count(is_orphan) / |V| (signal 57)
phantom_ratio    = |unresolved_edges| / (|edges| + |unresolved_edges|) (signal 58)
glue_deficit     = 1 - |{v: in_degree(v)>0 AND out_degree(v)>0}| / |V| (signal 59)
```

---

## Per-file Information Signals

Signals 24-26 are computed by graph/engine, not by graph algorithms proper, but live in `GraphMetrics` because they require file content access:

- **compression_ratio** (#24): `len(zlib.compress(content)) / len(content)`. Exists today.
- **semantic_coherence** (#25): `mean(cosine(v_i, v_j))` for function-level TF-IDF vectors. NEW. Requires function body text from IR1.
- **cognitive_load** (#26): `(concepts * complexity * nesting_factor) * (1 + G)`. Exists today.

See `registry/signals.md` for exact formulas.
