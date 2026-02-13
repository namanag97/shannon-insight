"""Data models for signal computation.

Phase 5: Full signal model with FileSignals, ModuleSignals, GlobalSignals, SignalField.
Backward compatibility: Primitives class preserved with from_file_signals() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

PrimitiveValues = dict[str, float]


@dataclass
class FileSignals:
    """All per-file signals from registry/signals.md #1-36.

    Populated by SignalFusion.build() from store slots.
    """

    path: str = ""

    # Hierarchical context (computed from path)
    parent_dir: str = ""  # Immediate parent directory (e.g., "src/api")
    module_path: str = ""  # Which module this file belongs to (from architecture)
    dir_depth: int = 0  # Nesting level from root (0 = root, 1 = one level deep, etc.)
    siblings_count: int = 0  # Other files in same directory

    # IR1 (scanning) - signals #1-7
    lines: int = 0
    function_count: int = 0
    class_count: int = 0  # structs in FileMetrics
    max_nesting: int = 0  # nesting_depth in FileMetrics
    impl_gini: float = 0.0  # function_size_gini in FileAnalysis
    stub_ratio: float = 0.0
    import_count: int = 0

    # IR2 (semantics) - signals #8-13
    role: str = "UNKNOWN"
    concept_count: int = 1
    concept_entropy: float = 0.0
    naming_drift: float = 0.0
    todo_density: float = 0.0
    docstring_coverage: float | None = None

    # IR3 (graph) - signals #14-26
    pagerank: float = 0.0
    betweenness: float = 0.0
    in_degree: int = 0
    out_degree: int = 0
    blast_radius_size: int = 0
    depth: int = -1  # BFS depth from entry points, -1 = unreachable
    is_orphan: bool = False
    phantom_import_count: int = 0
    broken_call_count: int = 0  # 0 until CALL edges exist
    community: int = -1
    compression_ratio: float = 0.0
    semantic_coherence: float = 0.0  # import-based coherence
    cognitive_load: float = 0.0

    # IR5t (temporal) - signals #27-34
    total_changes: int = 0
    churn_trajectory: str = "DORMANT"  # STABILIZING|CHURNING|SPIKING|DORMANT
    churn_slope: float = 0.0
    churn_cv: float = 0.0  # coefficient of variation
    bus_factor: float = 1.0  # 2^H where H = author entropy
    author_entropy: float = 0.0
    fix_ratio: float = 0.0
    refactor_ratio: float = 0.0
    change_entropy: float = 0.0  # Shannon entropy of change distribution across time windows

    # Pre-percentile risk (used by health Laplacian BEFORE percentile normalization)
    raw_risk: float = 0.0

    # Composites (computed by this phase, AFTER percentile normalization)
    risk_score: float = 0.0  # percentile-based composite (#35)
    wiring_quality: float = 1.0  # (#36)
    file_health_score: float = 1.0  # Per-file health composite

    # Percentiles (filled by normalization)
    percentiles: dict[str, float] = field(default_factory=dict)


@dataclass
class ModuleSignals:
    """All per-module signals from registry/signals.md #37-51.

    Populated by SignalFusion from Architecture and temporal aggregation.
    """

    path: str = ""

    # Martin metrics (from architecture/) - signals #37-41
    cohesion: float = 0.0
    coupling: float = 0.0
    instability: float | None = None  # None if isolated module (Ca=Ce=0)
    abstractness: float = 0.0
    main_seq_distance: float = 0.0  # 0.0 if instability is None

    # Boundary analysis - signals #42-44
    boundary_alignment: float = 0.0
    layer_violation_count: int = 0
    role_consistency: float = 0.0

    # Module temporal - signals #45-48 (aggregated from per-file)
    velocity: float = 0.0  # commits/week touching module
    coordination_cost: float = 0.0
    knowledge_gini: float = 0.0
    module_bus_factor: float = 1.0

    # Aggregated file signals - signals #49-50
    mean_cognitive_load: float = 0.0
    file_count: int = 0

    # Composite - signal #51
    health_score: float = 0.0


@dataclass
class DirectorySignals:
    """Per-directory aggregate signals.

    Provides a middle layer between FileSignals and ModuleSignals.
    Directories are filesystem-based (every unique parent_dir),
    while Modules are logical groupings that may span multiple directories.
    """

    path: str = ""  # Directory path (e.g., "src/api", "tests/unit")

    # Basic counts
    file_count: int = 0
    total_lines: int = 0
    total_functions: int = 0

    # Aggregate metrics (means across files in directory)
    avg_complexity: float = 0.0  # Mean cognitive_load
    avg_churn: float = 0.0  # Mean total_changes
    avg_risk: float = 0.0  # Mean risk_score

    # Cohesion: what % of imports stay within this directory
    internal_import_ratio: float = 0.0  # internal_imports / total_imports

    # Dominant characteristics
    dominant_role: str = "UNKNOWN"  # Most common role among files
    dominant_trajectory: str = "DORMANT"  # Most common churn trajectory

    # Risk indicators
    hotspot_file_count: int = 0  # Files with total_changes > median
    high_risk_file_count: int = 0  # Files with risk_score > 0.7

    # Module relationship
    module_path: str = ""  # Which module this directory belongs to


@dataclass
class GlobalSignals:
    """All global signals from registry/signals.md #52-62.

    Populated by SignalFusion from graph analysis and aggregation.
    """

    # Graph structure - signals #52-56
    modularity: float = 0.0
    fiedler_value: float = 0.0
    spectral_gap: float = 0.0
    cycle_count: int = 0
    centrality_gini: float = 0.0

    # Wiring quality - signals #57-59
    orphan_ratio: float = 0.0
    phantom_ratio: float = 0.0
    glue_deficit: float = 0.0

    # Phase 3/4 derived signals (needed for composites)
    clone_ratio: float = 0.0  # From Phase 3 clone detection
    violation_rate: float = 0.0  # From Phase 4 architecture
    conway_alignment: float = 1.0  # From Phase 3 author distances (1.0 = perfect alignment)
    team_size: int = 1  # From Phase 3 git history

    # Composites - signals #60-62
    wiring_score: float = 0.0
    architecture_health: float = 0.0
    team_risk: float = 0.0  # Not numbered in signals.md, display-only
    codebase_health: float = 0.0


@dataclass
class SignalField:
    """Unified signal container. One-stop shop for all signals.

    This is what finders read from. All 62 signals accessible here.
    Hierarchy: per_file -> per_directory -> per_module -> global_signals
    """

    tier: str = "FULL"  # "ABSOLUTE" | "BAYESIAN" | "FULL"
    per_file: dict[str, FileSignals] = field(default_factory=dict)
    per_directory: dict[str, DirectorySignals] = field(default_factory=dict)
    per_module: dict[str, ModuleSignals] = field(default_factory=dict)
    global_signals: GlobalSignals = field(default_factory=GlobalSignals)
    delta_h: dict[str, float] = field(default_factory=dict)  # Health Laplacian per file

    def file(self, path: str) -> FileSignals | None:
        """Get FileSignals for a path, or None if not found."""
        return self.per_file.get(path)

    def directory(self, path: str) -> DirectorySignals | None:
        """Get DirectorySignals for a directory path, or None if not found."""
        return self.per_directory.get(path)

    def top_files_by_risk(self, n: int = 10) -> list[tuple[str, float]]:
        """Get top N files by risk_score.

        Returns list of (path, risk_score) tuples sorted descending.
        """
        files = [(path, fs.risk_score) for path, fs in self.per_file.items()]
        return sorted(files, key=lambda x: x[1], reverse=True)[:n]

    def top_files_by_delta_h(self, n: int = 10) -> list[tuple[str, float]]:
        """Get top N files by delta_h (health Laplacian).

        Returns list of (path, delta_h) tuples sorted descending.
        Positive delta_h means worse than neighbors.
        """
        files = [(path, dh) for path, dh in self.delta_h.items()]
        return sorted(files, key=lambda x: x[1], reverse=True)[:n]

    def hotspot_files(self, min_changes: int | None = None) -> list[str]:
        """Get files above median change activity.

        Args:
            min_changes: Override minimum change threshold. If None, uses median.

        Returns:
            List of file paths that are active hotspots.
        """
        if min_changes is None:
            changes = [fs.total_changes for fs in self.per_file.values() if fs.total_changes > 0]
            if not changes:
                return []
            changes_sorted = sorted(changes)
            min_changes = changes_sorted[len(changes_sorted) // 2]

        return [path for path, fs in self.per_file.items() if fs.total_changes > min_changes]


# ── Backward Compatibility ────────────────────────────────────────────


@dataclass
class Primitives:
    """Five orthogonal quality primitives.

    Kept for backward-compatibility (attribute access via .structural_entropy etc.).
    Use FileSignals for new code.
    """

    structural_entropy: float
    network_centrality: float
    churn_volatility: float
    semantic_coherence: float
    cognitive_load: float

    def to_dict(self) -> PrimitiveValues:
        return {
            "structural_entropy": self.structural_entropy,
            "network_centrality": self.network_centrality,
            "churn_volatility": self.churn_volatility,
            "semantic_coherence": self.semantic_coherence,
            "cognitive_load": self.cognitive_load,
        }

    @classmethod
    def from_dict(cls, d: PrimitiveValues) -> Primitives:
        return cls(
            structural_entropy=d.get("structural_entropy", 0.0),
            network_centrality=d.get("network_centrality", 0.0),
            churn_volatility=d.get("churn_volatility", 0.0),
            semantic_coherence=d.get("semantic_coherence", 0.0),
            cognitive_load=d.get("cognitive_load", 0.0),
        )

    @classmethod
    def from_file_signals(cls, fs: FileSignals) -> Primitives:
        """Create Primitives from FileSignals for backward compatibility.

        Mapping:
            structural_entropy -> compression_ratio
            network_centrality -> pagerank
            churn_volatility -> churn_cv
            semantic_coherence -> semantic_coherence
            cognitive_load -> cognitive_load
        """
        return cls(
            structural_entropy=fs.compression_ratio,
            network_centrality=fs.pagerank,
            churn_volatility=fs.churn_cv,
            semantic_coherence=fs.semantic_coherence,
            cognitive_load=fs.cognitive_load,
        )
