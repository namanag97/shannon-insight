"""Performance benchmarks for temporal analysis.

These tests verify that temporal analysis meets performance requirements:
- Cold start: < 3s for 5000 commits
- Incremental: < 100ms for 10 new commits
- Memory: reasonable for large histories

Marked with @pytest.mark.slow to skip in normal test runs.
Run with: pytest tests/temporal/test_performance.py -v --run-slow
"""

import time

import pytest

from shannon_insight.temporal.cache import CommitCache
from shannon_insight.temporal.churn import build_churn_series
from shannon_insight.temporal.cochange import build_cochange_matrix
from shannon_insight.temporal.models import Commit, GitHistory


def generate_commits(n: int, files_per_commit: int = 3) -> list[Commit]:
    """Generate n synthetic commits for benchmarking."""
    authors = ["alice@example.com", "bob@example.com", "charlie@example.com"]
    files = [f"file_{i}.py" for i in range(100)]  # 100 files

    commits = []
    base_ts = 1700000000

    for i in range(n):
        # Vary files touched per commit
        import random

        random.seed(i)  # Reproducible
        commit_files = random.sample(files, min(files_per_commit, len(files)))

        commits.append(
            Commit(
                hash=f"{i:040d}",
                timestamp=base_ts - i * 3600,  # 1 hour apart
                author=authors[i % len(authors)],
                files=commit_files,
                subject=f"Commit {i}" + (" fix bug" if i % 5 == 0 else ""),
            )
        )

    return commits


def make_history(commits: list[Commit]) -> GitHistory:
    """Create GitHistory from commits."""
    file_set = set()
    for c in commits:
        file_set.update(c.files)
    span = (commits[0].timestamp - commits[-1].timestamp) // 86400 if commits else 0
    return GitHistory(commits=commits, file_set=file_set, span_days=max(1, span))


class TestChurnPerformance:
    """Performance tests for churn series computation."""

    @pytest.mark.slow
    def test_churn_1000_commits(self):
        """1000 commits should process in < 1s."""
        commits = generate_commits(1000)
        history = make_history(commits)
        analyzed_files = {f"file_{i}.py" for i in range(100)}

        start = time.perf_counter()
        result = build_churn_series(history, analyzed_files)
        elapsed = time.perf_counter() - start

        assert len(result) > 0
        assert elapsed < 1.0, f"Churn computation took {elapsed:.2f}s, expected < 1s"

    @pytest.mark.slow
    def test_churn_5000_commits(self):
        """5000 commits should process in < 3s."""
        commits = generate_commits(5000)
        history = make_history(commits)
        analyzed_files = {f"file_{i}.py" for i in range(100)}

        start = time.perf_counter()
        result = build_churn_series(history, analyzed_files)
        elapsed = time.perf_counter() - start

        assert len(result) > 0
        assert elapsed < 3.0, f"Churn computation took {elapsed:.2f}s, expected < 3s"


class TestCoChangePerformance:
    """Performance tests for co-change matrix computation."""

    @pytest.mark.slow
    def test_cochange_1000_commits(self):
        """1000 commits should process in < 2s."""
        commits = generate_commits(1000)
        history = make_history(commits)
        analyzed_files = {f"file_{i}.py" for i in range(100)}

        start = time.perf_counter()
        result = build_cochange_matrix(history, analyzed_files)
        elapsed = time.perf_counter() - start

        assert result.total_commits > 0
        assert elapsed < 2.0, f"CoChange computation took {elapsed:.2f}s, expected < 2s"


class TestCachePerformance:
    """Performance tests for commit cache."""

    @pytest.mark.slow
    def test_cache_store_1000_commits(self, tmp_path):
        """Storing 1000 commits should complete in < 1s."""
        commits = generate_commits(1000)

        with CommitCache(tmp_path / ".shannon") as cache:
            start = time.perf_counter()
            added = cache.store_commits(commits)
            elapsed = time.perf_counter() - start

            assert added == 1000
            assert elapsed < 1.0, f"Cache store took {elapsed:.2f}s, expected < 1s"

    @pytest.mark.slow
    def test_cache_retrieve_1000_commits(self, tmp_path):
        """Retrieving 1000 commits should complete in < 0.5s."""
        commits = generate_commits(1000)

        with CommitCache(tmp_path / ".shannon") as cache:
            cache.store_commits(commits)

            start = time.perf_counter()
            retrieved = cache.get_all_commits()
            elapsed = time.perf_counter() - start

            assert len(retrieved) == 1000
            assert elapsed < 0.5, f"Cache retrieve took {elapsed:.2f}s, expected < 0.5s"


class TestIncrementalPerformance:
    """Performance tests for incremental updates."""

    @pytest.mark.slow
    def test_incremental_10_commits(self, tmp_path):
        """Adding 10 new commits to cache should complete in < 100ms."""
        # Pre-populate cache
        initial_commits = generate_commits(1000)
        new_commits = generate_commits(10)

        with CommitCache(tmp_path / ".shannon") as cache:
            cache.store_commits(initial_commits)

            start = time.perf_counter()
            added = cache.store_commits(new_commits)
            elapsed = time.perf_counter() - start

            assert added == 10
            assert elapsed < 0.1, f"Incremental store took {elapsed:.3f}s, expected < 0.1s"


# Slow marker configuration is in tests/conftest.py
