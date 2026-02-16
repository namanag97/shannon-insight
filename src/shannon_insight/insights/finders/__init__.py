"""Finder implementations — Pattern-based finding detection.

V2 Architecture:
- 22 patterns defined declaratively in patterns/ directory
- Pattern executor runs patterns against FactStore
- Produces infrastructure.Finding objects

V1 Compatibility:
- get_default_finders() still works for backward compatibility
- Old finder classes are being phased out
"""

# V2: Pattern-based finders
from .executor import execute_patterns
from .registry import (
    ALL_PATTERNS,
    get_hotspot_filtered_patterns,
    get_pattern_by_name,
    get_patterns_by_category,
    get_patterns_by_phase,
    get_patterns_by_scope,
)

# V1 Compatibility: Import old finder classes for backward compatibility
# These will be deprecated once InsightKernel is updated to use execute_patterns()
try:
    from .accidental_coupling import AccidentalCouplingFinder
    from .architecture_erosion import ArchitectureErosionFinder
    from .boundary_mismatch import BoundaryMismatchFinder
    from .bug_attractor import BugAttractorFinder
    from .bug_magnet import BugMagnetFinder
    from .chronic_problem import ChronicProblemFinder
    from .conway_violation import ConwayViolationFinder
    from .copy_paste_clone import CopyPasteCloneFinder
    from .dead_dependency import DeadDependencyFinder
    from .directory_hotspot import DirectoryHotspotFinder
    from .duplicate_incomplete import DuplicateIncompleteFinder
    from .flat_architecture import FlatArchitectureFinder
    from .god_file import GodFileFinder
    from .hidden_coupling import HiddenCouplingFinder
    from .high_risk_hub import HighRiskHubFinder
    from .hollow_code import HollowCodeFinder
    from .incomplete_implementation import IncompleteImplementationFinder
    from .knowledge_silo import KnowledgeSiloFinder
    from .layer_violation import LayerViolationFinder
    from .naming_drift import NamingDriftFinder
    from .orphan_code import OrphanCodeFinder
    from .phantom_imports import PhantomImportsFinder
    from .review_blindspot import ReviewBlindspotFinder
    from .thrashing_code import ThrashingCodeFinder
    from .truck_factor import TruckFactorFinder
    from .unstable_file import UnstableFileFinder
    from .weak_link import WeakLinkFinder
    from .zone_of_pain import ZoneOfPainFinder

    _OLD_FINDERS_AVAILABLE = True
except ImportError:
    # Old finders have been deleted - v2 only
    _OLD_FINDERS_AVAILABLE = False


def get_default_finders() -> list:
    """Return all default finders (backward compatibility).

    Returns v1-style finder classes if available, otherwise returns empty list.
    New code should use execute_patterns() with ALL_PATTERNS instead.
    """
    if not _OLD_FINDERS_AVAILABLE:
        return []

    return [
        # Existing finders (Phase 0-5)
        HighRiskHubFinder(),
        HiddenCouplingFinder(),
        GodFileFinder(),
        UnstableFileFinder(),
        BoundaryMismatchFinder(),
        DeadDependencyFinder(),
        # Phase 6: Batch 1 - Structural
        OrphanCodeFinder(),
        HollowCodeFinder(),
        PhantomImportsFinder(),
        CopyPasteCloneFinder(),
        FlatArchitectureFinder(),
        NamingDriftFinder(),
        # Phase 6: Batch 2 - Architecture
        LayerViolationFinder(),
        ZoneOfPainFinder(),
        # Phase 6: Batch 3 - Cross-dimensional
        KnowledgeSiloFinder(),
        ConwayViolationFinder(),
        ReviewBlindspotFinder(),
        WeakLinkFinder(),
        BugAttractorFinder(),
        AccidentalCouplingFinder(),
        # NEW: Smart finders
        TruckFactorFinder(),
        BugMagnetFinder(),
        ThrashingCodeFinder(),
        DirectoryHotspotFinder(),
        IncompleteImplementationFinder(),
        DuplicateIncompleteFinder(),
    ]


def get_persistence_finders() -> list:
    """Return persistence-based finders (backward compatibility).

    Returns v1-style finder classes if available, otherwise returns empty list.
    """
    if not _OLD_FINDERS_AVAILABLE:
        return []

    return [
        ArchitectureErosionFinder(),
        ChronicProblemFinder(),
    ]


__all__ = [
    # V2: Pattern-based API
    "ALL_PATTERNS",
    "execute_patterns",
    "get_pattern_by_name",
    "get_patterns_by_phase",
    "get_patterns_by_category",
    "get_patterns_by_scope",
    "get_hotspot_filtered_patterns",
    # V1 Compatibility
    "get_default_finders",
    "get_persistence_finders",
]
