"""Tests for persistence-based finders (Phase 7)."""

import sys
import tempfile

sys.path.insert(0, "src")

from shannon_insight.insights.finders import (
    ArchitectureErosionFinder,
    ChronicProblemFinder,
    get_persistence_finders,
)
from shannon_insight.insights.store import AnalysisStore
from shannon_insight.persistence.database import HistoryDB


class TestChronicProblemFinder:
    def test_no_db_returns_empty(self):
        """Without db_conn, returns empty list."""
        finder = ChronicProblemFinder()
        store = AnalysisStore()
        findings = finder.find(store, db_conn=None)
        assert findings == []

    def test_no_chronic_findings(self):
        """With no chronic findings, returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Insert finding with only 2 snapshots (below threshold)
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f1', 1, 2, 2, 'active', 'high_risk_hub', 0.85)"
                )
                db.conn.commit()

                finder = ChronicProblemFinder(min_persistence=3)
                store = AnalysisStore()
                findings = finder.find(store, db_conn=db.conn)

                assert len(findings) == 0

    def test_finds_chronic_problems(self):
        """Finds problems persisting 3+ snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f1', 1, 5, 5, 'active', 'high_risk_hub', 0.8)"
                )
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f2', 1, 3, 3, 'active', 'god_file', 0.7)"
                )
                db.conn.commit()

                finder = ChronicProblemFinder(min_persistence=3)
                store = AnalysisStore()
                findings = finder.find(store, db_conn=db.conn)

                assert len(findings) == 2
                assert findings[0].finding_type == "chronic_problem"
                assert "persisted 5 snapshots" in findings[0].title

    def test_severity_multiplier(self):
        """Severity is multiplied for chronic problems."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f1', 1, 3, 3, 'active', 'high_risk_hub', 0.6)"
                )
                db.conn.commit()

                finder = ChronicProblemFinder(min_persistence=3, severity_multiplier=1.25)
                store = AnalysisStore()
                findings = finder.find(store, db_conn=db.conn)

                assert len(findings) == 1
                assert findings[0].severity == 0.75  # 0.6 * 1.25

    def test_severity_capped_at_1(self):
        """Severity is capped at 1.0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f1', 1, 3, 3, 'active', 'high_risk_hub', 0.9)"
                )
                db.conn.commit()

                finder = ChronicProblemFinder(min_persistence=3, severity_multiplier=1.25)
                store = AnalysisStore()
                findings = finder.find(store, db_conn=db.conn)

                assert findings[0].severity == 1.0  # Capped


class TestArchitectureErosionFinder:
    def test_no_db_returns_empty(self):
        """Without db_conn, returns empty list."""
        finder = ArchitectureErosionFinder()
        store = AnalysisStore()
        findings = finder.find(store, db_conn=None)
        assert findings == []

    def test_not_enough_snapshots(self):
        """With fewer than min_snapshots, returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Insert only 2 snapshots
                for i, ts in enumerate(["2025-01-01", "2025-01-02"]):
                    db.conn.execute(
                        "INSERT INTO snapshots (tool_version, timestamp, analyzed_path) VALUES (?, ?, ?)",
                        ("0.7.0", ts, "/tmp"),
                    )
                    snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    db.conn.execute(
                        "INSERT INTO global_signal_history (snapshot_id, signal_name, value) VALUES (?, ?, ?)",
                        (snap_id, "violation_rate", 0.1 + i * 0.02),
                    )
                db.conn.commit()

                finder = ArchitectureErosionFinder(min_snapshots=3)
                store = AnalysisStore()
                findings = finder.find(store, db_conn=db.conn)

                assert len(findings) == 0

    def test_no_erosion_stable_rate(self):
        """Stable violation rate doesn't trigger finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Insert 3 snapshots with stable rate
                for ts in ["2025-01-01", "2025-01-02", "2025-01-03"]:
                    db.conn.execute(
                        "INSERT INTO snapshots (tool_version, timestamp, analyzed_path) VALUES (?, ?, ?)",
                        ("0.7.0", ts, "/tmp"),
                    )
                    snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    db.conn.execute(
                        "INSERT INTO global_signal_history (snapshot_id, signal_name, value) VALUES (?, ?, ?)",
                        (snap_id, "violation_rate", 0.1),  # Same rate
                    )
                db.conn.commit()

                finder = ArchitectureErosionFinder(min_snapshots=3)
                store = AnalysisStore()
                findings = finder.find(store, db_conn=db.conn)

                assert len(findings) == 0

    def test_detects_erosion(self):
        """Detects architecture erosion when rate increases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Insert 3 snapshots with increasing rate
                rates = [0.05, 0.08, 0.12]  # Increasing by 0.07 total
                for ts, rate in zip(["2025-01-01", "2025-01-02", "2025-01-03"], rates):
                    db.conn.execute(
                        "INSERT INTO snapshots (tool_version, timestamp, analyzed_path) VALUES (?, ?, ?)",
                        ("0.7.0", ts, "/tmp"),
                    )
                    snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    db.conn.execute(
                        "INSERT INTO global_signal_history (snapshot_id, signal_name, value) VALUES (?, ?, ?)",
                        (snap_id, "violation_rate", rate),
                    )
                db.conn.commit()

                finder = ArchitectureErosionFinder(min_snapshots=3, erosion_threshold=0.05)
                store = AnalysisStore()
                findings = finder.find(store, db_conn=db.conn)

                assert len(findings) == 1
                assert findings[0].finding_type == "architecture_erosion"
                assert "increased" in findings[0].title


class TestGetPersistenceFinders:
    def test_returns_two_finders(self):
        """get_persistence_finders returns both persistence finders."""
        finders = get_persistence_finders()
        assert len(finders) == 2
        finder_names = {f.name for f in finders}
        assert "architecture_erosion" in finder_names
        assert "chronic_problem" in finder_names
