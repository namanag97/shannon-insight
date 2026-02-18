"""Backward compatibility utilities for temporal module.

Provides conversion between new GitRawData and old GitHistory
to maintain API compatibility during the transition.
"""

from __future__ import annotations

from collections import defaultdict

from ..persistence.git_models import GitRawData
from .models import Commit, GitHistory


def raw_data_to_history(data: GitRawData) -> GitHistory:
    """Convert GitRawData to GitHistory for backward compatibility.

    The old GitHistory format groups files by commit, while GitRawData
    stores them separately. This reconstructs the old format.

    Args:
        data: GitRawData from GitRawExtractor

    Returns:
        GitHistory compatible with existing code
    """
    # Group file changes by commit
    files_by_commit: dict[str, list[str]] = defaultdict(list)
    for fc in data.file_changes:
        files_by_commit[fc.commit_hash].append(fc.file_path)

    # Build Commit objects (preserving original order - newest first)
    commits = []
    for gc in data.commits:
        commits.append(
            Commit(
                hash=gc.hash,
                timestamp=gc.timestamp,
                author=gc.author_email,
                files=files_by_commit.get(gc.hash, []),
                subject=gc.subject,
            )
        )

    # Build file set
    file_set = {fc.file_path for fc in data.file_changes}

    # Calculate span days
    span_days = 0
    if len(commits) >= 2:
        newest = commits[0].timestamp
        oldest = commits[-1].timestamp
        span_days = max(1, (newest - oldest) // 86400)

    return GitHistory(
        commits=commits,
        file_set=file_set,
        span_days=span_days,
    )


__all__ = ["raw_data_to_history"]
