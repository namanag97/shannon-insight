# architecture/ --- Module Specification

## Status: NEW (does not exist today)

This package is entirely new in v2. It implements IR4 (ArchitecturalModel) --- the layer between the file-level dependency graph (IR3) and the signal fusion layer (IR5s).

## Responsibility

Module-level structural analysis: detecting module boundaries, inferring architectural layers, computing per-module quality metrics (Martin's I/A/D, cohesion, coupling), detecting layer violations, and classifying architectural patterns.

Transforms a file graph into a system-level architecture model.

## Exports

| Symbol | Kind | Description |
|--------|------|-------------|
| `ArchitectureAnalyzer` | class | Entry point. Takes `CodeGraph` + file roles, produces `Architecture`. |
| `Architecture` | dataclass | Top-level result: modules, layers, violations, patterns, health. |
| `Module` | dataclass | A group of files with cohesion/coupling/I/A/D metrics. |
| `Layer` | dataclass | A depth level containing one or more modules. |
| `Violation` | dataclass | A dependency edge that breaks layering (BACKWARD or SKIP). |
| `ArchPatterns` | dataclass | Boolean pattern flags (is_layered, hub_and_spoke, etc.). |
| `ArchHealth` | dataclass | Aggregate health: violation_rate, mean cohesion/coupling/D, alignment. |
| `ArchDelta` | dataclass | Structured diff between two `Architecture` snapshots. |
| `ModuleRole` | enum | Aggregated module-level role from file roles. |

## Dependencies

| Requires | What | Why |
|----------|------|-----|
| `graph/` | `CodeGraph`, `GraphMetrics` (communities, edges, nodes) | File graph is the raw input; Louvain communities for boundary alignment and fallback module detection. |
| `semantics/` | File `Role` assignments | Aggregated into `ModuleRole`; used for `role_consistency` computation. |

## Feeds Into

| Consumer | What | Why |
|----------|------|-----|
| `signals/` | Per-module signals (37--45), global signal 56 | Signal fusion layer reads module metrics for `ModuleSignals` and `architecture_health`. |
| `insights/` | `Architecture` object | Finders (BoundaryMismatch, LayerViolation, GodModule, ZoneOfPain) query architecture data. |

## Signals Computed

Per-module (scale S5) --- see `registry/signals.md` for authoritative definitions:

| # | Signal | Reference |
|---|--------|-----------|
| 37 | `cohesion` | registry/signals.md #37 |
| 38 | `coupling` | registry/signals.md #38 |
| 39 | `instability` | registry/signals.md #39 |
| 40 | `abstractness` | registry/signals.md #40 |
| 41 | `main_seq_distance` | registry/signals.md #41 |
| 42 | `boundary_alignment` | registry/signals.md #42 |
| 43 | `layer_violation_count` | registry/signals.md #43 |
| 44 | `role_consistency` | registry/signals.md #44 |
| 50 | `file_count` | registry/signals.md #50 |

Global (scale S6):

| # | Signal | Reference |
|---|--------|-----------|
| 56 | `centrality_gini` | registry/signals.md #56 |

Additionally produces (not numbered signals): layer assignments, violation list, `ArchPatterns`, `ArchHealth`, architecture entropy.

## Pipeline Position

```
graph/ (IR3: CodeGraph, communities)
  |
  v
architecture/ (IR4)  <-- semantics/ (file roles)
  |
  v
signals/ (IR5s: reads module metrics)
  |
  v
insights/ (IR6: architecture finders)
```

`architecture/` is the last step of the structural spine before signal fusion.

## Algorithm Overview

1. **Module detection** --- identify module boundaries from directory structure, with Louvain fallback for flat projects and config override. See `module-detection.md`.

2. **Module graph contraction** --- collapse file-level `CodeGraph` into module-level directed graph where each node is a module and edges aggregate cross-module file edges.

3. **Layer inference** --- topological sort of the module DAG to assign layer depths, then detect violations (back-edges and skip-edges). See `layer-inference.md`.

4. **Martin's metrics** --- compute I, A, D per module using expanded abstractness for dynamic languages. Abstractness computation detailed in `models.md` (Module.abstractness field).

5. **Pattern classification** --- detect architectural patterns (layered, modular, hub-and-spoke, god-module) from the module graph topology and metric distributions.

6. **Health aggregation** --- combine per-module metrics into `ArchHealth`.

## Temporal Contract

As required by `registry/temporal-operators.md`, every module spec defines its temporal interface.

### Output at time t

`Architecture(t)` --- the full architectural model computed from `CodeGraph(t)` and file roles at time t. Includes modules, layers, violations, patterns, and health.

### Delta(t1, t2)

```
ArchDelta:
  modules_added:       [Module]        # new directories/communities became modules
  modules_removed:     [Module]        # modules that no longer exist
  modules_split:       [(old, [new])]  # one module became multiple
  modules_merged:      [([old], new)]  # multiple modules collapsed into one
  layer_changes:       [(module, old_depth, new_depth)]
  new_violations:      [Violation]
  resolved_violations: [Violation]
  pattern_changes:     [(pattern, old_val, new_val)]
  cohesion_deltas:     {module_path: float}
  coupling_deltas:     {module_path: float}
```

Module identity across snapshots: match by path. If a path disappears and a new one appears with >70% file overlap, classify as rename/split/merge.

### Time series

| Metric | What it reveals |
|--------|-----------------|
| `violation_count(t)` | Architecture erosion rate |
| `violation_rate(t)` | Normalized erosion (violations / cross-module edges) |
| `mean_cohesion(t)` | Are modules becoming more/less focused? |
| `mean_coupling(t)` | Are modules becoming more/less entangled? |
| `mean_D(t)` | Architecture quality trend (main sequence distance) |
| `layer_count(t)` | Is architecture getting deeper or flatter? |
| `god_module_size(t)` | Is the biggest module growing disproportionately? |
| `boundary_alignment(t)` | Are directory boundaries drifting from dependency communities? |
| `architecture_drift_velocity(t)` | GED of module graph between snapshots |

### Reconstruction

Rebuild from historical `CodeGraph` + file roles:

```
architecture(t) = ArchitectureAnalyzer.analyze(
    code_graph=rebuild_graph(t),
    file_roles=rebuild_roles(t)
)
```

Requires Kind 3 temporal data (historical reconstruction via `git show`).

## Error Handling and Edge Cases

| Condition | Behavior |
|-----------|----------|
| Flat project (all files in one directory) | Louvain communities become modules. `boundary_alignment` = 1.0 by definition. Log: "No directory structure detected; using dependency communities as modules." |
| No layers detected (DAG has depth 0 or 1) | `is_layered = false`, `layer_violation_count = 0`. Skip layer-related signals. Log: "No layered architecture detected." |
| Single module | All module-level signals are trivially computed (cohesion=1, coupling=0, etc.). `ArchPatterns` flags all false except trivially true ones. |
| Module with 1 file | `cohesion = 0` (no internal edges possible). `coupling` = 1 or 0 depending on external edges. |
| Disconnected components | Each connected component is analyzed independently. Modules may span components. |
| Circular module dependencies | Back-edges are removed for layer assignment, then recorded as BACKWARD violations. |
| No semantic roles available | `role_consistency` defaults to 1.0. `ModuleRole` = UNKNOWN for all modules. |

## File Layout

```
architecture/
  __init__.py           # re-exports: ArchitectureAnalyzer, Architecture, Module, Layer, ...
  analyzer.py           # ArchitectureAnalyzer: orchestrates the pipeline
  models.py             # Architecture, Module, Layer, Violation, ArchPatterns, ArchHealth, ArchDelta
  module_detection.py   # module boundary detection algorithm
  layer_inference.py    # layer assignment + violation detection
  martin_metrics.py     # I, A, D computation with expanded abstractness
  patterns.py           # architectural pattern classification
```
