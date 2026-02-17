"""Tests for ProvenanceStore persistence, cleanup, and computation tree features.

Tests cover:
    - Temp-file based storage (write-through to JSONL)
    - Session directory creation and structure
    - get_computation_tree() returning nested dict
    - Automatic cleanup (atexit, signal handlers)
    - Stale session cleanup (cleanup_stale_sessions)
    - cleanup() method for explicit resource release
    - Config integration (enable_provenance, provenance_retention_hours)
    - FactStore delegation of get_computation_tree
    - Cross-platform temp directory handling
    - Graceful fallback when disk writes fail
"""

import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from shannon_insight.infrastructure.provenance import (
    DEFAULT_RETENTION_HOURS,
    TEMP_DIR_PREFIX,
    ProvenanceStore,
    _get_temp_base,
    cleanup_stale_sessions,
)
from shannon_insight.infrastructure.signals import Signal

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store():
    """Create a non-persisting ProvenanceStore for in-memory-only tests."""
    s = ProvenanceStore(persist=False)
    yield s
    s.clear()


@pytest.fixture
def persistent_store():
    """Create a persisting ProvenanceStore and clean up after."""
    s = ProvenanceStore(persist=True, session_id="test_session_persist")
    yield s
    # Uninstall signal handlers to avoid interference
    s._uninstall_cleanup_handlers()
    s.cleanup()


@pytest.fixture
def tmp_temp_dir(tmp_path):
    """Provide a custom temp base directory to avoid polluting /tmp."""
    temp_base = tmp_path / "fake_tmp"
    temp_base.mkdir()
    with patch(
        "shannon_insight.infrastructure.provenance._get_temp_base",
        return_value=temp_base,
    ):
        yield temp_base


# ---------------------------------------------------------------------------
# Persistence: temp-file storage
# ---------------------------------------------------------------------------


class TestPersistence:
    """Tests for temp-file based provenance storage."""

    def test_session_dir_created(self, persistent_store):
        """Session directory is created on init."""
        assert persistent_store.session_dir is not None
        assert persistent_store.session_dir.exists()
        assert persistent_store.session_dir.is_dir()

    def test_session_dir_name(self, persistent_store):
        """Session directory follows naming convention."""
        assert persistent_store.session_dir.name == f"{TEMP_DIR_PREFIX}test_session_persist"

    def test_provenance_file_created(self, persistent_store):
        """Provenance JSONL file is created on init."""
        assert persistent_store.provenance_file is not None
        assert persistent_store.provenance_file.name == "provenance.jsonl"

    def test_session_id_auto_generated(self):
        """Session ID is auto-generated if not provided."""
        store = ProvenanceStore(persist=False)
        assert store.session_id is not None
        assert len(store.session_id) > 0
        store.clear()

    def test_session_id_custom(self):
        """Custom session ID is used."""
        store = ProvenanceStore(persist=False, session_id="my_custom_id")
        assert store.session_id == "my_custom_id"
        store.clear()

    def test_record_writes_to_disk(self, persistent_store):
        """Records are written to the JSONL file on disk."""
        persistent_store.record("src/main.py", Signal.LINES, 150, "scanning")
        persistent_store.record("src/main.py", Signal.FUNCTION_COUNT, 5, "scanning")

        # Read the file directly
        with open(persistent_store.provenance_file) as f:
            lines = f.readlines()

        assert len(lines) == 2

        record1 = json.loads(lines[0])
        assert record1["signal"] == "lines"
        assert record1["value"] == 150
        assert record1["producer"] == "scanning"
        assert record1["entity_path"] == "src/main.py"

        record2 = json.loads(lines[1])
        assert record2["signal"] == "function_count"
        assert record2["value"] == 5

    def test_record_flushed_immediately(self, persistent_store):
        """Each record is flushed to disk immediately (write-through)."""
        persistent_store.record("src/main.py", Signal.LINES, 100, "scanning")

        # Read file immediately - should have 1 line
        with open(persistent_store.provenance_file) as f:
            lines = f.readlines()
        assert len(lines) == 1

        persistent_store.record("src/main.py", Signal.FUNCTION_COUNT, 5, "scanning")

        # Should now have 2 lines
        with open(persistent_store.provenance_file) as f:
            lines = f.readlines()
        assert len(lines) == 2

    def test_non_persistent_store_no_files(self, store):
        """Non-persisting store has no session dir or file."""
        assert store.session_dir is None
        assert store.provenance_file is None

    def test_non_persistent_record_still_works(self, store):
        """Records work in-memory even without persistence."""
        prov = store.record("src/main.py", Signal.LINES, 100, "scanning")
        assert prov.value == 100
        assert store.record_count == 1
        assert store.get_latest("src/main.py", Signal.LINES) is not None

    def test_persistence_survives_multiple_records(self, persistent_store):
        """Multiple records accumulate correctly on disk."""
        for i in range(10):
            persistent_store.record(f"file_{i}.py", Signal.LINES, i * 100, "scanning")

        with open(persistent_store.provenance_file) as f:
            lines = f.readlines()
        assert len(lines) == 10

        # Verify each record is valid JSON
        for i, line in enumerate(lines):
            record = json.loads(line)
            assert record["entity_path"] == f"file_{i}.py"
            assert record["value"] == i * 100


class TestPersistenceFallback:
    """Tests for graceful fallback when disk writes fail."""

    def test_fallback_on_unwritable_temp(self, tmp_temp_dir):
        """Falls back to in-memory when temp dir is not writable."""
        # Make the temp dir read-only
        os.chmod(tmp_temp_dir, 0o444)
        try:
            store = ProvenanceStore(persist=True, session_id="readonly_test")
            # Should still work in-memory
            store.record("src/main.py", Signal.LINES, 100, "scanning")
            assert store.record_count == 1
            # Persistence should have been disabled
            assert store.session_dir is None or not store._persist
            store.clear()
        finally:
            os.chmod(tmp_temp_dir, 0o755)


# ---------------------------------------------------------------------------
# get_computation_tree
# ---------------------------------------------------------------------------


class TestComputationTree:
    """Tests for get_computation_tree() returning nested dicts."""

    def test_simple_signal(self, store):
        """Tree for a signal with no inputs."""
        store.record("src/main.py", Signal.LINES, 150, "scanning")

        tree = store.get_computation_tree("src/main.py", Signal.LINES)
        assert tree["signal"] == "lines"
        assert tree["value"] == 150
        assert tree["producer"] == "scanning"
        assert tree["phase"] == 0
        assert tree["formula"] is None
        assert tree["inputs"] == []
        assert tree["children"] == []

    def test_signal_with_inputs(self, store):
        """Tree includes children for input signals."""
        store.record("src/main.py", Signal.IN_DEGREE, 5, "StructuralAnalyzer")
        store.record("src/main.py", Signal.OUT_DEGREE, 3, "StructuralAnalyzer")
        store.record(
            "src/main.py",
            Signal.PAGERANK,
            0.042,
            "StructuralAnalyzer",
            inputs=["in_degree", "out_degree"],
            formula="PR(v) = (1-d)/N + d * sum(PR(u)/out(u))",
        )

        tree = store.get_computation_tree("src/main.py", Signal.PAGERANK)
        assert tree["signal"] == "pagerank"
        assert tree["value"] == 0.042
        assert tree["formula"] == "PR(v) = (1-d)/N + d * sum(PR(u)/out(u))"
        assert tree["inputs"] == ["in_degree", "out_degree"]
        assert len(tree["children"]) == 2

        # Check children
        child_signals = {c["signal"] for c in tree["children"]}
        assert "in_degree" in child_signals
        assert "out_degree" in child_signals

        # Verify child values
        for child in tree["children"]:
            if child["signal"] == "in_degree":
                assert child["value"] == 5
            elif child["signal"] == "out_degree":
                assert child["value"] == 3

    def test_deep_dependency_tree(self, store):
        """Tree with multiple levels of dependencies."""
        store.record("a.py", Signal.LINES, 100, "scanning")
        store.record(
            "a.py",
            Signal.COGNITIVE_LOAD,
            3.5,
            "fusion",
            inputs=["lines"],
            formula="cognitive_load = f(lines, ...)",
        )
        store.record(
            "a.py",
            Signal.RISK_SCORE,
            0.8,
            "fusion",
            inputs=["cognitive_load"],
            formula="risk = 0.3*cognitive_load + ...",
        )

        tree = store.get_computation_tree("a.py", Signal.RISK_SCORE)
        assert tree["signal"] == "risk_score"
        assert len(tree["children"]) == 1
        assert tree["children"][0]["signal"] == "cognitive_load"
        assert len(tree["children"][0]["children"]) == 1
        assert tree["children"][0]["children"][0]["signal"] == "lines"
        assert tree["children"][0]["children"][0]["children"] == []

    def test_cycle_detection(self, store):
        """Tree handles circular dependencies gracefully."""
        store.record("a.py", Signal.IN_DEGREE, 5, "test", inputs=["out_degree"])
        store.record("a.py", Signal.OUT_DEGREE, 3, "test", inputs=["in_degree"])

        tree = store.get_computation_tree("a.py", Signal.IN_DEGREE)
        assert tree["signal"] == "in_degree"
        # out_degree should be a child
        assert len(tree["children"]) == 1
        out_child = tree["children"][0]
        assert out_child["signal"] == "out_degree"
        # in_degree should be marked as cycle
        assert len(out_child["children"]) == 1
        assert out_child["children"][0].get("cycle") is True

    def test_missing_signal(self, store):
        """Tree returns empty dict for unrecorded signal."""
        tree = store.get_computation_tree("src/main.py", Signal.PAGERANK)
        assert tree == {}

    def test_external_inputs(self, store):
        """Tree marks non-Signal inputs as external."""
        store.record(
            "src/main.py",
            Signal.PAGERANK,
            0.042,
            "StructuralAnalyzer",
            inputs=["custom_metric", "in_degree"],
        )
        store.record("src/main.py", Signal.IN_DEGREE, 5, "StructuralAnalyzer")

        tree = store.get_computation_tree("src/main.py", Signal.PAGERANK)
        assert len(tree["children"]) == 2

        # Find the external child
        external = [c for c in tree["children"] if c.get("external")]
        assert len(external) == 1
        assert external[0]["signal"] == "custom_metric"

    def test_tree_json_serializable(self, store):
        """Computation tree is JSON-serializable."""
        store.record("a.py", Signal.IN_DEGREE, 5, "structural")
        store.record(
            "a.py",
            Signal.PAGERANK,
            0.042,
            "structural",
            inputs=["in_degree"],
            formula="PR(v) = ...",
        )

        tree = store.get_computation_tree("a.py", Signal.PAGERANK)
        # Should not raise
        serialized = json.dumps(tree)
        assert isinstance(serialized, str)

        # Round-trip
        restored = json.loads(serialized)
        assert restored["signal"] == "pagerank"
        assert restored["value"] == 0.042


# ---------------------------------------------------------------------------
# Automatic cleanup
# ---------------------------------------------------------------------------


class TestCleanup:
    """Tests for explicit cleanup() method."""

    def test_cleanup_removes_session_dir(self):
        """cleanup() removes the session directory."""
        store = ProvenanceStore(persist=True, session_id="cleanup_test")
        store._uninstall_cleanup_handlers()

        session_dir = store.session_dir
        assert session_dir.exists()

        store.record("a.py", Signal.LINES, 100, "scanning")
        store.cleanup()

        assert not session_dir.exists()

    def test_cleanup_clears_memory(self):
        """cleanup() clears all in-memory records."""
        store = ProvenanceStore(persist=True, session_id="cleanup_mem_test")
        store._uninstall_cleanup_handlers()

        store.record("a.py", Signal.LINES, 100, "scanning")
        assert store.record_count == 1

        store.cleanup()
        assert store.record_count == 0
        assert store.get_latest("a.py", Signal.LINES) is None

    def test_cleanup_idempotent(self):
        """cleanup() can be called multiple times safely."""
        store = ProvenanceStore(persist=True, session_id="cleanup_idem_test")
        store._uninstall_cleanup_handlers()

        store.record("a.py", Signal.LINES, 100, "scanning")
        store.cleanup()
        store.cleanup()  # Should not raise

    def test_cleanup_non_persistent(self, store):
        """cleanup() on non-persistent store just clears memory."""
        store.record("a.py", Signal.LINES, 100, "scanning")
        store.cleanup()
        assert store.record_count == 0

    def test_clear_does_not_remove_files(self):
        """clear() only clears memory, not disk files."""
        store = ProvenanceStore(persist=True, session_id="clear_vs_cleanup_test")
        store._uninstall_cleanup_handlers()

        store.record("a.py", Signal.LINES, 100, "scanning")
        prov_file = store.provenance_file

        store.clear()
        assert store.record_count == 0
        # File should still exist
        assert prov_file.exists()

        # Clean up
        store.cleanup()


class TestCleanupHandlers:
    """Tests for atexit and signal handler installation."""

    def test_handlers_installed(self):
        """Handlers are installed when persisting."""
        store = ProvenanceStore(persist=True, session_id="handlers_test")
        assert store._handlers_installed
        store._uninstall_cleanup_handlers()
        store.cleanup()

    def test_handlers_not_installed_non_persistent(self, store):
        """Handlers are not installed for non-persistent stores."""
        assert not store._handlers_installed

    def test_uninstall_handlers(self):
        """Handlers can be cleanly uninstalled."""
        store = ProvenanceStore(persist=True, session_id="uninstall_test")
        assert store._handlers_installed
        store._uninstall_cleanup_handlers()
        assert not store._handlers_installed
        store.cleanup()

    def test_uninstall_without_install(self, store):
        """Uninstalling without installing is safe."""
        store._uninstall_cleanup_handlers()  # Should not raise

    def test_atexit_handler_marks_done(self):
        """atexit handler sets _cleanup_done flag."""
        store = ProvenanceStore(persist=True, session_id="atexit_flag_test")
        store._uninstall_cleanup_handlers()

        assert not store._cleanup_done
        store._cleanup_handler()
        assert store._cleanup_done

        # Calling again should be no-op
        store._cleanup_handler()

    def test_atexit_handler_removes_dir(self):
        """atexit handler removes the session directory."""
        store = ProvenanceStore(persist=True, session_id="atexit_dir_test")
        store._uninstall_cleanup_handlers()

        session_dir = store.session_dir
        assert session_dir.exists()

        store._cleanup_handler()
        assert not session_dir.exists()


# ---------------------------------------------------------------------------
# Stale session cleanup
# ---------------------------------------------------------------------------


class TestStaleSessionCleanup:
    """Tests for cleanup_stale_sessions()."""

    def test_removes_old_dirs(self, tmp_temp_dir):
        """Removes directories older than retention period."""
        # Create an "old" session dir
        old_dir = tmp_temp_dir / f"{TEMP_DIR_PREFIX}old_session"
        old_dir.mkdir()
        (old_dir / "provenance.jsonl").write_text('{"signal":"lines"}\n')

        # Make it appear old (set mtime to 25 hours ago)
        old_time = time.time() - (25 * 3600)
        os.utime(old_dir, (old_time, old_time))

        # Create a "recent" session dir
        recent_dir = tmp_temp_dir / f"{TEMP_DIR_PREFIX}recent_session"
        recent_dir.mkdir()
        (recent_dir / "provenance.jsonl").write_text('{"signal":"lines"}\n')

        deleted = cleanup_stale_sessions(retention_hours=24)
        assert deleted == 1
        assert not old_dir.exists()
        assert recent_dir.exists()

    def test_skips_recent_dirs(self, tmp_temp_dir):
        """Does not remove recent directories."""
        recent_dir = tmp_temp_dir / f"{TEMP_DIR_PREFIX}fresh_session"
        recent_dir.mkdir()

        deleted = cleanup_stale_sessions(retention_hours=24)
        assert deleted == 0
        assert recent_dir.exists()

    def test_skips_non_directories(self, tmp_temp_dir):
        """Skips files matching the prefix pattern."""
        file_path = tmp_temp_dir / f"{TEMP_DIR_PREFIX}not_a_dir.txt"
        file_path.write_text("not a directory\n")

        deleted = cleanup_stale_sessions(retention_hours=0)
        assert deleted == 0
        assert file_path.exists()

    def test_empty_temp_dir(self, tmp_temp_dir):
        """No errors when temp dir has no matching dirs."""
        deleted = cleanup_stale_sessions(retention_hours=24)
        assert deleted == 0

    def test_custom_retention(self, tmp_temp_dir):
        """Custom retention period is respected."""
        # Create a session dir modified 2 hours ago
        old_dir = tmp_temp_dir / f"{TEMP_DIR_PREFIX}two_hours_old"
        old_dir.mkdir()
        old_time = time.time() - (2 * 3600)
        os.utime(old_dir, (old_time, old_time))

        # 1-hour retention should delete it
        deleted = cleanup_stale_sessions(retention_hours=1)
        assert deleted == 1

    def test_retention_hours_boundary(self, tmp_temp_dir):
        """Dir exactly at retention boundary is NOT deleted (needs to be strictly older)."""
        # Create a session dir modified slightly less than 24 hours ago
        edge_dir = tmp_temp_dir / f"{TEMP_DIR_PREFIX}edge_case"
        edge_dir.mkdir()
        # 23 hours 59 minutes ago
        edge_time = time.time() - (23 * 3600 + 59 * 60)
        os.utime(edge_dir, (edge_time, edge_time))

        deleted = cleanup_stale_sessions(retention_hours=24)
        assert deleted == 0
        assert edge_dir.exists()

    def test_default_retention_hours(self):
        """Default retention is 24 hours."""
        assert DEFAULT_RETENTION_HOURS == 24


# ---------------------------------------------------------------------------
# FactStore integration
# ---------------------------------------------------------------------------


class TestFactStoreComputationTree:
    """Tests for FactStore.get_computation_tree() delegation."""

    def test_computation_tree_enabled(self):
        """get_computation_tree works when provenance is enabled."""
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(
            root="/tmp/test",
            enable_provenance=True,
            provenance_persist=False,
        )
        entity = EntityId(EntityType.FILE, "src/main.py")

        store.set_signal(entity, Signal.IN_DEGREE, 5, producer="structural")
        store.set_signal(
            entity,
            Signal.PAGERANK,
            0.042,
            producer="structural",
            inputs=["in_degree"],
            formula="PR(v) = ...",
        )

        tree = store.get_computation_tree(entity, Signal.PAGERANK)
        assert tree["signal"] == "pagerank"
        assert tree["value"] == 0.042
        assert len(tree["children"]) == 1
        assert tree["children"][0]["signal"] == "in_degree"

    def test_computation_tree_disabled(self):
        """get_computation_tree returns empty dict when provenance is disabled."""
        from shannon_insight.infrastructure.entities import EntityId, EntityType
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(root="/tmp/test", enable_provenance=False)
        entity = EntityId(EntityType.FILE, "src/main.py")

        tree = store.get_computation_tree(entity, Signal.PAGERANK)
        assert tree == {}

    def test_factstore_provenance_persist_flag(self):
        """FactStore can pass persist=False to ProvenanceStore."""
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(
            root="/tmp/test",
            enable_provenance=True,
            provenance_persist=False,
        )
        assert store.provenance is not None
        assert store.provenance.session_dir is None  # Not persisting

    def test_factstore_provenance_session_id(self):
        """FactStore can pass custom session_id to ProvenanceStore."""
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(
            root="/tmp/test",
            enable_provenance=True,
            provenance_session_id="custom_id",
            provenance_persist=False,
        )
        assert store.provenance.session_id == "custom_id"

    def test_factstore_provenance_retention_hours(self):
        """FactStore can pass custom retention_hours to ProvenanceStore."""
        from shannon_insight.infrastructure.store import FactStore

        store = FactStore(
            root="/tmp/test",
            enable_provenance=True,
            provenance_retention_hours=48,
            provenance_persist=False,
        )
        assert store.provenance._retention_hours == 48


# ---------------------------------------------------------------------------
# Config integration
# ---------------------------------------------------------------------------


class TestConfigIntegration:
    """Tests for config.enable_provenance and config.provenance_retention_hours."""

    def test_config_defaults(self):
        """Provenance config defaults are correct."""
        from shannon_insight.config import AnalysisConfig

        config = AnalysisConfig()
        assert config.enable_provenance is False
        assert config.provenance_retention_hours == 24

    def test_config_enable_provenance(self):
        """enable_provenance can be set to True."""
        from shannon_insight.config import AnalysisConfig

        config = AnalysisConfig(enable_provenance=True)
        assert config.enable_provenance is True

    def test_config_custom_retention(self):
        """provenance_retention_hours can be customized."""
        from shannon_insight.config import AnalysisConfig

        config = AnalysisConfig(provenance_retention_hours=48)
        assert config.provenance_retention_hours == 48

    def test_config_retention_zero(self):
        """Zero retention is valid (always clean up)."""
        from shannon_insight.config import AnalysisConfig

        config = AnalysisConfig(provenance_retention_hours=0)
        assert config.provenance_retention_hours == 0

    def test_config_retention_negative_raises(self):
        """Negative retention raises ValueError."""
        from shannon_insight.config import AnalysisConfig

        with pytest.raises(ValueError, match="provenance_retention_hours"):
            AnalysisConfig(provenance_retention_hours=-1)

    def test_config_env_var_enable_provenance(self):
        """SHANNON_ENABLE_PROVENANCE env var is respected."""
        from shannon_insight.config import load_config

        with patch.dict(os.environ, {"SHANNON_ENABLE_PROVENANCE": "true"}):
            config = load_config()
            assert config.enable_provenance is True

    def test_config_env_var_retention(self):
        """SHANNON_PROVENANCE_RETENTION_HOURS env var is respected."""
        from shannon_insight.config import load_config

        with patch.dict(os.environ, {"SHANNON_PROVENANCE_RETENTION_HOURS": "48"}):
            config = load_config()
            assert config.provenance_retention_hours == 48


# ---------------------------------------------------------------------------
# Temp base directory
# ---------------------------------------------------------------------------


class TestTempBase:
    """Tests for _get_temp_base()."""

    def test_returns_path(self):
        """Returns a Path object."""
        result = _get_temp_base()
        assert isinstance(result, Path)

    def test_directory_exists(self):
        """Returns an existing directory."""
        result = _get_temp_base()
        assert result.exists()
        assert result.is_dir()

    def test_matches_tempfile_gettempdir(self):
        """Returns the same path as tempfile.gettempdir()."""
        result = _get_temp_base()
        assert str(result) == tempfile.gettempdir()


# ---------------------------------------------------------------------------
# Edge cases and resource safety
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Tests for edge cases and resource safety."""

    def test_record_after_close_file(self):
        """Recording after file handle is closed doesn't crash."""
        store = ProvenanceStore(persist=True, session_id="close_file_test")
        store._uninstall_cleanup_handlers()

        store.record("a.py", Signal.LINES, 100, "scanning")
        store._close_file()
        # Should not raise - just silently skip disk write
        store.record("a.py", Signal.FUNCTION_COUNT, 5, "scanning")
        assert store.record_count == 2

        store.cleanup()

    def test_cleanup_after_dir_already_removed(self):
        """cleanup() is safe even if session dir was already removed."""
        store = ProvenanceStore(persist=True, session_id="removed_dir_test")
        store._uninstall_cleanup_handlers()

        # Manually remove the dir
        shutil.rmtree(store.session_dir)
        # Should not raise
        store.cleanup()

    def test_multiple_stores_different_sessions(self):
        """Multiple stores with different session IDs don't conflict."""
        store1 = ProvenanceStore(persist=True, session_id="multi_1")
        store2 = ProvenanceStore(persist=True, session_id="multi_2")

        store1._uninstall_cleanup_handlers()
        store2._uninstall_cleanup_handlers()

        try:
            store1.record("a.py", Signal.LINES, 100, "scanning")
            store2.record("a.py", Signal.LINES, 200, "scanning")

            assert store1.get_latest("a.py", Signal.LINES).value == 100
            assert store2.get_latest("a.py", Signal.LINES).value == 200

            assert store1.session_dir != store2.session_dir
        finally:
            store1.cleanup()
            store2.cleanup()

    def test_store_with_complex_values(self, store):
        """Computation tree handles complex values."""
        store.record(
            "a.py",
            Signal.RISK_SCORE,
            {"component1": 0.3, "component2": 0.5},
            "fusion",
        )

        tree = store.get_computation_tree("a.py", Signal.RISK_SCORE)
        assert tree["value"] == {"component1": 0.3, "component2": 0.5}

    def test_persistent_store_records_valid_json(self):
        """All records on disk are valid JSON."""
        store = ProvenanceStore(persist=True, session_id="json_valid_test")
        store._uninstall_cleanup_handlers()

        try:
            # Record various types of values
            store.record("a.py", Signal.LINES, 100, "scanning")
            store.record("a.py", Signal.PAGERANK, 0.042, "structural")
            store.record("a.py", Signal.ROLE, "model", "semantic")
            store.record("a.py", Signal.IS_ORPHAN, True, "graph")
            store.record(
                "a.py",
                Signal.RISK_SCORE,
                0.8,
                "fusion",
                inputs=["pagerank", "lines"],
                formula="risk = 0.3*pr + 0.7*lines_pctl",
            )

            with open(store.provenance_file) as f:
                lines = f.readlines()

            assert len(lines) == 5
            for line in lines:
                record = json.loads(line)
                assert "signal" in record
                assert "value" in record
                assert "producer" in record
                assert "phase" in record
                assert "timestamp" in record
                assert "inputs" in record
                assert "entity_path" in record
        finally:
            store.cleanup()
