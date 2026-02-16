# Entities

Entities are the things we analyze. They form a hierarchy.

---

## Entity Hierarchy

```
Codebase (root)
    │
    ├── Module
    │       │
    │       └── File
    │               │
    │               └── Symbol (future)
    │
    ├── Author
    │
    └── Commit
```

---

## Entity Types

```python
class EntityType(Enum):
    CODEBASE = "codebase"    # The repository root
    MODULE = "module"        # Logical grouping (directory, package)
    FILE = "file"            # Source file
    SYMBOL = "symbol"        # Function, class (future)
    AUTHOR = "author"        # Git contributor
    COMMIT = "commit"        # Git commit
```

---

## EntityId

Unique identifier for any entity:

```python
@dataclass(frozen=True)
class EntityId:
    type: EntityType
    key: str  # Unique within type

    def __hash__(self) -> int:
        return hash((self.type, self.key))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityId):
            return False
        return self.type == other.type and self.key == other.key
```

### Key Conventions

| Type | Key Format | Example |
|------|------------|---------|
| CODEBASE | Absolute path | `/Users/dev/myproject` |
| MODULE | Module name | `auth`, `graph`, `tests` |
| FILE | Relative path from root | `src/auth/login.py` |
| SYMBOL | `file:line:name` | `src/auth/login.py:45:authenticate` |
| AUTHOR | Email | `alice@example.com` |
| COMMIT | Short SHA | `abc1234` |

---

## Entity

```python
@dataclass
class Entity:
    id: EntityId
    parent: EntityId | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def type(self) -> EntityType:
        return self.id.type

    @property
    def key(self) -> str:
        return self.id.key
```

### Parent Relationships

| Entity Type | Parent Type | Example |
|-------------|-------------|---------|
| CODEBASE | None | Root has no parent |
| MODULE | CODEBASE | `auth` → codebase |
| FILE | MODULE or CODEBASE | `src/auth/login.py` → `auth` |
| SYMBOL | FILE | `authenticate` → `src/auth/login.py` |
| AUTHOR | None | Authors are top-level |
| COMMIT | None | Commits are top-level |

---

## Detailed Type Specifications

### 1. CODEBASE

The root entity representing the entire repository.

```python
codebase = Entity(
    id=EntityId(EntityType.CODEBASE, "/Users/dev/myproject"),
    parent=None,
    metadata={
        "name": "myproject",
        "languages": ["python", "typescript"],
        "file_count": 150,
    }
)
```

**Signals on CODEBASE** (11 signals, #52-62):
- modularity, fiedler_value, spectral_gap, cycle_count
- centrality_gini, orphan_ratio, phantom_ratio, glue_deficit
- wiring_score, architecture_health, codebase_health

---

### 2. MODULE

A logical grouping of files. Detected from directory structure or explicit configuration.

```python
module = Entity(
    id=EntityId(EntityType.MODULE, "auth"),
    parent=EntityId(EntityType.CODEBASE, "/Users/dev/myproject"),
    metadata={
        "path": "src/auth",
        "detection_method": "directory",  # or "louvain", "config"
    }
)
```

**Detection Methods**:

1. **Directory-based** (default): Top-level directories under src/lib/app
2. **Louvain community**: Detected from dependency graph clustering
3. **Explicit config**: Defined in `shannon-insight.toml`

**Signals on MODULE** (15 signals, #37-51):
- cohesion, coupling, instability, abstractness, main_seq_distance
- boundary_alignment, layer_violation_count, role_consistency
- velocity, coordination_cost, knowledge_gini, module_bus_factor
- mean_cognitive_load, file_count, health_score

---

### 3. FILE

A source code file.

```python
file = Entity(
    id=EntityId(EntityType.FILE, "src/auth/login.py"),
    parent=EntityId(EntityType.MODULE, "auth"),
    metadata={
        "language": "python",
        "size_bytes": 4500,
    }
)
```

**Path Normalization**:
- Always relative to codebase root
- Forward slashes on all platforms
- No leading `./`

**Signals on FILE** (36 signals, #1-36):
- lines, function_count, class_count, max_nesting, impl_gini, stub_ratio, import_count
- role, concept_count, concept_entropy, naming_drift, todo_density, docstring_coverage
- pagerank, betweenness, in_degree, out_degree, blast_radius_size, depth, is_orphan
- phantom_import_count, broken_call_count, community, compression_ratio, semantic_coherence, cognitive_load
- total_changes, churn_trajectory, churn_slope, churn_cv, bus_factor, author_entropy, fix_ratio, refactor_ratio
- risk_score, wiring_quality

---

### 4. SYMBOL (Future)

Function, class, or method within a file.

```python
symbol = Entity(
    id=EntityId(EntityType.SYMBOL, "src/auth/login.py:45:authenticate"),
    parent=EntityId(EntityType.FILE, "src/auth/login.py"),
    metadata={
        "kind": "function",  # or "class", "method"
        "line": 45,
        "name": "authenticate",
    }
)
```

**Status**: Not implemented in v2 phases 0-7. Reserved for future granularity.

---

### 5. AUTHOR

A git contributor identified by email.

```python
author = Entity(
    id=EntityId(EntityType.AUTHOR, "alice@example.com"),
    parent=None,
    metadata={
        "name": "Alice Smith",
        "first_commit": "2023-01-15",
        "last_commit": "2024-02-10",
        "total_commits": 150,
    }
)
```

**Identity Resolution**:
- Authors are keyed by email (normalized lowercase)
- Multiple emails for same person are NOT merged (future: author aliasing)

---

### 6. COMMIT

A git commit.

```python
commit = Entity(
    id=EntityId(EntityType.COMMIT, "abc1234"),
    parent=None,
    metadata={
        "full_sha": "abc1234567890abcdef",
        "author_email": "alice@example.com",
        "timestamp": "2024-02-10T14:30:00Z",
        "subject": "Fix authentication bug",
        "files_changed": 3,
    }
)
```

**Status**: Commits are tracked for co-change analysis but don't have signals computed on them directly.

---

## Entity Operations

### Construction

```python
def file_entity(path: str, module: str | None = None) -> Entity:
    """Create a file entity."""
    parent = EntityId(EntityType.MODULE, module) if module else None
    return Entity(
        id=EntityId(EntityType.FILE, path),
        parent=parent,
    )

def module_entity(name: str, codebase_path: str) -> Entity:
    """Create a module entity."""
    return Entity(
        id=EntityId(EntityType.MODULE, name),
        parent=EntityId(EntityType.CODEBASE, codebase_path),
    )
```

### Traversal

```python
def children(store: FactStore, entity: EntityId) -> list[EntityId]:
    """Get direct children of an entity."""
    return [e.id for e in store.entities.values() if e.parent == entity]

def ancestors(store: FactStore, entity: EntityId) -> list[EntityId]:
    """Get all ancestors up to root."""
    result = []
    current = store.entities.get(entity)
    while current and current.parent:
        result.append(current.parent)
        current = store.entities.get(current.parent)
    return result

def descendants(store: FactStore, entity: EntityId) -> list[EntityId]:
    """Get all descendants (recursive)."""
    result = []
    queue = children(store, entity)
    while queue:
        child = queue.pop(0)
        result.append(child)
        queue.extend(children(store, child))
    return result
```

---

## Entity Count by Phase

| Phase | CODEBASE | MODULE | FILE | SYMBOL | AUTHOR | COMMIT |
|-------|----------|--------|------|--------|--------|--------|
| 0 | 1 | 0 | n | 0 | 0 | 0 |
| 1 | 1 | 0 | n | 0 | 0 | 0 |
| 2 | 1 | 0 | n | 0 | 0 | 0 |
| 3 | 1 | 0 | n | 0 | m | c |
| 4 | 1 | k | n | 0 | m | c |
| 5+ | 1 | k | n | 0 | m | c |

Where:
- n = file count
- k = module count (typically 5-20)
- m = unique author count
- c = commit count in history window
