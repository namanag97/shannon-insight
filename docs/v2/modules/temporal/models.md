# temporal/ Data Models

All data models for the temporal spine. These capture the full temporal profile of a codebase as derived from git history.

## Trajectory Enum

```python
class Trajectory(str, Enum):
    DORMANT     = "dormant"
    STABILIZING = "stabilizing"
    STABLE      = "stable"
    CHURNING    = "churning"
    SPIKING     = "spiking"
```

Classification rules are defined in `registry/temporal-operators.md` (Trajectory operator). The canonical decision tree:

```
if total_changes <= 1:                              DORMANT
elif velocity < -threshold AND CV < 1:              STABILIZING
elif velocity > threshold AND CV > 0.5:             SPIKING
elif CV > 0.5:                                      CHURNING
else:                                               STABLE
```

**Status**: v2 NEW. Current code uses string literals (`"dormant"`, `"stabilizing"`, `"spiking"`, `"churning"`). The current code is also missing STABLE -- files that are not dormant and have low CV fall through to "stabilizing" incorrectly. v2 fixes this.

---

## CommitRef

```python
@dataclass
class CommitRef:
    sha:       str            # full 40-char hex hash
    timestamp: int            # unix epoch seconds
    author:    str            # email address from git log
    message:   str            # commit subject line (%s)
    files:     list[str]      # relative paths changed in this commit
```

**Status**: v2 extends the existing `Commit` dataclass. Current `Commit` has `hash`, `timestamp`, `author`, `files`. v2 renames `hash` to `sha` (avoids shadowing builtin) and adds `message` for intent classification.

**Backward compatibility**: The existing `Commit` name and fields continue to work during migration. `CommitRef` is the v2 canonical name.

---

## GitHistory

```python
@dataclass
class GitHistory:
    commits:    list[CommitRef]    # newest first (git log natural order)
    file_set:   set[str]          # union of all files across all commits
    span_days:  int               # (newest_timestamp - oldest_timestamp) / 86400
```

Properties:

| Property | Type | Computation |
|----------|------|-------------|
| `total_commits` | int | `len(commits)` |

**Status**: EXISTS. No changes in v2 except the element type changes from `Commit` to `CommitRef`.

---

## FileHistory

```python
@dataclass
class FileHistory:
    path:               str

    # Commit references
    commits:            list[CommitRef]     # all commits touching this file, newest first
    total_changes:      int                 # len(commits)
    first_seen:         int                 # unix timestamp of oldest commit
    last_modified:      int                 # unix timestamp of newest commit

    # Churn (D6 CHANGE)
    churn_series:       list[int]           # changes per time window
    churn_slope:        float               # linear regression slope of window series
    churn_cv:           float               # coefficient of variation of window series
    churn_trajectory:   Trajectory          # classified trajectory

    # Authorship (D7 AUTHORSHIP)
    authors:            dict[str, int]      # author email -> commit count
    author_count:       int                 # len(authors)
    author_entropy:     float               # Shannon entropy of author distribution
    bus_factor:         float               # 2^H (effective author count)
    primary_author:     str                 # mode of author distribution
    primary_author_pct: float               # fraction of commits by primary author

    # Intent (D8 INTENT)
    fix_ratio:          float               # fraction of commits classified as fixes
    refactor_ratio:     float               # fraction classified as refactoring
```

**Status**: v2 NEW. Unifies data currently split across `ChurnSeries` (churn fields) and computed ad-hoc in the insights layer (author fields). Intent fields are entirely new.

**Signal mapping**: This model is the source of per-file signals 27-34 from `registry/signals.md`.

| Field | Signal # | Signal name |
|-------|----------|-------------|
| `total_changes` | 27 | `total_changes` |
| `churn_trajectory` | 28 | `churn_trajectory` |
| `churn_slope` | 29 | `churn_slope` |
| `churn_cv` | 30 | `churn_cv` |
| `bus_factor` | 31 | `bus_factor` |
| `author_entropy` | 32 | `author_entropy` |
| `fix_ratio` | 33 | `fix_ratio` |
| `refactor_ratio` | 34 | `refactor_ratio` |

---

## ChurnSeries (legacy)

```python
@dataclass
class ChurnSeries:
    file_path:      str
    window_counts:  list[int]       # changes per time window
    total_changes:  int
    trajectory:     str             # string literal, not enum
    slope:          float           # linear regression slope
```

**Status**: EXISTS. Superseded by `FileHistory` in v2 but retained for backward compatibility during migration. Missing `churn_cv` as an explicit field.

---

## PairDynamics

```python
@dataclass
class PairDynamics:
    file_a:              str
    file_b:              str
    cochange_count:      int         # times changed in same commit
    lift:                float       # observed / expected co-change frequency
    confidence:          float       # max(P(B|A), P(A|B))
    has_structural_edge: bool        # does an import edge exist between these files?
    temporal_coupling:   float       # lift * confidence
```

**Status**: v2 NEW. Extends the existing `CoChangePair` with `has_structural_edge` (populated by graph/ after merge) and `temporal_coupling` (derived score). Drops the directional `confidence_a_b` / `confidence_b_a` split in favor of the max.

**Note on `has_structural_edge`**: This field is set to `False` by default when temporal/ produces the model. The graph/ module sets it to `True` for pairs that also have a structural (import) edge. This is the co-change enrichment join point.

---

## CoChangePair (legacy)

```python
@dataclass
class CoChangePair:
    file_a:          str
    file_b:          str
    cochange_count:  int
    total_a:         int
    total_b:         int
    confidence_a_b:  float      # P(B | A changed)
    confidence_b_a:  float      # P(A | B changed)
    lift:            float
```

**Status**: EXISTS. Superseded by `PairDynamics` in v2 but retained for backward compatibility.

---

## CoChangeMatrix (legacy)

```python
@dataclass
class CoChangeMatrix:
    pairs:              dict[tuple[str, str], CoChangePair]   # sparse
    total_commits:      int
    file_change_counts: dict[str, int]
```

**Status**: EXISTS. Remains available in v2. The v2 `TemporalModel.coevolution` dict replaces this as the primary interface.

---

## ModuleDynamics

```python
@dataclass
class ModuleDynamics:
    module_path:        str
    velocity:           float       # commits per week touching any file in module
    coordination_cost:  float       # mean(distinct authors per commit touching module)
    knowledge_gini:     float       # Gini coefficient of per-author commit counts
    module_bus_factor:  float       # min(bus_factor) across high-centrality files
    stability:          float       # fraction of files with STABILIZING or STABLE trajectory
    growth_rate:        float       # new files per month (files appearing in recent history)
    fix_hotspot_ratio:  float       # fraction of module commits that are fixes
```

**Status**: v2 NEW. Module-level aggregation of temporal data. Source of per-module signals 45-48 from `registry/signals.md`.

| Field | Signal # | Signal name |
|-------|----------|-------------|
| `velocity` | 45 | `velocity` |
| `coordination_cost` | 46 | `coordination_cost` |
| `knowledge_gini` | 47 | `knowledge_gini` |
| `module_bus_factor` | 48 | `module_bus_factor` |

**Note on `module_bus_factor`**: Defined as `min(bus_factor)` across files in the module that have high centrality (top quartile by pagerank). This requires centrality data from graph/, so when temporal/ runs in isolation, it falls back to `min(bus_factor)` across all files in the module.

---

## CodebaseDynamics

```python
@dataclass
class CodebaseDynamics:
    commit_frequency:    list[float]     # commits per week over time (time series)
    active_contributors: list[int]       # distinct authors per month (time series)
    growth_rate:         float           # new files per month
    entropy_rate:        float           # H of commit distribution across modules
    bus_factor_global:   float           # min bus factor across critical modules
    debt_velocity:       float           # rate of finding accumulation (from IR6, filled later)
```

**Status**: v2 NEW. Codebase-level temporal summary. `debt_velocity` is populated by the insights layer after findings are computed, not by temporal/ directly.

---

## TemporalModel

```python
@dataclass
class TemporalModel:
    file_histories:     dict[str, FileHistory]                  # path -> per-file profile
    coevolution:        dict[tuple[str, str], PairDynamics]     # sparse pair dynamics
    module_dynamics:    dict[str, ModuleDynamics]                # module path -> dynamics
    codebase_dynamics:  CodebaseDynamics                         # global summary

    # Legacy access (backward compat)
    git_history:        GitHistory                               # raw commit data
```

**Status**: v2 NEW. Top-level container that replaces the current pattern of returning `GitHistory`, `Dict[str, ChurnSeries]`, and `CoChangeMatrix` as separate objects. This is the single return type of the temporal extractor.

---

## SpectralSummary (misplaced)

```python
@dataclass
class SpectralSummary:
    fiedler_value:  float
    num_components: int
    eigenvalues:    list[float]
    spectral_gap:   float
```

**Status**: EXISTS in `temporal/models.py` but does not belong here. This is a graph/ concern (spectral decomposition of the Laplacian). **Phase 3 moves `spectral_gap` to `graph/models.py:GraphAnalysis`. The `fiedler_value`, `num_components`, and `eigenvalues` fields also move to GraphAnalysis. The `SpectralSummary` class is then removed from temporal/models.py.**
