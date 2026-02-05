"""Analyzer implementations — fill the AnalysisStore."""

from typing import List

from .per_file import PerFileAnalyzer
from .spectral import SpectralAnalyzer
from .structural import StructuralAnalyzer
from .temporal import TemporalAnalyzer


def get_default_analyzers() -> List:
    """Return all default analyzers in recommended order."""
    return [
        StructuralAnalyzer(),
        PerFileAnalyzer(),
        TemporalAnalyzer(),
        SpectralAnalyzer(),
    ]
