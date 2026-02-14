"""Thread-safe shared state for the dashboard server."""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)


class ServerState:
    """Holds the latest analysis results for the dashboard.

    Thread-safe: the file watcher thread writes via :meth:`update`,
    the Starlette async handlers read via :meth:`get_state`.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._state: dict[str, Any] | None = None
        self._previous_state: dict[str, Any] | None = None
        self._recent_changes: list[str] = []
        self._listeners: list[Any] = []  # asyncio.Queue objects

    def update(self, state: dict[str, Any]) -> None:
        """Replace the current dashboard state (called from watcher thread)."""
        with self._lock:
            self._previous_state = self._state
            self._state = state
            # Copy listeners list to avoid mutation during iteration
            listeners = list(self._listeners)
        # Notify all WebSocket listeners
        for queue in listeners:
            try:
                # Check queue fullness and log warnings
                if hasattr(queue, "qsize") and hasattr(queue, "maxsize"):
                    size = queue.qsize()
                    maxsize = queue.maxsize
                    if maxsize and size > maxsize * 0.5:
                        logger.warning(
                            "WebSocket queue filling up: %d/%d (%.0f%% full)",
                            size,
                            maxsize,
                            100 * size / maxsize,
                        )
                queue.put_nowait(state)
            except asyncio.QueueFull:
                logger.error(
                    "WebSocket queue full, dropping state update (client may be slow or stuck)"
                )
            except Exception as exc:
                logger.debug("Failed to notify listener: %s", exc)

    def get_state(self) -> dict[str, Any] | None:
        """Return the latest dashboard state (called from async handlers)."""
        with self._lock:
            return self._state

    def get_previous_state(self) -> dict[str, Any] | None:
        """Return the previous dashboard state for computing diffs."""
        with self._lock:
            return self._previous_state

    def set_recent_changes(self, paths: list[str]) -> None:
        """Record recently changed file paths (called from watcher)."""
        with self._lock:
            self._recent_changes = list(paths)

    def get_recent_changes(self) -> list[str]:
        """Return recently changed file paths."""
        with self._lock:
            return list(self._recent_changes)

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

    def send_progress(self, message: str, phase: str = "", percent: float | None = None) -> None:
        """Broadcast a progress message to all WebSocket listeners."""
        msg: dict[str, Any] = {"type": "progress", "message": message, "phase": phase}
        if percent is not None:
            msg["percent"] = percent
        with self._lock:
            listeners = list(self._listeners)
        for queue in listeners:
            try:
                queue.put_nowait(msg)
            except Exception:
                pass
