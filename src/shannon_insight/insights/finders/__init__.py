"""Finder implementations — read the AnalysisStore and produce Findings."""

from typing import List

from .high_risk_hub import HighRiskHubFinder
from .hidden_coupling import HiddenCouplingFinder
from .dead_dependency import DeadDependencyFinder
from .unstable_file import UnstableFileFinder
from .god_file import GodFileFinder
from .boundary_mismatch import BoundaryMismatchFinder


def get_default_finders() -> List:
    """Return all default finders."""
    return [
        HighRiskHubFinder(),
        HiddenCouplingFinder(),
        GodFileFinder(),
        UnstableFileFinder(),
        BoundaryMismatchFinder(),
        DeadDependencyFinder(),
    ]
