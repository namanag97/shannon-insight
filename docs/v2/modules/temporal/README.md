# temporal/ Module Specification

Git history in, change patterns out. This module is the **temporal spine** -- it runs fully in parallel with the structural spine (scanning/ -> semantics/ -> graph/ -> architecture/) and has zero data dependencies on any of them.

## Responsibility

Parse git log output into structured models that capture three facets of how code evolves:

1. **Change patterns** (D6 CHANGE) -- churn trajectories, velocity, volatility
2. **Authorship patterns** (D7 AUTHORSHIP) -- bus factor, knowledge distribution, coordination cost
3. **Intent patterns** (D8 INTENT) -- fix ratio, refactor ratio, commit classification

These three dimensions are irreducible: the same file can be stable or churning (D6) regardless of how many people touch it (D7) or why they touch it (D8).

## Exports

| Type | Description | Status |
|------|-------------|--------|
| `GitExtractor` | Parses git log via subprocess into `GitHistory` | EXISTS |
| `GitHistory` | Raw commit list + file set + span | EXISTS |
| `ChurnSeries` | Per-file churn time series + trajectory | EXISTS |
| `CoChangeMatrix` | Sparse co-change pairs with lift/confidence | EXISTS |
| `TemporalModel` | Full temporal analysis result (wraps all below) | v2 NEW |
| `FileHistory` | Per-file temporal profile (authors, churn, intent) | v2 NEW |
| `CommitRef` | Enriched commit with message for intent classification | v2 NEW (extends existing `Commit`) |
| `PairDynamics` | Co-change pair with structural edge flag | v2 NEW |
| `ModuleDynamics` | Module-level temporal aggregates | v2 NEW |
| `CodebaseDynamics` | Codebase-level temporal aggregates | v2 NEW |
| `Trajectory` | Enum: DORMANT, STABILIZING, STABLE, CHURNING, SPIKING | v2 NEW (replaces string literals) |
| `build_churn_series()` | Builds churn time series from git history | EXISTS |
| `build_cochange_matrix()` | Builds co-change matrix from git history | EXISTS |

## Requires

Nothing. This is a pipeline root alongside scanning/.

| Input | Source | How obtained |
|-------|--------|-------------|
| Git log | Git subprocess | `git log --format=... --name-only` |
| Analyzed file set | Caller passes in | Used to filter co-change pairs to current codebase |

The module does NOT depend on scanning/, semantics/, graph/, or any other analysis module. It reads git history directly and produces its own models.

## Feeds Into

| Consumer | What it receives | Purpose |
|----------|-----------------|---------|
| graph/ (IR3) | `CoChangeMatrix` / `PairDynamics` | Co-change enrichment of structural edges; hidden coupling detection |
| signals/ (IR5s) | `FileHistory` signals (27-34), `ModuleDynamics` signals (45-48) | Per-file and per-module temporal signals for fusion |
| insights/ (IR6) | `TemporalModel` | Temporal evidence in findings (unstable file, chronic problem, etc.) |

## Computed Signals

All signal definitions live in `registry/signals.md`. This module computes but does not define:

### Per-File (Scale S4)

| # | Signal | Dimension | Status |
|---|--------|-----------|--------|
| 27 | `total_changes` | D6 CHANGE | EXISTS (in `ChurnSeries.total_changes`) |
| 28 | `churn_trajectory` | D6 CHANGE | EXISTS (in `ChurnSeries.trajectory`, currently string) |
| 29 | `churn_slope` | D6 CHANGE | EXISTS (in `ChurnSeries.slope`) |
| 30 | `churn_cv` | D6 CHANGE | EXISTS (computed internally, not yet surfaced as field) |
| 31 | `bus_factor` | D7 AUTHORSHIP | PARTIAL (computed in insights layer, moving here in v2) |
| 32 | `author_entropy` | D7 AUTHORSHIP | PARTIAL (computed in insights layer, moving here in v2) |
| 33 | `fix_ratio` | D8 INTENT | v2 NEW |
| 34 | `refactor_ratio` | D8 INTENT | v2 NEW |

### Per-Module (Scale S5)

| # | Signal | Dimension | Status |
|---|--------|-----------|--------|
| 45 | `velocity` | D6 CHANGE | v2 NEW |
| 46 | `coordination_cost` | D7 AUTHORSHIP | v2 NEW |
| 47 | `knowledge_gini` | D7 AUTHORSHIP | v2 NEW |
| 48 | `module_bus_factor` | D7 AUTHORSHIP | v2 NEW |

## Temporal Contract

This module IS temporal data (Kind 1 per `registry/temporal-operators.md`). It is not parameterized by snapshot time -- it reads the full git history each run and produces a complete temporal model.

- **Output at time t**: Not applicable. The output spans the entire git history, not a single time point.
- **Delta**: Not applicable in the Kind 2 sense. The module itself produces deltas (churn slope is a velocity, trajectory is a classification of a time series).
- **Time series**: Produced, not consumed. `ChurnSeries.window_counts` IS a time series. `CodebaseDynamics.commit_frequency` IS a time series.
- **Reconstruction**: Not needed. Re-running `git log` at any commit yields the same result for that commit's past. The git log is the source of truth.

## Current State vs v2 Changes

### What exists today

The temporal/ package has four files:

| File | Contents |
|------|----------|
| `git_extractor.py` | `GitExtractor` class: subprocess git log parsing, header regex, commit list construction |
| `models.py` | `Commit`, `GitHistory`, `CoChangePair`, `CoChangeMatrix`, `ChurnSeries`, `SpectralSummary` |
| `churn.py` | `build_churn_series()`: 4-week window partitioning, linear regression slope, trajectory classification |
| `cochange.py` | `build_cochange_matrix()`: lift/confidence computation, bulk commit filtering, minimum threshold |

Current capabilities:
- Git log parsing (hash, timestamp, author, files)
- Churn trajectory classification (dormant/stabilizing/spiking/churning) -- note: current code has a bug where the fallback returns "stabilizing" instead of "stable"
- Co-change lift and confidence
- Bulk commit filtering (>50 files excluded)

### What v2 adds

1. **Commit message parsing** -- the current `git log --format` does not include `%s` (subject). v2 adds the commit message for intent classification.
2. **Intent classification** -- keyword matching + diff shape analysis on commit messages to compute `fix_ratio` and `refactor_ratio`.
3. **Author analysis per file** -- author entropy and bus factor are currently computed in the insights layer. v2 moves them here where they belong (D7 signals come from temporal data).
4. **`FileHistory` model** -- unified per-file temporal profile combining churn, authorship, and intent.
5. **`PairDynamics` model** -- extends `CoChangePair` with structural edge flag and temporal coupling score.
6. **`ModuleDynamics` model** -- module-level aggregates (velocity, coordination cost, knowledge Gini, module bus factor).
7. **`CodebaseDynamics` model** -- codebase-level aggregates (commit frequency series, active contributors, growth rate, entropy rate).
8. **`TemporalModel` model** -- top-level container replacing the current pattern of returning `GitHistory` + `CoChangeMatrix` + `Dict[str, ChurnSeries]` separately.
9. **`Trajectory` enum** -- replaces string literals with a proper enum, adds STABLE (currently missing from classification).
10. **`churn_cv` as explicit field** -- coefficient of variation is computed internally today but not surfaced.
11. **Conway's Law correlation** -- author overlap (Jaccard) between modules vs structural coupling, computed in `ModuleDynamics`.

### What does NOT change

- Git log subprocess approach (no libgit2 dependency)
- Co-change lift/confidence formulas
- 4-week default window for churn
- Bulk commit filtering threshold (50 files)
- `GitExtractor` interface (max_commits parameter, extract() -> Optional)

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Not a git repo | `GitExtractor.extract()` returns `None`. Callers get empty temporal model. |
| Shallow clone | Use available history. Churn trajectories may be less accurate but still computed. `span_days` reflects actual available range. |
| No commits | Return empty model (no files, no pairs, no dynamics). |
| git binary not found | Return `None` (caught via `FileNotFoundError`). |
| git log timeout | Return `None` (30s timeout on subprocess). |
| Empty commit (merge, no files) | Skipped during parsing (current behavior: requires `current_files` non-empty). |

## File Layout

```
temporal/
  __init__.py          # Public API re-exports
  models.py            # All data models (Commit, GitHistory, FileHistory, etc.)
  git_extractor.py     # Git log parsing via subprocess
  churn.py             # Churn series + trajectory classification
  cochange.py          # Co-change matrix construction
  authorship.py        # v2 NEW: author entropy, bus factor, knowledge Gini
  intent.py            # v2 NEW: commit message classification, fix/refactor ratio
```

## Performance

- Target: 400ms for 5000 commits (the default `max_commits` limit)
- Git log subprocess: ~200ms typical
- Parsing + churn + co-change: ~200ms typical
- Co-change is O(C x F^2) where C = commits and F = files per commit, mitigated by the 50-file bulk filter
- No external dependencies (pure Python + subprocess)
