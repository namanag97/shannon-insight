"""Fact data models for the unified fact store.

All facts are frozen dataclasses -- immutable records of observed reality.
They separate what-was-observed from what-was-computed, enabling incremental
re-analysis when only computations change.

Hierarchy:
    CommitFact          -- a git commit
    FileIdentity        -- stable identity across renames
    FileObservation     -- file state at a commit
    FileChangeFact      -- a file change within a commit
    ParsedSyntaxFact    -- parsed syntax keyed by content_hash (pure function)
    ExtractedFunction   -- function extracted from content
    ExtractedClass      -- class extracted from content
    ExtractedImport     -- import extracted from content

All models use ``from __future__ import annotations`` for Python 3.9 compat.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    """Type of change to a file in a commit.

    Values match git's single-letter status codes.
    """

    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"


# ── Identity & Observation ────────────────────────────────────────────


@dataclass(frozen=True)
class FileIdentity:
    """Stable identity for a file across its lifetime.

    Tracks a file from creation through renames to deletion.
    ``file_id`` is a UUID assigned at birth and never changes.
    """

    file_id: str  # UUID, stable across renames
    birth_commit: str  # commit hash that created this file
    birth_path: str  # original path at creation
    current_path: str | None  # None if deleted
    is_alive: bool


@dataclass(frozen=True)
class FileObservation:
    """Observed state of a file at a specific commit.

    Links a file identity to its content at a point in time.
    ``content_hash`` is SHA-256 of the raw file bytes.
    """

    file_id: str
    commit_hash: str
    path: str
    content_hash: str
    timestamp: int  # unix epoch seconds


# ── Git Facts ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CommitFact:
    """A commit observed from git log.

    Captures the immutable metadata of a single commit.
    ``author_id`` is a canonical ID after email deduplication.
    """

    commit_hash: str
    timestamp: int  # unix epoch seconds
    author_id: str  # canonical author identity
    author_email_raw: str
    author_name_raw: str
    message_subject: str
    message_body: str | None
    parent_hashes: tuple[str, ...]
    is_merge: bool


@dataclass(frozen=True)
class FileChangeFact:
    """A file change within a commit.

    One commit can produce many FileChangeFacts (one per file touched).
    ``change_type`` uses git's status codes via the ChangeType enum.
    """

    commit_hash: str
    file_id: str
    change_type: ChangeType
    old_path: str | None  # None for ADDED
    new_path: str | None  # None for DELETED
    additions: int | None  # line additions, None if binary
    deletions: int | None  # line deletions, None if binary


# ── Parsed Facts (keyed by content_hash) ──────────────────────────────


@dataclass(frozen=True)
class ParsedSyntaxFact:
    """Parsed syntax for a content hash.

    This is a pure function of file content: same bytes always produce
    the same ParsedSyntaxFact.  Keyed by ``content_hash`` so identical
    files are parsed only once.
    """

    content_hash: str
    language: str
    lines: int
    tokens: int | None
    complexity: int | None
    max_nesting: int | None
    has_main_guard: bool
    stub_ratio: float | None
    parser_type: str  # "tree-sitter" or "regex"


@dataclass(frozen=True)
class ExtractedFunction:
    """A function extracted from parsed content.

    Keyed by ``content_hash`` -- belongs to the file content, not a path.
    """

    content_hash: str
    name: str
    qualified_name: str  # "ClassName.method" or "function_name"
    start_line: int
    end_line: int
    params: tuple[str, ...]
    decorators: tuple[str, ...]
    body_tokens: int
    nesting_depth: int
    is_stub: bool
    class_name: str | None  # None if top-level function


@dataclass(frozen=True)
class ExtractedClass:
    """A class extracted from parsed content.

    Keyed by ``content_hash``.
    """

    content_hash: str
    name: str
    start_line: int
    end_line: int
    bases: tuple[str, ...]
    method_names: tuple[str, ...]
    field_names: tuple[str, ...]
    is_abstract: bool
    method_count: int


@dataclass(frozen=True)
class ExtractedImport:
    """An import statement extracted from parsed content.

    Keyed by ``content_hash``.  ``resolved_path`` is filled in during
    graph enrichment (phase 3); it may be None after initial parsing.
    """

    content_hash: str
    source: str  # "os.path" or "..models"
    names: tuple[str, ...]  # ("join", "dirname") from "from X import Y"
    is_relative: bool
    resolved_path: str | None  # resolved target in codebase, None if external
