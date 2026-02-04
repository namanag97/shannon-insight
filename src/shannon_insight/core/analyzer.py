"""Main entry point — composes scanner_factory + pipeline + progress."""

from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console

from ..models import AnomalyReport, AnalysisContext, FileMetrics
from ..analyzers import LANGUAGES
from ..config import AnalysisSettings, default_settings
from ..cache import AnalysisCache, compute_config_hash
from ..logging_config import get_logger
from ..security import validate_root_directory
from ..exceptions import UnsupportedLanguageError, InsufficientDataError
from .scanner_factory import ScannerFactory
from .pipeline import AnalysisPipeline
from .progress import ProgressReporter

logger = get_logger(__name__)
console = Console(stderr=True)

_MIN_FILES_FOR_ANALYSIS = 3


class CodebaseAnalyzer:
    """Main pipeline orchestrator — pure analysis engine."""

    SUPPORTED_LANGUAGES = set(LANGUAGES.keys()) | {"auto", "react", "javascript", "cpp"}

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

    def analyze(self) -> Tuple[List[AnomalyReport], AnalysisContext]:
        """Run full analysis pipeline with progress tracking."""
        console.print()
        console.print("[bold cyan]=" * 40)
        console.print(
            "[bold cyan]SHANNON INSIGHT - Multi-Signal Codebase Quality Analyzer"
        )
        console.print("[bold cyan]=" * 40)
        console.print()

        reporter = ProgressReporter(console)
        all_reports = reporter.run(lambda progress: self._run_with_progress(progress))

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

    def _run_with_progress(self, progress) -> List[AnomalyReport]:
        # Layer 1: Scan
        scan_task = progress.add_task("[cyan]Layer 1: Scanning codebase...", total=None)

        factory = ScannerFactory(self.root_dir, self.settings)
        scanners, detected = factory.create(self.language)
        if self.language == "auto":
            self._detected_languages = detected
            console.print(f"[yellow]Auto-detected: {', '.join(detected)}[/yellow]\n")

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
            scan_task, completed=True,
            description=f"[green]Layer 1: Found {found_desc} files ({total_files} total)",
        )
        logger.info(f"Scanned {total_files} files: {found_desc}")

        # Layers 2-5: per-language pipeline
        analysis_task = progress.add_task(
            "[cyan]Layers 2-5: Analyzing per language...", total=100,
        )

        pipeline = AnalysisPipeline(
            self.settings, cache=self.cache,
            config_hash=self.config_hash, root_dir=str(self.root_dir),
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

            lang_reports = pipeline.run(files)
            all_reports.extend(lang_reports)
            total_anomalies += len(lang_reports)
            langs_analyzed += 1

        all_reports.sort(key=lambda r: r.overall_score, reverse=True)

        progress.update(
            analysis_task, completed=100,
            description=(
                f"[green]Layers 2-5: {total_anomalies} anomalies "
                f"across {langs_analyzed} language(s)"
            ),
        )

        return all_reports
