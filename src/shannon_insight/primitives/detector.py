"""Anomaly detection using statistical methods"""

import statistics
from typing import Dict, List
from ..models import Primitives


class AnomalyDetector:
    """Detect anomalies in primitives using statistical methods"""

    def __init__(self, primitives: Dict[str, Primitives]):
        self.primitives = primitives

    def normalize(self) -> Dict[str, Primitives]:
        """Normalize all primitives to z-scores"""
        normalized = {}

        # Extract each primitive into separate lists
        entropy_vals = [p.structural_entropy for p in self.primitives.values()]
        centrality_vals = [p.network_centrality for p in self.primitives.values()]
        volatility_vals = [p.churn_volatility for p in self.primitives.values()]
        coherence_vals = [p.semantic_coherence for p in self.primitives.values()]
        load_vals = [p.cognitive_load for p in self.primitives.values()]

        # Compute z-scores
        entropy_z = self._z_scores(entropy_vals)
        centrality_z = self._z_scores(centrality_vals)
        volatility_z = self._z_scores(volatility_vals)
        coherence_z = self._z_scores(coherence_vals)
        load_z = self._z_scores(load_vals)

        # Build normalized primitives
        paths = list(self.primitives.keys())
        for i, path in enumerate(paths):
            normalized[path] = Primitives(
                structural_entropy=entropy_z[i],
                network_centrality=centrality_z[i],
                churn_volatility=volatility_z[i],
                semantic_coherence=coherence_z[i],
                cognitive_load=load_z[i],
            )

        return normalized

    def _z_scores(self, values: List[float]) -> List[float]:
        """Compute z-scores: (x - μ) / σ"""
        if not values or len(values) < 2:
            return [0] * len(values)

        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        if stdev == 0:
            return [0] * len(values)

        return [(x - mean) / stdev for x in values]

    def detect_anomalies(
        self, normalized: Dict[str, Primitives], threshold: float = 1.5
    ) -> Dict[str, List[str]]:
        """Detect which primitives are anomalous (z-score > threshold)"""
        anomalies = {}

        for path, prims in normalized.items():
            flags = []

            if abs(prims.structural_entropy) > threshold:
                direction = "high" if prims.structural_entropy > 0 else "low"
                flags.append(f"structural_entropy_{direction}")

            if prims.network_centrality > threshold:
                flags.append("high_centrality")

            if prims.churn_volatility > threshold:
                flags.append("high_volatility")

            if abs(prims.semantic_coherence) > threshold:
                direction = "low" if prims.semantic_coherence < 0 else "high"
                flags.append(f"semantic_coherence_{direction}")

            if prims.cognitive_load > threshold:
                flags.append("high_cognitive_load")

            if flags:
                anomalies[path] = flags

        return anomalies
