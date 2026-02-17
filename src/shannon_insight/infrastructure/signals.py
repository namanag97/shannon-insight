"""Signal enum and registry — the single source of truth for all 62 signals.

Inspired by Prometheus CollectorRegistry (auto-registration, collision detection)
and SonarQube MeasureComputer (declared input/output metrics with DAG validation).

Every signal is defined ONCE as an enum member. The enum IS the name — no string
typos possible. The registry maps each Signal to its SignalMeta, which describes
dtype, scope, polarity, percentileability, absolute threshold, producer, and phase.

Usage:
    from shannon_insight.infrastructure.signals import Signal, REGISTRY, get_signal_meta

    meta = get_signal_meta(Signal.PAGERANK)
    assert meta.polarity == "high_is_bad"
    assert meta.percentileable is True

    safe_set = percentileable_signals()
    assert Signal.COMMUNITY not in safe_set

Kills:
    C3  — name mismatches (enum, not string)
    C4  — duplicate computation (single-owner registration rejects duplicates)
    C12 — percentiling wrong signals (registry says percentileable=False)
    C17 — all-zero columns (every signal has declared producer)
    C47 — single source of truth (this file)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Polarity Enum
# ---------------------------------------------------------------------------


class Polarity(Enum):
    """How to interpret high values of a signal."""

    HIGH_IS_BAD = "high_is_bad"
    HIGH_IS_GOOD = "high_is_good"
    NEUTRAL = "neutral"


# ---------------------------------------------------------------------------
# Signal Enum
# ---------------------------------------------------------------------------


class Signal(Enum):
    """Every signal defined ONCE. The enum IS the name -- no string typos possible.

    Signals are organized by IR (Intermediate Representation) level:
        IR1  = Syntactic scanning        (signals 1-7)
        IR2  = Semantic analysis          (signals 8-13)
        IR3  = Graph analysis             (signals 14-26)
        IR5t = Temporal (git history)     (signals 27-34)
        IR5s = Signal fusion composites   (signals 35-36)
        IR4  = Architecture / modules     (signals 37-51)
        S6   = Global / codebase-level    (signals 52-62)

    The string value matches the field name in FileSignals / ModuleSignals /
    GlobalSignals dataclasses (see signals/models.py).
    """

    # ── IR1: Syntactic scanning (per-file, phase 0-1) ────────────────
    LINES = "lines"  # 1
    FUNCTION_COUNT = "function_count"  # 2
    CLASS_COUNT = "class_count"  # 3
    MAX_NESTING = "max_nesting"  # 4
    IMPL_GINI = "impl_gini"  # 5
    STUB_RATIO = "stub_ratio"  # 6
    IMPORT_COUNT = "import_count"  # 7

    # ── IR2: Semantic analysis (per-file, phase 2) ───────────────────
    ROLE = "role"  # 8
    CONCEPT_COUNT = "concept_count"  # 9
    CONCEPT_ENTROPY = "concept_entropy"  # 10
    NAMING_DRIFT = "naming_drift"  # 11
    TODO_DENSITY = "todo_density"  # 12
    DOCSTRING_COVERAGE = "docstring_coverage"  # 13

    # ── IR3: Graph analysis (per-file, phase 0-3) ───────────────────
    PAGERANK = "pagerank"  # 14
    BETWEENNESS = "betweenness"  # 15
    IN_DEGREE = "in_degree"  # 16
    OUT_DEGREE = "out_degree"  # 17
    BLAST_RADIUS_SIZE = "blast_radius_size"  # 18
    DEPTH = "depth"  # 19
    IS_ORPHAN = "is_orphan"  # 20
    PHANTOM_IMPORT_COUNT = "phantom_import_count"  # 21
    BROKEN_CALL_COUNT = "broken_call_count"  # 22
    COMMUNITY = "community"  # 23
    COMPRESSION_RATIO = "compression_ratio"  # 24
    SEMANTIC_COHERENCE = "semantic_coherence"  # 25
    COGNITIVE_LOAD = "cognitive_load"  # 26

    # ── IR5t: Temporal / git history (per-file, phase 3) ─────────────
    TOTAL_CHANGES = "total_changes"  # 27
    CHURN_TRAJECTORY = "churn_trajectory"  # 28
    CHURN_SLOPE = "churn_slope"  # 29
    CHURN_CV = "churn_cv"  # 30
    BUS_FACTOR = "bus_factor"  # 31
    AUTHOR_ENTROPY = "author_entropy"  # 32
    FIX_RATIO = "fix_ratio"  # 33
    REFACTOR_RATIO = "refactor_ratio"  # 34
    CHANGE_ENTROPY = "change_entropy"  # 34a (added: was computed but not registered)

    # ── IR5s: Per-file composites (phase 5) ──────────────────────────
    RISK_SCORE = "risk_score"  # 35
    WIRING_QUALITY = "wiring_quality"  # 36
    FILE_HEALTH_SCORE = "file_health_score"  # 36a (per-file health composite)

    # ── IR4: Per-module signals (phase 4-5) ──────────────────────────
    COHESION = "cohesion"  # 37
    COUPLING = "coupling"  # 38
    INSTABILITY = "instability"  # 39
    ABSTRACTNESS = "abstractness"  # 40
    MAIN_SEQ_DISTANCE = "main_seq_distance"  # 41
    BOUNDARY_ALIGNMENT = "boundary_alignment"  # 42
    LAYER_VIOLATION_COUNT = "layer_violation_count"  # 43
    ROLE_CONSISTENCY = "role_consistency"  # 44
    VELOCITY = "velocity"  # 45
    COORDINATION_COST = "coordination_cost"  # 46
    KNOWLEDGE_GINI = "knowledge_gini"  # 47
    MODULE_BUS_FACTOR = "module_bus_factor"  # 48
    MEAN_COGNITIVE_LOAD = "mean_cognitive_load"  # 49
    FILE_COUNT = "file_count"  # 50
    HEALTH_SCORE = "health_score"  # 51

    # ── S6: Global signals (phase 0-5) ───────────────────────────────
    MODULARITY = "modularity"  # 52
    FIEDLER_VALUE = "fiedler_value"  # 53
    SPECTRAL_GAP = "spectral_gap"  # 54
    CYCLE_COUNT = "cycle_count"  # 55
    CENTRALITY_GINI = "centrality_gini"  # 56
    ORPHAN_RATIO = "orphan_ratio"  # 57
    PHANTOM_RATIO = "phantom_ratio"  # 58
    GLUE_DEFICIT = "glue_deficit"  # 59
    WIRING_SCORE = "wiring_score"  # 60
    ARCHITECTURE_HEALTH = "architecture_health"  # 61
    CODEBASE_HEALTH = "codebase_health"  # 62


# ---------------------------------------------------------------------------
# SignalMeta — metadata for each signal
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SignalMeta:
    """Metadata for a single signal. Immutable once registered.

    Attributes:
        signal: The Signal enum member this metadata describes.
        dtype: Python type of the raw value (int, float, str, bool).
        scope: Granularity — "file", "module", or "global".
        percentileable: Whether percentile normalization is meaningful.
            False for enums (role, churn_trajectory), bools (is_orphan),
            assignment IDs (community), composites, and global single values.
        polarity: How to interpret high values.
            "high_is_bad"  — higher values indicate worse quality/more risk.
            "high_is_good" — higher values indicate better quality.
            "neutral"      — no inherent quality direction.
        absolute_threshold: For ABSOLUTE tier finders (codebases < 15 files).
            None means no absolute threshold is defined for this signal.
        produced_by: Single-owner module path that computes this signal.
            Used for collision detection and debugging provenance.
        phase: Earliest phase at which this signal becomes available (0-5).
    """

    signal: Signal
    dtype: type
    scope: str
    percentileable: bool
    polarity: str
    absolute_threshold: float | None
    produced_by: str
    phase: int

    def __post_init__(self) -> None:
        """Validate invariants at construction time."""
        if self.scope not in ("file", "module", "global"):
            raise ValueError(
                f"Invalid scope '{self.scope}' for {self.signal.value}. "
                f"Must be 'file', 'module', or 'global'."
            )
        if self.polarity not in ("high_is_bad", "high_is_good", "neutral"):
            raise ValueError(
                f"Invalid polarity '{self.polarity}' for {self.signal.value}. "
                f"Must be 'high_is_bad', 'high_is_good', or 'neutral'."
            )
        if not 0 <= self.phase <= 5:
            raise ValueError(f"Invalid phase {self.phase} for {self.signal.value}. Must be 0-5.")


# ---------------------------------------------------------------------------
# Registry — THE single source of truth, populated at import time
# ---------------------------------------------------------------------------


REGISTRY: dict[Signal, SignalMeta] = {}


def register(meta: SignalMeta) -> None:
    """Register a signal. Raises on duplicate with different producer (single-owner rule).

    Idempotent for the same producer — safe to call multiple times during testing
    or module reloads.

    Raises:
        ValueError: If signal already registered by a different producer.
    """
    if meta.signal in REGISTRY:
        existing = REGISTRY[meta.signal]
        if existing.produced_by != meta.produced_by:
            raise ValueError(
                f"Signal '{meta.signal.value}' already registered by "
                f"'{existing.produced_by}', cannot register again from "
                f"'{meta.produced_by}'"
            )
        return  # Idempotent for same producer
    REGISTRY[meta.signal] = meta


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_signal_meta(signal: Signal) -> SignalMeta:
    """Look up metadata for a signal.

    Raises:
        KeyError: If signal is not registered (indicates a registration bug).
    """
    try:
        return REGISTRY[signal]
    except KeyError:
        raise KeyError(
            f"Signal '{signal.value}' not found in registry. Did you forget to register it?"
        ) from None


def percentileable_signals() -> set[Signal]:
    """Signals safe for percentile normalization. Auto-derived, never hand-maintained.

    Returns the set of signals where SignalMeta.percentileable is True.
    Excludes enums (role, churn_trajectory), bools (is_orphan), assignment IDs
    (community), composites (risk_score, wiring_quality, health_score), and all
    global signals (single values, not distributions).
    """
    return {s for s, m in REGISTRY.items() if m.percentileable}


def signals_by_phase(phase: int) -> set[Signal]:
    """Signals available after a given phase completes.

    Returns all signals whose phase <= the given phase number.
    Phase 0 includes scanning + graph basics.
    Phase 5 includes everything (all 62 signals).
    """
    return {s for s, m in REGISTRY.items() if m.phase <= phase}


def signals_by_scope(scope: str) -> set[Signal]:
    """All signals with the given scope ("file", "module", or "global")."""
    return {s for s, m in REGISTRY.items() if m.scope == scope}


def signals_by_polarity(polarity: str) -> set[Signal]:
    """All signals with the given polarity direction."""
    return {s for s, m in REGISTRY.items() if m.polarity == polarity}


# ---------------------------------------------------------------------------
# Register all 62 signals
# ---------------------------------------------------------------------------
# Source of truth: docs/v2/registry/signals.md
# Each register() call corresponds to one row in the signal tables.
# The order follows the signal numbering (#1-#62).

# ── Per-File: IR1 Syntactic (scanning/) ──────────────────────────────────

register(
    SignalMeta(
        signal=Signal.LINES,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=500.0,
        produced_by="scanning",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.FUNCTION_COUNT,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=30.0,
        produced_by="scanning",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.CLASS_COUNT,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="scanning",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.MAX_NESTING,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=4.0,
        produced_by="scanning",
        phase=1,
    )
)

register(
    SignalMeta(
        signal=Signal.IMPL_GINI,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=0.6,
        produced_by="scanning",
        phase=1,
    )
)

register(
    SignalMeta(
        signal=Signal.STUB_RATIO,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=0.5,
        produced_by="scanning",
        phase=1,
    )
)

register(
    SignalMeta(
        signal=Signal.IMPORT_COUNT,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="scanning",
        phase=0,
    )
)

# ── Per-File: IR2 Semantic (semantics/) ──────────────────────────────────

register(
    SignalMeta(
        signal=Signal.ROLE,
        dtype=str,
        scope="file",
        percentileable=False,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="semantics/roles",
        phase=2,
    )
)

register(
    SignalMeta(
        signal=Signal.CONCEPT_COUNT,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="semantics",
        phase=2,
    )
)

register(
    SignalMeta(
        signal=Signal.CONCEPT_ENTROPY,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=1.5,
        produced_by="semantics",
        phase=2,
    )
)

register(
    SignalMeta(
        signal=Signal.NAMING_DRIFT,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=0.7,
        produced_by="semantics",
        phase=2,
    )
)

register(
    SignalMeta(
        signal=Signal.TODO_DENSITY,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=0.05,
        produced_by="scanning",
        phase=1,
    )
)

register(
    SignalMeta(
        signal=Signal.DOCSTRING_COVERAGE,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="semantics",
        phase=2,
    )
)

# ── Per-File: IR3 Graph (graph/) ─────────────────────────────────────────

register(
    SignalMeta(
        signal=Signal.PAGERANK,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.BETWEENNESS,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.IN_DEGREE,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.OUT_DEGREE,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.BLAST_RADIUS_SIZE,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.DEPTH,
        dtype=int,
        scope="file",
        percentileable=False,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.IS_ORPHAN,
        dtype=bool,
        scope="file",
        percentileable=False,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.PHANTOM_IMPORT_COUNT,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=0.0,
        produced_by="graph/algorithms",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.BROKEN_CALL_COUNT,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=0.0,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.COMMUNITY,
        dtype=int,
        scope="file",
        percentileable=False,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.COMPRESSION_RATIO,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="signals/fusion",  # Computed in fusion.py step1_collect
        phase=5,  # Available when fusion runs
    )
)

register(
    SignalMeta(
        signal=Signal.SEMANTIC_COHERENCE,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="signals/fusion",  # Computed in fusion.py from semantics.concept_entropy
        phase=5,  # Requires semantics slot (phase 2) but computed in fusion (phase 5)
    )
)

register(
    SignalMeta(
        signal=Signal.COGNITIVE_LOAD,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="signals/fusion",  # Computed in fusion.py from file_syntax
        phase=5,  # Requires syntax (phase 0-1) but computed in fusion (phase 5)
    )
)

# ── Per-File: IR5t Temporal (temporal/) ──────────────────────────────────

register(
    SignalMeta(
        signal=Signal.TOTAL_CHANGES,
        dtype=int,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.CHURN_TRAJECTORY,
        dtype=str,
        scope="file",
        percentileable=False,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.CHURN_SLOPE,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.CHURN_CV,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=1.0,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.BUS_FACTOR,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=1.0,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.AUTHOR_ENTROPY,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.FIX_RATIO,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=0.4,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.REFACTOR_RATIO,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="temporal/churn",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.CHANGE_ENTROPY,
        dtype=float,
        scope="file",
        percentileable=True,
        polarity="high_is_bad",  # High entropy = scattered changes = harder to predict
        absolute_threshold=None,
        produced_by="temporal/churn",
        phase=3,
    )
)

# ── Per-File: Composites (signals/) ──────────────────────────────────────

register(
    SignalMeta(
        signal=Signal.RISK_SCORE,
        dtype=float,
        scope="file",
        percentileable=False,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.WIRING_QUALITY,
        dtype=float,
        scope="file",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

# ── Per-Module: IR4 Architecture (architecture/) ─────────────────────────

register(
    SignalMeta(
        signal=Signal.COHESION,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.COUPLING,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.INSTABILITY,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.ABSTRACTNESS,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.MAIN_SEQ_DISTANCE,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.BOUNDARY_ALIGNMENT,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.LAYER_VIOLATION_COUNT,
        dtype=int,
        scope="module",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.ROLE_CONSISTENCY,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.VELOCITY,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.COORDINATION_COST,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.KNOWLEDGE_GINI,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.MODULE_BUS_FACTOR,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.MEAN_COGNITIVE_LOAD,
        dtype=float,
        scope="module",
        percentileable=True,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.FILE_COUNT,
        dtype=int,
        scope="module",
        percentileable=True,
        polarity="neutral",
        absolute_threshold=None,
        produced_by="architecture",
        phase=4,
    )
)

register(
    SignalMeta(
        signal=Signal.HEALTH_SCORE,
        dtype=float,
        scope="module",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

# ── Global: S6 (graph/, architecture/, signals/) ─────────────────────────

register(
    SignalMeta(
        signal=Signal.MODULARITY,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.FIEDLER_VALUE,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.SPECTRAL_GAP,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.CYCLE_COUNT,
        dtype=int,
        scope="global",
        percentileable=False,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=0,
    )
)

register(
    SignalMeta(
        signal=Signal.CENTRALITY_GINI,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.ORPHAN_RATIO,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.PHANTOM_RATIO,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.GLUE_DEFICIT,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_bad",
        absolute_threshold=None,
        produced_by="graph/algorithms",
        phase=3,
    )
)

register(
    SignalMeta(
        signal=Signal.WIRING_SCORE,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.ARCHITECTURE_HEALTH,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)

register(
    SignalMeta(
        signal=Signal.CODEBASE_HEALTH,
        dtype=float,
        scope="global",
        percentileable=False,
        polarity="high_is_good",
        absolute_threshold=None,
        produced_by="signals/fusion",
        phase=5,
    )
)


# ---------------------------------------------------------------------------
# Post-registration validation — runs at import time
# ---------------------------------------------------------------------------


def _validate_registry() -> None:
    """Verify every Signal enum member is registered. Runs once at import."""
    registered = set(REGISTRY.keys())
    all_signals = set(Signal)
    missing = all_signals - registered
    if missing:
        names = sorted(s.value for s in missing)
        raise RuntimeError(f"Signal registry incomplete! Missing registrations for: {names}")


_validate_registry()


# ---------------------------------------------------------------------------
# v2 API: SignalSpec, SIGNAL_REGISTRY, SignalStore
# ---------------------------------------------------------------------------
# These types provide the public interface expected by v2 architecture tests.
# They adapt the existing REGISTRY/SignalMeta data to the spec-defined API.


_POLARITY_MAP = {
    "high_is_bad": Polarity.HIGH_IS_BAD,
    "high_is_good": Polarity.HIGH_IS_GOOD,
    "neutral": Polarity.NEUTRAL,
}


@dataclass(frozen=True)
class SignalSpec:
    """Metadata for a signal (v2 public API).

    Attributes:
        signal: The Signal enum member.
        scope: Set of EntityType values this signal applies to.
        dtype: Python type of the raw value (int, float, str, bool).
        polarity: Polarity enum value.
        phase: Earliest phase at which this signal becomes available (0-5).
        source: Which module computes it.
        percentileable: Whether percentile normalization is meaningful.
        absolute_threshold: For ABSOLUTE tier finders. None if not defined.
    """

    signal: Signal
    scope: set
    dtype: type
    polarity: Polarity
    phase: int
    source: str
    percentileable: bool
    absolute_threshold: float | None = None


def _build_signal_registry() -> dict[Signal, SignalSpec]:
    """Build SIGNAL_REGISTRY from the existing REGISTRY.

    Converts SignalMeta (internal) to SignalSpec (v2 public API), mapping
    string scope/polarity to EntityType sets and Polarity enum values.
    """
    from shannon_insight.infrastructure.entities import EntityType

    scope_map = {
        "file": {EntityType.FILE},
        "module": {EntityType.MODULE},
        "global": {EntityType.CODEBASE},
    }

    registry: dict[Signal, SignalSpec] = {}
    for signal, meta in REGISTRY.items():
        registry[signal] = SignalSpec(
            signal=meta.signal,
            scope=scope_map[meta.scope],
            dtype=meta.dtype,
            polarity=_POLARITY_MAP[meta.polarity],
            phase=meta.phase,
            source=meta.produced_by,
            percentileable=meta.percentileable,
            absolute_threshold=meta.absolute_threshold,
        )
    return registry


SIGNAL_REGISTRY: dict[Signal, SignalSpec] = _build_signal_registry()


# ---------------------------------------------------------------------------
# SignalValue and SignalStore
# ---------------------------------------------------------------------------


@dataclass
class SignalValue:
    """A timestamped signal measurement."""

    entity: Any  # EntityId
    signal: Signal
    value: Any
    timestamp: datetime
    confidence: float = 1.0


class SignalStore:
    """Entity x Signal x Time -> Value store.

    Provides the v2 public API for storing and retrieving signal values
    keyed by (EntityId, Signal) pairs.
    """

    def __init__(self) -> None:
        self._data: dict[tuple, SignalValue] = {}
        self._history: dict[tuple, list] = {}

    def set(
        self,
        entity: Any,
        signal: Signal,
        value: Any,
        timestamp: datetime | None = None,
    ) -> None:
        """Set a signal value for an entity."""
        timestamp = timestamp or datetime.now()
        sv = SignalValue(entity, signal, value, timestamp)
        key = (entity, signal)
        self._data[key] = sv
        self._history.setdefault(key, []).append(sv)

    def get(
        self,
        entity: Any,
        signal: Signal,
        default: Any = None,
    ) -> Any:
        """Get the latest signal value for an entity."""
        sv = self._data.get((entity, signal))
        return sv.value if sv else default

    def has(self, entity: Any, signal: Signal) -> bool:
        """Check if a signal exists for an entity."""
        return (entity, signal) in self._data

    def has_any(self, signal: Signal) -> bool:
        """Check if a signal exists for any entity."""
        return any(k[1] == signal for k in self._data)

    def all_values(self, signal: Signal) -> list:
        """Get all (entity, value) pairs for a signal across entities."""
        return [(k[0], v.value) for k, v in self._data.items() if k[1] == signal]

    def history(self, entity: Any, signal: Signal) -> list:
        """Get historical values for a signal on an entity."""
        return self._history.get((entity, signal), [])
