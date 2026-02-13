"""Finder implementations — read the AnalysisStore and produce Findings.

Phase 6 adds 15 new finders in 3 batches:
- Batch 1: Structural (6 finders)
- Batch 2: Architecture (2 finders)
- Batch 3: Cross-dimensional (6 finders)

Phase 7 adds 2 persistence-based finders:
- chronic_problem: findings persisting 3+ snapshots
- architecture_erosion: violation_rate increasing 3+ snapshots

Plus existing Phase 0-5 finders (6).
Total: 22 finders.
"""

# Existing finders (Phase 0-5)
from .accidental_coupling import AccidentalCouplingFinder

# Phase 7: Persistence-based finders
from .architecture_erosion import ArchitectureErosionFinder
from .boundary_mismatch import BoundaryMismatchFinder
from .bug_attractor import BugAttractorFinder
from .bug_magnet import BugMagnetFinder

# Phase 7: Persistence-based finders
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

# NEW: Incomplete/Dead code finders
from .incomplete_implementation import IncompleteImplementationFinder

# Phase 6: Batch 3 - Cross-dimensional finders
from .knowledge_silo import KnowledgeSiloFinder

# Phase 6: Batch 2 - Architecture finders
from .layer_violation import LayerViolationFinder
from .naming_drift import NamingDriftFinder

# Phase 6: Batch 1 - Structural finders
from .orphan_code import OrphanCodeFinder
from .phantom_imports import PhantomImportsFinder
from .review_blindspot import ReviewBlindspotFinder
from .thrashing_code import ThrashingCodeFinder

# NEW: Smart finders that actually use temporal signals
from .truck_factor import TruckFactorFinder
from .unstable_file import UnstableFileFinder
from .weak_link import WeakLinkFinder
from .zone_of_pain import ZoneOfPainFinder


def get_default_finders() -> list:
    """Return all default finders (Phase 0-6).

    Returns finders in priority order:
    1. Cross-dimensional (highest severity, most complex)
    2. Architecture
    3. Structural
    4. Original finders

    Note: Persistence-based finders (chronic_problem, architecture_erosion)
    are NOT included here. Use get_persistence_finders() for those.
    """
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
        # NEW: Smart finders using previously-unused signals
        TruckFactorFinder(),  # bus_factor + centrality
        BugMagnetFinder(),  # fix_ratio + churn
        ThrashingCodeFinder(),  # churn_trajectory + churn_cv
        DirectoryHotspotFinder(),  # directory-level aggregates
        # NEW: Incomplete/Dead code finders
        IncompleteImplementationFinder(),  # stub_ratio, phantom_imports, broken_calls
        DuplicateIncompleteFinder(),  # clones + incomplete
    ]


def get_persistence_finders() -> list:
    """Return persistence-based finders (Phase 7).

    These finders require a database connection and query the
    finding_lifecycle and signal_history tables.

    Returns finders in priority order:
    1. architecture_erosion (codebase-level)
    2. chronic_problem (wraps other findings)
    """
    return [
        ArchitectureErosionFinder(),
        ChronicProblemFinder(),
    ]
