"""Pattern-based code issue detection.

Architecture:
- 28 patterns defined declaratively in patterns/ directory
- Pattern executor runs patterns against FactStore
- Produces infrastructure.Finding objects

Persistence finders (require database) work with historical snapshots.
"""

from .architecture_erosion import ArchitectureErosionFinder
from .chronic_problem import ChronicProblemFinder
from .executor import execute_patterns
from .registry import (
    ALL_PATTERNS,
    get_hotspot_filtered_patterns,
    get_pattern_by_name,
    get_patterns_by_category,
    get_patterns_by_phase,
    get_patterns_by_scope,
)


def get_persistence_finders() -> list:
    """Return finders that require database access for historical analysis.

    These finders work with historical snapshots and cannot be converted
    to the Pattern model (which works against single-snapshot FactStore).

    NOTE: ChronicProblemFinder is disabled by default because it can surface
    stale findings from history that no longer apply. Enable with --history flag.
    """
    return [
        ArchitectureErosionFinder(),
        # ChronicProblemFinder disabled - reads stale data from DB
        # Enable when we fix it to validate against current findings
    ]


__all__ = [
    # Pattern-based API
    "ALL_PATTERNS",
    "execute_patterns",
    "get_pattern_by_name",
    "get_patterns_by_phase",
    "get_patterns_by_category",
    "get_patterns_by_scope",
    "get_hotspot_filtered_patterns",
    # Persistence finders (require database)
    "ArchitectureErosionFinder",
    "ChronicProblemFinder",
    "get_persistence_finders",
]
