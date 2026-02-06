# graph/models.md -- Data Models

All data structures for the dependency graph, its derived metrics, and temporal diffs.

## Current State

Today `models.py` defines: `DependencyGraph`, `CycleGroup`, `Community`, `GraphAnalysis`, `ModuleAnalysis`, `FileAnalysis`, `BoundaryMismatch`, `CodebaseAnalysis`. These are flat dataclasses with dict-based adjacency.

v2 replaces these with a richer model that supports multi-edge types, confidence tagging, and structured diffs.

---

## CodeGraph

The central data structure. A multi-edge directed graph over files.

```python
@dataclass
class CodeGraph:
    nodes:      dict[str, FileNode]          # path -> node
    edges:      list[Edge]                   # all resolved edges
    unresolved: list[UnresolvedEdge]         # phantom imports + broken calls

    # Derived adjacency (built from edges for algorithm consumption)
    adjacency:  dict[str, list[str]]         # forward: A -> [B, C]
    reverse:    dict[str, list[str]]         # backward: B -> [A]
    edge_count: int                          # |edges|
```

**Replaces**: `DependencyGraph` (which had only adjacency/reverse/all_nodes/edge_count).

**Key change**: Edges are now first-class objects with type and confidence, not implicit in adjacency lists.

---

## FileNode

A node in the graph. Back-references to IR1 and IR2 for algorithm access.

```python
@dataclass
class FileNode:
    path:    str
    ir1:     FileSyntax              # from scanning/ (imports, calls, classes)
    ir2:     Optional[FileSemantics] # from semantics/ (role, concepts); None if IR2 not run
```

**New in v2**. Today nodes are bare strings (file paths).

---

## Edge

A typed, weighted, confidence-tagged relationship between two files.

```python
@dataclass
class Edge:
    source:     str                  # source file path
    target:     str                  # target file path
    type:       EdgeType             # IMPORT | CALL | TYPE_FLOW
    symbols:    list[str]            # what crosses the boundary: ["User", "Token"]
    weight:     int                  # |symbols|
    confidence: EdgeConfidence       # HIGH | MEDIUM | LOW
```

### EdgeType

```python
class EdgeType(Enum):
    IMPORT    = "import"      # A has import statement referencing B
    CALL      = "call"        # function in A calls function in B
    TYPE_FLOW = "type_flow"   # A uses a type defined in B as param/return/annotation
```

**IMPORT** edges exist today. **CALL** and **TYPE_FLOW** are new in v2.

Multiple edge types can exist between the same pair (A, B). An IMPORT edge and a CALL edge between the same files are both kept. Algorithms that need a simple graph (PageRank, BFS) collapse multi-edges by summing weights.

### EdgeConfidence

```python
class EdgeConfidence(Enum):
    HIGH   = "high"     # Exact resolution (import path match, JARVIS for Python calls)
    MEDIUM = "medium"   # Heuristic resolution (qualified call + import tracking)
    LOW    = "low"      # Ambiguous (unqualified method call, multiple candidates)
```

IMPORT edges are always HIGH (resolution is deterministic from import path).

CALL edges vary by language and resolution strategy. See `builder.md` for per-language confidence levels.

TYPE_FLOW edges follow the same confidence model as CALL edges.

Finders that consume edges can filter by confidence. Dead import detection uses only HIGH. Disagreement analysis flags LOW results separately.

---

## UnresolvedEdge

An edge that could not be resolved to a target file.

```python
@dataclass
class UnresolvedEdge:
    source:     str                  # file path
    target_ref: str                  # the unresolvable reference (import path or call target)
    type:       UnresolvedType       # PHANTOM_IMPORT | BROKEN_CALL
    context:    str                  # line of code containing the reference (for diagnostics)

class UnresolvedType(Enum):
    PHANTOM_IMPORT = "phantom_import"   # import points to nothing in project
    BROKEN_CALL    = "broken_call"      # call target cannot be resolved
```

**Distinction from external dependencies**: Imports to known third-party packages (stdlib, pip-installed) are filtered out during edge construction and are NOT recorded as unresolved. Only imports that appear to target project-internal paths but fail resolution become `PHANTOM_IMPORT`.

**New in v2** as an explicit model. Today phantom imports are partially tracked but not first-class.

---

## GraphMetrics

All computed signals from graph algorithms. One instance per analysis run.

```python
@dataclass
class GraphMetrics:
    # ── Per-node signals (signals 14-23) ──
    pagerank:              dict[str, float]     # signal 14
    betweenness:           dict[str, float]     # signal 15
    in_degree:             dict[str, int]       # signal 16
    out_degree:            dict[str, int]       # signal 17
    blast_radius:          dict[str, set[str]]  # raw sets
    blast_radius_size:     dict[str, int]       # signal 18 = |blast_radius[path]|
    depth:                 dict[str, int]       # signal 19; -1 = unreachable
    is_orphan:             dict[str, bool]      # signal 20
    phantom_import_count:  dict[str, int]       # signal 21
    broken_call_count:     dict[str, int]       # signal 22
    community:             dict[str, int]       # signal 23

    # ── Per-node information signals (signals 24-26) ──
    compression_ratio:     dict[str, float]     # signal 24
    semantic_coherence:    dict[str, float]     # signal 25
    cognitive_load:        dict[str, float]     # signal 26

    # ── Topology ──
    sccs:                  list[set[str]]       # strongly connected components (|nodes| > 1)
    communities:           list[Community]      # Louvain communities
    connected_components:  list[set[str]]       # weakly connected components

    # ── Global signals (signals 52-59) ──
    modularity:            float                # signal 52: Louvain Q score
    fiedler_value:         float                # signal 53: lambda_2 of Laplacian
    spectral_gap:          float                # signal 54: lambda_2 / lambda_3
    cycle_count:           int                  # signal 55: |SCCs with |nodes| > 1|
    centrality_gini:       float                # signal 56: gini(pagerank values)
    orphan_ratio:          float                # signal 57: count(is_orphan) / total_files
    phantom_ratio:         float                # signal 58: unresolved_edges / total_edges
    glue_deficit:          float                # signal 59: see registry/signals.md #59

    # ── Spectral (detailed) ──
    eigenvalues:           list[float]          # first k eigenvalues of Laplacian
    max_depth:             int                  # max DAG depth across all files

    # ── Clone detection ──
    clone_pairs:           list[ClonePair]      # NCD-detected similar file pairs
```

**Replaces**: `GraphAnalysis` + `FileAnalysis` + `ModuleAnalysis` fields that are graph-derived.

**Key change**: Module-level metrics (cohesion, coupling, etc.) move to `architecture/` in v2. This module computes only file-level and global graph signals.

---

## Community

Unchanged from today.

```python
@dataclass
class Community:
    id:      int
    members: set[str]
```

---

## CycleGroup

Unchanged from today.

```python
@dataclass
class CycleGroup:
    nodes:               set[str]
    internal_edge_count: int = 0
```

---

## ClonePair

New in v2.

```python
@dataclass
class ClonePair:
    file_a:   str
    file_b:   str
    ncd:      float          # Normalized Compression Distance [0, 1]; < 0.3 = clone
    jaccard:  float          # MinHash Jaccard estimate (pre-filter score)
```

---

## GraphDelta

Structured diff between two `CodeGraph` snapshots. New in v2.

```python
@dataclass
class GraphDelta:
    edges_added:          list[Edge]
    edges_removed:        list[Edge]
    edges_retyped:        list[tuple[Edge, list[EdgeType], list[EdgeType]]]
    new_phantoms:         list[UnresolvedEdge]
    resolved_phantoms:    list[UnresolvedEdge]
    new_cycles:           list[set[str]]        # SCCs that appeared
    broken_cycles:        list[set[str]]        # SCCs that disappeared
    community_migration:  list[tuple[str, int, int]]  # (path, old_comm, new_comm)
    pagerank_delta:       dict[str, float]
    modularity_delta:     float
    fiedler_delta:        float
```

Edge matching for delta computation: edges are identified by `(source, target, type)` tuple. If an IMPORT edge from A->B exists in both snapshots, it is the "same" edge. Symbol list changes are tracked as updates, not add/remove.

---

## Migration from Current Models

| Current (v1) | v2 | Notes |
|---|---|---|
| `DependencyGraph` | `CodeGraph` | Gains typed edges, unresolved tracking, FileNode |
| `GraphAnalysis` | `GraphMetrics` | Gains depth, spectral, orphan/phantom ratios, clones |
| `FileAnalysis` | Removed (split) | Graph signals go to `GraphMetrics` per-node dicts; file measurements go to `signals/` |
| `ModuleAnalysis` | Moves to `architecture/` | cohesion, coupling, boundary_alignment are IR4 concerns |
| `BoundaryMismatch` | Moves to `architecture/` | Module boundary analysis is IR4 |
| `CodebaseAnalysis` | Removed | Replaced by `InsightResult` in `insights/` |
