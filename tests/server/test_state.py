"""Tests for server.state.ServerState."""

import queue
import threading

from shannon_insight.server.state import ServerState


class TestServerState:
    """Thread-safe shared state tests."""

    def test_initial_state_is_none(self):
        state = ServerState()
        assert state.get_state() is None

    def test_update_and_get(self):
        state = ServerState()
        data = {"health": 7.2, "files": {}}
        state.update(data)
        assert state.get_state() == data

    def test_update_replaces(self):
        state = ServerState()
        state.update({"v": 1})
        state.update({"v": 2})
        result = state.get_state()
        assert result is not None
        assert result["v"] == 2

    def test_listener_receives_update(self):
        state = ServerState()
        q: queue.Queue = queue.Queue()
        state.add_listener(q)

        data = {"health": 5.0}
        state.update(data)

        msg = q.get(timeout=1)
        assert msg == data

    def test_remove_listener(self):
        state = ServerState()
        q: queue.Queue = queue.Queue()
        state.add_listener(q)
        state.remove_listener(q)

        state.update({"health": 5.0})
        assert q.empty()

    def test_progress_broadcast(self):
        state = ServerState()
        q: queue.Queue = queue.Queue()
        state.add_listener(q)

        state.send_progress("Scanning files...", phase="scan")

        msg = q.get(timeout=1)
        assert msg["type"] == "progress"
        assert msg["message"] == "Scanning files..."
        assert msg["phase"] == "scan"

    def test_thread_safety(self):
        """Multiple threads updating concurrently should not raise."""
        state = ServerState()
        errors = []

        def writer(n):
            try:
                for i in range(100):
                    state.update({"thread": n, "i": i})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(n,)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        result = state.get_state()
        assert result is not None
        assert "thread" in result
