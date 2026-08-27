"""Deterministic file discovery with filtering.

Contract: same root + config => identical sorted output, always. Symlinks are
never followed by default. Exclusion uses gitignore-style patterns via
``pathspec`` (gitwildmatch) — the same semantics users already know.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pathspec

from shannon_insight.syntax.packs import detect_language


@dataclass(frozen=True)
class DiscoveryConfig:
    respect_gitignore: bool = True
    exclude_patterns: tuple[str, ...] = (
        ".git/",
        "node_modules/",
        "vendor/",
        "dist/",
        "build/",
        "__pycache__/",
        ".venv/",
        "*.min.js",
        "*.pyc",
    )
    max_file_size_mb: float = 10.0
    allow_hidden: bool = False
    follow_symlinks: bool = False


def _is_excluded(spec: pathspec.PathSpec | None, rel_posix: str) -> bool:
    if spec is not None and spec.match_file(rel_posix):
        return True
    return False


def discover(root: str | Path, config: DiscoveryConfig | None = None) -> Iterator[Path]:
    """Yield analyzable source files under *root*, deterministically."""
    cfg = config or DiscoveryConfig()
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(f"analysis root not found: {root}")

    lines = list(cfg.exclude_patterns)
    if cfg.respect_gitignore:
        gi = Path(root) / ".gitignore"
        if gi.exists():
            try:
                lines += [
                    ln
                    for ln in gi.read_text(encoding="utf-8", errors="replace").splitlines()
                    if ln.strip() and not ln.lstrip().startswith("#")
                ]
            except OSError:
                pass
    spec = pathspec.PathSpec.from_lines("gitwildmatch", lines) if lines else None
    nested_specs: dict[Path, tuple[str, object]] = {}
    max_bytes = int(cfg.max_file_size_mb * 1024 * 1024)

    dirs = [root_path]
    while dirs:
        current = dirs.pop(0)
        try:
            entries = sorted(current.iterdir(), key=lambda p: p.name)
        except PermissionError:
            continue
        for entry in entries:
            name = entry.name
            if not cfg.allow_hidden and name.startswith("."):
                continue
            rel = entry.relative_to(root_path).as_posix()
            if cfg.respect_gitignore and entry.is_dir():
                ngi = entry / ".gitignore"
                if ngi.exists():
                    try:
                        sub_lines = [
                            f"{entry.relative_to(root_path).as_posix()}/{ln.strip()}"
                            for ln in ngi.read_text(encoding="utf-8", errors="replace").splitlines()
                            if ln.strip()
                            and not ln.lstrip().startswith("#")
                            and not ln.lstrip().startswith("!")
                        ]
                        if sub_lines:
                            nested_specs[entry] = pathspec.PathSpec.from_lines(
                                "gitwildmatch", sub_lines
                            )
                    except OSError:
                        pass
            if entry.is_symlink() and not cfg.follow_symlinks:
                continue
            if entry.is_dir():
                if not _is_excluded(spec, rel + "/"):
                    dirs.append(entry)
                continue
            if not entry.is_file():
                continue
            if detect_language(str(entry)) is None:
                continue
            if _is_excluded(spec, rel):
                continue
            for ndir, nspec in nested_specs.items():
                if rel.startswith(
                    ndir.relative_to(root_path).as_posix() + "/"
                ) and nspec.match_file(rel):
                    skip_nested = True
                    break
            else:
                skip_nested = False
            if skip_nested:
                continue
            try:
                if entry.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            yield entry


__all__ = ["DiscoveryConfig", "discover"]
