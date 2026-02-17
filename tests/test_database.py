"""Tests for the persistence database module."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "src")

from shannon_insight.persistence.database import HistoryDB
from shannon_insight.persistence.queries import (
    get_chronic_findings,
    get_finding_history,
    get_finding_lifecycle_map,
    get_global_signal_time_series,
    get_module_signal_time_series,
    get_signal_time_series,
    update_finding_lifecycle,
)


class TestDatabaseSchema:
    def test_creates_v2_tables(self):
        """Verify all v2 tables are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Check v2 tables exist
                tables = db.conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ).fetchall()
                table_names = {r["name"] for r in tables}

                # V1 tables
                assert "snapshots" in table_names
                assert "file_signals" in table_names
                assert "codebase_signals" in table_names
                assert "findings" in table_names
                assert "dependency_edges" in table_names
                assert "baseline" in table_names

                # V2 tables
                assert "signal_history" in table_names
                assert "module_signal_history" in table_names
                assert "global_signal_history" in table_names
                assert "finding_lifecycle" in table_names

    def test_schema_version_is_2(self):
        """Verify schema version is 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                row = db.conn.execute("SELECT version FROM schema_version").fetchone()
                assert row["version"] == 2

    def test_creates_v2_indexes(self):
        """Verify v2 indexes are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                indexes = db.conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
                ).fetchall()
                index_names = {r["name"] for r in indexes}

                assert "idx_signal_file_name" in index_names
                assert "idx_module_signal_history" in index_names
                assert "idx_finding_type" in index_names

    def test_signal_history_schema(self):
        """Verify signal_history table has correct columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Insert test row
                db.conn.execute(
                    """
                    INSERT INTO snapshots (tool_version, timestamp, analyzed_path)
                    VALUES ('0.7.0', '2025-01-01', '/tmp')
                    """
                )
                snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

                # Insert into signal_history
                db.conn.execute(
                    """
                    INSERT INTO signal_history (snapshot_id, file_path, signal_name, value, percentile)
                    VALUES (?, 'a.py', 'cognitive_load', 0.5, 0.75)
                    """,
                    (snap_id,),
                )

                row = db.conn.execute(
                    "SELECT * FROM signal_history WHERE file_path = 'a.py'"
                ).fetchone()
                assert row["value"] == 0.5
                assert row["percentile"] == 0.75

    def test_finding_lifecycle_schema(self):
        """Verify finding_lifecycle table has correct columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Insert test row
                db.conn.execute(
                    """
                    INSERT INTO finding_lifecycle
                        (identity_key, first_seen_snapshot, last_seen_snapshot, persistence_count, current_status, finding_type, severity)
                    VALUES ('abc123', 1, 3, 3, 'active', 'high_risk_hub', 0.85)
                    """
                )

                row = db.conn.execute(
                    "SELECT * FROM finding_lifecycle WHERE identity_key = 'abc123'"
                ).fetchone()
                assert row["persistence_count"] == 3
                assert row["current_status"] == "active"
                assert row["finding_type"] == "high_risk_hub"

    def test_module_signal_history_schema(self):
        """Verify module_signal_history table has correct columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    """
                    INSERT INTO snapshots (tool_version, timestamp, analyzed_path)
                    VALUES ('0.7.0', '2025-01-01', '/tmp')
                    """
                )
                snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

                db.conn.execute(
                    """
                    INSERT INTO module_signal_history (snapshot_id, module_path, signal_name, value)
                    VALUES (?, 'src/', 'cohesion', 0.8)
                    """,
                    (snap_id,),
                )

                row = db.conn.execute(
                    "SELECT * FROM module_signal_history WHERE module_path = 'src/'"
                ).fetchone()
                assert row["value"] == 0.8

    def test_global_signal_history_schema(self):
        """Verify global_signal_history table has correct columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    """
                    INSERT INTO snapshots (tool_version, timestamp, analyzed_path)
                    VALUES ('0.7.0', '2025-01-01', '/tmp')
                    """
                )
                snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

                db.conn.execute(
                    """
                    INSERT INTO global_signal_history (snapshot_id, signal_name, value)
                    VALUES (?, 'modularity', 0.6)
                    """,
                    (snap_id,),
                )

                row = db.conn.execute(
                    "SELECT * FROM global_signal_history WHERE signal_name = 'modularity'"
                ).fetchone()
                assert row["value"] == 0.6


class TestDatabaseMigration:
    def test_v1_migration_backfills_signal_history(self):
        """Test that v1 data is backfilled to signal_history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a v1-style database manually (simulate existing v1 DB)
            db_path = Path(tmpdir) / ".shannon" / "history.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)

            import sqlite3

            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE schema_version (version INTEGER NOT NULL)")
            conn.execute("INSERT INTO schema_version VALUES (1)")
            conn.execute(
                """
                CREATE TABLE snapshots (
                    id INTEGER PRIMARY KEY,
                    schema_version INTEGER DEFAULT 1,
                    tool_version TEXT NOT NULL,
                    commit_sha TEXT,
                    timestamp TEXT NOT NULL,
                    analyzed_path TEXT NOT NULL,
                    file_count INTEGER DEFAULT 0,
                    module_count INTEGER DEFAULT 0,
                    commits_analyzed INTEGER DEFAULT 0,
                    analyzers_ran TEXT DEFAULT '[]',
                    config_hash TEXT DEFAULT ''
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE file_signals (
                    id INTEGER PRIMARY KEY,
                    snapshot_id INTEGER,
                    file_path TEXT,
                    signal_name TEXT,
                    value REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE codebase_signals (
                    id INTEGER PRIMARY KEY,
                    snapshot_id INTEGER,
                    signal_name TEXT,
                    value REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE findings (
                    id INTEGER PRIMARY KEY,
                    snapshot_id INTEGER,
                    finding_type TEXT,
                    identity_key TEXT,
                    severity REAL,
                    title TEXT,
                    files TEXT DEFAULT '[]',
                    evidence TEXT DEFAULT '[]',
                    suggestion TEXT DEFAULT ''
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE dependency_edges (
                    id INTEGER PRIMARY KEY,
                    snapshot_id INTEGER,
                    src TEXT,
                    dst TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE baseline (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    snapshot_id INTEGER
                )
                """
            )

            # Insert v1 data
            conn.execute(
                "INSERT INTO snapshots (tool_version, timestamp, analyzed_path) VALUES ('0.6.0', '2025-01-01', '/tmp')"
            )
            conn.execute(
                "INSERT INTO file_signals (snapshot_id, file_path, signal_name, value) VALUES (1, 'a.py', 'cognitive_load', 0.5)"
            )
            conn.execute(
                "INSERT INTO codebase_signals (snapshot_id, signal_name, value) VALUES (1, 'modularity', 0.6)"
            )
            conn.execute(
                "INSERT INTO findings (snapshot_id, finding_type, identity_key, severity, title) VALUES (1, 'high_risk_hub', 'abc123', 0.85, 'Test')"
            )
            conn.commit()
            conn.close()

            # Now open with HistoryDB which should migrate
            with HistoryDB(tmpdir) as db:
                # Check schema version is now 2
                row = db.conn.execute("SELECT version FROM schema_version").fetchone()
                assert row["version"] == 2

                # Check signal_history was backfilled
                row = db.conn.execute(
                    "SELECT * FROM signal_history WHERE file_path = 'a.py'"
                ).fetchone()
                assert row is not None
                assert row["value"] == 0.5

                # Check global_signal_history was backfilled
                row = db.conn.execute(
                    "SELECT * FROM global_signal_history WHERE signal_name = 'modularity'"
                ).fetchone()
                assert row is not None
                assert row["value"] == 0.6

                # Check finding_lifecycle was backfilled
                row = db.conn.execute(
                    "SELECT * FROM finding_lifecycle WHERE identity_key = 'abc123'"
                ).fetchone()
                assert row is not None
                assert row["current_status"] == "active"
                assert row["persistence_count"] == 1


class TestTimeSeriesQueries:
    def test_get_signal_time_series(self):
        """Test querying signal time series for a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Insert 3 snapshots with signal data
                for i, ts in enumerate(["2025-01-01", "2025-01-02", "2025-01-03"]):
                    db.conn.execute(
                        "INSERT INTO snapshots (tool_version, timestamp, analyzed_path) VALUES (?, ?, ?)",
                        ("0.7.0", ts, "/tmp"),
                    )
                    snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    db.conn.execute(
                        "INSERT INTO signal_history (snapshot_id, file_path, signal_name, value, percentile) VALUES (?, ?, ?, ?, ?)",
                        (snap_id, "a.py", "cognitive_load", 0.5 + i * 0.1, 0.7 + i * 0.05),
                    )
                db.conn.commit()

                # Query time series
                points = get_signal_time_series(db.conn, "a.py", "cognitive_load")

                assert len(points) == 3
                # Should be in chronological order (oldest first)
                assert points[0].timestamp == "2025-01-01"
                assert points[0].value == 0.5
                assert points[2].timestamp == "2025-01-03"
                assert points[2].value == 0.7

    def test_get_module_signal_time_series(self):
        """Test querying signal time series for a module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    "INSERT INTO snapshots (tool_version, timestamp, analyzed_path) VALUES (?, ?, ?)",
                    ("0.7.0", "2025-01-01", "/tmp"),
                )
                snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                db.conn.execute(
                    "INSERT INTO module_signal_history (snapshot_id, module_path, signal_name, value) VALUES (?, ?, ?, ?)",
                    (snap_id, "src/", "cohesion", 0.8),
                )
                db.conn.commit()

                points = get_module_signal_time_series(db.conn, "src/", "cohesion")
                assert len(points) == 1
                assert points[0].value == 0.8

    def test_get_global_signal_time_series(self):
        """Test querying global signal time series."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    "INSERT INTO snapshots (tool_version, timestamp, analyzed_path) VALUES (?, ?, ?)",
                    ("0.7.0", "2025-01-01", "/tmp"),
                )
                snap_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                db.conn.execute(
                    "INSERT INTO global_signal_history (snapshot_id, signal_name, value) VALUES (?, ?, ?)",
                    (snap_id, "codebase_health", 8.5),
                )
                db.conn.commit()

                points = get_global_signal_time_series(db.conn, "codebase_health")
                assert len(points) == 1
                assert points[0].value == 8.5


class TestFindingLifecycleQueries:
    def test_get_finding_history(self):
        """Test querying finding lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    """
                    INSERT INTO finding_lifecycle
                        (identity_key, first_seen_snapshot, last_seen_snapshot, persistence_count, current_status, finding_type, severity)
                    VALUES ('abc123', 1, 3, 3, 'active', 'high_risk_hub', 0.85)
                    """
                )
                db.conn.commit()

                info = get_finding_history(db.conn, "abc123")
                assert info is not None
                assert info.persistence_count == 3
                assert info.current_status == "active"

    def test_get_finding_history_not_found(self):
        """Test querying non-existent finding returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                info = get_finding_history(db.conn, "nonexistent")
                assert info is None

    def test_get_chronic_findings(self):
        """Test querying chronic findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Create snapshots first (needed for FK and join)
                for i in range(1, 6):
                    db.conn.execute(
                        "INSERT INTO snapshots (id, tool_version, timestamp, analyzed_path) "
                        "VALUES (?, '0.7.0', '2025-01-01', '/tmp')",
                        (i,),
                    )

                # Insert findings with different persistence counts
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f1', 1, 5, 5, 'active', 'high_risk_hub', 0.9)"
                )
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f2', 1, 3, 3, 'active', 'god_file', 0.8)"
                )
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f3', 1, 2, 2, 'active', 'hidden_coupling', 0.7)"
                )
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f4', 1, 4, 4, 'resolved', 'unstable_file', 0.85)"
                )

                # Insert corresponding findings rows (required for JOIN to get files)
                db.conn.execute(
                    "INSERT INTO findings (snapshot_id, finding_type, identity_key, severity, title, files) "
                    "VALUES (5, 'high_risk_hub', 'f1', 0.9, 'High risk hub in utils.py', '[\"utils.py\"]')"
                )
                db.conn.execute(
                    "INSERT INTO findings (snapshot_id, finding_type, identity_key, severity, title, files) "
                    "VALUES (3, 'god_file', 'f2', 0.8, 'God file: main.py', '[\"main.py\"]')"
                )
                db.conn.execute(
                    "INSERT INTO findings (snapshot_id, finding_type, identity_key, severity, title, files) "
                    "VALUES (2, 'hidden_coupling', 'f3', 0.7, 'Hidden coupling', '[\"a.py\", \"b.py\"]')"
                )
                db.conn.execute(
                    "INSERT INTO findings (snapshot_id, finding_type, identity_key, severity, title, files) "
                    "VALUES (4, 'unstable_file', 'f4', 0.85, 'Unstable file', '[\"unstable.py\"]')"
                )
                db.conn.commit()

                chronic = get_chronic_findings(db.conn, min_persistence=3)

                # Should get f1 and f2 (>=3 and active), not f3 (<3) or f4 (resolved)
                assert len(chronic) == 2
                assert chronic[0].identity_key == "f1"  # highest persistence
                assert chronic[1].identity_key == "f2"

                # Verify files are populated correctly
                assert chronic[0].files == ["utils.py"]
                assert chronic[0].title == "High risk hub in utils.py"
                assert chronic[1].files == ["main.py"]
                assert chronic[1].title == "God file: main.py"

    def test_update_finding_lifecycle_new(self):
        """Test updating lifecycle for a new finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                update_finding_lifecycle(
                    db.conn, "new1", "high_risk_hub", 0.85, snapshot_id=1, is_present=True
                )
                db.conn.commit()

                info = get_finding_history(db.conn, "new1")
                assert info is not None
                assert info.persistence_count == 1
                assert info.current_status == "active"

    def test_update_finding_lifecycle_persisting(self):
        """Test updating lifecycle for a persisting finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Create finding
                update_finding_lifecycle(
                    db.conn, "persist1", "high_risk_hub", 0.8, snapshot_id=1, is_present=True
                )
                db.conn.commit()

                # Update in second snapshot
                update_finding_lifecycle(
                    db.conn, "persist1", "high_risk_hub", 0.85, snapshot_id=2, is_present=True
                )
                db.conn.commit()

                info = get_finding_history(db.conn, "persist1")
                assert info.persistence_count == 2
                assert info.last_seen_snapshot == 2

    def test_update_finding_lifecycle_resolved(self):
        """Test updating lifecycle for a resolved finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Create finding
                update_finding_lifecycle(
                    db.conn, "resolve1", "high_risk_hub", 0.8, snapshot_id=1, is_present=True
                )
                db.conn.commit()

                # Mark as resolved
                update_finding_lifecycle(
                    db.conn, "resolve1", "high_risk_hub", 0.8, snapshot_id=2, is_present=False
                )
                db.conn.commit()

                info = get_finding_history(db.conn, "resolve1")
                assert info.current_status == "resolved"
                assert info.persistence_count == 1  # Didn't increment

    def test_get_finding_lifecycle_map(self):
        """Test getting all lifecycle data as a dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f1', 1, 3, 3, 'active', 'high_risk_hub', 0.85)"
                )
                db.conn.execute(
                    "INSERT INTO finding_lifecycle VALUES ('f2', 1, 2, 2, 'resolved', 'god_file', 0.75)"
                )
                db.conn.commit()

                lifecycle_map = get_finding_lifecycle_map(db.conn)

                assert len(lifecycle_map) == 2
                assert lifecycle_map["f1"]["current_status"] == "active"
                assert lifecycle_map["f2"]["current_status"] == "resolved"


class TestTensorSnapshotLoader:
    def test_load_tensor_snapshot(self):
        """Test loading a TensorSnapshot with all V2 data."""
        from shannon_insight.persistence.reader import load_tensor_snapshot

        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Create a snapshot
                db.conn.execute(
                    """
                    INSERT INTO snapshots (
                        id, schema_version, tool_version, timestamp, analyzed_path,
                        file_count, module_count, commits_analyzed, analyzers_ran, config_hash
                    ) VALUES (1, 2, '0.8.0', '2025-01-15T10:00:00Z', '/project',
                              10, 2, 50, '["structural", "temporal"]', 'abc123')
                    """
                )

                # Insert file signal history
                db.conn.execute(
                    """
                    INSERT INTO signal_history (snapshot_id, file_path, signal_name, value, percentile)
                    VALUES (1, 'main.py', 'cognitive_load', 0.75, 0.85)
                    """
                )
                db.conn.execute(
                    """
                    INSERT INTO signal_history (snapshot_id, file_path, signal_name, value, percentile)
                    VALUES (1, 'main.py', 'pagerank', 0.12, 0.95)
                    """
                )
                db.conn.execute(
                    """
                    INSERT INTO signal_history (snapshot_id, file_path, signal_name, value, percentile)
                    VALUES (1, 'utils.py', 'cognitive_load', 0.30, 0.40)
                    """
                )

                # Insert module signal history
                db.conn.execute(
                    """
                    INSERT INTO module_signal_history (snapshot_id, module_path, signal_name, value)
                    VALUES (1, 'src/', 'cohesion', 0.65)
                    """
                )
                db.conn.execute(
                    """
                    INSERT INTO module_signal_history (snapshot_id, module_path, signal_name, value)
                    VALUES (1, 'src/', 'instability', 0.45)
                    """
                )

                # Insert global signal history
                db.conn.execute(
                    """
                    INSERT INTO global_signal_history (snapshot_id, signal_name, value)
                    VALUES (1, 'modularity', 0.72)
                    """
                )
                db.conn.execute(
                    """
                    INSERT INTO global_signal_history (snapshot_id, signal_name, value)
                    VALUES (1, 'codebase_health', 7.5)
                    """
                )

                # Insert a finding
                db.conn.execute(
                    """
                    INSERT INTO findings (
                        snapshot_id, finding_type, identity_key, severity, title, files, evidence, suggestion
                    ) VALUES (1, 'high_risk_hub', 'abc123', 0.9, 'Hub in main.py',
                              '["main.py"]', '[{"signal": "pagerank", "value": 0.12, "percentile": 0.95, "description": "High PageRank"}]',
                              'Consider refactoring')
                    """
                )

                # Insert dependency edge
                db.conn.execute(
                    """
                    INSERT INTO dependency_edges (snapshot_id, src, dst)
                    VALUES (1, 'main.py', 'utils.py')
                    """
                )

                db.conn.commit()

                # Load the TensorSnapshot
                snap = load_tensor_snapshot(db.conn, 1)

                # Verify metadata
                assert snap.schema_version == 2
                assert snap.tool_version == "0.8.0"
                assert snap.file_count == 10
                assert snap.module_count == 2
                assert snap.analyzers_ran == ["structural", "temporal"]

                # Verify file signals
                assert "main.py" in snap.file_signals
                assert snap.file_signals["main.py"]["cognitive_load"] == 0.75
                assert snap.file_signals["main.py"]["pagerank"] == 0.12
                assert snap.file_signals["main.py"]["percentiles"]["cognitive_load"] == 0.85
                assert "utils.py" in snap.file_signals

                # Verify module signals
                assert "src/" in snap.module_signals
                assert snap.module_signals["src/"]["cohesion"] == 0.65
                assert snap.module_signals["src/"]["instability"] == 0.45

                # Verify global signals
                assert snap.global_signals["modularity"] == 0.72
                assert snap.global_signals["codebase_health"] == 7.5

                # Verify findings
                assert len(snap.findings) == 1
                assert snap.findings[0].finding_type == "high_risk_hub"
                assert snap.findings[0].files == ["main.py"]

                # Verify dependency edges
                assert len(snap.dependency_edges) == 1
                assert snap.dependency_edges[0] == ("main.py", "utils.py")

    def test_load_tensor_snapshot_not_found(self):
        """Test loading non-existent snapshot raises ValueError."""
        import pytest

        from shannon_insight.persistence.reader import load_tensor_snapshot

        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                with pytest.raises(ValueError, match="No snapshot with id=999"):
                    load_tensor_snapshot(db.conn, 999)

    def test_persist_cochange_and_architecture(self):
        """Test persisting and loading cochange edges, architecture, and community data."""
        from shannon_insight.persistence.models import TensorSnapshot
        from shannon_insight.persistence.reader import load_tensor_snapshot
        from shannon_insight.persistence.writer import save_tensor_snapshot

        with tempfile.TemporaryDirectory() as tmpdir:
            with HistoryDB(tmpdir) as db:
                # Create a TensorSnapshot with all new fields
                snap = TensorSnapshot(
                    schema_version=2,
                    tool_version="0.9.0",
                    commit_sha="abc123",
                    timestamp="2025-02-01T12:00:00Z",
                    analyzed_path="/project",
                    file_count=5,
                    module_count=2,
                    commits_analyzed=100,
                    analyzers_ran=["structural", "temporal", "spectral"],
                    config_hash="hash123",
                    file_signals={
                        "main.py": {"cognitive_load": 0.5, "percentiles": {"cognitive_load": 0.8}}
                    },
                    module_signals={"src/": {"cohesion": 0.7}},
                    global_signals={"modularity": 0.65},
                    findings=[],
                    dependency_edges=[("main.py", "utils.py")],
                    # New fields
                    cochange_edges=[
                        ("main.py", "utils.py", 0.85, 2.1, 0.9, 0.7, 15),
                        ("main.py", "config.py", 0.45, 1.2, 0.6, 0.5, 8),
                    ],
                    modules=["src/", "tests/"],
                    layers=[
                        {"depth": 0, "modules": ["src/"]},
                        {"depth": 1, "modules": ["tests/"]},
                    ],
                    violations=[{"src": "tests/", "tgt": "src/", "type": "UPWARD_DEPENDENCY"}],
                    delta_h={"main.py": 0.12, "utils.py": -0.05},
                    communities=[
                        {"id": 0, "members": ["main.py", "utils.py"], "size": 2},
                        {"id": 1, "members": ["config.py"], "size": 1},
                    ],
                    node_community={"main.py": 0, "utils.py": 0, "config.py": 1},
                    modularity_score=0.72,
                )

                # Save and reload
                snap_id = save_tensor_snapshot(db.conn, snap)
                loaded = load_tensor_snapshot(db.conn, snap_id)

                # Verify cochange edges
                assert len(loaded.cochange_edges) == 2
                assert loaded.cochange_edges[0][0] == "main.py"
                assert loaded.cochange_edges[0][1] == "utils.py"
                assert loaded.cochange_edges[0][2] == 0.85  # weight
                assert loaded.cochange_edges[0][3] == 2.1  # lift
                assert loaded.cochange_edges[0][6] == 15  # cochange_count

                # Verify modules
                assert "src/" in loaded.modules
                assert "tests/" in loaded.modules

                # Verify layers
                assert len(loaded.layers) == 2
                assert loaded.layers[0]["depth"] == 0
                assert loaded.layers[0]["modules"] == ["src/"]

                # Verify violations
                assert len(loaded.violations) == 1
                assert loaded.violations[0]["src"] == "tests/"
                assert loaded.violations[0]["tgt"] == "src/"
                assert loaded.violations[0]["type"] == "UPWARD_DEPENDENCY"

                # Verify delta_h
                assert loaded.delta_h["main.py"] == 0.12
                assert loaded.delta_h["utils.py"] == -0.05

                # Verify communities
                assert len(loaded.communities) == 2
                assert loaded.communities[0]["id"] == 0
                assert loaded.communities[0]["members"] == ["main.py", "utils.py"]

                # Verify node_community
                assert loaded.node_community["main.py"] == 0
                assert loaded.node_community["config.py"] == 1

                # Verify modularity score
                assert loaded.modularity_score == 0.72
