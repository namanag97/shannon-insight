"""Architecture patterns.

3 patterns for detecting architectural quality issues.
Canonical spec: docs/v2/architecture/06-patterns/04-architecture.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shannon_insight.infrastructure.entities import EntityId
from shannon_insight.infrastructure.patterns import Pattern, PatternScope
from shannon_insight.infrastructure.signals import Signal

if TYPE_CHECKING:
    from shannon_insight.infrastructure.store import FactStore


# ==============================================================================
# 17. LAYER_VIOLATION
# ==============================================================================


def _layer_violation_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Module imports from wrong layer.

    Note: This pattern reads from architecture.violations instead of
    checking signals directly. It's handled specially in the executor.
    """
    # The actual violations are detected during architecture analysis
    # and stored in store.architecture.violations
    # The executor will iterate those and create findings
    return False  # Handled by executor


def _layer_violation_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Fixed severity."""
    return 0.52


def _layer_violation_evidence(store: FactStore, pair: tuple[EntityId, EntityId]) -> dict[str, Any]:
    """Build evidence for LAYER_VIOLATION."""
    # Actual evidence built by executor from violation data
    return {}


LAYER_VIOLATION = Pattern(
    name="layer_violation",
    scope=PatternScope.MODULE_PAIR,
    severity=0.52,
    requires={"architecture"},  # Requires architecture slot
    condition="source_layer < target_layer (wrong direction)",
    predicate=_layer_violation_predicate,
    severity_fn=_layer_violation_severity,
    evidence_fn=_layer_violation_evidence,
    description="Module imports from wrong layer",
    remediation="Inject dependency or restructure to respect layer ordering.",
    category="architecture",
    hotspot_filtered=False,
    phase=4,
)


# ==============================================================================
# 18. ZONE_OF_PAIN
# ==============================================================================


def _zone_of_pain_predicate(store: FactStore, entity: EntityId) -> bool:
    """Concrete + stable module (hard to change)."""
    abstractness = store.get_signal(entity, Signal.ABSTRACTNESS, None)
    instability = store.get_signal(entity, Signal.INSTABILITY, None)

    # CRITICAL: instability can be None for isolated modules (Ca+Ce=0)
    if instability is None:
        return False

    # Zone of pain: low abstractness AND low instability
    return abstractness is not None and abstractness < 0.3 and instability < 0.3


def _zone_of_pain_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.60


def _zone_of_pain_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for ZONE_OF_PAIN."""
    abstractness = store.get_signal(entity, Signal.ABSTRACTNESS, 0)
    instability = store.get_signal(entity, Signal.INSTABILITY, 0)
    main_seq_distance = store.get_signal(entity, Signal.MAIN_SEQ_DISTANCE, 0)

    return {
        "abstractness": abstractness,
        "instability": instability,
        "main_seq_distance": main_seq_distance,
        "dependent_count": store.get_signal(entity, Signal.COUPLING, 0),
    }


ZONE_OF_PAIN = Pattern(
    name="zone_of_pain",
    scope=PatternScope.MODULE,
    severity=0.60,
    requires={Signal.ABSTRACTNESS.name, Signal.INSTABILITY.name},
    condition="instability is not None AND abstractness < 0.3 AND instability < 0.3",
    predicate=_zone_of_pain_predicate,
    severity_fn=_zone_of_pain_severity,
    evidence_fn=_zone_of_pain_evidence,
    description="Concrete + stable module (hard to change)",
    remediation="Extract interfaces to increase abstractness.",
    category="architecture",
    hotspot_filtered=False,
    phase=4,
)


# ==============================================================================
# 19. ARCHITECTURE_EROSION
# ==============================================================================


def _architecture_erosion_predicate(store: FactStore, entity: EntityId) -> bool:
    """Violation rate increasing over 3+ snapshots.

    Note: This pattern requires persistence (signal_history table).
    It's handled specially by the executor.
    """
    # This pattern is applied by querying signal_history
    # for violation_rate trend over snapshots
    return False  # Handled by executor


def _architecture_erosion_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.65


def _architecture_erosion_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for ARCHITECTURE_EROSION."""
    # Actual evidence built by executor from persistence data
    return {}


ARCHITECTURE_EROSION = Pattern(
    name="architecture_erosion",
    scope=PatternScope.CODEBASE,
    severity=0.65,
    requires={"signal_history"},  # Requires persistence
    condition="violation_rate increasing 3+ snapshots",
    predicate=_architecture_erosion_predicate,
    severity_fn=_architecture_erosion_severity,
    evidence_fn=_architecture_erosion_evidence,
    description="Violation rate increasing over time",
    remediation="Review recent commits. Enforce layer rules in CI.",
    category="architecture",
    hotspot_filtered=False,
    phase=7,
)
