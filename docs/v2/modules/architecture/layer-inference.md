# architecture/ --- Layer Inference Algorithm

How Shannon Insight infers architectural layers from the dependency graph without any user-provided layering configuration. Produces layer assignments, detects violations, and computes architecture entropy.

## Overview

```
File-level CodeGraph
        |
        v
  [Module Graph Contraction]  -- collapse file edges into module edges
        |
        v
  Module directed graph
        |
        v
  [Cycle Detection]           -- DFS to find back-edges
        |
        v
  [DAG Extraction]            -- remove back-edges
        |
        v
  [Topological Sort]          -- establish dependency ordering
        |
        v
  [Layer Assignment]          -- assign depth to each module
        |
        v
  [Violation Detection]       -- classify removed back-edges + skip edges
```

## Step 1: Module Graph Contraction

Collapse the file-level `CodeGraph` into a module-level directed graph.

```
Input:  CodeGraph (file nodes + file edges)
        Module assignments (from module-detection.md)
Output: Module graph G_m = (V_m, E_m)

For each file edge (file_a -> file_b) in CodeGraph:
    module_a = module_of(file_a)
    module_b = module_of(file_b)
    if module_a != module_b:
        E_m[module_a -> module_b].weight += 1
        E_m[module_a -> module_b].files.append((file_a, file_b))
```

Each module-level edge records:
- `weight`: number of file-level edges it aggregates.
- `files`: the specific file pairs for traceability (used in `Violation.files`).
- `symbols`: union of all symbols crossing this boundary.

Self-loops (intra-module edges) are counted separately as `internal_edges` for cohesion computation. They do not appear in the module graph.

## Step 2: Cycle Detection (DFS)

Run DFS on the module graph to identify back-edges (cycles).

```
visited = {}     # module -> {WHITE, GRAY, BLACK}
back_edges = []

def dfs(module):
    visited[module] = GRAY
    for neighbor in G_m[module]:
        if visited[neighbor] == GRAY:
            back_edges.append((module, neighbor))  # cycle!
        elif visited[neighbor] == WHITE:
            dfs(neighbor)
    visited[module] = BLACK

for module in V_m:
    if visited.get(module, WHITE) == WHITE:
        dfs(module)
```

Back-edges represent circular dependencies between modules. These are the primary source of BACKWARD violations.

### Multiple Cycles

If the module graph has multiple SCCs (strongly connected components), each SCC's back-edges are detected independently. Use Tarjan's algorithm for SCC detection if the graph is large.

## Step 3: DAG Extraction

Remove all back-edges to produce a DAG:

```
G_dag = copy(G_m)
for (source, target) in back_edges:
    G_dag.remove_edge(source, target)
```

The resulting `G_dag` is a directed acyclic graph suitable for topological sorting.

## Step 4: Topological Sort

Compute a topological ordering of the DAG:

```
topo_order = topological_sort(G_dag)
# topo_order[0] = module with no dependencies (foundation)
# topo_order[-1] = module with most transitive dependencies (top layer)
```

Standard algorithm: Kahn's algorithm (BFS with in-degree tracking) or DFS-based reverse post-order.

## Step 5: Layer Assignment

Assign each module a layer depth based on its longest dependency path:

```
layer = {}

for module in topo_order:
    if in_degree(module, G_dag) == 0:
        layer[module] = 0                            # foundation layer
    else:
        layer[module] = max(layer[dep] + 1 for dep in predecessors(module, G_dag))
```

This produces a layering where:
- Layer 0: modules with no dependencies (foundations, core abstractions).
- Layer N: modules that transitively depend on up to N layers below.
- Deeper layers are "higher" in the architecture (closer to entry points / user-facing code).

### Layer Grouping

Group modules into `Layer` objects:

```
layers = defaultdict(list)
for module, depth in layer.items():
    layers[depth].append(module)

result = [Layer(depth=d, modules=sorted(ms)) for d, ms in sorted(layers.items())]
```

## Step 6: Violation Detection

Re-examine ALL original module-graph edges (including the back-edges removed in Step 3) to detect violations:

```
violations = []

for (source, target, data) in G_m.edges:
    src_layer = layer[source]
    tgt_layer = layer[target]

    if src_layer < tgt_layer:
        # Lower layer depends on higher layer -- BACKWARD violation
        violations.append(Violation(
            source_module=source,
            target_module=target,
            source_layer=src_layer,
            target_layer=tgt_layer,
            type=ViolationType.BACKWARD,
            edge_count=data.weight,
            symbols=data.symbols,
            files=data.files,
        ))

    if abs(src_layer - tgt_layer) > 1:
        # Dependency skips intermediate layers -- SKIP violation
        violations.append(Violation(
            source_module=source,
            target_module=target,
            source_layer=src_layer,
            target_layer=tgt_layer,
            type=ViolationType.SKIP,
            edge_count=data.weight,
            symbols=data.symbols,
            files=data.files,
        ))
```

Note: a single edge can be both BACKWARD and SKIP (e.g., layer 0 importing from layer 3). In this case, two `Violation` objects are created for the same edge.

### BACKWARD vs SKIP Severity

| Type | Severity | Rationale |
|------|----------|-----------|
| BACKWARD | High | Inverts dependency direction. Foundation layer becomes coupled to higher layers. Changes in upper layers break foundations. |
| SKIP | Medium | Bypasses intermediary abstractions. Creates hidden coupling. May indicate missing abstraction layer. |

## Architecture Entropy

Measures the evenness of module sizes. Computed from the file distribution across modules.

```
p_i = module_i.file_count / total_files
H_arch = -sum(p_i * log2(p_i) for p_i in proportions if p_i > 0)
H_max = log2(module_count)
evenness = H_arch / H_max   if H_max > 0 else 1.0
```

| Evenness | Interpretation |
|----------|---------------|
| > 0.8 | Modules are similarly sized. Healthy decomposition. |
| 0.5 -- 0.8 | Some modules are larger. Normal for projects with a core. |
| < 0.5 | One or two modules dominate. God module risk. |

## Edge Cases

### No Layered Architecture Detected

When `max(layer.values()) == 0` (all modules at the same depth):

- This occurs when the module graph is fully disconnected (no cross-module edges) or when all modules form a single SCC.
- Set `ArchPatterns.is_layered = false`.
- Set `ArchPatterns.layer_count = 1`.
- `layer_violation_count = 0` for all modules.
- No violations are produced.
- Log: "No layered architecture detected."

### All Modules in One Cycle

When all modules form a single SCC:

- All edges are back-edges. The DAG is empty.
- All modules are assigned layer 0.
- Every cross-module edge is a potential BACKWARD violation, but since there is no hierarchy, violations are not meaningful.
- Set `ArchPatterns.is_layered = false`.
- Log: "All modules form a dependency cycle. No layers can be inferred."

### Disconnected Module Graph

When the module graph has multiple weakly connected components:

- Run layer assignment independently per component.
- Layers are relative within each component (component A's layer 0 is unrelated to component B's layer 0).
- This is correct: independent subsystems have independent layerings.

### Single Module

When only one module is detected:

- No module graph exists.
- Layer assignment is trivially `{module: 0}`.
- No violations are possible.
- `ArchPatterns.is_layered = false`.

## Violation Rate

The normalized violation measure used in `ArchHealth`:

```
cross_module_edges = sum(edge.weight for edge in G_m.edges)
violating_edges = sum(v.edge_count for v in violations)
violation_rate = violating_edges / cross_module_edges   if cross_module_edges > 0 else 0.0
```

This is the fraction of cross-module dependencies that violate the inferred layering. Feeds into the global `architecture_health` composite (signal #61 in `registry/signals.md`).

## Visualization

Layers are presented as horizontal bands in the architecture view:

```
Layer 3 (top):    [cli/]  [web/]
Layer 2:          [services/]  [handlers/]
Layer 1:          [domain/]  [repositories/]
Layer 0 (base):   [models/]  [utils/]  [config/]

--- violations shown as red edges crossing upward ---
```

Each BACKWARD violation is a red arrow going from a lower layer to a higher layer. Each SKIP violation is a dotted arrow spanning more than one layer gap.
