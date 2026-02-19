"""Data models for raw git storage.

Raw git data is persisted to enable:
1. Incremental updates (only fetch new commits)
2. Multiple analyses without re-parsing git log
3. Rich queries (authorship, line counts, renames)

These models map directly to database tables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ChangeType(str, Enum):
    """Git change type from --name-status."""

    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"

    @classmethod
    def from_git(cls, code: str) -> ChangeType:
        """Parse git change code (A, M, D, R###, C###)."""
        if code.startswith("R"):
            return cls.RENAMED
        if code.startswith("C"):
            return cls.COPIED
        return cls(code[0])


@dataclass
class GitCommit:
    """Raw commit data from git log.

    Stores everything needed for churn analysis, authorship,
    and co-change detection without re-running git.
    """

    hash: str  # 40-char SHA
    timestamp: int  # unix seconds
    author_email: str
    author_name: str
    subject: str  # First line of commit message
    body: str = ""  # Optional multiline body
    parent_hashes: tuple[str, ...] = ()  # For merge detection

    @property
    def is_merge(self) -> bool:
        """True if commit has multiple parents."""
        return len(self.parent_hashes) > 1


@dataclass
class GitFileChange:
    """One file changed in one commit.

    Captures additions/deletions for churn analysis,
    change type for rename tracking, old_path for renames.
    """

    commit_hash: str
    file_path: str
    additions: int | None  # None for binary files
    deletions: int | None  # None for binary files
    change_type: ChangeType
    old_path: str | None = None  # For renames: R old -> new
    file_id: str | None = None  # Stable identity across renames

    @property
    def is_binary(self) -> bool:
        """True if git reported binary file (- - in numstat)."""
        return self.additions is None

    @property
    def churn(self) -> int:
        """Total lines changed (additions + deletions), 0 for binary."""
        if self.is_binary:
            return 0
        return (self.additions or 0) + (self.deletions or 0)


@dataclass
class GitExtractionSession:
    """Tracks a git extraction run.

    Enables incremental updates: next run continues from head_sha.
    """

    id: str  # UUID
    repo_path: str
    started_at: datetime
    completed_at: datetime | None
    head_sha: str  # HEAD at extraction time
    oldest_sha: str | None  # Oldest commit extracted
    commit_count: int
    file_change_count: int
    status: str  # "running" | "completed" | "failed"
    error_message: str | None = None


@dataclass
class GitRawData:
    """Extraction result: commits + file changes.

    Intermediate structure before database storage.
    """

    commits: list[GitCommit] = field(default_factory=list)
    file_changes: list[GitFileChange] = field(default_factory=list)
    head_sha: str = ""
    oldest_sha: str | None = None

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def file_change_count(self) -> int:
        return len(self.file_changes)


__all__ = [
    "ChangeType",
    "GitCommit",
    "GitFileChange",
    "GitExtractionSession",
    "GitRawData",
]
