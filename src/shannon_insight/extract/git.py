"""Git history extraction."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .models import Commit, FileChange, GitHistory


def extract_git_history(repo_path: Path, max_commits: int = 10000) -> GitHistory:
    """Extract commits and file changes from git repository."""
    commits = _parse_commits(repo_path, max_commits)
    changes = _parse_changes(repo_path, max_commits)
    return GitHistory(commits=commits, changes=changes)


def _parse_commits(repo_path: Path, max_commits: int) -> list[Commit]:
    """Parse git log for commit metadata."""
    cmd = [
        "git",
        "-C",
        str(repo_path),
        "log",
        f"-n{max_commits}",
        "--format=%H|%at|%ae|%s",
        "--name-only",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    commits = []
    current_hash = None
    current_ts = 0
    current_author = ""
    current_subject = ""
    current_files: list[str] = []

    for line in result.stdout.strip().split("\n"):
        if "|" in line and line.count("|") == 3:
            # Save previous commit
            if current_hash:
                commits.append(
                    Commit(
                        hash=current_hash,
                        timestamp=current_ts,
                        author=current_author,
                        subject=current_subject,
                        files=tuple(current_files),
                    )
                )

            # Parse new commit
            parts = line.split("|", 3)
            current_hash = parts[0]
            current_ts = int(parts[1]) if parts[1].isdigit() else 0
            current_author = parts[2]
            current_subject = parts[3]
            current_files = []
        elif line.strip():
            current_files.append(line.strip())

    # Save last commit
    if current_hash:
        commits.append(
            Commit(
                hash=current_hash,
                timestamp=current_ts,
                author=current_author,
                subject=current_subject,
                files=tuple(current_files),
            )
        )

    return commits


def _parse_changes(repo_path: Path, max_commits: int) -> list[FileChange]:
    """Parse git log --numstat for file changes."""
    cmd = [
        "git",
        "-C",
        str(repo_path),
        "log",
        f"-n{max_commits}",
        "--format=%H",
        "--numstat",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    changes = []
    current_hash = ""

    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
            current_hash = line
        elif "\t" in line and current_hash:
            parts = line.split("\t")
            if len(parts) >= 3:
                add_str, del_str, path = parts[0], parts[1], parts[2]
                additions = int(add_str) if add_str.isdigit() else 0
                deletions = int(del_str) if del_str.isdigit() else 0
                changes.append(
                    FileChange(
                        commit_hash=current_hash,
                        path=path,
                        change_type="M",
                        additions=additions,
                        deletions=deletions,
                    )
                )

    return changes
