"""Pattern Registry — Declarative finder definitions.

All 22 patterns defined as Pattern objects per canonical v2 architecture.
Patterns are grouped by category and executed by the pattern executor.

Canonical spec: docs/v2/architecture/06-patterns/
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shannon_insight.infrastructure.entities import EntityId, EntityType
from shannon_insight.infrastructure.patterns import Pattern, PatternScope
from shannon_insight.infrastructure.relations import RelationType
from shannon_insight.infrastructure.signals import Signal

if TYPE_CHECKING:
    from shannon_insight.infrastructure.store import FactStore


# ==============================================================================
# Helper Functions
# ==============================================================================


def compute_percentile(store: FactStore, entity: EntityId, signal: Signal) -> float:
    """Compute percentile rank for a signal value across all files.

    Uses canonical percentile formula: pctl(S,f) = |{v: S(v)≤S(f)}| / |all_files|
    Returns 0.0 if signal not available.
    """
    value = store.get_signal(entity, signal)
    if value is None:
        return 0.0

    files = store.files()
    values = [store.get_signal(f, signal, default=0) for f in files]
    count_below_or_equal = sum(1 for v in values if v <= value)
    return count_below_or_equal / max(len(values), 1)


def compute_median(store: FactStore, signal: Signal) -> float:
    """Compute median value for a signal across all files."""
    files = store.files()
    values = sorted([store.get_signal(f, signal, default=0) for f in files])
    if not values:
        return 0.0
    n = len(values)
    if n % 2 == 0:
        return (values[n // 2 - 1] + values[n // 2]) / 2
    return values[n // 2]


def compute_confidence_from_margins(
    triggered: list[tuple[str, float, float, str]]
) -> float:
    """Compute confidence from margins above/below thresholds.

    Args:
        triggered: List of (signal_name, actual, threshold, polarity)

    Returns:
        Confidence in [0, 1]
    """
    if not triggered:
        return 0.0

    margins = []
    for signal, actual, threshold, polarity in triggered:
        if polarity == "high_is_bad":
            margin = (actual - threshold) / (1.0 - threshold) if threshold < 1 else 0
        else:  # high_is_good
            margin = (threshold - actual) / threshold if threshold > 0 else 0
        margins.append(max(0.0, min(1.0, margin)))

    return sum(margins) / len(margins)


# ==============================================================================
# Category 1: Existing Patterns (v1 upgraded)
# ==============================================================================


def _high_risk_hub_predicate(store: FactStore, entity: EntityId) -> bool:
    """High centrality AND (high complexity OR high churn)."""
    pr_pctl = compute_percentile(store, entity, Signal.PAGERANK)
    br_pctl = compute_percentile(store, entity, Signal.BLAST_RADIUS_SIZE)
    cog_pctl = compute_percentile(store, entity, Signal.COGNITIVE_LOAD)
    trajectory = store.get_signal(entity, Signal.CHURN_TRAJECTORY, "")

    has_high_centrality = pr_pctl >= 0.90 or br_pctl >= 0.90
    has_high_complexity = cog_pctl >= 0.90
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

    evidence = {
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

    return evidence


HIGH_RISK_HUB = Pattern(
    name="high_risk_hub",
    scope=PatternScope.FILE,
    severity=1.00,
    requires={
        Signal.PAGERANK.name,
        Signal.BLAST_RADIUS_SIZE.name,
        Signal.COGNITIVE_LOAD.name,
        Signal.CHURN_TRAJECTORY.name,
        Signal.TOTAL_CHANGES.name,
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


def _hidden_coupling_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Co-change without structural dependency."""
    file_a, file_b = pair

    # Check for COCHANGES_WITH relation
    cochanges_rels = [
        r for r in store.outgoing(file_a, RelationType.COCHANGES_WITH)
        if r.target == file_b
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
        r for r in store.outgoing(file_a, RelationType.COCHANGES_WITH)
        if r.target == file_b
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
        r for r in store.outgoing(file_a, RelationType.COCHANGES_WITH)
        if r.target == file_b
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
# Pattern Registry
# ==============================================================================

# All 22 patterns will be registered here
ALL_PATTERNS: list[Pattern] = [
    HIGH_RISK_HUB,
    HIDDEN_COUPLING,
    # TODO: Add remaining 20 patterns
]


def get_patterns_by_phase(phase: int) -> list[Pattern]:
    """Get all patterns available after a given phase."""
    return [p for p in ALL_PATTERNS if p.phase <= phase]


def get_pattern_by_name(name: str) -> Pattern | None:
    """Look up a pattern by name."""
    for p in ALL_PATTERNS:
        if p.name == name:
            return p
    return None
