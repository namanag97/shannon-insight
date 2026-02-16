"""InsightKernel — orchestrates analyzers and finders on the blackboard."""

from __future__ import annotations

import concurrent.futures
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

from ..session import AnalysisSession
from ..logging_config import get_logger
from ..persistence.models import TensorSnapshot
from ..scanning.factory import ScannerFactory
from ..scanning.syntax_extractor import SyntaxExtractor
from .analyzers import get_default_analyzers, get_wave2_analyzers
from .finders import get_default_finders, get_persistence_finders
from .kernel_toposort import resolve_analyzer_order
from .models import InsightResult, StoreSummary
from .store_v2 import AnalysisStore
from .validation import (
    PhaseValidationError,
    validate_after_scanning,
    validate_after_structural,
    validate_signal_field,
)

if TYPE_CHECKING:
    from ..debug_export import DebugExporter

ProgressCallback = Optional[Callable[[str], None]]

logger = get_logger(__name__)

# Default timeout for individual analyzers (5 minutes)
_ANALYZER_TIMEOUT_SECONDS = 300


class AnalyzerTimeoutError(Exception):
    """Raised when an analyzer exceeds its time limit."""

    pass


def _run_with_timeout(func: Callable, timeout: float, name: str) -> None:
    """Run a function with a timeout. Raises AnalyzerTimeoutError if exceeded."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise AnalyzerTimeoutError(f"Analyzer '{name}' exceeded {timeout}s timeout")


class InsightKernel:
    """Orchestrate analysis: scan -> analyze -> find -> rank."""

    def __init__(
        self,
        root_dir: str,
        language: str = "auto",
        settings: AnalysisSettings | None = None,
        enable_persistence_finders: bool = False,
        debug_export_dir: str | Path | None = None,
    ):
        self.root_dir = str(Path(root_dir).resolve())
        self.language = language
        self.session.config = settings or default_settings
        self._analyzers = get_default_analyzers()
        self._wave2_analyzers = get_wave2_analyzers()
        self._finders = get_default_finders()
        self._persistence_finders = get_persistence_finders() if enable_persistence_finders else []
        self._debug_exporter: DebugExporter | None = None
        if debug_export_dir:
            from ..debug_export import DebugExporter

            self._debug_exporter = DebugExporter(debug_export_dir)

    def run(
        self,
        max_findings: int = 10,
        on_progress: ProgressCallback = None,
    ) -> tuple[InsightResult, TensorSnapshot]:
        """Execute the full insight pipeline and capture a snapshot.

        Parameters
        ----------
        max_findings : int
            Maximum findings to return (default 10).
        on_progress : callable, optional
            If provided, called with a status message string at each phase
            transition. Useful for driving a CLI spinner.

        Returns
        -------
        Tuple[InsightResult, TensorSnapshot]
            The insight result and a serialisable v2 snapshot of this run.
        """
        from ..persistence.capture import capture_tensor_snapshot

        def _progress(msg: str) -> None:
            if on_progress is not None:
                on_progress(msg)

        store = AnalysisStore(root_dir=self.root_dir)

        # Phase 1: Scan files
        _progress("Scanning files...")
        store.file_metrics = self._scan()
        logger.info(f"Scanned {len(store.file_metrics)} files")

        # Sync scanned files to FactStore as entities with basic signals
        store._sync_entities()

        if self._debug_exporter:
            self._debug_exporter.export_scanning(store)

        if not store.file_metrics:
            empty_result = InsightResult(
                findings=[],
                store_summary=StoreSummary(),
            )
            empty_snapshot = capture_tensor_snapshot(store, empty_result, self.session)
            return empty_result, empty_snapshot

        _progress(f"Parsing {len(store.file_metrics)} files...")

        # Phase 1.5: Extract file_syntax for deep parsing
        self._extract_syntax(store)

        if self._debug_exporter:
            self._debug_exporter.export_syntax(store)

        # Phase validation: after scanning
        if self.session.config.enable_validation:
            try:
                validate_after_scanning(store)
            except PhaseValidationError as e:
                logger.warning(f"Scanning validation failed: {e}")

        # Phase 2a: Run Wave 1 analyzers (topologically sorted by requires/provides)
        _progress("Analyzing dependencies...")
        for analyzer in self._resolve_order():
            if analyzer.requires.issubset(store.available):
                try:
                    _progress(f"Running {analyzer.name}...")
                    # Run with timeout to prevent hangs
                    _run_with_timeout(
                        lambda a=analyzer: a.analyze(store),
                        _ANALYZER_TIMEOUT_SECONDS,
                        analyzer.name,
                    )
                    logger.debug(f"Analyzer {analyzer.name} completed")

                    # Debug export after each analyzer
                    if self._debug_exporter:
                        self._export_after_analyzer(analyzer.name, store)

                except AnalyzerTimeoutError as e:
                    logger.warning(str(e))
                except Exception as e:
                    logger.warning(f"Analyzer {analyzer.name} failed: {e}")

        # Phase validation: after structural analysis
        if self.session.config.enable_validation:
            try:
                validate_after_structural(store)
            except PhaseValidationError as e:
                logger.warning(f"Structural validation failed: {e}")

        # Clear content cache to free memory (wave 2 doesn't need file content)
        store.clear_content_cache()

        # Phase 2b: Run Wave 2 analyzers (signal fusion, after all Wave 1)
        _progress("Computing signals...")
        for analyzer in self._wave2_analyzers:
            try:
                _progress(f"Running {analyzer.name}...")
                # Run with timeout to prevent hangs
                _run_with_timeout(
                    lambda a=analyzer: a.analyze(store),
                    _ANALYZER_TIMEOUT_SECONDS,
                    analyzer.name,
                )
                logger.debug(f"Wave 2 analyzer {analyzer.name} completed")

                if self._debug_exporter and "fusion" in analyzer.name.lower():
                    self._debug_exporter.export_fusion(store)

            except AnalyzerTimeoutError as e:
                logger.warning(str(e))
            except Exception as e:
                logger.warning(f"Wave 2 analyzer {analyzer.name} failed: {e}")

        # Phase validation: after signal fusion
        if self.session.config.enable_validation:
            try:
                validate_signal_field(store)
            except PhaseValidationError as e:
                logger.warning(f"Signal field validation failed: {e}")

        # Phase 3: Run patterns against FactStore
        _progress("Detecting issues...")
        from shannon_insight.insights.finders.executor import execute_patterns
        from shannon_insight.insights.finders.registry import ALL_PATTERNS

        # Use tier from session (already computed)
        tier = self.session.tier
        logger.debug(f"Using tier: {tier.value} for {len(store.file_metrics)} files")

        # Execute v2 patterns
        v2_findings = execute_patterns(
            store=store.fact_store,
            patterns=ALL_PATTERNS,
            tier=tier,
            max_findings=max_findings * 2,  # Get extra for backward compat filters
        )

        # Convert v2 findings to v1 format for backward compatibility
        from shannon_insight.insights.models import Evidence
        from shannon_insight.insights.models import Finding as V1Finding

        findings = []
        for v2_f in v2_findings:
            # Extract file paths from target
            if isinstance(v2_f.target, tuple):
                files = [v2_f.target[0].key, v2_f.target[1].key]
            else:
                files = [v2_f.target.key]

            # Convert evidence dict to Evidence objects
            # Handle both numeric and string values
            evidence = []
            for k, v in v2_f.evidence.items():
                # Convert to float if possible, otherwise use 0.0 as placeholder
                try:
                    numeric_value = float(v) if not isinstance(v, str) else 0.0
                except (ValueError, TypeError):
                    numeric_value = 0.0

                # Generate descriptive text (min 6 chars for test compatibility)
                if isinstance(v, bool):
                    description = f"{k}={v}"
                elif isinstance(v, (int, float)):
                    description = f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                else:
                    description = str(v) if len(str(v)) > 5 else f"{k}={v}"

                evidence.append(
                    Evidence(signal=k, value=numeric_value, percentile=0.0, description=description)
                )

            # Convert v2 Finding to v1 Finding
            v1_f = V1Finding(
                finding_type=v2_f.pattern,
                severity=v2_f.severity,  # v2 uses 0-1, v1 also uses 0-1
                title=v2_f.description,
                files=files,
                evidence=evidence,
                suggestion=v2_f.remediation,
                confidence=v2_f.confidence,
            )
            findings.append(v1_f)

        # Fallback: Run old v1 finders for backward compatibility
        for finder in self._finders:
            if finder.requires.issubset(store.available):
                try:
                    findings.extend(finder.find(store))
                except Exception as e:
                    logger.warning(f"V1 finder {finder.name} failed: {e}")

        # Phase 3b: Run persistence finders (need DB connection)
        if self._persistence_finders:
            _progress("Checking history...")
            self._run_persistence_finders(findings)

        # Phase 3c: Run diagnostics
        from .diagnostics import run_diagnostics

        diagnostic_report = run_diagnostics(store, findings)
        if diagnostic_report.has_issues:
            logger.info(f"Diagnostics: {diagnostic_report.summary()}")
            for issue in diagnostic_report.issues:
                logger.debug(f"  [{issue.severity}] {issue.message}")

        # Phase 4: Deduplicate, rank, and cap
        _progress("Ranking findings...")
        from .ranking import deduplicate_findings

        findings = deduplicate_findings(findings)
        findings.sort(key=lambda f: f.severity, reverse=True)
        capped = findings[:max_findings]

        result = InsightResult(
            findings=capped,
            store_summary=self._summarize(store),
        )
        result.diagnostic_report = diagnostic_report

        # Debug export: findings and index
        if self._debug_exporter:
            self._debug_exporter.export_findings(capped)
            self._debug_exporter.write_index(store, capped)
            logger.info(f"Debug export written to {self._debug_exporter.output_dir}")

        # Phase 5: Capture v2 snapshot (includes module signals, delta_h, architecture)
        _progress("Capturing snapshot...")
        snapshot = capture_tensor_snapshot(store, result, self.session.config)

        return result, snapshot

    def _scan(self) -> list:
        """Scan files using ScannerFactory."""
        # Use detected languages from environment, fallback to Python
        languages = list(self.session.env.detected_languages) if self.session.env.detected_languages else ["python"]
        language = languages[0] if len(languages) == 1 else "auto"

        factory = ScannerFactory(Path(self.root_dir), self.session.config)
        scanners, detected = factory.create(language)

        all_files = []
        for scanner, lang in scanners:
            if lang == "universal":
                continue
            all_files.extend(scanner.scan())

        return all_files

    def _extract_syntax(self, store: AnalysisStore) -> None:
        """Extract FileSyntax for all scanned files.

        Populates store.file_syntax slot with dict[path, FileSyntax].
        Also populates store._content_cache for later reuse (avoids re-reading files).
        Uses tree-sitter if available, falls back to regex.
        """
        root = Path(self.root_dir)
        extractor = SyntaxExtractor()

        # Get file paths from file_metrics
        file_paths = [root / fm.path for fm in store.file_metrics]

        # Extract syntax and cache content for later reuse (e.g., compression ratio)
        file_syntax = extractor.extract_all(file_paths, root, content_cache=store._content_cache)

        # Store result
        store.file_syntax.set(file_syntax, produced_by="kernel")
        logger.debug(
            f"Extracted syntax for {len(file_syntax)} files "
            f"(tree-sitter: {extractor.treesitter_count}, "
            f"fallback: {extractor.fallback_count}, "
            f"cached: {len(store._content_cache)})"
        )

    def _resolve_order(self) -> list:
        """Topologically sort analyzers by requires/provides.

        Uses graphlib.TopologicalSorter (via kernel_toposort) to order
        analyzers. Detects cycles and slot collisions at startup time
        instead of silently appending unresolvable analyzers.
        """
        return resolve_analyzer_order(self._analyzers)

    def _run_persistence_finders(self, findings: list) -> None:
        """Run persistence-based finders with a temporary DB connection."""
        from ..persistence import HistoryDB

        try:
            with HistoryDB(self.root_dir) as db:
                for finder in self._persistence_finders:
                    try:
                        findings.extend(finder.find(store=None, db_conn=db.conn))
                    except Exception as e:
                        logger.warning(f"Persistence finder {finder.name} failed: {e}")
        except Exception as e:
            logger.debug(f"No history DB available for persistence finders: {e}")

    def _export_after_analyzer(self, analyzer_name: str, store: AnalysisStore) -> None:
        """Export debug data after specific analyzers run."""
        if not self._debug_exporter:
            return

        name_lower = analyzer_name.lower()
        if "structural" in name_lower:
            self._debug_exporter.export_structural(store)
        elif "temporal" in name_lower:
            self._debug_exporter.export_temporal(store)
        elif "spectral" in name_lower:
            self._debug_exporter.export_spectral(store)
        elif "semantic" in name_lower:
            self._debug_exporter.export_semantic(store)
        elif "architecture" in name_lower:
            self._debug_exporter.export_architecture(store)

    def _summarize(self, store: AnalysisStore) -> StoreSummary:
        """Build summary from store state."""
        summary = StoreSummary(
            total_files=len(store.file_metrics),
            signals_available=sorted(store.available),
        )

        if store.structural.available:
            summary.total_modules = store.structural.value.total_modules

        if store.git_history.available:
            summary.commits_analyzed = store.git_history.value.total_commits
            summary.git_available = True

        if store.spectral.available:
            summary.fiedler_value = store.spectral.value.fiedler_value

        return summary
