"""Tests for Phase 3 temporal model additions."""

from shannon_insight.temporal.models import ChurnSeries, Commit


class TestCommitPhase3Fields:
    """Test Phase 3 additions to Commit."""

    def test_subject_field_default(self):
        commit = Commit(
            hash="abc123",
            timestamp=1234567890,
            author="dev@example.com",
            files=["a.py"],
        )
        assert commit.subject == ""

    def test_subject_field_explicit(self):
        commit = Commit(
            hash="abc123",
            timestamp=1234567890,
            author="dev@example.com",
            files=["a.py"],
            subject="fix: resolve auth bug",
        )
        assert commit.subject == "fix: resolve auth bug"


class TestChurnSeriesPhase3Fields:
    """Test Phase 3 additions to ChurnSeries."""

    def test_cv_field_default(self):
        cs = ChurnSeries(
            file_path="a.py",
            window_counts=[1, 2, 3],
            total_changes=6,
            trajectory="stabilizing",
            slope=0.5,
        )
        assert cs.cv == 0.0

    def test_bus_factor_default(self):
        cs = ChurnSeries(
            file_path="a.py",
            window_counts=[1, 2, 3],
            total_changes=6,
            trajectory="stabilizing",
            slope=0.5,
        )
        assert cs.bus_factor == 1.0

    def test_author_entropy_default(self):
        cs = ChurnSeries(
            file_path="a.py",
            window_counts=[1, 2, 3],
            total_changes=6,
            trajectory="stabilizing",
            slope=0.5,
        )
        assert cs.author_entropy == 0.0

    def test_fix_ratio_default(self):
        cs = ChurnSeries(
            file_path="a.py",
            window_counts=[1, 2, 3],
            total_changes=6,
            trajectory="stabilizing",
            slope=0.5,
        )
        assert cs.fix_ratio == 0.0

    def test_refactor_ratio_default(self):
        cs = ChurnSeries(
            file_path="a.py",
            window_counts=[1, 2, 3],
            total_changes=6,
            trajectory="stabilizing",
            slope=0.5,
        )
        assert cs.refactor_ratio == 0.0

    def test_all_phase3_fields_explicit(self):
        cs = ChurnSeries(
            file_path="a.py",
            window_counts=[1, 2, 3],
            total_changes=6,
            trajectory="stabilizing",
            slope=0.5,
            cv=0.35,
            bus_factor=2.5,
            author_entropy=1.32,
            fix_ratio=0.2,
            refactor_ratio=0.1,
        )
        assert cs.cv == 0.35
        assert cs.bus_factor == 2.5
        assert cs.author_entropy == 1.32
        assert cs.fix_ratio == 0.2
        assert cs.refactor_ratio == 0.1
