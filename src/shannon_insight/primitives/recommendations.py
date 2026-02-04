"""Generate actionable, context-aware recommendations from fused signals."""

import os
import statistics
from pathlib import Path
from typing import Dict, List, Tuple

from ..models import FileMetrics, Primitives, AnomalyReport
from ..math import Gini, IdentifierAnalyzer


# Filename stems / directory patterns that indicate expected hub roles.
# High centrality for these files is by design, not a defect.
_MODEL_STEMS = {"models", "types", "schemas", "entities", "dataclasses"}
_BASE_STEMS = {"base", "abstract", "interface", "interfaces", "abc"}
_CONFIG_STEMS = {"config", "settings", "constants", "defaults", "conf"}
_INIT_STEMS = {"__init__"}
_TEST_DIR_PARTS = {"test_codebase", "tests", "test", "testing", "fixtures",
                   "testdata", "test_data", "examples", "demo", "complexity_demo"}


def _classify_file_role(path: str) -> str:
    """Classify a file into a role based on its name and location.

    Returns one of:
        "model"    — data model / type definitions (expected hub)
        "base"     — base class / ABC (expected hub)
        "config"   — configuration / constants (expected hub)
        "init"     — package __init__ (expected hub, re-export only)
        "test"     — test fixture / example data
        "service"  — normal business logic (default)
    """
    stem = os.path.splitext(os.path.basename(path))[0].lower()
    parts = set(path.replace("\\", "/").lower().split("/"))

    if parts & _TEST_DIR_PARTS:
        return "test"
    if stem in _INIT_STEMS:
        return "init"
    if stem in _MODEL_STEMS:
        return "model"
    if stem in _BASE_STEMS:
        return "base"
    if stem in _CONFIG_STEMS:
        return "config"
    return "service"


class RecommendationEngine:
    """Generate context-aware recommendations from fused signals."""

    def __init__(
        self,
        files: List[FileMetrics],
        primitives: Dict[str, Primitives],
        normalized: Dict[str, Primitives],
        anomalies: Dict[str, List[str]],
        fused_scores: Dict[str, Tuple[float, float]],
        root_dir: str = "",
    ):
        self.files = files
        self.file_map = {f.path: f for f in files}
        self.primitives = primitives
        self.normalized = normalized
        self.anomalies = anomalies
        self.fused_scores = fused_scores
        self.root_dir = Path(root_dir) if root_dir else None

    def generate(self) -> List[AnomalyReport]:
        """Generate comprehensive analysis reports."""
        reports = []

        sorted_files = sorted(
            self.fused_scores.items(), key=lambda x: x[1][0], reverse=True
        )

        for path, (score, confidence) in sorted_files:
            if path not in self.anomalies:
                continue

            flags = self.anomalies[path]
            role = _classify_file_role(path)
            root_causes = self._identify_root_causes(path, flags, role)
            recommendations = self._generate_recommendations(path, flags, root_causes, role)

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

    # ------------------------------------------------------------------
    # Root cause identification
    # ------------------------------------------------------------------

    def _identify_root_causes(
        self, path: str, flags: List[str], role: str
    ) -> List[str]:
        causes = []
        file = self.file_map.get(path)

        # -- combination patterns --

        if "high_centrality" in flags and "high_volatility" in flags:
            if role in ("model", "base", "config", "init"):
                causes.append(
                    f"Frequently-changed {role} file that many modules depend on"
                )
            else:
                causes.append("Critical hub with unstable interface")

        if "high_cognitive_load" in flags and "structural_entropy_high" in flags:
            causes.append("Complex file with dense, non-repetitive code")

        # -- cognitive load with function size detail --

        if "high_cognitive_load" in flags:
            if file and file.function_sizes and len(file.function_sizes) > 1:
                try:
                    gini = Gini.gini_coefficient(file.function_sizes)
                except ValueError:
                    gini = 0.0
                max_fn = max(file.function_sizes)
                median_fn = statistics.median(file.function_sizes)

                if gini > 0.5:
                    causes.append(
                        f"High cognitive load concentrated in large functions "
                        f"(max={max_fn} lines, median={median_fn:.0f}, Gini={gini:.2f})"
                    )
                else:
                    causes.append(
                        f"High cognitive load: {file.functions} functions, "
                        f"complexity={file.complexity_score}, nesting={file.nesting_depth}"
                    )
            elif file:
                causes.append(
                    f"High cognitive load: {file.functions} functions, "
                    f"complexity={file.complexity_score}, nesting={file.nesting_depth}"
                )
            else:
                causes.append("High cognitive load — too many concepts")

        # -- semantic coherence with identifier cluster detail --

        if "semantic_coherence_low" in flags:
            clusters = self._get_identifier_clusters(path)
            if clusters and len(clusters) > 1:
                cluster_labels = []
                for c in clusters[:3]:
                    label = ", ".join(c['top_terms'][:3])
                    cluster_labels.append(label)
                causes.append(
                    f"{len(clusters)} responsibility clusters detected: "
                    + " | ".join(cluster_labels)
                )
            else:
                causes.append("Low cohesion — file handles multiple unrelated concerns")

        # -- centrality --

        if "high_centrality" in flags:
            if role == "model":
                causes.append(
                    "Central data-model file — high centrality is expected "
                    "but changes here ripple widely"
                )
            elif role == "base":
                causes.append(
                    "Base class inherited across the project — high centrality "
                    "is by design"
                )
            elif role == "config":
                causes.append(
                    "Configuration hub — many modules read settings from here"
                )
            elif role == "init":
                causes.append(
                    "Package __init__ re-exports — centrality is structural, not a defect"
                )
            else:
                causes.append("High coupling — many files depend on this")

        # -- compression complexity --

        if "structural_entropy_low" in flags:
            causes.append("Highly repetitive code — possible duplication")

        if "structural_entropy_high" in flags:
            if "high_cognitive_load" not in flags:
                causes.append("Very dense, non-repetitive code")

        if not causes:
            causes.append("General code quality concern")

        return causes

    # ------------------------------------------------------------------
    # Recommendation generation
    # ------------------------------------------------------------------

    def _generate_recommendations(
        self, path: str, flags: List[str], causes: List[str], role: str
    ) -> List[str]:
        recs: List[str] = []
        file = self.file_map.get(path)

        # ---- cognitive load with function-size-aware advice ----
        if "high_cognitive_load" in flags:
            if file and file.function_sizes and len(file.function_sizes) > 1:
                try:
                    gini = Gini.gini_coefficient(file.function_sizes)
                except ValueError:
                    gini = 0.0
                max_fn = max(file.function_sizes)
                median_fn = statistics.median(file.function_sizes)

                if gini > 0.5 and max_fn > median_fn * 3:
                    recs.append(
                        f"Extract the largest function ({max_fn} lines, "
                        f"{max_fn / median_fn:.0f}x the median) into smaller helpers"
                    )

            if file and file.nesting_depth > 5:
                recs.append(
                    f"Reduce nesting depth (currently {file.nesting_depth}) "
                    f"— flatten deeply nested conditionals"
                )
            if file and file.complexity_score > 10:
                recs.append(
                    f"Reduce cyclomatic complexity (currently {file.complexity_score}) "
                    f"— extract guard clauses"
                )
            recs.append("Split file into smaller, focused modules")

        # ---- centrality — role-aware ----
        if "high_centrality" in flags:
            if role == "model":
                recs.append(
                    "Keep data classes stable — changes here affect many consumers"
                )
                recs.append(
                    "Consider versioning or deprecation warnings before removing fields"
                )
                if file and file.functions + file.structs + file.interfaces > 8:
                    recs.append(
                        "File has grown large — consider splitting into "
                        "domain-specific model modules"
                    )
            elif role == "base":
                recs.append(
                    "Keep base class interface narrow and stable"
                )
                recs.append(
                    "Add regression tests for the public API so subclass "
                    "contracts don't break"
                )
            elif role == "config":
                recs.append("Validate all new settings with pydantic/schema checks")
                recs.append(
                    "Document configuration options to reduce churn from misuse"
                )
            elif role == "init":
                recs.append(
                    "Re-export only the public API — avoid pulling in heavy "
                    "internal modules"
                )
            else:
                recs.append("Implement dependency injection to reduce coupling")
                recs.append("Extract interface to isolate dependents")
                recs.append("Consider moving shared types to a separate module")

        # ---- identifier coherence ----
        if "semantic_coherence_low" in flags:
            clusters = self._get_identifier_clusters(path)
            if clusters and len(clusters) > 1:
                for c in clusters[:3]:
                    label = ", ".join(c['top_terms'][:3])
                    recs.append(
                        f"Extract {label} logic into a separate module"
                    )
            else:
                recs.append("Separate concerns into different files")
                recs.append("Group related functions into cohesive modules")

        # ---- volatility ----
        if "high_volatility" in flags:
            if role in ("model", "base", "config"):
                recs.append(
                    "Add integration tests to catch regressions from frequent changes"
                )
            else:
                recs.append("Stabilize interface — add integration tests")
                recs.append("Review commit history for thrashing patterns")

        # ---- compression complexity ----
        if "structural_entropy_high" in flags:
            recs.append("Refactor to reduce information density")
            recs.append("Extract repeated logic patterns into shared helpers")

        if "structural_entropy_low" in flags:
            recs.append("Review for code duplication — extract common patterns")

        # ---- file-specific metric-driven advice ----
        if file:
            if file.functions > 10:
                recs.append(
                    f"Extract business logic from {file.functions} functions "
                    f"into separate modules"
                )
            if file.structs > 5:
                recs.append(
                    f"Consider consolidating {file.structs} struct types "
                    f"into related modules"
                )
            if file.interfaces > 5:
                recs.append(
                    f"Group {file.interfaces} interfaces by responsibility"
                )

        if not recs:
            recs.append("Review file manually for code quality improvements")

        return recs

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_identifier_clusters(self, path: str) -> List[Dict]:
        """Get identifier clusters for a file (reads from disk)."""
        file_path = Path(path)
        if not file_path.is_absolute():
            if self.root_dir:
                resolved = self.root_dir / path
                if resolved.exists():
                    file_path = resolved
            if not file_path.exists():
                # Fallback: try from cwd
                file_path = Path(path)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            tokens = IdentifierAnalyzer.extract_identifier_tokens(content)
            return IdentifierAnalyzer.detect_semantic_clusters(tokens)
        except Exception:
            return []
