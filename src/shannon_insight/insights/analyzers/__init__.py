"""Analyzer implementations — fill the AnalysisStore."""

from .per_file import PerFileAnalyzer
from .spectral import SpectralAnalyzer
from .structural import StructuralAnalyzer
from .temporal import TemporalAnalyzer


def get_default_analyzers() -> list:
    """Return Wave 1 analyzers (topo-sorted by requires/provides)."""
    return [
        StructuralAnalyzer(),
        PerFileAnalyzer(),
        TemporalAnalyzer(),
        SpectralAnalyzer(),
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
