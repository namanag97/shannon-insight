"""Tests for GitRawExtractor with --numstat parsing."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shannon_insight.persistence.git_models import ChangeType
from shannon_insight.temporal.git_raw_extractor import GitRawExtractor


@pytest.fixture
def git_repo() -> Path:
    """Create a real git repo with commits for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Initialize repo
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, capture_output=True)

        # Create initial commit
        (repo / "README.md").write_text("# Test Repo\n")
        subprocess.run(["git", "add", "README.md"], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, capture_output=True)

        # Add a Python file
        (repo / "main.py").write_text("def main():\n    print('hello')\n")
        subprocess.run(["git", "add", "main.py"], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add main.py"], cwd=repo, capture_output=True)

        # Modify the file
        (repo / "main.py").write_text("def main():\n    print('hello world')\n\nmain()\n")
        subprocess.run(["git", "add", "main.py"], cwd=repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Fix: update greeting"], cwd=repo, capture_output=True
        )

        yield repo


class TestGitRawExtractor:
    """Test suite for GitRawExtractor."""

    def test_extract_basic(self, git_repo: Path) -> None:
        """Test basic extraction from a real repo."""
        extractor = GitRawExtractor(str(git_repo))
        data = extractor.extract()

        assert data is not None
        assert data.head_sha is not None
        assert len(data.head_sha) == 40
        assert data.commit_count >= 3
        assert data.file_change_count >= 3

    def test_extract_not_git_repo(self) -> None:
        """Test extraction from non-git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            extractor = GitRawExtractor(tmpdir)
            data = extractor.extract()
            assert data is None

    def test_commits_have_metadata(self, git_repo: Path) -> None:
        """Test commits have all required fields."""
        extractor = GitRawExtractor(str(git_repo))
        data = extractor.extract()

        assert data is not None
        for commit in data.commits:
            assert len(commit.hash) == 40
            assert commit.timestamp > 0
            assert commit.author_email
            assert commit.author_name
            assert commit.subject

    def test_file_changes_have_line_counts(self, git_repo: Path) -> None:
        """Test file changes have additions/deletions."""
        extractor = GitRawExtractor(str(git_repo))
        data = extractor.extract()

        assert data is not None
        # Find a non-binary file change
        text_changes = [fc for fc in data.file_changes if not fc.is_binary]
        assert len(text_changes) > 0

        for fc in text_changes:
            assert fc.additions is not None
            assert fc.deletions is not None
            assert fc.additions >= 0
            assert fc.deletions >= 0

    def test_rename_detection(self, git_repo: Path) -> None:
        """Test rename detection with -M flag."""
        # Create a file and rename it
        (git_repo / "old.py").write_text("content\n")
        subprocess.run(["git", "add", "old.py"], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add old.py"], cwd=git_repo, capture_output=True)

        subprocess.run(["git", "mv", "old.py", "new.py"], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Rename old to new"], cwd=git_repo, capture_output=True)

        extractor = GitRawExtractor(str(git_repo))
        data = extractor.extract()

        assert data is not None
        # Find rename
        renames = [fc for fc in data.file_changes if fc.change_type == ChangeType.RENAMED]
        assert len(renames) >= 1

        rename = renames[0]
        assert rename.old_path == "old.py"
        assert rename.file_path == "new.py"


class TestParseLog:
    """Test the log parsing logic with mock data."""

    def test_parse_basic_commit(self) -> None:
        """Test parsing a simple commit with numstat."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa1111222233334444555566667777888899990000|bbbbccccddddeeee|1700000000|test@example.com|Test User|Add feature
10	5	src/main.py
3	0	tests/test_main.py
"""
        commits, changes = extractor._parse_log(raw)

        assert len(commits) == 1
        assert commits[0].hash == "aaaa1111222233334444555566667777888899990000"
        assert commits[0].timestamp == 1700000000
        assert commits[0].author_email == "test@example.com"
        assert commits[0].author_name == "Test User"
        assert commits[0].subject == "Add feature"

        assert len(changes) == 2
        assert changes[0].file_path == "src/main.py"
        assert changes[0].additions == 10
        assert changes[0].deletions == 5
        assert changes[1].file_path == "tests/test_main.py"
        assert changes[1].additions == 3
        assert changes[1].deletions == 0

    def test_parse_binary_file(self) -> None:
        """Test parsing binary file (- - in numstat)."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Add image
-	-	assets/logo.png
"""
        commits, changes = extractor._parse_log(raw)

        assert len(changes) == 1
        assert changes[0].is_binary
        assert changes[0].additions is None
        assert changes[0].deletions is None

    def test_parse_rename_simple(self) -> None:
        """Test parsing simple rename: old => new."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Rename file
5	3	old.py => new.py
"""
        commits, changes = extractor._parse_log(raw)

        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.RENAMED
        assert changes[0].old_path == "old.py"
        assert changes[0].file_path == "new.py"

    def test_parse_rename_brace(self) -> None:
        """Test parsing brace rename: prefix{old => new}suffix."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Rename file
5	3	src/{old => new}.py
"""
        commits, changes = extractor._parse_log(raw)

        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.RENAMED
        assert changes[0].old_path == "src/old.py"
        assert changes[0].file_path == "src/new.py"

    def test_parse_subject_with_pipe(self) -> None:
        """Test parsing subject with | character."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Fix auth | update deps
5	3	main.py
"""
        commits, changes = extractor._parse_log(raw)

        assert len(commits) == 1
        assert commits[0].subject == "Fix auth | update deps"

    def test_parse_merge_commit(self) -> None:
        """Test parsing merge commit with multiple parents."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb cccc|1700000000|test@example.com|Test|Merge branch
1	0	main.py
"""
        commits, changes = extractor._parse_log(raw)

        assert len(commits) == 1
        assert commits[0].is_merge
        assert len(commits[0].parent_hashes) == 2
        assert "bbbb" in commits[0].parent_hashes
        assert "cccc" in commits[0].parent_hashes

    def test_parse_empty_commit(self) -> None:
        """Test parsing commit with no file changes."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Empty commit
COMMIT_START|cccc|dddd|1700001000|test@example.com|Test|Another commit
5	3	main.py
"""
        commits, changes = extractor._parse_log(raw)

        # Both commits should be parsed
        assert len(commits) == 2
        # Only second commit has changes
        assert len(changes) == 1
        assert changes[0].commit_hash == "cccc"

    def test_parse_multiple_commits(self) -> None:
        """Test parsing multiple commits in sequence."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb|1700000000|alice@example.com|Alice|First commit
10	5	a.py

COMMIT_START|bbbb|cccc|1699999000|bob@example.com|Bob|Second commit
3	2	b.py
1	0	c.py
"""
        commits, changes = extractor._parse_log(raw)

        assert len(commits) == 2
        assert commits[0].author_email == "alice@example.com"
        assert commits[1].author_email == "bob@example.com"

        assert len(changes) == 3
        # First commit
        assert changes[0].commit_hash == "aaaa"
        assert changes[0].file_path == "a.py"
        # Second commit
        assert changes[1].commit_hash == "bbbb"
        assert changes[2].commit_hash == "bbbb"
