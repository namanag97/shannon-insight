"""Core code issue patterns.

7 foundational patterns for detecting common code quality issues:
HIGH_RISK_HUB, HIDDEN_COUPLING, GOD_FILE, UNSTABLE_FILE,
BOUNDARY_MISMATCH, DEAD_DEPENDENCY, CHRONIC_PROBLEM.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shannon_insight.infrastructure.entities import EntityId
from shannon_insight.infrastructure.patterns import Pattern, PatternScope
from shannon_insight.infrastructure.relations import RelationType
from shannon_insight.infrastructure.signals import Signal

from ..helpers import compute_median, compute_percentile, get_thresholds

if TYPE_CHECKING:
    from shannon_insight.infrastructure.store import FactStore


# ==============================================================================
# 1. HIGH_RISK_HUB
# ==============================================================================


def _high_risk_hub_predicate(store: FactStore, entity: EntityId) -> bool:
    """High centrality AND (high complexity OR high churn)."""
    thresholds = get_thresholds(store)

    pr_pctl = compute_percentile(store, entity, Signal.PAGERANK)
    br_pctl = compute_percentile(store, entity, Signal.BLAST_RADIUS_SIZE)
    cog_pctl = compute_percentile(store, entity, Signal.COGNITIVE_LOAD)
    trajectory = store.get_signal(entity, Signal.CHURN_TRAJECTORY, "")

    has_high_centrality = (
        pr_pctl >= thresholds.hub_pagerank_pctl
        or br_pctl >= thresholds.hub_blast_radius_pctl
    )
    has_high_complexity = cog_pctl >= thresholds.hub_cognitive_load_pctl
    has_high_churn = trajectory in {"CHURNING", "SPIKING"}

    return has_high_centrality and (has_high_complexity or has_high_churn)


def _high_risk_hub_severity(store: FactStore, entity: EntityId) -> float:
    """Dynamic severity based on percentile strength."""
    pr_pctl = compute_percentile(store, entity, Signal.PAGERANK)
    br_pctl = compute_percentile(store, entity, Signal.BLAST_RADIUS_SIZE)
    cog_pctl = compute_percentile(store, entity, Signal.COGNITIVE_LOAD)

    pctls = [p for p in [pr_pctl, br_pctl, cog_pctl] if p >= 0.80]
    avg_pctl = sum(pctls) / len(pctls) if pctls else 0.9
    return 1.0 * max(0.5, avg_pctl)


def _high_risk_hub_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence dictionary for HIGH_RISK_HUB."""
    pr = store.get_signal(entity, Signal.PAGERANK, 0)
    br = store.get_signal(entity, Signal.BLAST_RADIUS_SIZE, 0)
    cog = store.get_signal(entity, Signal.COGNITIVE_LOAD, 0)
    trajectory = store.get_signal(entity, Signal.CHURN_TRAJECTORY, "")
    total_changes = store.get_signal(entity, Signal.TOTAL_CHANGES, 0)
    in_degree = store.get_signal(entity, Signal.IN_DEGREE, 0)

    pr_pctl = compute_percentile(store, entity, Signal.PAGERANK)
    br_pctl = compute_percentile(store, entity, Signal.BLAST_RADIUS_SIZE)
    cog_pctl = compute_percentile(store, entity, Signal.COGNITIVE_LOAD)

    return {
        "pagerank": pr,
        "pagerank_pctl": pr_pctl,
        "blast_radius_size": br,
        "blast_radius_pctl": br_pctl,
        "cognitive_load": cog,
        "cognitive_load_pctl": cog_pctl,
        "churn_trajectory": trajectory,
        "total_changes": total_changes,
        "in_degree": in_degree,
    }


HIGH_RISK_HUB = Pattern(
    name="high_risk_hub",
    scope=PatternScope.FILE,
    severity=1.00,
    requires={
        Signal.PAGERANK.value,
        Signal.BLAST_RADIUS_SIZE.value,
        Signal.COGNITIVE_LOAD.value,
        Signal.CHURN_TRAJECTORY.value,
        Signal.TOTAL_CHANGES.value,
    },
    condition="pctl(pagerank) > 0.90 AND pctl(blast_radius) > 0.90 AND (pctl(cognitive_load) > 0.90 OR churn_trajectory ∈ {CHURNING, SPIKING})",
    predicate=_high_risk_hub_predicate,
    severity_fn=_high_risk_hub_severity,
    evidence_fn=_high_risk_hub_evidence,
    description="Central file with high complexity and volatility",
    remediation="Split responsibilities. Pair-program to spread knowledge.",
    category="existing",
    hotspot_filtered=True,
    phase=0,
)


# ==============================================================================
# 2. HIDDEN_COUPLING
# ==============================================================================


def _hidden_coupling_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Co-change without structural dependency."""
    file_a, file_b = pair

    # Check for COCHANGES_WITH relation
    cochanges_rels = [
        r for r in store.outgoing(file_a, RelationType.COCHANGES_WITH) if r.target == file_b
    ]
    if not cochanges_rels:
        return False

    cochange_rel = cochanges_rels[0]
    lift = cochange_rel.metadata.get("lift", 0.0)
    confidence_ab = cochange_rel.metadata.get("confidence_a_b", 0.0)
    confidence_ba = cochange_rel.metadata.get("confidence_b_a", 0.0)
    max_conf = max(confidence_ab, confidence_ba)

    # Thresholds
    if lift < 2.0 or max_conf < 0.5:
        return False

    # Check NO structural dependency
    imports_ab = store.has_relation(file_a, RelationType.IMPORTS, file_b)
    imports_ba = store.has_relation(file_b, RelationType.IMPORTS, file_a)

    return not (imports_ab or imports_ba)


def _hidden_coupling_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Dynamic severity based on lift and confidence."""
    file_a, file_b = pair
    cochanges_rels = [
        r for r in store.outgoing(file_a, RelationType.COCHANGES_WITH) if r.target == file_b
    ]
    if not cochanges_rels:
        return 0.5

    cochange_rel = cochanges_rels[0]
    lift = cochange_rel.metadata.get("lift", 0.0)
    confidence_ab = cochange_rel.metadata.get("confidence_a_b", 0.0)
    confidence_ba = cochange_rel.metadata.get("confidence_b_a", 0.0)
    max_conf = max(confidence_ab, confidence_ba)

    strength = min(1.0, (lift / 10.0 + max_conf) / 2)
    return 0.90 * strength


def _hidden_coupling_evidence(store: FactStore, pair: tuple[EntityId, EntityId]) -> dict[str, Any]:
    """Build evidence for HIDDEN_COUPLING."""
    file_a, file_b = pair
    cochanges_rels = [
        r for r in store.outgoing(file_a, RelationType.COCHANGES_WITH) if r.target == file_b
    ]
    if not cochanges_rels:
        return {}

    cochange_rel = cochanges_rels[0]
    return {
        "lift": cochange_rel.metadata.get("lift", 0.0),
        "confidence_a_b": cochange_rel.metadata.get("confidence_a_b", 0.0),
        "confidence_b_a": cochange_rel.metadata.get("confidence_b_a", 0.0),
        "cochange_count": cochange_rel.metadata.get("cochange_count", 0),
        "no_import": True,
    }


HIDDEN_COUPLING = Pattern(
    name="hidden_coupling",
    scope=PatternScope.FILE_PAIR,
    severity=0.90,
    requires={RelationType.COCHANGES_WITH.name, RelationType.IMPORTS.name},
    condition="lift(A, B) ≥ 2.0 AND confidence(A, B) ≥ 0.5 AND NOT imports(A, B)",
    predicate=_hidden_coupling_predicate,
    severity_fn=_hidden_coupling_severity,
    evidence_fn=_hidden_coupling_evidence,
    description="Files that change together but have no explicit dependency",
    remediation="Extract shared concept or make dependency explicit.",
    category="existing",
    hotspot_filtered=False,
    phase=3,
)


# ==============================================================================
# 3. GOD_FILE
# ==============================================================================


def _god_file_predicate(store: FactStore, entity: EntityId) -> bool:
    """High complexity AND low coherence."""
    thresholds = get_thresholds(store)

    cog_pctl = compute_percentile(store, entity, Signal.COGNITIVE_LOAD)
    coh_pctl = compute_percentile(store, entity, Signal.SEMANTIC_COHERENCE)
    func_count = store.get_signal(entity, Signal.FUNCTION_COUNT, 0)

    # Minimum function count to avoid flagging trivial files
    if func_count < thresholds.god_file_min_functions:
        return False

    has_high_complexity = cog_pctl >= thresholds.god_file_cognitive_pctl
    has_low_coherence = coh_pctl <= thresholds.god_file_coherence_pctl  # LOW is bad

    return has_high_complexity and has_low_coherence


def _god_file_severity(store: FactStore, entity: EntityId) -> float:
    """Dynamic severity based on how extreme the signals are."""
    cog_pctl = compute_percentile(store, entity, Signal.COGNITIVE_LOAD)
    coh_pctl = compute_percentile(store, entity, Signal.SEMANTIC_COHERENCE)

    avg_pctl = (cog_pctl + (1 - coh_pctl)) / 2
    return 0.80 * max(0.5, avg_pctl)


def _god_file_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for GOD_FILE."""
    return {
        "cognitive_load": store.get_signal(entity, Signal.COGNITIVE_LOAD, 0),
        "cognitive_load_pctl": compute_percentile(store, entity, Signal.COGNITIVE_LOAD),
        "semantic_coherence": store.get_signal(entity, Signal.SEMANTIC_COHERENCE, 0),
        "semantic_coherence_pctl": compute_percentile(store, entity, Signal.SEMANTIC_COHERENCE),
        "function_count": store.get_signal(entity, Signal.FUNCTION_COUNT, 0),
        "concept_count": store.get_signal(entity, Signal.CONCEPT_COUNT, 0),
    }


GOD_FILE = Pattern(
    name="god_file",
    scope=PatternScope.FILE,
    severity=0.80,
    requires={Signal.COGNITIVE_LOAD.value, Signal.SEMANTIC_COHERENCE.value},
    condition="pctl(cognitive_load) > 0.90 AND pctl(semantic_coherence) < 0.20",
    predicate=_god_file_predicate,
    severity_fn=_god_file_severity,
    evidence_fn=_god_file_evidence,
    description="Large file with too many unrelated concepts",
    remediation="Split by concept clusters. Each concept = a candidate file.",
    category="existing",
    hotspot_filtered=False,
    phase=2,
)


# ==============================================================================
# 4. UNSTABLE_FILE
# ==============================================================================


def _unstable_file_predicate(store: FactStore, entity: EntityId) -> bool:
    """Erratic change pattern."""
    trajectory = store.get_signal(entity, Signal.CHURN_TRAJECTORY, "")
    total_changes = store.get_signal(entity, Signal.TOTAL_CHANGES, 0)
    median_changes = compute_median(store, Signal.TOTAL_CHANGES)

    return trajectory in {"CHURNING", "SPIKING"} and total_changes > median_changes


def _unstable_file_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.70


def _unstable_file_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for UNSTABLE_FILE."""
    return {
        "churn_trajectory": store.get_signal(entity, Signal.CHURN_TRAJECTORY, ""),
        "total_changes": store.get_signal(entity, Signal.TOTAL_CHANGES, 0),
        "churn_cv": store.get_signal(entity, Signal.CHURN_CV, 0),
        "churn_slope": store.get_signal(entity, Signal.CHURN_SLOPE, 0),
    }


UNSTABLE_FILE = Pattern(
    name="unstable_file",
    scope=PatternScope.FILE,
    severity=0.70,
    requires={Signal.CHURN_TRAJECTORY.value, Signal.TOTAL_CHANGES.value},
    condition="churn_trajectory ∈ {CHURNING, SPIKING} AND total_changes > median",
    predicate=_unstable_file_predicate,
    severity_fn=_unstable_file_severity,
    evidence_fn=_unstable_file_evidence,
    description="File with erratic change patterns",
    remediation="Investigate why this file isn't stabilizing. Check fix_ratio.",
    category="existing",
    hotspot_filtered=True,
    phase=3,
)


# ==============================================================================
# 5. BOUNDARY_MISMATCH
# ==============================================================================


def _boundary_mismatch_predicate(store: FactStore, entity: EntityId) -> bool:
    """Directory boundary doesn't match dependency structure."""
    boundary_alignment = store.get_signal(entity, Signal.BOUNDARY_ALIGNMENT, 1.0)
    file_count = store.get_signal(entity, Signal.FILE_COUNT, 0)

    return boundary_alignment < 0.7 and file_count >= 3


def _boundary_mismatch_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.60


def _boundary_mismatch_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for BOUNDARY_MISMATCH."""
    return {
        "boundary_alignment": store.get_signal(entity, Signal.BOUNDARY_ALIGNMENT, 0),
        "file_count": store.get_signal(entity, Signal.FILE_COUNT, 0),
        "role_consistency": store.get_signal(entity, Signal.ROLE_CONSISTENCY, 0),
    }


BOUNDARY_MISMATCH = Pattern(
    name="boundary_mismatch",
    scope=PatternScope.MODULE,
    severity=0.60,
    requires={Signal.BOUNDARY_ALIGNMENT.value, Signal.FILE_COUNT.value},
    condition="boundary_alignment < 0.7 AND file_count >= 3",
    predicate=_boundary_mismatch_predicate,
    severity_fn=_boundary_mismatch_severity,
    evidence_fn=_boundary_mismatch_evidence,
    description="Directory boundary doesn't match dependency structure",
    remediation="Directory boundary doesn't match dependency structure. Consider reorganizing.",
    category="existing",
    hotspot_filtered=False,
    phase=4,
)


# ==============================================================================
# 6. DEAD_DEPENDENCY
# ==============================================================================


def _dead_dependency_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Import edge with no co-change history."""
    file_a, file_b = pair

    # Must have import relationship
    if not store.has_relation(file_a, RelationType.IMPORTS, file_b):
        return False

    # Both files must have significant history (50+ commits)
    changes_a = store.get_signal(file_a, Signal.TOTAL_CHANGES, 0)
    changes_b = store.get_signal(file_b, Signal.TOTAL_CHANGES, 0)
    if changes_a < 50 or changes_b < 50:
        return False

    # Check for COCHANGES_WITH relation
    cochanges_rels = [
        r for r in store.outgoing(file_a, RelationType.COCHANGES_WITH) if r.target == file_b
    ]

    # Dead if no co-change or very low co-change
    if not cochanges_rels:
        return True

    cochange_count = cochanges_rels[0].metadata.get("cochange_count", 0)
    return cochange_count == 0


def _dead_dependency_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Fixed severity."""
    return 0.40


def _dead_dependency_evidence(store: FactStore, pair: tuple[EntityId, EntityId]) -> dict[str, Any]:
    """Build evidence for DEAD_DEPENDENCY."""
    file_a, file_b = pair
    return {
        "has_import": True,
        "cochange_count": 0,
        "total_changes_a": store.get_signal(file_a, Signal.TOTAL_CHANGES, 0),
        "total_changes_b": store.get_signal(file_b, Signal.TOTAL_CHANGES, 0),
    }


DEAD_DEPENDENCY = Pattern(
    name="dead_dependency",
    scope=PatternScope.FILE_PAIR,
    severity=0.40,
    requires={
        RelationType.IMPORTS.name,
        RelationType.COCHANGES_WITH.name,
        Signal.TOTAL_CHANGES.value,
    },
    condition="imports(A, B) AND cochange_count(A, B) = 0 AND total_changes(A) >= 50",
    predicate=_dead_dependency_predicate,
    severity_fn=_dead_dependency_severity,
    evidence_fn=_dead_dependency_evidence,
    description="Import edge with no co-change history",
    remediation="This import may be dead. Verify the imported symbols are actually used.",
    category="existing",
    hotspot_filtered=False,
    phase=3,
)


# ==============================================================================
# 7. CHRONIC_PROBLEM
# ==============================================================================


def _chronic_problem_predicate(store: FactStore, entity: EntityId) -> bool:
    """Finding that persists across 3+ snapshots.

    Note: This pattern is special - it wraps other findings.
    The predicate is handled differently in the executor.
    """
    # This pattern is applied as a post-processing step
    # by the executor, not as a regular pattern match
    return False


def _chronic_problem_severity(store: FactStore, entity: EntityId) -> float:
    """Amplified severity (base × 1.25)."""
    # Actual severity computed by executor based on base finding
    return 0.65


def _chronic_problem_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Evidence for CHRONIC_PROBLEM."""
    # Actual evidence built by executor from persistence data
    return {}


CHRONIC_PROBLEM = Pattern(
    name="chronic_problem",
    scope=PatternScope.FILE,  # Wraps other scopes
    severity=0.65,  # Base severity before amplification
    requires={"finding_lifecycle"},  # Requires persistence
    condition="same finding persists across 3+ snapshots",
    predicate=_chronic_problem_predicate,
    severity_fn=_chronic_problem_severity,
    evidence_fn=_chronic_problem_evidence,
    description="Finding that persists across 3+ snapshots",
    remediation="This issue has persisted for N snapshots. Prioritize resolution.",
    category="existing",
    hotspot_filtered=False,
    phase=7,
)
