# persistence/ Module Specification

## Responsibility

Serialize, store, diff, and retrieve analysis results. This module is the durable memory of Shannon Insight -- it converts transient in-memory analysis into persistent records that enable cross-snapshot comparison, trend analysis, and historical queries.

## Exports

| Symbol | Role |
|--------|------|
| `SnapshotWriter` | Serialize and write a TensorSnapshot to SQLite |
| `SnapshotReader` | Load snapshots by ID, commit, or query |
| `DiffEngine` | Compute structured deltas between two TensorSnapshots |
| `TensorSnapshot` | The universal data contract (defined in `models.md`) |
| `HistoryDB` | SQLite connection/migration manager |
| `HistoryQuery` | Read-only trend, health, and persistent-finding queries |

## Requires

| Module | What it provides |
|--------|-----------------|
| `insights/` | `InsightResult`, `Finding`, `Evidence`, `Suggestion`, `CompositeScores` |
| `signals/` | `SignalField`, `FileSignals`, `ModuleSignals`, `GlobalSignals` |
| `graph/` | `CodeGraph`, `GraphMetrics` (edge data, centrality, communities) |
| `architecture/` | `Architecture`, `Module`, `Layer`, `Violation` |
| `temporal/` | `TemporalModel`, `FileHistory`, `PairDynamics`, `CodebaseDynamics` |
| `config` | `AnalysisSettings` (for config hash) |

## Feeds

| Consumer | What it reads |
|----------|--------------|
| `cli/` | Historical data for `diff`, `health`, `history`, `explain` commands |
| `web/` | All views read TensorSnapshots via the API layer |

## Current State (v1)

The persistence layer exists today with a functional but limited schema:

### What exists

- **`models.py`**: `Snapshot` dataclass with flat `file_signals: Dict[str, Dict[str, float]]`, `codebase_signals: Dict[str, float]`, `findings: List[FindingRecord]`, `dependency_edges: List[Tuple[str, str]]`.
- **`database.py`**: `HistoryDB` managing `.shannon/history.db` with schema version 1 -- tables for `snapshots`, `file_signals`, `codebase_signals`, `findings`, `dependency_edges`, `baseline`.
- **`writer.py`**: `save_snapshot()` -- single-transaction batch insert.
- **`reader.py`**: `load_snapshot()`, `load_snapshot_by_commit()`, `list_snapshots()` -- full hydration from child tables.
- **`capture.py`**: `capture_snapshot()` -- bridges `AnalysisStore` + `InsightResult` into a `Snapshot`.
- **`diff_engine.py`**: `diff_snapshots()` -- three-pass diff (findings, files, codebase signals) with rename awareness.
- **`diff_models.py`**: `MetricDelta`, `FindingDelta`, `FileDelta`, `SnapshotDiff`.
- **`identity.py`**: `compute_identity_key()` -- stable SHA-256 hash for cross-snapshot finding tracking.
- **`rename.py`**: `detect_renames()` -- uses `git diff --name-status -M`.
- **`scope.py`**: `build_scoped_report()` -- change-scoped analysis with blast radius computation.
- **`queries.py`**: `HistoryQuery` with `file_trend()`, `codebase_health()`, `persistent_findings()`, `top_movers()`.

### What changes in v2

| Aspect | v1 | v2 |
|--------|----|----|
| Data model | Flat `Snapshot` (file signals + codebase signals) | `TensorSnapshot` (per-file, per-module, graph, architecture, temporal, global, findings, composites, suggestions) |
| Signal count | ~15 per file, ~6 global | 34 per file, 15 per module, 11 global, 6 composites |
| Module signals | Not stored | Full `ModuleSignals` table |
| Graph data | Only `dependency_edges` (source, dest) | Full `CodeGraph` with edge types, weights, unresolved edges |
| Architecture | Not stored | Full `Architecture` with layers, violations, Martin metrics |
| Temporal model | Not stored (reconstructed each run) | `TemporalModel` summary persisted |
| Evidence | 4 fields (signal, value, percentile, desc) | 6 fields (+ir_source, +confidence) |
| Schema version | 1 | 2 (with migration from v1) |
| Per-IR persistence | Everything or nothing | Selective per-IR storage (see `storage-strategy.md`) |
| Storage backend | SQLite only | SQLite (local) + PostgreSQL (hosted mode) |

## Temporal Contract

persistence/ enables **Kind 2 temporal** (cross-snapshot comparison).

### Output at time t

`TensorSnapshot(t)` -- the complete serialized analysis at time point t. Stored in `.shannon/history.db` when `--save` is passed.

### Delta(t1, t2)

`SnapshotDiff` -- structured comparison between any two snapshots:

- **Finding lifecycle**: new, persisting, resolved, regression, worsened, improved
- **Signal deltas**: per-file, per-module, and global metric changes with direction classification
- **Graph delta**: edges added/removed, community migration
- **Architecture delta**: new/resolved violations, layer changes
- **Rename detection**: `git diff --name-status -M` maps old paths to new paths before comparison

### Time series

Every numeric signal becomes a time series queryable via `HistoryQuery.file_trend()`:

```
S(file, t0), S(file, t1), ..., S(file, tn)
```

Enables sparklines in CLI and web views, trend classification (IMPROVING / STABLE / WORSENING), and velocity computation.

### Reconstruction

Kind 3 temporal (historical reconstruction) is supported by:
1. Loading a `TensorSnapshot` from the database for any past snapshot ID
2. Or re-running the full pipeline at a historical commit via `git show <sha>:<path>`

## Key Design Principles

1. **TensorSnapshot is the contract** -- everything downstream (CLI, web, CI) consumes this format. The persistence layer's job is to serialize and deserialize it faithfully.
2. **Single-transaction writes** -- all inserts for one snapshot happen atomically. No partial snapshots.
3. **Forward-compatible schema** -- new signals can be added without schema migration (they are stored as key-value rows, not columns).
4. **Opt-in persistence** -- `--save` is required. Bare `shannon-insight` produces no `.shannon/` side effects.
5. **Rename-aware diffing** -- file renames do not generate spurious add+remove deltas.
