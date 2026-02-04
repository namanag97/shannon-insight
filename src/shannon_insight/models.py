"""Data models for Shannon Insight"""

from dataclasses import dataclass, field
from collections import Counter
from typing import Dict, List, Optional


# Type alias used by the extensible-primitive pipeline (Phase 3+)
PrimitiveValues = Dict[str, float]


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
    function_sizes: List[int] = field(default_factory=list)


@dataclass
class Primitives:
    """Five orthogonal quality primitives.

    Kept for backward-compatibility (attribute access via .structural_entropy etc.).
    Internally the pipeline now uses ``Dict[str, float]`` (``PrimitiveValues``).
    """

    structural_entropy: float
    network_centrality: float
    churn_volatility: float
    semantic_coherence: float
    cognitive_load: float

    def to_dict(self) -> PrimitiveValues:
        return {
            "structural_entropy": self.structural_entropy,
            "network_centrality": self.network_centrality,
            "churn_volatility": self.churn_volatility,
            "semantic_coherence": self.semantic_coherence,
            "cognitive_load": self.cognitive_load,
        }

    @classmethod
    def from_dict(cls, d: PrimitiveValues) -> "Primitives":
        return cls(
            structural_entropy=d.get("structural_entropy", 0.0),
            network_centrality=d.get("network_centrality", 0.0),
            churn_volatility=d.get("churn_volatility", 0.0),
            semantic_coherence=d.get("semantic_coherence", 0.0),
            cognitive_load=d.get("cognitive_load", 0.0),
        )


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


@dataclass
class AnalysisContext:
    """Context passed to formatters alongside reports."""

    total_files_scanned: int
    detected_languages: List[str]
    settings: object  # AnalysisSettings — kept as object to avoid circular import
    top_n: int = 15
    explain_pattern: Optional[str] = None


@dataclass
class PipelineContext:
    """Mutable context that flows through composable pipeline stages."""

    files: List[FileMetrics]
    settings: object  # AnalysisSettings
    root_dir: str = ""
    cache: object = None  # Optional[AnalysisCache]
    config_hash: str = ""

    # Filled by stages as they run
    primitives: Optional[Dict] = None        # Dict[str, Primitives]
    normalized: Optional[Dict] = None        # Dict[str, Primitives]
    anomalies: Optional[Dict] = None         # Dict[str, List[str]]
    fused_scores: Optional[Dict] = None      # Dict[str, Tuple[float, float]]
    reports: Optional[List] = None           # List[AnomalyReport]


@dataclass
class DiffReport:
    """A single file's diff between current and baseline analysis."""

    file: str
    status: str  # "new" | "modified" | "improved" | "regressed"
    current: AnomalyReport  # full current report
    previous_score: Optional[float] = None
    score_delta: Optional[float] = None
    previous_confidence: Optional[float] = None
