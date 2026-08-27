"""Phase-A test fixtures: programmatic git repos (FRESH-BUILD conftest pattern)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _git(root: Path, *args: str) -> str:
    env = {
        "GIT_AUTHOR_NAME": "Alice",
        "GIT_AUTHOR_EMAIL": "alice@example.com",
        "GIT_COMMITTER_NAME": "Alice",
        "GIT_COMMITTER_EMAIL": "alice@example.com",
        "HOME": str(root),
    }
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {args} failed: {proc.stderr}")
    return proc.stdout.strip()


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Repo history: add -> fix-modify -> rename -> bot-commit."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")

    (root / "a.py").write_text("def one():\n    return 1\n")
    (root / "b.py").write_text("def two():\n    return 2\n")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "initial add")

    (root / "a.py").write_text("def one():\n    return 11\n")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "fix: correct one() result")

    _git(root, "mv", "b.py", "c.py")
    _git(root, "commit", "-qm", "rename b to c")

    env_bot = dict(_BOT_ENV)
    proc = subprocess.run(
        ["git", "-C", str(root), "commit", "--allow-empty", "-qm", "chore: bump"],
        capture_output=True,
        text=True,
        env={
            **env_bot,
            "HOME": str(root),
            "GIT_AUTHOR_NAME": "dependabot[bot]",
            "GIT_AUTHOR_EMAIL": "bot@github.com",
            "GIT_COMMITTER_NAME": "dependabot[bot]",
            "GIT_COMMITTER_EMAIL": "bot@github.com",
        },
        check=False,
    )
    assert proc.returncode == 0
    return root


_BOT_ENV = {}
