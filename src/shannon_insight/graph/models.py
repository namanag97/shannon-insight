"""Data models for multi-level codebase analysis.

Ontology levels:
  Level 1: Constructs (functions, classes) — extracted by scanner
  Level 2: Relationships (imports, calls) — dependency graph edges
  Level 3: Containers (files, modules) — filesystem groupings
  Level 4: Derived structures (communities, cycles, blast cones)
  Level 5: Measurements (scalars on all levels above)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ── Level 2: Relationships (the dependency graph) ──────────────────


@dataclass
class DependencyGraph:
    """First-class dependency graph built from import relationships.

    Edges are directed: adjacency[A] contains B means A imports/depends on B.
    """

    adjacency: dict[str, list[str]] = field(default_factory=dict)
    reverse: dict[str, list[str]] = field(default_factory=dict)
    all_nodes: set[str] = field(default_factory=set)
    edge_count: int = 0

    # Phase 3: track unresolved imports for phantom_import_count signal
    unresolved_imports: dict[str, list[str]] = field(default_factory=dict)


# ── Phase 2: Multi-type graph ──────────────────────────────────────


class NodeType(Enum):
    """Types of nodes in the multi-type code graph."""

    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    TYPE = "type"  # Type annotation nodes (e.g., "str", "list[int]", "MyClass")


class EdgeType(Enum):
    """Types of edges in the multi-type code graph."""

    IMPORTS = "imports"  # FILE -> FILE
    CALLS = "calls"  # FUNCTION -> FUNCTION
    INHERITS = "inherits"  # CLASS -> CLASS
    CONTAINS = "contains"  # FILE -> FUNCTION/CLASS
    RETURNS = "returns"  # FUNCTION -> TYPE (return type)
    PARAM_TYPE = "param_type"  # FUNCTION -> TYPE (parameter type)
    FIELD_TYPE = "field_type"  # CLASS -> TYPE (field type)


@dataclass
class CodeGraph:
    """Multi-type dependency graph built from parsed facts.

    This graph tracks relationships at four levels:
    - FILE level: import dependencies between files
    - FUNCTION level: call relationships between functions
    - CLASS level: inheritance relationships between classes
    - TYPE level: type annotation dependencies

    Node IDs:
    - FILE nodes: relative file path (e.g., "src/foo.py")
    - FUNCTION nodes: "file:qualified_name" (e.g., "src/foo.py:MyClass.method")
    - CLASS nodes: "file:ClassName" (e.g., "src/foo.py:MyClass")
    - TYPE nodes: normalized type string (e.g., "str", "list[int]", "MyClass")

    This graph is computed from FactDatabase, not stored.
    """

    # Nodes by type
    file_nodes: set[str] = field(default_factory=set)
    function_nodes: set[str] = field(default_factory=set)  # "file:qualified_name"
    class_nodes: set[str] = field(default_factory=set)  # "file:ClassName"
    type_nodes: set[str] = field(default_factory=set)  # Normalized type strings

    # Edges by type (adjacency lists: source -> [targets])
    import_edges: dict[str, list[str]] = field(default_factory=dict)  # FILE -> FILE
    call_edges: dict[str, list[str]] = field(default_factory=dict)  # FUNC -> FUNC
    inherit_edges: dict[str, list[str]] = field(default_factory=dict)  # CLASS -> CLASS
    contains_edges: dict[str, list[str]] = field(default_factory=dict)  # FILE -> FUNC/CLASS

    # Type flow edges (NEW)
    returns_edges: dict[str, str] = field(default_factory=dict)  # FUNC -> TYPE
    param_type_edges: dict[str, dict[str, str]] = field(
        default_factory=dict
    )  # FUNC -> {param: TYPE}
    field_type_edges: dict[str, dict[str, str]] = field(
        default_factory=dict
    )  # CLASS -> {field: TYPE}

    # Reverse indexes (for efficient lookups)
    imported_by: dict[str, list[str]] = field(default_factory=dict)  # FILE <- FILE
    called_by: dict[str, list[str]] = field(default_factory=dict)  # FUNC <- FUNC
    inherited_by: dict[str, list[str]] = field(default_factory=dict)  # CLASS <- CLASS
    contained_in: dict[str, str] = field(default_factory=dict)  # FUNC/CLASS -> FILE
    used_by: dict[str, list[str]] = field(default_factory=dict)  # TYPE <- FUNC/CLASS

    # Statistics
    @property
    def total_nodes(self) -> int:
        return (
            len(self.file_nodes)
            + len(self.function_nodes)
            + len(self.class_nodes)
            + len(self.type_nodes)
        )

    @property
    def total_edges(self) -> int:
        return (
            sum(len(v) for v in self.import_edges.values())
            + sum(len(v) for v in self.call_edges.values())
            + sum(len(v) for v in self.inherit_edges.values())
            + sum(len(v) for v in self.contains_edges.values())
            + len(self.returns_edges)
            + sum(len(v) for v in self.param_type_edges.values())
            + sum(len(v) for v in self.field_type_edges.values())
        )


# ── Level 4: Derived structures ────────────────────────────────────


@dataclass
class CycleGroup:
    """A strongly connected component with more than one node (a real cycle)."""

    nodes: set[str]
    internal_edge_count: int = 0


@dataclass
class Community:
    """A group of files discovered by modularity optimization."""

    id: int
    members: set[str]


@dataclass
class GraphAnalysis:
    """All derived structures from graph algorithms."""

    # Per-node measurements (Level 5 on Level 4 structures)
    pagerank: dict[str, float] = field(default_factory=dict)
    betweenness: dict[str, float] = field(default_factory=dict)
    in_degree: dict[str, int] = field(default_factory=dict)
    out_degree: dict[str, int] = field(default_factory=dict)

    # Blast radius: file -> set of files transitively affected
    blast_radius: dict[str, set[str]] = field(default_factory=dict)

    # Cycle groups (only SCCs with > 1 node)
    cycles: list[CycleGroup] = field(default_factory=list)

    # Community detection
    communities: list[Community] = field(default_factory=list)
    node_community: dict[str, int] = field(default_factory=dict)
    modularity_score: float = 0.0

    # Phase 3 additions:
    depth: dict[str, int] = field(
        default_factory=dict
    )  # BFS depth from entry points, -1 = unreachable
    is_orphan: dict[str, bool] = field(default_factory=dict)  # in_degree=0 AND not entry_point/test
    centrality_gini: float = 0.0  # Gini coefficient of pagerank distribution
    spectral_gap: float = 0.0  # λ₂/λ₃ (moved from SpectralSummary)

    # Phase 2 additions: Function-level analysis
    function_pagerank: dict[str, float] = field(default_factory=dict)  # FUNC -> pagerank
    function_betweenness: dict[str, float] = field(default_factory=dict)  # FUNC -> betweenness
    dead_functions: set[str] = field(default_factory=set)  # FUNC with no callers
    function_cycles: list[set[str]] = field(default_factory=list)  # SCCs in call graph

    # Phase 2 additions: Class-level analysis
    inheritance_depth: dict[str, int] = field(default_factory=dict)  # CLASS -> depth
    diamond_classes: list[str] = field(default_factory=list)  # Classes with diamond inheritance

    # Phase 2 additions: Cross-cutting
    hotspot_functions: list[str] = field(default_factory=list)  # High centrality + high churn


# ── Level 3 + 5: Container measurements ───────────────────────────


@dataclass
class ModuleAnalysis:
    """Per-module (directory) analysis."""

    path: str
    files: list[str] = field(default_factory=list)
    file_count: int = 0

    # Coupling/cohesion (ratio scale)
    internal_edges: int = 0
    external_edges_out: int = 0
    external_edges_in: int = 0
    cohesion: float = 0.0  # internal / possible_internal
    coupling: float = 0.0  # external / total

    # What communities do this module's files belong to?
    # If all files in one community -> well-aligned boundary
    # If spread across many -> misaligned boundary
    community_ids: set[int] = field(default_factory=set)
    boundary_alignment: float = 0.0  # 1.0 = all in same community

    # Phase 4 additions: Martin metrics
    instability: Optional[float] = None  # Ce / (Ca + Ce), None if isolated
    abstractness: float = 0.0  # abstract_symbols / total_symbols
    main_seq_distance: float = 0.0  # |A + I - 1|
    role_consistency: float = 0.0  # max(role_count) / total_files
    layer: int = -1  # Layer assignment (-1 = unassigned)
    layer_violation_count: int = 0  # Number of violations from this module


# ── Level 1 + 5: Per-file measurements ────────────────────────────


@dataclass
class FileAnalysis:
    """Per-file measurements combining construct-level and graph-level data."""

    path: str
    lines: int = 0
    function_count: int = 0

    # Construct-level measurements (Level 1 → Level 5)
    compression_ratio: float = 0.0
    cognitive_load: float = 0.0
    function_size_gini: float = 0.0
    max_function_size: int = 0
    nesting_depth: int = 0

    # Graph-level measurements for this file (Level 4 → Level 5)
    pagerank: float = 0.0
    betweenness: float = 0.0
    in_degree: int = 0
    out_degree: int = 0
    blast_radius_size: int = 0
    cycle_member: bool = False
    community_id: int = -1

    # Direct dependencies
    depends_on: list[str] = field(default_factory=list)
    depended_on_by: list[str] = field(default_factory=list)

    # Phase 3 additions:
    depth: int = -1  # BFS depth from entry points, -1 = unreachable
    is_orphan: bool = False  # in_degree=0 AND not entry_point/test
    phantom_import_count: int = 0  # number of unresolved imports


# ── Level 3 + 4 comparison: Declared vs Discovered ────────────────


@dataclass
class BoundaryMismatch:
    """When declared module boundaries don't match discovered communities."""

    module_path: str
    declared_files: set[str] = field(default_factory=set)
    community_distribution: dict[int, int] = field(default_factory=dict)
    # Files in this module that are more connected to another module
    misplaced_files: list[tuple[str, str]] = field(default_factory=list)  # (file, suggested_module)


# ── Phase 3: Clone detection and author distance ──────────────────


@dataclass
class ClonePair:
    """A pair of files detected as clones via NCD."""

    file_a: str
    file_b: str
    ncd: float  # Normalized Compression Distance, lower = more similar
    size_a: int  # bytes
    size_b: int


@dataclass
class AuthorDistance:
    """G5 distance space entry: author-based file distance."""

    file_a: str
    file_b: str
    distance: float  # 1 - weighted Jaccard overlap of author distributions


@dataclass
class SpectralSummary:
    """Spectral analysis summary from graph Laplacian.

    Moved from temporal/models.py to graph/models.py since this is
    graph spectral analysis, not temporal analysis.
    """

    fiedler_value: float  # algebraic connectivity (λ₂)
    num_components: int  # connected components
    eigenvalues: list[float]  # sorted ascending
    spectral_gap: float  # ratio of λ₂/λ₃


# ── Full result ────────────────────────────────────────────────────


@dataclass
class CodebaseAnalysis:
    """Complete multi-level analysis result. Queryable, not scored."""

    # Per-entity results
    files: dict[str, FileAnalysis] = field(default_factory=dict)
    modules: dict[str, ModuleAnalysis] = field(default_factory=dict)

    # Graph and derived structures
    graph: DependencyGraph = field(default_factory=DependencyGraph)
    graph_analysis: GraphAnalysis = field(default_factory=GraphAnalysis)

    # Boundary analysis
    boundary_mismatches: list[BoundaryMismatch] = field(default_factory=list)

    # Codebase-level summary
    total_files: int = 0
    total_modules: int = 0
    total_edges: int = 0
    cycle_count: int = 0
    modularity: float = 0.0

    # Statistical outliers (file -> list of reasons)
    outliers: dict[str, list[str]] = field(default_factory=dict)
