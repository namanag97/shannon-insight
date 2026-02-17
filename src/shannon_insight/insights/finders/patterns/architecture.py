"""Architecture patterns.

3 patterns for detecting architectural quality issues.
Canonical spec: docs/v2/architecture/06-patterns/04-architecture.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shannon_insight.infrastructure.entities import EntityId
from shannon_insight.infrastructure.patterns import Pattern, PatternScope
from shannon_insight.infrastructure.relations import RelationType
from shannon_insight.infrastructure.signals import Signal

if TYPE_CHECKING:
    from shannon_insight.infrastructure.store import FactStore


# ==============================================================================
# 17. LAYER_VIOLATION
# ==============================================================================


def _layer_violation_predicate(store: FactStore, entity: EntityId) -> bool:
    """Module has layer violations (imports from wrong layer)."""
    violation_count = store.get_signal(entity, Signal.LAYER_VIOLATION_COUNT, 0)
    return violation_count > 0


def _layer_violation_severity(store: FactStore, entity: EntityId) -> float:
    """Severity scales with number of violations."""
    violation_count = store.get_signal(entity, Signal.LAYER_VIOLATION_COUNT, 0)
    if violation_count >= 5:
        return 0.75
    elif violation_count >= 2:
        return 0.60
    return 0.52


def _layer_violation_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for LAYER_VIOLATION."""
    return {
        "layer_violation_count": store.get_signal(entity, Signal.LAYER_VIOLATION_COUNT, 0),
        "coupling": store.get_signal(entity, Signal.COUPLING, 0),
        "instability": store.get_signal(entity, Signal.INSTABILITY, 0),
    }


LAYER_VIOLATION = Pattern(
    name="layer_violation",
    scope=PatternScope.MODULE,  # Changed from MODULE_PAIR to MODULE
    severity=0.52,
    requires={Signal.LAYER_VIOLATION_COUNT.value},
    condition="layer_violation_count > 0",
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

    # Zone of pain: low abstractness (concrete) AND low instability (stable)
    # Modules with abstractness=0.0 are concrete - no interfaces, ABCs, or Protocols
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
    requires={Signal.ABSTRACTNESS.value, Signal.INSTABILITY.value},
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


# ==============================================================================
# 20. CIRCULAR_DEPENDENCY
# ==============================================================================


def _circular_dependency_predicate(store: FactStore, entity: EntityId) -> bool:
    """File is part of a circular dependency (SCC with > 1 nodes)."""
    return bool(store.get_signal(entity, Signal.CYCLE_MEMBER, False))


def _circular_dependency_severity(store: FactStore, entity: EntityId) -> float:
    """Severity scales with cycle size: larger cycles are harder to break."""
    cycle_size = store.get_signal(entity, Signal.CYCLE_SIZE, 2)
    if cycle_size >= 5:
        return 0.80
    elif cycle_size >= 3:
        return 0.70
    return 0.65


def _circular_dependency_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Evidence: which files share this cycle."""
    cycle_members = [r.target.key for r in store.outgoing(entity, RelationType.CYCLE_WITH)]
    return {
        "cycle_size": store.get_signal(entity, Signal.CYCLE_SIZE, 0),
        "cycle_members": cycle_members,
        "blast_radius_size": store.get_signal(entity, Signal.BLAST_RADIUS_SIZE, 0),
    }


CIRCULAR_DEPENDENCY = Pattern(
    name="circular_dependency",
    scope=PatternScope.FILE,
    severity=0.65,
    requires={Signal.CYCLE_MEMBER.value},
    condition="cycle_member = True",
    predicate=_circular_dependency_predicate,
    severity_fn=_circular_dependency_severity,
    evidence_fn=_circular_dependency_evidence,
    description="File is part of a circular dependency",
    remediation=(
        "Break the cycle by extracting shared types to a new common module. "
        "Alternatively, dependency-invert by making one side depend on an interface."
    ),
    category="architecture",
    hotspot_filtered=False,
    phase=3,
)


# ==============================================================================
# 21. ZONE_OF_USELESSNESS
# ==============================================================================


def _zone_of_uselessness_predicate(store: FactStore, entity: EntityId) -> bool:
    """Abstract module nobody depends on (high A + high I = Zone of Uselessness)."""
    abstractness = store.get_signal(entity, Signal.ABSTRACTNESS, None)
    instability = store.get_signal(entity, Signal.INSTABILITY, None)
    if instability is None or abstractness is None:
        return False
    return abstractness > 0.7 and instability > 0.7


def _zone_of_uselessness_severity(store: FactStore, entity: EntityId) -> float:
    return 0.50


def _zone_of_uselessness_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    return {
        "abstractness": store.get_signal(entity, Signal.ABSTRACTNESS, 0),
        "instability": store.get_signal(entity, Signal.INSTABILITY, 0),
        "main_seq_distance": store.get_signal(entity, Signal.MAIN_SEQ_DISTANCE, 0),
        "file_count": store.get_signal(entity, Signal.FILE_COUNT, 0),
    }


ZONE_OF_USELESSNESS = Pattern(
    name="zone_of_uselessness",
    scope=PatternScope.MODULE,
    severity=0.50,
    requires={Signal.ABSTRACTNESS.value, Signal.INSTABILITY.value},
    condition="instability is not None AND abstractness > 0.7 AND instability > 0.7",
    predicate=_zone_of_uselessness_predicate,
    severity_fn=_zone_of_uselessness_severity,
    evidence_fn=_zone_of_uselessness_evidence,
    description="Abstract module with no stable consumers (dead abstraction)",
    remediation=(
        "These abstractions have no stable consumers. "
        "Delete unused interfaces or add concrete implementations that other modules depend on."
    ),
    category="architecture",
    hotspot_filtered=False,
    phase=4,
)
