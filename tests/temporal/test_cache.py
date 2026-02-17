"""Tests for commit cache."""

from shannon_insight.temporal.cache import CommitCache
from shannon_insight.temporal.models import Commit


def make_commit(sha: str, timestamp: int, author: str = "alice@example.com") -> Commit:
    """Create a test commit."""
    return Commit(
        hash=sha,
        timestamp=timestamp,
        author=author,
        files=[f"{sha[:8]}.py"],
        subject=f"Commit {sha[:8]}",
    )


class TestCommitCache:
    """Tests for CommitCache."""

    def test_empty_cache(self, tmp_path):
        """Empty cache should have no commits and no last_sha."""
        with CommitCache(tmp_path / ".shannon") as cache:
            assert cache.last_sha is None
            assert cache.commit_count() == 0
            assert cache.get_all_commits() == []

    def test_store_and_retrieve_commits(self, tmp_path):
        """Should store and retrieve commits correctly."""
        commits = [
            make_commit("a" * 40, 1000, "alice@example.com"),
            make_commit("b" * 40, 900, "bob@example.com"),
        ]

        with CommitCache(tmp_path / ".shannon") as cache:
            added = cache.store_commits(commits)
            assert added == 2
            assert cache.commit_count() == 2

            retrieved = cache.get_all_commits()
            assert len(retrieved) == 2
            # Newest first
            assert retrieved[0].hash == "a" * 40
            assert retrieved[1].hash == "b" * 40

    def test_last_sha_persistence(self, tmp_path):
        """last_sha should persist across cache instances."""
        with CommitCache(tmp_path / ".shannon") as cache:
            cache.set_last_sha("abc123")

        with CommitCache(tmp_path / ".shannon") as cache:
            assert cache.last_sha == "abc123"

    def test_duplicate_commits_not_added(self, tmp_path):
        """Duplicate commits should not be added twice."""
        commit = make_commit("a" * 40, 1000)

        with CommitCache(tmp_path / ".shannon") as cache:
            added1 = cache.store_commits([commit])
            added2 = cache.store_commits([commit])

            assert added1 == 1
            assert added2 == 0
            assert cache.commit_count() == 1

    def test_is_cached(self, tmp_path):
        """is_cached should correctly identify cached commits."""
        commit = make_commit("a" * 40, 1000)

        with CommitCache(tmp_path / ".shannon") as cache:
            assert not cache.is_cached("a" * 40)
            cache.store_commits([commit])
            assert cache.is_cached("a" * 40)
            assert not cache.is_cached("b" * 40)

    def test_get_commits_since(self, tmp_path):
        """Should return commits newer than given SHA."""
        commits = [
            make_commit("c" * 40, 1000),  # newest
            make_commit("b" * 40, 900),
            make_commit("a" * 40, 800),  # oldest
        ]

        with CommitCache(tmp_path / ".shannon") as cache:
            cache.store_commits(commits)

            # Get commits since 'a' (oldest)
            newer = cache.get_commits_since("a" * 40)
            assert len(newer) == 2
            assert newer[0].hash == "c" * 40
            assert newer[1].hash == "b" * 40

            # Get commits since 'b' (middle)
            newer = cache.get_commits_since("b" * 40)
            assert len(newer) == 1
            assert newer[0].hash == "c" * 40

            # Get commits since 'c' (newest)
            newer = cache.get_commits_since("c" * 40)
            assert len(newer) == 0

    def test_clear(self, tmp_path):
        """clear should remove all data."""
        commit = make_commit("a" * 40, 1000)

        with CommitCache(tmp_path / ".shannon") as cache:
            cache.store_commits([commit])
            cache.set_last_sha("a" * 40)

            cache.clear()

            assert cache.commit_count() == 0
            assert cache.last_sha is None
            assert cache.get_all_commits() == []

    def test_commit_files_stored(self, tmp_path):
        """Commit files should be stored and retrieved."""
        commit = Commit(
            hash="a" * 40,
            timestamp=1000,
            author="alice@example.com",
            files=["foo.py", "bar.py", "baz/qux.py"],
            subject="Multi-file commit",
        )

        with CommitCache(tmp_path / ".shannon") as cache:
            cache.store_commits([commit])
            retrieved = cache.get_all_commits()

            assert len(retrieved) == 1
            assert set(retrieved[0].files) == {"foo.py", "bar.py", "baz/qux.py"}

    def test_creates_shannon_directory(self, tmp_path):
        """Should create .shannon directory if it doesn't exist."""
        shannon_path = tmp_path / "nested" / ".shannon"
        assert not shannon_path.exists()

        with CommitCache(shannon_path) as cache:
            cache.store_commits([make_commit("a" * 40, 1000)])

        assert shannon_path.exists()
        assert (shannon_path / "commit_cache.db").exists()
