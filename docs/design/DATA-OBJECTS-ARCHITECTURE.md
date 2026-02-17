# Data Objects Architecture Design

**Document Version:** 1.0
**Date:** 2026-02-17
**Status:** Design Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1: Current Data Objects Analysis](#phase-1-current-data-objects-analysis)
3. [Phase 2: Core Data Abstractions](#phase-2-core-data-abstractions)
4. [Phase 3: Improved Data Models by Layer](#phase-3-improved-data-models-by-layer)
5. [Phase 4: Layer Interfaces](#phase-4-layer-interfaces)
6. [Phase 5: Data Flow Design](#phase-5-data-flow-design)
7. [Phase 6: Protocol-Based Interfaces](#phase-6-protocol-based-interfaces)
8. [Phase 7: Migration Strategy](#phase-7-migration-strategy)
9. [Key Design Decisions](#key-design-decisions)

---

## Executive Summary

Shannon Insight currently has **multiple data models across 7 layers** with inconsistent abstractions, dual storage systems (`AnalysisStore` + `FactStore`), and unclear transformation boundaries. This document proposes a unified data object architecture with:

- **Canonical entity hierarchy** with stable IDs across renames/moves
- **Typed signal system** with clear value types and validation
- **Layer-specific data models** with clear input/output contracts
- **Transformation pipelines** with validation at each step
- **Protocol-based interfaces** for loose coupling

The redesign eliminates dual storage, provides clear layer boundaries, and enables incremental improvements similar to the temporal module redesign.

---

## Phase 1: Current Data Objects Analysis

### 1.1 Scanning Layer (`scanning/`)

**Current Models:**
- `FunctionDef`: Function/method definition (name, params, body_tokens, nesting_depth, call_targets)
- `ClassDef`: Class definition (name, bases, methods, fields, is_abstract)
- `ImportDecl`: Import declaration (source, names, resolved_path)
- `FileSyntax`: Complete syntax extraction (functions, classes, imports, language, metrics)

**Problems:**
1. **No entity identity**: Files identified by path only, can't track renames
2. **Mixed concerns**: `FileSyntax` contains both raw AST and computed metrics
3. **No validation**: No validation for nested structures
4. **Loose typing**: `call_targets` is `None` for regex fallback (nullable field pattern)
5. **Cached metrics**: `_lines`, `_tokens`, `_complexity` stored as mutable private fields
6. **No provenance**: No tracking of when/who created the syntax data

### 1.2 Graph Layer (`graph/`)

**Current Models:**
- `DependencyGraph`: adjacency dict, reverse dict, all_nodes, edge_count
- `GraphAnalysis`: pagerank, betweenness, degrees, blast_radius, cycles, communities
- `ModuleAnalysis`: per-module cohesion, coupling, Martin metrics
- `FileAnalysis`: per-file graph metrics (pagerank, betweenness, degrees, depth, is_orphan)
- `CycleGroup`, `Community`, `BoundaryMismatch`, `ClonePair`, `AuthorDistance`

**Problems:**
1. **No edge metadata**: Edges are just string pairs, no weights/types
2. **Scattered dictionaries**: Graph data split across multiple dicts
3. **No versioning**: Can't track graph evolution over time
4. **Weak typing**: Many `dict[str, T]` without clear schemas
5. **No validation**: No validation for graph invariants
6. **Derived data mixed with structural**: `GraphAnalysis` contains both raw graphs and derived metrics

### 1.3 Temporal Layer (`temporal/`)

**Current Models:**
- `Commit`: hash, timestamp, author, files, subject
- `GitHistory`: commits list, file_set, span_days
- `CoChangePair`: file_a, file_b, counts, confidences, lift, weight
- `CoChangeMatrix`: sparse pairs dict, total_commits, file_change_counts
- `ChurnSeries`: file_path, window_counts, trajectory, slope, cv, bus_factor, author_entropy, fix_ratio

**Problems:**
1. **No entity identity**: Files identified by path, can't track renames (detailed in TEMPORAL-MODULE-REDESIGN.md)
2. **Coarse granularity**: No line-level events
3. **No historical reconstruction**: Can't reconstruct past states
4. **Sparse data structures**: `CoChangeMatrix` uses dict keys as tuples, inefficient
5. **No time-series abstraction**: `window_counts` is just a list
6. **Mixed metrics**: `ChurnSeries` contains both raw data and derived metrics

### 1.4 Semantic Layer (`semantics/`)

**Current Models:**
- `Role`: Enum for file roles (TEST, ENTRY_POINT, INTERFACE, etc.)
- `Concept`: semantic concept with topic, weight, keywords
- `Completeness`: TODO density, docstring coverage
- `FileSemantics`: path, role, concepts, concept_count, concept_entropy, naming_drift, completeness

**Problems:**
1. **No concept ontology**: Concepts are just strings, no hierarchy
2. **Loose typing**: `Completeness.docstring_coverage` is `None` for non-Python
3. **No validation**: Concept weights can exceed 1.0
4. **No provenance**: No tracking of how concepts were extracted
5. **Mixed computed data**: `FileSemantics` contains both extracted data and derived metrics

### 1.5 Infrastructure Layer (`infrastructure/`)

**Current Models:**
- `EntityId`: type + key (frozen)
- `Entity`: id, parent, metadata dict
- `Signal` enum: 62 signals across 6 levels
- `SignalMeta`: dtype, scope, polarity, percentileability, threshold, producer, phase
- `Pattern`: pattern definition with predicate, severity_fn, evidence_fn

**Problems:**
1. **Dual storage**: Both `AnalysisStore` (slots) and `FactStore` exist
2. **Metadata as dict**: `Entity.metadata` is untyped, no schema
3. **No signal value type**: `Signal` enum has names but no value types
4. **No time-series support**: Signals are scalar only
5. **Weak relations**: Relations exist but not well-modeled
6. **No validation**: No runtime validation for signal values

### 1.6 Persistence Layer (`persistence/`)

**Current Models:**
- `EvidenceRecord`: signal, value, percentile, description
- `FindingRecord`: finding_type, identity_key, severity, files, evidence, suggestion, confidence, effort, scope
- `Snapshot`: v1 schema (file_signals, codebase_signals, findings)
- `TensorSnapshot`: v2 schema (adds module_signals, architecture, cochange_edges, communities)

**Problems:**
1. **Versioning complexity**: Both v1 and v2 schemas exist
2. **No schema validation**: No validation for snapshot integrity
3. **Manual conversion**: `snapshot_to_tensor()` is manual, error-prone
4. **No diff support**: Can't efficiently diff snapshots
5. **No provenance**: No tracking of what generated the snapshot
6. **Flat structure**: All signals serialized to flat dicts, loses type information

### 1.7 Insights Layer (`insights/`)

**Current Models:**
- `Evidence`: signal, value, percentile, description
- `Finding`: finding_type, severity, title, files, evidence, suggestion, confidence, effort, scope
- `StoreSummary`: total counts, git_available, fiedler_value, signals_available
- `InsightResult`: findings, store_summary, diagnostic_report

**Problems:**
1. **Duplicate evidence**: `EvidenceRecord` in persistence, `Evidence` in insights
2. **No finding hierarchy**: All findings are flat
3. **No lifecycle tracking**: Can't track findings across snapshots
4. **Weak typing**: `diagnostic_report` is `object` type
5. **No validation**: Severity and confidence can exceed [0, 1]

### 1.8 Dual Storage Problem

**AnalysisStore (Old):**
```python
class AnalysisStore:
    file_syntax: Slot[Dict[str, FileSyntax]]
    structural: Slot[CodebaseAnalysis]
    git_history: Slot[GitHistory]
    churn: Slot[Dict[str, ChurnSeries]]
    cochange: Slot[CoChangeMatrix]
    semantics: Slot[Dict[str, FileSemantics]]
    # ... more slots
```

**FactStore (New):**
```python
class FactStore:
    entities: Dict[EntityId, Entity]
    signals: Dict[EntityId, Dict[Signal, Any]]
    relations: Dict[RelationType, List[Tuple[EntityId, EntityId, float]]]
```

**Problems:**
1. **Confusion**: Which store to use?
2. **Synchronization**: `_sync_entities()` manually bridges them
3. **Inconsistency**: Data can diverge between stores
4. **Maintenance cost**: Need to maintain both
5. **Testing complexity**: Need to test both stores

---

## Phase 2: Core Data Abstractions

### 2.1 Entity Abstractions

**Core Principle:** Stable identity across time and transformations.

```python
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

class EntityType(Enum):
    """Types of entities in the codebase."""
    CODEBASE = "codebase"
    MODULE = "module"
    FILE = "file"
    SYMBOL = "symbol"
    AUTHOR = "author"
    COMMIT = "commit"

@dataclass(frozen=True, eq=True, order=True)
class EntityId:
    """Canonical, stable identifier for an entity.

    Immutable, hashable, comparable.
    Survives renames, moves, and other transformations.

    Key conventions:
        CODEBASE  - absolute path              e.g. /Users/dev/myproject
        MODULE    - module name (relative)       e.g. auth, graph, tests
        FILE      - canonical file path         e.g. src/auth/login.py
        SYMBOL    - file:line:name             e.g. src/auth/login.py:45:authenticate
        AUTHOR    - normalized email            e.g. alice@example.com (lowercase)
        COMMIT    - full SHA-256 hash          e.g. abc1234567890...
    """
    type: EntityType
    key: str  # Stable identifier that survives renames

@dataclass
class Entity:
    """A concrete entity with metadata and lifecycle.

    Every entity has:
        - id:       stable EntityId
        - parent:   optional parent EntityId (None for roots)
        - created:  creation timestamp
        - deleted:  deletion timestamp (None if still exists)
        - metadata: typed attributes
    """
    id: EntityId
    parent: Optional[EntityId] = None
    created: datetime = field(default_factory=datetime.now)
    deleted: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """True if entity has not been deleted."""
        return self.deleted is None
```

### 2.2 Signal Value Types

**Core Principle:** Type-safe, validated signal values.

```python
from dataclasses import dataclass
from typing import Union, List, Dict
from enum import Enum
from datetime import datetime

class SignalValueType(Enum):
    """Types of signal values."""
    SCALAR = "scalar"  # float, int
    CATEGORICAL = "categorical"  # str, Enum
    TIME_SERIES = "time_series"  # List[TimeSeriesPoint]
    GRAPH = "graph"  # GraphSignal
    SET = "set"  # Set[str]

@dataclass(frozen=True)
class TimeSeriesPoint:
    """A single point in a time series."""
    timestamp: int  # unix seconds
    value: float

@dataclass(frozen=True)
class TimeSeries:
    """A typed time series with metadata."""
    points: List[TimeSeriesPoint]
    unit: str = "days"  # days, weeks, hours, etc.
    start_timestamp: int = 0
    end_timestamp: int = 0
    length: int = field(init=False)

    def __post_init__(self):
        if not self.points:
            object.__setattr__(self, 'start_timestamp', 0)
            object.__setattr__(self, 'end_timestamp', 0)
            object.__setattr__(self, 'length', 0)
        else:
            points_sorted = sorted(self.points, key=lambda p: p.timestamp)
            object.__setattr__(self, 'points', points_sorted)
            object.__setattr__(self, 'start_timestamp', points_sorted[0].timestamp)
            object.__setattr__(self, 'end_timestamp', points_sorted[-1].timestamp)
            object.__setattr__(self, 'length', len(points_sorted))

@dataclass(frozen=True)
class GraphSignal:
    """Graph-based signal (e.g., blast_radius, community)."""
    node_id: str  # File or module ID
    nodes: Set[str]  # Related nodes
    weight: float = 1.0  # Edge weight
    metadata: Dict[str, Any] = field(default_factory=dict)

# Union type for signal values
SignalValue = Union[
    float,  # SCALAR
    int,  # SCALAR
    str,  # CATEGORICAL
    TimeSeries,  # TIME_SERIES
    GraphSignal,  # GRAPH
    Set[str],  # SET
]
```

### 2.3 Signal Abstractions

```python
from dataclasses import dataclass
from enum import Enum
from typing import Type, get_args, get_origin

class SignalScope(Enum):
    """Scope of a signal (which entities have it)."""
    FILE = "file"
    MODULE = "module"
    CODEBASE = "codebase"

class SignalPolarity(Enum):
    """How to interpret high values."""
    HIGH_IS_BAD = "high_is_bad"
    HIGH_IS_GOOD = "high_is_good"
    NEUTRAL = "neutral"

@dataclass(frozen=True)
class SignalDef:
    """Definition of a signal with metadata.

    This is the SINGLE source of truth for signal definitions.
    """
    name: str  # e.g., "pagerank"
    dtype: Type  # Expected value type (float, int, str, TimeSeries, etc.)
    scope: SignalScope  # Which entities have this signal
    value_type: SignalValueType  # Type category
    polarity: SignalPolarity
    percentileable: bool  # Can this be percentiled?
    absolute_threshold: Optional[float]  # Absolute threshold if known
    produced_by: str  # Which analyzer produces this
    phase: int  # Analysis phase when this is available
    description: str = ""  # Human-readable description

    def validate_value(self, value: SignalValue) -> bool:
        """Validate a signal value against type."""
        if self.value_type == SignalValueType.SCALAR:
            return isinstance(value, (int, float))
        elif self.value_type == SignalValueType.CATEGORICAL:
            return isinstance(value, (str, Enum))
        elif self.value_type == SignalValueType.TIME_SERIES:
            return isinstance(value, TimeSeries)
        elif self.value_type == SignalValueType.GRAPH:
            return isinstance(value, GraphSignal)
        elif self.value_type == SignalValueType.SET:
            return isinstance(value, set)
        return False

# Signal registry (single source of truth)
SIGNAL_REGISTRY: Dict[str, SignalDef] = {}

def register_signal(defn: SignalDef) -> None:
    """Register a signal definition."""
    if defn.name in SIGNAL_REGISTRY:
        raise ValueError(f"Signal {defn.name} already registered")
    SIGNAL_REGISTRY[defn.name] = defn

def get_signal_def(name: str) -> SignalDef:
    """Get signal definition by name."""
    if name not in SIGNAL_REGISTRY:
        raise KeyError(f"Unknown signal: {name}")
    return SIGNAL_REGISTRY[name]
```

### 2.4 Relation Abstractions

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional

class RelationType(Enum):
    """Types of relations between entities."""
    DEPENDS_ON = "depends_on"  # File depends on another file (import)
    CONTAINS = "contains"  # Module contains file, file contains symbol
    SIMILAR_TO = "similar_to"  # Clone pair, semantic similarity
    CO_CHANGES_WITH = "co_changes_with"  # Files changed together in git
    AUTHORED_BY = "authored_by"  # Commit authored by author
    IN_SAME_COMMUNITY = "in_same_community"  # Files in same graph community
    CALLS = "calls"  # Function calls another function

@dataclass(frozen=True)
class Relation:
    """A typed relation between two entities.

    Relations are:
        - Directed: A → B is different from B → A
        - Weighted: Have an optional weight (0.0 to 1.0)
        - Typed: Have a RelationType
        - Timestamped: Optional timestamp for temporal relations
    """
    type: RelationType
    source: EntityId
    target: EntityId
    weight: float = 1.0  # Edge weight
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[int] = None  # unix seconds

@dataclass
class RelationGraph:
    """A graph of relations with efficient querying.

    Optimized for:
        - Edge lookups: O(1) adjacency checks
        - Weighted queries: Get edges above threshold
        - Bidirectional queries: Get incoming/outgoing
    """
    forward: Dict[EntityId, List[Tuple[EntityId, Relation]]] = field(default_factory=dict)
    reverse: Dict[EntityId, List[Tuple[EntityId, Relation]]] = field(default_factory=dict)

    def add_relation(self, relation: Relation) -> None:
        """Add a relation to the graph."""
        # Forward edge
        if relation.source not in self.forward:
            self.forward[relation.source] = []
        self.forward[relation.source].append((relation.target, relation))

        # Reverse edge
        if relation.target not in self.reverse:
            self.reverse[relation.target] = []
        self.reverse[relation.target].append((relation.source, relation))

    def get_outgoing(self, entity_id: EntityId, rel_type: Optional[RelationType] = None) -> List[Tuple[EntityId, float]]:
        """Get outgoing relations from an entity."""
        if entity_id not in self.forward:
            return []

        if rel_type is None:
            return [(target, rel.weight) for target, rel in self.forward[entity_id]]
        else:
            return [(target, rel.weight) for target, rel in self.forward[entity_id] if rel.type == rel_type]

    def get_incoming(self, entity_id: EntityId, rel_type: Optional[RelationType] = None) -> List[Tuple[EntityId, float]]:
        """Get incoming relations to an entity."""
        if entity_id not in self.reverse:
            return []

        if rel_type is None:
            return [(source, rel.weight) for source, rel in self.reverse[entity_id]]
        else:
            return [(source, rel.weight) for source, rel in self.reverse[entity_id] if rel.type == rel_type]
```

### 2.5 Result Abstractions

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from hashlib import sha256
import json

@dataclass(frozen=True)
class Evidence:
    """Evidence supporting a finding.

    Evidence links a finding to specific signal values.
    """
    signal: str  # Signal name
    value: SignalValue  # Raw value
    percentile: Optional[float]  # Percentile (0-100), None if not percentiled
    description: str  # Human-readable description

@dataclass
class Finding:
    """A finding (issue, insight, pattern match).

    Findings have stable identity across analysis runs.
    """
    finding_type: str  # e.g., "high_risk_hub", "hidden_coupling"
    severity: float  # 0.0 to 1.0
    title: str
    description: str
    files: List[str]  # Involved files (canonical paths)
    evidence: List[Evidence]  # Supporting evidence
    suggestion: str  # Remediation suggestion
    confidence: float = 1.0  # 0.0 to 1.0
    effort: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    scope: str = "FILE"  # FILE, FILE_PAIR, MODULE, MODULE_PAIR, CODEBASE
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def identity_key(self) -> str:
        """Stable identity hash for this finding.

        Used to track findings across snapshots.
        """
        # Create stable hash from type, files, and evidence
        key_dict = {
            "finding_type": self.finding_type,
            "files": sorted(self.files),
            "evidence": [(e.signal, e.value) for e in self.evidence],
        }
        key_str = json.dumps(key_dict, sort_keys=True)
        return sha256(key_str.encode()).hexdigest()[:16]

    def validate(self) -> bool:
        """Validate finding integrity."""
        return (
            0.0 <= self.severity <= 1.0
            and 0.0 <= self.confidence <= 1.0
            and self.effort in {"LOW", "MEDIUM", "HIGH"}
            and self.scope in {"FILE", "FILE_PAIR", "MODULE", "MODULE_PAIR", "CODEBASE"}
        )

@dataclass
class AnalysisResult:
    """Complete analysis result.

    Contains findings, summary, and diagnostic information.
    """
    findings: List[Finding]
    total_files: int
    total_modules: int
    git_available: bool
    analysis_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def high_severity_count(self) -> int:
        """Count of high-severity findings (>= 0.7)."""
        return sum(1 for f in self.findings if f.severity >= 0.7)

    @property
    def medium_severity_count(self) -> int:
        """Count of medium-severity findings (0.4-0.7)."""
        return sum(1 for f in self.findings if 0.4 <= f.severity < 0.7)

    @property
    def low_severity_count(self) -> int:
        """Count of low-severity findings (< 0.4)."""
        return sum(1 for f in self.findings if f.severity < 0.4)
```

---

## Phase 3: Improved Data Models by Layer

### 3.1 Scanning Layer Data Models

**Core Abstractions:** Parse tree → AST nodes → syntax model

```python
from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict
from enum import Enum

class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    GO = "go"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    RUST = "rust"
    RUBY = "ruby"
    CPP = "cpp"
    C = "c"
    UNKNOWN = "unknown"

class FunctionKind(Enum):
    """Kind of function or method."""
    FUNCTION = "function"
    METHOD = "method"
    CLASSMETHOD = "classmethod"
    STATICMETHOD = "staticmethod"
    PROPERTY = "property"
    LAMBDA = "lambda"
    UNKNOWN = "unknown"

class ClassKind(Enum):
    """Kind of class."""
    CLASS = "class"
    INTERFACE = "interface"
    ABSTRACT = "abstract"
    PROTOCOL = "protocol"
    ENUM = "enum"
    DATACLASS = "dataclass"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class FunctionNode:
    """A function or method definition.

    Immutable, hashable AST node.
    """
    name: str
    kind: FunctionKind
    params: List[str]  # Parameter names
    decorators: List[str] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    is_exported: bool = False  # Public API?
    is_abstract: bool = False  # Has abstractmethod?
    is_stub: bool = False  # Has no meaningful implementation?

    @property
    def size(self) -> int:
        """Size in lines."""
        return max(1, self.end_line - self.start_line + 1)

@dataclass(frozen=True)
class ClassNode:
    """A class or interface definition.

    Immutable, hashable AST node.
    """
    name: str
    kind: ClassKind
    bases: List[str] = field(default_factory=list)  # Base class names
    methods: List[FunctionNode] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)  # Field/attribute names
    start_line: int = 0
    end_line: int = 0
    is_exported: bool = False

    @property
    def size(self) -> int:
        """Size in lines."""
        return max(1, self.end_line - self.start_line + 1)

@dataclass(frozen=True)
class ImportNode:
    """An import declaration.

    Immutable, hashable AST node.
    """
    module: str  # Module being imported
    names: List[str] = field(default_factory=list)  # Imported names
    alias: Optional[str] = None  # Import alias
    is_from: bool = False  # True for "from X import Y"
    is_wildcard: bool = False  # True for "from X import *"
    is_resolved: bool = False  # Can be resolved to a file?
    resolved_path: Optional[str] = None  # Resolved file path

    @property
    def is_phantom(self) -> bool:
        """True if import cannot be resolved."""
        return not self.is_resolved

@dataclass(frozen=True)
class FileAST:
    """Complete AST for a file.

    Immutable snapshot of file structure.
    Separated from metrics (computed later).
    """
    file_id: EntityId  # Canonical file ID
    path: str  # Current path (may change due to rename)
    language: Language
    functions: List[FunctionNode] = field(default_factory=list)
    classes: List[ClassNode] = field(default_factory=list)
    imports: List[ImportNode] = field(default_factory=list)
    has_main_guard: bool = False  # Has __name__ == "__main__" guard?
    line_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def function_count(self) -> int:
        return len(self.functions)

    @property
    def class_count(self) -> int:
        return len(self.classes)

    @property
    def import_count(self) -> int:
        return len(self.imports)

    @property
    def max_nesting(self) -> int:
        if not self.functions:
            return 0
        return max(fn.end_line - fn.start_line for fn in self.functions)

    def get_import_sources(self) -> Set[str]:
        """Get set of imported module sources."""
        return {imp.module for imp in self.imports}

    def get_resolved_imports(self) -> Set[str]:
        """Get set of resolved import paths."""
        return {imp.resolved_path for imp in self.imports if imp.resolved_path}
```

### 3.2 Graph Layer Data Models

**Core Abstractions:** Nodes → Edges → Graph → Graph metrics

```python
from dataclasses import dataclass, field
from typing import Set, Dict, List, Tuple, Optional
from enum import Enum

class EdgeType(Enum):
    """Types of edges in dependency graph."""
    IMPORT = "import"  # File imports module
    CALL = "call"  # Function calls function
    INHERITS = "inherits"  # Class inherits from class
    IMPLEMENTS = "implements"  # Class implements interface

@dataclass(frozen=True)
class Edge:
    """A directed edge in the dependency graph.

    Immutable, hashable.
    """
    source: EntityId  # Source node
    target: EntityId  # Target node
    edge_type: EdgeType
    weight: float = 1.0  # Edge weight
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.edge_type))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Edge):
            return False
        return (
            self.source == other.source
            and self.target == other.target
            and self.edge_type == other.edge_type
        )

@dataclass
class DependencyGraph:
    """Typed dependency graph with efficient querying.

    Supports:
        - Directed edges (A → B)
        - Multiple edge types
        - Weighted edges
        - Fast adjacency lookups
    """
    nodes: Set[EntityId] = field(default_factory=set)
    edges: Set[Edge] = field(default_factory=set)
    adjacency: Dict[EntityId, List[Tuple[EntityId, Edge]]] = field(default_factory=dict)
    reverse: Dict[EntityId, List[Tuple[EntityId, Edge]]] = field(default_factory=dict)

    def add_node(self, node_id: EntityId) -> None:
        """Add a node to the graph."""
        self.nodes.add(node_id)
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []
        if node_id not in self.reverse:
            self.reverse[node_id] = []

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        self.edges.add(edge)
        self.add_node(edge.source)
        self.add_node(edge.target)

        # Forward adjacency
        self.adjacency[edge.source].append((edge.target, edge))

        # Reverse adjacency
        self.reverse[edge.target].append((edge.source, edge))

    def get_outgoing(
        self, node_id: EntityId, edge_type: Optional[EdgeType] = None
    ) -> List[Tuple[EntityId, float]]:
        """Get outgoing edges from a node."""
        if node_id not in self.adjacency:
            return []

        if edge_type is None:
            return [(target, edge.weight) for target, edge in self.adjacency[node_id]]
        else:
            return [
                (target, edge.weight)
                for target, edge in self.adjacency[node_id]
                if edge.edge_type == edge_type
            ]

    def get_incoming(
        self, node_id: EntityId, edge_type: Optional[EdgeType] = None
    ) -> List[Tuple[EntityId, float]]:
        """Get incoming edges to a node."""
        if node_id not in self.reverse:
            return []

        if edge_type is None:
            return [(source, edge.weight) for source, edge in self.reverse[node_id]]
        else:
            return [
                (source, edge.weight)
                for source, edge in self.reverse[node_id]
                if edge.edge_type == edge_type
            ]

    def get_degree(self, node_id: EntityId) -> int:
        """Get total degree (in + out) of a node."""
        in_deg = len(self.reverse.get(node_id, []))
        out_deg = len(self.adjacency.get(node_id, []))
        return in_deg + out_deg

@dataclass
class GraphMetrics:
    """Graph algorithm results.

    Contains metrics computed from graph structure.
    """
    pagerank: Dict[EntityId, float] = field(default_factory=dict)
    betweenness: Dict[EntityId, float] = field(default_factory=dict)
    in_degree: Dict[EntityId, int] = field(default_factory=dict)
    out_degree: Dict[EntityId, int] = field(default_factory=dict)
    depth: Dict[EntityId, int] = field(default_factory=dict)  # BFS depth from entry points
    is_orphan: Set[EntityId] = field(default_factory=set)  # Nodes with no incoming edges
    blast_radius: Dict[EntityId, GraphSignal] = field(default_factory=dict)  # Transitive impact

    # Community detection
    communities: List[Set[EntityId]] = field(default_factory=list)
    node_community: Dict[EntityId, int] = field(default_factory=dict)
    modularity: float = 0.0

    # Cycle detection
    sccs: List[Set[EntityId]] = field(default_factory=list)  # Strongly connected components
    cycles: List[Set[EntityId]] = field(default_factory=list)  # Real cycles (SCC size > 1)
    cycle_count: int = 0

    # Spectral properties
    fiedler_value: float = 0.0  # λ₂ (algebraic connectivity)
    spectral_gap: float = 0.0  # λ₂ / λ₃
    eigenvalues: List[float] = field(default_factory=list)
```

### 3.3 Temporal Layer Data Models

**Core Abstractions:** Events → Time series → Temporal metrics

*See TEMPORAL-MODULE-REDESIGN.md for detailed design. Summary:*

```python
# CanonicalId - stable identity across renames
# GitEvent, CommitEvent, FileChangeEvent, LineChangeEvent
# TimeSeries with TimeSeriesPoint
# ChurnMetrics per entity
```

### 3.4 Semantic Layer Data Models

**Core Abstractions:** Semantics → Concepts → Roles

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class Role(Enum):
    """File role classification (same as current)."""
    TEST = "test"
    ENTRY_POINT = "entry_point"
    INTERFACE = "interface"
    CONSTANT = "constant"
    EXCEPTION = "exception"
    MODEL = "model"
    CLI = "cli"
    SERVICE = "service"
    MIGRATION = "migration"
    UTILITY = "utility"
    CONFIG = "config"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class Concept:
    """A semantic concept (topic) with weight.

    Immutable, hashable.
    """
    topic: str  # Concept name/label
    weight: float  # Relative importance [0, 1]
    keywords: List[str] = field(default_factory=list)  # Representative keywords
    confidence: float = 1.0  # Confidence in extraction [0, 1]

    def __hash__(self) -> int:
        return hash(self.topic)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Concept):
            return False
        return self.topic == other.topic

@dataclass(frozen=True)
class CompletenessMetrics:
    """Documentation and completeness metrics."""
    todo_count: int = 0  # Raw TODO/FIXME/HACK count
    todo_density: float = 0.0  # TODOs per 100 lines
    documented_count: int = 0  # Number of documented items
    total_documentable: int = 0  # Total items that could have docs
    docstring_coverage: Optional[float] = None  # Coverage ratio [0, 1], None if N/A
    comment_ratio: float = 0.0  # Comment lines / total lines

@dataclass(frozen=True)
class FileSemantics:
    """Complete semantic analysis for a file.

    Immutable snapshot of semantic properties.
    """
    file_id: EntityId  # Canonical file ID
    path: str  # Current path
    role: Role
    concepts: List[Concept] = field(default_factory=list)
    primary_concept: Optional[str] = None
    concept_entropy: float = 0.0  # Shannon entropy of concept weights
    naming_drift: float = 0.0  # Dissimilarity filename vs content [0, 1]
    completeness: CompletenessMetrics = field(default_factory=CompletenessMetrics)
    language: Language = Language.UNKNOWN
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def concept_count(self) -> int:
        return len(self.concepts)
```

### 3.5 Infrastructure Layer Data Models

**Core Abstractions:** Entity → Signal → Relation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional
from datetime import datetime

@dataclass(frozen=True)
class SignalValue:
    """Typed signal value with metadata.

    Immutable, validated.
    """
    signal_def: SignalDef
    value: SignalValue  # The actual value (float, int, str, TimeSeries, etc.)
    computed_at: datetime = field(default_factory=datetime.now)
    percentile: Optional[float] = None  # Percentile if computed
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate signal value against definition."""
        if not self.signal_def.validate_value(self.value):
            raise ValueError(
                f"Invalid value {self.value} for signal {self.signal_def.name}"
            )

@dataclass
class EntityStore:
    """Store for entities, signals, and relations.

    Unified storage for all data.
    """
    entities: Dict[EntityId, Entity] = field(default_factory=dict)
    signals: Dict[EntityId, Dict[str, SignalValue]] = field(default_factory=dict)
    relations: RelationGraph = field(default_factory=RelationGraph)

    def get_entity(self, entity_id: EntityId) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)

    def add_entity(self, entity: Entity) -> None:
        """Add an entity."""
        self.entities[entity.id] = entity

    def get_signal(
        self, entity_id: EntityId, signal_name: str
    ) -> Optional[SignalValue]:
        """Get signal value for an entity."""
        if entity_id not in self.signals:
            return None
        return self.signals[entity_id].get(signal_name)

    def set_signal(
        self, entity_id: EntityId, signal_value: SignalValue
    ) -> None:
        """Set signal value for an entity."""
        if entity_id not in self.signals:
            self.signals[entity_id] = {}
        self.signals[entity_id][signal_value.signal_def.name] = signal_value

    def get_entities_with_signal(self, signal_name: str) -> List[EntityId]:
        """Get all entities that have a specific signal."""
        return [
            entity_id
            for entity_id, signals in self.signals.items()
            if signal_name in signals
        ]

    def get_entities_in_scope(self, scope: SignalScope) -> List[EntityId]:
        """Get all entities in a given scope."""
        if scope == SignalScope.FILE:
            return [
                eid for eid, ent in self.entities.items() if eid.type == EntityType.FILE
            ]
        elif scope == SignalScope.MODULE:
            return [
                eid for eid, ent in self.entities.items() if eid.type == EntityType.MODULE
            ]
        elif scope == SignalScope.CODEBASE:
            return [
                eid for eid, ent in self.entities.items()
                if eid.type == EntityType.CODEBASE
            ]
        return []
```

### 3.6 Persistence Layer Data Models

**Core Abstractions:** Snapshot → Diff → History

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from hashlib import sha256
import json

@dataclass(frozen=True)
class SnapshotMetadata:
    """Metadata for an analysis snapshot."""
    schema_version: int = 3  # Updated schema version
    tool_version: str = ""
    git_sha: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    analyzed_path: str = ""
    config_hash: str = ""
    analysis_duration_seconds: float = 0.0
    file_count: int = 0
    module_count: int = 0

    @property
    def snapshot_id(self) -> str:
        """Unique ID for this snapshot."""
        key = f"{self.git_sha}:{self.timestamp.isoformat()}:{self.config_hash}"
        return sha256(key.encode()).hexdigest()[:16]

@dataclass(frozen=True)
class SnapshotData:
    """Data section of a snapshot.

    Contains all signals, relations, and findings.
    """
    # Entity data (flattened for serialization)
    entities: List[Dict[str, Any]] = field(default_factory=list)  # [id, type, key, parent, metadata]
    signals: List[Dict[str, Any]] = field(default_factory=list)  # [entity_id, signal_name, value, percentile]
    relations: List[Dict[str, Any]] = field(default_factory=list)  # [source, target, type, weight, metadata]

    # Graph structure
    dependency_edges: List[Tuple[str, str]] = field(default_factory=list)

    # Findings
    findings: List[Dict[str, Any]] = field(default_factory=list)  # Serialized Finding objects

@dataclass(frozen=True)
class Snapshot:
    """Complete analysis snapshot.

    Immutable, serializable, queryable.
    """
    metadata: SnapshotMetadata
    data: SnapshotData

    def validate(self) -> bool:
        """Validate snapshot integrity."""
        # Check that all signal entities exist
        entity_ids = {ent["id"] for ent in self.data.entities}
        signal_entity_ids = {sig["entity_id"] for sig in self.data.signals}
        return signal_entity_ids.issubset(entity_ids)

    def get_signals_for_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get all signals for an entity."""
        return {
            sig["signal_name"]: sig["value"]
            for sig in self.data.signals
            if sig["entity_id"] == entity_id
        }

@dataclass
class SnapshotDiff:
    """Difference between two snapshots.

    Enables efficient comparison and trend analysis.
    """
    from_snapshot_id: str
    to_snapshot_id: str
    added_entities: List[str] = field(default_factory=list)
    removed_entities: List[str] = field(default_factory=list)
    modified_entities: List[str] = field(default_factory=list)
    added_signals: List[Tuple[str, str]] = field(default_factory=list)  # (entity_id, signal_name)
    removed_signals: List[Tuple[str, str]] = field(default_factory=list)
    changed_signals: List[Tuple[str, str, Any, Any]] = field(default_factory=list)  # (entity_id, signal_name, old_value, new_value)
    added_findings: List[str] = field(default_factory=list)  # Finding identity keys
    removed_findings: List[str] = field(default_factory=list)
    changed_findings: List[str] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        """Total number of changes."""
        return (
            len(self.added_entities)
            + len(self.removed_entities)
            + len(self.modified_entities)
            + len(self.added_signals)
            + len(self.removed_signals)
            + len(self.changed_signals)
            + len(self.added_findings)
            + len(self.removed_findings)
            + len(self.changed_findings)
        )
```

### 3.7 Insights Layer Data Models

**Core Abstractions:** Patterns → Findings → Results

*See Section 2.5 for `Finding`, `Evidence`, `AnalysisResult`.*

Additional pattern abstractions:

```python
from dataclasses import dataclass
from typing import Callable, Dict, List, Set, Any
from enum import Enum

class PatternScope(Enum):
    """Scope of a pattern."""
    FILE = "file"
    FILE_PAIR = "file_pair"
    MODULE = "module"
    MODULE_PAIR = "module_pair"
    CODEBASE = "codebase"

class PatternSeverity(Enum):
    """Severity categories."""
    CRITICAL = "critical"  # 0.8 - 1.0
    HIGH = "high"  # 0.6 - 0.8
    MEDIUM = "medium"  # 0.4 - 0.6
    LOW = "low"  # 0.2 - 0.4
    INFO = "info"  # 0.0 - 0.2

@dataclass
class PatternDef:
    """Definition of a finding pattern.

    Declarative pattern matching with predicate and severity functions.
    """
    name: str  # Pattern name (e.g., "high_risk_hub")
    category: str  # Category (existing, ai_quality, performance, etc.)
    scope: PatternScope  # Scope of pattern
    severity: PatternSeverity  # Default severity
    requires: Set[str]  # Required signals
    description: str  # Human-readable description
    remediation: str  # Remediation suggestion
    predicate: Callable[[EntityStore, EntityId], bool]  # Match predicate
    severity_fn: Callable[[EntityStore, EntityId], float]  # Severity function
    evidence_fn: Callable[[EntityStore, EntityId], List[Evidence]]  # Evidence function
    min_tier: int = 0  # Minimum analysis tier
    hotspot_filtered: bool = True  # Filter hotspots (top N per category)

    def match(self, store: EntityStore, entity_id: EntityId) -> bool:
        """Check if pattern matches entity."""
        return self.predicate(store, entity_id)

    def compute_severity(self, store: EntityStore, entity_id: EntityId) -> float:
        """Compute severity for matched entity."""
        return self.severity_fn(store, entity_id)

    def gather_evidence(self, store: EntityStore, entity_id: EntityId) -> List[Evidence]:
        """Gather evidence for matched entity."""
        return self.evidence_fn(store, entity_id)
```

---

## Phase 4: Layer Interfaces

### 4.1 Scanning Layer Interface

**Input:** File paths
**Output:** `FileAST` objects

```python
from typing import List, Dict, Set
from pathlib import Path

class ScanningProtocol(Protocol):
    """Protocol for scanning layer."""

    def scan_file(self, file_path: Path) -> FileAST:
        """Scan a single file, return AST."""
        ...

    def scan_directory(self, directory: Path) -> Dict[str, FileAST]:
        """Scan directory, return dict of path -> FileAST."""
        ...

    def get_supported_languages(self) -> Set[Language]:
        """Get set of supported languages."""
        ...

    def validate_file(self, file_path: Path) -> bool:
        """Check if file can be scanned."""
        ...
```

**Validation Rules:**
- All function start_line < end_line
- All class start_line < end_line
- All functions have valid names (non-empty, identifier chars)
- All imports have non-empty module names
- Line count matches file actual line count

### 4.2 Graph Layer Interface

**Input:** `FileAST` objects
**Output:** `DependencyGraph`, `GraphMetrics`

```python
class GraphProtocol(Protocol):
    """Protocol for graph layer."""

    def build_graph(self, file_asts: Dict[str, FileAST]) -> DependencyGraph:
        """Build dependency graph from ASTs."""
        ...

    def analyze_graph(self, graph: DependencyGraph) -> GraphMetrics:
        """Run graph algorithms, return metrics."""
        ...

    def get_subgraph(self, graph: DependencyGraph, node_ids: Set[EntityId]) -> DependencyGraph:
        """Extract subgraph for given nodes."""
        ...

    def validate_graph(self, graph: DependencyGraph) -> bool:
        """Validate graph invariants (no self-loops, etc.)."""
        ...
```

**Validation Rules:**
- No self-loops (A → A)
- All edge sources and targets are nodes in graph
- Edge weights in [0, 1]
- PageRank values sum to 1.0
- All nodes have degree >= 0

### 4.3 Temporal Layer Interface

**Input:** Git repository path
**Output:** Time series, temporal metrics

```python
class TemporalProtocol(Protocol):
    """Protocol for temporal layer."""

    def extract_events(self, repo_path: str) -> List[GitEvent]:
        """Extract git events."""
        ...

    def build_time_series(self, entity_id: EntityId, events: List[GitEvent]) -> TimeSeries:
        """Build time series for entity."""
        ...

    def compute_churn_metrics(self, time_series: TimeSeries) -> Dict[str, Any]:
        """Compute churn metrics from time series."""
        ...

    def detect_patterns(self, time_series: TimeSeries) -> List[str]:
        """Detect patterns (spiking, churning, etc.)."""
        ...
```

**Validation Rules:**
- Time series sorted by timestamp
- All timestamps are valid unix seconds
- No duplicate timestamps
- Churn trajectory in valid enum set
- Bus factor >= 1.0

### 4.4 Semantic Layer Interface

**Input:** `FileAST` objects
**Output:** `FileSemantics` objects

```python
class SemanticProtocol(Protocol):
    """Protocol for semantic layer."""

    def classify_role(self, file_ast: FileAST) -> Role:
        """Classify file role."""
        ...

    def extract_concepts(self, file_ast: FileAST) -> List[Concept]:
        """Extract semantic concepts."""
        ...

    def compute_completeness(self, file_ast: FileAST) -> CompletenessMetrics:
        """Compute completeness metrics."""
        ...

    def compute_naming_drift(self, file_ast: FileAST) -> float:
        """Compute naming drift [0, 1]."""
        ...
```

**Validation Rules:**
- Concept weights sum to 1.0
- Concept entropy in [0, log2(num_concepts)]
- Naming drift in [0, 1]
- TODO density >= 0.0
- Docstring coverage in [0, 1] or None

### 4.5 Infrastructure Layer Interface

**Input:** Data from all layers
**Output:** Unified `EntityStore`

```python
class InfrastructureProtocol(Protocol):
    """Protocol for infrastructure layer."""

    def create_entity(self, entity_type: EntityType, key: str, **metadata) -> EntityId:
        """Create new entity."""
        ...

    def set_signal(self, entity_id: EntityId, signal_name: str, value: SignalValue) -> None:
        """Set signal for entity."""
        ...

    def get_signal(self, entity_id: EntityId, signal_name: str) -> Optional[SignalValue]:
        """Get signal for entity."""
        ...

    def add_relation(self, relation: Relation) -> None:
        """Add relation between entities."""
        ...

    def query_signals(self, signal_name: str, min_value: Optional[float] = None) -> List[EntityId]:
        """Query entities by signal value."""
        ...

    def validate_store(self) -> bool:
        """Validate store integrity."""
        ...
```

**Validation Rules:**
- All signals registered in SIGNAL_REGISTRY
- Signal values match signal definition types
- All relation sources and targets exist
- No circular parent relationships

### 4.6 Persistence Layer Interface

**Input:** `EntityStore`, `AnalysisResult`
**Output:** `Snapshot`, `SnapshotDiff`

```python
class PersistenceProtocol(Protocol):
    """Protocol for persistence layer."""

    def create_snapshot(self, store: EntityStore, result: AnalysisResult, **metadata) -> Snapshot:
        """Create snapshot from current state."""
        ...

    def save_snapshot(self, snapshot: Snapshot, path: str) -> None:
        """Save snapshot to disk."""
        ...

    def load_snapshot(self, path: str) -> Snapshot:
        """Load snapshot from disk."""
        ...

    def diff_snapshots(self, from_snapshot: Snapshot, to_snapshot: Snapshot) -> SnapshotDiff:
        """Compute difference between snapshots."""
        ...

    def query_snapshot(self, snapshot: Snapshot, query: str) -> Any:
        """Query snapshot data."""
        ...
```

**Validation Rules:**
- Snapshot validates successfully
- All finding identity keys are unique
- All signal percentiles in [0, 100]
- All finding severities and confidences in [0, 1]

### 4.7 Insights Layer Interface

**Input:** `EntityStore`, `PatternDef` objects
**Output:** `Finding` objects, `AnalysisResult`

```python
class InsightsProtocol(Protocol):
    """Protocol for insights layer."""

    def execute_patterns(self, store: EntityStore, patterns: List[PatternDef]) -> List[Finding]:
        """Execute patterns, return findings."""
        ...

    def rank_findings(self, findings: List[Finding]) -> List[Finding]:
        """Rank findings by severity."""
        ...

    def deduplicate_findings(self, findings: List[Finding]) -> List[Finding]:
        """Deduplicate findings by identity_key."""
        ...

    def filter_findings(self, findings: List[Finding], max_count: int) -> List[Finding]:
        """Filter to top N findings."""
        ...

    def generate_result(self, findings: List[Finding], **summary) -> AnalysisResult:
        """Generate final analysis result."""
        ...
```

**Validation Rules:**
- All findings validate successfully
- No duplicate identity keys
- Sorted by severity descending
- Count <= max_count

---

## Phase 5: Data Flow Design

### 5.1 End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Source Code                                │
│                    (files on disk)                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  1. SCANNING LAYER                                              │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Input: File paths                                            │ │
│  │ Process: Parse files (tree-sitter/regex)                       │ │
│  │ Output: FileAST objects                                       │ │
│  │ Validation: AST integrity, line numbers, valid identifiers      │ │
│  └────────────────────────────┬─────────────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. GRAPH LAYER                                                  │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Input: FileAST objects (imports)                              │ │
│  │ Process: Build dependency graph, run algorithms               │ │
│  │ Output: DependencyGraph, GraphMetrics                        │ │
│  │ Validation: No self-loops, valid edges, PageRank sum=1.0   │ │
│  └────────────────────────────┬─────────────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. SEMANTIC LAYER                                               │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Input: FileAST objects                                       │ │
│  │ Process: Classify roles, extract concepts, compute metrics    │ │
│  │ Output: FileSemantics objects                                │ │
│  │ Validation: Concept weights sum=1.0, valid role enum        │ │
│  └────────────────────────────┬─────────────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  4. TEMPORAL LAYER                                              │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Input: Git repository path                                  │ │
│  │ Process: Extract events, build time series, compute metrics  │ │
│  │ Output: TimeSeries, ChurnMetrics per entity                 │ │
│  │ Validation: Sorted timestamps, valid unix seconds            │ │
│  └────────────────────────────┬─────────────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  5. INFRASTRUCTURE LAYER (Unified Storage)                       │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Input: Data from all layers (FileAST, Graph, Semantics, etc.)│ │
│  │ Process: Create entities, set signals, add relations        │ │
│  │ Output: EntityStore (entities + signals + relations)       │ │
│  │ Validation: Registered signals, valid values, no cycles     │ │
│  └────────────────────────────┬─────────────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  6. INSIGHTS LAYER                                               │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Input: EntityStore, PatternDefs                              │ │
│  │ Process: Execute patterns, compute severity, gather evidence   │ │
│  │ Output: Finding objects                                      │ │
│  │ Validation: Severity [0,1], confidence [0,1], valid effort │ │
│  └────────────────────────────┬─────────────────────────────────────┘ │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  7. PERSISTENCE LAYER                                            │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Input: EntityStore, Findings, metadata                      │ │
│  │ Process: Serialize to Snapshot, save to disk                │ │
│  │ Output: Snapshot files (.parquet, .sqlite)                │ │
│  │ Validation: Snapshot integrity, unique finding keys         │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Transformation Functions

**Function:** `scan_file(file_path: Path) -> FileAST`
- Input: File on disk
- Output: Parsed AST
- Validation: Check line counts, identifier validity
- Error handling: Return `None` for unparseable files

**Function:** `build_graph(file_asts: Dict[str, FileAST]) -> DependencyGraph`
- Input: Dictionary of file ASTs
- Output: Dependency graph
- Transformation: Map imports → edges
- Validation: No self-loops, all nodes added

**Function:** `analyze_graph(graph: DependencyGraph) -> GraphMetrics`
- Input: Dependency graph
- Output: Computed metrics (PageRank, betweenness, etc.)
- Transformation: Run graph algorithms
- Validation: PageRank sums to 1.0, no negative metrics

**Function:** `classify_role(file_ast: FileAST) -> Role`
- Input: File AST
- Output: Role enum
- Transformation: Apply heuristics (patterns, decorators, etc.)
- Validation: Return valid Role enum value

**Function:** `extract_concepts(file_ast: FileAST) -> List[Concept]`
- Input: File AST
- Output: List of concepts
- Transformation: Extract keywords, cluster, weight
- Validation: Weights sum to 1.0, no duplicates

**Function:** `build_time_series(entity_id: EntityId, events: List[GitEvent]) -> TimeSeries`
- Input: Entity ID and git events
- Output: Time series
- Transformation: Aggregate events by time window
- Validation: Sorted timestamps, no duplicates

**Function:** `compute_churn_metrics(time_series: TimeSeries) -> Dict[str, Any]`
- Input: Time series
- Output: Churn metrics (trajectory, slope, cv, etc.)
- Transformation: Compute statistics, classify trajectory
- Validation: Valid trajectory enum, slope in range

### 5.3 Validation Checkpoints

**Checkpoint 1: After Scanning**
- Validate all `FileAST` objects
- Check line counts match actual files
- Validate function/class boundaries

**Checkpoint 2: After Graph Building**
- Validate `DependencyGraph`
- Check no self-loops
- Check all edge nodes exist

**Checkpoint 3: After Graph Analysis**
- Validate `GraphMetrics`
- Check PageRank sums to 1.0
- Check no negative metrics

**Checkpoint 4: After Semantic Analysis**
- Validate `FileSemantics`
- Check concept weights sum to 1.0
- Check role enum valid

**Checkpoint 5: After Temporal Analysis**
- Validate `TimeSeries`
- Check sorted timestamps
- Check valid unix seconds

**Checkpoint 6: After Infrastructure**
- Validate `EntityStore`
- Check all signals registered
- Check signal value types match definitions

**Checkpoint 7: After Insights**
- Validate `Finding` objects
- Check severity in [0, 1]
- Check confidence in [0, 1]

**Checkpoint 8: After Persistence**
- Validate `Snapshot`
- Check snapshot integrity
- Check unique finding keys

---

## Phase 6: Protocol-Based Interfaces

### 6.1 Layer Protocols

**Unified protocol for all layers:**

```python
from typing import Protocol, TypeVar, Generic, List, Dict, Any
from abc import abstractmethod

T = TypeVar('T')

class Layer(Protocol):
    """Base protocol for all analysis layers."""

    name: str
    phase: int

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        ...

    @abstractmethod
    def process(self, input_data: Any, context: Dict[str, Any]) -> T:
        """Process input data, produce output."""
        ...

    @abstractmethod
    def validate_output(self, output_data: T) -> bool:
        """Validate output data."""
        ...

class ScanningLayer(Layer, Generic[T]):
    """Protocol for scanning layer."""

    @abstractmethod
    def scan_file(self, file_path: str) -> T:
        """Scan a single file."""
        ...

class AnalysisLayer(Layer, Generic[T]):
    """Protocol for analysis layers."""

    @abstractmethod
    def analyze(self, input_data: Any, store: EntityStore) -> T:
        """Analyze input data with context from store."""
        ...

class PersistenceLayer(Layer, Generic[T]):
    """Protocol for persistence layer."""

    @abstractmethod
    def save(self, data: T, path: str) -> None:
        """Save data to disk."""
        ...

    @abstractmethod
    def load(self, path: str) -> T:
        """Load data from disk."""
        ...
```

### 6.2 Data Transformation Protocols

**Protocol for transforming between layers:**

```python
class Transformer(Protocol, Generic[T, U]):
    """Protocol for data transformations between layers."""

    @abstractmethod
    def transform(self, input_data: T) -> U:
        """Transform input data to output type."""
        ...

    @abstractmethod
    def validate_transform(self, input_data: T, output_data: U) -> bool:
        """Validate transformation correctness."""
        ...

# Example: FileAST → DependencyGraph
class ASTToGraphTransformer(Transformer[Dict[str, FileAST], DependencyGraph]):
    """Transform FileASTs to DependencyGraph."""

    def transform(self, file_asts: Dict[str, FileAST]) -> DependencyGraph:
        """Build dependency graph from ASTs."""
        graph = DependencyGraph()
        for file_id, ast in file_asts.items():
            graph.add_node(ast.file_id)
            for imp in ast.imports:
                if imp.is_resolved:
                    target_id = EntityId(EntityType.FILE, imp.resolved_path)
                    edge = Edge(ast.file_id, target_id, EdgeType.IMPORT)
                    graph.add_edge(edge)
        return graph

    def validate_transform(self, file_asts: Dict[str, FileAST], graph: DependencyGraph) -> bool:
        """Validate graph matches ASTs."""
        # Check that all files are nodes
        file_ids = {ast.file_id for ast in file_asts.values()}
        return file_ids == graph.nodes
```

### 6.3 Query Protocols

**Protocol for querying layer outputs:**

```python
class Query(Protocol, Generic[T]):
    """Protocol for querying layer outputs."""

    @abstractmethod
    def query(self, data: T, query_str: str, **params) -> Any:
        """Execute query on data."""
        ...

class GraphQuery(Query[DependencyGraph]):
    """Query dependency graph."""

    def query(self, graph: DependencyGraph, query_str: str, **params) -> Any:
        """Execute graph query."""
        if query_str == "neighbors":
            node_id = params.get("node_id")
            direction = params.get("direction", "outgoing")
            if direction == "outgoing":
                return graph.get_outgoing(node_id)
            else:
                return graph.get_incoming(node_id)
        elif query_str == "subgraph":
            node_ids = params.get("node_ids", set())
            return extract_subgraph(graph, node_ids)
        # ... more queries
```

---

## Phase 7: Migration Strategy

### 7.1 Migration Phases

**Phase 1: Foundation (Week 1-4)**
- Define new core abstractions (`Entity`, `Signal`, `Relation`)
- Implement `EntityStore` (unified storage)
- Add validation functions for all data models
- Write unit tests for new abstractions

**Phase 2: Layer Migration (Week 5-12)**
- Migrate scanning layer to use `FileAST`
- Migrate graph layer to use `DependencyGraph`, `GraphMetrics`
- Migrate semantic layer to use `FileSemantics`
- Migrate temporal layer to use new event model (see TEMPORAL-MODULE-REDESIGN.md)
- Update analyzers to write to `EntityStore`

**Phase 3: Remove Dual Storage (Week 13-16)**
- Remove `AnalysisStore` slots
- Migrate all analyzers to use `EntityStore`
- Remove `_sync_entities()` bridge
- Update finders to read from `EntityStore`
- Update tests

**Phase 4: Update Persistence (Week 17-20)**
- Migrate to new `Snapshot` schema (v3)
- Update `capture.py` to serialize `EntityStore`
- Update `diff_engine.py` to use `SnapshotDiff`
- Migrate existing v1/v2 snapshots to v3

**Phase 5: Clean Up (Week 21-24)**
- Remove old data models
- Update documentation
- Deprecate old APIs
- Add migration warnings

### 7.2 Backward Compatibility

**Adapter Pattern:**

```python
class AnalysisStoreAdapter:
    """Adapter from old AnalysisStore to new EntityStore."""

    def __init__(self, entity_store: EntityStore):
        self._store = entity_store

    @property
    def file_syntax(self) -> Slot[Dict[str, FileSyntax]]:
        """Adapter for file_syntax slot."""
        # Read from EntityStore and convert to old format
        file_entities = self._store.get_entities_in_scope(SignalScope.FILE)
        file_syntax_dict = {}
        for entity_id in file_entities:
            # Convert Entity to FileSyntax
            file_syntax_dict[entity_id.key] = self._entity_to_file_syntax(entity_id)
        return Slot(value=file_syntax_dict)

    def _entity_to_file_syntax(self, entity_id: EntityId) -> FileSyntax:
        """Convert Entity to FileSyntax (old format)."""
        # Read signals from EntityStore
        lines_signal = self._store.get_signal(entity_id, "lines")
        function_count_signal = self._store.get_signal(entity_id, "function_count")
        # ... more signals
        return FileSyntax(
            path=entity_id.key,
            lines=lines_signal.value if lines_signal else 0,
            function_count=function_count_signal.value if function_count_signal else 0,
            # ... more fields
        )
```

### 7.3 Data Migration

**Migrate v1/v2 snapshots to v3:**

```python
def migrate_snapshot_v2_to_v3(v2_snapshot: TensorSnapshot) -> Snapshot:
    """Migrate v2 snapshot to v3 format."""
    # Create entities
    entities = []
    for file_path in v2_snapshot.file_signals.keys():
        entity_id = EntityId(EntityType.FILE, file_path)
        entities.append({
            "id": str(entity_id),
            "type": EntityType.FILE.value,
            "key": file_path,
            "parent": None,
            "metadata": {},
        })

    # Create signals
    signals = []
    for file_path, file_signals in v2_snapshot.file_signals.items():
        entity_id = EntityId(EntityType.FILE, file_path)
        for signal_name, value in file_signals.items():
            signals.append({
                "entity_id": str(entity_id),
                "signal_name": signal_name,
                "value": value,
                "percentile": None,  # Not stored in v2
            })

    # Create metadata
    metadata = SnapshotMetadata(
        schema_version=3,
        tool_version=v2_snapshot.tool_version,
        git_sha=v2_snapshot.commit_sha,
        analyzed_path=v2_snapshot.analyzed_path,
        file_count=v2_snapshot.file_count,
        module_count=v2_snapshot.module_count,
    )

    # Create data
    data = SnapshotData(
        entities=entities,
        signals=signals,
        relations=v2_snapshot.dependency_edges,  # Convert to relations
        findings=[f.dict() for f in v2_snapshot.findings],
    )

    return Snapshot(metadata=metadata, data=data)
```

---

## Key Design Decisions

### Decision 1: Entity Identity

**Choice:** Use stable `EntityId` with type + key, tracking renames via lineage.

**Rationale:**
- Files can be renamed/moved; path-based IDs break
- Type + key uniquely identifies entity across transformations
- Lineage tracking enables historical reconstruction

**Trade-offs:**
- ✅ Pros: Stable identity, rename tracking, historical analysis
- ❌ Cons: Requires identity resolution logic, more complex

### Decision 2: Signal Value Types

**Choice:** Strongly typed signal values with validation (`SignalValue`).

**Rationale:**
- Prevents type errors at runtime
- Enables auto-documentation via type hints
- Catches invalid data early

**Trade-offs:**
- ✅ Pros: Type safety, validation, self-documenting
- ❌ Cons: More verbose, requires runtime type checking

### Decision 3: Immutable Data Models

**Choice:** Use `@dataclass(frozen=True)` for core data models.

**Rationale:**
- Prevents accidental mutation
- Enables hashability (can use as dict keys, set members)
- Thread-safe (no concurrent modification)

**Trade-offs:**
- ✅ Pros: Safety, hashability, immutability guarantees
- ❌ Cons: Cannot update fields, need to create new instances

### Decision 4: Single Storage (EntityStore)

**Choice:** Replace dual storage (`AnalysisStore` + `FactStore`) with unified `EntityStore`.

**Rationale:**
- Eliminates synchronization complexity
- Single source of truth
- Simpler testing and debugging

**Trade-offs:**
- ✅ Pros: Simplicity, no sync issues, single source of truth
- ❌ Cons: Large migration effort, backward compatibility work

### Decision 5: Layer Protocols

**Choice:** Define protocol-based interfaces for all layers.

**Rationale:**
- Enables loose coupling
- Allows layer swapping (e.g., different graph algorithms)
- Makes testing easier (mock protocols)

**Trade-offs:**
- ✅ Pros: Loose coupling, testability, extensibility
- ❌ Cons: More boilerplate, protocol checking at runtime

### Decision 6: Validation at Boundaries

**Choice:** Validate data at every layer boundary (input/output).

**Rationale:**
- Catches errors early
- Provides clear error messages
- Ensures data integrity across layers

**Trade-offs:**
- ✅ Pros: Early error detection, clear errors, data integrity
- ❌ Cons: Performance overhead, more code

### Decision 7: Typed Time Series

**Choice:** Use explicit `TimeSeries` dataclass with `TimeSeriesPoint`.

**Rationale:**
- Self-documenting (has unit, start/end timestamps)
- Type-safe (can't mix with raw lists)
- Enables validation (sorted, no duplicates)

**Trade-offs:**
- ✅ Pros: Type safety, self-documenting, validation
- ❌ Cons: More verbose than raw list

### Decision 8: Finding Identity Keys

**Choice:** Compute stable hash from finding type, files, and evidence.

**Rationale:**
- Enables tracking findings across snapshots
- Supports lifecycle analysis (new, recurring, resolved)
- Deduplicates findings across runs

**Trade-offs:**
- ✅ Pros: Stable identity, lifecycle tracking, deduplication
- ❌ Cons: Hash computation overhead, need consistent serialization

### Decision 9: Graph with Typed Edges

**Choice:** Use `Edge` dataclass with `EdgeType` enum.

**Rationale:**
- Explicit edge semantics (import vs call vs inherits)
- Enables weighted edges
- Supports multiple edge types in same graph

**Trade-offs:**
- ✅ Pros: Explicit semantics, weighted edges, multiple types
- ❌ Cons: More complex than simple string pairs

### Decision 10: Frozen Findings

**Choice:** `Finding` dataclass is mutable, but `identity_key` is computed property.

**Rationale:**
- Findings need to be mutable for severity adjustment
- Identity key is stable once computed
- Enables post-processing (ranking, filtering)

**Trade-offs:**
- ✅ Pros: Flexible for post-processing, stable identity
- ❌ Cons: Not truly immutable, careful with identity_key timing

---

## Summary

This document proposes a unified, type-safe data object architecture for Shannon Insight that:

1. **Eliminates dual storage** by providing a single `EntityStore`
2. **Provides stable identity** for entities across renames via `EntityId`
3. **Defines typed signal values** with validation and metadata
4. **Creates clear layer boundaries** with protocol-based interfaces
5. **Validates data at every transformation** for early error detection
6. **Supports historical analysis** via lineage tracking and snapshot diffs
7. **Enables lifecycle tracking** via stable finding identity keys

The architecture is production-ready with a 24-week migration plan that maintains backward compatibility through adapters.

**Key Benefits:**
- Type safety and validation prevent runtime errors
- Stable entity identity enables historical analysis
- Single storage eliminates synchronization complexity
- Clear layer boundaries enable loose coupling
- Protocol-based interfaces enable extensibility

**Next Steps:**
1. Implement core abstractions (Entity, Signal, Relation)
2. Build `EntityStore` with validation
3. Migrate scanning layer to new data models
4. Gradually migrate other layers
5. Remove dual storage and legacy code
