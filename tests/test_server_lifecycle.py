"""Tests for server process management and lifecycle.

Tests PID file management, port selection, stale cleanup,
and the shutdown manager.
"""

import json
import os
import socket
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shannon_insight.server.process import (
    DEFAULT_PORT,
    ServerInfo,
    _is_port_in_use,
    _is_process_alive,
    _pid_file_path,
    check_port_ownership,
    cleanup_stale_pid_files,
    find_available_port,
    read_pid_file,
    remove_pid_file,
    validate_existing_server,
    write_pid_file,
)

# ── ServerInfo ────────────────────────────────────────────────────


class TestServerInfo:
    def test_round_trip(self):
        info = ServerInfo(pid=1234, port=8765, project_path="/tmp/myproject")
        data = info.to_dict()
        restored = ServerInfo.from_dict(data)
        assert restored.pid == 1234
        assert restored.port == 8765
        assert restored.project_path == "/tmp/myproject"

    def test_to_dict_keys(self):
        info = ServerInfo(pid=1, port=2, project_path="/x")
        d = info.to_dict()
        assert set(d.keys()) == {"pid", "port", "project_path"}


# ── PID file read/write/remove ────────────────────────────────────


class TestPidFile:
    def test_write_and_read(self, tmp_path):
        project = str(tmp_path)
        write_pid_file(project, 8765)
        info = read_pid_file(project)
        assert info is not None
        assert info.pid == os.getpid()
        assert info.port == 8765
        assert info.project_path == str(tmp_path.resolve())

    def test_read_nonexistent(self, tmp_path):
        assert read_pid_file(str(tmp_path)) is None

    def test_read_malformed(self, tmp_path):
        pid_path = tmp_path / ".shannon" / "server.pid"
        pid_path.parent.mkdir(parents=True)
        pid_path.write_text("this is not json")
        assert read_pid_file(str(tmp_path)) is None

    def test_read_missing_keys(self, tmp_path):
        pid_path = tmp_path / ".shannon" / "server.pid"
        pid_path.parent.mkdir(parents=True)
        pid_path.write_text(json.dumps({"pid": 1}))  # Missing port and project_path
        assert read_pid_file(str(tmp_path)) is None

    def test_remove_existing(self, tmp_path):
        project = str(tmp_path)
        write_pid_file(project, 8765)
        assert remove_pid_file(project) is True
        assert read_pid_file(project) is None

    def test_remove_nonexistent(self, tmp_path):
        assert remove_pid_file(str(tmp_path)) is False

    def test_creates_shannon_dir(self, tmp_path):
        project = str(tmp_path)
        assert not (tmp_path / ".shannon").exists()
        write_pid_file(project, 8765)
        assert (tmp_path / ".shannon").is_dir()
        assert (tmp_path / ".shannon" / "server.pid").is_file()

    def test_pid_file_path(self, tmp_path):
        expected = tmp_path / ".shannon" / "server.pid"
        assert _pid_file_path(str(tmp_path)) == expected


# ── Process alive check ───────────────────────────────────────────


class TestIsProcessAlive:
    def test_current_process_is_alive(self):
        assert _is_process_alive(os.getpid()) is True

    def test_dead_pid(self):
        # PID 99999999 almost certainly doesn't exist
        assert _is_process_alive(99999999) is False

    def test_pid_zero(self):
        # PID 0 is special (kernel), should return True on most systems
        # But we just check it doesn't crash
        result = _is_process_alive(0)
        assert isinstance(result, bool)


# ── Port in use check ────────────────────────────────────────────


class TestIsPortInUse:
    def test_unused_port(self):
        # Find a port that's definitely not in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        _, port = sock.getsockname()
        sock.close()
        # Port was just released, should be free
        assert _is_port_in_use("127.0.0.1", port) is False

    def test_used_port(self):
        # Bind a port and check it's detected as in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        _, port = sock.getsockname()
        try:
            assert _is_port_in_use("127.0.0.1", port) is True
        finally:
            sock.close()


# ── Validate existing server ─────────────────────────────────────


class TestValidateExistingServer:
    def test_no_pid_file(self, tmp_path):
        result = validate_existing_server(str(tmp_path), "127.0.0.1")
        assert result is None

    def test_stale_pid_file_dead_process(self, tmp_path):
        # Write a PID file for a dead process
        pid_path = tmp_path / ".shannon" / "server.pid"
        pid_path.parent.mkdir(parents=True)
        info = ServerInfo(pid=99999999, port=8765, project_path=str(tmp_path))
        pid_path.write_text(json.dumps(info.to_dict()))

        result = validate_existing_server(str(tmp_path), "127.0.0.1")
        assert result is None
        # Should have cleaned up the stale file
        assert not pid_path.exists()

    def test_alive_process_but_port_not_bound(self, tmp_path):
        # Write a PID file for current process (alive) but port not bound
        pid_path = tmp_path / ".shannon" / "server.pid"
        pid_path.parent.mkdir(parents=True)
        info = ServerInfo(pid=os.getpid(), port=59999, project_path=str(tmp_path))
        pid_path.write_text(json.dumps(info.to_dict()))

        result = validate_existing_server(str(tmp_path), "127.0.0.1")
        assert result is None
        # Should have cleaned up
        assert not pid_path.exists()

    def test_alive_process_and_port_bound(self, tmp_path):
        # Bind a port, write PID file, check it's detected
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        _, port = sock.getsockname()

        try:
            pid_path = tmp_path / ".shannon" / "server.pid"
            pid_path.parent.mkdir(parents=True)
            info = ServerInfo(pid=os.getpid(), port=port, project_path=str(tmp_path))
            pid_path.write_text(json.dumps(info.to_dict()))

            result = validate_existing_server(str(tmp_path), "127.0.0.1")
            assert result is not None
            assert result.pid == os.getpid()
            assert result.port == port
        finally:
            sock.close()


# ── Find available port ──────────────────────────────────────────


class TestFindAvailablePort:
    def test_preferred_port_available(self):
        # Use a high port unlikely to be in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        _, port = sock.getsockname()
        sock.close()

        result = find_available_port("127.0.0.1", preferred_port=port)
        assert result == port

    def test_preferred_port_in_use_finds_next(self):
        # Mock _is_port_in_use: first call (preferred) returns True, rest return False
        call_count = [0]

        def mock_port_check(host, port):
            call_count[0] += 1
            if call_count[0] == 1:
                return True  # Preferred port "in use"
            return False  # Next port is "free"

        with patch("shannon_insight.server.process._is_port_in_use", side_effect=mock_port_check):
            with patch("shannon_insight.server.process.read_pid_file", return_value=None):
                result = find_available_port("127.0.0.1", preferred_port=DEFAULT_PORT)

        assert result == DEFAULT_PORT + 1

    def test_all_ports_in_use_raises(self):
        # Mock _is_port_in_use to always return True
        with patch("shannon_insight.server.process._is_port_in_use", return_value=True):
            with patch("shannon_insight.server.process.read_pid_file", return_value=None):
                with pytest.raises(RuntimeError, match="No available ports"):
                    find_available_port("127.0.0.1", preferred_port=DEFAULT_PORT)


# ── Check port ownership ─────────────────────────────────────────


class TestCheckPortOwnership:
    def test_available_port(self, tmp_path):
        result = check_port_ownership("127.0.0.1", 59998, str(tmp_path))
        assert result == "available"

    def test_same_project_port(self, tmp_path):
        # Bind a port and write PID file
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        _, port = sock.getsockname()

        try:
            write_pid_file(str(tmp_path), port)
            result = check_port_ownership("127.0.0.1", port, str(tmp_path))
            assert result == "same_project"
        finally:
            sock.close()
            remove_pid_file(str(tmp_path))

    def test_external_port(self):
        # Bind a port without a PID file
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        _, port = sock.getsockname()

        try:
            result = check_port_ownership("127.0.0.1", port, "/nonexistent/project")
            assert result == "external"
        finally:
            sock.close()


# ── Cleanup stale PID files ──────────────────────────────────────


class TestCleanupStalePidFiles:
    def test_cleans_dead_process(self, tmp_path):
        pid_path = tmp_path / ".shannon" / "server.pid"
        pid_path.parent.mkdir(parents=True)
        info = ServerInfo(pid=99999999, port=8765, project_path=str(tmp_path))
        pid_path.write_text(json.dumps(info.to_dict()))

        cleanup_stale_pid_files(str(tmp_path))
        assert not pid_path.exists()

    def test_leaves_alive_process(self, tmp_path):
        pid_path = tmp_path / ".shannon" / "server.pid"
        pid_path.parent.mkdir(parents=True)
        info = ServerInfo(pid=os.getpid(), port=8765, project_path=str(tmp_path))
        pid_path.write_text(json.dumps(info.to_dict()))

        cleanup_stale_pid_files(str(tmp_path))
        assert pid_path.exists()

    def test_no_pid_file(self, tmp_path):
        # Should not raise
        cleanup_stale_pid_files(str(tmp_path))


# ── ShutdownManager ──────────────────────────────────────────────


class TestShutdownManager:
    def test_shutdown_idempotent(self, tmp_path):
        from rich.console import Console

        from shannon_insight.server.lifecycle import ShutdownManager

        console = Console(file=open(os.devnull, "w"))
        write_pid_file(str(tmp_path), 8765)

        mgr = ShutdownManager(str(tmp_path), console)

        # First shutdown
        mgr.shutdown()
        assert mgr._shutdown_complete is True

        # Second shutdown should be a no-op
        mgr.shutdown()
        assert mgr._shutdown_complete is True

    def test_shutdown_removes_pid_file(self, tmp_path):
        from rich.console import Console

        from shannon_insight.server.lifecycle import ShutdownManager

        console = Console(file=open(os.devnull, "w"))
        write_pid_file(str(tmp_path), 8765)

        mgr = ShutdownManager(str(tmp_path), console)
        mgr.shutdown()

        assert not (tmp_path / ".shannon" / "server.pid").exists()

    def test_shutdown_stops_watcher(self, tmp_path):
        from rich.console import Console

        from shannon_insight.server.lifecycle import ShutdownManager

        console = Console(file=open(os.devnull, "w"))

        mock_watcher = MagicMock()
        mgr = ShutdownManager(str(tmp_path), console)
        mgr.register_watcher(mock_watcher)
        mgr.shutdown()

        mock_watcher.stop.assert_called_once()

    def test_shutdown_signals_uvicorn(self, tmp_path):
        from rich.console import Console

        from shannon_insight.server.lifecycle import ShutdownManager

        console = Console(file=open(os.devnull, "w"))

        mock_server = MagicMock()
        mock_server.should_exit = False
        mgr = ShutdownManager(str(tmp_path), console)
        mgr.register_uvicorn(mock_server)
        mgr.shutdown()

        assert mock_server.should_exit is True

    def test_shutdown_clears_websocket_listeners(self, tmp_path):
        from rich.console import Console

        from shannon_insight.server.lifecycle import ShutdownManager
        from shannon_insight.server.state import ServerState

        console = Console(file=open(os.devnull, "w"))

        state = ServerState()
        state._listeners = [MagicMock(), MagicMock()]  # Simulate 2 clients

        mgr = ShutdownManager(str(tmp_path), console)
        mgr.register_state(state)
        mgr.shutdown()

        assert len(state._listeners) == 0


# ── Integration: concurrent access ───────────────────────────────


class TestConcurrentAccess:
    def test_concurrent_pid_writes(self, tmp_path):
        """Multiple threads writing PID files shouldn't corrupt data."""
        results = []

        def write_and_read(project_dir, port):
            write_pid_file(project_dir, port)
            info = read_pid_file(project_dir)
            results.append(info)

        threads = []
        for i in range(5):
            project = str(tmp_path / f"project_{i}")
            Path(project).mkdir()
            t = threading.Thread(target=write_and_read, args=(project, 8765 + i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=5)

        # All reads should have succeeded
        assert len(results) == 5
        for info in results:
            assert info is not None
            assert info.pid == os.getpid()
