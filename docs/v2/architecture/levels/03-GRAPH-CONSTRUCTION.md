# Level 2: Graph Construction

## Overview

Level 2 transforms facts into **5 relationship graphs** (adjacency matrices) that capture structural and temporal dependencies.

**Depends on:** Level 0 (facts), Level 1 (semantics)
**Produces:** 5 typed adjacency matrices + derived graphs

---

## Five Graph Types

### 1. G_import (Static Dependencies)

**Definition:** Directed graph where (a,b) ∈ E means file a imports file b.

```python
DependencyGraph:
    adjacency: dict[str, list[str]]  # a → [b, c, d]
    reverse: dict[str, list[str]]    # b ← [a]
    unresolved_imports: set[str]
```

- **Directed**, unweighted (edge exists or doesn't)
- From `FileSyntax.imports`

### 2. G_cochange (Temporal Coupling)

**Definition:** Undirected graph where (a,b) ∈ E means files change together more than random.

**Weight formula:**
```
lift(a,b) = P(a,b) / (P(a) × P(b))
          = (cochange_count × total_commits) / (total_a × total_b)

With temporal decay: weight = Σ exp(-λ × days_since)
λ = ln(2) / 90  (90-day half-life)
```

**Interpretation:**
- lift = 1: independent
- lift > 2: significant coupling
- lift > 5: strong coupling

### 3. G_author (Authorship Distribution)

**Definition:** Undirected graph where (a,b) ∈ E means files share authors.

**Weight formula:**
```
distance(a,b) = 1 - Σ min(w_a, w_b) / Σ max(w_a, w_b)

Where w_author(file) = commits_by_author / total_commits

weight(a,b) = 1 - distance
```

- **Undirected**, weighted by 1 - author_distance
- Captures Conway's Law implications

### 4. G_semantic (Concept Similarity)

**Definition:** Undirected graph where (a,b) ∈ E means files have similar concepts.

**Weight formula:**
```
cosine(a,b) = (concepts_a · concepts_b) / (‖concepts_a‖ × ‖concepts_b‖)
```

- From TF-IDF concept vectors (Level 1)
- Store only top-k neighbors per file (k=10)

### 5. G_clone (Copy-Paste Clones)

**Definition:** Undirected graph where (a,b) ∈ E means files are clones.

**Weight formula:**
```
NCD(a,b) = (C(a+b) - min(C(a),C(b))) / max(C(a),C(b))

Where C(x) = len(zlib.compress(x))

Clone threshold: NCD < 0.3
weight(a,b) = 1 - NCD
```

**Algorithm:**
- Direct pairwise if |files| < 1000
- MinHash + LSH pre-filtering for larger codebases

---

## Edge Weight Summary

| Graph | Weight | Range | Interpretation |
|-------|--------|-------|----------------|
| G_import | 1.0 | {0,1} | exists or not |
| G_cochange | lift | [0,∞) | 1=independent, >2=coupled |
| G_author | 1-distance | [0,1] | 0=different, 1=same authors |
| G_semantic | cosine | [0,1] | 0=unrelated, 1=identical |
| G_clone | 1-NCD | [0,1] | 0=different, 1=clone |

---

## Graph Combination Operations

### Union
```
A_union[i,j] = max(A₁[i,j], A₂[i,j])
```
Edge in either graph.

### Intersection
```
A_inter[i,j] = min(A₁[i,j], A₂[i,j])
```
Edge in both graphs.

### Weighted Sum
```
A_comb = Σ αᵣ × Aᵣ   where Σαᵣ = 1
```
Multi-layer combined strength.

### Difference
```
A_diff[i,j] = A₁[i,j] × (1 - A₂[i,j])
```
Edges in G₁ but not G₂.

---

## Derived Graphs

### HIDDEN_COUPLING
```
G_cochange \ G_import

Files that change together but don't import each other.
Implicit dependency not in code structure.
```

### DEAD_IMPORT
```
G_import \ G_cochange

Import exists but files never change together.
Static dependency not validated by temporal patterns.
```

### CONWAY_VIOLATION
```
G_import \ G_author  (where author_distance > 0.7)

Import relationship maintained by different teams.
Cross-organizational coupling.
```

### ACCIDENTAL_COUPLING
```
G_import with low semantic similarity (cosine < 0.3)

Import between conceptually unrelated files.
```

---

## Supra-Adjacency Matrix

For multi-layer analysis:

```
M_supra = [
    G_import    ωI         ωI         ωI         ωI
    ωI          G_cochange ωI         ωI         ωI
    ωI          ωI         G_author   ωI         ωI
    ωI          ωI         ωI         G_semantic ωI
    ωI          ωI         ωI         ωI         G_clone
]

Where:
  I = n×n identity (same node across layers)
  ω = inter-layer coupling (0.1-0.5)
```

Used for multi-layer modularity, spectral analysis.

---

## Data Models

```python
@dataclass
class AdjacencyMatrix:
    relation_type: str       # "import" | "cochange" | etc.
    nodes: list[str]         # ordered node IDs
    matrix: sparse.csr_matrix
    directed: bool
    weighted: bool
    edge_count: int
    density: float

@dataclass
class MultiLayerGraph:
    import_graph: AdjacencyMatrix
    cochange_graph: AdjacencyMatrix
    author_graph: AdjacencyMatrix
    semantic_graph: AdjacencyMatrix
    clone_graph: AdjacencyMatrix

    # Derived (computed on demand)
    hidden_coupling: AdjacencyMatrix | None
    dead_imports: AdjacencyMatrix | None
    conway_violations: AdjacencyMatrix | None
```

---

## Construction Pipeline

```
Step 1: G_import from FileSyntax.imports
Step 2: G_cochange from GitHistory (lift formula)
Step 3: G_author from GitHistory (weighted Jaccard)
Step 4: G_semantic from concept vectors (cosine)
Step 5: G_clone from content (NCD < 0.3)

Output: MultiLayerGraph
```

---

## Integration Points

**Consumed by:**
- Level 3: Graph algorithms (PageRank, Louvain, SCC)
- Level 4: Architecture analysis (modules, layers)
- Level 5: Signal fusion
- Level 6: Finders (HIDDEN_COUPLING, etc.)
