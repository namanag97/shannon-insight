"""InsightKernel — orchestrates analyzers and finders on the blackboard."""

from __future__ import annotations

from pathlib import Path

from ..config import AnalysisSettings, default_settings
from ..logging_config import get_logger
from ..persistence.models import Snapshot
from ..scanning.factory import ScannerFactory
from ..scanning.syntax_extractor import SyntaxExtractor
from .analyzers import get_default_analyzers, get_wave2_analyzers
from .finders import get_default_finders
from .models import InsightResult, StoreSummary
from .store_v2 import AnalysisStore

logger = get_logger(__name__)


class InsightKernel:
    """Orchestrate analysis: scan -> analyze -> find -> rank."""

    def __init__(
        self,
        root_dir: str,
        language: str = "auto",
        settings: AnalysisSettings | None = None,
    ):
        self.root_dir = str(Path(root_dir).resolve())
        self.language = language
        self.settings = settings or default_settings
        self._analyzers = get_default_analyzers()
        self._wave2_analyzers = get_wave2_analyzers()
        self._finders = get_default_finders()

    def run(self, max_findings: int = 10) -> tuple[InsightResult, Snapshot]:
        """Execute the full insight pipeline and capture a snapshot.

        Returns
        -------
        Tuple[InsightResult, Snapshot]
            The insight result and a serialisable snapshot of this run.
        """
        from ..persistence.capture import capture_snapshot

        store = AnalysisStore(root_dir=self.root_dir)

        # Phase 1: Scan files
        store.file_metrics = self._scan()
        logger.info(f"Scanned {len(store.file_metrics)} files")

        if not store.file_metrics:
            empty_result = InsightResult(
                findings=[],
                store_summary=StoreSummary(),
            )
            empty_snapshot = capture_snapshot(store, empty_result, self.settings)
            return empty_result, empty_snapshot

        # Phase 1.5: Extract file_syntax for deep parsing
        self._extract_syntax(store)

        # Phase 2a: Run Wave 1 analyzers (topologically sorted by requires/provides)
        for analyzer in self._resolve_order():
            if analyzer.requires.issubset(store.available):
                try:
                    analyzer.analyze(store)
                    logger.debug(f"Analyzer {analyzer.name} completed")
                except Exception as e:
                    logger.warning(f"Analyzer {analyzer.name} failed: {e}")

        # Phase 2b: Run Wave 2 analyzers (signal fusion, after all Wave 1)
        for analyzer in self._wave2_analyzers:
            try:
                analyzer.analyze(store)
                logger.debug(f"Wave 2 analyzer {analyzer.name} completed")
            except Exception as e:
                logger.warning(f"Wave 2 analyzer {analyzer.name} failed: {e}")

        # Phase 3: Run finders (skip if required signals unavailable)
        findings = []
        for finder in self._finders:
            if finder.requires.issubset(store.available):
                try:
                    findings.extend(finder.find(store))
                except Exception as e:
                    logger.warning(f"Finder {finder.name} failed: {e}")

        # Phase 4: Rank and cap
        findings.sort(key=lambda f: f.severity, reverse=True)
        capped = findings[:max_findings]

        result = InsightResult(
            findings=capped,
            store_summary=self._summarize(store),
        )

        # Phase 5: Capture snapshot
        snapshot = capture_snapshot(store, result, self.settings)

        return result, snapshot

    def _scan(self) -> list:
        """Scan files using ScannerFactory."""
        factory = ScannerFactory(Path(self.root_dir), self.settings)
        scanners, detected = factory.create(self.language)

        all_files = []
        for scanner, lang in scanners:
            if lang == "universal":
                continue
            all_files.extend(scanner.scan())

        return all_files

    def _extract_syntax(self, store: AnalysisStore) -> None:
        """Extract FileSyntax for all scanned files.

        Populates store.file_syntax slot with dict[path, FileSyntax].
        Uses tree-sitter if available, falls back to regex.
        """
        root = Path(self.root_dir)
        extractor = SyntaxExtractor()

        # Get file paths from file_metrics
        file_paths = [root / fm.path for fm in store.file_metrics]

        # Extract syntax for all files
        file_syntax = extractor.extract_all(file_paths, root)

        # Store result
        store.file_syntax.set(file_syntax, produced_by="kernel")
        logger.debug(
            f"Extracted syntax for {len(file_syntax)} files "
            f"(tree-sitter: {extractor.treesitter_count}, "
            f"fallback: {extractor.fallback_count})"
        )

    def _resolve_order(self) -> list:
        """Topologically sort analyzers by requires/provides."""
        # Simple topological sort: analyzers with fewer requirements go first
        remaining = list(self._analyzers)
        ordered = []
        provided = {"files"}  # always available

        max_iterations = len(remaining) * 2
        iteration = 0
        while remaining and iteration < max_iterations:
            iteration += 1
            for analyzer in list(remaining):
                if analyzer.requires.issubset(provided):
                    ordered.append(analyzer)
                    remaining.remove(analyzer)
                    provided.update(analyzer.provides)

        # Append any remaining (their requirements might never be met,
        # but the kernel will skip them based on store.available)
        ordered.extend(remaining)
        return ordered

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
