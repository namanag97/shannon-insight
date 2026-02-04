"""Analyzer implementations — fill the AnalysisStore."""

from typing import List

from .structural import StructuralAnalyzer
from .per_file import PerFileAnalyzer
from .temporal import TemporalAnalyzer
from .spectral import SpectralAnalyzer


def get_default_analyzers() -> List:
    """Return all default analyzers in recommended order."""
    return [
        StructuralAnalyzer(),
        PerFileAnalyzer(),
        TemporalAnalyzer(),
        SpectralAnalyzer(),
    ]
