# signals/models.md -- Data Models

## Overview

The data models in this module represent the fused signal output at three scales: per-file, per-module, and global. Each field corresponds to a numbered signal defined in `registry/signals.md`. This document describes the **structure** -- field names, types, optionality, and grouping. For formulas and thresholds, see `registry/signals.md` and `registry/composites.md`.

## SignalField

The top-level container. A complete snapshot of all signals at a point in time.

```
SignalField:
  per_file:    {path: FileSignals}
  per_module:  {module: ModuleSignals}
  global_sigs: GlobalSignals
  timestamp:   datetime           # when this field was computed
  file_count:  int                # total files analyzed
  tier:        Tier               # ABSOLUTE | BAYESIAN | FULL (from normalization)
```

`Tier` determines which normalization strategy was used:

| Tier | File count | Composites available |
|------|-----------|---------------------|
| `ABSOLUTE` | < 15 | No. Raw signal values + absolute thresholds only. |
| `BAYESIAN` | 15-50 | Yes, with Bayesian-regularized percentiles. |
| `FULL` | 50+ | Yes, standard percentile normalization. |

## FileSignals

Approximately 36 fields per file, grouped by upstream source. Fields that depend on optional modules (semantics, temporal) are `Optional` -- they are `None` when the upstream did not run.

```
FileSignals:
  path: str                              # file path (key)

  # --- From scanning/ (IR1) --- always present ---
  lines:                int              # signal 1
  function_count:       int              # signal 2
  class_count:          int              # signal 3
  max_nesting:          int              # signal 4
  impl_gini:            float            # signal 5
  stub_ratio:           float            # signal 6
  import_count:         int              # signal 7

  # --- From semantics/ (IR2) --- optional (NEW module) ---
  role:                 Optional[Role]   # signal 8
  concept_count:        Optional[int]    # signal 9
  concept_entropy:      Optional[float]  # signal 10
  naming_drift:         Optional[float]  # signal 11
  todo_density:         Optional[float]  # signal 12
  docstring_coverage:   Optional[float]  # signal 13

  # --- From graph/ (IR3) --- always present if graph built ---
  pagerank:             float            # signal 14
  betweenness:          float            # signal 15
  in_degree:            int              # signal 16
  out_degree:           int              # signal 17
  blast_radius_size:    int              # signal 18
  depth:                int              # signal 19 (-1 = unreachable)
  is_orphan:            bool             # signal 20
  phantom_import_count: int              # signal 21
  broken_call_count:    int              # signal 22
  community:            int              # signal 23
  compression_ratio:    float            # signal 24
  semantic_coherence:   Optional[float]  # signal 25 (requires IR2 concept vectors)
  cognitive_load:       float            # signal 26

  # --- From temporal/ (IR5t) --- optional (requires git) ---
  total_changes:        Optional[int]    # signal 27
  churn_trajectory:     Optional[str]    # signal 28 (Trajectory enum as string)
  churn_slope:          Optional[float]  # signal 29
  churn_cv:             Optional[float]  # signal 30
  bus_factor:           Optional[float]  # signal 31
  author_entropy:       Optional[float]  # signal 32
  fix_ratio:            Optional[float]  # signal 33
  refactor_ratio:       Optional[float]  # signal 34

  # --- Composites (computed by this module) ---
  risk_score:           Optional[float]  # signal 35 (None if tier = ABSOLUTE)
  wiring_quality:       Optional[float]  # signal 36

  # --- Percentile ranks (computed by this module) ---
  percentiles:          Optional[Dict[str, float]]  # {signal_name: pctl_value}
```

### Field count

- IR1 signals: 7 (always present)
- IR2 signals: 6 (optional)
- IR3 signals: 13 (present when graph built)
- IR5t signals: 8 (optional)
- Composites: 2 (conditional on tier)
- Percentiles dict: 1

Total: ~37 fields per file.

## ModuleSignals

Approximately 16 fields per module. Modules are directory-level aggregations. Fields from architecture/ (IR4) are optional since architecture/ is a new module.

```
ModuleSignals:
  path: str                                    # module directory path (key)

  # --- From architecture/ (IR4) --- optional (NEW module) ---
  cohesion:                  Optional[float]   # signal 37
  coupling:                  Optional[float]   # signal 38
  instability:               Optional[float]   # signal 39
  abstractness:              Optional[float]   # signal 40
  main_seq_distance:         Optional[float]   # signal 41
  boundary_alignment:        Optional[float]   # signal 42
  layer_violation_count:     Optional[int]     # signal 43
  role_consistency:          Optional[float]   # signal 44

  # --- From temporal/ (IR5t) --- optional ---
  velocity:                  Optional[float]   # signal 45
  coordination_cost:         Optional[float]   # signal 46
  knowledge_gini:            Optional[float]   # signal 47
  module_bus_factor:         Optional[float]   # signal 48

  # --- Aggregated from per-file signals (computed by this module) ---
  mean_cognitive_load:       float             # signal 49
  file_count:                int               # signal 50

  # --- Composite (computed by this module) ---
  health_score:              Optional[float]   # signal 51
```

## GlobalSignals

Approximately 14 fields. Codebase-wide measurements.

```
GlobalSignals:
  # --- From graph/ (IR3) --- topology ---
  modularity:                float             # signal 52
  fiedler_value:             Optional[float]   # signal 53 (None if graph empty)
  spectral_gap:              Optional[float]   # signal 54
  cycle_count:               int               # signal 55
  centrality_gini:           float             # signal 56
  orphan_ratio:              float             # signal 57
  phantom_ratio:             float             # signal 58
  glue_deficit:              float             # signal 59

  # --- Composites (computed by this module) ---
  wiring_score:              float             # signal 60
  architecture_health:       Optional[float]   # signal 61 (requires IR4)
  team_risk:                 Optional[float]   # (requires temporal/)
  codebase_health:           Optional[float]   # signal 62

  # --- Supporting global values ---
  total_files:               int
  total_edges:               int
  total_modules:             int
```

## Backward Compatibility

The v1 `Primitives` dataclass (5 fields: structural_entropy, network_centrality, churn_volatility, semantic_coherence, cognitive_load) maps to v2 `FileSignals` as follows:

| v1 `Primitives` field | v2 `FileSignals` field |
|----------------------|----------------------|
| `structural_entropy` | `compression_ratio` |
| `network_centrality` | `pagerank` |
| `churn_volatility` | `churn_cv` (or computed from `total_changes` + `churn_slope`) |
| `semantic_coherence` | `semantic_coherence` |
| `cognitive_load` | `cognitive_load` |

The `Primitives` type alias and `PrimitiveValues` dict remain available for backward compatibility. Internally, `PrimitiveExtractor` populates a subset of `FileSignals` fields -- the plugin-computed ones. The remaining fields come from `SignalFusion` collecting upstream data.

## Optionality Rules

A field is `Optional` (may be `None`) when:

1. It comes from a module that may not have run (semantics/, architecture/, temporal/).
2. It requires a minimum data threshold that was not met (e.g., concept_entropy requires 20+ unique identifiers).
3. It is a composite that requires tier >= BAYESIAN (risk_score requires percentiles).

Composites handle missing inputs by using only available signals and renormalizing weights. See `composites.md` for the fallback strategy.
