# Pipeline Overview

The analysis pipeline has 7 stages, executed in strict order.

```
INITIALIZE → COLLECT → MODEL → DERIVE → DETECT → RANK → OUTPUT
```

---

## Stage Summary

| # | Stage | Input | Output | Duration |
|---|-------|-------|--------|----------|
| 1 | [Initialize](01-initialize.md) | CLI args, env | RuntimeContext, Config | ~10ms |
| 2 | [Collect](02-collect.md) | Files, git | Raw measurements, relations | ~80% |
| 3 | [Model](03-model.md) | Measurements | FactStore | ~5% |
| 4 | [Derive](04-derive.md) | FactStore | Derived signals | ~10% |
| 5 | [Detect](05-detect.md) | FactStore | Finding[] | ~3% |
| 6 | [Rank](06-rank.md) | Finding[] | Sorted Finding[] | ~1% |
| 7 | [Output](07-output.md) | Findings, Store | Terminal/JSON/HTML | ~1% |

---

## Data Objects Through Pipeline

```
Stage 1: Initialize
  └── RuntimeContext
        ├── root: Path
        ├── is_git_repo: bool
        ├── languages: list[str]
        ├── tier: ABSOLUTE | BAYESIAN | FULL
        └── config: Config

Stage 2: Collect
  ├── FileMetrics[]           (from CodeCollector)
  ├── FileSyntax[]            (from CodeCollector, Phase 1+)
  ├── GitHistory              (from GitCollector)
  ├── ChurnSeries[]           (from GitCollector)
  ├── IMPORTS relations       (from DependencyCollector)
  ├── COCHANGES_WITH relations (from CoChangeCollector)
  ├── AUTHORED_BY relations   (from GitCollector)
  └── FileSemantics[]         (from SemanticCollector, Phase 2+)

Stage 3: Model
  └── FactStore
        ├── entities: Dict[EntityId, Entity]
        ├── signals: SignalStore
        └── relations: RelationGraph

Stage 4: Derive
  └── FactStore (enriched)
        └── signals now include: pagerank, is_orphan, risk_score, etc.

Stage 5: Detect
  └── Finding[]
        ├── pattern: str
        ├── target: EntityId
        ├── severity: float
        ├── confidence: float
        └── evidence: dict

Stage 6: Rank
  └── Finding[] (sorted by score descending)

Stage 7: Output
  ├── AnalysisResult (returned to caller)
  └── TensorSnapshot (persisted if --save)
```

---

## Parallelism

Two independent spines merge at the Model stage:

```
STRUCTURAL SPINE              TEMPORAL SPINE
     │                              │
CodeCollector                 GitCollector
     │                              │
DependencyCollector           CoChangeCollector
     │                              │
SemanticCollector                   │
     │                              │
     └──────────┬───────────────────┘
                │
                ▼
            FactStore
                │
                ▼
            Derivers
                │
                ▼
            Patterns
```

**Implementation**: Run structural and temporal collectors in parallel threads. Merge results into FactStore.

---

## Error Handling

Each stage handles failures gracefully:

| Stage | Failure | Behavior |
|-------|---------|----------|
| Initialize | Invalid path | Exit with error |
| Initialize | No config | Use defaults |
| Collect | Parse error in file | Skip file, log warning |
| Collect | No git repo | Skip temporal collectors |
| Collect | Git timeout | Skip temporal, proceed with structural |
| Model | Entity conflict | Last write wins (log warning) |
| Derive | Missing dependency | Skip deriver (topo-sort handles) |
| Detect | Missing required signal | Skip pattern (graceful) |
| Rank | Empty findings | Return empty list |
| Output | Write failure | Raise to caller |

---

## Timeout Handling

```python
# Default timeouts (configurable)
STAGE_TIMEOUTS = {
    "collect_code": 120,      # 2 min per 10k files
    "collect_git": 60,        # 1 min
    "derive": 60,             # 1 min
    "detect": 30,             # 30 sec
}

# Individual collector/deriver timeout
ANALYZER_TIMEOUT = 300        # 5 min max per analyzer
```

---

## Detailed Stage Documentation

1. **[Initialize](01-initialize.md)** — Runtime context, config resolution, tier determination
2. **[Collect](02-collect.md)** — 5 collectors, what they produce
3. **[Model](03-model.md)** — FactStore construction
4. **[Derive](04-derive.md)** — Signal derivation, topo-sort, phases
5. **[Detect](05-detect.md)** — Pattern matching, hotspot filter, tier behavior
6. **[Rank](06-rank.md)** — Scoring formula, prioritization
7. **[Output](07-output.md)** — Formats, persistence, snapshots
