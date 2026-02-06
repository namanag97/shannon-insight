# Phase 5: Signal Fusion and Store Migration

## Goal

Unify all per-file, per-module, and global signals into a single `SignalField` data structure. Add percentile normalization, composite score computation, and the health Laplacian. Migrate the `AnalysisStore` from scattered typed slots to a unified signal layer that finders read from.

This is the "glue phase" — it doesn't compute new raw signals, but it transforms raw signals into normalized, comparable, composite forms.

## Packages Touched

- `signals/models.py` — **rewrite**: replace `Primitives` with `FileSignals`, `ModuleSignals`, `GlobalSignals`, `SignalField`
- `signals/fusion.py` — **new file**: `SignalFusion` class that builds SignalField from store
- `signals/normalization.py` — **new file**: tiered percentile normalization
- `signals/composites.py` — **new file**: composite score computation
- `signals/health_laplacian.py` — **new file**: health Laplacian computation
- `signals/extractor.py` — adapt to write into new model
- `signals/registry.py` — adapt to new model
- `insights/store.py` — add `signal_field` slot
- `insights/kernel.py` — register `SignalFusionAnalyzer` after all other analyzers
- `insights/ranking.py` — use signal_field percentiles instead of ad-hoc computation

## Prerequisites

- Phase 4 complete (architecture signals available for module-level composites)
- Phase 3 complete (graph enrichment signals)

## The Core Problem This Solves

Currently, signals are scattered:
- `store.structural.files["x.py"].pagerank` — graph signals
- `store.file_signals["x.py"]["cognitive_load"]` — primitive signals
- `store.churn["x.py"].trajectory` — temporal signals
- `store.structural.graph_analysis.modularity_score` — global signals

Finders have to know WHERE each signal lives. This is fragile and gets worse as signals multiply.

After this phase: `store.signal_field.file("x.py").pagerank` — one place.

## Changes

### New: `signals/models.py` (rewrite)

```python
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class FileSignals:
    """All per-file signals from registry/signals.md #1-36."""
    path: str

    # IR1 (scanning)
    lines: int = 0
    function_count: int = 0
    class_count: int = 0
    max_nesting: int = 0
    impl_gini: float = 0.0
    stub_ratio: float = 0.0
    import_count: int = 0

    # IR2 (semantics)
    role: str = "UNKNOWN"
    concept_count: int = 1
    concept_entropy: float = 0.0
    naming_drift: float = 0.0
    todo_density: float = 0.0
    docstring_coverage: float = 0.0

    # IR3 (graph)
    pagerank: float = 0.0
    betweenness: float = 0.0
    in_degree: int = 0
    out_degree: int = 0
    blast_radius_size: int = 0
    depth: int = -1
    is_orphan: bool = False
    phantom_import_count: int = 0
    broken_call_count: int = 0       # 0 until CALL edges exist
    community: int = -1
    compression_ratio: float = 0.0
    semantic_coherence: float = 0.0
    cognitive_load: float = 0.0

    # IR5t (temporal)
    total_changes: int = 0
    churn_trajectory: str = "DORMANT"
    churn_slope: float = 0.0
    churn_cv: float = 0.0
    bus_factor: float = 1.0
    author_entropy: float = 0.0
    fix_ratio: float = 0.0
    refactor_ratio: float = 0.0

    # Pre-percentile risk (used by health Laplacian BEFORE percentile normalization)
    raw_risk: float = 0.0          # weighted sum of raw signal values, NOT percentile-based

    # Composites (computed by this phase, AFTER percentile normalization)
    risk_score: float = 0.0        # percentile-based composite (different from raw_risk)
    wiring_quality: float = 1.0

    # Percentiles (filled by normalization)
    percentiles: Dict[str, float] = field(default_factory=dict)


@dataclass
class ModuleSignals:
    """All per-module signals from registry/signals.md #37-51."""
    path: str
    cohesion: float = 0.0
    coupling: float = 0.0
    instability: Optional[float] = None    # None if isolated module (Ca=Ce=0). Finders MUST check `is not None`.
    abstractness: float = 0.0
    main_seq_distance: float = 0.0         # 0.0 if instability is None (cannot compute)
    boundary_alignment: float = 0.0
    layer_violation_count: int = 0
    role_consistency: float = 0.0
    velocity: float = 0.0              # commits/week touching module
    coordination_cost: float = 0.0
    knowledge_gini: float = 0.0
    module_bus_factor: float = 1.0
    mean_cognitive_load: float = 0.0
    file_count: int = 0
    health_score: float = 0.0         # composite


@dataclass
class GlobalSignals:
    """All global signals from registry/signals.md #52-62."""
    modularity: float = 0.0
    fiedler_value: float = 0.0
    spectral_gap: float = 0.0
    cycle_count: int = 0
    centrality_gini: float = 0.0
    orphan_ratio: float = 0.0
    phantom_ratio: float = 0.0
    glue_deficit: float = 0.0
    wiring_score: float = 0.0         # composite
    architecture_health: float = 0.0  # composite
    team_risk: float = 0.0            # composite
    codebase_health: float = 0.0      # composite


@dataclass
class SignalField:
    """Unified signal container. One-stop shop for all signals."""
    per_file: Dict[str, FileSignals] = field(default_factory=dict)
    per_module: Dict[str, ModuleSignals] = field(default_factory=dict)
    global_signals: GlobalSignals = field(default_factory=GlobalSignals)
    delta_h: Dict[str, float] = field(default_factory=dict)  # health Laplacian per file
    tier: str = "FULL"               # ABSOLUTE | BAYESIAN | FULL

    def file(self, path: str) -> Optional[FileSignals]:
        return self.per_file.get(path)
```

### Backward Compatibility

Keep `Primitives` as a thin wrapper:

```python
@dataclass
class Primitives:
    """Backward-compat. Maps old 5-primitive model to new signals."""
    structural_entropy: float      # → compression_ratio
    network_centrality: float      # → pagerank
    churn_volatility: float        # → churn_cv
    semantic_coherence: float      # → semantic_coherence
    cognitive_load: float          # → cognitive_load

    @classmethod
    def from_file_signals(cls, fs: FileSignals) -> "Primitives":
        return cls(
            structural_entropy=fs.compression_ratio,
            network_centrality=fs.pagerank,
            churn_volatility=fs.churn_cv,
            semantic_coherence=fs.semantic_coherence,
            cognitive_load=fs.cognitive_load,
        )
```

### Deprecation: `signals/plugins/cognitive_load.py`

`cognitive_load` is currently computed in TWO places:
1. `graph/engine.py` → writes to `FileAnalysis.cognitive_load` (has access to graph context: in/out degree, blast radius)
2. `signals/plugins/cognitive_load.py` → writes to `store.file_signals[path]["cognitive_load"]` (standalone plugin)

SignalFusion would not know which to prefer, and the formulas may diverge.

**Resolution**: Keep the `graph/engine.py` version (richer data). Mark `signals/plugins/cognitive_load.py` as **deprecated** — it should still work for backward compatibility but SignalFusion reads `cognitive_load` from `store.structural.files[path].cognitive_load`, not from `store.file_signals`. Remove the plugin in a future cleanup pass after v2 finders are fully migrated.

### New: `signals/fusion.py`

```python
class SignalFusion:
    """Collects signals from all store slots into a unified SignalField."""

    def build(self, store: AnalysisStore) -> SignalField:
        field = SignalField()

        # Determine normalization tier
        n = len(store.file_metrics)
        if n < 15:
            field.tier = "ABSOLUTE"
        elif n < 50:
            field.tier = "BAYESIAN"
        else:
            field.tier = "FULL"

        # 1. Collect per-file signals from all sources
        for fm in store.file_metrics:
            fs = FileSignals(path=fm.path)
            self._fill_from_scanning(fs, fm)
            if store.structural:
                self._fill_from_graph(fs, store.structural, fm.path)
            if store.roles:
                fs.role = store.roles.get(fm.path, "UNKNOWN")
            if store.semantics:
                self._fill_from_semantics(fs, store.semantics.get(fm.path))
            if store.churn:
                self._fill_from_temporal(fs, store.churn.get(fm.path))
            field.per_file[fm.path] = fs

        # 2. Collect per-module architecture signals (no temporal yet)
        if store.architecture:
            for mod in store.architecture.modules.values():
                ms = ModuleSignals(path=mod.path)
                self._fill_from_architecture(ms, mod)
                field.per_module[mod.path] = ms

        # 3. Collect global signals
        self._fill_global(field.global_signals, store)

        # 4. Compute raw_risk per file (pre-percentile, used by health Laplacian)
        for fs in field.per_file.values():
            fs.raw_risk = self._compute_raw_risk(fs)

        # 5. Normalize (percentiles)
        normalize(field)

        # 6. Fill module temporal signals (AFTER normalization — needs percentiles
        #    for module_bus_factor which filters by pctl(pagerank) > 0.75)
        if store.architecture:
            for mod in store.architecture.modules.values():
                ms = field.per_module.get(mod.path)
                if ms:
                    self._fill_module_temporal(ms, mod, store, field)

        # 7. Compute composites (AFTER normalization + module temporal)
        compute_composites(field)

        # 8. Compute health Laplacian (uses raw_risk, not composites)
        if store.structural:
            field.delta_h = compute_health_laplacian(field, store.structural.graph)

        return field
```

### New: `signals/normalization.py`

Three tiers as specified in `registry/composites.md`:

```python
def normalize(field: SignalField) -> None:
    """Compute percentiles for all numeric signals."""
    if field.tier == "ABSOLUTE":
        # < 15 files: no percentiles, use absolute thresholds only
        return

    # Collect all values per signal
    signal_values: Dict[str, List[float]] = collect_numeric_signal_values(field)

    if field.tier == "BAYESIAN":
        # 15-50 files: Bayesian percentiles with PROMISE dataset priors
        for signal_name, values in signal_values.items():
            priors = get_bayesian_prior(signal_name)  # (alpha, beta) from literature
            for fs in field.per_file.values():
                raw = getattr(fs, signal_name, None)
                if raw is not None and isinstance(raw, (int, float)):
                    fs.percentiles[signal_name] = bayesian_percentile(raw, values, priors)
    else:
        # 50+ files: standard percentile
        for signal_name, values in signal_values.items():
            sorted_vals = sorted(values)
            for fs in field.per_file.values():
                raw = getattr(fs, signal_name, None)
                if raw is not None and isinstance(raw, (int, float)):
                    fs.percentiles[signal_name] = standard_percentile(raw, sorted_vals)

def standard_percentile(value: float, sorted_values: List[float]) -> float:
    """pctl(x) = |{v : v <= x}| / |values|"""
    idx = bisect_right(sorted_values, value)
    return idx / len(sorted_values)
```

### Percentile Floor

Percentiles alone are misleading for clustered distributions. Apply an absolute floor:

```python
def effective_percentile(signal_name: str, raw_value: float, pctl: float) -> float:
    """Only count the percentile if the raw value exceeds a minimum threshold."""
    minimums = {
        "pagerank": 0.005,
        "blast_radius_size": 5,
        "cognitive_load": 10.0,
        "lines": 100,
    }
    if signal_name in minimums and raw_value < minimums[signal_name]:
        return 0.0  # below floor, don't count as high percentile
    return pctl
```

This prevents 450 files with pagerank=0.001 from all showing as "90th percentile."

**Bayesian priors**: For the initial release, use flat priors (alpha=1, beta=1) which reduce to standard percentile. Literature-derived priors from PROMISE dataset are a calibration task, not a blocking dependency.

### New: `signals/composites.py`

Implements all 7 composites from `registry/composites.md`:

```python
def compute_composites(field: SignalField) -> None:
    """Compute all composite scores. Requires percentiles to be filled."""

    # Per-file composites
    for fs in field.per_file.values():
        fs.risk_score = compute_risk_score(fs, field)
        fs.wiring_quality = compute_wiring_quality(fs)

    # Per-module composites
    for ms in field.per_module.values():
        ms.health_score = compute_health_score(ms, field)

    # Global composites
    g = field.global_signals
    g.wiring_score = compute_wiring_score(field)
    g.architecture_health = compute_architecture_health(field)
    g.team_risk = compute_team_risk(field)
    g.codebase_health = compute_codebase_health(field)
```

Each composite follows the exact formula from `registry/composites.md`. No deviation.

For `field.tier == "ABSOLUTE"` (< 15 files): composites are NOT computed. The CLI should show raw signals only and explain why composites are unavailable.

### New: `signals/health_laplacian.py`

The health Laplacian detects files that are much worse than their neighbors:

```python
def compute_health_laplacian(field: SignalField, graph: DependencyGraph) -> Dict[str, float]:
    """Compute Δh(f) = h(f) - mean(h(neighbors(f))).

    h(f) = raw_risk(f) (pre-percentile weighted sum, NOT the percentile-based risk_score).
    Δh > 0 means this file is worse than its neighborhood.
    Δh > 0.4 triggers WEAK_LINK finder.

    Returns dict of file -> Δh value.
    """
    delta_h = {}
    for f, fs in field.per_file.items():
        neighbors = graph.adjacency.get(f, []) + graph.reverse.get(f, [])
        neighbors = [n for n in neighbors if n in field.per_file]
        if not neighbors:
            delta_h[f] = 0.0
            continue
        neighbor_risk = [field.per_file[n].raw_risk for n in neighbors]
        delta_h[f] = fs.raw_risk - (sum(neighbor_risk) / len(neighbor_risk))
    return delta_h
```

Using raw values avoids the circularity of computing a Laplacian on percentile-uniform data.

This is not a full Laplacian eigendecomposition — it's the discrete Laplacian applied to the raw_risk scalar field. Simple, fast, interpretable.

### Module-Level Temporal Signals

Signals #45-48 are aggregated from per-file temporal data using module definitions from Phase 4:

```python
def fill_module_temporal(ms: ModuleSignals, mod: Module, store: AnalysisStore,
                         field: SignalField):
    """Aggregate temporal signals to module level.

    IMPORTANT: This runs AFTER normalization (step 6 in build()), not during
    initial collection, because module_bus_factor needs percentile(pagerank).
    """
    if not store.git_history:
        return

    # velocity: commits per week touching any file in module
    module_commits = [c for c in store.git_history.commits
                      if any(f in mod.files for f in c.files)]
    weeks = max(store.git_history.span_days / 7, 1)
    ms.velocity = len(module_commits) / weeks

    # **Time window**: velocity uses commits from the last 90 days only
    # (configurable via `temporal.velocity_window_days` in shannon-insight.toml).
    # Full-lifetime velocity is meaningless for mature projects.

    # coordination_cost: mean distinct authors per commit touching module
    if module_commits:
        # Count distinct authors across files in the commit that are in this module
        ms.coordination_cost = _compute_coordination_cost(module_commits)

    # knowledge_gini: Gini of per-author commit counts within module
    author_counts = Counter(c.author for c in module_commits)
    ms.knowledge_gini = gini(list(author_counts.values())) if len(author_counts) > 1 else 0.0

    # module_bus_factor: min(bus_factor) across high-centrality files in module
    # Uses percentiles — safe because this runs AFTER normalization
    high_centrality = [f for f in mod.files
                       if field.file(f)
                       and field.file(f).percentiles.get("pagerank", 0) > 0.75]
    if high_centrality:
        ms.module_bus_factor = min(
            field.file(f).bus_factor for f in high_centrality
        )
```

### Modified: `insights/store.py`

```python
@dataclass
class AnalysisStore:
    # ... all existing slots preserved ...

    # Phase 5 addition:
    signal_field: Optional[SignalField] = None

@property
def available(self) -> Set[str]:
    # ... existing ...
    if self.signal_field:
        avail.add("signal_field")
    return avail
```

### New: `signals/analyzer.py`

```python
class SignalFusionAnalyzer:
    """Runs in Wave 2 — AFTER all Wave 1 analyzers complete."""
    name = "signal_fusion"
    # No requires/provides — kernel runs this in Wave 2 explicitly

    def analyze(self, store: AnalysisStore) -> None:
        fusion = SignalFusion()
        store.signal_field = fusion.build(store)
```

> **Note:** The kernel runs analyzers in two waves. Wave 1: all regular analyzers (topo-sorted by requires/provides). Wave 2: SignalFusionAnalyzer only. This eliminates ordering ambiguity — fusion always sees complete data from all Wave 1 analyzers, including temporal (which may or may not have run depending on git availability).

### Migration Path for Finders

Existing finders (HIGH_RISK_HUB, etc.) currently read from `store.structural` and `store.file_signals`. After this phase, they CAN read from `store.signal_field` instead. But we do NOT force migration — finders can read from either source.

New finders (Phase 6) MUST read from `store.signal_field`.

## New Signals Available After This Phase

| # | Signal | Type | Computed by |
|---|--------|------|-------------|
| 35 | `risk_score` | composite | `signals/composites.py` |
| 36 | `wiring_quality` | composite | `signals/composites.py` |
| 45 | `velocity` | per-module | `signals/fusion.py` |
| 46 | `coordination_cost` | per-module | `signals/fusion.py` |
| 47 | `knowledge_gini` | per-module | `signals/fusion.py` |
| 48 | `module_bus_factor` | per-module | `signals/fusion.py` |
| 49 | `mean_cognitive_load` | per-module | `signals/fusion.py` |
| 51 | `health_score` | module composite | `signals/composites.py` |
| 60 | `wiring_score` | global composite | `signals/composites.py` |
| 61 | `architecture_health` | global composite | `signals/composites.py` |
| — | `team_risk` | global composite | `signals/composites.py` |
| 62 | `codebase_health` | global composite | `signals/composites.py` |
| — | `delta_h` (health Laplacian) | per-file | `signals/health_laplacian.py` |

After this phase, ALL 62 base signals from `registry/signals.md` are computed (except #22 `broken_call_count` which requires CALL edges).

## Acceptance Criteria

1. `SignalField` correctly populated for Shannon Insight's own codebase
2. `risk_score` ≈ 1.0/10 for a file with low pagerank, low blast radius, low cognitive load, high bus factor, stable churn
3. `risk_score` > 8.0/10 for a file in top 10% of multiple risk dimensions
4. `wiring_quality` = 1.0 for a well-connected, non-orphan, non-stub file
5. `health_score` correctly combines Martin metrics and role consistency
6. `codebase_health` is in [0, 1] (displayed as 1-10 scale: × 10) and moves in expected direction when a bad file is added
7. Health Laplacian: Δh > 0 for a file with high risk score surrounded by healthy files
8. Normalization tier correctly selected based on file count
9. Composites NOT computed for < 15 file codebases (show raw signals)
10. All existing tests pass — existing finders still work reading from old store slots
11. Backward-compat: `Primitives.from_file_signals()` produces same values as current pipeline

## Estimated Scope

- 5 new files (fusion.py, normalization.py, composites.py, health_laplacian.py, analyzer.py)
- 4 modified files (models.py rewrite, store.py, kernel.py, ranking.py)
- ~1000 lines of new code
- ~2 weeks
