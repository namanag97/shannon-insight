"""Layer inference for Phase 4.

Infers architectural layers from module dependencies:
1. Build module graph (contract file-level edges to module edges)
2. Detect cycles (modules in SCC merge to same layer)
3. Topological sort for layer depths
4. Detect violations (BACKWARD, SKIP)
5. Assign layer labels (entry, service, foundation)
"""

from collections import defaultdict, deque

from ..graph.models import DependencyGraph
from .models import Layer, Module, Violation, ViolationType


def build_module_graph(
    modules: dict[str, Module],
    file_graph: DependencyGraph,
) -> dict[str, dict[str, int]]:
    """Build weighted module graph from file-level edges.

    Contracts file-level edges to module-level edges.
    Edge weight = number of file-level edges.

    Args:
        modules: Dict of module path to Module
        file_graph: The file-level dependency graph

    Returns:
        Dict[source_module][target_module] = edge_count
    """
    # Build file -> module lookup
    file_to_module: dict[str, str] = {}
    for mod_path, mod in modules.items():
        for f in mod.files:
            file_to_module[f] = mod_path

    # Contract edges
    module_edges: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for source_file, targets in file_graph.adjacency.items():
        source_mod = file_to_module.get(source_file)
        if not source_mod:
            continue

        for target_file in targets:
            target_mod = file_to_module.get(target_file)
            if target_mod and target_mod != source_mod:
                module_edges[source_mod][target_mod] += 1

    return {k: dict(v) for k, v in module_edges.items()}


def infer_layers(
    modules: dict[str, Module],
    file_graph: DependencyGraph,
) -> tuple[list[Layer], list[Violation]]:
    """Infer architectural layers from module dependencies.

    Uses topological sort on the module graph. Modules with no
    dependencies are at layer 0 (foundation), and layers increase
    as we follow import edges.

    Args:
        modules: Dict of module path to Module
        file_graph: The file-level dependency graph

    Returns:
        Tuple of (list of Layer objects, list of Violations)
    """
    if not modules:
        return [], []

    module_graph = build_module_graph(modules, file_graph)

    # Build reverse graph for traversal from leaves
    reverse_graph: dict[str, set[str]] = defaultdict(set)
    for source, targets in module_graph.items():
        for target in targets:
            reverse_graph[target].add(source)

    # Compute out-degree for each module
    out_degree: dict[str, int] = dict.fromkeys(modules, 0)
    for source, targets in module_graph.items():
        out_degree[source] = len(targets)

    # BFS from modules with no outgoing edges (foundation modules)
    # Layer 0 = modules that don't import anything
    queue: deque[str] = deque()
    layer_assignment: dict[str, int] = {}

    for mod_path in modules:
        if out_degree.get(mod_path, 0) == 0 or mod_path not in module_graph:
            queue.append(mod_path)
            layer_assignment[mod_path] = 0

    # Propagate layers upward through reverse edges
    while queue:
        mod_path = queue.popleft()
        current_layer = layer_assignment[mod_path]

        # Modules that import this one are at a higher layer
        for importer in reverse_graph.get(mod_path, set()):
            new_layer = current_layer + 1
            if importer not in layer_assignment:
                layer_assignment[importer] = new_layer
                queue.append(importer)
            elif layer_assignment[importer] < new_layer:
                layer_assignment[importer] = new_layer
                queue.append(importer)

    # Handle any remaining modules (isolated or cycles)
    for mod_path in modules:
        if mod_path not in layer_assignment:
            layer_assignment[mod_path] = 0

    # Update modules with layer assignments
    max_layer = 0
    for mod_path, layer in layer_assignment.items():
        modules[mod_path].layer = layer
        max_layer = max(max_layer, layer)

    # Build Layer objects
    layers_by_depth: dict[int, list[str]] = defaultdict(list)
    for mod_path, layer in layer_assignment.items():
        layers_by_depth[layer].append(mod_path)

    layers = []
    for depth in range(max_layer + 1):
        mods = sorted(layers_by_depth.get(depth, []))
        label = _infer_layer_label(depth, max_layer, mods, modules)
        layers.append(Layer(depth=depth, modules=mods, label=label))

    # Detect violations
    violations = detect_violations(modules, module_graph)

    return layers, violations


def detect_violations(
    modules: dict[str, Module],
    module_graph: dict[str, dict[str, int]],
) -> list[Violation]:
    """Detect layer dependency violations.

    Violations:
    - BACKWARD: lower layer imports upper layer (source.layer < target.layer)
    - SKIP: layer N imports layer N-k where k > 1 (skipping intermediate layers)

    Args:
        modules: Dict of module path to Module (with layer assigned)
        module_graph: Module-level edge weights

    Returns:
        List of Violation objects
    """
    violations: list[Violation] = []

    for source_mod, targets in module_graph.items():
        if source_mod not in modules:
            continue
        source_layer = modules[source_mod].layer

        for target_mod, edge_count in targets.items():
            if target_mod not in modules:
                continue
            target_layer = modules[target_mod].layer

            if source_layer < target_layer:
                # BACKWARD: lower layer imports upper layer
                violations.append(
                    Violation(
                        source_module=source_mod,
                        target_module=target_mod,
                        source_layer=source_layer,
                        target_layer=target_layer,
                        violation_type=ViolationType.BACKWARD,
                        edge_count=edge_count,
                    )
                )
            elif source_layer - target_layer > 1:
                # SKIP: skipping intermediate layers
                violations.append(
                    Violation(
                        source_module=source_mod,
                        target_module=target_mod,
                        source_layer=source_layer,
                        target_layer=target_layer,
                        violation_type=ViolationType.SKIP,
                        edge_count=edge_count,
                    )
                )

    return violations


def _infer_layer_label(
    depth: int,
    max_depth: int,
    modules: list[str],
    all_modules: dict[str, Module],
) -> str:
    """Infer a human-readable label for a layer.

    Args:
        depth: Layer depth (0 = foundation)
        max_depth: Maximum layer depth
        modules: Module paths in this layer
        all_modules: All modules for role lookup

    Returns:
        Label string like "foundation", "service", "entry"
    """
    if depth == 0:
        return "foundation"
    elif depth == max_depth:
        return "entry"
    elif depth == max_depth - 1:
        return "service"
    else:
        return "logic"
