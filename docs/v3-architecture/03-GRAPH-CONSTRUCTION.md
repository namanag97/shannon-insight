# Level 2: Graph Construction

## Overview

Level 2 builds multiple relationship graphs:
1. **G_import** - static import dependencies
2. **G_cochange** - behavioral coupling
3. **G_author** - team structure
4. **G_semantic** - conceptual similarity
5. **G_clone** - structural clones

## Individual Graphs

| Graph | Edge Condition | Weight | Directed | Source |
|-------|----------------|--------|----------|--------|
| G_import | a imports b | 1.0 | Yes | Syntax |
| G_cochange | lift(a,b) > 1 | lift | No | Temporal |
| G_author | jaccard > 0 | jaccard | No | Temporal |
| G_semantic | cosine > θ | cosine | No | Content |
| G_clone | NCD < 0.3 | 1-NCD | No | Content |

## Derived Graphs (Set Operations)

```
HIDDEN_COUPLING = G_cochange \ G_import
    "Files that change together but don't import each other"

DEAD_IMPORT = G_import \ G_cochange
    "Imports that never co-change (possibly unused)"

CONWAY_VIOLATION = G_import \ G_author
    "Cross-team dependencies"
```

## Combined Graph

```
A_combined = α₁A_import + α₂A_cochange + α₃A_author + α₄A_semantic + α₅A_clone

where Σαᵢ = 1
```

## Key Algorithms

### NCD Clone Detection
```
NCD(a,b) = (C(a+b) - min(C(a),C(b))) / max(C(a),C(b))

where C(x) = zlib.compress(x) length
Threshold: 0.3 (tuned empirically)
```

### TF-IDF Semantic Similarity
```
cosine(a,b) = (v_a · v_b) / (‖v_a‖ × ‖v_b‖)

where v_f = TF-IDF vector of file concepts
```

## Data Models

```python
@dataclass
class AdjacencyMatrix:
    nodes: set[str]
    edges: dict[str, list[str]]
    weights: dict[tuple[str, str], float]
    is_directed: bool
    is_weighted: bool

@dataclass
class CombinedGraphs:
    import_graph: AdjacencyMatrix
    cochange_graph: AdjacencyMatrix
    author_graph: AdjacencyMatrix
    semantic_graph: AdjacencyMatrix
    clone_graph: AdjacencyMatrix
    hidden_coupling: AdjacencyMatrix
    dead_imports: AdjacencyMatrix
    combined_graph: AdjacencyMatrix
```

## Current Implementation

**Files:**
- `src/shannon_insight/graph/builder.py` - DependencyGraph builder
- `src/shannon_insight/graph/clone_detection.py` - NCD clones
- `src/shannon_insight/graph/distance.py` - Author distances

**Status:** 3 of 5 graphs implemented. Missing: G_cochange, G_semantic as explicit graphs.

## Dependencies

- **Requires:** Level 0 (syntax), Level 1 (temporal)
- **Produces:** Graphs for Level 3 (algorithms)
