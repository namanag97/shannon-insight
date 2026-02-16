# Stage 3: Model

Assemble collected data into the unified FactStore.

---

## FactStore Structure

```python
@dataclass
class FactStore:
    """The central data structure: entities + signals + relations."""

    # Identity
    root: Path
    timestamp: datetime
    tier: Tier

    # Core data
    entities: dict[EntityId, Entity]
    signals: SignalStore
    relations: RelationGraph

    # Convenience indexes
    _files: list[EntityId] | None = None
    _modules: list[EntityId] | None = None
```

---

## Entity Construction

### From Collectors

```python
def build_entities(
    ctx: RuntimeContext,
    file_metrics: list[FileMetrics],
    modules: list[str],  # Detected or configured
) -> dict[EntityId, Entity]:
    """
    Build entity hierarchy from collected data.
    """
    entities: dict[EntityId, Entity] = {}

    # Codebase (root)
    codebase_id = EntityId(EntityType.CODEBASE, str(ctx.root))
    entities[codebase_id] = Entity(id=codebase_id, parent=None)

    # Modules
    for mod_name in modules:
        mod_id = EntityId(EntityType.MODULE, mod_name)
        entities[mod_id] = Entity(id=mod_id, parent=codebase_id)

    # Files
    for fm in file_metrics:
        file_id = EntityId(EntityType.FILE, fm.path)
        parent_mod = detect_module(fm.path, modules)
        parent_id = EntityId(EntityType.MODULE, parent_mod) if parent_mod else codebase_id
        entities[file_id] = Entity(id=file_id, parent=parent_id)

    # Authors (from git)
    for author_email in git_history.authors:
        author_id = EntityId(EntityType.AUTHOR, author_email)
        entities[author_id] = Entity(id=author_id, parent=None)

    return entities
```

### Module Detection

```python
def detect_modules(file_metrics: list[FileMetrics]) -> list[str]:
    """
    Detect modules from directory structure.
    Module = top-level directory containing source files.

    Examples:
      src/auth/login.py → "auth"
      src/auth/models.py → "auth"
      src/graph/builder.py → "graph"
      tests/test_auth.py → "tests"
    """
    modules: set[str] = set()

    for fm in file_metrics:
        parts = Path(fm.path).parts
        if len(parts) >= 2:
            # Skip common prefixes
            if parts[0] in ("src", "lib", "app"):
                if len(parts) >= 3:
                    modules.add(parts[1])
            else:
                modules.add(parts[0])

    return sorted(modules)
```

---

## Signal Loading

### From Raw Measurements

```python
def load_signals_from_metrics(
    store: FactStore,
    file_metrics: list[FileMetrics],
    timestamp: datetime,
) -> None:
    """
    Load raw signals from FileMetrics into SignalStore.
    """
    for fm in file_metrics:
        entity = EntityId(EntityType.FILE, fm.path)

        store.signals.set(entity, Signal.LINES, fm.lines, timestamp)
        store.signals.set(entity, Signal.FUNCTION_COUNT, fm.function_count, timestamp)
        store.signals.set(entity, Signal.CLASS_COUNT, fm.class_count, timestamp)
        store.signals.set(entity, Signal.IMPORT_COUNT, fm.import_count, timestamp)
```

### From FileSyntax (Phase 1+)

```python
def load_signals_from_syntax(
    store: FactStore,
    file_syntax: dict[str, FileSyntax],
    timestamp: datetime,
) -> None:
    """
    Load syntax-derived signals.
    """
    for path, syntax in file_syntax.items():
        entity = EntityId(EntityType.FILE, path)

        store.signals.set(entity, Signal.MAX_NESTING, syntax.max_nesting, timestamp)

        # impl_gini
        if syntax.functions:
            body_tokens = sorted(f.body_tokens for f in syntax.functions)
            gini = compute_gini(body_tokens)
            store.signals.set(entity, Signal.IMPL_GINI, gini, timestamp)
        else:
            store.signals.set(entity, Signal.IMPL_GINI, 0.0, timestamp)

        # stub_ratio
        if syntax.functions:
            stubs = sum(1 for f in syntax.functions if f.is_stub)
            ratio = stubs / len(syntax.functions)
            store.signals.set(entity, Signal.STUB_RATIO, ratio, timestamp)
        else:
            store.signals.set(entity, Signal.STUB_RATIO, 0.0, timestamp)
```

### From ChurnSeries (Phase 3+)

```python
def load_signals_from_churn(
    store: FactStore,
    churn: dict[str, ChurnSeries],
    timestamp: datetime,
) -> None:
    """
    Load temporal signals from ChurnSeries.
    """
    for path, series in churn.items():
        entity = EntityId(EntityType.FILE, path)

        store.signals.set(entity, Signal.TOTAL_CHANGES, series.total_changes, timestamp)
        store.signals.set(entity, Signal.CHURN_TRAJECTORY, series.churn_trajectory, timestamp)
        store.signals.set(entity, Signal.CHURN_SLOPE, series.churn_slope, timestamp)
        store.signals.set(entity, Signal.CHURN_CV, series.churn_cv, timestamp)
        store.signals.set(entity, Signal.BUS_FACTOR, series.bus_factor, timestamp)
        store.signals.set(entity, Signal.AUTHOR_ENTROPY, series.author_entropy, timestamp)
        store.signals.set(entity, Signal.FIX_RATIO, series.fix_ratio, timestamp)
        store.signals.set(entity, Signal.REFACTOR_RATIO, series.refactor_ratio, timestamp)
```

---

## Relation Loading

```python
def load_relations(
    store: FactStore,
    dep_graph: DependencyGraph,
    cochange: CoChangeMatrix,
    authored_by: list[tuple[str, str, int]],  # (path, email, commits)
) -> None:
    """
    Load all relations into RelationGraph.
    """
    # IMPORTS
    for source, targets in dep_graph.edges.items():
        for target in targets:
            store.relations.add(Relation(
                type=RelationType.IMPORTS,
                source=EntityId(EntityType.FILE, source),
                target=EntityId(EntityType.FILE, target),
            ))

    # COCHANGES_WITH
    for (a, b), lift in cochange.pairs.items():
        if lift > 0:  # Only store non-zero
            store.relations.add(Relation(
                type=RelationType.COCHANGES_WITH,
                source=EntityId(EntityType.FILE, a),
                target=EntityId(EntityType.FILE, b),
                weight=lift,
            ))

    # AUTHORED_BY
    for path, email, commits in authored_by:
        store.relations.add(Relation(
            type=RelationType.AUTHORED_BY,
            source=EntityId(EntityType.FILE, path),
            target=EntityId(EntityType.AUTHOR, email),
            metadata={"commits": commits},
        ))

    # IN_MODULE (from entity hierarchy)
    for entity_id, entity in store.entities.items():
        if entity_id.type == EntityType.FILE and entity.parent:
            if entity.parent.type == EntityType.MODULE:
                store.relations.add(Relation(
                    type=RelationType.IN_MODULE,
                    source=entity_id,
                    target=entity.parent,
                ))

    # CONTAINS (inverse of IN_MODULE)
    for entity_id, entity in store.entities.items():
        if entity_id.type == EntityType.FILE and entity.parent:
            store.relations.add(Relation(
                type=RelationType.CONTAINS,
                source=entity.parent,
                target=entity_id,
            ))
```

---

## Validation

After model construction, validate integrity:

```python
def validate_fact_store(store: FactStore) -> list[str]:
    """
    Validate FactStore integrity. Returns list of warnings.
    """
    warnings = []

    # Every file entity should have at least LINES signal
    for entity_id in store.files():
        if not store.signals.has(entity_id, Signal.LINES):
            warnings.append(f"File {entity_id.key} missing LINES signal")

    # Every IMPORTS relation should have valid source and target
    for rel in store.relations.by_type(RelationType.IMPORTS):
        if rel.source not in store.entities:
            warnings.append(f"IMPORTS source not in entities: {rel.source}")
        if rel.target not in store.entities:
            warnings.append(f"IMPORTS target not in entities: {rel.target}")

    # Modules should have at least one file
    for entity_id in store.modules():
        files = store.relations.incoming(entity_id, RelationType.IN_MODULE)
        if not files:
            warnings.append(f"Module {entity_id.key} has no files")

    return warnings
```

---

## Memory Considerations

For large codebases (10k+ files):

```python
# Estimated memory per file
MEMORY_PER_FILE = {
    "entity": 200,        # bytes
    "signals": 36 * 8,    # 36 signals × 8 bytes each
    "relations_avg": 5 * 100,  # ~5 relations × 100 bytes each
}

# Total per file: ~800 bytes
# 10k files: ~8 MB
# 100k files: ~80 MB

# Optimization: Don't store zero-valued signals
# Optimization: Use interned strings for paths
# Optimization: Lazy-load historical signals from disk
```
