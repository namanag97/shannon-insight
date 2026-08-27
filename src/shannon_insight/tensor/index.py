"""Node indexing utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NodeIndex:
    """Bidirectional mapping between file paths and integer indices."""

    _path_to_idx: dict[str, int]
    _idx_to_path: dict[int, str]

    @classmethod
    def from_paths(cls, paths: list[str]) -> NodeIndex:
        sorted_paths = sorted(paths)
        path_to_idx = {p: i for i, p in enumerate(sorted_paths)}
        idx_to_path = {i: p for p, i in path_to_idx.items()}
        return cls(path_to_idx, idx_to_path)

    def __len__(self) -> int:
        return len(self._path_to_idx)

    def __getitem__(self, key: str | int) -> int | str:
        if isinstance(key, str):
            return self._path_to_idx[key]
        return self._idx_to_path[key]

    def __contains__(self, path: str) -> bool:
        return path in self._path_to_idx

    def paths(self) -> list[str]:
        return [self._idx_to_path[i] for i in range(len(self))]
