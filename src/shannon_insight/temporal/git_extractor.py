"""Extract git history via subprocess."""

import re
import subprocess
from pathlib import Path
from typing import Optional

from ..logging_config import get_logger
from .models import Commit, GitHistory

logger = get_logger(__name__)


class GitExtractor:
    """Parse git log into structured GitHistory."""

    def __init__(self, repo_path: str, max_commits: int = 5000):
        self.repo_path = str(Path(repo_path).resolve())
        self.max_commits = max_commits

    def extract(self) -> Optional[GitHistory]:
        """Parse git log via subprocess. Return None if not a git repo."""
        if not self._is_git_repo():
            logger.info("Not a git repository — skipping temporal analysis")
            return None

        raw = self._run_git_log()
        if raw is None:
            return None

        commits = self._parse_log(raw)
        if not commits:
            return None

        file_set = set()
        for c in commits:
            file_set.update(c.files)

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

    def _is_git_repo(self) -> bool:
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

    def _run_git_log(self) -> Optional[str]:
        try:
            cmd = [
                "git",
                "-C",
                self.repo_path,
                "log",
                "--format=%H|%at|%ae",
                "--name-only",
                f"-n{self.max_commits}",
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                logger.warning(f"git log failed: {result.stderr.strip()}")
                return None
            return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"git log error: {e}")
            return None

    # Matches: 40-char hex hash | unix timestamp | author email
    _HEADER_RE = re.compile(r"^[0-9a-f]{40}\|\d+\|.+$")

    def _parse_log(self, raw: str) -> list:
        """Parse git log output into Commit objects.

        Handles merge commits (no files) and consecutive headers correctly
        by detecting header lines via regex rather than relying on blank-line
        separation.
        """
        commits = []
        current_hash = None
        current_ts = 0
        current_author = ""
        current_files = []

        for line in raw.split("\n"):
            line = line.strip()
            if not line:
                continue

            if self._HEADER_RE.match(line):
                # Flush previous commit
                if current_hash and current_files:
                    commits.append(
                        Commit(
                            hash=current_hash,
                            timestamp=current_ts,
                            author=current_author,
                            files=current_files,
                        )
                    )

                parts = line.split("|", 2)
                current_hash = parts[0]
                try:
                    current_ts = int(parts[1])
                except ValueError:
                    current_hash = None
                    continue
                current_author = parts[2]
                current_files = []
            elif current_hash:
                # This is a file path belonging to the current commit
                current_files.append(line)

        # Flush last commit
        if current_hash and current_files:
            commits.append(
                Commit(
                    hash=current_hash,
                    timestamp=current_ts,
                    author=current_author,
                    files=current_files,
                )
            )

        return commits
