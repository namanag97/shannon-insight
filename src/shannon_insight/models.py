"""Data models for Shannon Insight"""

from dataclasses import dataclass
from collections import Counter
from typing import List


@dataclass
class FileMetrics:
    """Raw observations for a single file"""

    path: str
    lines: int
    tokens: int
    imports: List[str]
    exports: List[str]
    functions: int
    interfaces: int
    structs: int
    complexity_score: float
    nesting_depth: int
    ast_node_types: Counter
    last_modified: float


@dataclass
class Primitives:
    """Five orthogonal quality primitives"""

    structural_entropy: float
    network_centrality: float
    churn_volatility: float
    semantic_coherence: float
    cognitive_load: float


@dataclass
class AnomalyReport:
    """Final analysis output"""

    file: str
    overall_score: float
    confidence: float
    primitives: Primitives
    normalized_primitives: Primitives
    anomaly_flags: List[str]
    root_causes: List[str]
    recommendations: List[str]
