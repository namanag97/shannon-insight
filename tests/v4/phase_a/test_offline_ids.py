"""Offline identity synthesis: no .git → session-scoped UUIDs for every ParsedFile."""

from __future__ import annotations

import subprocess
from pathlib import Path

from shannon_insight.intake.pipeline import i0b_resolve_offline
from shannon_insight.intake.service import IntakeConfig, IntakeService


def _write_corpus(root: Path) -> None:
    (root / "a.py").write_text("def one():\n    return 1\n")
    (root / "zz.py").write_text("def two():\n    return 2\n")
    sub = root / "sub"
    sub.mkdir()
    (sub / "b.py").write_text("def three():\n    return 3\n")


def _git(root: Path, *args: str) -> None:
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
    assert proc.returncode == 0, f"git {args} failed: {proc.stderr}"


class TestOfflineIdentities:
    def test_no_git_every_file_gets_unique_nonempty_id(self, tmp_path: Path):
        root = tmp_path / "plain"
        root.mkdir()
        _write_corpus(root)

        report = IntakeService().run(IntakeConfig(root=root))

        assert report.has_git is False
        assert len(report.files) == 3
        ids = [f.file_id for f in report.files]
        assert all(ids), "every ParsedFile needs a truthy file_id without git"
        assert len(set(ids)) == len(ids), "session-scoped ids must be unique"
        assert all(f.total_changes == 0 for f in report.files)
        scoped = [e for e in report.events if e.kind == "identities_session_scoped"]
        assert len(scoped) == 1
        assert scoped[0].detail == "3"

    def test_i0b_node_covers_all_paths(self):
        view = i0b_resolve_offline(["z.py", "a.py", "m.py"])
        assert set(view.path_to_id) == {"z.py", "a.py", "m.py"}
        assert all(view.path_to_id.values())
        assert len(set(view.path_to_id.values())) == 3
        assert view.stats["alive"] == 3
        assert view.stats["renames"] == 0

    def test_use_git_on_repo_ids_still_resolve(self, tmp_path: Path):
        root = tmp_path / "repo"
        root.mkdir()
        _write_corpus(root)
        _git(root, "init", "-q")
        _git(root, "add", ".")
        _git(root, "commit", "-qm", "initial add")

        report = IntakeService().run(IntakeConfig(root=root))

        assert report.has_git is True
        assert len(report.files) == 3
        ids = [f.file_id for f in report.files]
        assert all(ids)
        assert len(set(ids)) == len(ids)
        assert not any(e.kind == "identities_session_scoped" for e in report.events)

    def test_summary_keys_unchanged_offline(self, tmp_path: Path):
        root = tmp_path / "plain2"
        root.mkdir()
        _write_corpus(root)

        report = IntakeService().run(IntakeConfig(root=root))
        summary = report.summary()

        expected = {
            "session",
            "parsed",
            "skipped",
            "languages",
            "commits",
            "changes",
            "authors_human",
            "authors_bots",
            "renames_linked",
            "branch",
            "partial_history",
            "classes",
            "has_git",
            "duration_ms",
        }
        assert set(summary) == expected
        assert summary["has_git"] is False
        assert summary["parsed"] == 3
