"""Extraction data models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Function:
    name: str
    params: int
    body_tokens: int
    signature_tokens: int
    nesting_depth: int
    start_line: int
    end_line: int

    @property
    def is_stub(self) -> bool:
        return self.body_tokens < 5


@dataclass(frozen=True)
class Import:
    module: str
    names: tuple[str, ...]
    level: int  # 0 = absolute, 1+ = relative
    line: int

    @property
    def is_relative(self) -> bool:
        return self.level > 0


@dataclass
class FileSyntax:
    path: str
    language: str
    content_hash: str
    lines: int
    functions: list[Function]
    classes: list[str]
    imports: list[Import]
    identifiers: frozenset[str]
    complexity: int
    max_nesting: int
    has_main_guard: bool = False

    @property
    def function_count(self) -> int:
        return len(self.functions)

    @property
    def class_count(self) -> int:
        return len(self.classes)

    @property
    def import_count(self) -> int:
        return len(self.imports)

    @property
    def stub_ratio(self) -> float:
        if not self.functions:
            return 0.0
        return sum(1 for f in self.functions if f.is_stub) / len(self.functions)

    @property
    def impl_gini(self) -> float:
        """Gini coefficient of function body sizes."""
        if len(self.functions) < 2:
            return 0.0
        sizes = sorted(f.body_tokens for f in self.functions)
        n = len(sizes)
        total = sum(sizes)
        if total == 0:
            return 0.0
        gini_value = (2 * sum(i * s for i, s in enumerate(sizes, 1))) / (n * total) - (n + 1) / n
        return max(0.0, min(1.0, gini_value))


@dataclass(frozen=True)
class Commit:
    hash: str
    timestamp: int  # Unix seconds
    author: str
    subject: str
    files: tuple[str, ...]

    @property
    def is_fix(self) -> bool:
        s = self.subject.lower()
        return any(kw in s for kw in ["fix", "bug", "patch", "issue", "error"])

    @property
    def is_refactor(self) -> bool:
        s = self.subject.lower()
        return any(kw in s for kw in ["refactor", "clean", "rename", "move"])


@dataclass(frozen=True)
class FileChange:
    commit_hash: str
    path: str
    change_type: Literal["A", "M", "D", "R"]
    additions: int = 0
    deletions: int = 0
    old_path: str | None = None  # For renames


@dataclass
class GitHistory:
    commits: list[Commit]
    changes: list[FileChange]

    @property
    def total_commits(self) -> int:
        return len(self.commits)

    def changes_for_file(self, path: str) -> list[FileChange]:
        return [c for c in self.changes if c.path == path]

    def files_in_commit(self, commit_hash: str) -> list[str]:
        return [c.path for c in self.changes if c.commit_hash == commit_hash]
