"""InsightKernel — orchestrates analyzers and finders on the blackboard."""

from pathlib import Path
from typing import List, Optional

from ..config import AnalysisSettings, default_settings
from ..core.scanner_factory import ScannerFactory
from ..logging_config import get_logger
from .models import InsightResult, StoreSummary
from .store import AnalysisStore
from .analyzers import get_default_analyzers
from .finders import get_default_finders

logger = get_logger(__name__)


class InsightKernel:
    """Orchestrate analysis: scan -> analyze -> find -> rank."""

    def __init__(
        self,
        root_dir: str,
        language: str = "auto",
        settings: Optional[AnalysisSettings] = None,
    ):
        self.root_dir = str(Path(root_dir).resolve())
        self.language = language
        self.settings = settings or default_settings
        self._analyzers = get_default_analyzers()
        self._finders = get_default_finders()

    def run(self, max_findings: int = 10) -> InsightResult:
        """Execute the full insight pipeline."""
        store = AnalysisStore(root_dir=self.root_dir)

        # Phase 1: Scan files
        store.file_metrics = self._scan()
        logger.info(f"Scanned {len(store.file_metrics)} files")

        if not store.file_metrics:
            return InsightResult(
                findings=[],
                store_summary=StoreSummary(),
            )

        # Phase 2: Run analyzers (topologically sorted by requires/provides)
        for analyzer in self._resolve_order():
            if analyzer.requires.issubset(store.available):
                try:
                    analyzer.analyze(store)
                    logger.debug(f"Analyzer {analyzer.name} completed")
                except Exception as e:
                    logger.warning(f"Analyzer {analyzer.name} failed: {e}")

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

        return InsightResult(
            findings=capped,
            store_summary=self._summarize(store),
        )

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

        if store.structural:
            summary.total_modules = store.structural.total_modules

        if store.git_history:
            summary.commits_analyzed = store.git_history.total_commits
            summary.git_available = True

        if store.spectral:
            summary.fiedler_value = store.spectral.fiedler_value

        return summary
