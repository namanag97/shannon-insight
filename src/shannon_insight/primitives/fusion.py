"""Signal fusion with consistency checking"""

import statistics
from typing import Dict, Tuple
from ..models import Primitives


class SignalFusion:
    """Fuse multiple primitives with consistency checking"""

    def __init__(
        self, primitives: Dict[str, Primitives], normalized: Dict[str, Primitives]
    ):
        self.primitives = primitives
        self.normalized = normalized

    def fuse(self) -> Dict[str, Tuple[float, float]]:
        """Fuse signals with consistency weighting

        Returns: {path: (score, confidence)}
        """
        results = {}

        for path in self.primitives.keys():
            norm = self.normalized[path]

            # Extract z-scores
            scores = [
                norm.structural_entropy,
                norm.network_centrality,
                norm.churn_volatility,
                norm.semantic_coherence,
                norm.cognitive_load,
            ]

            # Compute consistency (inverse of variance)
            mean_score = statistics.mean(scores)
            variance = statistics.variance(scores) if len(scores) > 1 else 0

            # Consistency: 1 / (1 + variance/mean²)
            consistency = 1 / (1 + variance / (mean_score**2 + 1e-9))

            # Weighted average (equal weights for now)
            weights = [0.2, 0.25, 0.2, 0.15, 0.2]
            fused_score = sum(s * w for s, w in zip(scores, weights))

            # Apply consistency penalty
            final_score = consistency * abs(fused_score)

            results[path] = (final_score, consistency)

        return results
