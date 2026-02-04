"""Extract quality primitives — registry-driven.

Each primitive registered in ``registry.PRIMITIVE_REGISTRY`` is computed by a
``_compute_<name>`` method on this class that returns ``Dict[str, float]``.
The results are merged automatically.
"""

from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Optional
from datetime import datetime
import numpy as np

from ..models import FileMetrics, Primitives, PrimitiveValues
from ..cache import AnalysisCache
from ..logging_config import get_logger
from ..math import Entropy, GraphMetrics, RobustStatistics as RobustStats, Compression, Gini, IdentifierAnalyzer
from .registry import get_registry

logger = get_logger(__name__)


class PrimitiveExtractor:
    """Extract quality primitives for each file — driven by the registry."""

    def __init__(
        self,
        files: List[FileMetrics],
        cache: Optional[AnalysisCache] = None,
        config_hash: str = ""
    ):
        self.files = files
        self.file_map = {f.path: f for f in files}
        self.cache = cache
        self.config_hash = config_hash
        logger.debug(f"Initialized PrimitiveExtractor for {len(files)} files")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_all(self) -> Dict[str, Primitives]:
        """Extract all registered primitives for each file.

        Returns a Dict[str, Primitives] for backward-compatibility. The
        Primitives dataclass is built from the dict values.
        """
        raw = self.extract_all_dict()

        results: Dict[str, Primitives] = {}
        for path, vals in raw.items():
            results[path] = Primitives.from_dict(vals)
        return results

    def extract_all_dict(self) -> Dict[str, PrimitiveValues]:
        """Extract all registered primitives as Dict[str, Dict[str, float]].

        This is the extensible entry-point. New primitives added to the
        registry are picked up automatically as long as a matching
        ``_compute_<name>`` method exists on this class.
        """
        registry = get_registry()

        # Pre-compute dependency graph (needed by centrality)
        dep_graph = self._build_dependency_graph()

        # Compute each registered primitive
        per_primitive: Dict[str, Dict[str, float]] = {}
        for defn in registry:
            compute_fn = getattr(self, f"_compute_{defn.name}", None)
            if compute_fn is None:
                logger.warning(f"No compute method for primitive {defn.name!r}, skipping")
                continue
            if defn.name == "network_centrality":
                per_primitive[defn.name] = compute_fn(dep_graph)
            else:
                per_primitive[defn.name] = compute_fn()

        # Pivot: file -> {prim_name: value}
        result: Dict[str, PrimitiveValues] = {}
        for file in self.files:
            vals: PrimitiveValues = {}
            for defn in registry:
                if defn.name in per_primitive:
                    vals[defn.name] = per_primitive[defn.name].get(file.path, 0.0)
            result[file.path] = vals

        return result

    # ------------------------------------------------------------------
    # Primitive compute methods (one per registered primitive)
    # ------------------------------------------------------------------

    def _compute_structural_entropy(self) -> Dict[str, float]:
        """Compute compression-based complexity (replaces AST node entropy).

        Uses zlib compression ratio as a Kolmogorov complexity approximation.
        Language-agnostic: works on raw bytes, no parser needed.
        """
        complexities: Dict[str, float] = {}
        for file in self.files:
            file_path = Path(file.path)
            if not file_path.is_absolute():
                # Resolve relative paths against the first file's parent
                # (files come from scanners which use relative paths)
                candidates = list(Path('.').rglob(str(file_path)))
                if candidates:
                    file_path = candidates[0]

            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                complexities[file.path] = Compression.compression_ratio(content)
            except Exception as e:
                logger.warning(f"Failed to compute compression for {file.path}: {e}")
                complexities[file.path] = 0.0

        return complexities

    # -- stdlib / third-party skip sets for dependency graph --

    _STDLIB_NAMES = frozenset({
        "abc", "ast", "asyncio", "base64", "bisect", "builtins", "calendar",
        "cmath", "codecs", "collections", "concurrent", "contextlib", "copy",
        "csv", "ctypes", "dataclasses", "datetime", "decimal", "difflib",
        "email", "enum", "errno", "fcntl", "fileinput", "fnmatch", "fractions",
        "ftplib", "functools", "gc", "getpass", "glob", "gzip", "hashlib",
        "heapq", "hmac", "html", "http", "importlib", "inspect", "io",
        "itertools", "json", "logging", "lzma", "math", "mimetypes",
        "multiprocessing", "operator", "os", "pathlib", "pickle", "platform",
        "pprint", "queue", "random", "re", "secrets", "select", "shelve",
        "shlex", "shutil", "signal", "socket", "sqlite3", "ssl",
        "statistics", "string", "struct", "subprocess", "sys", "tempfile",
        "textwrap", "threading", "time", "timeit", "tkinter", "token",
        "tomllib", "traceback", "types", "typing", "unicodedata", "unittest",
        "urllib", "uuid", "venv", "warnings", "weakref", "xml", "zipfile",
        "zlib",
    })

    _THIRDPARTY_NAMES = frozenset({
        "numpy", "np", "pandas", "pd", "scipy", "sklearn", "matplotlib",
        "plt", "seaborn", "requests", "flask", "django", "fastapi",
        "pydantic", "typer", "click", "rich", "diskcache", "pytest",
        "setuptools", "wheel", "pip", "pkg_resources",
    })

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build file dependency graph from internal project imports only."""
        graph = defaultdict(set)
        file_by_name = {}
        for file in self.files:
            name = Path(file.path).stem
            file_by_name[name] = file.path

        skip_names = self._STDLIB_NAMES | self._THIRDPARTY_NAMES

        for file in self.files:
            for imp in file.imports:
                pkg_name = imp.split("/")[-1].split(".")[-1]
                if pkg_name in skip_names:
                    continue
                if pkg_name.startswith(".") or pkg_name == "":
                    continue
                if pkg_name in file_by_name and file_by_name[pkg_name] != file.path:
                    graph[file.path].add(file_by_name[pkg_name])

        return dict(graph)

    def _compute_network_centrality(self, graph: Dict[str, Set[str]]) -> Dict[str, float]:
        """Compute PageRank centrality."""
        scores = {f.path: 1.0 for f in self.files}
        damping = 0.85
        iterations = 20

        incoming = defaultdict(set)
        for src, targets in graph.items():
            for tgt in targets:
                incoming[tgt].add(src)

        for _ in range(iterations):
            new_scores = {}
            for file in self.files:
                rank = 1 - damping
                for src in incoming.get(file.path, []):
                    out_degree = len(graph.get(src, []))
                    if out_degree > 0:
                        rank += damping * (scores[src] / out_degree)
                new_scores[file.path] = rank
            scores = new_scores

        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}

        return scores

    def _compute_churn_volatility(self) -> Dict[str, float]:
        """Compute volatility of file modifications (filesystem-based)."""
        volatilities = {}
        now = datetime.now().timestamp()
        ages = [now - f.last_modified for f in self.files]

        if not ages:
            return {}

        max_age = max(ages)

        for file in self.files:
            age = now - file.last_modified
            volatility = 1 - (age / max_age) if max_age > 0 else 0
            volatilities[file.path] = volatility

        return volatilities

    def _compute_semantic_coherence(self) -> Dict[str, float]:
        """Compute semantic coherence via identifier token analysis.

        Replaces the old TF-IDF-on-imports approach.  Extracts identifiers
        from source code, splits camelCase/snake_case, and measures how
        tightly the vocabulary clusters (single responsibility = coherent).
        """
        coherences: Dict[str, float] = {}
        for file in self.files:
            file_path = Path(file.path)
            if not file_path.is_absolute():
                candidates = list(Path('.').rglob(str(file_path)))
                if candidates:
                    file_path = candidates[0]

            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                tokens = IdentifierAnalyzer.extract_identifier_tokens(content)
                coherences[file.path] = IdentifierAnalyzer.compute_coherence(tokens)
            except Exception as e:
                logger.warning(f"Failed to compute coherence for {file.path}: {e}")
                coherences[file.path] = 1.0  # Default to coherent on failure

        return coherences

    def _compute_cognitive_load(self) -> Dict[str, float]:
        """Compute cognitive load enhanced with Gini coefficient.

        Base load = concepts x complexity x nesting_factor
        Enhanced with function size inequality: load x (1 + gini)

        High Gini means a few functions dominate the file's complexity
        (the "God function" pattern), which makes the file harder to
        understand even if the total function count is moderate.
        """
        loads: Dict[str, float] = {}

        for file in self.files:
            concepts = file.functions + file.structs + file.interfaces
            base_load = concepts * file.complexity_score * (1 + file.nesting_depth / 10)

            # Apply Gini coefficient for function size inequality
            if file.function_sizes and len(file.function_sizes) > 1:
                try:
                    gini = Gini.gini_coefficient(file.function_sizes)
                except ValueError:
                    gini = 0.0
                concentration = 1.0 + gini
            else:
                concentration = 1.0

            loads[file.path] = base_load * concentration

        # Normalize to [0, 1]
        if loads:
            max_load = max(loads.values())
            if max_load > 0:
                loads = {k: v / max_load for k, v in loads.items()}

        return loads
