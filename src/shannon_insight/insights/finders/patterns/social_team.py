"""Social/Team patterns.

3 patterns for detecting team coordination and knowledge issues.
Canonical spec: docs/v2/architecture/06-patterns/03-social-team.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shannon_insight.infrastructure.entities import EntityId
from shannon_insight.infrastructure.patterns import Pattern, PatternScope
from shannon_insight.infrastructure.signals import Signal

from ..helpers import compute_percentile, is_solo_project

if TYPE_CHECKING:
    from shannon_insight.infrastructure.store import FactStore


# ==============================================================================
# 14. KNOWLEDGE_SILO
# ==============================================================================


def _knowledge_silo_predicate(store: FactStore, entity: EntityId) -> bool:
    """Central file owned by one person."""
    # Skip bus_factor checks for solo developer projects
    if is_solo_project(store):
        return False

    bus_factor = store.get_signal(entity, Signal.BUS_FACTOR, 0)
    pr_pctl = compute_percentile(store, entity, Signal.PAGERANK)

    return bus_factor <= 1.5 and pr_pctl > 0.75


def _knowledge_silo_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.70


def _knowledge_silo_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for KNOWLEDGE_SILO."""
    return {
        "bus_factor": store.get_signal(entity, Signal.BUS_FACTOR, 0),
        "author_entropy": store.get_signal(entity, Signal.AUTHOR_ENTROPY, 0),
        "pagerank": store.get_signal(entity, Signal.PAGERANK, 0),
        "pagerank_pctl": compute_percentile(store, entity, Signal.PAGERANK),
    }


KNOWLEDGE_SILO = Pattern(
    name="knowledge_silo",
    scope=PatternScope.FILE,
    severity=0.70,
    requires={Signal.BUS_FACTOR.value, Signal.PAGERANK.value},
    condition="bus_factor <= 1.5 AND pctl(pagerank) > 0.75",
    predicate=_knowledge_silo_predicate,
    severity_fn=_knowledge_silo_severity,
    evidence_fn=_knowledge_silo_evidence,
    description="Central file owned by one person",
    remediation="Pair-program to spread knowledge. Document the code.",
    category="social_team",
    hotspot_filtered=True,
    phase=0,
)


# ==============================================================================
# 15. CONWAY_VIOLATION
# ==============================================================================


def _conway_violation_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Modules with different teams but structural coupling.

    TODO: CONWAY_VIOLATION disabled until author_distance computation is implemented.
    Currently author_distance is hardcoded to 0.0, so this pattern can never fire.
    The pattern is also excluded from ALL_PATTERNS in the registry.
    """
    # Always skip: author_distance not yet implemented
    return False


def _conway_violation_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Fixed severity."""
    return 0.55


def _conway_violation_evidence(store: FactStore, pair: tuple[EntityId, EntityId]) -> dict[str, Any]:
    """Build evidence for CONWAY_VIOLATION."""
    mod_a, mod_b = pair
    return {
        "author_distance": 0.0,  # TODO: Compute
        "coupling": store.get_signal(mod_a, Signal.COUPLING, 0),
    }


CONWAY_VIOLATION = Pattern(
    name="conway_violation",
    scope=PatternScope.MODULE_PAIR,
    severity=0.55,
    requires={Signal.COUPLING.value},  # + AUTHORED_BY relations
    condition="d_author(M1, M2) > 0.8 AND structural_coupling(M1, M2) > 0.3",
    predicate=_conway_violation_predicate,
    severity_fn=_conway_violation_severity,
    evidence_fn=_conway_violation_evidence,
    description="Modules with different teams but structural coupling",
    remediation="Align team boundaries with module boundaries.",
    category="social_team",
    hotspot_filtered=False,
    phase=5,
)


# ==============================================================================
# 16. REVIEW_BLINDSPOT
# ==============================================================================


def _review_blindspot_predicate(store: FactStore, entity: EntityId) -> bool:
    """Bug-prone file with single owner."""
    # Skip bus_factor checks for solo developer projects
    if is_solo_project(store):
        return False

    bus_factor = store.get_signal(entity, Signal.BUS_FACTOR, 0)
    fix_ratio = store.get_signal(entity, Signal.FIX_RATIO, 0)

    return bus_factor <= 1.0 and fix_ratio > 0.3


def _review_blindspot_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.80


def _review_blindspot_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for REVIEW_BLINDSPOT."""
    return {
        "bus_factor": store.get_signal(entity, Signal.BUS_FACTOR, 0),
        "fix_ratio": store.get_signal(entity, Signal.FIX_RATIO, 0),
        "total_changes": store.get_signal(entity, Signal.TOTAL_CHANGES, 0),
    }


REVIEW_BLINDSPOT = Pattern(
    name="review_blindspot",
    scope=PatternScope.FILE,
    severity=0.80,
    requires={Signal.BUS_FACTOR.value, Signal.FIX_RATIO.value},
    condition="bus_factor <= 1.0 AND fix_ratio > 0.3",
    predicate=_review_blindspot_predicate,
    severity_fn=_review_blindspot_severity,
    evidence_fn=_review_blindspot_evidence,
    description="Bug-prone file with single owner",
    remediation="Require code review from second developer. Pair on bug fixes.",
    category="social_team",
    hotspot_filtered=True,
    phase=5,
)
