"""StructuralAnalyzer — wraps existing AnalysisEngine."""

from ...graph.engine import AnalysisEngine
from ...logging_config import get_logger
from ..store import AnalysisStore

logger = get_logger(__name__)


class StructuralAnalyzer:
    name = "structural"
    requires: set[str] = {"files"}
    provides: set[str] = {"structural"}

    def analyze(self, store: AnalysisStore) -> None:
        if not store.file_metrics:
            return

        engine = AnalysisEngine(store.file_metrics, root_dir=store.root_dir)
        store.structural = engine.run()
        logger.debug(
            f"Structural analysis: {store.structural.total_files} files, "
            f"{store.structural.total_edges} edges"
        )
