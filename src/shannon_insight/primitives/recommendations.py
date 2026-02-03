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
        self.file_map = {f.path: f for f in files}
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
        file = self.file_map.get(path)

        if "high_centrality" in flags and "high_volatility" in flags:
            causes.append("Critical hub with unstable interface")

        if "high_cognitive_load" in flags and "structural_entropy_high" in flags:
            causes.append("Complex file with chaotic organization")

        if "semantic_coherence_low" in flags:
            if file and len(file.imports) > 10:
                causes.append(
                    f"Too many imports ({len(file.imports)}) - file handles unrelated concerns"
                )
            else:
                causes.append("Low cohesion - file handles multiple unrelated concerns")

        if "high_centrality" in flags:
            causes.append("High coupling - many files depend on this")

        if "structural_entropy_low" in flags:
            causes.append("Overly uniform structure - possible code duplication")

        if "high_cognitive_load" in flags:
            if file:
                causes.append(
                    f"High cognitive load: {file.functions} functions, "
                    f"complexity={file.complexity_score}, nesting={file.nesting_depth}"
                )
            else:
                causes.append("High cognitive load - too many concepts")

        if not causes:
            causes.append("General code quality concern")

        return causes

    def _generate_recommendations(
        self, path: str, flags: List[str], causes: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        file = self.file_map.get(path)

        if "high_cognitive_load" in flags:
            if file and file.nesting_depth > 5:
                recs.append(
                    f"Reduce nesting depth (currently {file.nesting_depth}) - flatten deeply nested conditionals"
                )
            if file and file.complexity_score > 10:
                recs.append(
                    f"Reduce cyclomatic complexity (currently {file.complexity_score}) - extract guard clauses"
                )
            recs.append("Split file into smaller, focused modules")
            recs.append("Extract helper functions to reduce complexity")

        if "high_centrality" in flags:
            recs.append("Implement dependency injection to reduce coupling")
            recs.append("Extract interface to isolate dependents")
            recs.append("Consider moving shared types to separate module")

        if "semantic_coherence_low" in flags:
            if file and len(file.imports) > 10:
                recs.append(
                    f"Reduce import count from {len(file.imports)} to <10 - group related imports"
                )
            recs.append("Separate concerns into different files")
            recs.append("Group related functions into cohesive modules")
            recs.append("Consider extracting unrelated functionality to separate files")

        if "high_volatility" in flags:
            recs.append("Stabilize interface - add integration tests")
            recs.append("Consider feature flags for experimental changes")
            recs.append("Review commit history for thrashing patterns")

        if "structural_entropy_high" in flags:
            recs.append("Refactor to follow consistent patterns")
            recs.append("Standardize code structure across file")

        if "structural_entropy_low" in flags:
            recs.append("Review for code duplication - extract common patterns")
            recs.append("Consider DRY principle - eliminate copy-paste code")

        # Add file-specific recommendations
        if file:
            if file.functions > 10:
                recs.append(
                    f"Extract business logic from {file.functions} functions into separate modules"
                )
            if file.structs > 5:
                recs.append(
                    f"Consider consolidating {file.structs} struct types into related modules"
                )
            if file.interfaces > 5:
                recs.append(f"Group {file.interfaces} interfaces by responsibility")

        if not recs:
            recs.append("Review file manually for code quality improvements")

        return recs
