"""Cross-Dimensional patterns.

3 patterns that combine signals from multiple dimensions.
Canonical spec: docs/v2/architecture/06-patterns/05-cross-dimensional.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shannon_insight.infrastructure.entities import EntityId
from shannon_insight.infrastructure.patterns import Pattern, PatternScope
from shannon_insight.infrastructure.relations import RelationType
from shannon_insight.infrastructure.signals import Signal

from ..helpers import compute_median, compute_percentile

if TYPE_CHECKING:
    from shannon_insight.infrastructure.store import FactStore


# ==============================================================================
# 20. WEAK_LINK
# ==============================================================================


def _weak_link_predicate(store: FactStore, entity: EntityId) -> bool:
    """Central file with high risk score.

    Uses RISK_SCORE (file-scoped) instead of HEALTH_SCORE (module-scoped).
    HEALTH_SCORE is a module signal and would never be set on FILE entities,
    causing this pattern to never fire.
    """
    pr_pctl = compute_percentile(store, entity, Signal.PAGERANK)
    risk_score = store.get_signal(entity, Signal.RISK_SCORE, 0.0)

    return pr_pctl > 0.80 and risk_score > 0.7


def _weak_link_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.75


def _weak_link_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for WEAK_LINK."""
    return {
        "pagerank": store.get_signal(entity, Signal.PAGERANK, 0),
        "pagerank_pctl": compute_percentile(store, entity, Signal.PAGERANK),
        "risk_score": store.get_signal(entity, Signal.RISK_SCORE, 0),
    }


WEAK_LINK = Pattern(
    name="weak_link",
    scope=PatternScope.FILE,
    severity=0.75,
    requires={Signal.PAGERANK.value, Signal.RISK_SCORE.value},
    condition="pctl(pagerank) > 0.80 AND risk_score > 0.7",
    predicate=_weak_link_predicate,
    severity_fn=_weak_link_severity,
    evidence_fn=_weak_link_evidence,
    description="Central file with high risk score",
    remediation="Refactor to reduce risk. Consider splitting.",
    category="cross_dimensional",
    hotspot_filtered=True,
    phase=5,
)


# ==============================================================================
# 21. BUG_ATTRACTOR
# ==============================================================================


def _bug_attractor_predicate(store: FactStore, entity: EntityId) -> bool:
    """File with high fix ratio."""
    fix_ratio = store.get_signal(entity, Signal.FIX_RATIO, 0)
    total_changes = store.get_signal(entity, Signal.TOTAL_CHANGES, 0)
    median_changes = compute_median(store, Signal.TOTAL_CHANGES)

    return fix_ratio > 0.5 and total_changes > median_changes


def _bug_attractor_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.70


def _bug_attractor_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for BUG_ATTRACTOR."""
    return {
        "fix_ratio": store.get_signal(entity, Signal.FIX_RATIO, 0),
        "total_changes": store.get_signal(entity, Signal.TOTAL_CHANGES, 0),
        "cognitive_load": store.get_signal(entity, Signal.COGNITIVE_LOAD, 0),
    }


BUG_ATTRACTOR = Pattern(
    name="bug_attractor",
    scope=PatternScope.FILE,
    severity=0.70,
    requires={Signal.FIX_RATIO.value, Signal.TOTAL_CHANGES.value},
    condition="fix_ratio > 0.5 AND total_changes > median",
    predicate=_bug_attractor_predicate,
    severity_fn=_bug_attractor_severity,
    evidence_fn=_bug_attractor_evidence,
    description="File with high fix ratio",
    remediation="Simplify logic. Add defensive checks. Increase test coverage.",
    category="cross_dimensional",
    hotspot_filtered=True,
    phase=3,
)


# ==============================================================================
# 22. ACCIDENTAL_COUPLING
# ==============================================================================


def _accidental_coupling_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Files import each other but share no concepts."""
    file_a, file_b = pair

    # Must have import relationship
    imports_ab = store.has_relation(file_a, RelationType.IMPORTS, file_b)
    imports_ba = store.has_relation(file_b, RelationType.IMPORTS, file_a)

    if not (imports_ab or imports_ba):
        return False

    # Check concept overlap (Jaccard similarity)
    # For now, we use semantic similarity as proxy
    # In full implementation, this would compute Jaccard of concept sets
    similar_rels = [
        r for r in store.outgoing(file_a, RelationType.SIMILAR_TO) if r.target == file_b
    ]

    if not similar_rels:
        # No similarity data, assume low overlap
        return True

    similarity = similar_rels[0].metadata.get("similarity", 0.0)
    # Low similarity = low concept overlap
    return similarity < 0.2


def _accidental_coupling_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Fixed severity."""
    return 0.50


def _accidental_coupling_evidence(
    store: FactStore, pair: tuple[EntityId, EntityId]
) -> dict[str, Any]:
    """Build evidence for ACCIDENTAL_COUPLING."""
    file_a, file_b = pair

    similar_rels = [
        r for r in store.outgoing(file_a, RelationType.SIMILAR_TO) if r.target == file_b
    ]
    similarity = similar_rels[0].metadata.get("similarity", 0.0) if similar_rels else 0.0

    return {
        "has_import": True,
        "concept_overlap": similarity,  # Using semantic similarity as proxy
    }


ACCIDENTAL_COUPLING = Pattern(
    name="accidental_coupling",
    scope=PatternScope.FILE_PAIR,
    severity=0.50,
    requires={RelationType.IMPORTS.name, RelationType.SIMILAR_TO.name},
    condition="imports(A, B) AND concept_overlap(A, B) < 0.2",
    predicate=_accidental_coupling_predicate,
    severity_fn=_accidental_coupling_severity,
    evidence_fn=_accidental_coupling_evidence,
    description="Files import each other but share no concepts",
    remediation="Review if import is necessary. May indicate wrong abstraction.",
    category="cross_dimensional",
    hotspot_filtered=False,
    phase=2,
)
