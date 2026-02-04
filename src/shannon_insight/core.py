"""Main pipeline orchestrator for Shannon Insight.

Key design decision: when multiple languages are detected, the pipeline
(extraction → normalization → detection → fusion → recommendations) runs
**per language** so that z-scores, TF-IDF coherence, and dependency graphs
are computed within each language's population.  Reports are then merged
and sorted by score.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TextColumn,
)

from .models import AnomalyReport, AnalysisContext, FileMetrics
from .analyzers import GoScanner, TypeScriptScanner, PythonScanner
from .analyzers.java_analyzer import JavaScanner
from .analyzers.rust_analyzer import RustScanner
from .analyzers.c_analyzer import CScanner
from .analyzers.ruby_analyzer import RubyScanner
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
console = Console(stderr=True)

# Minimum files needed per language for statistical analysis
_MIN_FILES_FOR_ANALYSIS = 3


class CodebaseAnalyzer:
    """Main pipeline orchestrator — pure analysis engine.

    Output formatting is handled by the ``formatters`` package.
    """

    SUPPORTED_LANGUAGES = {
        "auto", "go", "typescript", "react", "javascript",
        "python", "java", "rust", "c", "cpp", "ruby",
    }

    @staticmethod
    def _severity_label(score: float) -> str:
        if score >= 3.0:
            return "[red bold]critical[/red bold]"
        elif score >= 2.0:
            return "[red]high[/red]"
        elif score >= 1.0:
            return "[yellow]moderate[/yellow]"
        else:
            return "[green]low[/green]"

    def __init__(
        self,
        root_dir: "Path | str",
        language: str = "auto",
        settings: Optional[AnalysisSettings] = None,
    ):
        self.root_dir = validate_root_directory(Path(root_dir))
        logger.info(f"Analyzing codebase at: {self.root_dir}")

        if language not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(language, list(self.SUPPORTED_LANGUAGES))
        self.language = language

        self.settings = settings or default_settings
        logger.debug(
            f"Settings: cache={self.settings.enable_cache}, "
            f"workers={self.settings.parallel_workers}, "
            f"threshold={self.settings.z_score_threshold}"
        )

        self.cache = None
        if self.settings.enable_cache:
            self.cache = AnalysisCache(
                cache_dir=self.settings.cache_dir,
                ttl_hours=self.settings.cache_ttl_hours,
                enabled=True,
            )
            logger.debug(f"Cache enabled at {self.settings.cache_dir}")

        self.config_hash = compute_config_hash(self.settings.model_dump())

        self._total_files_scanned = 0
        self._detected_languages: List[str] = [language] if language != "auto" else []

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def analyze(self) -> Tuple[List[AnomalyReport], AnalysisContext]:
        """Run full analysis pipeline with progress tracking.

        When multiple languages are present, layers 2-5 run **per language**
        so that z-scores and TF-IDF are computed within each language's
        population (avoiding cross-language statistical contamination).
        Reports are merged and sorted at the end.
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
            # Layer 1: Scan all languages
            scan_task = progress.add_task(
                "[cyan]Layer 1: Scanning codebase...", total=None
            )

            scanners = self._get_scanners()
            lang_file_groups: List[Tuple[str, List[FileMetrics]]] = []
            total_files = 0

            for scanner, lang in scanners:
                lang_files = scanner.scan()
                if lang_files:
                    lang_file_groups.append((lang, lang_files))
                    total_files += len(lang_files)

            if total_files == 0:
                logger.warning("No files found to analyze")
                raise InsufficientDataError(
                    "No source files found in the specified directory",
                    minimum_required=1,
                )

            self._total_files_scanned = total_files

            parts = [f"{len(files)} {lang.capitalize()}" for lang, files in lang_file_groups]
            found_desc = " + ".join(parts) if parts else str(total_files)

            progress.update(
                scan_task,
                completed=True,
                description=f"[green]Layer 1: Found {found_desc} files ({total_files} total)",
            )
            logger.info(f"Scanned {total_files} files: {found_desc}")

            # Layers 2-5: per-language pipeline
            analysis_task = progress.add_task(
                "[cyan]Layers 2-5: Analyzing per language...", total=100
            )

            all_reports: List[AnomalyReport] = []
            total_anomalies = 0
            langs_analyzed = 0

            for lang, files in lang_file_groups:
                if len(files) < _MIN_FILES_FOR_ANALYSIS:
                    logger.warning(
                        f"Skipping {lang}: only {len(files)} files "
                        f"(need {_MIN_FILES_FOR_ANALYSIS} for statistics)"
                    )
                    continue

                lang_reports = self._run_pipeline(files)
                all_reports.extend(lang_reports)
                total_anomalies += len(lang_reports)
                langs_analyzed += 1

            # Sort all reports by score descending
            all_reports.sort(key=lambda r: r.overall_score, reverse=True)

            progress.update(
                analysis_task,
                completed=100,
                description=(
                    f"[green]Layers 2-5: {total_anomalies} anomalies "
                    f"across {langs_analyzed} language(s)"
                ),
            )

        console.print()

        if self.cache:
            stats = self.cache.stats()
            logger.debug(f"Cache stats: {stats}")

        context = AnalysisContext(
            total_files_scanned=self._total_files_scanned,
            detected_languages=self._detected_languages,
            settings=self.settings,
        )

        return all_reports, context

    # ------------------------------------------------------------------
    # Per-language pipeline (layers 2-5)
    # ------------------------------------------------------------------

    def _run_pipeline(self, files: List[FileMetrics]) -> List[AnomalyReport]:
        """Run layers 2-5 on a single-language file group."""
        # Layer 2: Primitive Extraction
        extractor = PrimitiveExtractor(
            files, cache=self.cache, config_hash=self.config_hash,
            root_dir=str(self.root_dir),
        )
        primitives = extractor.extract_all()
        logger.info(f"Extracted primitives for {len(primitives)} files")

        # Layer 3: Normalization & Anomaly Detection
        detector = AnomalyDetector(
            primitives, threshold=self.settings.z_score_threshold
        )
        normalized = detector.normalize()
        anomalies = detector.detect_anomalies(normalized)
        logger.info(f"Detected {len(anomalies)} anomalies")

        # Layer 4: Signal Fusion
        fusion = SignalFusion(
            primitives, normalized, weights=self.settings.fusion_weights
        )
        fused_scores = fusion.fuse()
        logger.info(f"Fused signals for {len(fused_scores)} files")

        # Layer 5: Recommendations
        engine = RecommendationEngine(
            files, primitives, normalized, anomalies, fused_scores,
            root_dir=str(self.root_dir),
        )
        reports = engine.generate()
        logger.info(f"Generated {len(reports)} reports")

        return reports

    # ------------------------------------------------------------------
    # Scanner selection
    # ------------------------------------------------------------------

    def _get_scanners(self) -> List[Tuple]:
        """Get appropriate scanner(s) based on language setting."""
        mk = lambda cls, lang: (cls(str(self.root_dir), settings=self.settings), lang)

        explicit_map = {
            "go":         lambda: [mk(GoScanner, "go")],
            "typescript": lambda: [mk(TypeScriptScanner, "typescript")],
            "react":      lambda: [mk(TypeScriptScanner, "react")],
            "javascript": lambda: [mk(TypeScriptScanner, "javascript")],
            "python":     lambda: [mk(PythonScanner, "python")],
            "java":       lambda: [mk(JavaScanner, "java")],
            "rust":       lambda: [mk(RustScanner, "rust")],
            "c":          lambda: [mk(CScanner, "c")],
            "cpp":        lambda: [mk(CScanner, "cpp")],
            "ruby":       lambda: [mk(RubyScanner, "ruby")],
        }

        if self.language in explicit_map:
            self._detected_languages = [self.language]
            return explicit_map[self.language]()

        # Auto-detect all languages present
        logger.debug("Auto-detecting languages...")

        skip_dirs = {"venv", ".venv", "node_modules", "__pycache__",
                     ".git", "dist", "build", "target"}

        def _has_ext(ext: str) -> bool:
            for p in self.root_dir.rglob(f"*{ext}"):
                if not any(part in skip_dirs for part in p.parts):
                    return True
            return False

        candidates = [
            (_has_ext(".go"),                                "go",         GoScanner),
            (_has_ext(".ts") or _has_ext(".tsx"),            "typescript", TypeScriptScanner),
            (_has_ext(".py"),                                "python",     PythonScanner),
            (_has_ext(".java"),                              "java",       JavaScanner),
            (_has_ext(".rs"),                                "rust",       RustScanner),
            (_has_ext(".c") or _has_ext(".cpp") or
             _has_ext(".cc") or _has_ext(".h"),              "c/c++",      CScanner),
            (_has_ext(".rb"),                                "ruby",       RubyScanner),
        ]

        scanners = []
        for detected, lang, cls in candidates:
            if detected:
                logger.info(f"Auto-detected: {lang} files")
                scanners.append(mk(cls, lang))

        if scanners:
            detected_names = [lang for _, lang in scanners]
            self._detected_languages = detected_names
            console.print(f"[yellow]Auto-detected: {', '.join(detected_names)}[/yellow]\n")
        else:
            logger.warning("Could not auto-detect language, defaulting to Python")
            console.print(
                "[yellow]Could not auto-detect language. Defaulting to Python.[/yellow]\n"
            )
            self._detected_languages = ["python"]
            scanners.append(mk(PythonScanner, "python"))

        return scanners
