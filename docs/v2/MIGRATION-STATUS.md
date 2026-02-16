# V2 Migration Status

## Progress Summary

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ DONE | Bridge AnalysisStore to FactStore |
| **Phase 2** | ✅ DONE | Migrate Analyzers to write to FactStore |
| **Phase 3** | ⏳ NEXT | Convert Finders to Pattern Model |
| **Phase 4** | 🔒 Blocked | Update InsightKernel for v2 |
| **Phase 5** | 🔒 Blocked | Update CLI for v2 |
| **Phase 6** | 🔒 Blocked | Update Server/Frontend |
| **Phase 7** | 🔒 Blocked | Cleanup old code |

## What Was Done

### Phase 1: Bridge Store
- `insights/store_v2.py` now has `fact_store` property exposing `FactStore`
- `_sync_entities()` method syncs FileMetrics to FILE entities
- Basic signals (LINES, FUNCTION_COUNT, CLASS_COUNT, IMPORT_COUNT) auto-populated

### Phase 2: Migrate Analyzers
Modified these analyzers to write to FactStore:

1. **StructuralAnalyzer** (`insights/analyzers/structural.py`):
   - Writes: PAGERANK, BETWEENNESS, IN_DEGREE, OUT_DEGREE, BLAST_RADIUS_SIZE, COMMUNITY, DEPTH, IS_ORPHAN, PHANTOM_IMPORT_COUNT, COMPRESSION_RATIO, COGNITIVE_LOAD
   - Writes: MODULARITY, CYCLE_COUNT, CENTRALITY_GINI (global)
   - Writes: IMPORTS relations

2. **TemporalAnalyzer** (`insights/analyzers/temporal.py`):
   - Writes: TOTAL_CHANGES, CHURN_CV, BUS_FACTOR, AUTHOR_ENTROPY, FIX_RATIO, REFACTOR_RATIO, CHURN_TRAJECTORY, CHURN_SLOPE
   - Writes: COCHANGES_WITH relations

3. **SpectralAnalyzer** (`insights/analyzers/spectral.py`):
   - Writes: FIEDLER_VALUE, SPECTRAL_GAP (global)

### Test Results
- 1186 tests pass (was 1178)
- 8 new tests added for FactStore sync
- All v2 architecture tests (45) pass

## What's Next: Phase 3

Convert 26 finder classes to declarative Pattern model:

1. Create `insights/finders/registry.py` with Pattern definitions
2. Create pattern executor that runs against FactStore
3. Convert each finder (HIGH_RISK_HUB, GOD_FILE, etc.) to Pattern dataclass
4. Delete old finder class files

## Files Created (v2 Infrastructure)

```
src/shannon_insight/infrastructure/
├── __init__.py
├── entities.py      # EntityType, EntityId, Entity
├── signals.py       # Signal enum (62), SignalSpec, SIGNAL_REGISTRY, SignalStore
├── relations.py     # RelationType (8), Relation, RelationGraph
├── store.py         # FactStore
├── runtime.py       # Tier, RuntimeContext
├── patterns.py      # PatternScope, Pattern, Finding
├── math.py          # compute_gini, compute_entropy, etc.
├── pipeline.py      # run_pipeline (minimal)
├── thresholds.py
└── validation.py
```

## How to Continue

In a new session, say:

```
Continue v2 migration from Phase 3. Read docs/v2/MIGRATION-STATUS.md and docs/v2/MIGRATION-PLAN.md for context. Start by converting finders to the Pattern model.
```

## Key Architecture Docs

- `docs/v2/architecture/` - Complete v2 architecture spec
- `docs/v2/MIGRATION-PLAN.md` - Full migration plan
- `tests/test_v2_architecture.py` - 45 acceptance tests for v2
