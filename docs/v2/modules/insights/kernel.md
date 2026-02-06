# insights/kernel -- The InsightKernel

**Status**: EXISTS -- upgrading from blackboard-only to hybrid pipeline+blackboard with demand-driven evaluation

## Current Implementation (v1)

The current kernel in `src/shannon_insight/insights/kernel.py` follows a fixed four-phase pipeline:

```python
class InsightKernel:
    def run(self, max_findings=10) -> Tuple[InsightResult, Snapshot]:
        # Phase 1: Scan files
        store.file_metrics = self._scan()

        # Phase 2: Run analyzers (topologically sorted)
        for analyzer in self._resolve_order():
            if analyzer.requires.issubset(store.available):
                analyzer.analyze(store)

        # Phase 3: Run finders (skip if required signals unavailable)
        for finder in self._finders:
            if finder.requires.issubset(store.available):
                findings.extend(finder.find(store))

        # Phase 4: Rank and cap
        findings.sort(key=lambda f: f.severity, reverse=True)
        return InsightResult(findings[:max_findings], summary), snapshot
```

The `AnalysisStore` is the blackboard: a mutable dataclass with named slots (`structural`, `git_history`, `cochange`, `churn`, `file_signals`, `spectral`). Analyzers write; finders read.

Four analyzers run in topological order:
1. `StructuralAnalyzer` (requires: files, provides: structural)
2. `PerFileAnalyzer` (requires: files, provides: file_signals)
3. `TemporalAnalyzer` (requires: files, provides: temporal)
4. `SpectralAnalyzer` (requires: structural, provides: spectral)

The topological sort is a simple iterative resolution: repeatedly scan remaining analyzers, run any whose `requires` is a subset of currently `provided`, add their `provides`, repeat.

### Limitations of v1

- **Always computes everything**: all four analyzers run regardless of which finders will actually use the results. SpectralAnalyzer computes a full eigendecomposition even if no finder needs spectral data.
- **Coarse signal categories**: `store.available` tracks broad categories (`"structural"`, `"temporal"`), not individual signals. A finder requiring only `pagerank` still demands the entire `"structural"` category.
- **No execution plan visibility**: the user cannot see what was computed or why.
- **Fixed analyzer set**: adding a new IR level (IR2, IR4) requires modifying kernel internals.

## v2 Architecture: Hybrid Pipeline + Blackboard with Demand-Driven Evaluation

### Overview

The v2 kernel retains the blackboard pattern (analyzers write signals, finders read them) but adds demand-driven evaluation: instead of running all analyzers, it traces which signals each active finder needs and computes only those.

```
Active finders ──> Required signals ──> Transitive IR deps ──> Execution plan
                                                                      │
                                                                      v
                                                              Execute subgraph
                                                                      │
                                                                      v
                                                              Run finders
                                                                      │
                                                                      v
                                                              Score + rank
```

### Signal Registry

Every signal in the system (from `registry/signals.md`) is registered with:

```python
@dataclass
class SignalSpec:
    name: str                   # "pagerank", "stub_ratio", etc.
    ir_source: str              # "IR1", "IR2", "IR3", "IR4", "IR5t", "IR5s"
    compute_module: str         # "graph", "scanning", "temporal", etc.
    depends_on: List[str]       # other signals this needs to be computed first
    scope: str                  # "file", "module", "global"
```

The registry is static -- it does not change between runs. It defines the DAG of signal dependencies.

### Demand-Driven Evaluation Algorithm

```
1. COLLECT: Gather all required signals from active finders
   required_signals = union(finder.requires for finder in active_finders)

2. TRACE: Walk the signal dependency graph transitively
   For each required signal:
     Add its compute_module to needed_modules
     For each signal it depends_on:
       Recursively add to required_signals

3. SORT: Topological sort of needed modules
   Using the IR ordering: IR0 -> IR1 -> IR2 -> IR3 -> IR4
   With IR5t (temporal) running in parallel with the structural spine

4. BUILD PLAN: Create an ExecutionPlan listing which modules run
   plan = ExecutionPlan(
       modules=sorted_modules,
       signals=required_signals,
       finders=active_finders,
       skipped_modules=[m for m in all_modules if m not in needed_modules],
   )

5. EXECUTE: Run only the needed subgraph
   For each module in plan.modules:
     module.compute(store, signals=plan.signals_for(module))

6. FIND: Run active finders against populated store
   For each finder in plan.finders:
     if finder.requires.issubset(store.available):
       findings.extend(finder.find(store))

7. SCORE: Compute confidence, apply lifecycle, rank
```

### Example: --focus ai-quality

When the user runs `shannon-insight --focus ai-quality`, only the AI code quality finders activate:

```
Active finders: ORPHAN_CODE, HOLLOW_CODE, PHANTOM_IMPORTS,
                COPY_PASTE_CLONE, FLAT_ARCHITECTURE, NAMING_DRIFT

Required signals: is_orphan, role, stub_ratio, impl_gini,
                  phantom_import_count, depth, glue_deficit,
                  naming_drift, NCD clone pairs

Trace dependencies:
  is_orphan      -> IR3 (graph)   -> IR1, IR2
  role           -> IR2 (semant)  -> IR1
  stub_ratio     -> IR1 (scanning)
  naming_drift   -> IR2 (semant)  -> IR1
  NCD clone      -> IR3 (graph)   -> IR1

Execution plan:
  [x] IR0 (scanning)
  [x] IR1 (scanning)
  [x] IR2 (semantics)
  [x] IR3 (graph)
  [ ] IR4 (architecture) -- SKIPPED
  [ ] IR5t (temporal)    -- SKIPPED
  [x] IR5s (signals)     -- only fuses needed signals

Result: No git history read. No architecture analysis. No eigendecomposition.
        ~40% faster than full run.
```

### Analyzer Protocol (v2)

```python
class Analyzer(Protocol):
    name: str
    ir_level: str               # "IR1", "IR2", "IR3", "IR4", "IR5t", "IR5s"
    requires: Set[str]          # signal categories or specific signal names
    provides: Set[str]          # signals this analyzer writes to the store

    def analyze(self, store: AnalysisStore) -> None:
        """Compute signals and write them to the store."""
        ...
```

v2 analyzers remain blackboard writers. The protocol is unchanged except for the addition of `ir_level` for plan construction.

### Finder Protocol (v2)

```python
class Finder(Protocol):
    name: str
    finding_type: str           # "HIGH_RISK_HUB", etc.
    requires: Set[str]          # specific signal names needed
    scope: Scope                # FILE, FILE_PAIR, MODULE, etc.
    base_severity: float        # from registry/finders.md
    effort: Effort              # LOW | MEDIUM | HIGH

    def find(self, store: AnalysisStore) -> List[Finding]:
        """Evaluate predicate and return findings with evidence."""
        ...
```

Key change from v1: `requires` lists specific signal names (not broad categories), enabling precise demand tracing.

### Execution Phases (v2)

```
Phase 1: Build execution plan (demand-driven)
Phase 2: Run structural spine (IR0 -> IR1 -> IR2 -> IR3 -> IR4)
         Run temporal spine in parallel (IR5t)
Phase 3: Signal fusion (IR5s) -- only needed composites
Phase 4: Run finders
Phase 5: Score (confidence, severity adjustment)
Phase 6: Lifecycle (match against history, update first_seen/persistence/trend)
Phase 7: Rank and cap
Phase 8: Build suggestions (group related findings)
Phase 9: Capture snapshot
```

### Parallelism

The structural and temporal spines are independent until IR3 (where co-change data optionally enriches graph edges). The kernel launches both spines concurrently:

```python
async def _execute_plan(self, plan: ExecutionPlan, store: AnalysisStore):
    structural_task = asyncio.create_task(self._run_structural_spine(plan, store))
    temporal_task = asyncio.create_task(self._run_temporal_spine(plan, store))

    await asyncio.gather(structural_task, temporal_task)

    # IR5s runs after both spines complete
    if "IR5s" in plan.modules:
        await self._run_signal_fusion(plan, store)
```

### Configuration

The kernel accepts configuration to control execution:

```python
@dataclass
class KernelConfig:
    max_findings: int = 20
    focus: Optional[str] = None         # "ai-quality", "architecture", "social", etc.
    disabled_finders: Set[str] = field(default_factory=set)
    min_confidence: float = 0.0         # filter findings below this confidence
    include_temporal: bool = True       # can be forced off for speed
```

### Backward Compatibility

The v1 API is preserved: `InsightKernel(root_dir, language, settings).run()` still works. The demand-driven evaluation is an internal optimization -- when no `--focus` is specified, all finders are active and the full pipeline runs (matching v1 behavior).
