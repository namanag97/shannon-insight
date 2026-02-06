# semantics/ -- Data Models

All types exported by the `semantics/` package. Defined in `semantics/models.py`.

---

## FileSemantics

The complete semantic annotation for a single source file. One instance per file per snapshot.

```python
@dataclass(frozen=True)
class FileSemantics:
    path:          str                  # relative to project root, matches FileSyntax.path
    role:          Role                 # deterministic classification
    concepts:      list[Concept]        # sorted by weight descending; empty if < 20 identifiers
    public_api:    list[Symbol]         # exported functions, classes, constants
    consumed_api:  list[ConsumedSymbol] # imports that are actually referenced in code
    completeness:  Completeness         # stub ratio, docstring coverage, TODO density
```

**Invariants**:
- `path` is always set (never None).
- `role` is always set (never None) -- defaults to UNKNOWN.
- `concepts` may be empty (file below identifier threshold).
- `sum(c.weight for c in concepts)` approximately equals 1.0 when concepts are present.

---

## Role

Enum with 12 values. Classifies a file's architectural purpose. See `role-classification.md` for the decision tree.

```python
class Role(str, Enum):
    MODEL       = "model"        # Data structures, schemas, DTOs, ORM models
    SERVICE     = "service"      # Business logic with state or injected dependencies
    UTILITY     = "utility"      # Stateless helper functions, no classes
    CONFIG      = "config"       # Settings, constants, environment variable loading
    TEST        = "test"         # Test code (unit, integration, e2e)
    CLI         = "cli"          # Command-line interface definitions
    INTERFACE   = "interface"    # Abstract classes, protocols, ABCs, trait definitions
    EXCEPTION   = "exception"    # Custom exception/error class definitions
    CONSTANT    = "constant"     # Module-level constants (ALL_CAPS assignments)
    ENTRY_POINT = "entry_point"  # main(), __main__.py, WSGI/ASGI apps, cmd/main.go
    MIGRATION   = "migration"    # Database migration files
    UNKNOWN     = "unknown"      # Could not classify
```

**Design notes**:
- `str, Enum` mixin so the value serializes to JSON naturally.
- These 12 values cover the vast majority of files in production codebases. UNKNOWN is the catch-all.
- Role is a per-file signal (registry/signals.md #8, dimension D3 NAMING).
- Temporal operator: delta only (role changed from X to Y).

---

## Concept

A topic cluster extracted from a file's identifiers via TF-IDF + Louvain community detection. See `concept-extraction.md`.

```python
@dataclass(frozen=True)
class Concept:
    topic:    str          # The highest-TF-IDF token in the cluster ("auth", "cache", "payment")
    tokens:   list[str]    # All tokens in this Louvain community
    weight:   float        # Fraction of file's identifiers belonging to this concept, in [0, 1]
```

**Invariants**:
- `topic` is always one of the members of `tokens`.
- `weight > 0` for all concepts.
- Concepts are sorted by weight descending in `FileSemantics.concepts`.
- When a file has < 20 unique identifiers, concepts is empty (not a single fallback concept -- signals are set to defaults directly).

**Relationship to signals**:
- `concept_count` = `len(concepts)` (registry/signals.md #9).
- `concept_entropy` = Shannon entropy of concept weights (registry/signals.md #10).

---

## Symbol

A public API element exported by a file.

```python
@dataclass(frozen=True)
class Symbol:
    name:    str                        # "AuthService", "authenticate", "MAX_RETRIES"
    kind:    Literal["function", "class", "constant", "type"]
    params:  int | None                 # Parameter count for functions/methods; None for non-callables
```

**Classification rules**:
- `function`: Top-level function definitions not prefixed with `_`.
- `class`: Class definitions not prefixed with `_`.
- `constant`: Top-level assignments where the name is ALL_CAPS.
- `type`: Type aliases (Python `TypeAlias`, TypeScript `type`, Go `type`).
- Private symbols (prefixed with `_` in Python, unexported in Go) are excluded.

**Used for**: `docstring_coverage` computation (registry/signals.md #13) and `api_surface_delta` in SemanticDelta.

---

## ConsumedSymbol

Tracks which imported symbols are actually *used* in the file's code, not just imported.

```python
@dataclass(frozen=True)
class ConsumedSymbol:
    source_file:   str          # Resolved path of the file this was imported from
    symbols_used:  list[str]    # Subset of imported names that appear in function/class bodies
```

**How computed**:
1. For each `ImportDecl` in the file's `FileSyntax`, collect `import.names`.
2. Scan all function bodies and class bodies for references to those names.
3. Names that appear in bodies are "consumed"; names that are imported but never referenced are dead imports.

**Used by**: graph/ for edge weight (consumed symbols = meaningful coupling, unused imports = noise).

---

## Completeness

Measures how "finished" a file's implementation is.

```python
@dataclass(frozen=True)
class Completeness:
    stub_ratio:          float    # From IR1: fraction of functions that are stubs. [0, 1].
    implementation_gini: float    # From IR1: Gini coefficient of function body sizes. [0, 1].
    docstring_coverage:  float    # Documented public symbols / total public symbols. [0, 1].
    todo_density:        float    # (TODO + FIXME + HACK count) / lines. [0, inf).
```

**Field sources**:
- `stub_ratio`: Forwarded from `FileSyntax` computation (see registry/signals.md #6 for formula).
- `implementation_gini`: Forwarded from `FileSyntax` computation (see registry/signals.md #5 for formula).
- `docstring_coverage`: Computed by semantics/ from public Symbol list and docstring presence (registry/signals.md #13).
- `todo_density`: Computed by semantics/ via regex scan of raw source (registry/signals.md #12).

---

## SemanticDelta

The structured diff between two `FileSemantics` snapshots for the same file at different times.

```python
@dataclass(frozen=True)
class SemanticDelta:
    path:               str
    role_changed:       tuple[Role, Role] | None     # (old_role, new_role) or None if unchanged
    concepts_added:     list[Concept]                 # Concepts present in t2 but not t1
    concepts_removed:   list[Concept]                 # Concepts present in t1 but not t2
    concept_drift:      float                         # Cosine distance between concept TF-IDF vectors
    api_surface_delta:  int                           # len(public_api at t2) - len(public_api at t1)
    completeness_delta: float                         # stub_ratio(t2) - stub_ratio(t1)
```

**Concept matching**: Concepts are matched across snapshots by `topic` string. A concept is "added" if its topic appears in t2 but not t1. "Removed" if it appears in t1 but not t2. Concepts with the same topic but different weights or token sets are neither added nor removed -- the weight change contributes to `concept_drift`.

**concept_drift computation**:
```
v1 = TF-IDF vector of all concept tokens at t1
v2 = TF-IDF vector of all concept tokens at t2
concept_drift = 1 - cosine_similarity(v1, v2)
```

- `concept_drift = 0.0`: identical concept profile.
- `concept_drift > 0.5`: substantial shift in what the file is about.

**Cumulative concept drift** (time series, not stored in SemanticDelta):
```
cumulative_drift(f, T) = sum(concept_drift(f, t_i, t_{i+1}) for i in 0..T-1)
```

High cumulative drift = file has wandered far from its original purpose.

---

## Type Summary

| Type | Frozen | Serializable | Temporal operator |
|------|--------|-------------|-------------------|
| FileSemantics | Yes | Yes (to JSON/SQLite) | Full delta via SemanticDelta |
| Role | Yes (enum) | Yes (string value) | Delta only (changed from/to) |
| Concept | Yes | Yes | Matched by topic across snapshots |
| Symbol | Yes | Yes | Delta (added/removed from public API) |
| ConsumedSymbol | Yes | Yes | Delta (new/dropped consumption) |
| Completeness | Yes | Yes | All fields support delta, velocity, trend |
| SemanticDelta | Yes | Yes | N/A (it IS a delta) |
