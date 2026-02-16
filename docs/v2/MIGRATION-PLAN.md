# V2 Migration Plan

## Current State

### V1 Architecture (Current)
```
CLI (analyze.py)
    │
    ▼
InsightKernel (insights/kernel.py)
    │
    ├── ScannerFactory → FileMetrics[]
    │
    ├── AnalysisStore (insights/store_v2.py)  ← Blackboard with Optional fields
    │
    ├── Analyzers (5):
    │   ├── StructuralAnalyzer → writes structural
    │   ├── TemporalAnalyzer → writes git_history, cochange, churn
    │   ├── SpectralAnalyzer → writes spectral
    │   ├── SemanticAnalyzer → writes semantics, roles
    │   └── ArchitectureAnalyzer → writes architecture
    │
    ├── SignalFusionAnalyzer → writes signal_field
    │
    └── Finders (26) → read store, return Finding[]
```

### V2 Infrastructure (Built, Not Integrated)
```
infrastructure/
├── entities.py      # EntityType, EntityId, Entity
├── signals.py       # Signal enum (62), SignalSpec, SIGNAL_REGISTRY, SignalStore
├── relations.py     # RelationType (8), Relation, RelationGraph
├── store.py         # FactStore (unified)
├── runtime.py       # Tier, RuntimeContext
├── patterns.py      # PatternScope, Pattern, Finding
├── math.py          # compute_gini, compute_entropy, etc.
└── pipeline.py      # run_pipeline (minimal)
```

## Migration Strategy

**Approach**: Incremental migration with backward compatibility at each step.

Each migration step must:
1. Pass all existing tests (no regressions)
2. Pass v2 architecture tests
3. Remove deprecated code after migration

---

## Phase 1: Bridge Store (insights/store_v2.py → infrastructure/store.py)

**Goal**: Make `AnalysisStore` a facade over `FactStore`.

**Changes**:
1. `AnalysisStore.__init__` creates internal `FactStore`
2. Each slot write also populates `FactStore`
3. Keep backward-compatible API
4. Delete old `insights/store.py` (unused)

**Files**:
- Modify: `insights/store_v2.py`
- Delete: `insights/store.py`

---

## Phase 2: Migrate Analyzers

**Goal**: Analyzers write to `FactStore` via `AnalysisStore` bridge.

### 2a: StructuralAnalyzer
- Write to `FactStore.signals` for: pagerank, betweenness, in_degree, out_degree, etc.
- Write to `FactStore.relations` for: IMPORTS relations

### 2b: TemporalAnalyzer
- Write to `FactStore.signals` for: total_changes, churn_cv, bus_factor, etc.
- Write to `FactStore.relations` for: COCHANGES_WITH, AUTHORED_BY

### 2c: SemanticAnalyzer
- Write to `FactStore.signals` for: concept_count, naming_drift, etc.
- Write to `FactStore.relations` for: SIMILAR_TO

### 2d: ArchitectureAnalyzer
- Write to `FactStore.signals` for: cohesion, coupling, instability, etc.
- Write to `FactStore.relations` for: IN_MODULE, CONTAINS, DEPENDS_ON

### 2e: SignalFusionAnalyzer
- Write composites to `FactStore.signals`: risk_score, health_score, etc.

**Files**:
- Modify: `insights/analyzers/structural.py`
- Modify: `insights/analyzers/temporal.py`
- Modify: `insights/analyzers/spectral.py`
- Modify: `architecture/analyzer.py`
- Modify: `semantics/analyzer.py`
- Modify: `signals/analyzer.py`

---

## Phase 3: Migrate Finders to Pattern Model

**Goal**: Finders use declarative `Pattern` definitions.

**Current**: Each finder is a class with `find()` method.
**Target**: Finders are `Pattern` dataclasses with predicates.

### 3a: Create Pattern Registry
- Create `insights/finders/registry.py`
- Define all 22 patterns declaratively

### 3b: Pattern Executor
- Create pattern executor that runs patterns against `FactStore`
- Produces `infrastructure.Finding` objects

### 3c: Migrate Each Finder
Convert each finder class to a Pattern definition:
- HIGH_RISK_HUB, HIDDEN_COUPLING, GOD_FILE, etc.

### 3d: Remove Old Finder Classes
After migration, delete the 26 finder class files.

**Files**:
- Create: `insights/finders/registry.py`
- Create: `insights/finders/executor.py`
- Delete: All individual finder files (26 files)

---

## Phase 4: Migrate InsightKernel

**Goal**: `InsightKernel` uses v2 infrastructure throughout.

**Changes**:
1. Create `RuntimeContext` at start
2. Use `FactStore` as primary store
3. Use pattern executor for findings
4. Produce `infrastructure.Finding` objects

**Files**:
- Modify: `insights/kernel.py`
- Delete: `insights/models.py` (old Finding model)

---

## Phase 5: Update CLI

**Goal**: CLI works with v2 output types.

**Changes**:
1. Handle `infrastructure.Finding` instead of old Finding
2. Use `FactStore` for signal queries
3. Update JSON output format

**Files**:
- Modify: `cli/analyze.py`
- Modify: `cli/_finding_display.py`
- Modify: `cli/_signal_display.py`

---

## Phase 6: Update Server/Frontend

**Goal**: Server returns v2 data structures.

**Changes**:
1. API returns `infrastructure.Finding` JSON
2. Frontend receives updated schema

**Files**:
- Modify: `server/api.py`
- Modify: `server/static/app.js`

---

## Phase 7: Cleanup

**Goal**: Remove all v1 remnants.

**Delete**:
- `insights/store.py` (old store)
- `insights/store_v2.py` (bridge, now unnecessary)
- Individual finder class files
- Old model definitions

**Consolidate**:
- `signals/` module → use `infrastructure/signals.py`
- `math/gini.py`, `math/entropy.py` → use `infrastructure/math.py`

---

## Execution Order

| # | Phase | Est. Files | Blocked By | Agent |
|---|-------|-----------|------------|-------|
| 1 | Bridge Store | 2 | - | Agent 1 |
| 2a | StructuralAnalyzer | 3 | 1 | Agent 2 |
| 2b | TemporalAnalyzer | 2 | 1 | Agent 3 |
| 2c | SemanticAnalyzer | 2 | 1 | Agent 4 |
| 2d | ArchitectureAnalyzer | 2 | 1 | Agent 5 |
| 2e | SignalFusionAnalyzer | 2 | 1 | Agent 6 |
| 3 | Pattern Model | 28 | 2a-2e | Agent 7 |
| 4 | InsightKernel | 2 | 3 | Agent 8 |
| 5 | CLI | 4 | 4 | Agent 9 |
| 6 | Server | 2 | 5 | Agent 10 |
| 7 | Cleanup | 30+ | 6 | Agent 11 |

---

## Testing Strategy

After each phase:
1. Run `make all` (format + check + test)
2. Run `shannon-insight . --json` on self
3. Verify output matches expected

---

## Rollback Plan

Each phase is a git commit. If issues arise:
```bash
git revert <phase-commit>
```

---

## Success Criteria

1. All 1178+ tests pass
2. CLI produces same findings as before
3. No `Optional` soup in store
4. Signal access via enum, not strings
5. Finders are declarative patterns
6. Old code deleted
