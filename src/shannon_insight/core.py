"""Main pipeline orchestrator for Shannon Insight"""

import csv
import io
import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TextColumn,
)
from rich.table import Table

from .models import AnomalyReport
from .analyzers import GoScanner, TypeScriptScanner, PythonScanner
from .primitives import (
    PrimitiveExtractor,
    AnomalyDetector,
    SignalFusion,
    RecommendationEngine,
)
from .config import AnalysisSettings, default_settings
from .cache import AnalysisCache, compute_config_hash
from .logging_config import get_logger
from .security import validate_root_directory
from .exceptions import (
    InvalidPathError,
    UnsupportedLanguageError,
    InsufficientDataError,
)

logger = get_logger(__name__)
console = Console()


class CodebaseAnalyzer:
    """Main pipeline orchestrator with enterprise features"""

    SUPPORTED_LANGUAGES = {"auto", "go", "typescript", "react", "javascript", "python"}

    def __init__(
        self,
        root_dir: "Path | str",
        language: str = "auto",
        settings: Optional[AnalysisSettings] = None,
    ):
        """
        Initialize codebase analyzer.

        Args:
            root_dir: Root directory of codebase to analyze
            language: Programming language (auto, go, typescript, react, javascript)
            settings: Analysis settings (uses defaults if not provided)

        Raises:
            InvalidPathError: If root_dir is invalid
            UnsupportedLanguageError: If language is not supported
        """
        # Validate root directory
        self.root_dir = validate_root_directory(Path(root_dir))
        logger.info(f"Analyzing codebase at: {self.root_dir}")

        # Validate language
        if language not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(language, list(self.SUPPORTED_LANGUAGES))
        self.language = language

        # Load settings
        self.settings = settings or default_settings
        logger.debug(
            f"Settings: cache={self.settings.enable_cache}, "
            f"workers={self.settings.parallel_workers}, "
            f"threshold={self.settings.z_score_threshold}"
        )

        # Initialize cache
        self.cache = None
        if self.settings.enable_cache:
            self.cache = AnalysisCache(
                cache_dir=self.settings.cache_dir,
                ttl_hours=self.settings.cache_ttl_hours,
                enabled=True,
            )
            logger.debug(f"Cache enabled at {self.settings.cache_dir}")

        # Compute config hash for cache invalidation
        self.config_hash = compute_config_hash(self.settings.model_dump())

        # Track analysis metadata
        self._total_files_scanned = 0
        self._detected_language = language

    def analyze(self) -> List[AnomalyReport]:
        """
        Run full analysis pipeline with progress tracking.

        Returns:
            List of anomaly reports sorted by severity

        Raises:
            InsufficientDataError: If no files found to analyze
        """
        console.print()
        console.print("[bold cyan]=" * 40)
        console.print(
            "[bold cyan]SHANNON INSIGHT - Multi-Signal Codebase Quality Analyzer"
        )
        console.print("[bold cyan]=" * 40)
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False,
        ) as progress:
            # Layer 1: Data Collection
            scan_task = progress.add_task(
                "[cyan]Layer 1: Scanning codebase...", total=None
            )

            scanner = self._get_scanner()
            files = scanner.scan()

            if not files:
                logger.warning("No files found to analyze")
                raise InsufficientDataError(
                    "No source files found in the specified directory",
                    minimum_required=1,
                )

            self._total_files_scanned = len(files)

            progress.update(
                scan_task,
                completed=True,
                description=f"[green]Layer 1: Found {len(files)} source files",
            )
            logger.info(f"Scanned {len(files)} files")

            # Layer 2: Primitive Extraction
            extract_task = progress.add_task(
                "[cyan]Layer 2: Extracting primitives...", total=100
            )

            extractor = PrimitiveExtractor(
                files, cache=self.cache, config_hash=self.config_hash
            )
            primitives = extractor.extract_all()

            progress.update(
                extract_task,
                completed=100,
                description=f"[green]Layer 2: Extracted 5 primitives for {len(primitives)} files",
            )
            logger.info(f"Extracted primitives for {len(primitives)} files")

            # Layer 3: Normalization & Anomaly Detection
            detect_task = progress.add_task(
                "[cyan]Layer 3: Normalizing and detecting anomalies...", total=100
            )

            detector = AnomalyDetector(
                primitives, threshold=self.settings.z_score_threshold
            )
            normalized = detector.normalize()
            anomalies = detector.detect_anomalies(normalized)

            progress.update(
                detect_task,
                completed=100,
                description=f"[green]Layer 3: Detected {len(anomalies)} anomalous files",
            )
            logger.info(f"Detected {len(anomalies)} anomalies")

            # Layer 4: Signal Fusion
            fusion_task = progress.add_task(
                "[cyan]Layer 4: Fusing signals with consistency check...", total=100
            )

            fusion = SignalFusion(
                primitives, normalized, weights=self.settings.fusion_weights
            )
            fused_scores = fusion.fuse()

            progress.update(
                fusion_task,
                completed=100,
                description=f"[green]Layer 4: Computed consensus scores for {len(fused_scores)} files",
            )
            logger.info(f"Fused signals for {len(fused_scores)} files")

            # Layer 5: Recommendations
            rec_task = progress.add_task(
                "[cyan]Layer 5: Generating recommendations...", total=100
            )

            engine = RecommendationEngine(
                files, primitives, normalized, anomalies, fused_scores
            )
            reports = engine.generate()

            progress.update(
                rec_task,
                completed=100,
                description=f"[green]Layer 5: Generated {len(reports)} actionable reports",
            )
            logger.info(f"Generated {len(reports)} reports")

        console.print()

        # Show cache stats if enabled
        if self.cache:
            stats = self.cache.stats()
            logger.debug(f"Cache stats: {stats}")

        return reports

    def _get_scanner(self):
        """
        Get appropriate scanner based on language.

        Returns:
            Language-specific scanner instance

        Raises:
            UnsupportedLanguageError: If no scanner available for detected language
        """
        if self.language == "go":
            logger.debug("Using Go scanner")
            self._detected_language = "go"
            return GoScanner(str(self.root_dir), settings=self.settings)
        elif self.language in ["typescript", "react", "javascript"]:
            logger.debug(f"Using TypeScript scanner for {self.language}")
            self._detected_language = self.language
            return TypeScriptScanner(str(self.root_dir), settings=self.settings)
        elif self.language == "python":
            logger.debug("Using Python scanner")
            self._detected_language = "python"
            return PythonScanner(str(self.root_dir), settings=self.settings)
        else:
            # Auto-detect
            logger.debug("Auto-detecting language...")

            skip_dirs = {"venv", ".venv", "node_modules", "__pycache__", ".git", "dist", "build"}

            def _has_ext(ext: str) -> bool:
                for p in self.root_dir.rglob(f"*{ext}"):
                    if not any(part in skip_dirs for part in p.parts):
                        return True
                return False

            has_go = _has_ext(".go")
            has_ts = _has_ext(".ts") or _has_ext(".tsx")
            has_py = _has_ext(".py")

            if has_go:
                logger.info("Auto-detected: Go codebase")
                console.print("[yellow]Auto-detected: Go codebase[/yellow]\n")
                self._detected_language = "go"
                return GoScanner(str(self.root_dir), settings=self.settings)
            elif has_ts:
                logger.info("Auto-detected: TypeScript/React codebase")
                console.print(
                    "[yellow]Auto-detected: TypeScript/React codebase[/yellow]\n"
                )
                self._detected_language = "typescript"
                return TypeScriptScanner(str(self.root_dir), settings=self.settings)
            elif has_py:
                logger.info("Auto-detected: Python codebase")
                console.print("[yellow]Auto-detected: Python codebase[/yellow]\n")
                self._detected_language = "python"
                return PythonScanner(str(self.root_dir), settings=self.settings)
            else:
                logger.warning("Could not auto-detect language, defaulting to Python")
                console.print(
                    "[yellow]Could not auto-detect language. Defaulting to Python.[/yellow]\n"
                )
                self._detected_language = "python"
                return PythonScanner(str(self.root_dir), settings=self.settings)

    def print_summary(self, reports: List[AnomalyReport], top_n: int = 10):
        """
        Print a compact summary dashboard using Rich Panel and Table.

        Args:
            reports: List of anomaly reports
            top_n: Number of top files to display in summary
        """
        num_anomalies = len(reports)
        pct = (num_anomalies / self._total_files_scanned * 100) if self._total_files_scanned > 0 else 0
        avg_confidence = (
            sum(r.confidence for r in reports) / num_anomalies
            if num_anomalies > 0
            else 0.0
        )

        summary_text = (
            f"Scanned [bold]{self._total_files_scanned}[/bold] files "
            f"([cyan]{self._detected_language}[/cyan])  |  "
            f"[yellow]{num_anomalies}[/yellow] anomalies "
            f"([yellow]{pct:.0f}%[/yellow])  |  "
            f"Avg confidence: [blue]{avg_confidence:.2f}[/blue]"
        )
        console.print(Panel(summary_text, title="[bold cyan]Summary[/bold cyan]", expand=False))
        console.print()

        if not reports:
            return

        table = Table(title=f"Top {min(top_n, len(reports))} Files Requiring Attention")
        table.add_column("#", style="dim", width=4)
        table.add_column("File", style="yellow", no_wrap=True, max_width=40)
        table.add_column("Score", style="red", justify="right")
        table.add_column("Confidence", style="blue", justify="right")
        table.add_column("Primary Issue", style="white")

        for i, report in enumerate(reports[:top_n], 1):
            primary = report.anomaly_flags[0] if report.anomaly_flags else "-"
            table.add_row(
                str(i),
                report.file,
                f"{report.overall_score:.3f}",
                f"{report.confidence:.2f}",
                primary,
            )

        console.print(table)
        console.print()

    def print_report(self, reports: List[AnomalyReport], top_n: int = 10):
        """
        Print human-readable analysis report with rich formatting.

        Args:
            reports: List of anomaly reports
            top_n: Number of top files to display
        """
        console.print("[bold cyan]=" * 40)
        console.print(
            f"[bold cyan]TOP {min(top_n, len(reports))} FILES REQUIRING ATTENTION"
        )
        console.print("[bold cyan]=" * 40)
        console.print()

        for i, report in enumerate(reports[:top_n], 1):
            console.print(f"[bold yellow]{i}. {report.file}[/bold yellow]")
            console.print(
                f"   Overall Score: [red]{report.overall_score:.3f}[/red] "
                f"(Confidence: [blue]{report.confidence:.2f}[/blue])"
            )
            console.print()

            console.print("   [dim]Raw Primitives:[/dim]")
            console.print(
                f"     - Structural Entropy:  {report.primitives.structural_entropy:.3f}"
            )
            console.print(
                f"     - Network Centrality:  {report.primitives.network_centrality:.3f}"
            )
            console.print(
                f"     - Churn Volatility:    {report.primitives.churn_volatility:.3f}"
            )
            console.print(
                f"     - Semantic Coherence:  {report.primitives.semantic_coherence:.3f}"
            )
            console.print(
                f"     - Cognitive Load:      {report.primitives.cognitive_load:.3f}"
            )
            console.print()

            console.print("   [dim]Normalized (Z-Scores):[/dim]")
            console.print(
                f"     - Structural Entropy:  {report.normalized_primitives.structural_entropy:+.2f}s"
            )
            console.print(
                f"     - Network Centrality:  {report.normalized_primitives.network_centrality:+.2f}s"
            )
            console.print(
                f"     - Churn Volatility:    {report.normalized_primitives.churn_volatility:+.2f}s"
            )
            console.print(
                f"     - Semantic Coherence:  {report.normalized_primitives.semantic_coherence:+.2f}s"
            )
            console.print(
                f"     - Cognitive Load:      {report.normalized_primitives.cognitive_load:+.2f}s"
            )
            console.print()

            if report.root_causes:
                console.print("   [dim]Root Causes:[/dim]")
                for cause in report.root_causes:
                    console.print(f"     [red]![/red] {cause}")
                console.print()

            if report.recommendations:
                console.print("   [dim]Recommendations:[/dim]")
                for rec in report.recommendations:
                    console.print(f"     [green]->[/green] {rec}")
                console.print()

            console.print("[dim]" + "-" * 80 + "[/dim]")
            console.print()

        logger.info(f"Printed report for top {min(top_n, len(reports))} files")

    def print_explain(self, reports: List[AnomalyReport], pattern: str):
        """
        Print a deep-dive explanation for file(s) matching a pattern.

        Args:
            reports: List of anomaly reports
            pattern: File name or pattern to match
        """
        matching = [r for r in reports if pattern in r.file]

        if not matching:
            console.print(f"[yellow]No files matching '{pattern}' found in analysis results.[/yellow]")
            return

        for report in matching:
            console.print(Panel(
                f"[bold]{report.file}[/bold]",
                title="[bold cyan]Deep Dive[/bold cyan]",
                expand=False,
            ))
            console.print()

            console.print("[bold]Raw Primitives:[/bold]")
            console.print(f"  Structural Entropy:  {report.primitives.structural_entropy:.4f}")
            console.print(f"  Network Centrality:  {report.primitives.network_centrality:.4f}")
            console.print(f"  Churn Volatility:    {report.primitives.churn_volatility:.4f}")
            console.print(f"  Semantic Coherence:  {report.primitives.semantic_coherence:.4f}")
            console.print(f"  Cognitive Load:      {report.primitives.cognitive_load:.4f}")
            console.print()

            threshold = self.settings.z_score_threshold
            console.print(f"[bold]Normalized Z-Scores[/bold] (threshold: {threshold:.1f}):")
            for name, val in [
                ("Structural Entropy", report.normalized_primitives.structural_entropy),
                ("Network Centrality", report.normalized_primitives.network_centrality),
                ("Churn Volatility", report.normalized_primitives.churn_volatility),
                ("Semantic Coherence", report.normalized_primitives.semantic_coherence),
                ("Cognitive Load", report.normalized_primitives.cognitive_load),
            ]:
                marker = " [red]<< ANOMALY[/red]" if abs(val) > threshold else ""
                console.print(f"  {name:22s}  {val:+.3f}s{marker}")
            console.print()

            console.print(f"[bold]Overall Score:[/bold] [red]{report.overall_score:.4f}[/red]")
            console.print(f"[bold]Confidence:[/bold]    [blue]{report.confidence:.4f}[/blue]")
            console.print()

            if report.anomaly_flags:
                console.print("[bold]Anomaly Flags:[/bold]")
                for flag in report.anomaly_flags:
                    console.print(f"  [red]-[/red] {flag}")
                console.print()

            if report.root_causes:
                console.print("[bold]Root Causes:[/bold]")
                for cause in report.root_causes:
                    console.print(f"  [red]![/red] {cause}")
                console.print()

            if report.recommendations:
                console.print("[bold]Recommendations:[/bold]")
                for rec in report.recommendations:
                    console.print(f"  [green]->[/green] {rec}")
                console.print()

            console.print("[dim]" + "-" * 80 + "[/dim]")
            console.print()

    def format_json(self, reports: List[AnomalyReport]) -> str:
        """Format reports as JSON string."""
        data = [asdict(r) for r in reports]
        return json.dumps(data, indent=2)

    def format_csv(self, reports: List[AnomalyReport]) -> str:
        """Format reports as CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "file", "overall_score", "confidence",
            "structural_entropy", "network_centrality",
            "churn_volatility", "semantic_coherence", "cognitive_load",
            "anomaly_flags",
        ])
        for r in reports:
            writer.writerow([
                r.file, f"{r.overall_score:.4f}", f"{r.confidence:.4f}",
                f"{r.primitives.structural_entropy:.4f}",
                f"{r.primitives.network_centrality:.4f}",
                f"{r.primitives.churn_volatility:.4f}",
                f"{r.primitives.semantic_coherence:.4f}",
                f"{r.primitives.cognitive_load:.4f}",
                ";".join(r.anomaly_flags),
            ])
        return output.getvalue()

    def format_quiet(self, reports: List[AnomalyReport]) -> str:
        """Format reports as one file path per line."""
        return "\n".join(r.file for r in reports)

    def export_json(
        self, reports: List[AnomalyReport], filename: str = "analysis_report.json"
    ):
        """
        Export analysis to JSON file.

        Args:
            reports: List of anomaly reports
            filename: Output filename
        """
        output_path = Path(filename)
        with open(output_path, "w") as f:
            f.write(self.format_json(reports))

        console.print(f"[green]Exported detailed report to {output_path}[/green]")
        logger.info(f"Exported {len(reports)} reports to {output_path}")
