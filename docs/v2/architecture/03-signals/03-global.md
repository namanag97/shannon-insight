# Global Signals (#52-62)

11 signals computed on the CODEBASE entity.

---

## Graph Structure (Phase 0)

### #52 modularity

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [-0.5, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | Louvain Q score |

```
Q = (1/2m) Σ [A_ij - k_i × k_j / (2m)] δ(c_i, c_j)

where:
  A_ij = adjacency matrix
  k_i = degree of node i
  m = total edges
  c_i = community of node i
  δ = 1 if same community, 0 otherwise

Q > 0.3 = good community structure
Q < 0.1 = weak structure
```

---

### #53 fiedler_value

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | λ₂ of graph Laplacian L = D - A |
| **Edge case** | 0 = disconnected graph |

Also called "algebraic connectivity". Computed via Lanczos iteration for top-k eigenvalues.

```
λ₂ = 0: graph is disconnected
λ₂ small: bottleneck exists (easy to partition)
λ₂ large: well-connected (hard to partition)
```

---

### #54 spectral_gap

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | `λ₂ / λ₃` |

```
Large gap: clear best cut (well-defined clusters)
Small gap: ambiguous structure
```

---

### #55 cycle_count

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | Count of SCCs with |nodes| > 1 (Tarjan's algorithm) |

Each SCC with > 1 node is a circular dependency.

---

## Distribution Metrics (Phase 3)

### #56 centrality_gini

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | Gini coefficient of pagerank distribution |

```
> 0.7 = hub-dominated (few files have most traffic)
< 0.3 = evenly distributed
```

---

### #57 orphan_ratio

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | `count(is_orphan = true) / total_files` |

---

### #58 phantom_ratio

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | `unresolved_import_edges / total_import_edges` |

---

### #59 glue_deficit

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | graph/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | `1 - |{v: in_degree(v) > 0 AND out_degree(v) > 0}| / |V|` |

Fraction of nodes that are NOT internal (glue). High = many leaf/root nodes, few orchestrators.

---

## Composites (Phase 5)

### #60 wiring_score

| Property | Value |
|----------|-------|
| **Dimension** | Composite |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 5 |
| **Source** | signals/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | See below |

```
wiring_score = 1 - (
    0.25 × orphan_ratio
  + 0.25 × phantom_ratio
  + 0.20 × glue_deficit
  + 0.15 × mean(stub_ratio across all files)
  + 0.15 × clone_ratio
)

where clone_ratio = |files in NCD clone pairs| / |total files|
```

Also called "AI quality score" — measures structural completeness.

---

### #61 architecture_health

| Property | Value |
|----------|-------|
| **Dimension** | Composite |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 5 |
| **Source** | signals/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | See below |

```
architecture_health = 0.25 × (1 - violation_rate)
                    + 0.20 × mean(cohesion across modules)
                    + 0.20 × (1 - mean(coupling across modules))
                    + 0.20 × (1 - mean(main_seq_distance across modules))
                    + 0.15 × mean(boundary_alignment across modules)

where violation_rate = violating_cross_module_edges / total_cross_module_edges
```

---

### #62 codebase_health

| Property | Value |
|----------|-------|
| **Dimension** | Composite |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 5 |
| **Source** | signals/ |
| **Percentileable** | No (single value) |
| **Absolute threshold** | — |
| **Formula** | See below |

```
codebase_health = 0.30 × architecture_health
               + 0.30 × wiring_score
               + 0.20 × (global_bus_factor / team_size)
               + 0.20 × modularity

where:
  global_bus_factor = min_bus_factor_critical (capped at team_size)
  min_bus_factor_critical = min(bus_factor) across files with pctl(pagerank) > 0.75
  team_size = |distinct authors in recent window|
```

**The one number.** Display as 1-10 scale (multiply by 10).

**Note**: Finding density is NOT included (circular dependency with finders). It can be displayed alongside but must not be part of the formula.

---

## Summary Table

| # | Signal | Dimension | Polarity | Phase |
|---|--------|-----------|----------|-------|
| 52 | modularity | D4 | HIGH_IS_GOOD | 0 |
| 53 | fiedler_value | D4 | HIGH_IS_GOOD | 0 |
| 54 | spectral_gap | D4 | HIGH_IS_GOOD | 0 |
| 55 | cycle_count | D4 | HIGH_IS_BAD | 0 |
| 56 | centrality_gini | D4 | HIGH_IS_BAD | 3 |
| 57 | orphan_ratio | D4 | HIGH_IS_BAD | 3 |
| 58 | phantom_ratio | D4 | HIGH_IS_BAD | 3 |
| 59 | glue_deficit | D4 | HIGH_IS_BAD | 3 |
| 60 | wiring_score | Composite | HIGH_IS_GOOD | 5 |
| 61 | architecture_health | Composite | HIGH_IS_GOOD | 5 |
| 62 | codebase_health | Composite | HIGH_IS_GOOD | 5 |
