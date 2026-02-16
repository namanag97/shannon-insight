"""Infrastructure patterns for Shannon Insight v2.

Phase 0 deliverables: Signal registry, typed store, validation contracts,
fusion pipeline builder, threshold strategy, error taxonomy.

These patterns are the foundation -- all feature code depends on them.
"""

from shannon_insight.infrastructure.entities import (
    Entity,
    EntityId,
    EntityType,
)
from shannon_insight.infrastructure.math import (
    compute_bus_factor,
    compute_entropy,
    compute_gini,
    compute_percentile,
)
from shannon_insight.infrastructure.patterns import (
    Finding,
    Pattern,
    PatternScope,
)
from shannon_insight.infrastructure.relations import (
    Relation,
    RelationGraph,
    RelationType,
)
from shannon_insight.session import Tier  # Re-export Tier for backward compat
from shannon_insight.infrastructure.signals import (
    SIGNAL_REGISTRY,
    Polarity,
    Signal,
    SignalSpec,
    SignalStore,
)
from shannon_insight.infrastructure.store import (
    FactStore,
)
from shannon_insight.infrastructure.thresholds import (
    ThresholdCheck,
    compute_hotspot_median,
    is_hotspot,
)
from shannon_insight.infrastructure.validation import (
    PhaseValidationError,
    run_all_validations,
    validate_after_scanning,
    validate_after_structural,
    validate_signal_field,
)

__all__ = [
    "AnalysisResult",
    "Entity",
    "EntityId",
    "EntityType",
    "FactStore",
    "compute_bus_factor",
    "compute_entropy",
    "compute_gini",
    "compute_percentile",
    "Finding",
    "Pattern",
    "PatternScope",
    "Relation",
    "RelationGraph",
    "RelationType",
    "ThresholdCheck",
    "compute_hotspot_median",
    "is_hotspot",
    "RuntimeContext",
    "Tier",
    "Polarity",
    "Signal",
    "SignalSpec",
    "SignalStore",
    "SIGNAL_REGISTRY",
    "PhaseValidationError",
    "run_all_validations",
    "validate_after_scanning",
    "validate_after_structural",
    "run_pipeline",
    "validate_signal_field",
]
