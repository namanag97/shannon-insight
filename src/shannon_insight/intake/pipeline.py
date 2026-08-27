"""Phase-1 acquisition pipeline: explicit fine-grained DAG nodes.

Each node is a named, pure-or-isolated unit with one domain responsibility.
Orchestration lives in IntakeService; composition order is the contract.

    STRUCTURAL SPINE                     TEMPORAL SPINE
    S0 session_context                   X1 has_git
    G1 candidate_paths                   X2 extract_streams
       (walk ∧ exclude ∧ detect)         X4 merge_numstat      (inside X2)
    H1 read_capped                       A0 canonicalize_authors
    H2 content_hash                         (mailmap → normalize →
    P0 parse_unit                            alias-merge → bot-flag)
       (bundle fast-path |               I0 resolve_identity
        Walker: scan→walk→imports           (order-invariant input!)
        →exports→metrics)                ═══ JOIN ═══
                                        J1 stamp_files · J2 stamp_changes ·
                                        J3 churn_rollup
                                        R0 assemble_report
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from pathlib import Path

from shannon_insight.facts.authors import AuthorRecord
from shannon_insight.facts.discovery import DiscoveryConfig, discover
from shannon_insight.facts.git_extractor import extract_git_facts
from shannon_insight.facts.identity import FileChange, FileIdentityResolver
from shannon_insight.facts.models import ChangeType, CommitFact, FileChangeFact
from shannon_insight.syntax.models import FileSyntax
from shannon_insight.syntax.parser import ParserManager, analyze_source

# ── S0 session ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SessionContext:
    root: Path
    config_hash: str
    mode: str = "FULL"


def s0_session_context(
    root: str | Path,
    exclude_patterns: tuple[str, ...],
    max_file_size_mb: float,
    allow_hidden: bool,
    follow_symlinks: bool,
    max_files: int,
    max_commits: int,
    use_git: bool,
) -> SessionContext:
    """Canonicalize inputs into one hashed context. Pure."""
    canonical = "|".join(
        [
            str(Path(root).resolve()),
            ",".join(sorted(exclude_patterns or DiscoveryConfig().exclude_patterns)),
            f"size={max_file_size_mb}",
            f"hidden={allow_hidden}",
            f"symlink={follow_symlinks}",
            f"maxfiles={max_files}",
            f"maxcommits={max_commits}",
            f"git={use_git}",
        ]
    )
    return SessionContext(
        root=Path(root).resolve(), config_hash=hashlib.sha256(canonical.encode()).hexdigest()[:16]
    )


# ── Structural spine ──────────────────────────────────────────────────────


def g1_candidate_paths(root: Path, cfg: DiscoveryConfig) -> list[Path]:
    """G1: walk ∧ gitwildmatch-exclude ∧ language-detect. Deterministic sort."""
    return sorted(discover(root, cfg))


def h1_read_capped(path: Path, cap_bytes: int) -> tuple[bytes | None, str]:
    """H1/H2 fused IO node: size-guard then read. Returns (content|None, skip_detail)."""
    try:
        size = path.stat().st_size
        if size > cap_bytes:
            return None, f"too_large:{size}"
        return path.read_bytes(), ""
    except OSError as exc:
        return None, f"read_error:{exc!r}"[:160]


def h2_content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def p0_parse_unit(
    rel_path: str,
    content: bytes,
    manager: ParserManager,
) -> FileSyntax:
    """P0: bundle fast-path or full Walker pass (scan→walk→imports→exports→metrics)."""
    return analyze_source(rel_path, content, manager=manager)


# ── Temporal spine ────────────────────────────────────────────────────────


def x1_has_git(root: Path) -> bool:
    return (root / ".git").exists()


def x2_extract_streams(
    root: Path, max_commits: int, timeout_seconds: int = 30
) -> tuple[list[CommitFact], list[FileChangeFact]]:
    """X2+X4: two git passes merged per-hash; OLDEST-FIRST output."""
    return extract_git_facts(root, max_commits=max_commits, timeout_seconds=timeout_seconds)


def a0_canonicalize_authors(
    commits: list[CommitFact], mailmap_content: str | None
) -> tuple[list[CommitFact], list[AuthorRecord]]:
    return canonicalize_authors_impl(commits, mailmap_content)


def canonicalize_authors_impl(
    commits: list[CommitFact], mailmap_content: str | None
) -> tuple[list[CommitFact], list[AuthorRecord]]:
    from shannon_insight.facts.git_extractor import canonicalize_authors

    return canonicalize_authors(commits, mailmap_content)


class IdentityView:
    """I0 result: alive path→id map plus chain statistics."""

    def __init__(self, resolver: FileIdentityResolver) -> None:
        self._resolver = resolver
        self.path_to_id: dict[str, str] = dict(resolver._path_to_id)
        self.stats = resolver.stats()

    def changes_per_id(self, changes: list[FileChangeFact]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for chg in changes:
            fid = self.path_to_id.get(chg.new_path or chg.old_path or "")
            if fid:
                counts[fid] = counts.get(fid, 0) + 1
        return counts


def i0_resolve_identity(commits: list[CommitFact], changes: list[FileChangeFact]) -> IdentityView:
    """I1+I2+I3: feed resolver strictly oldest-first (its ORDER INVARIANT)."""
    conn_conn = __import__("sqlite3").connect(":memory:")
    resolver = FileIdentityResolver(conn_conn)
    by_hash: dict[str, list[FileChangeFact]] = {}
    for chg in changes:
        by_hash.setdefault(chg.commit_hash, []).append(chg)
    for commit in commits:  # commits arrive oldest-first
        for chg in by_hash.get(commit.commit_hash, []):
            resolver.process_change(
                commit.commit_hash,
                commit.timestamp,
                FileChange(
                    commit_hash=commit.commit_hash,
                    path=chg.new_path or chg.old_path or "",
                    change_type=chg.change_type,
                    old_path=chg.old_path,
                ),
            )
    resolver.commit()
    return IdentityView(resolver)


def i0b_resolve_offline(paths_sorted: list[str]) -> IdentityView:
    """I0b: session-scoped identities when no git history exists.

    Each path becomes an implicit ADD fed oldest-first (sorted-path order),
    so downstream phases get a non-empty file_id per ParsedFile.
    """
    conn_conn = __import__("sqlite3").connect(":memory:")
    resolver = FileIdentityResolver(conn_conn)
    for seq, path in enumerate(paths_sorted):
        marker = f"session:{seq:08d}"
        resolver.process_change(
            marker,
            seq,
            FileChange(commit_hash=marker, path=path, change_type=ChangeType.ADDED),
        )
    resolver.commit()
    return IdentityView(resolver)


# ── Join ──────────────────────────────────────────────────────────────────


def j0_join(files: list, changes: list[FileChangeFact], view: IdentityView):
    """J1+J2+J3: stamp ids onto both artifact families + churn rollup."""
    churn = view.changes_per_id(changes)
    stamped_files = [
        replace(
            f,
            file_id=view.path_to_id.get(f.rel_path),
            total_changes=churn.get(view.path_to_id.get(f.rel_path, ""), 0),
        )
        for f in files
    ]
    stamped_changes = [
        replace(c, file_id=view.path_to_id.get(c.new_path or c.old_path or "", "")) for c in changes
    ]
    return stamped_files, stamped_changes


__all__ = [
    "IdentityView",
    "SessionContext",
    "a0_canonicalize_authors",
    "g1_candidate_paths",
    "h1_read_capped",
    "h2_content_hash",
    "i0_resolve_identity",
    "i0b_resolve_offline",
    "j0_join",
    "p0_parse_unit",
    "s0_session_context",
    "x1_has_git",
    "x2_extract_streams",
]
