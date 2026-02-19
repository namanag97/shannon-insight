"""Tests for GitRawExtractor with --numstat parsing."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pytest

from shannon_insight.facts.store import FactStore
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
        subprocess.run(
            ["git", "commit", "-m", "Rename old to new"], cwd=git_repo, capture_output=True
        )

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


class TestIdentityResolution:
    """Test FactStore-based identity resolution in GitRawExtractor."""

    def test_add_assigns_identity(self) -> None:
        """ADD assigns a stable file_id via FactStore."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        raw = """COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Add file
10	0	src/main.py
"""
        commits, changes = extractor._parse_log(raw)
        extractor._resolve_identities(commits, changes)

        # file_id should be assigned
        assert changes[0].file_id is not None
        assert len(changes[0].file_id) == 36  # UUID format

        # FactStore should know about this identity
        resolved = store.resolve_file_id("src/main.py")
        assert resolved == changes[0].file_id

        # Identity record should exist
        identity = store.get_file_identity(changes[0].file_id)
        assert identity is not None
        assert identity["birth_path"] == "src/main.py"
        assert identity["current_path"] == "src/main.py"
        assert identity["is_alive"] is True

    def test_rename_preserves_identity(self) -> None:
        """RENAME transfers identity from old_path to new_path."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        # Commit 1: add file (older timestamp)
        # Commit 2: rename file (newer timestamp)
        raw = """COMMIT_START|bbbb|cccc|1700001000|test@example.com|Test|Rename
0	0	old.py => new.py

COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Add file
5	0	old.py
"""
        commits, changes = extractor._parse_log(raw)
        extractor._resolve_identities(commits, changes)

        # Both changes should share the same file_id
        add_change = next(c for c in changes if c.change_type != ChangeType.RENAMED)
        rename_change = next(c for c in changes if c.change_type == ChangeType.RENAMED)

        assert add_change.file_id is not None
        assert rename_change.file_id is not None
        assert add_change.file_id == rename_change.file_id

        # FactStore should resolve new_path to the same identity
        resolved = store.resolve_file_id("new.py")
        assert resolved == add_change.file_id

        # old_path should no longer resolve (identity moved)
        old_resolved = store.resolve_file_id("old.py")
        assert old_resolved is None

    def test_delete_marks_dead(self) -> None:
        """DELETE marks identity as dead in FactStore."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        # Commit 1: add file (older)
        # Commit 2: delete file (newer)
        # Note: git numstat for deletes still shows line counts
        raw = """COMMIT_START|bbbb|cccc|1700001000|test@example.com|Test|Delete
5	0	main.py

COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Add
5	0	main.py
"""
        commits, changes = extractor._parse_log(raw)

        # Manually set the delete change_type (parser sees MODIFIED by default)
        # We need to simulate a delete properly
        # The parser can't distinguish ADD vs DELETE vs MODIFY from numstat alone;
        # it only detects RENAMED from the => pattern. So let's use _resolve_identities
        # with manually crafted changes instead.

        from shannon_insight.persistence.git_models import GitCommit, GitFileChange

        add_commit = GitCommit(
            hash="aaaa",
            parent_hashes=(),
            timestamp=1700000000,
            author_email="test@example.com",
            author_name="Test",
            subject="Add file",
        )
        del_commit = GitCommit(
            hash="bbbb",
            parent_hashes=("aaaa",),
            timestamp=1700001000,
            author_email="test@example.com",
            author_name="Test",
            subject="Delete file",
        )

        add_change = GitFileChange(
            commit_hash="aaaa",
            file_path="main.py",
            additions=5,
            deletions=0,
            change_type=ChangeType.ADDED,
        )
        del_change = GitFileChange(
            commit_hash="bbbb",
            file_path="main.py",
            additions=0,
            deletions=5,
            change_type=ChangeType.DELETED,
        )

        all_commits = [add_commit, del_commit]
        all_changes = [add_change, del_change]

        extractor._resolve_identities(all_commits, all_changes)

        # Both should have file_ids
        assert add_change.file_id is not None
        assert del_change.file_id is not None
        assert add_change.file_id == del_change.file_id

        # Identity should be marked dead
        identity = store.get_file_identity(add_change.file_id)
        assert identity is not None
        assert identity["is_alive"] is False

        # resolve_file_id should return None for dead files
        assert store.resolve_file_id("main.py") is None

    def test_modify_uses_existing_identity(self) -> None:
        """MODIFY uses the existing identity from a prior ADD."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        from shannon_insight.persistence.git_models import GitCommit, GitFileChange

        add_commit = GitCommit(
            hash="aaaa",
            parent_hashes=(),
            timestamp=1700000000,
            author_email="test@example.com",
            author_name="Test",
            subject="Add file",
        )
        mod_commit = GitCommit(
            hash="bbbb",
            parent_hashes=("aaaa",),
            timestamp=1700001000,
            author_email="test@example.com",
            author_name="Test",
            subject="Modify file",
        )

        add_change = GitFileChange(
            commit_hash="aaaa",
            file_path="main.py",
            additions=5,
            deletions=0,
            change_type=ChangeType.ADDED,
        )
        mod_change = GitFileChange(
            commit_hash="bbbb",
            file_path="main.py",
            additions=3,
            deletions=1,
            change_type=ChangeType.MODIFIED,
        )

        all_commits = [add_commit, mod_commit]
        all_changes = [add_change, mod_change]

        extractor._resolve_identities(all_commits, all_changes)

        assert add_change.file_id is not None
        assert mod_change.file_id is not None
        assert add_change.file_id == mod_change.file_id

    def test_modify_without_prior_add_creates_identity(self) -> None:
        """MODIFY with no prior ADD (partial history) creates implicit identity."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        from shannon_insight.persistence.git_models import GitCommit, GitFileChange

        mod_commit = GitCommit(
            hash="aaaa",
            parent_hashes=(),
            timestamp=1700000000,
            author_email="test@example.com",
            author_name="Test",
            subject="Modify file",
        )
        mod_change = GitFileChange(
            commit_hash="aaaa",
            file_path="main.py",
            additions=3,
            deletions=1,
            change_type=ChangeType.MODIFIED,
        )

        extractor._resolve_identities([mod_commit], [mod_change])

        # Should get an identity via implicit ADD
        assert mod_change.file_id is not None
        assert store.resolve_file_id("main.py") == mod_change.file_id

    def test_no_fact_store_skips_identity(self) -> None:
        """Without FactStore, file_id remains None (backward compat)."""
        extractor = GitRawExtractor("/fake/path")

        raw = """COMMIT_START|aaaa|bbbb|1700000000|test@example.com|Test|Add file
10	0	src/main.py
"""
        commits, changes = extractor._parse_log(raw)
        # No fact_store, so no identity resolution
        assert changes[0].file_id is None

    def test_commits_stored_in_fact_store(self) -> None:
        """Commits are persisted to FactStore during identity resolution."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        from shannon_insight.persistence.git_models import GitCommit, GitFileChange

        commit = GitCommit(
            hash="aaaa1111222233334444555566667777888899990000",
            parent_hashes=(),
            timestamp=1700000000,
            author_email="test@example.com",
            author_name="Test",
            subject="Add file",
        )
        change = GitFileChange(
            commit_hash="aaaa1111222233334444555566667777888899990000",
            file_path="main.py",
            additions=5,
            deletions=0,
            change_type=ChangeType.ADDED,
        )

        extractor._resolve_identities([commit], [change])

        # Verify commit was stored
        stored = store.get_commit("aaaa1111222233334444555566667777888899990000")
        assert stored is not None
        assert stored["timestamp"] == 1700000000
        assert stored["author_email"] == "test@example.com"
        assert stored["message_subject"] == "Add file"

    def test_file_changes_stored_in_fact_store(self) -> None:
        """File changes are persisted to FactStore during identity resolution."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        from shannon_insight.persistence.git_models import GitCommit, GitFileChange

        commit = GitCommit(
            hash="aaaa",
            parent_hashes=(),
            timestamp=1700000000,
            author_email="test@example.com",
            author_name="Test",
            subject="Add file",
        )
        change = GitFileChange(
            commit_hash="aaaa",
            file_path="main.py",
            additions=5,
            deletions=0,
            change_type=ChangeType.ADDED,
        )

        extractor._resolve_identities([commit], [change])

        # Verify file change was stored
        stored_changes = store.get_changes_for_commit("aaaa")
        assert len(stored_changes) == 1
        assert stored_changes[0]["file_id"] == change.file_id
        assert stored_changes[0]["change_type"] == "A"
        assert stored_changes[0]["new_path"] == "main.py"
        assert stored_changes[0]["additions"] == 5
        assert stored_changes[0]["deletions"] == 0

    def test_oldest_first_processing(self) -> None:
        """Commits are processed oldest-first even if parsed newest-first."""
        store = FactStore.in_memory()
        extractor = GitRawExtractor("/fake/path", fact_store=store)

        from shannon_insight.persistence.git_models import GitCommit, GitFileChange

        # Provide commits in reverse chronological order (newest first,
        # as git log normally outputs them)
        newer = GitCommit(
            hash="bbbb",
            parent_hashes=("aaaa",),
            timestamp=1700001000,
            author_email="test@example.com",
            author_name="Test",
            subject="Rename file",
        )
        older = GitCommit(
            hash="aaaa",
            parent_hashes=(),
            timestamp=1700000000,
            author_email="test@example.com",
            author_name="Test",
            subject="Add file",
        )

        add_change = GitFileChange(
            commit_hash="aaaa",
            file_path="old.py",
            additions=5,
            deletions=0,
            change_type=ChangeType.ADDED,
        )
        rename_change = GitFileChange(
            commit_hash="bbbb",
            file_path="new.py",
            additions=0,
            deletions=0,
            change_type=ChangeType.RENAMED,
            old_path="old.py",
        )

        # Input order: newer first (like git log output)
        all_commits = [newer, older]
        all_changes = [rename_change, add_change]

        extractor._resolve_identities(all_commits, all_changes)

        # Despite reverse input order, identity should be consistent:
        # ADD creates identity, RENAME transfers it
        assert add_change.file_id is not None
        assert rename_change.file_id is not None
        assert add_change.file_id == rename_change.file_id

        # new.py should resolve to the same identity
        assert store.resolve_file_id("new.py") == add_change.file_id
