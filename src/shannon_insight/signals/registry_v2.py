"""Signal Registry v2 — 62 signals with metadata.

This is the single source of truth for all signals in Shannon Insight v2.
Every signal is defined exactly ONCE. The Signal enum IS the name — no string typos possible.

Signal Count Breakdown:
    Per-file (S4):  37 signals (#1-36 + raw_risk intermediate)
    Per-module (S5): 15 signals (#37-51)
    Global (S6):     11 signals (#52-62)
    Total:           63 signals (62 from spec + raw_risk for health Laplacian)

Rules:
    - Every signal has a single owner (produced_by) - enforced at registration
    - Percentileable signals participate in normalization
    - Polarity determines trend direction (IMPROVING vs WORSENING)
    - Phase indicates when the signal first becomes available
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    """Every signal defined ONCE. The enum IS the name — no string typos possible."""

    # ═══════════════════════════════════════════════════════════════════════════
    # Per-File Signals (Scale S4)
    # ═══════════════════════════════════════════════════════════════════════════

    # IR1 scanning (#1-7)
    LINES = "lines"
    FUNCTION_COUNT = "function_count"
    CLASS_COUNT = "class_count"
    MAX_NESTING = "max_nesting"
    IMPL_GINI = "impl_gini"
    STUB_RATIO = "stub_ratio"
    IMPORT_COUNT = "import_count"

    # IR2 semantics (#8-13)
    ROLE = "role"
    CONCEPT_COUNT = "concept_count"
    CONCEPT_ENTROPY = "concept_entropy"
    NAMING_DRIFT = "naming_drift"
    TODO_DENSITY = "todo_density"
    DOCSTRING_COVERAGE = "docstring_coverage"

    # IR3 graph (#14-26)
    PAGERANK = "pagerank"
    BETWEENNESS = "betweenness"
    IN_DEGREE = "in_degree"
    OUT_DEGREE = "out_degree"
    BLAST_RADIUS_SIZE = "blast_radius_size"
    DEPTH = "depth"
    IS_ORPHAN = "is_orphan"
    PHANTOM_IMPORT_COUNT = "phantom_import_count"
    BROKEN_CALL_COUNT = "broken_call_count"
    COMMUNITY = "community"
    COMPRESSION_RATIO = "compression_ratio"
    SEMANTIC_COHERENCE = "semantic_coherence"
    COGNITIVE_LOAD = "cognitive_load"

    # IR5t temporal (#27-34)
    TOTAL_CHANGES = "total_changes"
    CHURN_TRAJECTORY = "churn_trajectory"
    CHURN_SLOPE = "churn_slope"
    CHURN_CV = "churn_cv"
    BUS_FACTOR = "bus_factor"
    AUTHOR_ENTROPY = "author_entropy"
    FIX_RATIO = "fix_ratio"
    REFACTOR_RATIO = "refactor_ratio"

    # IR5s composites (#35-37)
    RAW_RISK = "raw_risk"  # Intermediate - not user-facing
    RISK_SCORE = "risk_score"
    WIRING_QUALITY = "wiring_quality"

    # ═══════════════════════════════════════════════════════════════════════════
    # Per-Module Signals (Scale S5) (#37-51)
    # ═══════════════════════════════════════════════════════════════════════════

    COHESION = "cohesion"
    COUPLING = "coupling"
    INSTABILITY = "instability"
    ABSTRACTNESS = "abstractness"
    MAIN_SEQ_DISTANCE = "main_seq_distance"
    BOUNDARY_ALIGNMENT = "boundary_alignment"
    LAYER_VIOLATION_COUNT = "layer_violation_count"
    ROLE_CONSISTENCY = "role_consistency"
    VELOCITY = "velocity"
    COORDINATION_COST = "coordination_cost"
    KNOWLEDGE_GINI = "knowledge_gini"
    MODULE_BUS_FACTOR = "module_bus_factor"
    MEAN_COGNITIVE_LOAD = "mean_cognitive_load"
    FILE_COUNT = "file_count"
    HEALTH_SCORE = "health_score"

    # ═══════════════════════════════════════════════════════════════════════════
    # Global Signals (Scale S6) (#52-62)
    # ═══════════════════════════════════════════════════════════════════════════

    MODULARITY = "modularity"
    FIEDLER_VALUE = "fiedler_value"
    SPECTRAL_GAP = "spectral_gap"
    CYCLE_COUNT = "cycle_count"
    CENTRALITY_GINI = "centrality_gini"
    ORPHAN_RATIO = "orphan_ratio"
    PHANTOM_RATIO = "phantom_ratio"
    GLUE_DEFICIT = "glue_deficit"
    WIRING_SCORE = "wiring_score"
    ARCHITECTURE_HEALTH = "architecture_health"
    CODEBASE_HEALTH = "codebase_health"


@dataclass(frozen=True)
class SignalMeta:
    """Metadata for a signal.

    Attributes:
        signal: The Signal enum value
        dtype: Python type (int, float, str, bool)
        scope: "file" | "module" | "global"
        percentileable: True if signal participates in percentile normalization
        polarity: "high_is_bad" | "high_is_good" | "neutral"
        absolute_threshold: For ABSOLUTE tier finders. None = no threshold.
        produced_by: Single owner (module path) that computes this signal
        phase: First available after this phase (0-5)
        nullable: True if signal can be None (e.g., instability for isolated modules)
    """

    signal: Signal
    dtype: type
    scope: str
    percentileable: bool
    polarity: str
    absolute_threshold: float | None
    produced_by: str
    phase: int
    nullable: bool = False


# THE registry — populated at import time, validated immediately
REGISTRY: dict[Signal, SignalMeta] = {}


def register(meta: SignalMeta) -> None:
    """Register a signal. Raises on duplicate with different producer (single-owner rule)."""
    if meta.signal in REGISTRY:
        existing = REGISTRY[meta.signal]
        if existing.produced_by != meta.produced_by:
            raise ValueError(
                f"Signal {meta.signal.value} already registered by {existing.produced_by}, "
                f"cannot register again from {meta.produced_by}"
            )
        return  # Idempotent for same producer
    REGISTRY[meta.signal] = meta


def percentileable_signals() -> set[Signal]:
    """Signals safe for percentile normalization. Auto-derived, never hand-maintained."""
    return {s for s, m in REGISTRY.items() if m.percentileable}


def signals_by_phase(phase: int) -> set[Signal]:
    """Signals available after a given phase completes."""
    return {s for s, m in REGISTRY.items() if m.phase <= phase}


def signals_by_scope(scope: str) -> set[Signal]:
    """Signals at a given scope (file, module, global)."""
    return {s for s, m in REGISTRY.items() if m.scope == scope}


# ═══════════════════════════════════════════════════════════════════════════════
# Register all 62 signals at module load time
# ═══════════════════════════════════════════════════════════════════════════════

# IR1 scanning — computed by scanning/ (Phase 0)
register(SignalMeta(Signal.LINES, int, "file", True, "high_is_bad", 500, "scanning/metrics", 0))
register(
    SignalMeta(Signal.FUNCTION_COUNT, int, "file", True, "high_is_bad", 30, "scanning/metrics", 0)
)
register(SignalMeta(Signal.CLASS_COUNT, int, "file", True, "neutral", None, "scanning/metrics", 0))
register(SignalMeta(Signal.MAX_NESTING, int, "file", True, "high_is_bad", 4, "scanning/metrics", 1))
register(
    SignalMeta(Signal.IMPL_GINI, float, "file", True, "high_is_bad", 0.6, "scanning/metrics", 1)
)
register(
    SignalMeta(Signal.STUB_RATIO, float, "file", True, "high_is_bad", 0.5, "scanning/metrics", 1)
)
register(SignalMeta(Signal.IMPORT_COUNT, int, "file", True, "neutral", None, "scanning/metrics", 0))

# IR2 semantics — computed by semantics/ (Phase 2)
register(SignalMeta(Signal.ROLE, str, "file", False, "neutral", None, "semantics/roles", 2))
register(
    SignalMeta(
        Signal.CONCEPT_COUNT, int, "file", True, "high_is_bad", None, "semantics/concepts", 2
    )
)
register(
    SignalMeta(
        Signal.CONCEPT_ENTROPY, float, "file", True, "high_is_bad", 1.5, "semantics/concepts", 2
    )
)
register(
    SignalMeta(Signal.NAMING_DRIFT, float, "file", True, "high_is_bad", 0.7, "semantics/naming", 2)
)
register(
    SignalMeta(Signal.TODO_DENSITY, float, "file", True, "high_is_bad", 0.05, "scanning/metrics", 1)
)
register(
    SignalMeta(
        Signal.DOCSTRING_COVERAGE, float, "file", True, "high_is_good", None, "semantics/docs", 2
    )
)

# IR3 graph — computed by graph/ (Phase 0 and 3)
register(
    SignalMeta(Signal.PAGERANK, float, "file", True, "high_is_bad", None, "graph/algorithms", 0)
)
register(
    SignalMeta(Signal.BETWEENNESS, float, "file", True, "high_is_bad", None, "graph/algorithms", 0)
)
register(SignalMeta(Signal.IN_DEGREE, int, "file", True, "neutral", None, "graph/algorithms", 0))
register(SignalMeta(Signal.OUT_DEGREE, int, "file", True, "neutral", None, "graph/algorithms", 0))
register(
    SignalMeta(
        Signal.BLAST_RADIUS_SIZE, int, "file", True, "high_is_bad", None, "graph/algorithms", 0
    )
)
register(
    SignalMeta(Signal.DEPTH, int, "file", False, "neutral", None, "graph/algorithms", 3)
)  # -1 = orphan
register(
    SignalMeta(Signal.IS_ORPHAN, bool, "file", False, "high_is_bad", None, "graph/algorithms", 3)
)
register(
    SignalMeta(
        Signal.PHANTOM_IMPORT_COUNT, int, "file", True, "high_is_bad", 0, "graph/algorithms", 3
    )
)
register(
    SignalMeta(
        Signal.BROKEN_CALL_COUNT, int, "file", True, "high_is_bad", 0, "graph/algorithms", 99
    )
)  # Future
register(SignalMeta(Signal.COMMUNITY, int, "file", False, "neutral", None, "graph/algorithms", 0))
register(
    SignalMeta(
        Signal.COMPRESSION_RATIO, float, "file", True, "neutral", None, "scanning/metrics", 0
    )
)
register(
    SignalMeta(
        Signal.SEMANTIC_COHERENCE,
        float,
        "file",
        True,
        "high_is_good",
        None,
        "semantics/coherence",
        2,
    )
)
register(
    SignalMeta(
        Signal.COGNITIVE_LOAD, float, "file", True, "high_is_bad", None, "signals/composites", 1
    )
)

# IR5t temporal — computed by temporal/ (Phase 3)
register(
    SignalMeta(Signal.TOTAL_CHANGES, int, "file", True, "high_is_bad", None, "temporal/churn", 3)
)
register(
    SignalMeta(Signal.CHURN_TRAJECTORY, str, "file", False, "neutral", None, "temporal/churn", 3)
)
register(
    SignalMeta(Signal.CHURN_SLOPE, float, "file", True, "high_is_bad", None, "temporal/churn", 3)
)
register(SignalMeta(Signal.CHURN_CV, float, "file", True, "high_is_bad", 1.0, "temporal/churn", 3))
register(
    SignalMeta(Signal.BUS_FACTOR, float, "file", True, "high_is_good", 1.0, "temporal/churn", 3)
)
register(
    SignalMeta(
        Signal.AUTHOR_ENTROPY, float, "file", True, "high_is_good", None, "temporal/churn", 3
    )
)
register(SignalMeta(Signal.FIX_RATIO, float, "file", True, "high_is_bad", 0.4, "temporal/churn", 3))
register(
    SignalMeta(
        Signal.REFACTOR_RATIO, float, "file", True, "high_is_good", None, "temporal/churn", 3
    )
)

# IR5s composites — computed by signals/ (Phase 5)
register(
    SignalMeta(Signal.RAW_RISK, float, "file", False, "high_is_bad", None, "signals/composites", 5)
)
register(
    SignalMeta(
        Signal.RISK_SCORE, float, "file", False, "high_is_bad", None, "signals/composites", 5
    )
)
register(
    SignalMeta(
        Signal.WIRING_QUALITY, float, "file", False, "high_is_good", None, "signals/composites", 5
    )
)

# IR4 architecture — computed by architecture/ (Phase 4)
register(
    SignalMeta(
        Signal.COHESION, float, "module", True, "high_is_good", None, "architecture/metrics", 4
    )
)
register(
    SignalMeta(
        Signal.COUPLING, float, "module", True, "high_is_bad", None, "architecture/metrics", 4
    )
)
register(
    SignalMeta(
        Signal.INSTABILITY,
        float,
        "module",
        True,
        "neutral",
        None,
        "architecture/metrics",
        4,
        nullable=True,
    )
)
register(
    SignalMeta(
        Signal.ABSTRACTNESS, float, "module", True, "neutral", None, "architecture/metrics", 4
    )
)
register(
    SignalMeta(
        Signal.MAIN_SEQ_DISTANCE,
        float,
        "module",
        True,
        "high_is_bad",
        None,
        "architecture/metrics",
        4,
    )
)
register(
    SignalMeta(
        Signal.BOUNDARY_ALIGNMENT,
        float,
        "module",
        True,
        "high_is_good",
        None,
        "architecture/metrics",
        4,
    )
)
register(
    SignalMeta(
        Signal.LAYER_VIOLATION_COUNT,
        int,
        "module",
        True,
        "high_is_bad",
        None,
        "architecture/metrics",
        4,
    )
)
register(
    SignalMeta(
        Signal.ROLE_CONSISTENCY,
        float,
        "module",
        True,
        "high_is_good",
        None,
        "architecture/metrics",
        4,
    )
)
register(SignalMeta(Signal.VELOCITY, float, "module", True, "neutral", None, "temporal/modules", 5))
register(
    SignalMeta(
        Signal.COORDINATION_COST, float, "module", True, "high_is_bad", None, "temporal/modules", 5
    )
)
register(
    SignalMeta(
        Signal.KNOWLEDGE_GINI, float, "module", True, "high_is_bad", None, "temporal/modules", 5
    )
)
register(
    SignalMeta(
        Signal.MODULE_BUS_FACTOR, float, "module", True, "high_is_good", None, "temporal/modules", 5
    )
)
register(
    SignalMeta(
        Signal.MEAN_COGNITIVE_LOAD,
        float,
        "module",
        True,
        "high_is_bad",
        None,
        "signals/composites",
        5,
    )
)
register(
    SignalMeta(Signal.FILE_COUNT, int, "module", True, "neutral", None, "architecture/metrics", 4)
)
register(
    SignalMeta(
        Signal.HEALTH_SCORE, float, "module", False, "high_is_good", None, "signals/composites", 5
    )
)

# Global signals — computed by graph/ and signals/ (Phase 0, 3, 5)
register(
    SignalMeta(
        Signal.MODULARITY, float, "global", False, "high_is_good", None, "graph/algorithms", 0
    )
)
register(
    SignalMeta(
        Signal.FIEDLER_VALUE, float, "global", False, "high_is_good", None, "graph/algorithms", 0
    )
)
register(
    SignalMeta(
        Signal.SPECTRAL_GAP, float, "global", False, "high_is_good", None, "graph/algorithms", 0
    )
)
register(
    SignalMeta(Signal.CYCLE_COUNT, int, "global", False, "high_is_bad", None, "graph/algorithms", 0)
)
register(
    SignalMeta(
        Signal.CENTRALITY_GINI, float, "global", False, "high_is_bad", None, "graph/algorithms", 3
    )
)
register(
    SignalMeta(
        Signal.ORPHAN_RATIO, float, "global", False, "high_is_bad", None, "graph/algorithms", 3
    )
)
register(
    SignalMeta(
        Signal.PHANTOM_RATIO, float, "global", False, "high_is_bad", None, "graph/algorithms", 3
    )
)
register(
    SignalMeta(
        Signal.GLUE_DEFICIT, float, "global", False, "high_is_bad", None, "graph/algorithms", 3
    )
)
register(
    SignalMeta(
        Signal.WIRING_SCORE, float, "global", False, "high_is_good", None, "signals/composites", 5
    )
)
register(
    SignalMeta(
        Signal.ARCHITECTURE_HEALTH,
        float,
        "global",
        False,
        "high_is_good",
        None,
        "signals/composites",
        5,
    )
)
register(
    SignalMeta(
        Signal.CODEBASE_HEALTH,
        float,
        "global",
        False,
        "high_is_good",
        None,
        "signals/composites",
        5,
    )
)


# Validate all signals are registered
def _validate_registry() -> None:
    """Ensure every Signal enum has metadata."""
    missing = set(Signal) - set(REGISTRY.keys())
    if missing:
        raise ValueError(f"Missing metadata for signals: {missing}")


_validate_registry()
