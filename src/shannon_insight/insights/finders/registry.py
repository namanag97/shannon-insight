"""Pattern Registry — Central registry of all code issue patterns.

26 patterns organized by category, plus lookup functions for querying
patterns by name, category, scope, or phase.

Disabled patterns:
- CONWAY_VIOLATION: Disabled until author_distance computation is implemented.
"""

from __future__ import annotations

from shannon_insight.infrastructure.patterns import Pattern

from .patterns import (
    ACCIDENTAL_COUPLING,
    ARCHITECTURE_EROSION,
    BOUNDARY_MISMATCH,
    BUG_ATTRACTOR,
    CHRONIC_PROBLEM,
    COPY_PASTE_CLONE,
    DEAD_DEPENDENCY,
    DIRECTORY_HOTSPOT,
    DUPLICATE_INCOMPLETE,
    FLAT_ARCHITECTURE,
    GOD_FILE,
    HIDDEN_COUPLING,
    HIGH_RISK_HUB,
    HOLLOW_CODE,
    INCOMPLETE_IMPLEMENTATION,
    KNOWLEDGE_SILO,
    LAYER_VIOLATION,
    NAMING_DRIFT,
    ORPHAN_CODE,
    PHANTOM_IMPORTS,
    REVIEW_BLINDSPOT,
    THRASHING_CODE,
    TRUCK_FACTOR,
    UNSTABLE_FILE,
    WEAK_LINK,
    ZONE_OF_PAIN,
)

# ==============================================================================
# Pattern Registry
# ==============================================================================

ALL_PATTERNS: list[Pattern] = [
    # Core (7)
    HIGH_RISK_HUB,
    HIDDEN_COUPLING,
    GOD_FILE,
    UNSTABLE_FILE,
    BOUNDARY_MISMATCH,
    DEAD_DEPENDENCY,
    CHRONIC_PROBLEM,
    # AI Quality (8)
    ORPHAN_CODE,
    HOLLOW_CODE,
    PHANTOM_IMPORTS,
    COPY_PASTE_CLONE,
    FLAT_ARCHITECTURE,
    NAMING_DRIFT,
    INCOMPLETE_IMPLEMENTATION,
    DUPLICATE_INCOMPLETE,
    # Team/Ownership (3) - CONWAY_VIOLATION disabled
    KNOWLEDGE_SILO,
    REVIEW_BLINDSPOT,
    TRUCK_FACTOR,
    # Architecture (3)
    LAYER_VIOLATION,
    ZONE_OF_PAIN,
    ARCHITECTURE_EROSION,
    # Cross-Dimensional (3)
    WEAK_LINK,
    BUG_ATTRACTOR,
    ACCIDENTAL_COUPLING,
    # Temporal (2)
    THRASHING_CODE,
    DIRECTORY_HOTSPOT,
]

assert len(ALL_PATTERNS) == 26, f"Expected 26 patterns, got {len(ALL_PATTERNS)}"


# ==============================================================================
# Registry Functions
# ==============================================================================


def get_patterns_by_phase(phase: int) -> list[Pattern]:
    """Get all patterns available after a given phase.

    Args:
        phase: Phase number (0-7)

    Returns:
        List of patterns available at or before this phase
    """
    return [p for p in ALL_PATTERNS if p.phase <= phase]


def get_pattern_by_name(name: str) -> Pattern | None:
    """Look up a pattern by name.

    Args:
        name: Pattern name (e.g., "high_risk_hub")

    Returns:
        Pattern object if found, None otherwise
    """
    for p in ALL_PATTERNS:
        if p.name == name:
            return p
    return None


def get_patterns_by_category(category: str) -> list[Pattern]:
    """Get all patterns in a category.

    Args:
        category: Category name (existing, ai_quality, social_team, architecture, cross_dimensional)

    Returns:
        List of patterns in this category
    """
    return [p for p in ALL_PATTERNS if p.category == category]


def get_patterns_by_scope(scope_name: str) -> list[Pattern]:
    """Get all patterns with a given scope.

    Args:
        scope_name: Scope name (FILE, FILE_PAIR, MODULE, MODULE_PAIR, CODEBASE)

    Returns:
        List of patterns with this scope
    """
    return [p for p in ALL_PATTERNS if p.scope.value == scope_name.lower()]


def get_hotspot_filtered_patterns() -> list[Pattern]:
    """Get all patterns that require hotspot filtering.

    Returns:
        List of patterns with hotspot_filtered=True
    """
    return [p for p in ALL_PATTERNS if p.hotspot_filtered]
