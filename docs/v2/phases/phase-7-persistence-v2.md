# Phase 7: Persistence V2

## Goal

Upgrade the persistence layer to store the full `SignalField`, enable cross-snapshot comparison (Kind 2 temporal), and support finding lifecycle tracking. This unlocks trend detection, sparklines, and the CHRONIC_PROBLEM / ARCHITECTURE_EROSION finders.

## Packages Touched

- `persistence/models.py` — extend `Snapshot` → `TensorSnapshot`
- `persistence/capture.py` — serialize `SignalField` into snapshot
- `persistence/database.py` — new schema for signal time series
- `persistence/diff_engine.py` — upgrade to diff `SignalField` and track finding lifecycle
- `persistence/queries.py` — add time-series queries

## Prerequisites

- Phase 5 complete (SignalField is the thing we're persisting)
- Phase 6 complete (findings with confidence and scope to track)

## Changes

### Modified: `persistence/models.py`

Extend `Snapshot` to `TensorSnapshot`:

```python
@dataclass
class TensorSnapshot:
    """V2 snapshot: stores the full SignalField plus architecture and temporal summary."""

    # ── Metadata (same as v1) ─────────────────────────────────
    schema_version: int = 2
    tool_version: str = ""
    commit_sha: Optional[str] = None
    timestamp: str = ""
    analyzed_path: str = ""
    file_count: int = 0
    module_count: int = 0
    commits_analyzed: int = 0
    analyzers_ran: List[str] = field(default_factory=list)
    config_hash: str = ""

    # ── Per-file signals (replaces v1 file_signals) ───────────
    # Dict[file_path, Dict[signal_name, value]]
    # Serialized from SignalField.per_file
    file_signals: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # ── Per-module signals (NEW) ──────────────────────────────
    module_signals: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # ── Global signals (replaces v1 codebase_signals) ─────────
    global_signals: Dict[str, Any] = field(default_factory=dict)

    # ── Findings (enhanced) ───────────────────────────────────
    findings: List[FindingRecord] = field(default_factory=list)

    # ── Graph structure (same as v1) ──────────────────────────
    dependency_edges: List[Tuple[str, str]] = field(default_factory=list)

    # ── Architecture summary (NEW) ────────────────────────────
    modules: List[str] = field(default_factory=list)        # module paths
    layers: List[Dict[str, Any]] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
```

Backward compatibility: read v1 `Snapshot` (schema_version=1) and convert to `TensorSnapshot` by mapping `file_signals` and `codebase_signals` to the same field names. Missing fields get defaults.

### Modified: `persistence/capture.py`

```python
def capture_snapshot(store: AnalysisStore, result: InsightResult, settings) -> TensorSnapshot:
    """Serialize the full analysis into an immutable TensorSnapshot."""
    snap = TensorSnapshot(schema_version=2, ...)

    # Serialize SignalField
    if store.signal_field:
        for path, fs in store.signal_field.per_file.items():
            snap.file_signals[path] = _serialize_file_signals(fs)
        for path, ms in store.signal_field.per_module.items():
            snap.module_signals[path] = _serialize_module_signals(ms)
        snap.global_signals = _serialize_global_signals(store.signal_field.global_signals)

    # Serialize findings with identity keys
    for finding in result.findings:
        snap.findings.append(FindingRecord(
            finding_type=finding.finding_type,
            identity_key=_compute_identity_key(finding),
            severity=finding.severity,
            confidence=finding.confidence,
            title=finding.title,
            files=finding.files,
            evidence=[...],
            suggestion=finding.suggestion,
        ))

    # Serialize architecture
    if store.architecture:
        snap.modules = list(store.architecture.modules.keys())
        snap.layers = [{"depth": l.depth, "modules": l.modules} for l in store.architecture.layers]
        snap.violations = [{"src": v.source_module, "tgt": v.target_module, "type": v.violation_type.value}
                          for v in store.architecture.violations]

    return snap
```

### Modified: `persistence/database.py`

New SQLite tables:

```sql
-- Signals time series (one row per file per snapshot per signal)
CREATE TABLE IF NOT EXISTS signal_history (
    snapshot_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    signal_name TEXT NOT NULL,
    value REAL,
    percentile REAL,
    PRIMARY KEY (snapshot_id, file_path, signal_name),
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

-- Module signals time series
CREATE TABLE IF NOT EXISTS module_signal_history (
    snapshot_id INTEGER NOT NULL,
    module_path TEXT NOT NULL,
    signal_name TEXT NOT NULL,
    value REAL,
    PRIMARY KEY (snapshot_id, module_path, signal_name),
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

-- Global signals time series
CREATE TABLE IF NOT EXISTS global_signal_history (
    snapshot_id INTEGER NOT NULL,
    signal_name TEXT NOT NULL,
    value REAL,
    PRIMARY KEY (snapshot_id, signal_name),
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

-- Finding lifecycle
CREATE TABLE IF NOT EXISTS finding_lifecycle (
    identity_key TEXT NOT NULL,
    first_seen_snapshot INTEGER NOT NULL,
    last_seen_snapshot INTEGER NOT NULL,
    persistence_count INTEGER DEFAULT 1,
    current_status TEXT DEFAULT 'active',  -- active | resolved
    finding_type TEXT NOT NULL,
    severity REAL,
    PRIMARY KEY (identity_key)
);

-- Performance index for time-series queries
CREATE INDEX IF NOT EXISTS idx_signal_file_name
    ON signal_history(file_path, signal_name, snapshot_id);
CREATE INDEX IF NOT EXISTS idx_finding_type
    ON finding_lifecycle(finding_type, current_status);
```

**Migration**: On first v2 run, check schema_version of existing database. If v1, run migration:
1. Create new tables
2. Backfill `signal_history` from existing `snapshots.file_signals` JSON
3. Backfill `finding_lifecycle` from existing findings
4. Bump schema version

### Modified: `persistence/diff_engine.py`

Upgrade diff to compare `TensorSnapshot`:

```python
@dataclass
class SignalDelta:
    """Change in a signal between two snapshots."""
    signal_name: str
    old_value: float
    new_value: float
    delta: float
    trend: str         # "improving" | "stable" | "worsening" (based on signal polarity)

@dataclass
class FindingDelta:
    """Finding lifecycle event."""
    identity_key: str
    finding_type: str
    status: str        # "new" | "resolved" | "persisting" | "regression"
    severity: float
    persistence_count: int

@dataclass
class SnapshotDiff:
    """Structured diff between two TensorSnapshots."""
    # Existing
    files_added: List[str]
    files_removed: List[str]

    # Enhanced
    signal_deltas: Dict[str, List[SignalDelta]]   # file -> signal changes
    module_deltas: Dict[str, List[SignalDelta]]    # module -> signal changes
    global_deltas: List[SignalDelta]
    finding_deltas: List[FindingDelta]

    # Summary
    debt_velocity: int        # |new findings| - |resolved findings|
    improving_files: List[str]
    worsening_files: List[str]
```

Finding lifecycle tracking:

```
For each finding in new snapshot:
    key = identity_key (SHA-256 of finding_type + sorted(files))
    if key in old snapshot findings:
        status = "persisting"
        increment persistence_count in finding_lifecycle table
    elif key in finding_lifecycle with status="resolved":
        status = "regression"
        reactivate in finding_lifecycle
    else:
        status = "new"
        insert into finding_lifecycle

For each finding in old snapshot NOT in new:
    status = "resolved"
    update finding_lifecycle.current_status = "resolved"
```

**Rename-aware identity keys**: Before computing identity_key, check if any file in the finding was renamed (using persistence/rename detection). If so, map to the canonical (oldest) path before hashing. This prevents rename→"resolved"+new finding false lifecycle events.

### New: `persistence/queries.py` additions

```python
def get_signal_time_series(
    db: HistoryDB,
    file_path: str,
    signal_name: str,
    limit: int = 20,
) -> List[Tuple[str, float]]:
    """Return (timestamp, value) pairs for a signal over time."""

def get_finding_history(
    db: HistoryDB,
    identity_key: str,
) -> Dict:
    """Return lifecycle data for a finding."""

def get_chronic_findings(
    db: HistoryDB,
    min_persistence: int = 3,
) -> List[Dict]:
    """Return findings persisting across 3+ snapshots."""
```

### Follow-up Finders (after Phase 7)

Now that finding lifecycle is tracked, enable two deferred finders:

#### `finders/chronic_problem.py` — CHRONIC_PROBLEM (upgrade)

```
Condition: same finding persists across 3+ snapshots
Wraps: any other finding
Severity: base_severity × 1.25
Evidence: first_seen timestamp, persistence_count, trend
```

#### `finders/architecture_erosion.py` — ARCHITECTURE_EROSION

```
Condition: violation_rate increasing over 3+ snapshots
Scope: CODEBASE
Severity: 0.65
Evidence: violation_rate time series
Requires: 3+ snapshots with architecture data
```

These are small additions (~100 lines each) after the persistence infrastructure is in place.

## New Signals Available After This Phase

No new base signals. But enables:
- Kind 2 temporal: any signal becomes a time series after 2+ `--save` runs
- Trend detection on all numeric signals
- Finding persistence tracking

## Acceptance Criteria

1. `TensorSnapshot` correctly serializes all `SignalField` data
2. V1 snapshots (schema_version=1) load without error and convert to TensorSnapshot
3. `signal_history` table populated on `--save`
4. `get_signal_time_series` returns correct values for a signal across 3 snapshots
5. Finding lifecycle correctly detects: new, persisting, resolved, regression
6. `debt_velocity` = |new| - |resolved| computed correctly
7. CHRONIC_PROBLEM fires for a finding present in 3+ consecutive snapshots
8. ARCHITECTURE_EROSION fires when violation_rate increases across 3+ snapshots
9. `shannon-insight diff` shows signal deltas and finding lifecycle
10. `shannon-insight health` shows signal trends (sparklines if terminal supports)
11. Database migration from v1 → v2 schema works on existing `.shannon/history.db`
12. All existing tests pass

## What This Phase Does NOT Do

- **Kind 3 temporal** (historical reconstruction): BACKLOGGED (see `BACKLOG.md` B2).
- **CP/Tucker tensor decomposition**: BACKLOGGED (see `BACKLOG.md` B1).
- **Seasonality/stationarity operators**: BACKLOGGED (see `BACKLOG.md` B3). Signal history table provides the data foundation — operators can be added incrementally when a finder needs them.

## Estimated Scope

- 0 new packages
- 2 new finder files (chronic_problem, architecture_erosion)
- 5 modified files
- ~800 lines of new code
- ~2 weeks
