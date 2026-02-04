"""
Shannon Insight - Multi-Level Codebase Structural Analysis

Mathematical codebase analysis using information theory and graph algorithms.
Produces structural intelligence — dependency graphs, community detection,
blast radius, cycle detection — not arbitrary scores.

Named after Claude Shannon, father of information theory.
"""

__version__ = "0.6.0"
__author__ = "Naman Agarwal"

from .core import CodebaseAnalyzer
from .models import FileMetrics, AnomalyReport, Primitives, AnalysisContext, DiffReport, PrimitiveValues, PipelineContext

__all__ = [
    "CodebaseAnalyzer",
    "Primitives",
    "PrimitiveValues",
    "FileMetrics",
    "AnomalyReport",
    "AnalysisContext",
    "DiffReport",
    "PipelineContext",
]
