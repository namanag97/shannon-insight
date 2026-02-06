"""Finder implementations — read the AnalysisStore and produce Findings."""

from .boundary_mismatch import BoundaryMismatchFinder
from .dead_dependency import DeadDependencyFinder
from .god_file import GodFileFinder
from .hidden_coupling import HiddenCouplingFinder
from .high_risk_hub import HighRiskHubFinder
from .unstable_file import UnstableFileFinder


def get_default_finders() -> list:
    """Return all default finders."""
    return [
        HighRiskHubFinder(),
        HiddenCouplingFinder(),
        GodFileFinder(),
        UnstableFileFinder(),
        BoundaryMismatchFinder(),
        DeadDependencyFinder(),
    ]
