"""Populate IMPORT layer (R=0)."""
from __future__ import annotations

from pathlib import Path

from ..tensor.core import RelationTensor, IMPORT
from ..extract.models import FileSyntax


def resolve_import(imp, source_path: str, file_set: set[str]) -> str | None:
    """Resolve import to target file path."""
    source_dir = str(Path(source_path).parent)

    if imp.is_relative:
        # Relative import
        target_dir = source_dir
        for _ in range(imp.level - 1):
            target_dir = str(Path(target_dir).parent)

        if imp.module:
            candidates = [
                f"{target_dir}/{imp.module.replace('.', '/')}.py",
                f"{target_dir}/{imp.module.replace('.', '/')}/__init__.py",
            ]
        else:
            candidates = [f"{target_dir}/__init__.py"]
    else:
        # Absolute import
        module_path = imp.module.replace(".", "/")
        candidates = [
            f"{module_path}.py",
            f"{module_path}/__init__.py",
            f"src/{module_path}.py",
            f"src/{module_path}/__init__.py",
        ]

    for candidate in candidates:
        # Normalize
        normalized = str(Path(candidate))
        if normalized in file_set:
            return normalized

    return None


def populate_imports(
    tensor: RelationTensor,
    syntax_map: dict[str, FileSyntax],
    t: int = -1,
):
    """Fill T[:,:,t,IMPORT] from resolved imports."""
    file_set = set(syntax_map.keys())

    # Use last time window if -1
    if t == -1:
        t = tensor.n_windows - 1

    for source_path, syntax in syntax_map.items():
        for imp in syntax.imports:
            target = resolve_import(imp, source_path, file_set)
            if target and target != source_path:
                tensor.add_edge(source_path, target, t, IMPORT, weight=1.0)
