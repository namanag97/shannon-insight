"""Extract the 5 orthogonal quality primitives"""

from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Optional
from datetime import datetime
import numpy as np

from ..models import FileMetrics, Primitives
from ..cache import AnalysisCache
from ..logging_config import get_logger
from ..math import Entropy, GraphMetrics, RobustStatistics as RobustStats

logger = get_logger(__name__)


class PrimitiveExtractor:
    """Extract the 5 orthogonal quality primitives"""

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

    def extract_all(self) -> Dict[str, Primitives]:
        """Extract all 5 primitives for each file"""
        results = {}

        # Build dependency graph (needed for centrality)
        dep_graph = self._build_dependency_graph()

        # Compute each primitive
        entropies = self._compute_structural_entropy()
        centralities = self._compute_network_centrality(dep_graph)
        volatilities = self._compute_churn_volatility()
        coherences = self._compute_semantic_coherence()
        loads = self._compute_cognitive_load()

        for file in self.files:
            results[file.path] = Primitives(
                structural_entropy=entropies.get(file.path, 0),
                network_centrality=centralities.get(file.path, 0),
                churn_volatility=volatilities.get(file.path, 0),
                semantic_coherence=coherences.get(file.path, 0),
                cognitive_load=loads.get(file.path, 0),
            )

        return results

    # ---- Primitive 1: Structural Entropy ----

    def _compute_structural_entropy(self) -> Dict[str, float]:
        """Compute normalized entropy of AST node type distribution."""
        entropies = {}

        for file in self.files:
            if not file.ast_node_types or sum(file.ast_node_types.values()) == 0:
                entropies[file.path] = 0.0
                continue

            entropies[file.path] = Entropy.normalized(file.ast_node_types)

        return entropies

    # ---- Primitive 2: Network Centrality ----

    # Standard library modules to ignore when building dependency graph
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

    # Common third-party packages to ignore
    _THIRDPARTY_NAMES = frozenset({
        "numpy", "np", "pandas", "pd", "scipy", "sklearn", "matplotlib",
        "plt", "seaborn", "requests", "flask", "django", "fastapi",
        "pydantic", "typer", "click", "rich", "diskcache", "pytest",
        "setuptools", "wheel", "pip", "pkg_resources",
    })

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build file dependency graph from internal project imports only."""
        graph = defaultdict(set)

        # Map import paths to actual files
        file_by_name = {}
        for file in self.files:
            name = Path(file.path).stem
            file_by_name[name] = file.path

        skip_names = self._STDLIB_NAMES | self._THIRDPARTY_NAMES

        for file in self.files:
            for imp in file.imports:
                # Extract the leaf module name
                pkg_name = imp.split("/")[-1].split(".")[-1]

                # Skip stdlib and third-party imports
                if pkg_name in skip_names:
                    continue

                # Skip relative import markers
                if pkg_name.startswith(".") or pkg_name == "":
                    continue

                # Only add edge if it points to a different file
                if pkg_name in file_by_name and file_by_name[pkg_name] != file.path:
                    graph[file.path].add(file_by_name[pkg_name])

        return dict(graph)

    def _compute_network_centrality(
        self, graph: Dict[str, Set[str]]
    ) -> Dict[str, float]:
        """Compute PageRank centrality.

        TODO: Delegate to GraphMetrics.pagerank() for consistency and
        correctness. The inline implementation differs from the canonical
        version: it uses (1-d) instead of (1-d)/N for base probability,
        has no dangling-node redistribution, no convergence check, and
        misses nodes that appear only as targets. The min-max normalization
        at the end masks the base-probability difference but the other
        issues remain.
        """
        # Initialize PageRank scores
        scores = {f.path: 1.0 for f in self.files}
        damping = 0.85
        iterations = 20

        # Build reverse graph (incoming edges)
        incoming = defaultdict(set)
        for src, targets in graph.items():
            for tgt in targets:
                incoming[tgt].add(src)

        # PageRank iteration
        for _ in range(iterations):
            new_scores = {}

            for file in self.files:
                # Base probability
                rank = 1 - damping

                # Add contribution from incoming edges
                for src in incoming.get(file.path, []):
                    out_degree = len(graph.get(src, []))
                    if out_degree > 0:
                        rank += damping * (scores[src] / out_degree)

                new_scores[file.path] = rank

            scores = new_scores

        # Normalize to [0, 1]
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}

        return scores

    # ---- Primitive 3: Churn Volatility ----

    def _compute_churn_volatility(self) -> Dict[str, float]:
        """Compute volatility of file modifications (filesystem-based)"""
        volatilities = {}

        # Since no git history, use file modification time as proxy
        now = datetime.now().timestamp()
        ages = [now - f.last_modified for f in self.files]

        if not ages:
            return {}

        # Normalize age to volatility score
        # Recent changes = high volatility
        max_age = max(ages)

        for file in self.files:
            age = now - file.last_modified
            # Invert: older = more stable = lower volatility
            volatility = 1 - (age / max_age) if max_age > 0 else 0
            volatilities[file.path] = volatility

        return volatilities

    # ---- Primitive 4: Semantic Coherence ----

    def _compute_semantic_coherence(self) -> Dict[str, float]:
        """Compute semantic coherence via TF-IDF clustering"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # Build document corpus (use imports + exports)
        documents = []
        paths = []

        for file in self.files:
            tokens = file.imports + file.exports
            doc = " ".join(tokens) if tokens else "empty"
            documents.append(doc)
            paths.append(file.path)

        if len(documents) < 2:
            return {f.path: 1.0 for f in self.files}

        # Compute TF-IDF vectors
        vectorizer = TfidfVectorizer(min_df=1, max_df=0.8)
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
        except Exception as e:
            logger.warning(f"TF-IDF vectorization failed: {e}")
            return {f.path: 1.0 for f in self.files}

        # Compute pairwise similarities
        similarities = cosine_similarity(tfidf_matrix)

        coherences = {}
        n = len(paths)
        for i, path in enumerate(paths):
            # Coherence = average similarity to OTHER files (exclude self)
            if n > 1:
                other_sims = [similarities[i][j] for j in range(n) if j != i]
                coherences[path] = float(np.mean(other_sims))
            else:
                coherences[path] = 1.0

        return coherences

    # ---- Primitive 5: Cognitive Load ----

    def _compute_cognitive_load(self) -> Dict[str, float]:
        """Compute cognitive load = concepts × complexity.

        TODO: The formula CL = concepts * complexity * (1 + depth/10) is a
        hand-tuned heuristic with no academic citation. The /10 divisor
        maps typical nesting depths (0-5) to a 0-50% multiplier. Consider
        citing Cant et al. (1995) "A Conceptual Complexity Metric" or
        replacing with a validated cognitive complexity model such as
        SonarSource's Cognitive Complexity (2017).
        """
        loads = {}

        for file in self.files:
            # Concepts = functions + structs + interfaces
            concepts = file.functions + file.structs + file.interfaces

            # Cognitive load = concepts × complexity × nesting
            load = concepts * file.complexity_score * (1 + file.nesting_depth / 10)
            loads[file.path] = load

        # Normalize to [0, 1]
        if loads:
            max_load = max(loads.values())
            if max_load > 0:
                loads = {k: v / max_load for k, v in loads.items()}

        return loads
