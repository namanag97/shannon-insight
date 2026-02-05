"""Extract quality primitives — plugin-driven.

Each primitive registered in the plugin registry provides a ``compute()``
method that returns ``Dict[str, float]``. Results are merged automatically.
"""

from pathlib import Path
from typing import Dict, List, Optional

from ..cache import AnalysisCache
from ..logging_config import get_logger
from ..models import FileMetrics, Primitives, PrimitiveValues
from .registry import get_plugins

logger = get_logger(__name__)


class PrimitiveExtractor:
    """Extract quality primitives for each file — driven by plugins."""

    def __init__(
        self,
        files: List[FileMetrics],
        cache: Optional[AnalysisCache] = None,
        config_hash: str = "",
        root_dir: Optional[str] = None,
    ):
        self.files = files
        self.file_map = {f.path: f for f in files}
        self.cache = cache
        self.config_hash = config_hash
        self.root_dir = Path(root_dir) if root_dir else None
        logger.debug(f"Initialized PrimitiveExtractor for {len(files)} files")

    def extract_all(self) -> Dict[str, Primitives]:
        """Extract all registered primitives for each file."""
        raw = self.extract_all_dict()
        results: Dict[str, Primitives] = {}
        for path, vals in raw.items():
            results[path] = Primitives.from_dict(vals)
        return results

    def extract_all_dict(self) -> Dict[str, PrimitiveValues]:
        """Extract all registered primitives as Dict[str, Dict[str, float]]."""
        plugins = get_plugins()
        root = self.root_dir or Path(".")

        per_primitive: Dict[str, Dict[str, float]] = {}
        for plugin in plugins:
            try:
                per_primitive[plugin.name] = plugin.compute(self.files, root)
            except Exception as e:
                logger.warning(f"Plugin {plugin.name!r} failed: {e}")
                per_primitive[plugin.name] = {f.path: 0.0 for f in self.files}

        # Pivot: file -> {prim_name: value}
        result: Dict[str, PrimitiveValues] = {}
        for file in self.files:
            vals: PrimitiveValues = {}
            for plugin in plugins:
                vals[plugin.name] = per_primitive[plugin.name].get(file.path, 0.0)
            result[file.path] = vals

        return result
