"""Dependency graph construction from import declarations."""

from pathlib import Path
from typing import Optional

from ..scanning.syntax import FileSyntax
from .models import DependencyGraph


def build_dependency_graph(file_syntax: list[FileSyntax], root_dir: str = "") -> DependencyGraph:
    """Build dependency graph from import declarations in FileSyntax.

    Also tracks unresolved imports for phantom_import_count signal.
    Only imports that look like they should resolve internally are tracked
    as unresolved — stdlib and third-party imports are excluded.
    """
    file_map: dict[str, FileSyntax] = {f.path: f for f in file_syntax}
    all_paths = set(file_map.keys())
    adjacency: dict[str, list[str]] = {p: [] for p in all_paths}
    reverse: dict[str, list[str]] = {p: [] for p in all_paths}
    unresolved: dict[str, list[str]] = {}  # Phase 3: track unresolved imports
    edge_count = 0

    path_index = _build_path_index(all_paths)
    project_prefixes = _infer_project_prefixes(all_paths)

    for fs in file_syntax:
        for imp in fs.import_sources:
            resolved = _resolve_import(imp, fs.path, path_index, all_paths)
            if resolved and resolved != fs.path:
                adjacency[fs.path].append(resolved)
                reverse[resolved].append(fs.path)
                edge_count += 1
            elif resolved is None and _looks_internal(imp, project_prefixes):
                # Only track as phantom if it looks like it should be internal
                if fs.path not in unresolved:
                    unresolved[fs.path] = []
                unresolved[fs.path].append(imp)

    return DependencyGraph(
        adjacency=adjacency,
        reverse=reverse,
        all_nodes=all_paths,
        edge_count=edge_count,
        unresolved_imports=unresolved,
    )


def _infer_project_prefixes(all_paths: set[str]) -> set[str]:
    """Infer project namespace prefixes from file paths.

    If files live under "src/myproject/", then "myproject" is a project prefix.
    Relative imports (starting with ".") are always considered internal.
    """
    prefixes: set[str] = set()
    for path in all_paths:
        parts = Path(path).parts
        # Top-level directory names are likely project prefixes
        if len(parts) >= 2:
            prefixes.add(parts[0])
            # Also add "src/X" patterns
            if parts[0] == "src" and len(parts) >= 3:
                prefixes.add(parts[1])
    return prefixes


def _looks_internal(imp: str, project_prefixes: set[str]) -> bool:
    """Check if an unresolved import looks like it should be internal.

    Returns True for:
    - Relative imports (.foo, ..bar) — always internal
    - Imports matching a project namespace prefix

    Returns False for:
    - Stdlib-looking imports (single-segment: os, sys, math, fmt)
    - Go stdlib imports (quoted paths like "fmt", "net/http")
    - Third-party packages (don't match project prefixes)
    """
    imp = imp.strip()

    # Relative imports are always internal
    if imp.startswith("."):
        return True

    # Go-style quoted imports: strip quotes
    if imp.startswith('"') and imp.endswith('"'):
        imp = imp[1:-1]

    # Single-segment imports are almost always stdlib/builtin
    # (os, sys, fmt, math, json, etc.)
    if "." not in imp and "/" not in imp:
        return False

    # Check if any segment matches a project prefix
    first_segment = imp.split(".")[0].split("/")[0]
    if first_segment in project_prefixes:
        return True

    return False


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

    # Try with common project prefixes prepended
    for prefix in ("src.", "src.shannon_insight."):
        candidate = prefix + imp
        if candidate in path_index:
            return path_index[candidate]

    # Try stripping prefixes progressively
    # "shannon_insight.signals.composites" → "signals.composites" → "composites"
    parts = imp.split(".")
    for i in range(1, len(parts)):
        suffix = ".".join(parts[i:])
        if suffix in path_index:
            return path_index[suffix]

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
