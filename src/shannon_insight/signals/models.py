"""Data models for signal computation."""

from dataclasses import dataclass
from typing import Dict

PrimitiveValues = Dict[str, float]


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
