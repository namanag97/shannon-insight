"""AI Code Quality patterns.

6 patterns for detecting AI-generated code issues.
Canonical spec: docs/v2/architecture/06-patterns/02-ai-quality.md
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
# 8. ORPHAN_CODE
# ==============================================================================


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


# ==============================================================================
# 9. HOLLOW_CODE
# ==============================================================================


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


# ==============================================================================
# 10. PHANTOM_IMPORTS
# ==============================================================================


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


# ==============================================================================
# 11. COPY_PASTE_CLONE
# ==============================================================================


def _copy_paste_clone_predicate(store: FactStore, pair: tuple[EntityId, EntityId]) -> bool:
    """Files with high content similarity (NCD < 0.3)."""
    file_a, file_b = pair

    # Check for CLONED_FROM relation
    cloned_rels = [
        r for r in store.outgoing(file_a, RelationType.CLONED_FROM) if r.target == file_b
    ]

    if not cloned_rels:
        return False

    ncd_score = cloned_rels[0].metadata.get("ncd", 1.0)
    return ncd_score < 0.3


def _copy_paste_clone_severity(store: FactStore, pair: tuple[EntityId, EntityId]) -> float:
    """Fixed severity."""
    return 0.50


def _copy_paste_clone_evidence(store: FactStore, pair: tuple[EntityId, EntityId]) -> dict[str, Any]:
    """Build evidence for COPY_PASTE_CLONE."""
    file_a, file_b = pair
    cloned_rels = [
        r for r in store.outgoing(file_a, RelationType.CLONED_FROM) if r.target == file_b
    ]

    if not cloned_rels:
        return {}

    return {
        "ncd": cloned_rels[0].metadata.get("ncd", 1.0),
        "lines_a": store.get_signal(file_a, Signal.LINES, 0),
        "lines_b": store.get_signal(file_b, Signal.LINES, 0),
    }


COPY_PASTE_CLONE = Pattern(
    name="copy_paste_clone",
    scope=PatternScope.FILE_PAIR,
    severity=0.50,
    requires={RelationType.CLONED_FROM.name},
    condition="NCD(A, B) < 0.3",
    predicate=_copy_paste_clone_predicate,
    severity_fn=_copy_paste_clone_severity,
    evidence_fn=_copy_paste_clone_evidence,
    description="Files with high content similarity (NCD)",
    remediation="Extract shared logic into a common module.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=3,
)


# ==============================================================================
# 12. FLAT_ARCHITECTURE
# ==============================================================================


def _flat_architecture_predicate(store: FactStore, entity: EntityId) -> bool:
    """Codebase has flat structure (max depth <= 1)."""
    # This is a CODEBASE-level pattern
    # Compute max depth across all files
    files = store.files()
    depths = [store.get_signal(f, Signal.DEPTH, 0) for f in files]
    max_depth = max(depths) if depths else 0

    # Check glue_deficit (global signal)
    glue_deficit = store.get_signal(entity, Signal.GLUE_DEFICIT, 0)

    return max_depth <= 1 and glue_deficit > 0.5


def _flat_architecture_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.60


def _flat_architecture_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for FLAT_ARCHITECTURE."""
    # Compute max depth
    files = store.files()
    depths = [store.get_signal(f, Signal.DEPTH, 0) for f in files]
    max_depth = max(depths) if depths else 0

    return {
        "max_depth": max_depth,
        "glue_deficit": store.get_signal(entity, Signal.GLUE_DEFICIT, 0),
        "orphan_ratio": store.get_signal(entity, Signal.ORPHAN_RATIO, 0),
    }


FLAT_ARCHITECTURE = Pattern(
    name="flat_architecture",
    scope=PatternScope.CODEBASE,
    severity=0.60,
    requires={Signal.DEPTH.name, Signal.GLUE_DEFICIT.name},
    condition="max(depth) <= 1 AND glue_deficit > 0.5",
    predicate=_flat_architecture_predicate,
    severity_fn=_flat_architecture_severity,
    evidence_fn=_flat_architecture_evidence,
    description="Codebase has flat structure with no layering",
    remediation="Introduce layering. Group related files into packages.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=3,
)


# ==============================================================================
# 13. NAMING_DRIFT
# ==============================================================================


def _naming_drift_predicate(store: FactStore, entity: EntityId) -> bool:
    """File name doesn't match content concepts."""
    naming_drift = store.get_signal(entity, Signal.NAMING_DRIFT, 0)
    return naming_drift > 0.7


def _naming_drift_severity(store: FactStore, entity: EntityId) -> float:
    """Fixed severity."""
    return 0.45


def _naming_drift_evidence(store: FactStore, entity: EntityId) -> dict[str, Any]:
    """Build evidence for NAMING_DRIFT."""
    return {
        "naming_drift": store.get_signal(entity, Signal.NAMING_DRIFT, 0),
        "concept_count": store.get_signal(entity, Signal.CONCEPT_COUNT, 0),
    }


NAMING_DRIFT = Pattern(
    name="naming_drift",
    scope=PatternScope.FILE,
    severity=0.45,
    requires={Signal.NAMING_DRIFT.name},
    condition="naming_drift > 0.7",
    predicate=_naming_drift_predicate,
    severity_fn=_naming_drift_severity,
    evidence_fn=_naming_drift_evidence,
    description="File name doesn't match content concepts",
    remediation="Rename file to match primary concept, or split if doing too much.",
    category="ai_quality",
    hotspot_filtered=False,
    phase=2,
)
