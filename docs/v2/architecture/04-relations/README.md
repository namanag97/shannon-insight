# Relations

Relations are typed edges between entities. There are **8 relation types**.

---

## Relation Model

```python
class RelationType(Enum):
    """All 8 relation types."""

    IMPORTS = "imports"               # File → File
    COCHANGES_WITH = "cochanges"      # File → File (symmetric, weighted)
    SIMILAR_TO = "similar"            # File → File (weighted)
    AUTHORED_BY = "authored"          # File → Author
    IN_MODULE = "in_module"           # File → Module
    CONTAINS = "contains"             # Module → File, Codebase → Module
    DEPENDS_ON = "depends"            # Module → Module
    CLONED_FROM = "cloned"            # File → File (weighted)

@dataclass
class Relation:
    type: RelationType
    source: EntityId
    target: EntityId
    weight: float = 1.0
    metadata: dict = field(default_factory=dict)
```

---

## Relation Types

### 1. IMPORTS

Static dependency between files.

| Property | Value |
|----------|-------|
| **Source** | FILE |
| **Target** | FILE |
| **Directed** | Yes |
| **Weight** | 1.0 (exists or not) |
| **Collector** | DependencyCollector |

```python
Relation(
    type=RelationType.IMPORTS,
    source=EntityId(FILE, "src/auth/login.py"),
    target=EntityId(FILE, "src/db/connection.py"),
    weight=1.0,
)
```

**Derived from**: Import statements in source code.

---

### 2. COCHANGES_WITH

Files that change together in commits.

| Property | Value |
|----------|-------|
| **Source** | FILE |
| **Target** | FILE |
| **Directed** | No (symmetric) |
| **Weight** | Lift score (0, ∞) |
| **Collector** | CoChangeCollector |

```python
Relation(
    type=RelationType.COCHANGES_WITH,
    source=EntityId(FILE, "src/auth/login.py"),
    target=EntityId(FILE, "src/auth/session.py"),
    weight=3.5,  # lift
    metadata={
        "count": 45,       # commits together
        "confidence": 0.7,
    }
)
```

**Weight formula**:
```
lift(A, B) = P(A ∩ B) / (P(A) × P(B))

lift = 1: independent (random co-occurrence)
lift > 2: significant co-change
lift > 5: strong coupling
```

---

### 3. SIMILAR_TO

Semantic similarity between files (concept overlap).

| Property | Value |
|----------|-------|
| **Source** | FILE |
| **Target** | FILE |
| **Directed** | No (symmetric) |
| **Weight** | Cosine similarity [0, 1] |
| **Collector** | SemanticCollector |

```python
Relation(
    type=RelationType.SIMILAR_TO,
    source=EntityId(FILE, "src/auth/login.py"),
    target=EntityId(FILE, "src/auth/oauth.py"),
    weight=0.85,  # cosine similarity
    metadata={
        "method": "tfidf",
        "shared_concepts": ["auth", "user", "token"],
    }
)
```

**Note**: Only top-k most similar pairs stored (k = 10 per file).

---

### 4. AUTHORED_BY

Authorship relationship.

| Property | Value |
|----------|-------|
| **Source** | FILE |
| **Target** | AUTHOR |
| **Directed** | Yes |
| **Weight** | 1.0 |
| **Collector** | GitCollector |

```python
Relation(
    type=RelationType.AUTHORED_BY,
    source=EntityId(FILE, "src/auth/login.py"),
    target=EntityId(AUTHOR, "alice@example.com"),
    weight=1.0,
    metadata={
        "commits": 25,
        "lines_added": 500,
        "first_commit": "2023-01-15",
        "last_commit": "2024-02-01",
    }
)
```

---

### 5. IN_MODULE

File membership in module.

| Property | Value |
|----------|-------|
| **Source** | FILE |
| **Target** | MODULE |
| **Directed** | Yes |
| **Weight** | 1.0 |
| **Collector** | ModuleCollector |

```python
Relation(
    type=RelationType.IN_MODULE,
    source=EntityId(FILE, "src/auth/login.py"),
    target=EntityId(MODULE, "auth"),
    weight=1.0,
)
```

---

### 6. CONTAINS

Containment (inverse of IN_MODULE).

| Property | Value |
|----------|-------|
| **Source** | MODULE or CODEBASE |
| **Target** | FILE or MODULE |
| **Directed** | Yes |
| **Weight** | 1.0 |
| **Collector** | ModuleCollector |

```python
# Module contains file
Relation(
    type=RelationType.CONTAINS,
    source=EntityId(MODULE, "auth"),
    target=EntityId(FILE, "src/auth/login.py"),
)

# Codebase contains module
Relation(
    type=RelationType.CONTAINS,
    source=EntityId(CODEBASE, "/repo"),
    target=EntityId(MODULE, "auth"),
)
```

---

### 7. DEPENDS_ON

Module-level dependency (aggregated from IMPORTS).

| Property | Value |
|----------|-------|
| **Source** | MODULE |
| **Target** | MODULE |
| **Directed** | Yes |
| **Weight** | Edge count |
| **Collector** | DependencyCollector |

```python
Relation(
    type=RelationType.DEPENDS_ON,
    source=EntityId(MODULE, "auth"),
    target=EntityId(MODULE, "database"),
    weight=12,  # 12 import edges from auth → database
    metadata={
        "files_using": ["login.py", "session.py", "permissions.py"],
    }
)
```

---

### 8. CLONED_FROM

Copy-paste clone detection via NCD.

| Property | Value |
|----------|-------|
| **Source** | FILE |
| **Target** | FILE |
| **Directed** | No (symmetric) |
| **Weight** | 1 - NCD similarity [0, 1] |
| **Collector** | CloneDeriver |

```python
Relation(
    type=RelationType.CLONED_FROM,
    source=EntityId(FILE, "src/handlers/user.py"),
    target=EntityId(FILE, "src/handlers/admin.py"),
    weight=0.85,  # 85% similar
    metadata={
        "ncd": 0.15,  # Normalized Compression Distance
        "method": "zlib",
    }
)
```

**Clone threshold**: NCD < 0.3 (weight > 0.7).

---

## RelationGraph

```python
class RelationGraph:
    """Queryable collection of all relations."""

    def __init__(self):
        self._edges: list[Relation] = []
        self._by_type: dict[RelationType, list[Relation]] = {}
        self._by_source: dict[EntityId, list[Relation]] = {}
        self._by_target: dict[EntityId, list[Relation]] = {}

    def add(self, relation: Relation) -> None:
        """Add a relation."""
        self._edges.append(relation)
        self._by_type.setdefault(relation.type, []).append(relation)
        self._by_source.setdefault(relation.source, []).append(relation)
        self._by_target.setdefault(relation.target, []).append(relation)

    def by_type(self, type: RelationType) -> list[Relation]:
        """Get all relations of a type."""
        return self._by_type.get(type, [])

    def outgoing(
        self,
        entity: EntityId,
        type: RelationType | None = None,
    ) -> list[Relation]:
        """Get outgoing relations from entity."""
        rels = self._by_source.get(entity, [])
        if type:
            rels = [r for r in rels if r.type == type]
        return rels

    def incoming(
        self,
        entity: EntityId,
        type: RelationType | None = None,
    ) -> list[Relation]:
        """Get incoming relations to entity."""
        rels = self._by_target.get(entity, [])
        if type:
            rels = [r for r in rels if r.type == type]
        return rels

    def has(
        self,
        source: EntityId,
        type: RelationType,
        target: EntityId,
    ) -> bool:
        """Check if relation exists."""
        for r in self.outgoing(source, type):
            if r.target == target:
                return True
        return False

    def weight(
        self,
        source: EntityId,
        type: RelationType,
        target: EntityId,
    ) -> float:
        """Get relation weight (0 if not exists)."""
        for r in self.outgoing(source, type):
            if r.target == target:
                return r.weight
        return 0.0

    def matrix(
        self,
        type: RelationType,
        entities: list[EntityId] | None = None,
    ) -> tuple[list[EntityId], np.ndarray]:
        """
        Build adjacency matrix for relation type.
        Returns (entity_list, matrix).
        """
        if entities is None:
            # Gather all entities involved in this relation type
            entities = set()
            for r in self.by_type(type):
                entities.add(r.source)
                entities.add(r.target)
            entities = sorted(entities, key=lambda e: e.key)

        idx = {e: i for i, e in enumerate(entities)}
        n = len(entities)
        matrix = np.zeros((n, n))

        for r in self.by_type(type):
            if r.source in idx and r.target in idx:
                i, j = idx[r.source], idx[r.target]
                matrix[i, j] = r.weight

        return entities, matrix
```

---

## Relation Summary

| # | Type | Source → Target | Symmetric | Weighted | Phase |
|---|------|-----------------|-----------|----------|-------|
| 1 | IMPORTS | File → File | No | No | 0 |
| 2 | COCHANGES_WITH | File → File | Yes | Yes (lift) | 3 |
| 3 | SIMILAR_TO | File → File | Yes | Yes (cosine) | 2 |
| 4 | AUTHORED_BY | File → Author | No | No | 3 |
| 5 | IN_MODULE | File → Module | No | No | 4 |
| 6 | CONTAINS | Module → File | No | No | 4 |
| 7 | DEPENDS_ON | Module → Module | No | Yes (count) | 4 |
| 8 | CLONED_FROM | File → File | Yes | Yes (sim) | 3 |

---

## Relations Used by Finders

| Finder | Relations Used |
|--------|----------------|
| HIDDEN_COUPLING | IMPORTS (absent), COCHANGES_WITH (present) |
| DEAD_DEPENDENCY | IMPORTS (present), COCHANGES_WITH (absent) |
| ACCIDENTAL_COUPLING | IMPORTS (present), concept overlap low |
| CONWAY_VIOLATION | DEPENDS_ON, AUTHORED_BY |
| COPY_PASTE_CLONE | CLONED_FROM |
| BOUNDARY_MISMATCH | IN_MODULE, community assignments |
| LAYER_VIOLATION | DEPENDS_ON |
| WEAK_LINK | IMPORTS (neighbors) |
