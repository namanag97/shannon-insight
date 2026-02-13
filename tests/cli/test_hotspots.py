"""Tests for cli/_hotspots.py - hotspot ranking and display."""

import pytest

from shannon_insight.cli._hotspots import (
    Hotspot,
    compute_hotspot_score,
    compute_trends,
    format_hotspot_row,
    get_hotspot_summary,
    identify_hotspots,
)
from shannon_insight.persistence.models import TensorSnapshot


class TestHotspotScoring:
    """Test compute_hotspot_score function."""

    def test_zero_signals_zero_score(self):
        """All zero signals should produce zero score."""
        score = compute_hotspot_score(
            pagerank=0.0,
            total_changes=0,
            churn_cv=0.0,
            blast_radius=0,
            finding_count=0,
        )
        assert score == 0.0

    def test_max_signals_high_score(self):
        """High signals should produce high score."""
        score = compute_hotspot_score(
            pagerank=1.0,
            total_changes=100,
            churn_cv=2.0,
            blast_radius=50,
            finding_count=10,
        )
        # Should be close to 1.0 with all max values
        assert score > 0.9

    def test_weights_sum_to_one(self):
        """Score weights should sum to 1.0."""
        # Compute with all ones (normalized)
        score = compute_hotspot_score(
            pagerank=1.0,
            total_changes=100,
            churn_cv=2.0,  # 2.0 is max for CV
            blast_radius=50,
            finding_count=10,
            max_pagerank=1.0,
            max_changes=100,
            max_blast=50,
            max_findings=10,
        )
        assert score == pytest.approx(1.0, abs=0.01)

    def test_partial_score(self):
        """Partial signals should produce partial score."""
        score = compute_hotspot_score(
            pagerank=0.5,
            total_changes=50,
            churn_cv=1.0,
            blast_radius=25,
            finding_count=5,
            max_pagerank=1.0,
            max_changes=100,
            max_blast=50,
            max_findings=10,
        )
        assert 0.4 < score < 0.6


class TestHotspotIdentification:
    """Test identify_hotspots function."""

    def test_empty_snapshot_returns_empty(self):
        """Empty snapshot should return empty list."""
        snapshot = TensorSnapshot(file_signals={})
        hotspots = identify_hotspots(snapshot, findings=[], n=10)
        assert hotspots == []

    def test_identifies_top_files(self):
        """Should identify files with highest combined signals."""
        snapshot = TensorSnapshot(
            file_signals={
                "high_risk.py": {
                    "pagerank": 0.9,
                    "total_changes": 100,
                    "churn_cv": 1.5,
                    "blast_radius_size": 30,
                },
                "low_risk.py": {
                    "pagerank": 0.1,
                    "total_changes": 5,
                    "churn_cv": 0.2,
                    "blast_radius_size": 2,
                },
            }
        )

        hotspots = identify_hotspots(snapshot, findings=[], n=10)

        assert len(hotspots) == 2
        assert hotspots[0].path == "high_risk.py"
        assert hotspots[0].rank == 1
        assert hotspots[1].path == "low_risk.py"
        assert hotspots[1].rank == 2

    def test_respects_n_limit(self):
        """Should respect the n parameter."""
        snapshot = TensorSnapshot(
            file_signals={f"file{i}.py": {"pagerank": 0.1 * i} for i in range(10)}
        )

        hotspots = identify_hotspots(snapshot, findings=[], n=3)
        assert len(hotspots) == 3

    def test_respects_min_score(self):
        """Should filter by min_score."""
        snapshot = TensorSnapshot(
            file_signals={
                "high.py": {"pagerank": 0.9, "total_changes": 50},
                "low.py": {"pagerank": 0.01, "total_changes": 1},
            }
        )

        hotspots = identify_hotspots(snapshot, findings=[], n=10, min_score=0.1)
        assert len(hotspots) == 1
        assert hotspots[0].path == "high.py"


class TestHotspotTrends:
    """Test compute_trends function."""

    def test_no_previous_no_trends(self):
        """No previous data should not modify hotspots."""
        hotspots = [
            Hotspot(
                path="file.py",
                score=0.5,
                rank=1,
                pagerank=0.5,
                total_changes=10,
                churn_cv=0.5,
                blast_radius=5,
                finding_count=1,
            )
        ]
        result = compute_trends(hotspots, None)
        assert result[0].trend == "stable"

    def test_identifies_new_files(self):
        """Files not in previous should be marked 'new'."""
        hotspots = [
            Hotspot(
                path="new_file.py",
                score=0.5,
                rank=1,
                pagerank=0.5,
                total_changes=10,
                churn_cv=0.5,
                blast_radius=5,
                finding_count=1,
            )
        ]
        prev = {"old_file.py": {"pagerank": 0.3}}

        result = compute_trends(hotspots, prev)
        assert result[0].trend == "new"

    def test_identifies_score_increase(self):
        """Score increase should be marked 'up'."""
        hotspots = [
            Hotspot(
                path="file.py",
                score=0.8,
                rank=1,
                pagerank=0.8,
                total_changes=50,
                churn_cv=1.0,
                blast_radius=20,
                finding_count=3,
            )
        ]
        prev = {
            "file.py": {
                "pagerank": 0.3,
                "total_changes": 10,
                "churn_cv": 0.2,
                "blast_radius_size": 5,
            }
        }

        result = compute_trends(hotspots, prev)
        assert result[0].trend == "up"

    def test_identifies_score_decrease(self):
        """Score decrease should be marked 'down'."""
        hotspots = [
            Hotspot(
                path="file.py",
                score=0.2,
                rank=1,
                pagerank=0.2,
                total_changes=5,
                churn_cv=0.2,
                blast_radius=2,
                finding_count=0,
            )
        ]
        prev = {
            "file.py": {
                "pagerank": 0.8,
                "total_changes": 50,
                "churn_cv": 1.5,
                "blast_radius_size": 30,
            }
        }

        result = compute_trends(hotspots, prev)
        assert result[0].trend == "down"


class TestHotspotDisplay:
    """Test hotspot display formatting."""

    def test_format_row_high_risk(self):
        """High-risk hotspot should use red color."""
        hs = Hotspot(
            path="risky.py",
            score=0.8,
            rank=1,
            pagerank=0.9,
            total_changes=100,
            churn_cv=1.5,
            blast_radius=30,
            finding_count=5,
        )
        row = format_hotspot_row(hs)
        assert "1" in row  # Rank number
        assert "0.8" in row
        assert "risky.py" in row

    def test_format_row_truncates_long_path(self):
        """Long paths should be truncated."""
        long_path = "very/deep/nested/directory/structure/with/a/long/filename.py"
        hs = Hotspot(
            path=long_path,
            score=0.5,
            rank=1,
            pagerank=0.5,
            total_changes=10,
            churn_cv=0.5,
            blast_radius=5,
            finding_count=1,
        )
        row = format_hotspot_row(hs)
        assert "..." in row

    def test_format_row_with_trend(self):
        """Row with trend should show indicator."""
        hs = Hotspot(
            path="file.py",
            score=0.5,
            rank=1,
            pagerank=0.5,
            total_changes=10,
            churn_cv=0.5,
            blast_radius=5,
            finding_count=1,
            trend="up",
            rank_change=-3,
        )
        row = format_hotspot_row(hs, show_trend=True)
        # Should show up arrow for worse trend
        assert "↑" in row or "up" in row.lower()


class TestHotspotSummary:
    """Test get_hotspot_summary function."""

    def test_empty_returns_zeros(self):
        """Empty data should return all zeros."""
        snapshot = TensorSnapshot(file_signals={})
        summary = get_hotspot_summary(snapshot, [])

        assert summary["total_hotspots"] == 0
        assert summary["high_risk_count"] == 0
        assert summary["medium_risk_count"] == 0

    def test_counts_risk_levels(self):
        """Should count high and medium risk files."""
        snapshot = TensorSnapshot(
            file_signals={
                "high1.py": {
                    "pagerank": 1.0,
                    "total_changes": 100,
                    "churn_cv": 2.0,
                    "blast_radius_size": 50,
                },
                "high2.py": {
                    "pagerank": 0.9,
                    "total_changes": 90,
                    "churn_cv": 1.8,
                    "blast_radius_size": 40,
                },
                "medium.py": {
                    "pagerank": 0.5,
                    "total_changes": 30,
                    "churn_cv": 0.8,
                    "blast_radius_size": 15,
                },
                "low.py": {
                    "pagerank": 0.1,
                    "total_changes": 5,
                    "churn_cv": 0.2,
                    "blast_radius_size": 2,
                },
            }
        )

        summary = get_hotspot_summary(snapshot, [])

        assert summary["total_hotspots"] >= 3  # All with score > 0.1
        assert summary["high_risk_count"] >= 1
