# Module: signals/ (IR5s -- Signal Fusion)

## Responsibility

Fuse all upstream IR outputs into normalized signal vectors, composite scores, the health Laplacian, and temporal tensor operations. This is the single layer that collects every measurement from every module, normalizes them onto a common scale, computes derived composites, and produces the `SignalField` that insights/ evaluates against.

In the pipeline, signals/ is the last computation step before insights/. It reads everything and writes the unified representation that finders consume.

## Current State vs v2

### Exists today

- 5 per-file quality plugins: compression (structural entropy), centrality (PageRank), volatility (churn), coherence (identifier clustering), cognitive load (Gini-enhanced)
- `PrimitivePlugin` base class with `compute()` and `interpret()` protocol
- `PrimitiveExtractor` orchestrates all plugins, produces `Dict[str, Primitives]`
- `PrimitiveDefinition` registry with direction and default weights
- `Primitives` dataclass (5 fields: structural_entropy, network_centrality, churn_volatility, semantic_coherence, cognitive_load)

### v2 scope expansion

The module transforms from a 5-plugin primitive extractor into the full IR5s fusion layer:

- **SignalField** replaces `Primitives` -- ~36 per-file fields, ~16 per-module fields, ~14 global fields (~62 base signals total)
- **Percentile normalization** with tiered analysis for small codebases (W2)
- **6 composite scores**: risk_score, wiring_quality, health_score, wiring_score, architecture_health, codebase_health
- **Health Laplacian**: scalar health field over the dependency graph, Laplacian reveals weak links and hidden strengths
- **Temporal tensor**: T in R^(n x d x t), temporal operators applied to all numeric signals, CP/Tucker decomposition for evolution archetypes
- **Signal independence analysis**: covariance checks, PCA-based dimensionality validation (W5)

The existing plugin system is preserved for per-file signal computation. The new fusion layer wraps around it, consuming plugin outputs alongside signals from scanning/, semantics/, graph/, architecture/, and temporal/.

## Exports

| Export | Type | Description |
|--------|------|-------------|
| `SignalFusion` | class | Orchestrates collection, normalization, composition, and temporal operations |
| `SignalField` | dataclass | The complete fused output: per_file, per_module, global |
| `FileSignals` | dataclass | ~36 per-file signal fields (see `models.md`) |
| `ModuleSignals` | dataclass | ~16 per-module signal fields (see `models.md`) |
| `GlobalSignals` | dataclass | ~14 global signal fields (see `models.md`) |

## Requires

| Module | What | Why |
|--------|------|-----|
| `scanning/` | `FileSyntax` (lines, function_count, max_nesting, impl_gini, stub_ratio, import_count) | IR1 signals (1-7) |
| `semantics/` | `FileSemantics` (role, concept_count, concept_entropy, naming_drift, todo_density, docstring_coverage) | IR2 signals (8-13) |
| `graph/` | `GraphMetrics` (pagerank, betweenness, in/out degree, blast_radius, depth, orphan, phantom, community, compression_ratio, semantic_coherence, cognitive_load), global topology signals | IR3 signals (14-26, 52-59) |
| `architecture/` | `Architecture` (cohesion, coupling, instability, abstractness, main_seq_distance, boundary_alignment, layer_violations, role_consistency) | IR4 module-level signals (37-44) |
| `temporal/` | `TemporalModel` (total_changes, churn_trajectory, churn_slope, churn_cv, bus_factor, author_entropy, fix_ratio, refactor_ratio, velocity, coordination_cost, knowledge_gini, module_bus_factor) | IR5t signals (27-34, 45-48) |

## Feeds Into

| Module | What | Why |
|--------|------|-----|
| `insights/` | `SignalField` | The signal field that all finders evaluate against |
| `persistence/` | `SignalField` (serialized) | Historical signal storage for cross-snapshot temporal operators |

## Signals Computed

This module does NOT compute base signals (those come from upstream modules). It computes:

### Composite scores (from `registry/composites.md`)

| # | Signal | Level | Status |
|---|--------|-------|--------|
| 35 | `risk_score` | per-file | NEW (v1 had no composites) |
| 36 | `wiring_quality` | per-file | NEW |
| 51 | `health_score` | per-module | NEW |
| 60 | `wiring_score` | global | NEW |
| 61 | `architecture_health` | global | NEW |
| 62 | `codebase_health` | global | NEW |

### Also computes (not numbered signals)

- Percentile ranks for all numeric per-file signals
- Health Laplacian: h(f), delta-h(f) for every file in the dependency graph
- Aggregated module-level statistics: mean_cognitive_load (#49), file_count (#50)
- Temporal derivatives on all signals: delta, velocity, trend (when historical data available)

## Temporal Contract

### Output at time t

`SignalField(t)` -- the complete signal field at snapshot time t. Every signal is a scalar at a given time point.

### SignalField as time series

Every signal becomes a time series when historical snapshots exist:

```
S(f, t0), S(f, t1), ..., S(f, now)
```

The temporal operators from `registry/temporal-operators.md` are applied to all numeric signals:

| Operator | Applicable to | Produces |
|----------|---------------|----------|
| delta | All numeric + bool + enum | Change since last snapshot |
| velocity | All numeric | Rate of change (OLS slope) |
| acceleration | All numeric | Is change speeding up or slowing down? |
| trend | All numeric | IMPROVING / STABLE / WORSENING (polarity-aware) |
| trajectory | All numeric | DORMANT / STABILIZING / STABLE / CHURNING / SPIKING |
| volatility | Unbounded numeric only | Coefficient of variation |
| seasonality | Unbounded numeric only | Autocorrelation at lag |
| stationarity | Unbounded numeric only | ADF test: STATIONARY / NON_STATIONARY |

These are second-order signals -- not listed separately in the registry. They are implicit for every signal with applicable type.

### Delta(t1, t2)

```
SignalFieldDelta:
  per_file_deltas:   {path: {signal_name: (old_value, new_value)}}
  per_module_deltas: {module: {signal_name: (old_value, new_value)}}
  global_deltas:     {signal_name: (old_value, new_value)}
  composite_deltas:  {signal_name: (old_value, new_value)}
  health_laplacian_delta: {path: float}
```

### Reconstruction

Re-run the full pipeline at a historical commit (Kind 3 temporal data). `SignalFusion` is a pure function of its upstream inputs -- given historical scanning + semantics + graph + architecture + temporal outputs, it produces the same `SignalField`.

## Error Handling

- **Missing upstream data**: If a module did not run (e.g., no git history = no temporal signals), the corresponding fields in `FileSignals` are `None`. Composites use only available signals and adjust weights proportionally. The `SignalField` is always produced, even if partial.
- **Small codebases**: Tiered normalization (see `normalization.md`). Below 15 files, composites are not computed -- raw signal values and absolute thresholds are used instead.
- **Zero-variance signals**: If a signal is constant across all files, its percentile is 0.5 for all files. This prevents division-by-zero in normalization and avoids false outliers.
- **NaN / infinite values**: Clamp to domain bounds before normalization. Log a warning. Never propagate NaN into composites.

## File Layout

```
signals/
  __init__.py           # re-exports SignalFusion, SignalField, FileSignals, etc.
  models.py             # SignalField, FileSignals, ModuleSignals, GlobalSignals
  fusion.py             # SignalFusion: orchestrates collection, normalization, composition
  normalization.py      # Percentile normalization, tiered analysis, Bayesian priors
  composites.py         # Composite score computation pipeline
  health_laplacian.py   # Health scalar field + Laplacian diffusion
  temporal_tensor.py    # Temporal tensor operations, CP/Tucker decomposition
  base.py               # PrimitivePlugin ABC (exists)
  extractor.py          # PrimitiveExtractor (exists, drives plugins)
  registry.py           # Plugin registry + PrimitiveDefinition (exists)
  plugins/
    __init__.py
    compression.py      # CompressionPrimitive (exists)
    centrality.py       # CentralityPrimitive (exists)
    volatility.py       # VolatilityPrimitive (exists)
    coherence.py        # CoherencePrimitive (exists)
    cognitive_load.py   # CognitiveLoadPrimitive (exists)
```
