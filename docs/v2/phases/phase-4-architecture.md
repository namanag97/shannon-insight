# Phase 4: Architecture Package

## Goal

Create the `architecture/` package (IR4) that detects module boundaries, infers layers, computes Martin metrics (instability, abstractness, main sequence distance), and detects layer violations.

## Packages Touched

- **NEW** `architecture/` — new package
- `graph/models.py` — `ModuleAnalysis` gains Martin metrics fields
- `insights/store.py` — add architecture slot
- `insights/kernel.py` — register `ArchitectureAnalyzer`

## Prerequisites

- Phase 2 complete (file roles for `role_consistency` and `abstractness` detection)
- Phase 3 complete (enriched graph with orphan detection, depth, community data)

## Changes

### New: `architecture/__init__.py`

Exports: `ArchitectureAnalyzer`, `Architecture`, `Module`, `Layer`, `Violation`

### New: `architecture/models.py`

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

class ViolationType(Enum):
    BACKWARD = "backward"       # lower layer imports upper layer
    SKIP = "skip"               # layer N imports layer N+2 (skipping N+1)

@dataclass
class Module:
    """A group of source files forming a logical unit."""
    path: str                                     # directory path
    files: List[str] = field(default_factory=list)
    file_count: int = 0

    # Martin metrics
    afferent_coupling: int = 0     # Ca: incoming edges from other modules
    efferent_coupling: int = 0     # Ce: outgoing edges to other modules
    internal_edges: int = 0
    external_edges: int = 0
    cohesion: float = 0.0          # internal / possible_internal
    coupling: float = 0.0          # external / (internal + external)
    instability: Optional[float] = None  # Ce / (Ca + Ce), None if isolated (Ca=Ce=0)
    abstractness: float = 0.0      # abstract_symbols / total_symbols
    main_seq_distance: float = 0.0 # |A + I - 1|

    # Boundary analysis
    boundary_alignment: float = 0.0  # files in dominant community / total files
    role_consistency: float = 0.0    # max(role_count) / total files
    dominant_role: str = "UNKNOWN"

    # Layer assignment (set by layer inference)
    layer: int = -1                  # -1 = unassigned

@dataclass
class Layer:
    """A depth level in the inferred architectural layering."""
    depth: int
    modules: List[str] = field(default_factory=list)  # module paths
    label: str = ""   # e.g., "entry", "service", "core", "foundation"

@dataclass
class Violation:
    """A dependency that breaks the inferred layer ordering."""
    source_module: str
    target_module: str
    source_layer: int
    target_layer: int
    violation_type: ViolationType
    edge_count: int = 1           # number of file-level edges causing this

@dataclass
class Architecture:
    """Top-level result of architectural analysis."""
    modules: Dict[str, Module] = field(default_factory=dict)
    layers: List[Layer] = field(default_factory=list)
    violations: List[Violation] = field(default_factory=list)
    violation_rate: float = 0.0   # violating edges / total cross-module edges

    # Patterns detected
    has_layering: bool = False     # True if 2+ layers inferred
    max_depth: int = 0
    module_count: int = 0
```

### New: `architecture/analyzer.py`

```python
class ArchitectureAnalyzer:
    """Analyzer protocol implementation for architecture detection."""
    name = "architecture"
    requires = {"structural", "roles"}
    provides = {"architecture"}

    def analyze(self, store: AnalysisStore) -> None:
        # 1. Detect modules (directories → Module objects)
        modules = detect_modules(store.structural, store.root_dir)

        # 2. Compute Martin metrics per module
        compute_martin_metrics(modules, store.structural)

        # 3. Compute role consistency per module
        compute_role_consistency(modules, store.roles)

        # 4. Infer layers via module-level topological sort
        layers, violations = infer_layers(modules, store.structural)

        # 5. Assemble Architecture result
        store.architecture = Architecture(
            modules=modules,
            layers=layers,
            violations=violations,
            ...
        )
```

### New: `architecture/modules.py`

Module detection algorithm:

```
1. Walk the source tree. Each directory containing ≥1 analyzed source file is a candidate.

2. Determine granularity:
   - Count files per directory at each depth level
   - Choose the depth where most directories have 3-15 files
   - This is the "module depth"
   - Typical: depth=1 for flat projects, depth=2 for src/pkg/module layouts

3. Assign files to modules at the chosen depth.

4. Fallback for flat projects (all files in one directory):
   - Use Louvain communities from Phase 3 as synthetic modules
   - Label each community by its dominant role
```

**Config override**: Users can set module depth explicitly in `shannon-insight.toml`:
```toml
[architecture]
module_depth = 2  # or "auto" (default)
```

### New: `architecture/metrics.py`

Martin metrics computation:

```python
def compute_martin_metrics(modules: Dict[str, Module], structural: CodebaseAnalysis):
    """Compute instability, abstractness, and main-sequence distance per module."""
    for mod in modules.values():
        # Afferent coupling (Ca): edges from files in OTHER modules to files in THIS module
        # Efferent coupling (Ce): edges from files in THIS module to files in OTHER modules
        ca, ce = count_coupling(mod, modules, structural.graph)

        mod.afferent_coupling = ca
        mod.efferent_coupling = ce
        mod.instability = ce / (ca + ce) if (ca + ce) > 0 else None  # None = cannot measure (isolated module)
        # Finders (ZONE_OF_PAIN) must check `instability is not None` before evaluating.

        # Abstractness: abstract_symbols / total_symbols
        # For Python: ABC subclasses, Protocol subclasses, classes with @abstractmethod,
        #             functions raising NotImplementedError
        # "never-instantiated" detection deferred — requires CALL edges (see BACKLOG.md B6)
        mod.abstractness = compute_abstractness(mod, structural)

        # Main sequence distance: |A + I - 1|
        # Guard: instability can be None for isolated modules (Ca=Ce=0)
        if mod.instability is not None:
            mod.main_seq_distance = abs(mod.abstractness + mod.instability - 1.0)
        else:
            mod.main_seq_distance = 0.0  # cannot compute without instability
```

### New: `architecture/layers.py`

Layer inference:

```
1. Build module graph: contract file-level edges to module-level edges
   - Edge (mod_A → mod_B) if any file in A imports any file in B
   - Weight = number of file-level edges

2. Detect cycles: find SCCs in module graph
   - Modules in same SCC get merged into a single layer
   - Log warning: "Modules X, Y form a cycle — cannot determine layer order"

3. Remove back-edges to create DAG (keep the lower-weight edge as back-edge)

4. Topological sort (Kahn's algorithm) → each module gets a layer depth
   - Depth 0 = no dependencies on other modules (foundation)
   - Max depth = entry points

5. Detect violations:
   - BACKWARD: module at layer N imports module at layer N+k (k > 0, against inferred direction)
   - SKIP: module at layer N imports module at layer N-k where k > 1 (skipping intermediate layers)

6. Assign layer labels heuristically:
   - Deepest layer with entry points → "entry"
   - Layer 0 (no deps) → "foundation"
   - Middle layers → "service" or "logic"
```

### Modified: `graph/models.py`

Extend `ModuleAnalysis` with Martin metric fields:

```python
@dataclass
class ModuleAnalysis:
    # ... existing fields ...

    # Phase 4 additions:
    instability: Optional[float] = None
    abstractness: float = 0.0
    main_seq_distance: float = 0.0
    role_consistency: float = 0.0
    layer: int = -1
    layer_violation_count: int = 0
```

### Modified: `insights/store.py`

```python
@dataclass
class AnalysisStore:
    # ... existing ...

    # Phase 4:
    architecture: Optional[Architecture] = None

@property
def available(self) -> Set[str]:
    # ... existing ...
    if self.architecture:
        avail.add("architecture")
    return avail
```

## New Signals Available After This Phase

| # | Signal | Scale | Computed by |
|---|--------|-------|-------------|
| 37 | `cohesion` | S5 module | `architecture/metrics.py` |
| 38 | `coupling` | S5 module | `architecture/metrics.py` |
| 39 | `instability` | S5 module | `architecture/metrics.py` |
| 40 | `abstractness` | S5 module | `architecture/metrics.py` |
| 41 | `main_seq_distance` | S5 module | `architecture/metrics.py` |
| 42 | `boundary_alignment` | S5 module | existing (upgraded with role data) |
| 43 | `layer_violation_count` | S5 module | `architecture/layers.py` |
| 44 | `role_consistency` | S5 module | `architecture/metrics.py` |
| 50 | `file_count` | S5 module | `architecture/modules.py` |

Note: Module-level temporal signals (#45-48: velocity, coordination_cost, knowledge_gini, module_bus_factor) are deferred to Phase 5 since they require module definitions + temporal data aggregation.

## New Finders Available After This Phase

No new finders yet. But these signals unlock finders in Phase 6:
- `abstractness` + `instability` → ZONE_OF_PAIN finder
- `layer_violation_count` → LAYER_VIOLATION finder
- `boundary_alignment` → BOUNDARY_MISMATCH upgrade
- `role_consistency` → evidence for multiple finders

## Acceptance Criteria

1. Module detection produces sensible groupings for Shannon Insight's own codebase (scanning/, graph/, insights/, etc.)
2. Martin metrics:
   - `instability` = None for isolated modules (Ca=Ce=0)
   - `instability` ≈ 1.0 for a module with many outgoing deps and few incoming (unstable)
   - `instability` ≈ 0.0 for a module with many incoming deps and few outgoing (stable foundation)
3. Layer inference produces ≥ 2 layers for Shannon Insight's codebase
4. `config.py` (no deps) should be layer 0 (foundation)
5. `cli/` (depends on everything) should be highest layer
6. Violation detection finds at least one backward edge in a test fixture designed to have one
7. `role_consistency` = 1.0 for a directory where all files have the same role
8. Flat projects (all files in root) fall back to Louvain-based modules
9. All existing tests pass
10. `compute_abstractness` correctly identifies ABC/Protocol/abstractmethod patterns

## Edge Cases

- **Single-module project**: Skip layer inference, all metrics are trivial
- **Monorepo**: Respect workspace boundaries (use top-level directories as module roots)
- **Circular module dependencies**: Modules in SCC are merged to same layer, logged as warning
- **Empty modules** (directory with only `__init__.py`): Skip, don't create Module object

## Estimated Scope

- 5 new files (package init, models, analyzer, modules, metrics, layers)
- 3 modified files
- ~800 lines of new code
- ~2 weeks
