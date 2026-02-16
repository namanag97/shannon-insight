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
    "Entity",
    "EntityId",
    "EntityType",
    "compute_bus_factor",
    "compute_entropy",
    "compute_gini",
    "compute_percentile",
    "ThresholdCheck",
    "compute_hotspot_median",
    "is_hotspot",
    "PhaseValidationError",
    "run_all_validations",
    "validate_after_scanning",
    "validate_after_structural",
    "validate_signal_field",
]
