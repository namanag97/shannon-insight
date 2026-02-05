"""
Shannon Insight - Multi-Level Codebase Structural Analysis

Mathematical codebase analysis using information theory and graph algorithms.
Produces structural intelligence — dependency graphs, community detection,
blast radius, cycle detection — not arbitrary scores.

Named after Claude Shannon, father of information theory.
"""

__version__ = "0.7.0"
__author__ = "Naman Agarwal"

from .insights import Finding, InsightKernel, InsightResult
from .models import FileMetrics, Primitives, PrimitiveValues

__all__ = [
    "InsightKernel",
    "InsightResult",
    "Finding",
    "FileMetrics",
    "Primitives",
    "PrimitiveValues",
]
