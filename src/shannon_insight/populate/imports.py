"""Populate IMPORT layer (R=0) from FileSyntax import declarations.

Resolves imports to file paths using the file set, handling both
relative and absolute imports.  Weight = 1.0 for each resolved import.
Self-imports are skipped.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..tensor.core import IMPORT
from ..extract.models import FileSyntax


# ---------------------------------------------------------------------------
# Import resolution (mirrors graph/builder.py logic for tensor population)
# ---------------------------------------------------------------------------

def _resolve_import(imp: Any, source_path: str, file_set: set[str]) -> str | None:
    """Resolve a single Import object to a target file path in *file_set*.

    Handles:
      - Already-resolved imports (imp.resolved_path is set)
      - Relative imports (.base, ..models) via leading dots in imp.source
      - Absolute imports (some.module) by dotted-path-to-slash conversion
    """
    # If already resolved by the scanner, use that directly
    if hasattr(imp, "resolved_path") and imp.resolved_path:
        normalized = str(Path(imp.resolved_path))
        if normalized in file_set:
            return normalized

    # Get module string — ImportDecl uses .source, extract.models uses .module
    module_str = getattr(imp, "source", None) or getattr(imp, "module", "")
    if not module_str:
        return None

    source_dir = str(Path(source_path).parent)

    if imp.is_relative:
        # Count leading dots to determine relative level
        level = len(module_str) - len(module_str.lstrip("."))
        module_part = module_str.lstrip(".")

        # Walk up directories
        target_dir = source_dir
        for _ in range(max(0, level - 1)):
            target_dir = str(Path(target_dir).parent)

        if module_part:
            candidates = [
                f"{target_dir}/{module_part.replace('.', '/')}.py",
                f"{target_dir}/{module_part.replace('.', '/')}/__init__.py",
            ]
        else:
            candidates = [f"{target_dir}/__init__.py"]
    else:
        # Absolute import — try with and without src/ prefix
        module_path = module_str.replace(".", "/")
        candidates = [
            f"{module_path}.py",
            f"{module_path}/__init__.py",
            f"src/{module_path}.py",
            f"src/{module_path}/__init__.py",
        ]

    for candidate in candidates:
        normalized = str(Path(candidate))
        if normalized in file_set:
            return normalized

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def populate_imports(
    tensor: Any,
    syntax_map: dict[str, Any],
    t: int = -1,
) -> None:
    """Fill T[:,:,t,IMPORT] from resolved imports.

    Args:
        tensor: A ``RelationTensor`` instance.
        syntax_map: ``{path: FileSyntax}`` mapping — the file set is derived
            from its keys.
        t: Time-window index.  ``-1`` (default) means the current window
            (``tensor.n_windows - 1``).
    """
    file_set = set(syntax_map.keys())

    # Default to the latest time window
    if t == -1:
        t = tensor.n_windows - 1

    for source_path, syntax in syntax_map.items():
        for imp in syntax.imports:
            target = _resolve_import(imp, source_path, file_set)
            if target and target != source_path:  # skip self-imports
                tensor.add_edge(source_path, target, t, IMPORT, weight=1.0)
