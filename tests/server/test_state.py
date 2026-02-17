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
        # State updates are wrapped with type: complete
        assert msg["type"] == "complete"
        assert msg["state"] == data

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

    def test_previous_state_tracking(self):
        """Update twice, verify get_previous_state returns the first state."""
        state = ServerState()
        first = {"health": 5.0, "version": 1}
        second = {"health": 7.0, "version": 2}

        state.update(first)
        state.update(second)

        previous = state.get_previous_state()
        assert previous is not None
        assert previous == first
        assert previous["version"] == 1

        current = state.get_state()
        assert current is not None
        assert current["version"] == 2

    def test_recent_changes(self):
        """set_recent_changes, verify get_recent_changes returns them."""
        state = ServerState()
        paths = ["src/foo.py", "src/bar.py", "tests/test_foo.py"]

        state.set_recent_changes(paths)
        result = state.get_recent_changes()

        assert result == paths
        # Verify it returns a copy, not the original list
        result.append("extra.py")
        assert state.get_recent_changes() == paths

    def test_progress_with_percent(self):
        """send_progress with percent parameter, verify it's in the message."""
        state = ServerState()
        q: queue.Queue = queue.Queue()
        state.add_listener(q)

        state.send_progress("Analyzing files...", phase="analyze", percent=42.5)

        msg = q.get(timeout=1)
        assert msg["type"] == "progress"
        assert msg["message"] == "Analyzing files..."
        assert msg["phase"] == "analyze"
        assert msg["percent"] == 42.5


class TestQueueOverflowHandling:
    """Verify graceful degradation when client queues fill up."""

    def test_update_handles_full_queue_gracefully(self):
        """update() handles full queue without raising (drops message)."""
        import asyncio

        state = ServerState()
        # Create a small bounded queue
        q: asyncio.Queue = asyncio.Queue(maxsize=2)
        state.add_listener(q)

        # Fill the queue
        try:
            q.put_nowait({"msg": 1})
            q.put_nowait({"msg": 2})
        except asyncio.QueueFull:
            pass

        # This should not raise even though queue is full
        state.update({"health": 7.0})

        # State should still be updated
        assert state.get_state() == {"health": 7.0}

    def test_send_progress_handles_full_queue_gracefully(self):
        """send_progress() handles full queue without raising."""
        import asyncio

        state = ServerState()
        q: asyncio.Queue = asyncio.Queue(maxsize=2)
        state.add_listener(q)

        # Fill the queue
        try:
            q.put_nowait({"msg": 1})
            q.put_nowait({"msg": 2})
        except asyncio.QueueFull:
            pass

        # This should not raise even though queue is full
        state.send_progress("Testing...", phase="test")

        # No exception means success
