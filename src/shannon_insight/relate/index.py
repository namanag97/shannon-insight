"""ModuleIndex (seam ①): the pass-1 totality substrate.

Built once from Phase-1 artifacts; binding kernels only ever query it —
never the filesystem, never each other's maps. Case-folding rescue is a
first-class query because case-mismatched imports are a real portability
defect worth counting, not an error to swallow.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from shannon_insight.syntax.models import FileSyntax


class ModuleIndex:
    def __init__(self, files: dict[str, FileSyntax]) -> None:
        self._files: set[str] = set(files)
        self._casefold: dict[str, str] = {}
        for rel in files:
            self._casefold.setdefault(rel.lower(), rel)
        self._files_by_dir: dict[str, list[tuple[str, str]]] = {}
        for rel in files:
            d, _, name = rel.rpartition("/")
            self._files_by_dir.setdefault(d, []).append((name, rel))
        for lst in self._files_by_dir.values():
            lst.sort()
        self._dirs: frozenset[str] | None = None

    def has(self, rel_posix: str) -> bool:
        return rel_posix in self._files

    def casefold_lookup(self, rel_posix: str) -> str | None:
        return self._casefold.get(rel_posix.lower())

    @property
    def dirs(self) -> frozenset[str]:
        if self._dirs is None:
            seen: set[str] = set()
            for rel in self._files:
                d = rel.rpartition("/")[0]
                while d:
                    seen.add(d)
                    d = d.rpartition("/")[0]
            self._dirs = frozenset(seen)
        return self._dirs

    def dir_exists(self, dir_posix: str) -> bool:
        d = dir_posix.strip("/")
        return (not d) or d in self.dirs

    def files_under(self, dir_posix: str, suffixes: tuple[str, ...], cap: int) -> list[str]:
        """All indexed files directly under dir_posix matching suffix set."""
        d = dir_posix.strip("/")
        hits = [
            rel
            for name, rel in self._files_by_dir.get(d, [])
            if not suffixes or PurePosixPath(name).suffix.lower() in suffixes
        ]
        return sorted(hits)[:cap]

    def __len__(self) -> int:
        return len(self._files)


def normalize_base(*segments: str) -> str:
    """Join + collapse ./ and intermediate ../ lexically (no fs)."""
    parts: list[str] = []
    for seg in segments:
        if not seg:
            continue
        for piece in seg.split("/"):
            if piece in ("", "."):
                continue
            if piece == "..":
                if parts and parts[-1] != "..":
                    parts.pop()
                else:
                    parts.append("..")
            else:
                parts.append(piece)
    return "/".join(parts)


__all__ = ["ModuleIndex", "normalize_base"]
