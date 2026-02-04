"""
Shannon Insight - Multi-Signal Codebase Quality Analyzer

A mathematical approach to code quality analysis using five orthogonal primitives:
1. Structural Entropy - Disorder in code organization
2. Network Centrality - Importance in dependency graph
3. Churn Volatility - Instability of change patterns
4. Semantic Coherence - Conceptual focus
5. Cognitive Load - Mental effort to understand

Named after Claude Shannon, father of information theory.
"""

__version__ = "0.4.0"
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
