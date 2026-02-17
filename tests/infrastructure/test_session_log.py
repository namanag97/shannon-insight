"""Tests for SessionLogManager."""

import json
import time
from datetime import datetime, timedelta

import pytest

from shannon_insight.infrastructure.provenance import ProvenanceStore
from shannon_insight.infrastructure.session_log import SessionLogManager
from shannon_insight.infrastructure.signals import Signal


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    return tmp_path


class TestSessionLogManager:
    """Tests for session log management."""

    def test_log_dir_path(self, tmp_project):
        """Log directory is .shannon/logs under project root."""
        manager = SessionLogManager(root=tmp_project)
        assert manager.log_dir == tmp_project / ".shannon" / "logs"

    def test_current_log_path(self, tmp_project):
        """Current log path includes session timestamp."""
        manager = SessionLogManager(root=tmp_project)
        log_path = manager.current_log_path
        assert log_path.parent == manager.log_dir
        assert log_path.name.startswith("session_")
        assert log_path.suffix == ".jsonl"

    def test_ensure_log_dir(self, tmp_project):
        """Creates log directory if it doesn't exist."""
        manager = SessionLogManager(root=tmp_project)
        assert not manager.log_dir.exists()

        manager.ensure_log_dir()
        assert manager.log_dir.exists()

    def test_write_log_empty(self, tmp_project):
        """Empty provenance store produces no log file."""
        manager = SessionLogManager(root=tmp_project)
        prov = ProvenanceStore()

        result = manager.write_log(prov)
        assert result is None

    def test_write_log(self, tmp_project):
        """Write provenance records to session log."""
        manager = SessionLogManager(root=tmp_project)
        prov = ProvenanceStore()
        prov.record("src/main.py", Signal.LINES, 150, "scanning")
        prov.record("src/main.py", Signal.FUNCTION_COUNT, 5, "scanning")

        log_path = manager.write_log(prov)
        assert log_path is not None
        assert log_path.exists()

        # Verify contents
        with open(log_path) as f:
            lines = f.readlines()
        assert len(lines) == 2

        record = json.loads(lines[0])
        assert record["signal"] == "lines"
        assert record["value"] == 150

    def test_cleanup_old_logs(self, tmp_project):
        """Delete logs older than retention period."""
        manager = SessionLogManager(root=tmp_project, retention_hours=1)
        manager.ensure_log_dir()

        # Create an "old" log file (timestamp 2 hours ago)
        old_time = datetime.now() - timedelta(hours=2)
        old_name = f"session_{old_time.strftime('%Y%m%d_%H%M%S')}.jsonl"
        old_file = manager.log_dir / old_name
        old_file.write_text('{"signal":"lines","value":100}\n')

        # Create a "recent" log file
        recent_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        recent_file = manager.log_dir / recent_name
        recent_file.write_text('{"signal":"lines","value":200}\n')

        deleted = manager.cleanup_old_logs()
        assert deleted == 1
        assert not old_file.exists()
        assert recent_file.exists()

    def test_cleanup_no_logs_dir(self, tmp_project):
        """Cleanup when log directory doesn't exist."""
        manager = SessionLogManager(root=tmp_project)
        deleted = manager.cleanup_old_logs()
        assert deleted == 0

    def test_cleanup_invalid_filename(self, tmp_project):
        """Cleanup skips files with unparseable timestamps."""
        manager = SessionLogManager(root=tmp_project, retention_hours=0)
        manager.ensure_log_dir()

        # Create a file with invalid timestamp format
        bad_file = manager.log_dir / "session_not_a_timestamp.jsonl"
        bad_file.write_text("bad\n")

        deleted = manager.cleanup_old_logs()
        assert deleted == 0
        assert bad_file.exists()

    def test_list_logs(self, tmp_project):
        """List logs newest first."""
        manager = SessionLogManager(root=tmp_project)
        manager.ensure_log_dir()

        # Create logs with different timestamps
        for i in range(3):
            ts = datetime.now() - timedelta(hours=i)
            name = f"session_{ts.strftime('%Y%m%d_%H%M%S')}.jsonl"
            log_file = manager.log_dir / name
            log_file.write_text(f'{{"order":{i}}}\n')
            # Ensure different mtime
            time.sleep(0.05)

        logs = manager.list_logs()
        assert len(logs) == 3
        # Newest first (highest mtime)
        assert logs[0].stat().st_mtime >= logs[1].stat().st_mtime

    def test_list_logs_empty(self, tmp_project):
        """List logs when none exist."""
        manager = SessionLogManager(root=tmp_project)
        assert manager.list_logs() == []

    def test_read_log(self, tmp_project):
        """Read a session log file."""
        manager = SessionLogManager(root=tmp_project)
        manager.ensure_log_dir()

        log_file = manager.log_dir / "session_20260115_103000.jsonl"
        log_file.write_text(
            '{"signal":"lines","value":100}\n{"signal":"function_count","value":5}\n'
        )

        records = manager.read_log(log_file)
        assert len(records) == 2
        assert records[0]["signal"] == "lines"
        assert records[1]["signal"] == "function_count"

    def test_retention_hours(self, tmp_project):
        """Custom retention period."""
        manager = SessionLogManager(root=tmp_project, retention_hours=48)
        assert manager.retention_hours == 48

    def test_session_id_format(self, tmp_project):
        """Session ID is a valid timestamp string."""
        manager = SessionLogManager(root=tmp_project)
        # Should be parseable as YYYYMMDD_HHMMSS
        datetime.strptime(manager.session_id, "%Y%m%d_%H%M%S")


class TestSessionLogHandlers:
    """Tests for atexit and signal handlers."""

    def test_install_handlers_idempotent(self, tmp_project):
        """Installing handlers twice is safe."""
        manager = SessionLogManager(root=tmp_project)
        manager.install_handlers()
        manager.install_handlers()  # Should not raise
        manager.uninstall_handlers()

    def test_uninstall_handlers(self, tmp_project):
        """Uninstalling handlers is safe."""
        manager = SessionLogManager(root=tmp_project)
        manager.install_handlers()
        manager.uninstall_handlers()
        assert not manager._handlers_installed

    def test_uninstall_without_install(self, tmp_project):
        """Uninstalling without installing is safe."""
        manager = SessionLogManager(root=tmp_project)
        manager.uninstall_handlers()  # Should not raise
