# Module: graph/ (IR3 -- RelationshipGraph)

## Responsibility

Multi-edge dependency graph construction and all graph algorithms. Transforms file-level syntax (IR1) and semantic annotations (IR2) into a unified `CodeGraph` with three edge types. Computes centrality, topology, spectral properties, clone detection, and the six distance spaces.

This module is the structural backbone of Shannon Insight. Every file-level structural signal and every cross-file relationship passes through this module.

## Current State vs v2

### Exists today

- IMPORT edges from `build_dependency_graph()` in `builder.py`
- PageRank centrality (via `math/graph.py`)
- Betweenness centrality (via `math/graph.py`)
- Tarjan SCC (iterative, in `algorithms.py`)
- Blast radius BFS on reverse graph (`algorithms.py`)
- Louvain community detection with modularity Q (`algorithms.py`)
- Per-file measurements: compression_ratio, cognitive_load, function_size_gini (`engine.py`)
- Per-module measurements: cohesion, coupling, boundary_alignment (`engine.py`)
- Boundary mismatch detection (`engine.py`)
- Statistical outlier detection via MAD (`engine.py`)

### v2 additions

- **CALL edges** (NEW): function-to-function cross-file edges with confidence tagging. See `builder.md`.
- **TYPE_FLOW edges** (NEW): type usage edges linking consumer to type-defining file. See `builder.md`.
- **Edge confidence** (NEW): HIGH | MEDIUM | LOW on every edge.
- **UnresolvedEdge** (NEW): explicit tracking of phantom imports and broken calls.
- **DAG depth** (NEW): longest path from entry points via BFS.
- **Spectral analysis** (NEW): Lanczos for top-k Laplacian eigenvalues, fiedler_value, spectral_gap.
- **Centrality Gini** (NEW): Gini coefficient of pagerank distribution.
- **NCD clone detection** (NEW): MinHash pre-filtered Normalized Compression Distance. See `clone-detection.md`.
- **Six distance spaces** (NEW): G1-G6 over the same node set. See `distance-spaces.md`.
- **GraphDelta** (NEW): structured diff between two CodeGraph snapshots.
- **Semantic coherence** (NEW): mean pairwise cosine similarity of function-level TF-IDF vectors.
- **Orphan/phantom ratio** (NEW): global connectivity quality signals.

## Exports

| Export | Type | Description |
|--------|------|-------------|
| `GraphBuilder` | class | Constructs `CodeGraph` from scanning + semantics + temporal inputs |
| `CodeGraph` | dataclass | The multi-edge graph: nodes, edges, unresolved edges |
| `GraphMetrics` | dataclass | All computed signals: centrality, topology, spectral, quality |
| `Edge` | dataclass | Typed, weighted, confidence-tagged edge |
| `FileNode` | dataclass | Node with back-references to IR1 and IR2 |
| `UnresolvedEdge` | dataclass | Phantom import or broken call with context |
| `GraphDelta` | dataclass | Structured diff between two graphs |

## Requires

| Module | What | Why |
|--------|------|-----|
| `scanning/` | `FileSyntax` (imports, calls, classes) | Edge construction (IMPORT, CALL, TYPE_FLOW) |
| `semantics/` | `FileSemantics` (roles, concepts) | Orphan classification, concept vectors for G6 |
| `temporal/` | `PairDynamics` (co-change lift) | Co-change enrichment on edges (optional) |

## Feeds Into

| Module | What | Why |
|--------|------|-----|
| `architecture/` | `CodeGraph`, communities | Module contraction, layer inference |
| `signals/` | Per-file signals 14-26, global signals 52-59 | Signal fusion and composites |
| `insights/` | Graph data, distance spaces | Finding predicates (hidden coupling, dead dependency, etc.) |

## Signals Computed

### Per-file (signals 14-26)

All formulas defined in `registry/signals.md`. This module computes:

| # | Signal | Status |
|---|--------|--------|
| 14 | `pagerank` | Exists |
| 15 | `betweenness` | Exists (v2: Brandes' proper normalization) |
| 16 | `in_degree` | Exists |
| 17 | `out_degree` | Exists |
| 18 | `blast_radius_size` | Exists |
| 19 | `depth` | NEW |
| 20 | `is_orphan` | Exists (v2: uses IR2 role for entry point exclusion) |
| 21 | `phantom_import_count` | NEW (explicit tracking) |
| 22 | `broken_call_count` | NEW (requires CALL edges) |
| 23 | `community` | Exists |
| 24 | `compression_ratio` | Exists |
| 25 | `semantic_coherence` | NEW |
| 26 | `cognitive_load` | Exists |

### Global (signals 52-59)

| # | Signal | Status |
|---|--------|--------|
| 52 | `modularity` | Exists |
| 53 | `fiedler_value` | NEW |
| 54 | `spectral_gap` | NEW |
| 55 | `cycle_count` | Exists |
| 56 | `centrality_gini` | NEW |
| 57 | `orphan_ratio` | NEW (explicit) |
| 58 | `phantom_ratio` | NEW (explicit) |
| 59 | `glue_deficit` | NEW |

### Also produces (not numbered signals)

- NCD clone pairs with similarity scores
- Six distance space matrices (G1-G6)
- Graph edit distance (GED) between snapshots

## Temporal Contract

### Output at time t

`CodeGraph(t)` and `GraphMetrics(t)`. The graph is a pure function of the scanned files at time t plus optional temporal enrichment.

### Delta(t1, t2)

```
GraphDelta:
  edges_added:         [Edge]
  edges_removed:       [Edge]
  edges_retyped:       [(Edge, old_types, new_types)]
  new_phantoms:        [UnresolvedEdge]
  resolved_phantoms:   [UnresolvedEdge]
  new_cycles:          [set[str]]       # SCCs that appeared
  broken_cycles:       [set[str]]       # SCCs that disappeared
  community_migration: [(path, old_community, new_community)]
  pagerank_delta:      {path: float}
  modularity_delta:    float
  fiedler_delta:       float
```

### Time series

| Metric | What it reveals |
|--------|-----------------|
| `modularity(t)` | Architecture quality trend |
| `fiedler_value(t)` | Connectivity robustness trend |
| `cycle_count(t)` | Circular dependency accumulation |
| `orphan_ratio(t)` | Disconnection trend |
| `centrality_gini(t)` | Importance concentration/distribution |
| `phantom_ratio(t)` | Broken reference accumulation |
| `edge_count(t)` | Coupling growth |
| `density(t)` | Is graph getting denser? |

### Graph Edit Distance

```
GED(G1, G2) = (|edges_added| + |edges_removed|) / ((|E1| + |E2|) / 2)
```

GED near 0 = graph barely changed. GED > 0.1 in one commit = major structural change.

### Reconstruction

Rebuild graph from historical `FileSyntax` + `ImportDecl` via `git show <sha>:<path>` and re-parse. Requires Kind 3 temporal data.

## Error Handling

- **Disconnected graph**: Compute all algorithms per weakly-connected component. Report `connected_component_count` as a global signal. Centrality normalization is per-component.
- **Empty graph** (0 edges): Return zero-valued metrics. Skip spectral analysis (Laplacian undefined). All files are orphans.
- **Self-loops**: Filtered during edge construction. A file cannot import itself.
- **Duplicate edges**: Multiple import statements from A to B collapse to a single IMPORT edge with `weight = |symbols|`. CALL and TYPE_FLOW edges are separate.

## File Layout

```
graph/
  __init__.py           # re-exports GraphBuilder, CodeGraph, GraphMetrics, Edge, FileNode
  models.py             # CodeGraph, FileNode, Edge, UnresolvedEdge, GraphMetrics, GraphDelta
  builder.py            # GraphBuilder: edge construction (IMPORT, CALL, TYPE_FLOW)
  algorithms.py         # PageRank, betweenness, Tarjan, blast radius, Louvain, DAG depth, spectral
  engine.py             # AnalysisEngine: orchestrates builder + algorithms + measurements
  distance_spaces.py    # Six distance space implementations + disagreement computation
  clone_detection.py    # NCD clone detection with MinHash pre-filtering
```
