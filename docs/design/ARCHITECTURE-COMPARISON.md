# Current vs New Architecture: Benefits & Innovations

**Document Version:** 1.0
**Date:** 2026-02-17

---

## Executive Summary

| Aspect | Current Architecture | New Architecture | Impact |
|---------|-------------------|-------------------|---------|
| **Storage** | Dual (AnalysisStore + FactStore) | Unified (EntityStore) | ✅ Eliminates synchronization complexity |
| **Entity Identity** | Path-based, breaks on rename | Stable EntityId (type + key) | ✅ Tracks files across renames/moves |
| **Signal Types** | Scalar only, weakly typed | Multi-type (SCALAR, TIME_SERIES, GRAPH) | ✅ Richer signals, type safety |
| **Validation** | Minimal, scattered | At every layer boundary | ✅ Early error detection |
| **Data Flow** | Mixed concerns, unclear | Layered with clear contracts | ✅ Predictable, testable |
| **Immutability** | Mutable, fragile | Frozen dataclasses | ✅ Thread-safe, hashable |
| **Findings** | No stable identity | Hash-based identity keys | ✅ Lifecycle tracking |
| **Temporal** | Coarse, file-level only | Multi-granularity, line-level | ✅ Advanced temporal analysis |
| **Graph** | Untyped edges, scattered dicts | Typed Edge objects, efficient lookups | ✅ Explicit semantics, performance |
| **Persistence** | Flat dicts, no diff support | Structured Snapshot with SnapshotDiff | ✅ Efficient comparison, trends |

---

## 1. Storage: Dual vs Unified

### Current State

**Dual Storage Problem:**
```python
# OLD: AnalysisStore (slots)
class AnalysisStore:
    file_syntax: Slot[Dict[str, FileSyntax]]
    structural: Slot[CodebaseAnalysis]
    git_history: Slot[GitHistory]
    # ... 12+ more slots

# NEW: FactStore (v2)
class FactStore:
    entities: Dict[EntityId, Entity]
    signals: Dict[EntityId, Dict[Signal, Any]]
    relations: Dict[RelationType, List[Tuple[EntityId, EntityId, float]]]
```

**Problems:**
- Confusion: Which store to use?
- Synchronization: `_sync_entities()` manually bridges them
- Inconsistency: Data can diverge between stores
- Maintenance: Need to maintain both
- Testing: Need to test both
- Complexity: 2 APIs to learn

### New Architecture

**Unified EntityStore:**
```python
# NEW: Single unified storage
class EntityStore:
    entities: Dict[EntityId, Entity]
    signals: Dict[EntityId, Dict[str, SignalValue]]
    relations: RelationGraph  # Efficient adjacency lookups
```

**Benefits:**
- ✅ **Single source of truth**: No synchronization needed
- ✅ **Simpler API**: One interface for all data
- ✅ **No divergence**: Can't have inconsistent data
- ✅ **Easier testing**: Mock one store instead of two
- ✅ **Better performance**: No bridge overhead
- ✅ **Clearer code**: No `_sync_entities()` hacks

**Innovation:** Unified storage with typed signals and efficient relation graph.

---

## 2. Entity Identity: Path-based vs Stable

### Current State

**Path-based Identity:**
```python
# Files identified only by path
file_signals["src/auth/login.py"] = {...}

# PROBLEM: If file is renamed, identity breaks!
# src/auth/login.py → src/auth/user/login.py
# Now you have TWO entities with NO connection
```

**Problems:**
- Can't track files across renames
- Can't analyze file lineage
- Historical analysis impossible
- Git blame shows old paths, can't map

### New Architecture

**Stable EntityId:**
```python
# EntityId: Stable identity across renames
@dataclass(frozen=True)
class EntityId:
    type: EntityType  # FILE, MODULE, AUTHOR, COMMIT
    key: str  # Stable identifier (survives renames)

# Track lineage across renames
class EntityLineage:
    canonical_id: EntityId
    timeline: List[Tuple[int, str]]  # [(timestamp, alias), ...]
    # [(1234567890, "src/auth/login.py"),
    #  (1234568000, "src/auth/user/login.py")]
```

**Benefits:**
- ✅ **Rename tracking**: File identity survives moves/renames
- ✅ **Historical analysis**: Reconstruct past states
- ✅ **Git blame mapping**: Map old paths to current identity
- ✅ **Lineage queries**: "Show file history across all renames"

**Innovation:** Canonical identity with lineage tracking, similar to Git's object model.

---

## 3. Signal Types: Scalar-only vs Multi-type

### Current State

**Scalar-only Signals:**
```python
# Signal enum has names but no value types
class Signal(Enum):
    PAGERANK = "pagerank"  # Just a string name!
    TOTAL_CHANGES = "total_changes"  # No type info

# Values stored as Any (no validation)
signals: Dict[Signal, Any] = {
    Signal.PAGERANK: 0.95,  # What if someone puts a string?
    Signal.TOTAL_CHANGES: "high",  # Type error at runtime!
}
```

**Problems:**
- No type safety
- No validation
- Can't represent time series
- Can't represent graph signals
- Runtime type errors
- No auto-documentation

### New Architecture

**Typed Signal Values:**
```python
# Signal definition with type
@dataclass(frozen=True)
class SignalDef:
    name: str
    dtype: Type  # Expected value type (float, int, TimeSeries, etc.)
    scope: SignalScope  # FILE, MODULE, CODEBASE
    value_type: SignalValueType  # SCALAR, TIME_SERIES, GRAPH, SET
    polarity: SignalPolarity  # HIGH_IS_BAD, HIGH_IS_GOOD

# Registry enforces single definition
SIGNAL_REGISTRY: Dict[str, SignalDef] = {}

# Typed signal value with validation
@dataclass(frozen=True)
class SignalValue:
    signal_def: SignalDef
    value: SignalValue  # Validated against dtype
    computed_at: datetime

# Multi-type signal values
SignalValue = Union[
    float,        # SCALAR
    int,          # SCALAR
    str,          # CATEGORICAL
    TimeSeries,    # TIME_SERIES (structured)
    GraphSignal,   # GRAPH (blast_radius, community)
    Set[str],      # SET (similar_files, co_change_partners)
]
```

**Benefits:**
- ✅ **Type safety**: Compile-time and runtime validation
- ✅ **Richer signals**: Time series, graph, set types
- ✅ **Self-documenting**: dtype, scope, polarity in definition
- ✅ **Early errors**: Invalid types caught immediately
- ✅ **Better IDE support**: Autocomplete works on typed values

**Innovation:** Multi-type signal system with runtime validation and metadata.

---

## 4. Validation: Minimal vs At Every Boundary

### Current State

**Minimal Validation:**
```python
# Validation scattered, inconsistent
class FileSyntax:
    path: str  # No validation that it's a valid path
    functions: List[FunctionDef]  # No validation of function boundaries
    classes: List[ClassDef]  # No validation of class names

# Signal values unchecked
store.set_signal(Signal.PAGERANK, "high")  # Type error!
```

**Problems:**
- Invalid data propagates through pipeline
- Errors detected late (hard to debug)
- No guarantees of data integrity
- Silent failures possible

### New Architecture

**Validation at Every Boundary:**
```python
# Validation in every layer
class FileAST:
    def validate(self) -> bool:
        # Check all functions have valid names
        for fn in self.functions:
            if not fn.name or not fn.name.isidentifier():
                raise ValueError(f"Invalid function name: {fn.name}")
            if fn.start_line >= fn.end_line:
                raise ValueError(f"Invalid function bounds: {fn}")

# Signal validation
def set_signal(self, entity_id: EntityId, signal_value: SignalValue):
    # Validate signal value against definition
    if not signal_value.signal_def.validate_value(signal_value.value):
        raise ValueError(f"Invalid value {signal_value.value} for signal {signal_value.signal_def.name}")

# 8 validation checkpoints
1. After Scanning: Validate FileAST
2. After Graph: Validate DependencyGraph (no self-loops)
3. After Graph Analysis: Validate GraphMetrics (PageRank sums to 1.0)
4. After Semantics: Validate FileSemantics (concept weights sum to 1.0)
5. After Temporal: Validate TimeSeries (sorted timestamps)
6. After Infrastructure: Validate EntityStore (signals registered)
7. After Insights: Validate Finding (severity [0,1])
8. After Persistence: Validate Snapshot (integrity)
```

**Benefits:**
- ✅ **Early error detection**: Fail fast, fail clearly
- ✅ **Clear error messages**: Know exactly what's wrong
- ✅ **Data integrity guarantees**: Invalid data can't propagate
- ✅ **Easier debugging**: Error location is known

**Innovation:** Comprehensive validation checkpoint system.

---

## 5. Data Flow: Mixed Concerns vs Layered Contracts

### Current State

**Mixed Concerns:**
```python
# FileSyntax contains AST + metrics
class FileSyntax:
    functions: List[FunctionDef]  # AST data
    classes: List[ClassDef]  # AST data
    imports: List[ImportDecl]  # AST data
    _lines: int  # Computed metric (cached)
    _tokens: int  # Computed metric (cached)
    _complexity: float  # Computed metric (cached)

    # Properties mix AST and metrics
    @property
    def function_count(self) -> int:
        return len(self.functions)  # Computed from AST

    @property
    def impl_gini(self) -> float:
        # Complex computation mixed with data
        values = sorted(fn.body_tokens for fn in self.functions)
        n = len(values)
        total = sum(values)
        # ... 10 more lines of computation
```

**Problems:**
- Hard to understand what's data vs computation
- No clear layer boundaries
- Hard to test in isolation
- Difficult to cache selectively
- Unclear what's input vs output

### New Architecture

**Layered with Clear Contracts:**
```python
# Layer 1: Raw AST (immutable)
@dataclass(frozen=True)
class FileAST:
    file_id: EntityId
    path: str
    language: Language
    functions: List[FunctionNode]  # Only AST data
    classes: List[ClassNode]  # Only AST data
    imports: List[ImportNode]  # Only AST data

# Layer 2: Signals (computed from AST)
# Stored separately in EntityStore
signals = {
    entity_id: {
        "function_count": SignalValue(signal_def, len(file_ast.functions)),
        "impl_gini": SignalValue(signal_def, compute_gini(file_ast)),
    }
}

# Clear transformation functions
def compute_scanning_signals(file_ast: FileAST) -> Dict[str, SignalValue]:
    """Transform AST to signals."""
    return {
        "function_count": SignalValue(..., len(file_ast.functions)),
        "class_count": SignalValue(..., len(file_ast.classes)),
        "max_nesting": SignalValue(..., file_ast.max_nesting),
    }

# Layer protocols define contracts
class ScanningProtocol(Protocol):
    def scan_file(self, file_path: Path) -> FileAST: ...
    def validate_input(self, file_path: Path) -> bool: ...
    def validate_output(self, ast: FileAST) -> bool: ...

class AnalysisProtocol(Protocol):
    def analyze(self, input_data: FileAST, store: EntityStore) -> Dict[str, SignalValue]: ...
    def validate_input(self, input_data: FileAST) -> bool: ...
    def validate_output(self, signals: Dict[str, SignalValue]) -> bool: ...
```

**Benefits:**
- ✅ **Clear separation**: AST vs signals distinct
- ✅ **Testable layers**: Each layer testable in isolation
- ✅ **Composable**: Can replace layers independently
- ✅ **Predictable**: Input/output contracts explicit
- ✅ **Cachable**: Can cache signals without AST

**Innovation:** Protocol-based layer interfaces with input/output contracts.

---

## 6. Immutability: Mutable vs Frozen

### Current State

**Mutable Data:**
```python
@dataclass
class FileSyntax:
    path: str  # Mutable!
    functions: List[FunctionDef]  # Mutable list!
    classes: List[ClassDef]  # Mutable list!
    _lines: int  # Mutable!

# PROBLEM: Can accidentally mutate
fs = FileSyntax(...)
fs.path = "different/path.py"  # Accidentally changed!
fs.functions.append(new_function)  # Modified after analysis!

# Not hashable, can't use as dict keys or set members
my_set.add(fs)  # TypeError: unhashable type
```

**Problems:**
- Accidental mutation causes bugs
- Can't use as dict keys or set members
- Thread-safety issues
- Hard to reason about state
- Caching problems (keys can change)

### New Architecture

**Frozen Dataclasses:**
```python
@dataclass(frozen=True)
class FileAST:
    file_id: EntityId
    path: str  # Immutable!
    functions: Tuple[FunctionNode, ...]  # Immutable tuple!
    classes: Tuple[ClassNode, ...]  # Immutable tuple!

# PROBLEM SOLVED: Can't accidentally mutate
ast = FileAST(...)
ast.path = "different/path.py"  # FrozenInstanceError!
ast.functions.append(new_function)  # AttributeError!

# Hashable, can use as dict keys/set members
my_set.add(ast)  # Works!
my_dict[ast] = "metadata"  # Works!

# Thread-safe by default
# No concurrent modification issues
```

**Benefits:**
- ✅ **No accidental mutation**: Guaranteed immutability
- ✅ **Hashable**: Can use as dict keys/set members
- ✅ **Thread-safe**: No concurrent modification
- ✅ **Predictable**: State never changes after creation
- ✅ **Cacheable**: Safe to use as cache keys

**Innovation:** Immutable data model for all core data structures.

---

## 7. Findings: No Identity vs Stable Identity

### Current State

**No Stable Identity:**
```python
@dataclass
class Finding:
    finding_type: str
    severity: float
    files: List[str]
    evidence: List[Evidence]

# PROBLEM: Can't track findings across runs
# Run 1: high_risk_hub in src/auth/login.py
# Run 2: high_risk_hub in src/auth/login.py (same finding?)
# Run 3: Is it new? Recurring? Resolved?

# No lifecycle tracking
# Can't answer:
# - Is this a new finding?
# - Has this finding been seen before?
# - Did this finding get worse?
```

**Problems:**
- Can't track findings over time
- Can't detect recurring problems
- Can't measure resolution
- Can't deduplicate across runs
- No lifecycle management

### New Architecture

**Stable Identity via Hash:**
```python
@dataclass(frozen=True)
class Finding:
    finding_type: str
    severity: float
    files: List[str]
    evidence: List[Evidence]

    @property
    def identity_key(self) -> str:
        """Stable identity hash.

        Same finding across runs → same hash.
        Different finding → different hash.
        """
        key_dict = {
            "finding_type": self.finding_type,
            "files": sorted(self.files),  # Deterministic order
            "evidence": [(e.signal, e.value) for e in self.evidence],
        }
        key_str = json.dumps(key_dict, sort_keys=True)
        return sha256(key_str.encode()).hexdigest()[:16]

# FindingLifecycle tracks state across snapshots
class FindingLifecycle:
    finding_key: str
    snapshots_seen: List[str]  # snapshot_ids
    state: FindingState  # NEW, RECURRING, RESOLVED, CHRONIC
    first_seen: datetime
    last_seen: datetime
    severity_history: List[float]  # Track severity over time

# Can answer lifecycle questions
# - New finding? first_seen == today
# - Recurring? snapshots_seen count > 1
# - Resolved? not in latest snapshot
# - Getting worse? severity_history[-1] > severity_history[-2]
```

**Benefits:**
- ✅ **Lifecycle tracking**: Track findings over time
- ✅ **Deduplication**: Detect same finding across runs
- ✅ **Trend analysis**: Severity increasing/decreasing?
- ✅ **Resolution tracking**: Know when problems are fixed
- ✅ **Recurrence detection**: Same problem keeps coming back

**Innovation:** Hash-based finding identity with lifecycle tracking.

---

## 8. Temporal: Coarse vs Multi-Granularity

### Current State

**Coarse Granularity:**
```python
# Only file-level events
class FileChangeEvent:
    file_path: str
    change_type: str  # 'A', 'M', 'D'
    lines_added: int
    lines_deleted: int

# PROBLEM: Can't see line-level changes
# File modified 100 times, but which lines changed?
# Which lines are "hot spots"?
# How often does line 45 change?

# No identity tracking
# src/auth/login.py → src/auth/user/login.py
# Now you have TWO separate histories with no connection

# No historical reconstruction
# Can't ask: "What did file look like 2 months ago?"
# Can't diff: "Show me changes between commit A and B"
```

**Problems:**
- No line-level granularity
- Can't identify hot spots
- Can't track renames
- No historical reconstruction
- Limited temporal queries

### New Architecture

**Multi-Granularity Events:**
```python
# Commit-level events
@dataclass
class CommitEvent:
    commit_sha: str
    timestamp: int
    author: str
    files: List[str]

# File-level events
@dataclass
class FileChangeEvent:
    file_path: str
    old_path: Optional[str]  # For renames!
    change_type: str  # 'A', 'M', 'D', 'R'
    lines_added: int
    lines_deleted: int

# Line-level events (NEW!)
@dataclass
class LineChangeEvent:
    file_path: str
    line_number: int
    old_content: Optional[str]
    new_content: Optional[str]
    change_type: str  # 'ADD', 'DELETE', 'MODIFY'

# Identity tracking across renames
class IdentityResolver:
    def resolve(self, path_at_time: str, timestamp: int) -> EntityId:
        """Resolve historical path to canonical ID."""
        # src/auth/user/login.py (now)
        # ↓ resolved
        # src/auth/login.py (historical)
        return EntityId(EntityType.FILE, "src/auth/login.py")

# Time series with structure
@dataclass(frozen=True)
class TimeSeries:
    points: List[TimeSeriesPoint]
    unit: str  # days, weeks, hours
    start_timestamp: int
    end_timestamp: int

    # Advanced temporal operators
    def apply_operator(self, operator: TemporalOperator) -> Any:
        """Compute delta, velocity, acceleration, trajectory."""
        return operator(self.points)

# Historical reconstruction
def reconstruct_state(entity_id: EntityId, at_timestamp: int) -> EntityState:
    """Reconstruct entity state at a point in time."""
    # Apply all events up to timestamp
    # Return complete state
    pass
```

**Benefits:**
- ✅ **Line-level analysis**: Identify hot spots within files
- ✅ **Rename tracking**: Track files across renames
- ✅ **Historical reconstruction**: See past states
- ✅ **Advanced operators**: Delta, velocity, acceleration, trajectory
- ✅ **Temporal queries**: "Show me changes in time range"

**Innovation:** Multi-granularity event model with identity resolution and historical reconstruction.

---

## 9. Graph: Untyped vs Typed Edges

### Current State

**Untyped Edges:**
```python
# Edges are just string pairs
adjacency: Dict[str, List[str]] = {
    "src/auth/login.py": ["src/auth/db.py", "src/utils/crypto.py"],
    "src/auth/db.py": ["src/auth/login.py"],  # What kind of edge?
}

# No edge types
# Is this:
# - Import dependency?
# - Function call?
# - Class inheritance?
# - Interface implementation?

# No edge weights
# All edges equal weight?

# Scattered dictionaries
pagerank: Dict[str, float]
betweenness: Dict[str, float]
in_degree: Dict[str, int]
out_degree: Dict[str, int]
depth: Dict[str, int]
# Can't query "all metrics for node" efficiently
```

**Problems:**
- No edge semantics
- No edge weights
- Inefficient lookups
- Scattered data
- No validation

### New Architecture

**Typed Edges with Efficient Lookups:**
```python
# Typed edge
@dataclass(frozen=True)
class Edge:
    source: EntityId
    target: EntityId
    edge_type: EdgeType  # IMPORT, CALL, INHERITS, IMPLEMENTS
    weight: float  # 0.0 to 1.0
    metadata: Dict[str, Any]

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.edge_type))

# Efficient graph with adjacency
@dataclass
class DependencyGraph:
    nodes: Set[EntityId]
    edges: Set[Edge]
    adjacency: Dict[EntityId, List[Tuple[EntityId, Edge]]]
    reverse: Dict[EntityId, List[Tuple[EntityId, Edge]]]

    # Efficient queries
    def get_outgoing(self, node_id: EntityId, edge_type: Optional[EdgeType] = None) -> List[Tuple[EntityId, float]]:
        """Get all outgoing edges, optionally filtered by type."""
        if node_id not in self.adjacency:
            return []
        if edge_type is None:
            return [(target, edge.weight) for target, edge in self.adjacency[node_id]]
        else:
            return [(target, edge.weight) for target, edge in self.adjacency[node_id] if edge.edge_type == edge_type]

    def get_incoming(self, node_id: EntityId, edge_type: Optional[EdgeType] = None) -> List[Tuple[EntityId, float]]:
        """Get all incoming edges, optionally filtered by type."""
        if node_id not in self.reverse:
            return []
        if edge_type is None:
            return [(source, edge.weight) for source, edge in self.reverse[node_id]]
        else:
            return [(source, edge.weight) for source, edge in self.reverse[node_id] if edge.edge_type == edge_type]

# All metrics in one place
@dataclass
class GraphMetrics:
    pagerank: Dict[EntityId, float]
    betweenness: Dict[EntityId, float]
    in_degree: Dict[EntityId, int]
    out_degree: Dict[EntityId, int]
    depth: Dict[EntityId, int]
    blast_radius: Dict[EntityId, GraphSignal]
    # ... all metrics in one place
```

**Benefits:**
- ✅ **Explicit semantics**: Know what type of edge (import vs call)
- ✅ **Edge weights**: Capture relationship strength
- ✅ **Efficient lookups**: O(1) adjacency checks
- ✅ **Filtered queries**: Get only import edges, only call edges
- ✅ **Consolidated metrics**: All graph metrics in one object
- ✅ **Validation**: No self-loops, valid weights

**Innovation:** Typed edge system with efficient bidirectional adjacency.

---

## 10. Persistence: Flat vs Structured with Diff

### Current State

**Flat Dictionaries:**
```python
@dataclass
class Snapshot:
    # Flat dicts lose type information
    file_signals: Dict[str, Dict[str, float]]  # {path: {signal: value}}
    codebase_signals: Dict[str, float]  # {signal: value}

    # No diff support
    # To compare snapshots: Load both, iterate, compute diff manually

    # No schema validation
    # Can have inconsistent data
    file_signals["path"]["pagerank"] = "invalid"  # Type error!
```

**Problems:**
- Loss of type information
- No efficient diff support
- No schema validation
- Manual comparison
- Hard to query

### New Architecture

**Structured with Diff Support:**
```python
# Structured snapshot
@dataclass(frozen=True)
class Snapshot:
    metadata: SnapshotMetadata  # Version, timestamps, git SHA
    data: SnapshotData  # Entities, signals, relations

    def validate(self) -> bool:
        """Validate snapshot integrity."""
        # Check that all signal entities exist
        entity_ids = {ent["id"] for ent in self.data.entities}
        signal_entity_ids = {sig["entity_id"] for sig in self.data.signals}
        return signal_entity_ids.issubset(entity_ids)

    def get_signals_for_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get all signals for an entity (O(n) lookup)."""
        return {
            sig["signal_name"]: sig["value"]
            for sig in self.data.signals
            if sig["entity_id"] == entity_id
        }

# Efficient diff
@dataclass
class SnapshotDiff:
    from_snapshot_id: str
    to_snapshot_id: str
    added_entities: List[str]
    removed_entities: List[str]
    modified_entities: List[str]
    added_signals: List[Tuple[str, str]]  # (entity_id, signal_name)
    removed_signals: List[Tuple[str, str]]
    changed_signals: List[Tuple[str, str, Any, Any]]  # (entity_id, signal_name, old_value, new_value)
    added_findings: List[str]  # Finding identity keys
    removed_findings: List[str]
    changed_findings: List[str]

    @property
    def change_count(self) -> int:
        """Total number of changes."""
        return (
            len(self.added_entities) + len(self.removed_entities)
            + len(self.modified_entities) + len(self.added_signals)
            + len(self.removed_signals) + len(self.changed_signals)
            + len(self.added_findings) + len(self.removed_findings)
            + len(self.changed_findings)
        )

# Efficient diff computation
def diff_snapshots(from_snapshot: Snapshot, to_snapshot: Snapshot) -> SnapshotDiff:
    """Compute difference between snapshots efficiently."""
    # Use sets for O(1) lookups
    from_entities = {ent["id"] for ent in from_snapshot.data.entities}
    to_entities = {ent["id"] for ent in to_snapshot.data.entities}

    # Compute diff
    added = to_entities - from_entities
    removed = from_entities - to_entities
    # ... efficient computation

    return SnapshotDiff(
        from_snapshot_id=from_snapshot.metadata.snapshot_id,
        to_snapshot_id=to_snapshot.metadata.snapshot_id,
        added_entities=list(added),
        removed_entities=list(removed),
        # ... more diffs
    )
```

**Benefits:**
- ✅ **Structured data**: Preserves type information
- ✅ **Efficient diffs**: O(n) computation with sets
- ✅ **Validation**: Snapshot integrity checking
- ✅ **Trend analysis**: Track changes over time
- ✅ **Queryable**: Efficient lookups by entity/signal

**Innovation:** Structured snapshots with efficient diff computation and validation.

---

## Summary of Innovations

### Top 10 Innovations

| # | Innovation | Impact |
|---|-------------|---------|
| 1 | **Stable Entity Identity** | Tracks files across renames, enables historical analysis |
| 2 | **Multi-Type Signal System** | Supports SCALAR, TIME_SERIES, GRAPH, SET types with validation |
| 3 | **Unified EntityStore** | Eliminates dual storage, no synchronization complexity |
| 4 | **Finding Lifecycle Tracking** | Hash-based identity enables trend analysis, recurrence detection |
| 5 | **Multi-Granularity Temporal** | Line-level events, identity resolution, historical reconstruction |
| 6 | **Typed Edge System** | Explicit semantics (import/call/inherit), efficient queries |
| 7 | **Validation Checkpoints** | 8 validation layers guarantee data integrity |
| 8 | **Immutable Data Models** | Frozen dataclasses prevent accidental mutation, thread-safe |
| 9 | **Protocol-Based Layers** | Clear contracts, testable, composable |
| 10 | **Efficient Snapshot Diff** | O(n) diff computation enables trend analysis |

### Benefits Summary

**Development Benefits:**
- ✅ **Fewer bugs**: Type safety and validation prevent runtime errors
- ✅ **Easier debugging**: Clear error messages, validation checkpoints
- ✅ **Faster development**: Protocol-based interfaces, clear contracts
- ✅ **Better testing**: Each layer testable in isolation
- ✅ **Self-documenting**: Type hints and metadata in definitions

**Performance Benefits:**
- ✅ **Faster queries**: Efficient adjacency lookups, set-based diffs
- ✅ **Less memory**: Frozen dataclasses, no duplicate storage
- ✅ **Better caching**: Immutable objects safe as cache keys
- ✅ **Parallelization**: Layer independence enables parallel execution

**Feature Benefits:**
- ✅ **Rename tracking**: Stable entity identity survives file moves
- ✅ **Line-level analysis**: Identify hot spots within files
- ✅ **Historical reconstruction**: See past states, compute trends
- ✅ **Finding lifecycle**: Track problems over time, measure resolution
- ✅ **Richer signals**: Time series, graph, set types

**Maintainability Benefits:**
- ✅ **Single storage**: No synchronization complexity
- ✅ **Clear boundaries**: Layer protocols define contracts
- ✅ **Validation everywhere**: Early error detection
- ✅ **Type safety**: Compile-time and runtime validation

---

## Migration Path

The new architecture can be migrated incrementally:

**Phase 1: Foundation (Week 1-4)**
- Implement core abstractions (`Entity`, `Signal`, `Relation`)
- Build `EntityStore` with validation
- Write unit tests

**Phase 2: Layer Migration (Week 5-12)**
- Migrate scanning layer to `FileAST`
- Migrate graph layer to `DependencyGraph`
- Migrate temporal layer (see TEMPORAL-MODULE-REDESIGN.md)
- Update analyzers

**Phase 3: Remove Dual Storage (Week 13-16)**
- Remove `AnalysisStore` slots
- Migrate to `EntityStore` only
- Remove `_sync_entities()` bridge

**Phase 4: Update Persistence (Week 17-20)**
- Implement new `Snapshot` schema
- Add `SnapshotDiff` computation
- Migrate existing snapshots

**Phase 5: Clean Up (Week 21-24)**
- Remove old data models
- Update documentation
- Deprecate old APIs

**Total: 24 weeks** with backward compatibility maintained via adapters.
