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
    """Central file owned by a very small team (bus_factor in (1.0, 2.0]).

    bus_factor <= 1.0 is handled by TRUCK_FACTOR — avoid duplicate findings.
    """
    if is_solo_project(store):
        return False

    bus_factor = store.get_signal(entity, Signal.BUS_FACTOR, 0)
    pr_pctl = compute_percentile(store, entity, Signal.PAGERANK)

    # TRUCK_FACTOR handles bus_factor <= 1.0 — only take moderate-risk case here
    if bus_factor <= 1.0:
        return False

    return bus_factor <= 2.0 and pr_pctl > 0.75


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
    condition="bus_factor in (1.0, 2.0] AND pctl(pagerank) > 0.75",
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
    """Modules with different teams but structural coupling."""
    mod_a, mod_b = pair

    coupling = store.get_signal(mod_a, Signal.COUPLING, 0)
    if coupling <= 0.3:
        return False

    author_dist = _compute_module_author_distance(store, mod_a, mod_b)
    return author_dist > 0.8


def _compute_module_author_distance(store: FactStore, mod_a: EntityId, mod_b: EntityId) -> float:
    """Aggregate file-level AUTHOR_DISTANCE relations to module level."""
    from shannon_insight.infrastructure.relations import RelationType

    # Collect files in each module via IN_MODULE relations (reverse: CONTAINS)
    def _files_in_module(mod: EntityId) -> set[str]:
        return {r.source.key for r in store.incoming(mod, RelationType.IN_MODULE)}

    files_a = _files_in_module(mod_a)
    files_b = _files_in_module(mod_b)

    if not files_a or not files_b:
        return 1.0  # Unknown team composition → assume different teams

    # Average AUTHOR_DISTANCE for cross-module file pairs
    from shannon_insight.infrastructure.entities import EntityId as EId, EntityType
    distances = []
    for fa_path in files_a:
        fa_id = EId(EntityType.FILE, fa_path)
        for rel in store.outgoing(fa_id, RelationType.AUTHOR_DISTANCE):
            if rel.target.key in files_b:
                distances.append(rel.metadata.get("distance", 1.0))

    return sum(distances) / len(distances) if distances else 1.0


def _conway_violation_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Severity scales with coupling strength."""
    mod_a, _mod_b = pair
    coupling = store.get_signal(mod_a, Signal.COUPLING, 0)
    # Base 0.55, increase with coupling strength
    return min(0.75, 0.55 + coupling * 0.2)


def _conway_violation_evidence(store: FactStore, pair: tuple[EntityId, EntityId]) -> dict[str, Any]:
    """Build evidence for CONWAY_VIOLATION."""
    mod_a, mod_b = pair
    return {
        "module_a": mod_a.key,
        "module_b": mod_b.key,
        "coupling": store.get_signal(mod_a, Signal.COUPLING, 0),
        # author_distance will be added when module-level aggregation is implemented
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
