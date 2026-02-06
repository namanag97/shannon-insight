# architecture/ --- Data Models

All data models for the architecture package. These are pure data containers (dataclasses); computation logic lives in the analyzer, module detection, layer inference, and metric modules.

## Architecture

The top-level result of `ArchitectureAnalyzer.analyze()`.

```python
@dataclass
class Architecture:
    modules:     list[Module]       # all detected modules
    layers:      list[Layer]        # topological layer assignments
    violations:  list[Violation]    # layering violations
    patterns:    ArchPatterns       # classified architectural patterns
    health:      ArchHealth         # aggregate health metrics
    module_graph: dict[str, list[str]]  # adjacency list: module_path -> [dependency_paths]
```

Serializable via `dataclasses.asdict()`. Stored fully in persistence (IR4 data is small --- module-level, not file-level).

## Module

A group of source files that form a logical unit. Detected via directory structure, Louvain fallback, or config override (see `module-detection.md`).

```python
@dataclass
class Module:
    path:             str           # directory path relative to project root (e.g., "src/auth/")
    files:            list[str]     # file paths belonging to this module
    role:             ModuleRole    # aggregated from file roles
    role_distribution: dict[str, int]  # Role -> count (e.g., {"SERVICE": 5, "MODEL": 3})

    # Structural metrics (see registry/signals.md #37-44)
    cohesion:          float        # signal #37: internal_edges / possible_edges
    coupling:          float        # signal #38: external_edges / total_edges
    instability:       Optional[float]  # signal #39: Ce / (Ca + Ce), None if Ca+Ce=0
    abstractness:      float        # signal #40: abstract_symbols / total_symbols
    main_seq_distance: float        # signal #41: |A + I - 1|, 0.0 if instability is None
    boundary_alignment: float       # signal #42: files in dominant Louvain community / total
    layer_violation_count: int      # signal #43: backward/skip edges into this module
    role_consistency:  float        # signal #44: max(role_count) / total_files
    file_count:        int          # signal #50

    # Edge counts (used to compute I, coupling)
    ca: int                         # afferent coupling: incoming edges from other modules
    ce: int                         # efferent coupling: outgoing edges to other modules
    internal_edges: int             # edges between files within this module
```

### Invariants

- `file_count == len(files)`
- `instability == ce / (ca + ce)` if `ca + ce > 0`, else `None` (isolated module)
- `main_seq_distance == abs(abstractness + instability - 1.0)` if `instability is not None`, else `0.0`
- `role_consistency == max(role_distribution.values()) / file_count` if `file_count > 0`
- `cohesion == 0.0` if `file_count <= 1`

## ModuleRole

Aggregated role for a module, derived from the dominant file role within it.

```python
class ModuleRole(str, Enum):
    MODEL       = "MODEL"        # majority of files are MODEL
    SERVICE     = "SERVICE"      # majority are SERVICE
    UTILITY     = "UTILITY"      # majority are UTILITY
    CONFIG      = "CONFIG"       # majority are CONFIG
    TEST        = "TEST"         # majority are TEST
    CLI         = "CLI"          # majority are CLI
    INTERFACE   = "INTERFACE"    # majority are INTERFACE
    MIXED       = "MIXED"        # no role exceeds 50% of files
    UNKNOWN     = "UNKNOWN"      # majority are UNKNOWN
```

Assignment rule:

```
dominant_role = mode(file.role for file in module.files)
if count(dominant_role) / len(module.files) >= 0.5:
    module.role = ModuleRole(dominant_role.name)
else:
    module.role = ModuleRole.MIXED
```

MIXED modules are a smell: the directory contains files with diverse purposes, suggesting the module boundary is wrong.

## Layer

A depth level in the inferred architectural layering. Depth 0 = foundation (no dependencies on other layers), higher depths = closer to entry points / user-facing.

```python
@dataclass
class Layer:
    depth:    int             # 0 = foundation layer
    modules:  list[str]       # module paths assigned to this layer
```

Layer assignment is computed by `layer_inference.py` (see `layer-inference.md`). When no layered architecture is detected, the `layers` list is empty.

## Violation

A dependency that breaks the inferred layering.

```python
class ViolationType(str, Enum):
    BACKWARD = "BACKWARD"   # lower-layer module depends on higher-layer module
    SKIP     = "SKIP"       # dependency skips one or more intermediate layers

@dataclass
class Violation:
    source_module:  str             # module containing the importing file(s)
    target_module:  str             # module being imported
    source_layer:   int             # layer depth of source module
    target_layer:   int             # layer depth of target module
    type:           ViolationType   # BACKWARD or SKIP
    edge_count:     int             # number of file-level edges constituting this violation
    symbols:        list[str]       # imported symbols crossing the boundary
    files:          list[tuple[str, str]]  # [(source_file, target_file), ...] for traceability
```

### Violation Types

**BACKWARD**: `source_layer < target_layer`. A foundation-layer module imports from a higher layer. This inverts the dependency direction and creates rigidity --- changes in upper layers can break lower layers.

**SKIP**: `abs(source_layer - target_layer) > 1`. A module depends on another more than one layer away, bypassing intermediate layers. This creates hidden coupling and makes the intermediate layers' abstraction leaky.

A single file-level edge can constitute both a BACKWARD and SKIP violation simultaneously if it goes from layer 0 to layer 3, for example.

## ArchPatterns

Boolean flags and metrics classifying the overall architectural shape.

```python
@dataclass
class ArchPatterns:
    is_layered:      bool   # clear topological ordering exists (layer_count >= 2)
    is_modular:      bool   # mean cohesion > 0.3 AND mean coupling < 0.5
    has_god_module:  bool   # largest module has > 40% of all cross-module edges
    hub_and_spoke:   bool   # one module has > 50% of total outgoing edges
    layer_count:     int    # max layer depth + 1
    max_module_size: int    # file_count of largest module
    module_count:    int    # total number of detected modules

    # Architecture entropy (module size distribution)
    architecture_entropy:  float   # H of module size distribution
    architecture_evenness: float   # H / H_max --- 1.0 = all modules same size
```

### Pattern Detection Rules

| Pattern | Condition |
|---------|-----------|
| `is_layered` | `layer_count >= 2` AND `violation_rate < 0.3` |
| `is_modular` | `mean(cohesion) > 0.3` AND `mean(coupling) < 0.5` |
| `has_god_module` | `max(module.ca + module.ce) / sum(all cross-module edges) > 0.4` |
| `hub_and_spoke` | `max(module.ce) / sum(module.ce for all) > 0.5` |

## ArchHealth

Aggregate architectural health metrics. Feeds into the global `architecture_health` composite (signal #61 in `registry/signals.md`).

```python
@dataclass
class ArchHealth:
    violation_rate:        float   # violating edges / total cross-module edges
    mean_cohesion:         float   # mean of module cohesion values
    mean_coupling:         float   # mean of module coupling values
    mean_main_seq_dist:    float   # mean of module D values
    boundary_alignment:    float   # mean of module boundary_alignment values
    mean_role_consistency: float   # mean of module role_consistency values
```

## ArchDelta

Structured diff between two `Architecture` snapshots at different times.

```python
@dataclass
class ArchDelta:
    # Module lifecycle
    modules_added:       list[Module]
    modules_removed:     list[Module]
    modules_split:       list[tuple[str, list[str]]]    # (old_path, [new_paths])
    modules_merged:      list[tuple[list[str], str]]    # ([old_paths], new_path)

    # Layer changes
    layer_changes:       list[tuple[str, int, int]]     # (module_path, old_depth, new_depth)

    # Violation lifecycle
    new_violations:      list[Violation]
    resolved_violations: list[Violation]

    # Pattern changes
    pattern_changes:     list[tuple[str, Any, Any]]     # (pattern_name, old_value, new_value)

    # Per-module metric deltas
    cohesion_deltas:     dict[str, float]   # module_path -> delta
    coupling_deltas:     dict[str, float]
    instability_deltas:  dict[str, float]
    abstractness_deltas: dict[str, float]
```

### Module Identity Across Snapshots

Modules are matched by path. When a path disappears:

1. Check if a new path appeared with >70% file overlap --- classify as **rename**.
2. Check if the files distributed across multiple new modules --- classify as **split**.
3. Check if multiple old modules merged into one new path --- classify as **merge**.
4. Otherwise --- classify as **removed**.

File overlap computation:

```
overlap(old, new) = |old.files & new.files| / |old.files | new.files|
```

Uses Jaccard similarity. Threshold: 0.7 for rename, 0.3 for split/merge detection.
