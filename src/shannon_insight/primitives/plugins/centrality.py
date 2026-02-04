"""Network centrality via PageRank on dependency graph."""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from ..base import PrimitivePlugin
from ...models import FileMetrics


class CentralityPrimitive(PrimitivePlugin):
    name = "network_centrality"
    display_name = "Network Centrality"
    short_name = "centrality"
    description = "Importance in dependency graph (PageRank)"
    direction = "high_is_bad"
    default_weight = 0.25

    _SKIP_NAMES = frozenset({
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
        "numpy", "np", "pandas", "pd", "scipy", "sklearn", "matplotlib",
        "plt", "seaborn", "requests", "flask", "django", "fastapi",
        "pydantic", "typer", "click", "rich", "diskcache", "pytest",
        "setuptools", "wheel", "pip", "pkg_resources",
    })

    def compute(self, files: List[FileMetrics], root_dir: Path) -> Dict[str, float]:
        graph = self._build_graph(files)
        return self._pagerank(files, graph)

    def _build_graph(self, files: List[FileMetrics]) -> Dict[str, Set[str]]:
        graph: Dict[str, Set[str]] = defaultdict(set)
        file_by_name = {Path(f.path).stem: f.path for f in files}
        for file in files:
            for imp in file.imports:
                pkg = imp.split("/")[-1].split(".")[-1]
                if pkg in self._SKIP_NAMES or pkg.startswith(".") or pkg == "":
                    continue
                if pkg in file_by_name and file_by_name[pkg] != file.path:
                    graph[file.path].add(file_by_name[pkg])
        return dict(graph)

    @staticmethod
    def _pagerank(files: List[FileMetrics], graph: Dict[str, Set[str]]) -> Dict[str, float]:
        scores = {f.path: 1.0 for f in files}
        damping, iterations = 0.85, 20
        incoming: Dict[str, Set[str]] = defaultdict(set)
        for src, targets in graph.items():
            for tgt in targets:
                incoming[tgt].add(src)
        for _ in range(iterations):
            new = {}
            for f in files:
                rank = 1 - damping
                for src in incoming.get(f.path, []):
                    out = len(graph.get(src, []))
                    if out > 0:
                        rank += damping * (scores[src] / out)
                new[f.path] = rank
            scores = new
        mx = max(scores.values()) if scores else 1.0
        if mx > 0:
            scores = {k: v / mx for k, v in scores.items()}
        return scores

    def interpret(self, v: float) -> str:
        if v > 0.5:
            return "high = heavily depended on"
        return "within typical range"
