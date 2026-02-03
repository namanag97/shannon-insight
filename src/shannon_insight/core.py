"""Main pipeline orchestrator for Shannon Insight"""

import json
from dataclasses import asdict
from typing import List
from .models import AnomalyReport
from .analyzers import GoScanner, TypeScriptScanner
from .primitives import (
    PrimitiveExtractor,
    AnomalyDetector,
    SignalFusion,
    RecommendationEngine,
)


class CodebaseAnalyzer:
    """Main pipeline orchestrator"""

    def __init__(self, root_dir: str, language: str = "auto"):
        self.root_dir = root_dir
        self.language = language

    def analyze(self) -> List[AnomalyReport]:
        """Run full analysis pipeline"""
        print("=" * 80)
        print("SHANNON INSIGHT - Multi-Signal Codebase Quality Analyzer")
        print("=" * 80)
        print()

        # Layer 1: Data Collection
        print("Layer 1: Scanning codebase...")
        scanner = self._get_scanner()
        files = scanner.scan()
        print(f"  Found {len(files)} source files\n")

        if not files:
            print("No files found to analyze.")
            return []

        # Layer 2: Primitive Extraction
        print("Layer 2: Extracting primitives...")
        extractor = PrimitiveExtractor(files)
        primitives = extractor.extract_all()
        print(f"  Extracted 5 primitives for {len(primitives)} files\n")

        # Layer 3: Normalization & Anomaly Detection
        print("Layer 3: Normalizing and detecting anomalies...")
        detector = AnomalyDetector(primitives)
        normalized = detector.normalize()
        anomalies = detector.detect_anomalies(normalized, threshold=1.5)
        print(f"  Detected {len(anomalies)} anomalous files\n")

        # Layer 4: Signal Fusion
        print("Layer 4: Fusing signals with consistency check...")
        fusion = SignalFusion(primitives, normalized)
        fused_scores = fusion.fuse()
        print(f"  Computed consensus scores for {len(fused_scores)} files\n")

        # Layer 5: Recommendations
        print("Layer 5: Generating recommendations...")
        engine = RecommendationEngine(
            files, primitives, normalized, anomalies, fused_scores
        )
        reports = engine.generate()
        print(f"  Generated {len(reports)} actionable reports\n")

        return reports

    def _get_scanner(self):
        """Get appropriate scanner based on language"""
        if self.language == "go":
            return GoScanner(self.root_dir)
        elif self.language in ["typescript", "react", "javascript"]:
            return TypeScriptScanner(self.root_dir)
        else:
            # Auto-detect
            from pathlib import Path

            root = Path(self.root_dir)
            has_go = any(root.rglob("*.go"))
            has_ts = any(root.rglob("*.ts")) or any(root.rglob("*.tsx"))

            if has_go:
                print("Auto-detected: Go codebase\n")
                return GoScanner(self.root_dir)
            elif has_ts:
                print("Auto-detected: TypeScript/React codebase\n")
                return TypeScriptScanner(self.root_dir)
            else:
                print("Could not auto-detect language. Defaulting to Go.\n")
                return GoScanner(self.root_dir)

    def print_report(self, reports: List[AnomalyReport], top_n: int = 10):
        """Print human-readable analysis report"""
        print("=" * 80)
        print(f"TOP {min(top_n, len(reports))} FILES REQUIRING ATTENTION")
        print("=" * 80)
        print()

        for i, report in enumerate(reports[:top_n], 1):
            print(f"{i}. {report.file}")
            print(
                f"   Overall Score: {report.overall_score:.3f} (Confidence: {report.confidence:.2f})"
            )
            print()

            print("   Raw Primitives:")
            print(
                f"     • Structural Entropy:  {report.primitives.structural_entropy:.3f}"
            )
            print(
                f"     • Network Centrality:  {report.primitives.network_centrality:.3f}"
            )
            print(
                f"     • Churn Volatility:    {report.primitives.churn_volatility:.3f}"
            )
            print(
                f"     • Semantic Coherence:  {report.primitives.semantic_coherence:.3f}"
            )
            print(f"     • Cognitive Load:      {report.primitives.cognitive_load:.3f}")
            print()

            print("   Normalized (Z-Scores):")
            print(
                f"     • Structural Entropy:  {report.normalized_primitives.structural_entropy:+.2f}σ"
            )
            print(
                f"     • Network Centrality:  {report.normalized_primitives.network_centrality:+.2f}σ"
            )
            print(
                f"     • Churn Volatility:    {report.normalized_primitives.churn_volatility:+.2f}σ"
            )
            print(
                f"     • Semantic Coherence:  {report.normalized_primitives.semantic_coherence:+.2f}σ"
            )
            print(
                f"     • Cognitive Load:      {report.normalized_primitives.cognitive_load:+.2f}σ"
            )
            print()

            if report.root_causes:
                print("   Root Causes:")
                for cause in report.root_causes:
                    print(f"     ⚠ {cause}")
                print()

            if report.recommendations:
                print("   Recommendations:")
                for rec in report.recommendations:
                    print(f"     → {rec}")
                print()

            print("-" * 80)
            print()

    def export_json(
        self, reports: List[AnomalyReport], filename: str = "analysis_report.json"
    ):
        """Export analysis to JSON"""
        data = [asdict(r) for r in reports]

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Exported detailed report to {filename}")
