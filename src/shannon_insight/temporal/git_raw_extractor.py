"""Extract raw git data with --numstat for line counts.

This extractor captures the complete git data needed for temporal analysis:
- Commits with metadata (hash, timestamp, author, subject, parents)
- File changes with line counts (additions, deletions)
- Change types (A/M/D/R/C) and rename tracking

Designed for accuracy AND speed:
- Single git log call with all data
- Streaming parse to avoid OOM on huge repos
- Handles edge cases: merges, binaries, renames, unicode paths, pipes in subjects

Optional FactStore integration:
- When a FactStore is provided, the extractor resolves stable file identities
  across renames and stores commits + changes into the fact database.
- Commits are processed oldest-first for correct identity chain resolution.
- Without a FactStore, behavior is unchanged (backward compatible).
"""

from __future__ import annotations

import re
import subprocess
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from ..logging_config import get_logger
from ..persistence.git_models import (
    ChangeType,
    GitCommit,
    GitFileChange,
    GitRawData,
)

if TYPE_CHECKING:
    from ..facts.store import FactStore

logger = get_logger(__name__)

# Maximum git log output size (50MB) to prevent OOM on huge repos
_MAX_OUTPUT_BYTES = 50 * 1024 * 1024


class GitRawExtractor:
    """Extract raw git data with --numstat for line counts.

    Usage:
        extractor = GitRawExtractor("/path/to/repo")
        data = extractor.extract()  # GitRawData with commits + file_changes

    With FactStore (identity resolution + persistence):
        from shannon_insight.facts.store import FactStore
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/path/to/repo", fact_store=store)
        data = extractor.extract()
        # file_changes now have file_id set, and store has commits + identities

    Edge cases handled:
        - Merge commits (multiple parents)
        - Binary files (- - in numstat)
        - Renames/copies (-M -C flags)
        - Empty commits (no file changes)
        - Huge repos (50MB output limit)
        - Unicode paths
        - Pipe characters in subjects (maxsplit parsing)
    """

    def __init__(
        self,
        repo_path: str,
        max_commits: int = 10000,
        fact_store: FactStore | None = None,
    ):
        """Initialize extractor.

        Args:
            repo_path: Path to git repository
            max_commits: Maximum commits to extract (newest first)
            fact_store: Optional FactStore for identity resolution and
                        persistence. If None, identity resolution is skipped.
        """
        self.repo_path = str(Path(repo_path).resolve())
        self.max_commits = max_commits
        self.fact_store = fact_store

    def extract(self, since_sha: Optional[str] = None) -> Optional[GitRawData]:
        """Extract raw git data.

        When a FactStore is configured, commits are processed oldest-first
        for correct identity chain resolution. Each file change gets a
        stable ``file_id`` assigned, and commits + changes are persisted
        to the fact store.

        Args:
            since_sha: If provided, only extract commits after this SHA
                       (for incremental updates)

        Returns:
            GitRawData with commits and file_changes, or None if not a git repo
        """
        if not self._is_git_repo():
            logger.info("Not a git repository — skipping raw git extraction")
            return None

        head_sha = self._get_head_sha()
        if head_sha is None:
            return None

        raw = self._run_git_log(since_sha=since_sha)
        if raw is None:
            return None

        commits, file_changes = self._parse_log(raw)
        if not commits:
            return GitRawData(
                commits=[],
                file_changes=[],
                head_sha=head_sha,
                oldest_sha=None,
            )

        if self.fact_store is not None:
            self._resolve_identities(commits, file_changes)

        oldest_sha = commits[-1].hash if commits else None

        return GitRawData(
            commits=commits,
            file_changes=file_changes,
            head_sha=head_sha,
            oldest_sha=oldest_sha,
        )

    def _is_git_repo(self) -> bool:
        """Check if path is a git repository."""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _get_head_sha(self) -> Optional[str]:
        """Get current HEAD SHA."""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    def _run_git_log(self, since_sha: Optional[str] = None) -> Optional[str]:
        """Run git log with numstat.

        Format: COMMIT_START|hash|parents|timestamp|email|name|subject
        Then --numstat gives: additions\\tdeletions\\tpath
        With -M -C, renames show: additions\\tdeletions\\told_path => new_path
        """
        try:
            # Using COMMIT_START marker to unambiguously delimit commits
            # (handles subjects/bodies with arbitrary content)
            cmd = [
                "git",
                "-C",
                self.repo_path,
                "log",
                # Format: marker|hash|parents|timestamp|email|name|subject
                "--format=COMMIT_START|%H|%P|%at|%ae|%an|%s",
                "--numstat",  # additions deletions path
                "-M",  # detect renames
                "-C",  # detect copies
            ]

            if since_sha:
                # Incremental: commits after since_sha (exclusive)
                cmd.append(f"{since_sha}..HEAD")
            else:
                # Full history with limit
                cmd.append(f"-n{self.max_commits}")

            # Use Popen for streaming to avoid loading unbounded output
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                chunks = []
                total_size = 0
                stdout = proc.stdout
                if stdout is None:
                    return None

                while True:
                    chunk = stdout.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > _MAX_OUTPUT_BYTES:
                        logger.warning(
                            "git log output exceeded %dMB limit, truncating",
                            _MAX_OUTPUT_BYTES // (1024 * 1024),
                        )
                        proc.kill()
                        break
                    chunks.append(chunk)

                proc.wait(timeout=30)
                if proc.returncode not in (0, -9):  # -9 = killed
                    stderr = proc.stderr.read() if proc.stderr else ""
                    logger.warning("git log failed: %s", stderr.strip())
                    return None
                return "".join(chunks)
            finally:
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning("git log error: %s", e)
            return None

    # Regex for numstat line: additions<tab>deletions<tab>path
    # Binary files show as: -<tab>-<tab>path
    # Renames show as: adds<tab>dels<tab>old => new
    _NUMSTAT_RE = re.compile(r"^(\d+|-)\t(\d+|-)\t(.+)$")

    # Rename pattern: old_path => new_path (with optional {old => new} for partial renames)
    _RENAME_RE = re.compile(r"^(.+?)\s+=>\s+(.+)$")
    _RENAME_BRACE_RE = re.compile(r"^(.*)?\{(.+?) => (.+?)\}(.*)$")

    def _parse_log(self, raw: str) -> tuple[list[GitCommit], list[GitFileChange]]:
        """Parse git log output into commits and file changes.

        Handles:
        - COMMIT_START markers for reliable commit delimiting
        - numstat lines with additions/deletions
        - Binary files (- - in numstat)
        - Renames: old => new or prefix{old => new}suffix
        """
        commits: list[GitCommit] = []
        file_changes: list[GitFileChange] = []

        current_commit: Optional[GitCommit] = None

        for line in raw.split("\n"):
            line_stripped = line.rstrip()
            if not line_stripped:
                continue

            # Check for commit header
            if line_stripped.startswith("COMMIT_START|"):
                # Flush previous commit
                if current_commit is not None:
                    commits.append(current_commit)

                # Parse header: COMMIT_START|hash|parents|timestamp|email|name|subject
                # Use maxsplit=6 to handle subjects with | characters
                parts = line_stripped.split("|", 6)
                if len(parts) < 7:
                    current_commit = None
                    continue

                try:
                    timestamp = int(parts[3])
                except ValueError:
                    current_commit = None
                    continue

                parent_str = parts[2].strip()
                parent_hashes = tuple(parent_str.split()) if parent_str else ()

                current_commit = GitCommit(
                    hash=parts[1],
                    parent_hashes=parent_hashes,
                    timestamp=timestamp,
                    author_email=parts[4],
                    author_name=parts[5],
                    subject=parts[6] if len(parts) > 6 else "",
                )
                continue

            # Parse numstat line
            if current_commit is not None:
                match = self._NUMSTAT_RE.match(line_stripped)
                if match:
                    adds_str, dels_str, path_part = match.groups()

                    # Handle binary files (- -)
                    additions = None if adds_str == "-" else int(adds_str)
                    deletions = None if dels_str == "-" else int(dels_str)

                    # Check for rename
                    old_path = None
                    file_path = path_part
                    change_type = ChangeType.MODIFIED

                    # Try brace rename first: prefix{old => new}suffix
                    brace_match = self._RENAME_BRACE_RE.match(path_part)
                    if brace_match:
                        prefix, old_part, new_part, suffix = brace_match.groups()
                        old_path = f"{prefix or ''}{old_part}{suffix or ''}"
                        file_path = f"{prefix or ''}{new_part}{suffix or ''}"
                        change_type = ChangeType.RENAMED
                    else:
                        # Try simple rename: old => new
                        rename_match = self._RENAME_RE.match(path_part)
                        if rename_match:
                            old_path = rename_match.group(1).strip()
                            file_path = rename_match.group(2).strip()
                            change_type = ChangeType.RENAMED

                    file_changes.append(
                        GitFileChange(
                            commit_hash=current_commit.hash,
                            file_path=file_path,
                            additions=additions,
                            deletions=deletions,
                            change_type=change_type,
                            old_path=old_path,
                        )
                    )

        # Flush last commit
        if current_commit is not None:
            commits.append(current_commit)

        return commits, file_changes

    # ── FactStore identity resolution ──────────────────────────────────

    def _resolve_identities(
        self,
        commits: list[GitCommit],
        file_changes: list[GitFileChange],
    ) -> None:
        """Resolve stable file identities and persist to FactStore.

        Processes commits oldest-first for correct identity chain resolution.
        Each file change gets a stable ``file_id`` assigned. Commits and
        changes are stored in the fact database.

        Args:
            commits: Parsed commits (may be in any order).
            file_changes: Parsed file changes (parallel to commits via commit_hash).
        """
        assert self.fact_store is not None  # noqa: S101

        # Build commit_hash -> list[file_change_index] for fast lookup
        changes_by_commit: dict[str, list[int]] = {}
        for i, fc in enumerate(file_changes):
            changes_by_commit.setdefault(fc.commit_hash, []).append(i)

        # Process oldest-first for correct identity chains
        commits_oldest_first = sorted(commits, key=lambda c: c.timestamp)

        for commit in commits_oldest_first:
            # Store commit fact
            self.fact_store.store_commit(
                commit_hash=commit.hash,
                timestamp=commit.timestamp,
                author_email=commit.author_email,
                author_name=commit.author_name,
                message_subject=commit.subject,
                message_body=commit.body or None,
                parent_hashes=list(commit.parent_hashes),
                is_merge=commit.is_merge,
            )

            # Resolve identity for each file change in this commit
            for idx in changes_by_commit.get(commit.hash, []):
                change = file_changes[idx]
                file_id = self._resolve_single_identity(commit, change)
                change.file_id = file_id

                # Store file change fact in FactStore
                self.fact_store.store_file_change(
                    commit_hash=commit.hash,
                    file_id=file_id,
                    change_type=change.change_type.value,
                    old_path=change.old_path,
                    new_path=change.file_path,
                    additions=change.additions,
                    deletions=change.deletions,
                )

        self.fact_store.commit()

    def _resolve_single_identity(
        self,
        commit: GitCommit,
        change: GitFileChange,
    ) -> str:
        """Resolve the stable file identity for a single change.

        Dispatches to the appropriate handler based on change type:
        - ADDED/COPIED: register a new identity
        - RENAMED: transfer identity from old_path to new_path
        - DELETED: mark identity as dead
        - MODIFIED: look up existing identity (implicit ADD if missing)

        Args:
            commit: The commit containing this change.
            change: The file change to resolve.

        Returns:
            The stable file_id string.
        """
        assert self.fact_store is not None  # noqa: S101

        if change.change_type == ChangeType.ADDED:
            return self._identity_add(commit, change.file_path)

        elif change.change_type == ChangeType.COPIED:
            # Copy creates a new identity (not shared with source)
            return self._identity_add(commit, change.file_path)

        elif change.change_type == ChangeType.RENAMED:
            return self._identity_rename(commit, change)

        elif change.change_type == ChangeType.DELETED:
            return self._identity_delete(commit, change.file_path)

        else:  # MODIFIED
            return self._identity_modify(commit, change.file_path)

    def _identity_add(self, commit: GitCommit, file_path: str) -> str:
        """Handle ADD: register a new file identity.

        If the path already has a living identity (e.g., duplicate ADD in
        history), reuse it instead of creating a duplicate.
        """
        assert self.fact_store is not None  # noqa: S101

        # Check if already tracked (handles duplicate ADDs gracefully)
        existing = self.fact_store.resolve_file_id(file_path)
        if existing is not None:
            return existing

        file_id = str(uuid.uuid4())
        self.fact_store.register_file_identity(
            file_id=file_id,
            birth_commit=commit.hash,
            birth_path=file_path,
            current_path=file_path,
            is_alive=True,
        )
        return file_id

    def _identity_rename(self, commit: GitCommit, change: GitFileChange) -> str:
        """Handle RENAME: transfer identity from old_path to new_path.

        If old_path has no known identity (partial history), create a
        retroactive identity rooted at this commit.
        """
        assert self.fact_store is not None  # noqa: S101

        old_path = change.old_path
        new_path = change.file_path

        if old_path is None:
            # Malformed rename without old_path: treat as add
            logger.warning(
                "RENAME without old_path for %s in %s, treating as ADD",
                new_path,
                commit.hash,
            )
            return self._identity_add(commit, new_path)

        # Find existing identity for old_path
        file_id = self.fact_store.resolve_file_id(old_path)

        if file_id is None:
            # Partial history: old_path was never seen.
            # Create a retroactive identity with old_path as birth_path.
            file_id = str(uuid.uuid4())
            self.fact_store.register_file_identity(
                file_id=file_id,
                birth_commit=commit.hash,
                birth_path=old_path,
                current_path=old_path,
                is_alive=True,
            )

        # Update identity to point to new_path
        self.fact_store.update_file_path(
            file_id=file_id,
            new_path=new_path,
            timestamp=commit.timestamp,
            is_alive=True,
        )

        return file_id

    def _identity_delete(self, commit: GitCommit, file_path: str) -> str:
        """Handle DELETE: mark identity as dead.

        If the path has no known identity (partial history), create one
        retroactively so we have a record.
        """
        assert self.fact_store is not None  # noqa: S101

        file_id = self.fact_store.resolve_file_id(file_path)

        if file_id is None:
            # Partial history: never saw ADD for this file
            file_id = str(uuid.uuid4())
            self.fact_store.register_file_identity(
                file_id=file_id,
                birth_commit=commit.hash,
                birth_path=file_path,
                current_path=file_path,
                is_alive=True,
            )

        # Mark as dead (current_path=None, is_alive=False)
        self.fact_store.update_file_path(
            file_id=file_id,
            new_path=None,
            timestamp=commit.timestamp,
            is_alive=False,
        )

        return file_id

    def _identity_modify(self, commit: GitCommit, file_path: str) -> str:
        """Handle MODIFY: return existing identity.

        If the path has no identity (partial history / shallow clone),
        treat as an implicit ADD.
        """
        assert self.fact_store is not None  # noqa: S101

        file_id = self.fact_store.resolve_file_id(file_path)
        if file_id is not None:
            return file_id

        # Implicit ADD for partial history
        logger.debug(
            "MODIFY for unknown path %s (commit %s), treating as implicit ADD",
            file_path,
            commit.hash,
        )
        return self._identity_add(commit, file_path)


__all__ = ["GitRawExtractor"]
