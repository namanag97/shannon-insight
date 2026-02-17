"""Analyzer implementations — fill the AnalysisStore."""

from typing import TYPE_CHECKING

from .spectral import SpectralAnalyzer
from .structural import StructuralAnalyzer
from .temporal import TemporalAnalyzer

if TYPE_CHECKING:
    from ...config import AnalysisConfig


def get_default_analyzers(config: "AnalysisConfig") -> list:
    """Return Wave 1 analyzers (topo-sorted by requires/provides).

    Order is determined by requires/provides dependencies:
    1. StructuralAnalyzer: requires files, provides structural
    2. TemporalAnalyzer: requires files, provides git_history/cochange/churn
    3. SpectralAnalyzer: requires structural, provides spectral
    4. SemanticAnalyzer: requires file_syntax, provides semantics/roles
    5. ArchitectureAnalyzer: requires structural, provides architecture

    Args:
        config: Analysis configuration with algorithm parameters
    """
    from shannon_insight.architecture.analyzer import ArchitectureAnalyzer
    from shannon_insight.semantics.analyzer import SemanticAnalyzer

    return [
        StructuralAnalyzer(
            pagerank_damping=config.pagerank_damping,
            pagerank_iterations=config.pagerank_iterations,
            pagerank_tolerance=config.pagerank_tolerance,
        ),
        TemporalAnalyzer(
            max_commits=config.git_max_commits,
            min_commits=config.git_min_commits,
        ),
        SpectralAnalyzer(),
        SemanticAnalyzer(),
        ArchitectureAnalyzer(),
    ]


def get_wave2_analyzers() -> list:
    """Return Wave 2 analyzers (run after all Wave 1 complete).

    Wave 2 contains analyzers that need ALL Wave 1 signals to be ready.
    Currently: SignalFusionAnalyzer (unifies all signals into SignalField).
    """
    from shannon_insight.signals.analyzer import SignalFusionAnalyzer

    return [
        SignalFusionAnalyzer(),
    ]
