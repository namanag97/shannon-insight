"""Tests for git facts database storage."""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from shannon_insight.persistence.git_facts import GitFactDatabase
from shannon_insight.persistence.git_models import (
    ChangeType,
    GitCommit,
    GitExtractionSession,
    GitFileChange,
)


@pytest.fixture
def db() -> GitFactDatabase:
    """Create a test database in a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_git_facts.db"
        yield GitFactDatabase(db_path)


@pytest.fixture
def sample_session() -> GitExtractionSession:
    """Create a sample extraction session."""
    return GitExtractionSession(
        id=str(uuid4()),
        repo_path="/tmp/test_repo",
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        head_sha="a" * 40,
        oldest_sha="b" * 40,
        commit_count=0,
        file_change_count=0,
        status="running",
        error_message=None,
    )


@pytest.fixture
def sample_commits() -> list[GitCommit]:
    """Create sample commits for testing."""
    now = int(datetime.now(timezone.utc).timestamp())
    day = 86400

    return [
        GitCommit(
            hash="a" * 40,
            timestamp=now,
            author_email="alice@example.com",
            author_name="Alice",
            subject="Fix authentication bug",
            parent_hashes=("b" * 40,),
        ),
        GitCommit(
            hash="b" * 40,
            timestamp=now - day,
            author_email="bob@example.com",
            author_name="Bob",
            subject="Refactor user module",
            parent_hashes=("c" * 40,),
        ),
        GitCommit(
            hash="c" * 40,
            timestamp=now - 2 * day,
            author_email="alice@example.com",
            author_name="Alice",
            subject="Add user registration",
            parent_hashes=("d" * 40,),
        ),
        # Merge commit
        GitCommit(
            hash="d" * 40,
            timestamp=now - 3 * day,
            author_email="bob@example.com",
            author_name="Bob",
            subject="Merge branch 'feature'",
            parent_hashes=("e" * 40, "f" * 40),
        ),
    ]


@pytest.fixture
def sample_file_changes() -> list[GitFileChange]:
    """Create sample file changes."""
    return [
        # Commit a: fix auth
        GitFileChange(
            commit_hash="a" * 40,
            file_path="src/auth.py",
            additions=10,
            deletions=5,
            change_type=ChangeType.MODIFIED,
        ),
        GitFileChange(
            commit_hash="a" * 40,
            file_path="tests/test_auth.py",
            additions=20,
            deletions=0,
            change_type=ChangeType.MODIFIED,
        ),
        # Commit b: refactor user
        GitFileChange(
            commit_hash="b" * 40,
            file_path="src/user.py",
            additions=50,
            deletions=30,
            change_type=ChangeType.MODIFIED,
        ),
        GitFileChange(
            commit_hash="b" * 40,
            file_path="src/auth.py",
            additions=5,
            deletions=5,
            change_type=ChangeType.MODIFIED,
        ),
        # Commit c: add registration (rename)
        GitFileChange(
            commit_hash="c" * 40,
            file_path="src/registration.py",
            additions=100,
            deletions=0,
            change_type=ChangeType.ADDED,
        ),
        GitFileChange(
            commit_hash="c" * 40,
            file_path="src/models/user_model.py",
            additions=30,
            deletions=10,
            change_type=ChangeType.RENAMED,
            old_path="src/models/user.py",
        ),
        # Commit d: merge (binary file)
        GitFileChange(
            commit_hash="d" * 40,
            file_path="assets/logo.png",
            additions=None,  # Binary
            deletions=None,
            change_type=ChangeType.MODIFIED,
        ),
    ]


class TestGitFactDatabase:
    """Test suite for GitFactDatabase."""

    def test_create_database(self, db: GitFactDatabase) -> None:
        """Test database creation and schema init."""
        assert db.db_path.exists()
        stats = db.get_stats()
        assert stats["commit_count"] == 0
        assert stats["file_change_count"] == 0

    def test_session_lifecycle(
        self, db: GitFactDatabase, sample_session: GitExtractionSession
    ) -> None:
        """Test creating and completing a session."""
        # Create session
        db.create_session(sample_session)

        # Check it was created
        latest = db.get_latest_session(sample_session.repo_path)
        assert latest is None  # Not completed yet

        # Complete session
        db.complete_session(sample_session.id, commit_count=10, file_change_count=50)

        # Now it should be found
        latest = db.get_latest_session(sample_session.repo_path)
        assert latest is not None
        assert latest.status == "completed"
        assert latest.commit_count == 10
        assert latest.file_change_count == 50

    def test_store_commits_batch(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
    ) -> None:
        """Test batch commit storage."""
        db.create_session(sample_session)

        count = db.store_commits_batch(sample_commits, sample_session.id)
        assert count == 4

        stats = db.get_stats()
        assert stats["commit_count"] == 4

    def test_store_file_changes_batch(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
        sample_file_changes: list[GitFileChange],
    ) -> None:
        """Test batch file change storage."""
        db.create_session(sample_session)
        db.store_commits_batch(sample_commits, sample_session.id)

        count = db.store_file_changes_batch(sample_file_changes)
        assert count == 7

        stats = db.get_stats()
        assert stats["file_change_count"] == 7

    def test_get_file_churn(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
        sample_file_changes: list[GitFileChange],
    ) -> None:
        """Test file churn query."""
        db.create_session(sample_session)
        db.store_commits_batch(sample_commits, sample_session.id)
        db.store_file_changes_batch(sample_file_changes)

        churn = db.get_file_churn("src/auth.py")
        assert churn["change_count"] == 2
        assert churn["additions"] == 15  # 10 + 5
        assert churn["deletions"] == 10  # 5 + 5
        assert churn["churn"] == 25

    def test_get_file_authors(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
        sample_file_changes: list[GitFileChange],
    ) -> None:
        """Test file author query."""
        db.create_session(sample_session)
        db.store_commits_batch(sample_commits, sample_session.id)
        db.store_file_changes_batch(sample_file_changes)

        authors = db.get_file_authors("src/auth.py")
        assert len(authors) == 2
        # Should be sorted by commit count
        emails = [a[0] for a in authors]
        assert "alice@example.com" in emails
        assert "bob@example.com" in emails

    def test_get_renames(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
        sample_file_changes: list[GitFileChange],
    ) -> None:
        """Test rename detection."""
        db.create_session(sample_session)
        db.store_commits_batch(sample_commits, sample_session.id)
        db.store_file_changes_batch(sample_file_changes)

        renames = db.get_renames()
        assert len(renames) == 1
        old_path, new_path, _ts = renames[0]
        assert old_path == "src/models/user.py"
        assert new_path == "src/models/user_model.py"

    def test_get_timestamp_range(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
    ) -> None:
        """Test timestamp range query."""
        db.create_session(sample_session)
        db.store_commits_batch(sample_commits, sample_session.id)

        ts_range = db.get_timestamp_range()
        assert ts_range is not None
        min_ts, max_ts = ts_range
        assert min_ts < max_ts

    def test_empty_database_queries(self, db: GitFactDatabase) -> None:
        """Test queries on empty database don't crash."""
        assert db.get_timestamp_range() is None
        assert db.get_file_churn("nonexistent.py")["change_count"] == 0
        assert db.get_file_authors("nonexistent.py") == []
        assert db.get_renames() == []

    def test_merge_commit_detection(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
    ) -> None:
        """Test merge commit is_merge flag."""
        # Find merge commit in sample
        merge_commit = next(c for c in sample_commits if c.is_merge)
        assert len(merge_commit.parent_hashes) == 2

    def test_binary_file_handling(
        self,
        db: GitFactDatabase,
        sample_session: GitExtractionSession,
        sample_commits: list[GitCommit],
        sample_file_changes: list[GitFileChange],
    ) -> None:
        """Test binary files have NULL additions/deletions."""
        db.create_session(sample_session)
        db.store_commits_batch(sample_commits, sample_session.id)
        db.store_file_changes_batch(sample_file_changes)

        # Binary file should have 0 churn (NULLs summed as 0)
        churn = db.get_file_churn("assets/logo.png")
        assert churn["change_count"] == 1
        assert churn["additions"] == 0
        assert churn["deletions"] == 0


class TestGitModels:
    """Test the data model classes."""

    def test_change_type_from_git(self) -> None:
        """Test parsing git change codes."""
        assert ChangeType.from_git("A") == ChangeType.ADDED
        assert ChangeType.from_git("M") == ChangeType.MODIFIED
        assert ChangeType.from_git("D") == ChangeType.DELETED
        assert ChangeType.from_git("R100") == ChangeType.RENAMED
        assert ChangeType.from_git("R050") == ChangeType.RENAMED
        assert ChangeType.from_git("C100") == ChangeType.COPIED

    def test_git_commit_is_merge(self) -> None:
        """Test merge detection."""
        normal = GitCommit(
            hash="a" * 40,
            timestamp=0,
            author_email="test@test.com",
            author_name="Test",
            subject="Normal commit",
            parent_hashes=("b" * 40,),
        )
        assert not normal.is_merge

        merge = GitCommit(
            hash="a" * 40,
            timestamp=0,
            author_email="test@test.com",
            author_name="Test",
            subject="Merge commit",
            parent_hashes=("b" * 40, "c" * 40),
        )
        assert merge.is_merge

    def test_git_file_change_is_binary(self) -> None:
        """Test binary file detection."""
        normal = GitFileChange(
            commit_hash="a" * 40,
            file_path="test.py",
            additions=10,
            deletions=5,
            change_type=ChangeType.MODIFIED,
        )
        assert not normal.is_binary
        assert normal.churn == 15

        binary = GitFileChange(
            commit_hash="a" * 40,
            file_path="test.png",
            additions=None,
            deletions=None,
            change_type=ChangeType.MODIFIED,
        )
        assert binary.is_binary
        assert binary.churn == 0
