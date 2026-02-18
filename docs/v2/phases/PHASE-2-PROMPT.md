# Phase 2: Build Proper Multi-Type Graph from Facts

## Context

Phase 1 is complete. We now store all parsed data in `.shannon/facts.db`:
- `call_targets` for every function (what it calls)
- `bases` for every class (inheritance)
- `names` for every import (symbol-level)
- `resolved_path` for imports (pre-computed resolution)

**The problem:** The graph builder (`src/shannon_insight/graph/builder.py`) ignores all of this. It only builds FILE → FILE edges from import statements.

## Your Task

Update the graph infrastructure to build a proper multi-type graph with:

1. **FILE → FILE edges** (imports) - already works
2. **FUNCTION → FUNCTION edges** (calls) - NEW
3. **CLASS → CLASS edges** (inheritance) - NEW
4. **FILE → FUNCTION edges** (contains) - NEW
5. **FILE → CLASS edges** (contains) - NEW

## Files to Modify

### 1. `src/shannon_insight/graph/models.py`

Add new types:

```python
from enum import Enum

class NodeType(Enum):
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"

class EdgeType(Enum):
    IMPORTS = "imports"           # FILE -> FILE
    CALLS = "calls"               # FUNCTION -> FUNCTION
    INHERITS = "inherits"         # CLASS -> CLASS
    CONTAINS = "contains"         # FILE -> FUNCTION/CLASS

@dataclass
class CodeGraph:
    """Multi-type dependency graph."""

    # Nodes by type
    file_nodes: set[str] = field(default_factory=set)
    function_nodes: set[str] = field(default_factory=set)  # "file:qualified_name"
    class_nodes: set[str] = field(default_factory=set)     # "file:ClassName"

    # Edges by type (adjacency lists)
    import_edges: dict[str, list[str]] = field(default_factory=dict)
    call_edges: dict[str, list[str]] = field(default_factory=dict)
    inherit_edges: dict[str, list[str]] = field(default_factory=dict)
    contains_edges: dict[str, list[str]] = field(default_factory=dict)

    # Reverse indexes
    imported_by: dict[str, list[str]] = field(default_factory=dict)
    called_by: dict[str, list[str]] = field(default_factory=dict)
    inherited_by: dict[str, list[str]] = field(default_factory=dict)
    contained_in: dict[str, str] = field(default_factory=dict)
```

### 2. `src/shannon_insight/graph/builder.py`

Add new function that reads from FactDatabase:

```python
def build_code_graph_from_facts(
    db: FactDatabase,
    session_id: str
) -> CodeGraph:
    """Build multi-type graph from stored facts.

    This is the NEW way - uses pre-computed data from Phase 1.
    """
    graph = CodeGraph()

    # Get all facts
    file_facts = db.get_file_facts_for_session(session_id)
    call_targets = db.get_call_targets_for_session(session_id)
    class_bases = db.get_class_bases_for_session(session_id)
    imports = db.get_imports_for_session(session_id)

    # Build FILE nodes
    for fact in file_facts:
        graph.file_nodes.add(fact.path)

    # Build FUNCTION nodes and CONTAINS edges
    for qualified_name in call_targets.keys():
        # qualified_name is "ClassName.method" or "func_name"
        # We need to find which file it's in
        file_path = _find_file_for_function(qualified_name, file_facts)
        if file_path:
            node_id = f"{file_path}:{qualified_name}"
            graph.function_nodes.add(node_id)
            graph.contains_edges.setdefault(file_path, []).append(node_id)
            graph.contained_in[node_id] = file_path

    # Build CALL edges
    for caller_qn, targets in call_targets.items():
        caller_file = _find_file_for_function(caller_qn, file_facts)
        if not caller_file:
            continue
        caller_node = f"{caller_file}:{caller_qn}"

        for target in targets:
            # Resolve target to a node
            target_node = _resolve_call_target(target, caller_file, file_facts, call_targets)
            if target_node:
                graph.call_edges.setdefault(caller_node, []).append(target_node)
                graph.called_by.setdefault(target_node, []).append(caller_node)

    # Build CLASS nodes and INHERIT edges
    for class_key, bases in class_bases.items():
        # class_key is "file:ClassName"
        graph.class_nodes.add(class_key)
        file_path = class_key.split(":")[0]
        graph.contains_edges.setdefault(file_path, []).append(class_key)
        graph.contained_in[class_key] = file_path

        for base in bases:
            # Try to resolve base class to a node
            base_node = _resolve_class(base, file_path, class_bases)
            if base_node:
                graph.inherit_edges.setdefault(class_key, []).append(base_node)
                graph.inherited_by.setdefault(base_node, []).append(class_key)

    # Build IMPORT edges (use resolved_path from facts)
    for imp in imports:
        if imp.resolved_path:
            graph.import_edges.setdefault(imp.file_path, []).append(imp.resolved_path)
            graph.imported_by.setdefault(imp.resolved_path, []).append(imp.file_path)

    return graph
```

### 3. `src/shannon_insight/graph/algorithms.py`

Add algorithms for new edge types:

```python
def compute_function_pagerank(graph: CodeGraph) -> dict[str, float]:
    """PageRank on the function call graph."""
    # Use graph.call_edges instead of graph.import_edges
    ...

def find_dead_functions(graph: CodeGraph) -> set[str]:
    """Functions with no incoming CALL edges (never called)."""
    all_functions = graph.function_nodes
    called_functions = set(graph.called_by.keys())
    return all_functions - called_functions

def compute_inheritance_depth(graph: CodeGraph) -> dict[str, int]:
    """Compute inheritance chain depth for each class."""
    depths = {}
    for class_node in graph.class_nodes:
        depth = 0
        current = class_node
        visited = set()
        while current in graph.inherit_edges and current not in visited:
            visited.add(current)
            bases = graph.inherit_edges[current]
            if bases:
                depth += 1
                current = bases[0]  # Follow first base
            else:
                break
        depths[class_node] = depth
    return depths

def find_diamond_inheritance(graph: CodeGraph) -> list[tuple[str, list[str]]]:
    """Find classes with diamond inheritance pattern."""
    diamonds = []
    for class_node in graph.class_nodes:
        # BFS to find if multiple paths lead to same ancestor
        ...
    return diamonds
```

### 4. Update `GraphAnalysis` model

Add new fields:

```python
@dataclass
class GraphAnalysis:
    # Existing fields...

    # NEW: Function-level analysis
    function_pagerank: dict[str, float] = field(default_factory=dict)
    function_betweenness: dict[str, float] = field(default_factory=dict)
    dead_functions: set[str] = field(default_factory=set)
    function_cycles: list[set[str]] = field(default_factory=list)

    # NEW: Class-level analysis
    inheritance_depth: dict[str, int] = field(default_factory=dict)
    diamond_classes: list[str] = field(default_factory=list)

    # NEW: Cross-cutting
    hotspot_functions: list[str] = field(default_factory=list)  # high centrality + high churn
```

## Key Implementation Details

### Resolving Call Targets

`call_targets` contains raw identifiers like `["logger", "AnalysisStore", "self.run"]`. You need to resolve these to actual function nodes:

```python
def _resolve_call_target(
    target: str,
    caller_file: str,
    file_facts: list[FileFact],
    all_functions: dict[str, list[str]]
) -> str | None:
    """Resolve a call target string to a function node ID.

    Strategy:
    1. If target matches a function in same file, use that
    2. If target matches an imported name, follow the import
    3. If target is "self.X" or "cls.X", look for method X in same class
    4. Otherwise, return None (external/stdlib call)
    """
    # Check same-file functions first
    for qn in all_functions.keys():
        if qn.endswith(f".{target}") or qn == target:
            file_for_func = _find_file_for_function(qn, file_facts)
            if file_for_func == caller_file:
                return f"{caller_file}:{qn}"

    # Check if it's an imported symbol
    # ...

    return None  # External call, don't create edge
```

### Handling Methods

Methods have `class_name` set. Their qualified name is `ClassName.method_name`. When building call edges:
- `self.other_method` should resolve to `ClassName.other_method` in same file
- `super().method` should resolve to base class method

## Tests to Write

Create `tests/graph/test_code_graph.py`:

```python
def test_call_edges_created_from_call_targets():
    """Call targets from Phase 1 become CALL edges."""
    # Setup: create facts with call_targets
    # Build graph
    # Assert: call_edges exist

def test_inherit_edges_created_from_bases():
    """Class bases from Phase 1 become INHERIT edges."""
    ...

def test_function_pagerank_computed():
    """PageRank works on function call graph."""
    ...

def test_dead_functions_detected():
    """Functions with no callers are detected."""
    ...

def test_inheritance_depth_computed():
    """Inheritance depth is computed correctly."""
    ...
```

## Integration

Once `CodeGraph` is built, integrate it:

1. **Kernel**: After fact storage, build `CodeGraph` from facts
2. **Analyzers**: Use `CodeGraph` instead of `DependencyGraph` for richer analysis
3. **Finders**: New findings like `DEAD_CODE`, `DEEP_INHERITANCE`, `HOTSPOT_FUNCTION`

## Success Criteria

After Phase 2:

```python
# This should work:
graph = build_code_graph_from_facts(db, session_id)

assert len(graph.call_edges) > 0  # Function calls tracked
assert len(graph.inherit_edges) > 0  # Inheritance tracked
assert len(graph.function_nodes) > len(graph.file_nodes)  # More granular

# New signals available:
analysis = analyze_code_graph(graph)
assert "kernel.py:InsightKernel.run" in analysis.function_pagerank
assert len(analysis.dead_functions) >= 0
```

## Do NOT

- Do not break existing `DependencyGraph` - keep it for backward compat
- Do not remove existing tests
- Do not change the Fact models from Phase 1
- Do not store the new graph in facts.db (it's computed, not stored)

## Estimated Effort

| Task | Hours |
|------|-------|
| CodeGraph model | 2 |
| build_code_graph_from_facts | 4 |
| Call target resolution | 3 |
| New algorithms | 4 |
| Tests | 3 |
| Integration | 2 |
| **Total** | **18** |
