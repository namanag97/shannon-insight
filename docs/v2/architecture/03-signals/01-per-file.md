# Per-File Signals (#1-36)

36 signals computed on FILE entities.

---

## Syntactic Signals (Phase 0-1)

### #1 lines

| Property | Value |
|----------|-------|
| **Dimension** | D1 SIZE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 0 |
| **Source** | scanning/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 500 |
| **Formula** | Line count of file |

---

### #2 function_count

| Property | Value |
|----------|-------|
| **Dimension** | D1 SIZE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 0 |
| **Source** | scanning/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 30 |
| **Formula** | Count of function/method definitions |

---

### #3 class_count

| Property | Value |
|----------|-------|
| **Dimension** | D1 SIZE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | NEUTRAL |
| **Phase** | 0 |
| **Source** | scanning/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Count of class definitions |

---

### #4 max_nesting

| Property | Value |
|----------|-------|
| **Dimension** | D2 SHAPE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 1 |
| **Source** | scanning/ (tree-sitter) |
| **Percentileable** | Yes |
| **Absolute threshold** | > 4 |
| **Formula** | Max nesting depth across all functions in file |

---

### #5 impl_gini

| Property | Value |
|----------|-------|
| **Dimension** | D2 SHAPE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 1 |
| **Source** | signals/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 0.6 |
| **Formula** | `G = (2 × Σᵢ i × xᵢ) / (n × Σ xᵢ) - (n + 1) / n` where xᵢ = function body_token counts sorted ascending |
| **Edge case** | 0.0 if ≤ 1 function |

G ≈ 0: uniform function sizes. G > 0.6: bimodal (some complete, some stubs) — AI code signature.

---

### #6 stub_ratio

| Property | Value |
|----------|-------|
| **Dimension** | D2 SHAPE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 1 |
| **Source** | scanning/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 0.5 |
| **Formula** | `mean(stub_score(f) for f in functions)` |
| **Edge case** | 0.0 if no functions |

```python
def stub_score(f: FunctionDef) -> float:
    # Hard classify
    if f.body_tokens < 5:
        return 1.0
    if re.match(r'^\s*(pass|\.\.\.return\s+None?)\s*$', f.body):
        return 1.0
    # Soft classify
    return 1 - min(1, f.body_tokens / (f.signature_tokens * 3))
```

---

### #7 import_count

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | NEUTRAL |
| **Phase** | 0 |
| **Source** | scanning/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Count of import declarations |

---

## Semantic Signals (Phase 2)

### #8 role

| Property | Value |
|----------|-------|
| **Dimension** | D3 NAMING |
| **Type** | enum (Role) |
| **Range** | Role enum |
| **Polarity** | — (categorical) |
| **Phase** | 2 |
| **Source** | semantics/ |
| **Percentileable** | No |
| **Absolute threshold** | — |
| **Formula** | Decision tree on structural signals |

```python
class Role(Enum):
    MODEL = "model"           # Dataclasses only
    SERVICE = "service"       # Classes with methods
    UTILITY = "utility"       # Functions only, no classes
    CONFIG = "config"         # settings, constants
    TEST = "test"             # test_*.py, *_test.py
    CLI = "cli"               # __main__, click/typer
    INTERFACE = "interface"   # ABC, Protocol only
    EXCEPTION = "exception"   # Exception classes only
    CONSTANT = "constant"     # All caps assignments
    ENTRY_POINT = "entry_point"  # has __main__ guard
    MIGRATION = "migration"   # alembic/django migration
    UNKNOWN = "unknown"       # Default
```

---

### #9 concept_count

| Property | Value |
|----------|-------|
| **Dimension** | D3 NAMING |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 2 |
| **Source** | semantics/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Count of concept clusters from TF-IDF + Louvain |
| **Edge case** | 1 if < 3 functions (role-based single concept) |

---

### #10 concept_entropy

| Property | Value |
|----------|-------|
| **Dimension** | D3 NAMING |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 2 |
| **Source** | semantics/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 1.5 |
| **Formula** | `H = -Σ w(c) × log₂(w(c))` where w(c) = weight of concept c |
| **Edge case** | 0.0 if < 3 functions (single concept) |

H = 0: single concept. H > 1.5: many competing concepts (god file risk).

---

### #11 naming_drift

| Property | Value |
|----------|-------|
| **Dimension** | D3 NAMING |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 2 |
| **Source** | semantics/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 0.7 |
| **Formula** | `1 - cosine(tfidf(filename_tokens), tfidf(content_concept_tokens))` |
| **Edge case** | 0.0 for generic filenames (utils.py, helpers.py) |

---

### #12 todo_density

| Property | Value |
|----------|-------|
| **Dimension** | D3 NAMING |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 1 |
| **Source** | scanning/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 0.05 |
| **Formula** | `(TODO + FIXME + HACK count) / lines` |

---

### #13 docstring_coverage

| Property | Value |
|----------|-------|
| **Dimension** | D3 NAMING |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 2 |
| **Source** | semantics/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `documented_public_symbols / total_public_symbols` |
| **Edge case** | None for languages without docstring support |

---

## Graph Signals (Phase 0, 3)

### #14 pagerank

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `PR(v) = (1-d)/N + d × Σ PR(u)/out_degree(u)` for u→v, d=0.85, 50 iterations |

---

### #15 betweenness

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `B(v) = Σ_{s≠v≠t} σ(s,t|v) / σ(s,t)` (Brandes' algorithm) |

---

### #16 in_degree

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | NEUTRAL |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Count of files that import this file |

---

### #17 out_degree

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | NEUTRAL |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Count of files this file imports |

---

### #18 blast_radius_size

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, n-1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `|BFS(v, reverse(G))| - 1` (transitive dependents) |

---

### #19 depth

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) or -1 |
| **Polarity** | NEUTRAL |
| **Phase** | 3 |
| **Source** | graph/ |
| **Percentileable** | No |
| **Absolute threshold** | — |
| **Formula** | Shortest path from nearest entry point via BFS |
| **Edge case** | -1 = unreachable (orphan) |

---

### #20 is_orphan

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | bool |
| **Range** | {0, 1} |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | graph/ |
| **Percentileable** | No |
| **Absolute threshold** | = 1 |
| **Formula** | `in_degree = 0 AND role ∉ {ENTRY_POINT, TEST}` |

---

### #21 phantom_import_count

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 0 |
| **Formula** | Count of import declarations where `resolved_path = null` and not external |

---

### #22 broken_call_count

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | — (future) |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 0 |
| **Formula** | Count of CALL edge targets that cannot be resolved |
| **Note** | Defaults to 0 until CALL edges implemented |

---

### #23 community

| Property | Value |
|----------|-------|
| **Dimension** | D4 REFERENCE |
| **Type** | int |
| **Range** | [0, k) |
| **Polarity** | — (assignment ID) |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | No |
| **Absolute threshold** | — |
| **Formula** | Louvain community assignment ID |
| **Note** | Not a quality signal; used for boundary alignment |

---

### #24 compression_ratio

| Property | Value |
|----------|-------|
| **Dimension** | D5 INFORMATION |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | NEUTRAL |
| **Phase** | 0 |
| **Source** | graph/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `len(zlib.compress(content)) / len(content)` |

< 0.15 = highly repetitive. 0.3-0.6 = normal. > 0.7 = very dense.

---

### #25 semantic_coherence

| Property | Value |
|----------|-------|
| **Dimension** | D5 INFORMATION |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 2 |
| **Source** | semantics/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `mean(cosine(vᵢ, vⱼ))` for all function-level TF-IDF vector pairs |
| **Phase 0** | Partial (import-based proxy) |
| **Phase 2** | Full (function-level TF-IDF pairwise cosine) |

---

### #26 cognitive_load

| Property | Value |
|----------|-------|
| **Dimension** | D5 INFORMATION |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 1 |
| **Source** | signals/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | See below |

```python
cognitive_load = (concepts × complexity × nesting_factor) × (1 + G)

where:
  concepts = function_count + class_count
  complexity = mean cyclomatic complexity
  nesting_factor = e^(max_nesting / 5)
  G = gini(function_body_token_counts)
```

The exponential nesting penalty reflects nonlinear comprehension cost.

---

## Temporal Signals (Phase 3)

### #27 total_changes

| Property | Value |
|----------|-------|
| **Dimension** | D6 CHANGE |
| **Type** | int |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Count of commits touching this file |
| **Edge case** | 0 if no git history |

---

### #28 churn_trajectory

| Property | Value |
|----------|-------|
| **Dimension** | D6 CHANGE |
| **Type** | enum (Trajectory) |
| **Range** | Trajectory enum |
| **Polarity** | — (categorical) |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | No |
| **Absolute threshold** | — |
| **Formula** | Classification of churn time series |
| **Edge case** | DORMANT if ≤ 1 total change |

```python
class Trajectory(Enum):
    DORMANT = "dormant"         # ≤ 1 change ever
    STABILIZING = "stabilizing" # CV < 0.5 and slope < 0
    STABLE = "stable"           # CV < 1.0 and |slope| < 0.1
    CHURNING = "churning"       # CV > 1.0
    SPIKING = "spiking"         # Recent spike > 3σ above mean
```

---

### #29 churn_slope

| Property | Value |
|----------|-------|
| **Dimension** | D6 CHANGE |
| **Type** | float |
| **Range** | (-∞, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | Linear regression slope of changes-per-4-week-window series |
| **Edge case** | 0 if no git history |

---

### #30 churn_cv

| Property | Value |
|----------|-------|
| **Dimension** | D6 CHANGE |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 1.0 |
| **Formula** | Coefficient of variation = `std(changes_per_window) / mean(changes_per_window)` |
| **Edge case** | 0 if no git history |

---

### #31 bus_factor

| Property | Value |
|----------|-------|
| **Dimension** | D7 AUTHORSHIP |
| **Type** | float |
| **Range** | [1, ∞) |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | Yes |
| **Absolute threshold** | = 1 (risk) |
| **Formula** | `2^H` where H = author_entropy |
| **Edge case** | 1.0 if single-commit file |

bus_factor = 1: single author. bus_factor = k: k equally-contributing authors.

---

### #32 author_entropy

| Property | Value |
|----------|-------|
| **Dimension** | D7 AUTHORSHIP |
| **Type** | float |
| **Range** | [0, ∞) |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `H = -Σ p(a) × log₂(p(a))` where p(a) = commits_by_author / total_commits |
| **Edge case** | 0.0 if single author |

H = 0: single author. H = log₂(k): k equally-contributing authors.

---

### #33 fix_ratio

| Property | Value |
|----------|-------|
| **Dimension** | D8 INTENT |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | Yes |
| **Absolute threshold** | > 0.4 |
| **Formula** | `|commits matching fix/bug/patch/hotfix/resolve/repair| / total_commits` |
| **Edge case** | 0.0 if no commits match fix patterns |

---

### #34 refactor_ratio

| Property | Value |
|----------|-------|
| **Dimension** | D8 INTENT |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_GOOD |
| **Phase** | 3 |
| **Source** | temporal/ |
| **Percentileable** | Yes |
| **Absolute threshold** | — |
| **Formula** | `|commits matching refactor/restructure/reorganize/clean/simplify| / total_commits` |
| **Edge case** | 0.0 if no commits match refactor patterns |

---

## Composite Signals (Phase 5)

### #35 risk_score

| Property | Value |
|----------|-------|
| **Dimension** | Composite |
| **Type** | float |
| **Range** | [0, 1] |
| **Polarity** | HIGH_IS_BAD |
| **Phase** | 5 |
| **Source** | signals/ |
| **Percentileable** | No (already composite) |
| **Absolute threshold** | — |
| **Formula** | See [07-composites/README.md](../07-composites/README.md) |

```
risk_score(f) = 0.25 × pctl(pagerank, f)
              + 0.20 × pctl(blast_radius_size, f)
              + 0.20 × pctl(cognitive_load, f)
              + 0.20 × instability_factor(f)
              + 0.15 × (1 - bus_factor(f) / max_bus_factor)

where instability_factor = 1.0 if churn_trajectory ∈ {CHURNING, SPIKING}
                           0.3 otherwise
```

---

### #36 wiring_quality

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
| **Formula** | See [07-composites/README.md](../07-composites/README.md) |

```
wiring_quality(f) = 1 - (
    0.30 × is_orphan(f)
  + 0.25 × stub_ratio(f)
  + 0.25 × (phantom_import_count(f) / max(import_count(f), 1))
  + 0.20 × (broken_call_count(f) / max(total_calls(f), 1))
)
```
