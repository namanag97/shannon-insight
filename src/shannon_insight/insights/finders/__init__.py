"""Finder implementations — read the AnalysisStore and produce Findings.

Phase 6 adds 15 new finders in 3 batches:
- Batch 1: Structural (6 finders)
- Batch 2: Architecture (2 finders)
- Batch 3: Cross-dimensional (6 finders)

Plus existing Phase 0-5 finders (6).
Total: 21 finders (22 with CHRONIC_PROBLEM deferred to Phase 7).
"""

# Existing finders (Phase 0-5)
from .accidental_coupling import AccidentalCouplingFinder
from .boundary_mismatch import BoundaryMismatchFinder
from .bug_attractor import BugAttractorFinder
from .conway_violation import ConwayViolationFinder
from .copy_paste_clone import CopyPasteCloneFinder
from .dead_dependency import DeadDependencyFinder
from .flat_architecture import FlatArchitectureFinder
from .god_file import GodFileFinder
from .hidden_coupling import HiddenCouplingFinder
from .high_risk_hub import HighRiskHubFinder
from .hollow_code import HollowCodeFinder

# Phase 6: Batch 3 - Cross-dimensional finders
from .knowledge_silo import KnowledgeSiloFinder

# Phase 6: Batch 2 - Architecture finders
from .layer_violation import LayerViolationFinder
from .naming_drift import NamingDriftFinder

# Phase 6: Batch 1 - Structural finders
from .orphan_code import OrphanCodeFinder
from .phantom_imports import PhantomImportsFinder
from .review_blindspot import ReviewBlindspotFinder
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
    ]
