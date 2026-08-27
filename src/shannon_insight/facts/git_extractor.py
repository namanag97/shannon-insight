"""Git fact extraction (Phase 1 acquisition spine).

Produces immutable CommitFact / FileChangeFact streams from `git log`, with
rename detection (-M). Two subprocess passes keyed by commit hash: one
--name-status (statuses incl. renames), one --numstat (additions/deletions).

Contract: output is OLDEST-FIRST and deterministic for a given repo state.
"""

from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path

from shannon_insight.facts.models import ChangeType, CommitFact, FileChangeFact
from shannon_insight.facts.authors import AuthorRecord, AuthorResolver

_SEP = "\x1f"

_FIX_WORDS = ("fix", "bug", "patch", "hotfix", "resolve", "repair", "issue")
_REFACTOR_WORDS = ("refactor", "restructure", "reorganize", "clean", "simplify")


def classify_intent(subject: str) -> str:
    s = subject.lower()
    if any(w in s for w in _FIX_WORDS):
        return "fix"
    if any(w in s for w in _REFACTOR_WORDS):
        return "refactor"
    return "other"


def _run_git(root: str, args: list[str], timeout_seconds: int) -> str:
    proc = subprocess.run(
        ["git", "-C", root, *args],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    return proc.stdout


def _git0(root: str, args: list[str], timeout_seconds: int) -> str:
    return _run_git(root, args, timeout_seconds)


def git_context(root, max_commits=5000, timeout_seconds=30):
    """X0a: branch/shallow/depth context. Pure read; degrades gracefully."""
    from dataclasses import dataclass as _dc

    @_dc(frozen=True)
    class GitContext:
        branch: str | None
        is_shallow: bool
        total_commits: int
        analyzed_commits: int
        partial_history: bool

    root_str = str(root)
    try:
        branch = _git0(root_str, ["rev-parse", "--abbrev-ref", "HEAD"], timeout_seconds).strip()
        shallow = _git0(root_str, ["rev-parse", "--is-shallow-repository"], timeout_seconds).strip() == "true"
        total_s = _git0(root_str, ["rev-list", "--count", "HEAD"], timeout_seconds).strip()
        total = int(total_s) if total_s.isdigit() else 0
    except (subprocess.TimeoutExpired, OSError):
        return None
    analyzed = min(total, max_commits) if total else 0
    return GitContext(
        branch=branch or None,
        is_shallow=shallow,
        total_commits=total,
        analyzed_commits=analyzed,
        partial_history=bool(total and analyzed < total),
    )


def extract_git_facts(
    root: str | Path,
    max_commits: int = 5000,
    timeout_seconds: int = 30,
) -> tuple[list[CommitFact], list[FileChangeFact]]:
    """Return (commits oldest-first, changes oldest-first)."""
    root_str = str(root)
    fmt = _SEP.join(["%H", "%at", "%ae", "%an", "%s", "%P"])
    limit = f"--max-count={max_commits}"

    status_out = _run_git(
        root_str,
        ["log", limit, "--date=unix", f"--format={fmt}", "--name-status", "-M"],
        timeout_seconds,
    )
    numstat_out = _run_git(
        root_str,
        ["log", limit, "--date=unix", f"--format={fmt}", "--numstat"],
        timeout_seconds,
    )

    commits: list[CommitFact] = []
    changes: list[FileChangeFact] = []
    current_hash: str | None = None
    current_changes: list[tuple[ChangeType, str | None, str | None]] = []

    def flush() -> None:
        nonlocal current_hash, current_changes
        if current_hash is None:
            return
        commit = next((c for c in commits if c.commit_hash == current_hash), None)
        if commit is not None:
            for ct, old, new in current_changes:
                changes.append(
                    FileChangeFact(
                        commit_hash=current_hash,
                        file_id="",
                        change_type=ct,
                        old_path=old,
                        new_path=new,
                        additions=None,
                        deletions=None,
                    )
                )
        current_hash = None
        current_changes = []

    for line in status_out.splitlines():
        parts = line.split(_SEP)
        if len(parts) == 6:
            flush()
            h, ts, email, name, subject, parents = parts
            current_hash = h
            parents_list = tuple(p for p in parents.split() if p)
            commits.append(
                CommitFact(
                    commit_hash=h,
                    timestamp=int(ts) if ts.isdigit() else 0,
                    author_id=email.strip().lower(),
                    author_email_raw=email.strip(),
                    author_name_raw=name.strip(),
                    message_subject=subject,
                    message_body=None,
                    parent_hashes=parents_list,
                    is_merge=len(parents_list) > 1,
                )
            )
            continue
        if current_hash is None or not line.strip():
            continue

        status, _, rest = line.partition("\t")
        code = status[:1]
        try:
            ct = ChangeType(code)
        except ValueError:
            continue
        fields = rest.split("\t") if rest else []
        if ct is ChangeType.RENAMED and len(fields) >= 2:
            old_path, new_path = fields[0], fields[-1]
        elif ct is ChangeType.DELETED and fields and fields[0]:
            old_path, new_path = fields[0], None
        else:
            old_path = None
            new_path = fields[0] if fields and fields[0] else None
        if not old_path and not new_path:
            continue
        current_changes.append((ct, old_path, new_path))

    flush()

    # Merge numstat additions/deletions by (hash, path).
    adds = _parse_numstat_stream(numstat_out)
    enriched: list[FileChangeFact] = []
    for ch in changes:
        key = ch.new_path or ch.old_path or ""
        add, dele = adds.get(ch.commit_hash, {}).get(key, (None, None))
        enriched.append(replace(ch, additions=add, deletions=dele))

    commits.reverse()
    enriched.reverse()
    return commits, enriched


def canonicalize_authors(
    commits: list[CommitFact],
    mailmap_content: str | None = None,
) -> tuple[list[CommitFact], list[AuthorRecord]]:
    """Rewrite author_id on every commit to the canonical id; return records."""
    resolver = AuthorResolver()
    if mailmap_content:
        resolver.load_mailmap(mailmap_content)

    out: list[CommitFact] = []
    seen_ids: dict[str, str] = {}
    for c in commits:
        record = resolver.resolve(c.author_name_raw, c.author_email_raw)
        seen_ids[c.author_email_raw] = record.author_id
        out.append(replace(c, author_id=record.author_id))

    records = {r.author_id: r for r in resolver.records()}
    return out, [records[i] for i in sorted(seen_ids.values())]


def _parse_numstat_stream(stream: str) -> dict[str, dict[str, tuple[int | None, int | None]]]:
    result: dict[str, dict[str, tuple[int | None, int | None]]] = {}
    current: str | None = None
    for line in stream.splitlines():
        parts = line.split(_SEP)
        if len(parts) == 6:
            current = parts[0]
            result.setdefault(current, {})
            continue
        if current is None or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) < 3:
            continue
        add_s, del_s, path = cols[0], cols[1], cols[2]
        add = int(add_s) if add_s.isdigit() else None
        dele = int(del_s) if del_s.isdigit() else None
        result[current][path] = (add, dele)
    return result


__all__ = ["classify_intent", "extract_git_facts", "canonicalize_authors"]
