"""Comprehensive tests for churn computation."""

import pytest

from shannon_insight.temporal.churn import (
    FIX_KEYWORDS,
    REFACTOR_KEYWORDS,
    _compute_author_entropy,
    build_churn_series,
    compute_change_entropy,
)
from shannon_insight.temporal.models import Commit, GitHistory, Trajectory


def make_commits(data: list[tuple[str, int, str, list[str], str]]) -> list[Commit]:
    """Create commits from (sha, timestamp, author, files, subject) tuples."""
    return [
        Commit(hash=sha, timestamp=ts, author=author, files=files, subject=subject)
        for sha, ts, author, files, subject in data
    ]


def make_history(commits_data: list[tuple[str, int, str, list[str], str]]) -> GitHistory:
    """Create GitHistory from commit data."""
    commits = make_commits(commits_data)
    file_set = set()
    for c in commits:
        file_set.update(c.files)
    span = 0
    if len(commits) >= 2:
        span = (commits[0].timestamp - commits[-1].timestamp) // 86400
    return GitHistory(commits=commits, file_set=file_set, span_days=max(1, span))


class TestBuildChurnSeries:
    """Test build_churn_series function."""

    def test_empty_history(self):
        """Empty history should return empty dict."""
        history = GitHistory(commits=[], file_set=set(), span_days=0)
        result = build_churn_series(history, {"foo.py"})
        assert result == {}

    def test_single_file_single_commit(self):
        """Single commit should create ChurnSeries."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py"], "init"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})

        assert "foo.py" in result
        cs = result["foo.py"]
        assert cs.total_changes == 1
        assert cs.trajectory == Trajectory.DORMANT  # total <= 1

    def test_file_not_in_analyzed_files_excluded(self):
        """Files not in analyzed_files should be excluded."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py", "bar.py"], "init"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})  # bar.py excluded

        assert "foo.py" in result
        assert "bar.py" not in result

    def test_fix_ratio_computed(self):
        """fix_ratio should count commits with fix keywords."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py"], "fix: auth bug"),
                ("b" * 40, 900000, "alice@example.com", ["foo.py"], "add feature"),
                ("c" * 40, 800000, "alice@example.com", ["foo.py"], "bugfix login"),
                ("d" * 40, 700000, "alice@example.com", ["foo.py"], "refactor code"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})

        cs = result["foo.py"]
        assert cs.fix_ratio == pytest.approx(0.5)  # 2 out of 4 are fixes

    def test_refactor_ratio_computed(self):
        """refactor_ratio should count commits with refactor keywords."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py"], "refactor auth"),
                ("b" * 40, 900000, "alice@example.com", ["foo.py"], "add feature"),
                ("c" * 40, 800000, "alice@example.com", ["foo.py"], "cleanup code"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})

        cs = result["foo.py"]
        assert cs.refactor_ratio == pytest.approx(2 / 3)  # 2 out of 3

    def test_bus_factor_single_author(self):
        """Single author should have bus_factor = 1."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py"], "commit 1"),
                ("b" * 40, 900000, "alice@example.com", ["foo.py"], "commit 2"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})

        cs = result["foo.py"]
        assert cs.bus_factor == pytest.approx(1.0)
        assert cs.author_entropy == pytest.approx(0.0)

    def test_bus_factor_two_equal_authors(self):
        """Two equal authors should have bus_factor = 2."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py"], "commit 1"),
                ("b" * 40, 900000, "bob@example.com", ["foo.py"], "commit 2"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})

        cs = result["foo.py"]
        assert cs.bus_factor == pytest.approx(2.0)
        assert cs.author_entropy == pytest.approx(1.0)

    def test_change_entropy_computed(self):
        """change_entropy should be computed for each file."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py"], "commit 1"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})

        cs = result["foo.py"]
        assert cs.change_entropy >= 0.0


class TestKeywords:
    """Test fix and refactor keyword detection."""

    def test_fix_keywords_comprehensive(self):
        """All fix keywords should be present."""
        expected = {"fix", "bug", "patch", "hotfix", "bugfix", "repair", "issue"}
        assert FIX_KEYWORDS == expected

    def test_refactor_keywords_comprehensive(self):
        """All refactor keywords should be present."""
        expected = {"refactor", "cleanup", "clean up", "reorganize", "restructure", "rename"}
        assert REFACTOR_KEYWORDS == expected

    def test_keyword_matching_case_insensitive(self):
        """Keywords should match case-insensitively in commit messages."""
        history = make_history(
            [
                ("a" * 40, 1000000, "alice@example.com", ["foo.py"], "FIX: bug"),
                ("b" * 40, 900000, "alice@example.com", ["foo.py"], "REFACTOR code"),
            ]
        )
        result = build_churn_series(history, {"foo.py"})

        cs = result["foo.py"]
        assert cs.fix_ratio == pytest.approx(0.5)
        assert cs.refactor_ratio == pytest.approx(0.5)


class TestAuthorEntropy:
    """Test author entropy computation."""

    def test_single_author_zero_entropy(self):
        """Single author should have zero entropy."""
        from collections import Counter

        counts = Counter({"alice": 5})
        assert _compute_author_entropy(counts) == 0.0

    def test_two_equal_authors_one_bit(self):
        """Two equal authors should have 1 bit entropy."""
        from collections import Counter

        counts = Counter({"alice": 5, "bob": 5})
        assert _compute_author_entropy(counts) == pytest.approx(1.0)

    def test_four_equal_authors_two_bits(self):
        """Four equal authors should have 2 bits entropy."""
        from collections import Counter

        counts = Counter({"alice": 5, "bob": 5, "charlie": 5, "diana": 5})
        assert _compute_author_entropy(counts) == pytest.approx(2.0)


class TestChangeEntropy:
    """Test change entropy computation."""

    def test_single_window_zero_entropy(self):
        """Changes in single window should have zero entropy."""
        # All changes in one window
        assert compute_change_entropy([10]) == 0.0

    def test_uniform_distribution_max_entropy(self):
        """Uniform distribution should have maximum entropy."""
        # Equal changes across 4 windows
        entropy = compute_change_entropy([5, 5, 5, 5])
        assert entropy == pytest.approx(2.0)  # log2(4) = 2

    def test_no_changes_zero_entropy(self):
        """No changes should have zero entropy."""
        assert compute_change_entropy([0, 0, 0, 0]) == 0.0
