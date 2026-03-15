"""Phase executors for RuntimeKernel.

Each phase of the analysis pipeline has a dedicated executor that
implements the PhaseExecutor protocol.

Phases (in order):
1. DISCOVERY - Find source files
2. SCANNING - Extract syntax (tree-sitter or regex)
3. STRUCTURAL - Build graph, compute centrality
4. TEMPORAL - Extract git history, churn
5. TENSOR_BUILD - Build 4D relationship tensor
6. FUSION - Compute signals and composites
7. PATTERNS - Detect code issues
8. REPORTING - Rank findings, capture snapshot
"""

from .discovery import DiscoveryExecutor
from .fusion import FusionExecutor
from .patterns import PatternsExecutor
from .reporting import ReportingExecutor
from .scanning import ScanningExecutor
from .structural import StructuralExecutor
from .temporal import TemporalExecutor
from .tensor_build import TensorBuildExecutor

__all__ = [
    "DiscoveryExecutor",
    "ScanningExecutor",
    "StructuralExecutor",
    "TemporalExecutor",
    "TensorBuildExecutor",
    "FusionExecutor",
    "PatternsExecutor",
    "ReportingExecutor",
]

# Phase executors in pipeline order
PHASE_EXECUTORS = [
    DiscoveryExecutor(),
    ScanningExecutor(),
    StructuralExecutor(),
    TemporalExecutor(),
    TensorBuildExecutor(),
    FusionExecutor(),
    PatternsExecutor(),
    ReportingExecutor(),
]
