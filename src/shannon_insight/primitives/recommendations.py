"""Generate actionable recommendations from fused signals"""

from typing import Dict, List, Tuple
from ..models import FileMetrics, Primitives, AnomalyReport


class RecommendationEngine:
    """Generate actionable recommendations from fused signals"""

    def __init__(
        self,
        files: List[FileMetrics],
        primitives: Dict[str, Primitives],
        normalized: Dict[str, Primitives],
        anomalies: Dict[str, List[str]],
        fused_scores: Dict[str, Tuple[float, float]],
    ):
        self.files = files
        self.primitives = primitives
        self.normalized = normalized
        self.anomalies = anomalies
        self.fused_scores = fused_scores

    def generate(self) -> List[AnomalyReport]:
        """Generate comprehensive analysis reports"""
        reports = []

        # Sort by fused score (descending)
        sorted_files = sorted(
            self.fused_scores.items(), key=lambda x: x[1][0], reverse=True
        )

        for path, (score, confidence) in sorted_files:
            if path not in self.anomalies:
                continue  # Skip non-anomalous files

            flags = self.anomalies[path]
            root_causes = self._identify_root_causes(path, flags)
            recommendations = self._generate_recommendations(path, flags, root_causes)

            report = AnomalyReport(
                file=path,
                overall_score=score,
                confidence=confidence,
                primitives=self.primitives[path],
                normalized_primitives=self.normalized[path],
                anomaly_flags=flags,
                root_causes=root_causes,
                recommendations=recommendations,
            )

            reports.append(report)

        return reports

    def _identify_root_causes(self, path: str, flags: List[str]) -> List[str]:
        """Identify root causes from anomaly flags"""
        causes = []

        if "high_centrality" in flags and "high_volatility" in flags:
            causes.append("Critical hub with unstable interface")

        if "high_cognitive_load" in flags and "structural_entropy_high" in flags:
            causes.append("Complex file with chaotic organization")

        if "semantic_coherence_low" in flags:
            causes.append("Low cohesion - file handles unrelated concerns")

        if "high_centrality" in flags:
            causes.append("High coupling - many dependencies")

        if "structural_entropy_low" in flags:
            causes.append("Overly uniform structure - possible code duplication")

        return causes

    def _generate_recommendations(
        self, path: str, flags: List[str], causes: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []

        if "high_cognitive_load" in flags:
            recs.append("Split into smaller, focused modules")
            recs.append("Extract helper functions to reduce complexity")

        if "high_centrality" in flags:
            recs.append("Implement dependency injection to reduce coupling")
            recs.append("Extract interface to isolate dependents")

        if "semantic_coherence_low" in flags:
            recs.append("Separate concerns into different files")
            recs.append("Group related functions into cohesive modules")

        if "high_volatility" in flags:
            recs.append("Stabilize interface - add integration tests")
            recs.append("Consider feature flags for experimental changes")

        if "structural_entropy_high" in flags:
            recs.append("Refactor to follow consistent patterns")
            recs.append("Standardize code structure across file")

        return recs
