# Per-Module Signals (#37-51)

15 signals computed on MODULE entities.

---

## Martin Metrics (Phase 4)

### #37 cohesion

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `internal_edges / (file_count × (file_count - 1))` |
| **Edge case** | 0 if file_count ≤ 1 |

High cohesion = files within module import each other. Low cohesion = files are unrelated.

---

### #38 coupling

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `external_edges / (internal_edges + external_edges)` |
| **Edge case** | 0 if no edges |

High coupling = module depends heavily on others. Low coupling = self-contained.

---

### #39 instability

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float or None |
| **Range** | [0, 1] or None |
| **Polarity** | NEUTRAL |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `Ce / (Ca + Ce)` |
| **Edge case** | **None if Ca + Ce = 0** (isolated module) |

```
Ca = afferent coupling (incoming edges from other modules)
Ce = efferent coupling (outgoing edges to other modules)
I = 0: maximally stable (all dependents, no dependencies)
I = 1: maximally unstable (all dependencies, no dependents)
```

**Important**: Finders must guard against `instability = None`.

---

### #40 abstractness

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | NEUTRAL |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `abstract_symbols / total_symbols` |

Abstract symbols (Python):
- Classes with ABC base
- Classes with Protocol base
- Classes with NotImplementedError in methods

**Note**: "never-instantiated" detection deferred until CALL edges exist.

---

### #41 main_seq_distance

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float or skip |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `|abstractness + instability - 1|` |
| **Edge case** | **Skip if instability = None** |

```
D = 0: on main sequence (ideal)
D > 0: off main sequence

Zone of Pain: A < 0.3 AND I < 0.3 (concrete and stable — hard to change)
Zone of Uselessness: A > 0.7 AND I > 0.7 (abstract and unstable — why?)
```

---

### #42 boundary_alignment

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `files_in_dominant_louvain_community / total_files_in_module` |

High = directory boundary matches dependency structure.
Low = files in this directory actually belong to different communities.

---

### #43 layer_violation_count

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Count of backward or skip edges into this module |
| **Edge case** | 0 if modules in same SCC |

---

### #44 role_consistency

| Property | Value |
|----------|-------|
| **Dimension** | D3 NAMING |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `max(role_count) / total_files_in_module` |

1.0 = all files have same role. Low = mixed roles (code smell).

---

## Temporal Aggregates (Phase 5)

### #45 velocity

| Property | Value |
|----------|-------|
| **Dimension** | D6 CHANGE |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | NEUTRAL |
| **Phase** | 5 |
| **Source** | signals/ (aggregated) |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Commits per week touching any file in module |
| **Edge case** | 0.0 if no commits in recent window |

---

### #46 coordination_cost

| Property | Value |
|----------|-------|
| **Dimension** | D7 AUTHORSHIP |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 5 |
| **Source** | signals/ (aggregated) |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `mean(distinct_authors_per_commit)` for commits touching module |

High = many authors touch same commits. Low = clear ownership.

---

### #47 knowledge_gini

| Property | Value |
|----------|-------|
| **Dimension** | D7 AUTHORSHIP |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 5 |
| **Source** | signals/ (aggregated) |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Gini coefficient of per-author commit counts within module |

> 0.7 = knowledge silo (one author dominates).

---

### #48 module_bus_factor

| Property | Value |
|----------|-------|
| **Dimension** | D7 AUTHORSHIP |
| **Type** | float |
| **Range** | [1, ∞) |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 5 |
| **Source** | signals/ (aggregated) |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `min(bus_factor)` across high-centrality files in module |

The weakest link determines module's bus factor.

---

### #49 mean_cognitive_load

| Property | Value |
|----------|-------|
| **Dimension** | D5 INFORMATION |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 5 |
| **Source** | signals/ (aggregated) |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `mean(cognitive_load)` across files in module |

---

## Size (Phase 4)

### #50 file_count

| Property | Value |
|----------|-------|
| **Dimension** | D1 SIZE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | NEUTRAL |
| **Phase** | 4 |
| **Source** | architecture/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Number of source files in module |

---

## Composite (Phase 5)

### #51 health_score

| Property | Value |
|----------|-------|
| **Dimension** | Composite |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 5 |
| **Source** | signals/ |
| **Percentileable** | No (already composite) |
| **Absolute threshold** | — |
| **Formula** | See below |

```
health_score(m) = 0.20 × cohesion(m)
               + 0.15 × (1 - coupling(m))
               + 0.20 × (1 - main_seq_distance(m))
               + 0.15 × boundary_alignment(m)
               + 0.15 × role_consistency(m)
               + 0.15 × (1 - mean(stub_ratio across files in m))
```

**None guard**: If `instability = None` (isolated module), skip the main_seq_distance term and redistribute weight:

```python
if instability is None:
    # Redistribute 0.20 proportionally
    scale = 1.0 / 0.80  # = 1.25
    return (0.20 * scale * cohesion +
            0.15 * scale * (1 - coupling) +
            0.15 * scale * boundary_alignment +
            0.15 * scale * role_consistency +
            0.15 * scale * (1 - mean_stub_ratio))
```
