# graph/builder.md -- Edge Construction

`GraphBuilder` constructs a `CodeGraph` from scanning, semantics, and temporal inputs. It resolves import paths, call targets, and type references into typed edges with confidence tags.

## Current State

Today `builder.py` contains a single function `build_dependency_graph()` that:
1. Builds a dotted-path index from all file paths
2. Resolves each import string (relative and absolute) to a file path
3. Returns a `DependencyGraph` with adjacency/reverse dicts

This handles IMPORT edges only. Resolution is Python-centric (dotted modules, `__init__.py`, relative imports).

## v2 GraphBuilder

```python
class GraphBuilder:
    def __init__(
        self,
        syntax: list[FileSyntax],          # from scanning/ (IR1)
        semantics: list[FileSemantics],    # from semantics/ (IR2), optional
        temporal: Optional[TemporalModel], # from temporal/ (IR5t), optional
    ): ...

    def build(self) -> CodeGraph: ...
```

### Construction phases

```
Phase 1: IMPORT edges        (exists today, all languages)
Phase 2: CALL edges           (NEW, per-language resolution)
Phase 3: TYPE_FLOW edges      (NEW, per-language resolution)
Phase 4: Co-change enrichment (NEW, optional temporal join)
Phase 5: Unresolved tracking  (NEW, explicit phantom/broken logging)
```

---

## Phase 1: IMPORT Edges (exists)

For every `ImportDecl` in every `FileSyntax`:

```
if import.resolved_path is not None:
    add Edge(source, resolved_path, IMPORT, import.names, confidence=HIGH)
elif not import.is_external:
    add UnresolvedEdge(source, import.source, PHANTOM_IMPORT, context)
```

### Import resolution strategy

Exists today in `builder.py`. v2 extends for multi-language:

| Language | Resolution | Notes |
|----------|-----------|-------|
| Python | Dotted path + relative imports | Exists. Handles `__init__.py`, `src.` prefix stripping |
| Go | Package path from `import "pkg/path"` | Match against directory structure |
| TypeScript/JS | Relative `./` and `../` paths, `@/` aliases | Parse `tsconfig.json` for path mappings |
| Java | Package declaration + class name | Match `com.foo.Bar` to `com/foo/Bar.java` |
| Rust | `mod` declarations + `use` statements | Follow `mod.rs` / directory conventions |
| Ruby | `require` / `require_relative` | File path with `.rb` extension |
| C/C++ | `#include "local.h"` (not `<system.h>`) | Header-to-source mapping heuristic |

All IMPORT edges have `confidence=HIGH` because resolution is deterministic from the import path. If resolution fails, the edge becomes an `UnresolvedEdge`, not a LOW-confidence edge.

---

## Phase 2: CALL Edges (NEW)

For every call site extracted by tree-sitter (stored in `FunctionDef.calls`), resolve the target to a file.

### Resolution strategies by language

#### Python: JARVIS integration

JARVIS (2024 SOTA, ~99% precision, ~84% recall) provides flow-sensitive call resolution:

```
For Python projects:
  1. Run JARVIS on project root -> call graph JSON
  2. Map JARVIS output to our Edge model:
     for each (caller_file, caller_fn) -> (callee_file, callee_fn):
       add Edge(caller_file, callee_file, CALL, [callee_fn], confidence=HIGH)
```

JARVIS resolves: direct calls, method calls on known types, class instantiation, module-qualified calls, import aliases.

JARVIS does NOT resolve: `eval()`, `getattr()`, metaprogramming, complex closures. These become `UnresolvedEdge(type=BROKEN_CALL)` only if the call target appears to be project-internal.

**Fallback** (if JARVIS unavailable): use the heuristic strategy below.

#### Other languages: heuristic resolution

```
For each call site call_expr in function F of file A:

  Case 1: Direct call  foo()
    Search imports of A for symbol "foo"
    If found in file B: Edge(A, B, CALL, ["foo"], confidence=HIGH)

  Case 2: Qualified call  module.foo()
    Search imports of A for "module"
    If "module" resolves to file B, check B defines "foo"
    If yes: Edge(A, B, CALL, ["foo"], confidence=HIGH)
    If B exists but "foo" not found: Edge(A, B, CALL, ["foo"], confidence=MEDIUM)

  Case 3: Method call  obj.method()
    If obj has a type annotation -> resolve type to file
      confidence=HIGH (if type resolves) or MEDIUM (if type is ambiguous)
    If no type annotation:
      Search all imported files for a function/method named "method"
      If exactly 1 match: Edge(A, match, CALL, ["method"], confidence=MEDIUM)
      If multiple matches: Edge to each candidate, confidence=LOW
      If 0 matches: UnresolvedEdge(A, "obj.method", BROKEN_CALL)

  Case 4: Chained call  a.b.c()
    confidence=LOW at best. Only attempt if "a" resolves via imports.
    Otherwise: skip (do not create edge or unresolved record).
```

### Per-language confidence estimates

From W4 research (see `docs/solutions.md`):

| Language | Approach | Precision | Recall | Default confidence |
|----------|----------|-----------|--------|--------------------|
| Python | JARVIS | ~99% | ~84% | HIGH |
| JavaScript | Import tracking + heuristic | ~90% | ~70% | MEDIUM |
| TypeScript | Import tracking + type annotations | ~92% | ~75% | MEDIUM |
| Go | Import tracking + package-qualified calls | ~85% | ~65% | MEDIUM |
| Java | Import tracking + class-qualified calls | ~90% | ~70% | MEDIUM |
| Rust | `use` tracking + module-qualified calls | ~85% | ~60% | MEDIUM |
| Ruby | `require` tracking + heuristic | ~75% | ~50% | LOW |
| C/C++ | Header tracking + heuristic | ~70% | ~50% | LOW |

---

## Phase 3: TYPE_FLOW Edges (NEW)

For every function parameter, return type, and field annotation that references a project-internal type:

```
for file in files:
    for func in file.functions:
        for type_ref in extract_type_references(func):
            defining_file = resolve_type(type_ref, file.imports, all_files)
            if defining_file and defining_file != file.path:
                add Edge(file.path, defining_file, TYPE_FLOW, [type_ref], confidence)
```

### Type reference extraction

Extracted by tree-sitter from:
- Function parameter type annotations: `def foo(user: User)` -> `User`
- Return type annotations: `def foo() -> Token` -> `Token`
- Variable annotations: `db: Database = ...` -> `Database`
- Class field annotations: `name: str` (skip builtins)
- Generic parameters: `list[User]` -> `User`

### Resolution

Same as CALL Case 1/2: search imports for the type name, resolve to defining file. Confidence follows the same model.

TYPE_FLOW edges are the hardest to resolve accurately because type aliases, re-exports, and generic wrappers create ambiguity. In languages without type annotations (Ruby, JS without TS), TYPE_FLOW edges are not generated.

---

## Phase 4: Co-change Enrichment (NEW, optional)

If `temporal/` provides `PairDynamics`, annotate edges with temporal coupling:

```
for edge in graph.edges:
    pair_key = (edge.source, edge.target)
    if pair_key in pair_dynamics:
        edge.temporal_coupling = pair_dynamics[pair_key].lift * pair_dynamics[pair_key].confidence
```

This does not create new edges. It enriches existing structural edges with evolutionary data.

Edges with high structural weight but low temporal coupling are candidates for the DEAD_DEPENDENCY finder.

File pairs with high temporal coupling but NO structural edge are candidates for the HIDDEN_COUPLING finder (detected via distance space disagreement, not here).

---

## Phase 5: Unresolved Tracking

After all edge construction phases, compile unresolved references:

```
for file in files:
    # Phantom imports: imports with resolved_path=None and not external
    for imp in file.imports:
        if imp.resolved_path is None and not imp.is_external:
            add UnresolvedEdge(file.path, imp.source, PHANTOM_IMPORT, context_line)

    # Broken calls: call targets that could not be resolved
    # (already tracked during Phase 2)
```

Per-file signal `phantom_import_count` = count of PHANTOM_IMPORT unresolved edges for that file (signal #21).

Per-file signal `broken_call_count` = count of BROKEN_CALL unresolved edges for that file (signal #22).

---

## Multi-edge Collapse

Some algorithms (PageRank, BFS) need a simple directed graph. When collapsing:

```
simple_weight(A, B) = sum(edge.weight for edge in edges if edge.source == A and edge.target == B)
```

The collapsed graph is computed lazily and cached. It is NOT stored in `CodeGraph` -- algorithms request it via a method.

---

## Build Order Recommendation

For incremental v2 implementation:

1. **IMPORT edges** -- already done, refactor into Edge model with confidence=HIGH
2. **UnresolvedEdge tracking** -- straightforward, enables signal 21
3. **CALL edges for Python** -- JARVIS integration, highest value
4. **CALL edges for other languages** -- heuristic, diminishing returns per language
5. **TYPE_FLOW edges** -- requires type annotation extraction, lowest priority
