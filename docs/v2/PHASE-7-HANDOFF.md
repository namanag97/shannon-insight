# Phase 7 Handoff: Persistence V2

> **For the next agent**: This document summarizes Phase 6 completion and provides context for Phase 7 implementation.

---

## Phase 6 Completed ✅

**Commit**: `abb6f5e` on `feature/v2-phase-6`

### What Was Built
- 14 new finders (20 total)
- `confidence`, `effort`, `scope` fields added to Finding model
- `compute_confidence()` margin-based helper
- `compute_hotspot_median()` helper
- 28 new tests (727 total pass)

### Key Files to Know
```
src/shannon_insight/insights/
├── finders/staar
│   ├── __init__.py          # get_default_finders() returns 20 finders
│   ├── orphan_code.py       # Batch 1: Structural
│   ├── hollow_code.py
│   ├── phantom_imports.py
│   ├── copy_paste_clone.py
│   ├── flat_architecture.py
│   ├── naming_drift.py
│   ├── layer_violation.py   # Batch 2: Architecture
│   ├── zone_of_pain.py      # Guards instability=None
│   ├── knowledge_silo.py    # Batch 3: Cross-dimensional
│   ├── conway_violation.py
│   ├── review_blindspot.py
│   ├── weak_link.py         # Uses raw_risk, NOT percentiles
│   ├── bug_attractor.py
│   └── accidental_coupling.py
├── helpers.py               # compute_hotspot_median()
├── models.py                # Finding with confidence/effort/scope
├── store_v2.py              # Slot[T] pattern for typed blackboard
└── protocols_v2.py          # Analyzer/Finder protocols
```

---

## Phase 7: Persistence V2

### Goal
Upgrade persistence to store full `SignalField`, enable cross-snapshot comparison, and track finding lifecycle. This unlocks:
- Trend detection on all signals
- CHRONIC_PROBLEM finder (persists 3+ snapshots)
- ARCHITECTURE_EROSION finder (violation_rate increasing)

### Spec Location
`docs/v2/phases/phase-7-persistence-v2.md`

### Files to Modify
1. `persistence/models.py` — Extend `Snapshot` → `TensorSnapshot`
2. `persistence/capture.py` — Serialize `SignalField` into snapshot
3. `persistence/database.py` — New tables: `signal_history`, `module_signal_history`, `global_signal_history`, `finding_lifecycle`
4. `persistence/diff_engine.py` — Add `SignalDelta`, `FindingDelta`, `SnapshotDiff`
5. `persistence/queries.py` — Add `get_signal_time_series()`, `get_finding_history()`, `get_chronic_findings()`

### New Finders to Add
After persistence infrastructure:
1. `finders/chronic_problem.py` — Wraps any finding persisting 3+ snapshots
2. `finders/architecture_erosion.py` — violation_rate increasing over 3+ snapshots

### Key Implementation Notes

**TensorSnapshot schema** (from spec):
```python
@dataclass
class TensorSnapshot:
    schema_version: int = 2
    file_signals: Dict[str, Dict[str, Any]]     # Per-file signals
    module_signals: Dict[str, Dict[str, Any]]   # Per-module signals
    global_signals: Dict[str, Any]              # Global signals
    findings: List[FindingRecord]               # With identity_key
    modules: List[str]                          # Architecture
    layers: List[Dict]
    violations: List[Dict]
```

**Identity key for findings**:
```python
identity_key = SHA256(finding_type + sorted(files))
```
- Use rename detection to map to canonical path before hashing

**Finding lifecycle states**:
- `new` — First time seen
- `persisting` — In both old and new snapshot
- `resolved` — Was in old, not in new
- `regression` — Was resolved, now back

**Database migration**:
- Check `schema_version` of existing DB
- If v1, backfill new tables from existing JSON
- Bump schema version

### Acceptance Criteria (from spec)
1. TensorSnapshot serializes all SignalField data
2. V1 snapshots load and convert to TensorSnapshot
3. signal_history populated on --save
4. get_signal_time_series returns correct values
5. Finding lifecycle detects: new, persisting, resolved, regression
6. debt_velocity = |new| - |resolved|
7. CHRONIC_PROBLEM fires for 3+ snapshot persistence
8. ARCHITECTURE_EROSION fires on increasing violation_rate
9. `shannon-insight diff` shows signal deltas
10. `shannon-insight health` shows trends
11. DB migration v1→v2 works
12. All existing tests pass

---

## Quick Start Commands

```bash
# Verify Phase 6 complete
source .venv/bin/activate
python -c "from shannon_insight.insights.finders import get_default_finders; print(len(get_default_finders()))"
# Should print: 20

# Run tests
make test

# Read Phase 7 spec
cat docs/v2/phases/phase-7-persistence-v2.md

# Read existing persistence code
ls src/shannon_insight/persistence/
```

---

## What NOT to Change

- Don't modify the 14 new finders from Phase 6
- Don't change SignalField/FileSignals/ModuleSignals models
- Don't change the finder protocols

---

## Branch Strategy

```bash
git checkout -b feature/v2-phase-7
# Work on Phase 7
# Commit with prefix: [Phase 7]
```

---

## Estimated Effort
- ~800 lines new code
- ~2 weeks
- Focus: persistence layer, not finders (except 2 new ones at end)
