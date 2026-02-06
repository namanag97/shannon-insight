# Module: insights/

**IR Level**: IR6 (Insights)
**Status**: EXISTS -- upgrading from v1 (7 finders, blackboard) to v2 (22 finders, demand-driven)

## Responsibility

Evaluate finding predicates against a populated signal field to produce evidence-backed, actionable findings. This module is the final consumer of all upstream data -- it reads signals, applies thresholds and conditions, constructs multi-IR evidence chains, computes confidence scores, and emits prioritized results.

The insights module does NOT compute signals. It reads them from `signals/` (via the `SignalField`) and evaluates boolean predicates to determine which findings apply.

## Exports

| Symbol | Type | Description |
|---|---|---|
| `InsightKernel` | class | Orchestrates analyzers and finders; demand-driven evaluation |
| `InsightResult` | dataclass | Complete output: findings + composites + suggestions |
| `Finding` | dataclass | Single actionable finding with evidence chain |
| `Evidence` | dataclass | One item in an evidence chain, tied to an IR source |
| `Suggestion` | dataclass | Actionable recommendation with priority and effort |
| `CompositeScores` | dataclass | Summary composites (ai_quality, arch_health, team_risk, codebase_health) |

## Dependencies

| Direction | Module | What |
|---|---|---|
| **Requires** | `signals/` | `SignalField` (the fused signal data finders evaluate against) |
| **Feeds** | `persistence/` | `InsightResult` for snapshot serialization and history |
| **Feeds** | `cli/` | `InsightResult` for terminal display |
| **Feeds** | `web/` | `InsightResult` for all five web views (future) |

## Current State (v1)

- **7 finders**: HIGH_RISK_HUB, HIDDEN_COUPLING, GOD_FILE, UNSTABLE_FILE, BOUNDARY_MISMATCH, DEAD_DEPENDENCY, CHRONIC_PROBLEM
- **4 analyzers** (blackboard writers): StructuralAnalyzer, PerFileAnalyzer, TemporalAnalyzer, SpectralAnalyzer
- **Blackboard architecture**: `AnalysisStore` is a mutable dataclass; analyzers write to named slots, finders read from slots
- **Signal tracking**: `store.available` is a set of category strings (`"structural"`, `"temporal"`, `"file_signals"`, `"spectral"`)
- **Evidence model**: flat -- each `Evidence` has signal/value/percentile/description but no IR source tag
- **No confidence scoring** -- only severity
- **No finding lifecycle** -- CHRONIC_PROBLEM queries history DB directly, but findings lack `first_seen`, `trend`, or `regression` fields
- **Topological sort**: simple iterative resolution based on `requires`/`provides` sets

## v2 Additions

### 15 new finders (see `finders/` subdirectory)

| Category | Finders |
|---|---|
| AI Code Quality | ORPHAN_CODE, HOLLOW_CODE, PHANTOM_IMPORTS, COPY_PASTE_CLONE, FLAT_ARCHITECTURE, NAMING_DRIFT |
| Social / Team | KNOWLEDGE_SILO, CONWAY_VIOLATION, REVIEW_BLINDSPOT |
| Architecture | LAYER_VIOLATION, ZONE_OF_PAIN, ARCHITECTURE_EROSION |
| Cross-Dimensional | WEAK_LINK, BUG_ATTRACTOR, ACCIDENTAL_COUPLING |

### Demand-driven evaluation

Replace the "run all analyzers then run all finders" model with a demand-driven approach: the kernel collects the signals required by active finders, traces dependencies transitively through the IR chain, and builds a minimal execution plan. See `kernel.md`.

### Multi-IR evidence chains

Each `Evidence` item gains an `ir_source` field (`"IR1"`, `"IR2"`, `"IR3"`, `"IR4"`, `"IR5t"`, `"IR5s"`). Findings assemble evidence from multiple IRs, giving users a layered explanation. See `models.md`.

### Confidence scoring

Every finding gains a `confidence` field in [0, 1] computed from margin above threshold. See `scoring.md`.

### Finding lifecycle

Findings gain temporal fields: `first_seen`, `persistence_count`, `trend`, `regression`. CHRONIC_PROBLEM is generalized -- any finding can track its lifecycle via stable IDs. See `models.md`.

## Temporal Contract

### Output at time t

`InsightResult(t)` contains all findings, composites, and suggestions at analysis time t.

### Delta

`InsightDelta(t_prev, t_now)`:
- `new_findings` -- findings present at t_now but not t_prev
- `resolved_findings` -- findings present at t_prev but not t_now
- `persisting` -- findings in both, with updated `persistence_count`
- `regressions` -- findings that were resolved in some prior snapshot but reappeared
- `worsening` -- persisting findings whose severity or evidence increased
- `improving` -- persisting findings whose severity or evidence decreased

Tracking uses stable finding IDs: `finding_id = hash(type + sorted(targets))`.

### Time series

| Metric | Formula | What it reveals |
|---|---|---|
| `finding_count(t)` | total findings per snapshot | Debt accumulation curve |
| `debt_velocity(t)` | `\|new\| - \|resolved\|` | Positive = accumulating; negative = paying down |
| `mttr` | `mean(last_seen - first_seen)` for resolved findings | Mean time to resolve |
| `severity_distribution(t)` | histogram of severities | Is the tail getting heavier? |

### Reconstruction

Re-run `InsightKernel` at a historical commit by checking out the source tree and re-executing the full pipeline. Requires Kind 3 temporal data.

## Error Handling

**Missing signals lead to graceful skip, never crash.**

Each finder declares `requires: Set[str]` listing the signal categories it needs. Before running a finder, the kernel checks `finder.requires.issubset(store.available)`. If any required signal is missing -- because an upstream module failed, because git history is absent, or because the user's `--focus` flag excluded an IR level -- the finder is silently skipped.

This design means:
- A non-git repository still gets structural findings (GOD_FILE, ORPHAN_CODE, etc.)
- A `--focus ai-quality` run skips IR4 and temporal finders entirely
- An upstream parse failure in one language does not prevent findings on other files
