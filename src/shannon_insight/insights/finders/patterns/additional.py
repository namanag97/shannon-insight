"""Temporal and cross-file patterns.

6 patterns that leverage git history and multi-file analysis:
1. TRUCK_FACTOR - Critical code owned by single contributor
2. INCOMPLETE_IMPLEMENTATION - Files with phantom imports or high stub ratio
3. BUG_MAGNET - Files where most changes are bug fixes
4. THRASHING_CODE - Files with erratic change patterns
5. DIRECTORY_HOTSPOT - Module-level change concentration
6. DUPLICATE_INCOMPLETE - Clone pairs where both are incomplete
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
# TRUCK_FACTOR - Critical code owned by single person
# ==============================================================================


def _truck_factor_predicate(store: FactStore, entity: EntityId) -> bool:
    """Central file owned by one person."""
    # Skip bus_factor checks for solo developer projects
    if is_solo_project(store):
        return False

    bus_factor = store.get_signal(entity, Signal.BUS_FACTOR, 0)
    lines = store.get_signal(entity, Signal.LINES, 0)
    total_changes = store.get_signal(entity, Signal.TOTAL_CHANGES, 0)
    pagerank_pctl = compute_percentile(store, entity, Signal.PAGERANK)
    blast_radius = store.get_signal(entity, Signal.BLAST_RADIUS_SIZE, 0)

    # Must have single author, non-trivial code, and be important
    return (
        bus_factor <= 1.0
        and lines >= 50
        and total_changes > 0
        and (pagerank_pctl >= 0.70 or blast_radius >= 3)
    )


def _truck_factor_severity(store: FactStore, entity: EntityId) -> float:
    """Higher severity for more central files."""
    pagerank_pctl = compute_percentile(store, entity, Signal.PAGERANK)
    blast_radius = store.get_signal(entity, Signal.BLAST_RADIUS_SIZE, 0)

    severity = 0.85
    if pagerank_pctl >= 0.70 and blast_radius >= 3:
        severity = 0.95
    return severity


def _truck_factor_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for TRUCK_FACTOR."""
    return {
        "bus_factor": store.get_signal(entity, Signal.BUS_FACTOR, 0),
        "author_entropy": store.get_signal(entity, Signal.AUTHOR_ENTROPY, 0),
        "pagerank": store.get_signal(entity, Signal.PAGERANK, 0),
        "pagerank_pctl": compute_percentile(store, entity, Signal.PAGERANK),
        "blast_radius_size": store.get_signal(entity, Signal.BLAST_RADIUS_SIZE, 0),
        "lines": store.get_signal(entity, Signal.LINES, 0),
    }


TRUCK_FACTOR = Pattern(
    name="truck_factor",
    scope=PatternScope.FILE,
    severity=0.85,
    requires={Signal.BUS_FACTOR.value, Signal.PAGERANK.value, Signal.BLAST_RADIUS_SIZE.value},
    condition="bus_factor <= 1.0 AND lines >= 50 AND (pctl(pagerank) >= 0.70 OR blast_radius >= 3)",
    predicate=_truck_factor_predicate,
    severity_fn=_truck_factor_severity,
    evidence_fn=_truck_factor_evidence,
    description="Critical code owned by single person - truck factor risk",
    remediation="Document this code and have another team member review it. Consider pair programming.",
    category="social_team",
    hotspot_filtered=True,
    phase=3,
)


# ==============================================================================
# INCOMPLETE_IMPLEMENTATION - Phantom imports or high stub ratio
# ==============================================================================


def _incomplete_impl_predicate(store: FactStore, entity: EntityId) -> bool:
    """File with broken dependencies or stubs."""
    phantom_count = store.get_signal(entity, Signal.PHANTOM_IMPORT_COUNT, 0)
    broken_calls = store.get_signal(entity, Signal.BROKEN_CALL_COUNT, 0)
    stub_ratio = store.get_signal(entity, Signal.STUB_RATIO, 0)
    impl_gini = store.get_signal(entity, Signal.IMPL_GINI, 0)
    function_count = store.get_signal(entity, Signal.FUNCTION_COUNT, 0)

    # Runtime issues are standalone triggers
    has_runtime_issue = phantom_count > 0 or broken_calls > 0

    # Stub-heavy code with uniform sizes (AI pattern)
    has_ai_pattern = impl_gini < 0.15 and function_count > 5 and stub_ratio > 0.3

    issue_count = sum(
        [
            phantom_count > 0,
            broken_calls > 0,
            stub_ratio > 0.6,
            has_ai_pattern,
        ]
    )

    return has_runtime_issue or issue_count >= 2


def _incomplete_impl_severity(store: FactStore, entity: EntityId) -> float:
    """Higher severity for runtime errors."""
    phantom_count = store.get_signal(entity, Signal.PHANTOM_IMPORT_COUNT, 0)
    broken_calls = store.get_signal(entity, Signal.BROKEN_CALL_COUNT, 0)

    severity = 0.80
    if phantom_count > 0 or broken_calls > 0:
        severity = 0.90
    return severity


def _incomplete_impl_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for INCOMPLETE_IMPLEMENTATION."""
    return {
        "phantom_import_count": store.get_signal(entity, Signal.PHANTOM_IMPORT_COUNT, 0),
        "broken_call_count": store.get_signal(entity, Signal.BROKEN_CALL_COUNT, 0),
        "stub_ratio": store.get_signal(entity, Signal.STUB_RATIO, 0),
        "impl_gini": store.get_signal(entity, Signal.IMPL_GINI, 0),
        "function_count": store.get_signal(entity, Signal.FUNCTION_COUNT, 0),
    }


INCOMPLETE_IMPLEMENTATION = Pattern(
    name="incomplete_implementation",
    scope=PatternScope.FILE,
    severity=0.80,
    requires={Signal.PHANTOM_IMPORT_COUNT.value, Signal.STUB_RATIO.value},
    condition="phantom_import_count > 0 OR broken_call_count > 0 OR stub_ratio > 0.6",
    predicate=_incomplete_impl_predicate,
    severity_fn=_incomplete_impl_severity,
    evidence_fn=_incomplete_impl_evidence,
    description="File with broken dependencies and/or stub functions",
    remediation="Fix imports, implement stubs, or remove dead code.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=1,
)


# ==============================================================================
# BUG_MAGNET - Files where most changes are bug fixes
# ==============================================================================


def _bug_magnet_predicate(store: FactStore, entity: EntityId) -> bool:
    """File with high fix ratio."""
    fix_ratio = store.get_signal(entity, Signal.FIX_RATIO, 0)
    total_changes = store.get_signal(entity, Signal.TOTAL_CHANGES, 0)

    return fix_ratio > 0.4 and total_changes >= 5


def _bug_magnet_severity(store: FactStore, entity: EntityId) -> float:
    """Higher severity for higher fix ratio."""
    fix_ratio = store.get_signal(entity, Signal.FIX_RATIO, 0)
    cognitive_load = store.get_signal(entity, Signal.COGNITIVE_LOAD, 0)

    severity = 0.80 + (fix_ratio - 0.4) * 0.3
    if cognitive_load > 30:
        severity += 0.05
    return min(0.95, severity)


def _bug_magnet_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for BUG_MAGNET."""
    return {
        "fix_ratio": store.get_signal(entity, Signal.FIX_RATIO, 0),
        "total_changes": store.get_signal(entity, Signal.TOTAL_CHANGES, 0),
        "cognitive_load": store.get_signal(entity, Signal.COGNITIVE_LOAD, 0),
    }


BUG_MAGNET = Pattern(
    name="bug_magnet",
    scope=PatternScope.FILE,
    severity=0.80,
    requires={Signal.FIX_RATIO.value, Signal.TOTAL_CHANGES.value},
    condition="fix_ratio > 0.4 AND total_changes >= 5",
    predicate=_bug_magnet_predicate,
    severity_fn=_bug_magnet_severity,
    evidence_fn=_bug_magnet_evidence,
    description="File where most changes are bug fixes",
    remediation="Refactor this code or add more tests. Look for root cause patterns.",
    category="fragile",
    hotspot_filtered=True,
    phase=3,
)


# ==============================================================================
# THRASHING_CODE - Erratic, unstable change patterns
# ==============================================================================


def _thrashing_code_predicate(store: FactStore, entity: EntityId) -> bool:
    """File with erratic change patterns."""
    churn_trajectory = store.get_signal(entity, Signal.CHURN_TRAJECTORY, "DORMANT")
    churn_cv = store.get_signal(entity, Signal.CHURN_CV, 0)
    total_changes = store.get_signal(entity, Signal.TOTAL_CHANGES, 0)
    lines = store.get_signal(entity, Signal.LINES, 0)

    is_spiking = churn_trajectory == "SPIKING"
    is_erratic = churn_cv > 1.5

    return (is_spiking or is_erratic) and total_changes >= 3 and lines >= 30


def _thrashing_code_severity(store: FactStore, entity: EntityId) -> float:
    """Higher severity for spiking + erratic."""
    churn_trajectory = store.get_signal(entity, Signal.CHURN_TRAJECTORY, "DORMANT")
    churn_cv = store.get_signal(entity, Signal.CHURN_CV, 0)

    is_spiking = churn_trajectory == "SPIKING"
    is_erratic = churn_cv > 1.5

    if is_spiking and is_erratic:
        return 0.90
    elif is_spiking:
        return 0.80
    elif churn_cv > 2.0:
        return 0.85
    return 0.75


def _thrashing_code_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for THRASHING_CODE."""
    return {
        "churn_trajectory": store.get_signal(entity, Signal.CHURN_TRAJECTORY, "DORMANT"),
        "churn_cv": store.get_signal(entity, Signal.CHURN_CV, 0),
        "total_changes": store.get_signal(entity, Signal.TOTAL_CHANGES, 0),
    }


THRASHING_CODE = Pattern(
    name="thrashing_code",
    scope=PatternScope.FILE,
    severity=0.75,
    requires={Signal.CHURN_TRAJECTORY.value, Signal.CHURN_CV.value},
    condition="(churn_trajectory = 'SPIKING' OR churn_cv > 1.5) AND total_changes >= 3",
    predicate=_thrashing_code_predicate,
    severity_fn=_thrashing_code_severity,
    evidence_fn=_thrashing_code_evidence,
    description="File with erratic, unstable change patterns",
    remediation="Review recent changes for conflicting requirements. Consider a design review.",
    category="fragile",
    hotspot_filtered=True,
    phase=3,
)


# ==============================================================================
# DIRECTORY_HOTSPOT - Directory-level hotspots
# ==============================================================================


def _directory_hotspot_predicate(store: FactStore, entity: EntityId) -> bool:
    """Directory with multiple high-risk files.

    Note: This pattern operates on MODULE scope entities but targets directories.
    It counts high-risk files within the directory.
    """
    # For MODULE scope, we check file counts within the module/directory
    file_count = store.get_signal(entity, Signal.FILE_COUNT, 0)

    if file_count < 3:
        return False

    # Skip test directories (check entity key for test patterns)
    if "test" in entity.key.lower():
        return False

    # We'll rely on mean_cognitive_load as a proxy for directory health
    # Threshold 15 aligns with typical HIGH_RISK_HUB cognitive_load levels
    mean_cog = store.get_signal(entity, Signal.MEAN_COGNITIVE_LOAD, 0)

    return mean_cog > 15 and file_count >= 3


def _directory_hotspot_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity for directory hotspots."""
    mean_cog = store.get_signal(entity, Signal.MEAN_COGNITIVE_LOAD, 0)

    if mean_cog > 40:
        return 0.90
    elif mean_cog > 30:
        return 0.85
    return 0.80


def _directory_hotspot_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for DIRECTORY_HOTSPOT."""
    return {
        "file_count": store.get_signal(entity, Signal.FILE_COUNT, 0),
        "mean_cognitive_load": store.get_signal(entity, Signal.MEAN_COGNITIVE_LOAD, 0),
        "health_score": store.get_signal(entity, Signal.HEALTH_SCORE, 0),
    }


DIRECTORY_HOTSPOT = Pattern(
    name="directory_hotspot",
    scope=PatternScope.MODULE,
    severity=0.80,
    requires={Signal.FILE_COUNT.value, Signal.MEAN_COGNITIVE_LOAD.value},
    condition="file_count >= 3 AND mean_cognitive_load > 20",
    predicate=_directory_hotspot_predicate,
    severity_fn=_directory_hotspot_severity,
    evidence_fn=_directory_hotspot_evidence,
    description="Entire directory has systemic issues",
    remediation="Consider refactoring this directory as a whole rather than individual files.",
    category="fragile",
    hotspot_filtered=False,
    phase=5,
)


# ==============================================================================
# DUPLICATE_INCOMPLETE - Clone pairs where both are incomplete
# ==============================================================================


def _duplicate_incomplete_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Both files are clones and incomplete."""
    entity_a, entity_b = pair

    # Check stub ratio or phantom imports for both
    stub_a = store.get_signal(entity_a, Signal.STUB_RATIO, 0)
    stub_b = store.get_signal(entity_b, Signal.STUB_RATIO, 0)
    phantom_a = store.get_signal(entity_a, Signal.PHANTOM_IMPORT_COUNT, 0)
    phantom_b = store.get_signal(entity_b, Signal.PHANTOM_IMPORT_COUNT, 0)

    incomplete_a = stub_a > 0.3 or phantom_a > 0
    incomplete_b = stub_b > 0.3 or phantom_b > 0

    # Check if they're similar (via compression ratio similarity)
    # In full implementation, would check CLONE relations
    comp_a = store.get_signal(entity_a, Signal.COMPRESSION_RATIO, 0)
    comp_b = store.get_signal(entity_b, Signal.COMPRESSION_RATIO, 0)
    similar_compression = abs(comp_a - comp_b) < 0.1 if comp_a > 0 and comp_b > 0 else False

    return incomplete_a and incomplete_b and similar_compression


def _duplicate_incomplete_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Higher severity for more incomplete clones."""
    entity_a, entity_b = pair
    stub_a = store.get_signal(entity_a, Signal.STUB_RATIO, 0)
    stub_b = store.get_signal(entity_b, Signal.STUB_RATIO, 0)
    phantom_a = store.get_signal(entity_a, Signal.PHANTOM_IMPORT_COUNT, 0)
    phantom_b = store.get_signal(entity_b, Signal.PHANTOM_IMPORT_COUNT, 0)

    severity = 0.75
    if stub_a > 0.5 and stub_b > 0.5:
        severity += 0.10
    if phantom_a > 0 and phantom_b > 0:
        severity += 0.10
    return min(0.90, severity)


def _duplicate_incomplete_evidence(
    store: FactStore, pair: tuple[EntityId, EntityId]
) -> dict[str, Any]:
    """Build evidence for DUPLICATE_INCOMPLETE."""
    entity_a, entity_b = pair
    return {
        "stub_ratio_a": store.get_signal(entity_a, Signal.STUB_RATIO, 0),
        "stub_ratio_b": store.get_signal(entity_b, Signal.STUB_RATIO, 0),
        "phantom_count_a": store.get_signal(entity_a, Signal.PHANTOM_IMPORT_COUNT, 0),
        "phantom_count_b": store.get_signal(entity_b, Signal.PHANTOM_IMPORT_COUNT, 0),
    }


DUPLICATE_INCOMPLETE = Pattern(
    name="duplicate_incomplete",
    scope=PatternScope.FILE_PAIR,
    severity=0.75,
    requires={Signal.STUB_RATIO.value, Signal.PHANTOM_IMPORT_COUNT.value},
    condition="both files incomplete (stub_ratio > 0.3 OR phantom_import_count > 0) AND similar",
    predicate=_duplicate_incomplete_predicate,
    severity_fn=_duplicate_incomplete_severity,
    evidence_fn=_duplicate_incomplete_evidence,
    description="Both files are incomplete copies",
    remediation="Complete one implementation and delete the duplicate.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=3,
)
