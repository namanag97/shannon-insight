"""Dependency graph construction from import declarations."""

from pathlib import Path
from typing import Optional

from ..scanning.models import FileMetrics
from .models import DependencyGraph


def build_dependency_graph(file_metrics: list[FileMetrics], root_dir: str = "") -> DependencyGraph:
    """Build dependency graph from import declarations in FileMetrics.

    Also tracks unresolved imports for phantom_import_count signal.
    """
    file_map: dict[str, FileMetrics] = {f.path: f for f in file_metrics}
    all_paths = set(file_map.keys())
    adjacency: dict[str, list[str]] = {p: [] for p in all_paths}
    reverse: dict[str, list[str]] = {p: [] for p in all_paths}
    unresolved: dict[str, list[str]] = {}  # Phase 3: track unresolved imports
    edge_count = 0

    path_index = _build_path_index(all_paths)

    for fm in file_metrics:
        for imp in fm.imports:
            resolved = _resolve_import(imp, fm.path, path_index, all_paths)
            if resolved and resolved != fm.path:
                adjacency[fm.path].append(resolved)
                reverse[resolved].append(fm.path)
                edge_count += 1
            elif resolved is None:
                # Phase 3: track unresolved imports (potentially phantom)
                if fm.path not in unresolved:
                    unresolved[fm.path] = []
                unresolved[fm.path].append(imp)

    return DependencyGraph(
        adjacency=adjacency,
        reverse=reverse,
        all_nodes=all_paths,
        edge_count=edge_count,
        unresolved_imports=unresolved,
    )


def _build_path_index(all_paths: set[str]) -> dict[str, str]:
    """Map dotted module paths to file paths for import resolution.

    Builds multiple lookup keys per file so resolution can work
    from different prefix levels.
    """
    index: dict[str, str] = {}
    for path in all_paths:
        # "src/shannon_insight/models.py" -> dotted form
        dotted = path.replace("/", ".").replace("\\", ".").replace(".py", "")
        # Remove __init__ suffix: "src.shannon_insight.math.__init__" -> "src.shannon_insight.math"
        if dotted.endswith(".__init__"):
            dotted = dotted[: -len(".__init__")]

        index[dotted] = path

        # Also without "src." prefix
        if dotted.startswith("src."):
            short = dotted[4:]
            index[short] = path

    return index


def _resolve_import(
    imp: str,
    source_path: str,
    path_index: dict[str, str],
    all_paths: set[str],
) -> Optional[str]:
    """Resolve an import string to a file path in the codebase.

    Handles:
      - Relative imports: .base, ..models, ..math.graph
      - Absolute imports: shannon_insight.models, pathlib, os
    """
    imp = imp.strip()

    # ── Relative imports (leading dots) ────────────────────────
    if imp.startswith("."):
        return _resolve_relative_import(imp, source_path, all_paths)

    # ── Absolute imports ───────────────────────────────────────
    # Try exact match in index
    if imp in path_index:
        return path_index[imp]

    # Try with common project prefixes stripped
    for prefix in ("src.", "src.shannon_insight."):
        candidate = prefix + imp
        if candidate in path_index:
            return path_index[candidate]

    # Not an internal import (stdlib or third-party)
    return None


def _resolve_relative_import(imp: str, source_path: str, all_paths: set[str]) -> Optional[str]:
    """Resolve a Python relative import like ..models or .base."""
    # Count leading dots
    dot_count = 0
    while dot_count < len(imp) and imp[dot_count] == ".":
        dot_count += 1
    module_part = imp[dot_count:]  # e.g., "models", "math.graph", "base"

    # Navigate up from source file's directory
    source_dir = Path(source_path).parent
    for _ in range(dot_count - 1):  # -1 because . means current package
        source_dir = source_dir.parent

    # Build candidate paths
    if module_part:
        module_as_path = module_part.replace(".", "/")
        candidates = [
            str(source_dir / module_as_path) + ".py",
            str(source_dir / module_as_path / "__init__.py"),
        ]
    else:
        candidates = [str(source_dir / "__init__.py")]

    for candidate in candidates:
        if candidate in all_paths:
            return candidate

    return None
