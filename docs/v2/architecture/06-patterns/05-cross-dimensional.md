# Cross-Dimensional Patterns

3 patterns that combine signals from multiple dimensions.

---

## 20. WEAK_LINK

File worse than its neighborhood (health Laplacian).

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.75 |
| **Phase** | 5 |
| **Hotspot** | Yes |
| **Requires** | raw_risk, IMPORTS, total_changes |

### Condition

```python
Δh(f) > 0.4 AND
total_changes > median(total_changes)  # hotspot filter
```

Where Δh is the health Laplacian:
```
Δh(f) = raw_risk(f) - mean(raw_risk(n) for n in neighbors(f))
```

### Health Laplacian

```python
def compute_delta_h(f: EntityId, store: FactStore) -> float:
    """
    Health Laplacian: file's risk relative to its neighborhood.

    Δh > 0: file is worse than neighbors
    Δh < 0: file is better than neighbors
    Δh = 0: file matches neighbors (or is orphan)
    """
    raw_risk_f = store.signals.get(f, Signal.RAW_RISK)

    # Get neighbors (files this file imports OR files that import this file)
    neighbors = set()
    for rel in store.relations.outgoing(f, RelationType.IMPORTS):
        neighbors.add(rel.target)
    for rel in store.relations.incoming(f, RelationType.IMPORTS):
        neighbors.add(rel.source)

    if not neighbors:
        # Orphan: no neighborhood comparison
        return 0.0

    neighbor_risks = [store.signals.get(n, Signal.RAW_RISK, 0) for n in neighbors]
    mean_neighbor_risk = sum(neighbor_risks) / len(neighbor_risks)

    return raw_risk_f - mean_neighbor_risk
```

### raw_risk Formula

Uses absolute values (not percentiles) to preserve variation:

```
raw_risk(f) = 0.25 × pagerank(f) / max_pagerank
            + 0.20 × blast_radius_size(f) / max_blast
            + 0.20 × cognitive_load(f) / max_cognitive
            + 0.20 × instability_factor(f)
            + 0.15 × (1 - bus_factor(f) / max_bus_factor)

where instability_factor = 1.0 if trajectory ∈ {CHURNING, SPIKING}
                           0.3 otherwise
```

### Evidence

- **IR5s**: Δh value, neighbor raw_risk values
- risk_score for display

### Remediation

"This file drags down its healthy neighborhood. Prioritize improvement."

### Effort

MEDIUM

### Edge Case

**Orphan files** have Δh = 0.0 (no neighbors). They are caught by ORPHAN_CODE instead.

---

## 21. BUG_ATTRACTOR

Central file with high fix ratio.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.70 |
| **Phase** | 3 |
| **Hotspot** | Yes |
| **Requires** | fix_ratio, pagerank, total_changes |

### Condition

```python
fix_ratio > 0.4 AND
pctl(pagerank) > 0.75 AND
total_changes > median(total_changes)  # hotspot filter
```

### Evidence

- **IR5t**: fix_ratio, list of fix commits
- **IR3**: pagerank, blast_radius

### Remediation

"40%+ of changes are bug fixes in a central file. Root-cause analysis needed."

### Effort

MEDIUM

### fix_ratio Detection

```python
FIX_PATTERNS = [
    r'\bfix\b', r'\bbug\b', r'\bpatch\b', r'\bhotfix\b',
    r'\bresolve\b', r'\brepair\b', r'\bcorrect\b',
]

def is_fix_commit(message: str) -> bool:
    message_lower = message.lower()
    return any(re.search(p, message_lower) for p in FIX_PATTERNS)

def compute_fix_ratio(commits: list[Commit]) -> float:
    if not commits:
        return 0.0
    fix_count = sum(1 for c in commits if is_fix_commit(c.message))
    return fix_count / len(commits)
```

---

## 22. ACCIDENTAL_COUPLING

Files with dependency but no semantic relationship.

| Property | Value |
|----------|-------|
| **Scope** | FILE_PAIR |
| **Severity** | 0.50 |
| **Phase** | 2 |
| **Hotspot** | No |
| **Requires** | IMPORTS, concepts (from semantics) |

### Condition

```python
imports(A, B) AND
concept_overlap(A, B) < 0.2
```

Where:
```
concept_overlap = |concepts(A) ∩ concepts(B)| / |concepts(A) ∪ concepts(B)|
```

This is Jaccard similarity of concept sets.

### Evidence

- **G1**: structural edge (import)
- **IR2**: concept lists for both files
- Jaccard overlap score

### Remediation

"Connected but unrelated concepts. Consider removing or abstracting the dependency."

### Effort

MEDIUM

### Implementation

```python
def accidental_coupling_predicate(
    store: FactStore,
    a: EntityId,
    b: EntityId,
) -> bool:
    # Check for import edge
    if not store.relations.has(a, RelationType.IMPORTS, b):
        return False

    # Get concepts
    semantics_a = store.get_semantics(a.key)
    semantics_b = store.get_semantics(b.key)

    if not semantics_a or not semantics_b:
        return False

    concepts_a = set(semantics_a.concepts)
    concepts_b = set(semantics_b.concepts)

    if not concepts_a or not concepts_b:
        return False

    # Jaccard similarity
    intersection = concepts_a & concepts_b
    union = concepts_a | concepts_b
    overlap = len(intersection) / len(union)

    return overlap < 0.2

def accidental_coupling_evidence(
    store: FactStore,
    a: EntityId,
    b: EntityId,
) -> dict:
    semantics_a = store.get_semantics(a.key)
    semantics_b = store.get_semantics(b.key)

    concepts_a = set(semantics_a.concepts)
    concepts_b = set(semantics_b.concepts)

    intersection = concepts_a & concepts_b
    union = concepts_a | concepts_b

    return {
        "concepts_a": list(concepts_a),
        "concepts_b": list(concepts_b),
        "shared_concepts": list(intersection),
        "overlap": len(intersection) / len(union) if union else 0,
    }
```

---

## Cross-Dimensional Summary

These patterns combine signals from different dimensions to find issues that no single dimension could detect:

| Pattern | Dimensions Combined |
|---------|---------------------|
| WEAK_LINK | D4 (pagerank), D5 (cognitive), D6 (churn), D7 (bus_factor) |
| BUG_ATTRACTOR | D4 (pagerank), D8 (fix_ratio) |
| ACCIDENTAL_COUPLING | D4 (imports), D3 (concepts) |

This is the power of multi-dimensional analysis: issues emerge at the intersection of dimensions.
