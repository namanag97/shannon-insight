# Distance Spaces

Between any two files, "closeness" has multiple independent meanings. Each is defined by a different graph over the same set of nodes.

**The core insight**: Findings are disagreements between distance spaces.

---

## The Six Spaces

| # | Space | Edges | Meaning | Status | Phase |
|---|-------|-------|---------|--------|-------|
| G1 | **Dependency** | import A→B | Structural proximity | Operational | 0 |
| G2 | **Call** | fn in A calls fn in B | Behavioral proximity | Backlogged | — |
| G3 | **Type** | A uses type from B | Contract proximity | Backlogged | — |
| G4 | **Co-change** | A, B in same commit | Evolutionary proximity | Operational | 3 |
| G5 | **Author** | A, B share authors | Social proximity | Planned | 3 |
| G6 | **Semantic** | A, B share concepts | Meaning proximity | Planned | 2 |

---

## Distance Functions

### G1: Dependency Distance

```python
def d1(a: str, b: str, graph: DependencyGraph) -> float:
    """
    Shortest path length in dependency graph.
    Returns infinity if unreachable.
    """
    path = shortest_path(graph, a, b)
    return len(path) if path else float('inf')
```

---

### G2: Call Distance (Backlogged)

```python
def d2(a: str, b: str, call_graph: CallGraph) -> float:
    """
    Minimum call chain length between any function in A and any function in B.
    Returns infinity if no call path exists.
    """
    # Requires CALL edges (not implemented in phases 0-7)
    pass
```

---

### G3: Type Distance (Backlogged)

```python
def d3(a: str, b: str) -> float:
    """
    1 - (types used by A that are defined in B) / (types used by A)
    Returns 1 if no type relationship.
    """
    # Requires TYPE_FLOW edges (not implemented in phases 0-7)
    pass
```

---

### G4: Co-change Distance

```python
def d4(a: str, b: str, cochange: CoChangeMatrix) -> float:
    """
    Inverse of co-change lift.

    d = 1 / (lift + ε)

    Large distance = never co-change.
    Small distance = frequently co-change.
    """
    lift = cochange.lift(a, b)
    epsilon = 0.01  # Avoid division by zero
    return 1 / (lift + epsilon)
```

---

### G5: Author Distance

```python
def d5(a: str, b: str, authorship: dict[str, dict[str, int]]) -> float:
    """
    Jaccard distance of author sets.

    d = 1 - |authors(A) ∩ authors(B)| / |authors(A) ∪ authors(B)|

    d = 0: same authors
    d = 1: completely different authors
    """
    authors_a = set(authorship[a].keys())
    authors_b = set(authorship[b].keys())

    if not authors_a and not authors_b:
        return 0.0  # Both have no authors

    intersection = authors_a & authors_b
    union = authors_a | authors_b

    return 1 - len(intersection) / len(union)

def d5_weighted(a: str, b: str, authorship: dict[str, dict[str, int]]) -> float:
    """
    Weighted variant (preferred):

    d = 1 - Σ_author min(w_a, w_b) / Σ_author max(w_a, w_b)

    where w = commits_by_author / total_commits_on_file
    """
    wa = authorship[a]  # author → commits
    wb = authorship[b]

    total_a = sum(wa.values()) or 1
    total_b = sum(wb.values()) or 1

    all_authors = set(wa.keys()) | set(wb.keys())

    min_sum = 0
    max_sum = 0
    for author in all_authors:
        pa = wa.get(author, 0) / total_a
        pb = wb.get(author, 0) / total_b
        min_sum += min(pa, pb)
        max_sum += max(pa, pb)

    if max_sum == 0:
        return 0.0

    return 1 - min_sum / max_sum
```

---

### G6: Semantic Distance

```python
def d6(a: str, b: str, tfidf_vectors: dict[str, np.ndarray]) -> float:
    """
    1 - cosine similarity of TF-IDF vectors.

    d = 0: identical concepts
    d = 1: no shared concepts
    """
    va = tfidf_vectors[a]
    vb = tfidf_vectors[b]

    dot = np.dot(va, vb)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)

    if norm_a == 0 or norm_b == 0:
        return 1.0

    cosine = dot / (norm_a * norm_b)
    return 1 - cosine
```

---

## The Disagreement Principle

When two spaces tell contradictory stories about the same pair, there is a finding.

| Close in | Far in | Finding | Finder |
|----------|--------|---------|--------|
| G4 Co-change | G1 Dependency | Hidden coupling | HIDDEN_COUPLING |
| G1 Dependency | G4 Co-change | Dead dependency | DEAD_DEPENDENCY |
| G6 Semantic | G1 Dependency | Missed abstraction | (future) |
| G1 Dependency | G6 Semantic | Accidental coupling | ACCIDENTAL_COUPLING |
| G5 Author | G1 Dependency | Conway violation | CONWAY_VIOLATION |
| G1 Dependency | G5 Author | Coordination risk | (future) |
| G2 Call | G3 Type | Weak contract | (future) |
| G1 Dependency | G2 Call | Dead import | (future) |
| G6 Semantic | G5 Author | Knowledge misalignment | (future) |
| G4 Co-change | G6 Semantic | Coincidental coupling | (future) |

**15 pairs** of 6 spaces = systematic finding discovery.

---

## Disagreement Score

```python
def disagreement(
    a: str,
    b: str,
    space1: DistanceSpace,
    space2: DistanceSpace,
    all_files: list[str],
) -> float:
    """
    Disagreement = |rank_diff| between two spaces.

    rank(A, B, space) = percentile of d(A, B) among all file pairs
    """
    # Compute distances
    d1 = space1.distance(a, b)
    d2 = space2.distance(a, b)

    # Compute ranks (percentiles)
    all_d1 = [space1.distance(x, y) for x, y in combinations(all_files, 2)]
    all_d2 = [space2.distance(x, y) for x, y in combinations(all_files, 2)]

    rank1 = sum(1 for d in all_d1 if d <= d1) / len(all_d1)
    rank2 = sum(1 for d in all_d2 if d <= d2) / len(all_d2)

    return abs(rank1 - rank2)
```

**High disagreement** = contradictory stories = worth investigating.

---

## Aggregate Anomaly

For a single file:

```python
def anomaly(
    file: str,
    all_files: list[str],
    spaces: list[tuple[DistanceSpace, DistanceSpace]],
) -> float:
    """
    Max disagreement across all other files and all space pairs.

    Files with high aggregate anomaly are "structurally surprising."
    """
    max_disagreement = 0

    for other in all_files:
        if other == file:
            continue
        for space1, space2 in spaces:
            d = disagreement(file, other, space1, space2, all_files)
            max_disagreement = max(max_disagreement, d)

    return max_disagreement
```

---

## DistanceSpace Protocol

```python
class DistanceSpace(Protocol):
    """Interface for distance computation."""

    name: str

    def distance(self, a: str, b: str) -> float:
        """Compute distance between two files. Returns [0, ∞)."""
        ...

    def matrix(self, files: list[str]) -> np.ndarray:
        """Build full distance matrix."""
        ...

@dataclass
class G1_Dependency:
    name: str = "dependency"
    graph: DependencyGraph

    def distance(self, a: str, b: str) -> float:
        return shortest_path_length(self.graph, a, b)

@dataclass
class G4_CoChange:
    name: str = "cochange"
    cochange: CoChangeMatrix

    def distance(self, a: str, b: str) -> float:
        lift = self.cochange.lift(a, b)
        return 1 / (lift + 0.01)

@dataclass
class G5_Author:
    name: str = "author"
    authorship: dict[str, dict[str, int]]

    def distance(self, a: str, b: str) -> float:
        return author_distance_weighted(a, b, self.authorship)

@dataclass
class G6_Semantic:
    name: str = "semantic"
    vectors: dict[str, np.ndarray]

    def distance(self, a: str, b: str) -> float:
        return 1 - cosine_similarity(self.vectors[a], self.vectors[b])
```

---

## Build Order

Based on dependencies and implementation phases:

1. **G1 + G4** — exist today (dependency graph + co-change from git)
2. **G5** — trivial to add (author overlap from git data) → Phase 3
3. **G6** — requires concept vectors → Phase 2+
4. ~~**G2**~~ — **BACKLOGGED**. Requires CALL edges in IR3.
5. ~~**G3**~~ — **BACKLOGGED**. Requires TYPE_FLOW edges in IR3.

---

## Usage in Finders

```python
# HIDDEN_COUPLING: close in G4, far in G1
def hidden_coupling_predicate(store: FactStore, a: EntityId, b: EntityId) -> bool:
    # Far in G1: no import edge
    has_import = store.relations.has(a, RelationType.IMPORTS, b) or \
                 store.relations.has(b, RelationType.IMPORTS, a)

    # Close in G4: high co-change
    lift = store.relations.weight(a, RelationType.COCHANGES_WITH, b)

    return not has_import and lift > 2.0

# ACCIDENTAL_COUPLING: close in G1, far in G6
def accidental_coupling_predicate(store: FactStore, a: EntityId, b: EntityId) -> bool:
    # Close in G1: import edge exists
    has_import = store.relations.has(a, RelationType.IMPORTS, b)

    # Far in G6: low concept overlap
    concepts_a = store.get_semantics(a.key).concepts
    concepts_b = store.get_semantics(b.key).concepts
    overlap = len(set(concepts_a) & set(concepts_b)) / len(set(concepts_a) | set(concepts_b))

    return has_import and overlap < 0.2
```
