"""StructuralAnalyzer — wraps existing AnalysisEngine.

Also runs Phase 3 clone detection (NCD) on file contents.
"""

from pathlib import Path

from ...graph.clone_detection import detect_clones
from ...graph.engine import AnalysisEngine
from ...logging_config import get_logger
from ..store_v2 import AnalysisStore

logger = get_logger(__name__)


class StructuralAnalyzer:
    name = "structural"
    requires: set[str] = {"files"}
    provides: set[str] = {"structural", "clone_pairs"}

    def analyze(self, store: AnalysisStore) -> None:
        if not store.file_metrics:
            return

        engine = AnalysisEngine(store.file_metrics, root_dir=store.root_dir)
        result = engine.run()
        store.structural.set(result, produced_by=self.name)
        logger.debug(f"Structural analysis: {result.total_files} files, {result.total_edges} edges")

        # Phase 3: Clone detection via NCD
        self._detect_clones(store)

    def _detect_clones(self, store: AnalysisStore) -> None:
        """Run NCD clone detection on file contents."""
        root = Path(store.root_dir) if store.root_dir else Path.cwd()

        # Read file contents
        file_contents: dict[str, bytes] = {}
        for fm in store.file_metrics:
            try:
                full_path = root / fm.path
                file_contents[fm.path] = full_path.read_bytes()
            except OSError:
                pass

        if len(file_contents) < 2:
            return

        # Get roles if available (for TEST/MIGRATION exclusion)
        roles: dict[str, str] = {}
        if store.roles.available:
            roles = store.roles.value

        clone_pairs = detect_clones(file_contents, roles)
        store.clone_pairs.set(clone_pairs, produced_by=self.name)
        logger.debug(f"Clone detection: {len(clone_pairs)} pairs found")
