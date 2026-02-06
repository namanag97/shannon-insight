"""InsightKernel — orchestrates analyzers and finders on the blackboard."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from ..config import AnalysisSettings, default_settings
from ..logging_config import get_logger
from ..persistence.models import Snapshot
from ..scanning.factory import ScannerFactory
from .analyzers import get_default_analyzers
from .finders import get_default_finders
from .models import InsightResult, StoreSummary
from .store import AnalysisStore

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

    def run(self, max_findings: int = 10) -> Tuple[InsightResult, Snapshot]:
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
