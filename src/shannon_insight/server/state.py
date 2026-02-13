"""Thread-safe shared state for the dashboard server."""

from __future__ import annotations

import threading
from typing import Any


class ServerState:
    """Holds the latest analysis results for the dashboard.

    Thread-safe: the file watcher thread writes via :meth:`update`,
    the Starlette async handlers read via :meth:`get_state`.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._state: dict[str, Any] | None = None
        self._listeners: list[Any] = []  # asyncio.Queue objects

    def update(self, state: dict[str, Any]) -> None:
        """Replace the current dashboard state (called from watcher thread)."""
        with self._lock:
            self._state = state
            # Copy listeners list to avoid mutation during iteration
            listeners = list(self._listeners)
        # Notify all WebSocket listeners
        for queue in listeners:
            try:
                queue.put_nowait(state)
            except Exception:
                pass  # Queue full or closed — skip

    def get_state(self) -> dict[str, Any] | None:
        """Return the latest dashboard state (called from async handlers)."""
        with self._lock:
            return self._state

    def add_listener(self, queue: Any) -> None:
        """Register an asyncio.Queue to receive state updates."""
        with self._lock:
            self._listeners.append(queue)

    def remove_listener(self, queue: Any) -> None:
        """Unregister a listener queue."""
        with self._lock:
            try:
                self._listeners.remove(queue)
            except ValueError:
                pass

    def send_progress(self, message: str, phase: str = "") -> None:
        """Broadcast a progress message to all WebSocket listeners."""
        msg = {"type": "progress", "message": message, "phase": phase}
        with self._lock:
            listeners = list(self._listeners)
        for queue in listeners:
            try:
                queue.put_nowait(msg)
            except Exception:
                pass
