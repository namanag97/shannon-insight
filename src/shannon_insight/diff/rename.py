"""Git rename detection — uses `git diff --name-status -M` between two commits."""

import logging
import subprocess
from typing import Dict

logger = logging.getLogger(__name__)


def detect_renames(
    repo_path: str,
    old_commit: str,
    new_commit: str,
) -> Dict[str, str]:
    """Detect file renames between two commits using git.

    Runs ``git diff --name-status -M <old> <new>`` and parses lines that
    start with 'R' (rename).  Each such line has the format::

        R<similarity>\told_path\tnew_path

    Args:
        repo_path: Filesystem path to the git repository root.
        old_commit: The older commit SHA (or ref).
        new_commit: The newer commit SHA (or ref).

    Returns:
        A dict mapping ``{old_path: new_path}`` for every detected rename.
        Returns an empty dict if git is unavailable or the command fails.
    """
    try:
        result = subprocess.run(
            [
                "git", "diff",
                "--name-status",
                "-M",  # enable rename detection
                old_commit,
                new_commit,
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            logger.warning(
                "git diff --name-status failed (rc=%d): %s",
                result.returncode,
                result.stderr.strip(),
            )
            return {}

        renames: Dict[str, str] = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 3:
                continue

            status = parts[0]
            # Rename lines start with 'R' followed by a similarity percentage
            # e.g. "R100", "R085"
            if status.startswith("R"):
                old_path = parts[1]
                new_path = parts[2]
                renames[old_path] = new_path
                logger.debug("Detected rename: %s -> %s", old_path, new_path)

        if renames:
            logger.info("Detected %d file rename(s)", len(renames))

        return renames

    except FileNotFoundError:
        logger.warning("git executable not found — rename detection unavailable")
        return {}
    except subprocess.TimeoutExpired:
        logger.warning("git diff timed out — rename detection unavailable")
        return {}
    except Exception as exc:
        logger.warning("Rename detection failed: %s", exc)
        return {}
