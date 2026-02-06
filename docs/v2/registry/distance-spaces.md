# Registry: Distance Spaces

Between any two files, "closeness" has six independent meanings. Each is defined by a different graph over the same set of nodes. **Findings are disagreements between distance spaces.**

## The Six Spaces

| # | Space | Edges | Distance meaning | Source IR | Status |
|---|-------|-------|-----------------|-----------|--------|
| G1 | **Dependency** | import A→B | Structural proximity | IR3 | Exists |
| G2 | **Call** | fn in A calls fn in B | Behavioral proximity | IR3 (CALL edges) | Phase 3 |
| G3 | **Type** | A uses type from B | Contract proximity | IR3 (TYPE_FLOW edges) | Phase 3+ |
| G4 | **Co-change** | A, B in same commit | Evolutionary proximity | IR5t | Exists |
| G5 | **Author** | A, B share authors | Social proximity | IR5t | Trivial to add |
| G6 | **Semantic** | A, B share concepts | Meaning proximity | IR2 | Phase 2+ |

## Distance Functions

### G1: Dependency distance

```
d₁(A, B) = shortest_path_length(A, B, dependency_graph)
           ∞ if unreachable
```

### G2: Call distance

```
d₂(A, B) = min call chain length between any function in A and any function in B
           ∞ if no call path exists
```

### G3: Type distance

```
d₃(A, B) = 1 - |types_used_by_A ∩ types_defined_in_B| / |types_used_by_A|
           1 if no type relationship
```

### G4: Co-change distance

```
d₄(A, B) = 1 / (cochange_lift(A, B) + ε)
           large if they never co-change

where lift(A, B) = P(A∩B) / (P(A) × P(B))
      ε = 0.01 (avoid division by zero)
```

### G5: Author distance

```
d₅(A, B) = 1 - |authors(A) ∩ authors(B)| / |authors(A) ∪ authors(B)|
           1 if completely different authors

Weighted variant (preferred):
d₅ʷ(A, B) = 1 - Σ_a min(wₐ(A), wₐ(B)) / Σ_a max(wₐ(A), wₐ(B))
where wₐ(f) = commits_by_a_on_f / total_commits_on_f
```

### G6: Semantic distance

```
d₆(A, B) = 1 - cosine(tfidf_vector(A), tfidf_vector(B))
           1 if no shared concepts
```

## The Disagreement Principle

When two spaces tell contradictory stories about the same pair, there is a finding:

| Close in | Far in | Finding | Finder (see `finders.md`) |
|---|---|---|---|
| G4 Co-change | G1 Dependency | **Hidden coupling** | HIDDEN_COUPLING |
| G1 Dependency | G4 Co-change | **Dead dependency** | DEAD_DEPENDENCY |
| G6 Semantic | G1 Dependency | **Missed abstraction** | (future) |
| G1 Dependency | G6 Semantic | **Accidental coupling** | ACCIDENTAL_COUPLING |
| G5 Author | G1 Dependency | **Conway violation** | CONWAY_VIOLATION |
| G1 Dependency | G5 Author | **Coordination risk** | (future) |
| G2 Call | G3 Type | **Weak contract** | (future) |
| G1 Dependency | G2 Call | **Dead import** | (future) |
| G6 Semantic | G5 Author | **Knowledge misalignment** | (future) |
| G4 Co-change | G6 Semantic | **Coincidental coupling** | (future) |

15 pairs of 6 spaces = systematic finding discovery. Unexplored pairs are potential new finding classes.

## Disagreement Score

```
For file pair (A, B):
  rank_k(A, B) = percentile of d_k(A, B) among all file pairs in space k

  disagreement(A, B, k₁, k₂) = |rank_k₁(A, B) - rank_k₂(A, B)|
```

High disagreement = contradictory stories. Worth investigating.

**Aggregate anomaly** for a single file:
```
anomaly(A) = max over all B, all space pairs (k₁, k₂): disagreement(A, B, k₁, k₂)
```

Files with high aggregate anomaly are "structurally surprising."

## Build Order

Based on dependencies and implementation phases:

1. **G1 + G4** — exist today (dependency graph + co-change from git)
2. **G5** — trivial to add (author overlap from git data already in IR5t)
3. **G6** — requires IR2 concept vectors (Phase 2)
4. **G2** — requires CALL edges in IR3 (Phase 3)
5. **G3** — requires TYPE_FLOW edges in IR3 (Phase 3+, hardest)

## Multi-Graph Analysis

### Combined Laplacian

```
L_combined = Σᵢ αᵢ Lᵢ

where Lᵢ = Laplacian of graph i
      αᵢ = weight (default: α₁=0.30, α₄=0.25, α₅=0.15, α₆=0.20, α₂=0.10)
```

Eigenvectors of L_combined define multi-relational communities.

### Graph Disagreement Matrix

```
D_ij = ‖Lᵢ/‖Lᵢ‖_F - Lⱼ/‖Lⱼ‖_F‖_F
```

6×6 matrix. High values = fruitful finding opportunities between those two spaces.
