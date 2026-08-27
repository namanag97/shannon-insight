"""Intake application service: thin orchestration over the fine-DAG nodes.

Node order IS the contract (see pipeline.py). This class adds nothing but
sequencing, event emission, and per-item isolation.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path

from shannon_insight.core.errors import ErrorCode, ShannonError
from shannon_insight.facts.authors import AuthorRecord
from shannon_insight.facts.classify import FileClass, classify
from shannon_insight.facts.discovery import DiscoveryConfig
from shannon_insight.facts.models import CommitFact, FileChangeFact
from shannon_insight.facts.git_extractor import git_context
from shannon_insight.intake.pipeline import (
    IdentityView,
    a0_canonicalize_authors,
    g1_candidate_paths,
    h1_read_capped,
    h2_content_hash,
    i0_resolve_identity,
    i0b_resolve_offline,
    j0_join,
    p0_parse_unit,
    s0_session_context,
    x1_has_git,
    x2_extract_streams,
)
from shannon_insight.syntax.models import FileSyntax
from shannon_insight.syntax.parser import ParserManager


class SkipReason(Enum):
    UNPARSEABLE_CLASS = "unparseable_class"
    UNSUPPORTED_LANGUAGE = "unsupported_language"
    TOO_LARGE = "too_large"
    READ_ERROR = "read_error"
    PARSE_ERROR = "parse_error"


@dataclass(frozen=True)
class IntakeConfig:
    root: str | Path
    exclude_patterns: tuple[str, ...] = ()
    max_file_size_mb: float = 10.0
    allow_hidden: bool = False
    follow_symlinks: bool = False
    max_commits: int = 5000
    use_git: bool = True
    max_files: int = 50_000
    respect_gitignore: bool = True


@dataclass(frozen=True)
class ParsedFile:
    rel_path: str
    content_hash: str
    language: str
    syntax: FileSyntax
    file_id: str | None = None
    total_changes: int = 0
    file_class: FileClass = FileClass.SOURCE


@dataclass(frozen=True)
class SkippedFile:
    rel_path: str
    reason: SkipReason
    detail: str = ""


@dataclass(frozen=True)
class IntakeEvent:
    kind: str
    detail: str = ""


@dataclass
class IntakeReport:
    session_hash: str = ""
    files: list[ParsedFile] = field(default_factory=list)
    skipped: list[SkippedFile] = field(default_factory=list)
    commits: list[CommitFact] = field(default_factory=list)
    changes: list[FileChangeFact] = field(default_factory=list)
    authors: list[AuthorRecord] = field(default_factory=list)
    human_author_count: int = 0
    bot_author_count: int = 0
    rename_events: int = 0
    has_git: bool = False
    branch: str | None = None
    is_shallow: bool = False
    total_commits: int = 0
    partial_history: bool = False
    duration_ms: int = 0
    events: list[IntakeEvent] = field(default_factory=list)

    @property
    def parsed_count(self) -> int:
        return len(self.files)

    def summary(self) -> dict[str, object]:
        by_lang: dict[str, int] = {}
        for f in self.files:
            by_lang[f.language] = by_lang.get(f.language, 0) + 1
        return {
            "session": self.session_hash,
            "parsed": self.parsed_count,
            "skipped": len(self.skipped),
            "languages": dict(sorted(by_lang.items())),
            "commits": len(self.commits),
            "changes": len(self.changes),
            "authors_human": self.human_author_count,
            "authors_bots": self.bot_author_count,
            "renames_linked": self.rename_events,
            "branch": self.branch,
            "partial_history": self.partial_history,
            "classes": dict(sorted(_class_hist(self.files).items())),
            "has_git": self.has_git,
            "duration_ms": self.duration_ms,
        }


def _class_hist(files):
    hist: dict[str, int] = {}
    for f in files:
        key = getattr(f.file_class, "value", str(f.file_class))
        hist[key] = hist.get(key, 0) + 1
    return hist


class IntakeService:
    """Sequences the acquisition DAG; owns no analysis logic."""

    def __init__(self, parser_manager: ParserManager | None = None) -> None:
        self._parsers = parser_manager or ParserManager()

    def run(self, config: IntakeConfig) -> IntakeReport:
        started = time.monotonic()
        report = IntakeReport()
        root = Path(config.root)

        ctx = s0_session_context(
            root=root,
            exclude_patterns=config.exclude_patterns,
            max_file_size_mb=config.max_file_size_mb,
            allow_hidden=config.allow_hidden,
            follow_symlinks=config.follow_symlinks,
            max_files=config.max_files,
            max_commits=config.max_commits,
            use_git=config.use_git,
        )
        report.session_hash = ctx.config_hash

        disc_cfg = DiscoveryConfig(
            exclude_patterns=config.exclude_patterns or DiscoveryConfig().exclude_patterns,
            respect_gitignore=config.respect_gitignore,
            max_file_size_mb=config.max_file_size_mb,
            allow_hidden=config.allow_hidden,
            follow_symlinks=config.follow_symlinks,
        )

        paths = g1_candidate_paths(root, disc_cfg)
        if len(paths) > config.max_files:
            report.events.append(IntakeEvent("repo_too_large", str(len(paths))))
            raise ShannonError(
                message=f"file count {len(paths)} exceeds cap {config.max_files}",
                code=ErrorCode.FACTS_REPO_TOO_LARGE,
                recoverable=True,
                recovery_hint="raise [files].max_files or tighten exclude_patterns",
            )
        report.events.append(IntakeEvent("files_discovered", str(len(paths))))

        cap_bytes = int(config.max_file_size_mb * 1024 * 1024)
        for path in paths:
            rel = path.relative_to(root).as_posix()
            content, skip_detail = h1_read_capped(path, cap_bytes)
            if content is None:
                reason = (
                    SkipReason.TOO_LARGE if skip_detail.startswith("too_large") else SkipReason.READ_ERROR
                )
                report.skipped.append(SkippedFile(rel, reason, skip_detail))
                continue
            file_class = classify(rel).file_class
            if file_class in (FileClass.DOC, FileClass.DATA):
                report.skipped.append(SkippedFile(rel, SkipReason.UNPARSEABLE_CLASS, file_class.value))
                continue
            try:
                syntax = p0_parse_unit(rel, content, self._parsers)
            except Exception as exc:  # per-item isolation (FM-25 gate keeps this narrow)
                report.skipped.append(SkippedFile(rel, SkipReason.PARSE_ERROR, repr(exc)[:160]))
                continue
            report.files.append(
                ParsedFile(
                    rel_path=rel,
                    content_hash=h2_content_hash(content),
                    language=syntax.language,
                    syntax=syntax,
                    file_class=file_class,
                )
            )
        report.events.append(IntakeEvent("files_parsed", str(len(report.files))))

        report.has_git = config.use_git and x1_has_git(root)
        if report.has_git:
            gctx = git_context(root, max_commits=config.max_commits)
            if gctx is not None:
                report.branch = gctx.branch
                report.is_shallow = gctx.is_shallow
                report.total_commits = gctx.total_commits
                report.partial_history = gctx.partial_history or gctx.is_shallow
                if gctx.partial_history:
                    report.events.append(
                        IntakeEvent("partial_history", f"{gctx.analyzed_commits}/{gctx.total_commits}")
                    )
            try:
                commits, changes = x2_extract_streams(root, config.max_commits)
            except (subprocess.TimeoutExpired, OSError) as exc:
                report.has_git = False
                report.events.append(IntakeEvent("git_degraded", repr(exc)[:120]))
                report.duration_ms = int((time.monotonic() - started) * 1000)
                report.events.append(IntakeEvent("intake_completed", ""))
                return report

            mailmap_path = root / ".mailmap"
            mailmap_content = (
                mailmap_path.read_text(encoding="utf-8", errors="replace")
                if mailmap_path.exists()
                else None
            )
            commits, author_records = a0_canonicalize_authors(commits, mailmap_content)

            view: IdentityView = i0_resolve_identity(commits, changes)
            report.files, stamped_changes = j0_join(report.files, changes, view)
            report.changes = stamped_changes
            report.commits = commits
            report.authors = author_records
            report.human_author_count = sum(1 for a in author_records if not a.is_bot)
            report.bot_author_count = sum(1 for a in author_records if a.is_bot)
            report.rename_events = view.stats["renames"]
            report.events.append(IntakeEvent("git_extracted", str(len(commits))))
            report.events.append(IntakeEvent("identities_resolved", str(view.stats["renames"])))
        else:
            view = i0b_resolve_offline(sorted(f.rel_path for f in report.files))
            report.files = [
                replace(f, file_id=view.path_to_id.get(f.rel_path)) for f in report.files
            ]
            report.events.append(IntakeEvent("identities_session_scoped", str(len(report.files))))

        report.duration_ms = int((time.monotonic() - started) * 1000)
        report.events.append(IntakeEvent("intake_completed", ""))
        return report


__all__ = [
    "IntakeConfig",
    "IntakeEvent",
    "IntakeReport",
    "IntakeService",
    "ParsedFile",
    "SkipReason",
    "SkippedFile",
]
