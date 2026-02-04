"""PerFileAnalyzer — wraps existing primitive plugins."""

from pathlib import Path
from typing import Set

from ...primitives.extractor import PrimitiveExtractor
from ...logging_config import get_logger
from ..store import AnalysisStore

logger = get_logger(__name__)


class PerFileAnalyzer:
    name = "per_file"
    requires: Set[str] = {"files"}
    provides: Set[str] = {"file_signals"}

    def analyze(self, store: AnalysisStore) -> None:
        if not store.file_metrics:
            return

        extractor = PrimitiveExtractor(
            store.file_metrics,
            root_dir=store.root_dir,
        )
        store.file_signals = extractor.extract_all_dict()
        logger.debug(f"Per-file signals: {len(store.file_signals)} files")
