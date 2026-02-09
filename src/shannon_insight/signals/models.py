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
    """

    tier: str = "FULL"  # "ABSOLUTE" | "BAYESIAN" | "FULL"
    per_file: dict[str, FileSignals] = field(default_factory=dict)
    per_module: dict[str, ModuleSignals] = field(default_factory=dict)
    global_signals: GlobalSignals = field(default_factory=GlobalSignals)
    delta_h: dict[str, float] = field(default_factory=dict)  # Health Laplacian per file

    def file(self, path: str) -> FileSignals | None:
        """Get FileSignals for a path, or None if not found."""
        return self.per_file.get(path)


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
