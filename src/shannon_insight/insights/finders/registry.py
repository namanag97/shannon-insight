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


def _god_file_predicate(store: FactStore, entity: EntityId) -> bool:
    """High complexity AND low coherence."""
    cog_pctl = compute_percentile(store, entity, Signal.COGNITIVE_LOAD)
    coh_pctl = compute_percentile(store, entity, Signal.SEMANTIC_COHERENCE)
    func_count = store.get_signal(entity, Signal.FUNCTION_COUNT, 0)

    # Minimum function count to avoid flagging trivial files
    if func_count < 3:
        return False

    has_high_complexity = cog_pctl >= 0.90
    has_low_coherence = coh_pctl <= 0.20  # semantic_coherence is HIGH_IS_GOOD

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
    requires={Signal.COGNITIVE_LOAD.name, Signal.SEMANTIC_COHERENCE.name},
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
    requires={Signal.CHURN_TRAJECTORY.name, Signal.TOTAL_CHANGES.name},
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


def _orphan_code_predicate(store: FactStore, entity: EntityId) -> bool:
    """File is unreachable (orphan)."""
    is_orphan = store.get_signal(entity, Signal.IS_ORPHAN, False)
    return is_orphan


def _orphan_code_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.55


def _orphan_code_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for ORPHAN_CODE."""
    return {
        "is_orphan": True,
        "in_degree": store.get_signal(entity, Signal.IN_DEGREE, 0),
        "depth": store.get_signal(entity, Signal.DEPTH, -1),
        "role": store.get_signal(entity, Signal.ROLE, "UNKNOWN"),
    }


ORPHAN_CODE = Pattern(
    name="orphan_code",
    scope=PatternScope.FILE,
    severity=0.55,
    requires={Signal.IS_ORPHAN.name, Signal.ROLE.name},
    condition="is_orphan = True",
    predicate=_orphan_code_predicate,
    severity_fn=_orphan_code_severity,
    evidence_fn=_orphan_code_evidence,
    description="File with no incoming dependencies",
    remediation="Wire into dependency graph or remove if unused.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=3,
)


def _hollow_code_predicate(store: FactStore, entity: EntityId) -> bool:
    """File with many stub functions."""
    stub_ratio = store.get_signal(entity, Signal.STUB_RATIO, 0)
    impl_gini = store.get_signal(entity, Signal.IMPL_GINI, 0)

    return stub_ratio > 0.5 and impl_gini > 0.6


def _hollow_code_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.71


def _hollow_code_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for HOLLOW_CODE."""
    return {
        "stub_ratio": store.get_signal(entity, Signal.STUB_RATIO, 0),
        "impl_gini": store.get_signal(entity, Signal.IMPL_GINI, 0),
        "function_count": store.get_signal(entity, Signal.FUNCTION_COUNT, 0),
    }


HOLLOW_CODE = Pattern(
    name="hollow_code",
    scope=PatternScope.FILE,
    severity=0.71,
    requires={Signal.STUB_RATIO.name, Signal.IMPL_GINI.name},
    condition="stub_ratio > 0.5 AND impl_gini > 0.6",
    predicate=_hollow_code_predicate,
    severity_fn=_hollow_code_severity,
    evidence_fn=_hollow_code_evidence,
    description="File with many stub functions",
    remediation="Implement the stub functions. Priority: functions called by other files.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=1,
)


def _phantom_imports_predicate(store: FactStore, entity: EntityId) -> bool:
    """File has unresolved imports."""
    phantom_count = store.get_signal(entity, Signal.PHANTOM_IMPORT_COUNT, 0)
    return phantom_count > 0


def _phantom_imports_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.65


def _phantom_imports_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for PHANTOM_IMPORTS."""
    return {
        "phantom_import_count": store.get_signal(entity, Signal.PHANTOM_IMPORT_COUNT, 0),
        "import_count": store.get_signal(entity, Signal.IMPORT_COUNT, 0),
    }


PHANTOM_IMPORTS = Pattern(
    name="phantom_imports",
    scope=PatternScope.FILE,
    severity=0.65,
    requires={Signal.PHANTOM_IMPORT_COUNT.name},
    condition="phantom_import_count > 0",
    predicate=_phantom_imports_predicate,
    severity_fn=_phantom_imports_severity,
    evidence_fn=_phantom_imports_evidence,
    description="File with unresolved imports",
    remediation="Create missing module or replace with existing library.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=3,
)


def _knowledge_silo_predicate(store: FactStore, entity: EntityId) -> bool:
    """Central file owned by one person."""
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
    requires={Signal.BUS_FACTOR.name, Signal.PAGERANK.name},
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
# Pattern Registry
# ==============================================================================

# All 22 patterns (implemented: 8, remaining: 14)
# This registry demonstrates the pattern structure. Remaining patterns
# follow the same structure with their specific predicates/severity/evidence.
ALL_PATTERNS: list[Pattern] = [
    # Existing (v1 upgraded)
    HIGH_RISK_HUB,
    HIDDEN_COUPLING,
    GOD_FILE,
    UNSTABLE_FILE,
    # AI Quality
    ORPHAN_CODE,
    HOLLOW_CODE,
    PHANTOM_IMPORTS,
    # Social/Team
    KNOWLEDGE_SILO,
    # TODO: Add remaining 14 patterns following same structure
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
