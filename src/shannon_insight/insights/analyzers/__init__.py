"""Analyzer implementations — fill the AnalysisStore."""

from .spectral import SpectralAnalyzer
from .structural import StructuralAnalyzer
from .temporal import TemporalAnalyzer


def get_default_analyzers() -> list:
    """Return Wave 1 analyzers (topo-sorted by requires/provides).

    Order is determined by requires/provides dependencies:
    1. StructuralAnalyzer: requires files, provides structural
    2. TemporalAnalyzer: requires files, provides git_history/cochange/churn
    3. SpectralAnalyzer: requires structural, provides spectral
    4. SemanticAnalyzer: requires file_syntax, provides semantics/roles
    5. ArchitectureAnalyzer: requires structural, provides architecture
    """
    from shannon_insight.architecture.analyzer import ArchitectureAnalyzer
    from shannon_insight.semantics.analyzer import SemanticAnalyzer

    return [
        StructuralAnalyzer(),
        TemporalAnalyzer(),
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
