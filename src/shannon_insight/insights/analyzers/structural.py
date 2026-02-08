"""StructuralAnalyzer — wraps existing AnalysisEngine."""

from ...graph.engine import AnalysisEngine
from ...logging_config import get_logger
from ..store_v2 import AnalysisStore

logger = get_logger(__name__)


class StructuralAnalyzer:
    name = "structural"
    requires: set[str] = {"files"}
    provides: set[str] = {"structural"}

    def analyze(self, store: AnalysisStore) -> None:
        if not store.file_metrics:
            return

        engine = AnalysisEngine(store.file_metrics, root_dir=store.root_dir)
        result = engine.run()
        store.structural.set(result, produced_by=self.name)
        logger.debug(f"Structural analysis: {result.total_files} files, {result.total_edges} edges")
