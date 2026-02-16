# Social/Team Patterns

3 patterns for detecting team and ownership issues.

---

## 14. KNOWLEDGE_SILO

Critical file with single owner.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.70 |
| **Phase** | 3 |
| **Hotspot** | Yes |
| **Requires** | bus_factor, pagerank, total_changes |

### Condition

```python
bus_factor <= 1.5 AND
pctl(pagerank) > 0.75 AND
total_changes > median(total_changes)  # hotspot filter
```

### Evidence

- **IR5t**: bus_factor, author list with commit counts
- **IR3**: pagerank percentile

### Remediation

"Pair-program or rotate ownership. Single point of knowledge failure."

### Effort

LOW

### Polarity Note

- `bus_factor` is HIGH_IS_GOOD, so we check for low values (≤ 1.5)
- `pagerank` is HIGH_IS_BAD, so we check for high values (> 0.75)

---

## 15. CONWAY_VIOLATION

Coupled modules maintained by different teams.

| Property | Value |
|----------|-------|
| **Scope** | MODULE_PAIR |
| **Severity** | 0.55 |
| **Phase** | 4 |
| **Hotspot** | No |
| **Requires** | DEPENDS_ON, AUTHORED_BY, author distance (G5) |

### Condition

```python
d_author(M₁, M₂) > 0.8 AND
structural_coupling(M₁, M₂) > 0.3
```

Where:
- `d_author` = weighted Jaccard distance of author sets
- `structural_coupling` = normalized cross-module edge count

### Evidence

- **G5**: author distance
- **G1**: structural coupling
- Module names

### Remediation

"Coupled modules maintained by different teams. Align team boundaries."

### Effort

HIGH

### Implementation

```python
def author_distance(module_a: str, module_b: str, store: FactStore) -> float:
    """
    Weighted Jaccard distance of author contributions across modules.
    """
    authors_a = aggregate_authors(module_a, store)  # email → total_commits
    authors_b = aggregate_authors(module_b, store)

    all_authors = set(authors_a.keys()) | set(authors_b.keys())
    total_a = sum(authors_a.values()) or 1
    total_b = sum(authors_b.values()) or 1

    min_sum = 0
    max_sum = 0
    for author in all_authors:
        wa = authors_a.get(author, 0) / total_a
        wb = authors_b.get(author, 0) / total_b
        min_sum += min(wa, wb)
        max_sum += max(wa, wb)

    return 1 - (min_sum / max_sum) if max_sum > 0 else 0

def structural_coupling(module_a: str, module_b: str, store: FactStore) -> float:
    """
    Normalized count of cross-module edges.
    """
    edges = store.relations.by_type(RelationType.DEPENDS_ON)
    a_to_b = sum(1 for e in edges if e.source.key == module_a and e.target.key == module_b)
    b_to_a = sum(1 for e in edges if e.source.key == module_b and e.target.key == module_a)

    # Normalize by module sizes
    files_a = len([f for f in store.files() if get_module(f) == module_a])
    files_b = len([f for f in store.files() if get_module(f) == module_b])
    max_edges = files_a * files_b

    return (a_to_b + b_to_a) / max_edges if max_edges > 0 else 0
```

---

## 16. REVIEW_BLINDSPOT

High-centrality code with single owner and no tests.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.80 |
| **Phase** | 3 |
| **Hotspot** | Yes |
| **Requires** | pagerank, bus_factor, has_test (mapping), total_changes |

### Condition

```python
pctl(pagerank) > 0.75 AND
bus_factor <= 1.5 AND
NOT has_test_file AND
total_changes > median(total_changes)  # hotspot filter
```

### Test File Detection

```python
def has_test_file(path: str, store: FactStore) -> bool:
    """
    Check if file has a corresponding test file.

    Naming conventions:
    - src/auth/login.py → tests/test_login.py
    - src/auth/login.py → tests/auth/test_login.py
    - src/auth/login.py → src/auth/login_test.py
    """
    stem = Path(path).stem
    patterns = [
        f"test_{stem}.py",
        f"{stem}_test.py",
        f"**/test_{stem}.py",
        f"**/{stem}_test.py",
    ]
    return any(store.file_exists(p) for p in patterns)
```

### Evidence

- **IR3**: centrality (pagerank percentile)
- **IR5t**: author distribution (bus_factor)
- Test file presence

### Remediation

"High-centrality code with single owner and no tests. Add tests and reviewer."

### Effort

MEDIUM
