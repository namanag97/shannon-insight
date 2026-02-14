"""PID file and port management for the Shannon Insight server.

Handles:
- PID file lifecycle (write, read, validate, cleanup)
- Smart port selection (reuse for same project, find next for different)
- Stale PID file detection and cleanup
- Process validation (is the PID still alive?)
"""

from __future__ import annotations

import json
import logging
import os
import signal
import socket
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Port range for auto-selection
DEFAULT_PORT = 8765
MAX_PORT = 8785  # Try up to 20 ports


@dataclass
class ServerInfo:
    """Information about a running (or formerly running) server instance."""

    pid: int
    port: int
    project_path: str

    def to_dict(self) -> dict:
        return {
            "pid": self.pid,
            "port": self.port,
            "project_path": self.project_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ServerInfo:
        return cls(
            pid=data["pid"],
            port=data["port"],
            project_path=data["project_path"],
        )


def _pid_file_path(project_root: str) -> Path:
    """Return the PID file path for a project."""
    return Path(project_root) / ".shannon" / "server.pid"


def _is_process_alive(pid: int) -> bool:
    """Check if a process with the given PID is still running."""
    try:
        os.kill(pid, 0)  # Signal 0 = check existence, don't actually kill
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it (different user)
        return True
    except OSError:
        return False


def _is_port_in_use(host: str, port: int) -> bool:
    """Check if a port is currently bound."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


def read_pid_file(project_root: str) -> ServerInfo | None:
    """Read and parse the PID file for a project.

    Returns None if the file doesn't exist or is malformed.
    """
    pid_path = _pid_file_path(project_root)
    if not pid_path.exists():
        return None

    try:
        data = json.loads(pid_path.read_text())
        return ServerInfo.from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Malformed PID file at %s: %s", pid_path, exc)
        return None


def write_pid_file(project_root: str, port: int) -> Path:
    """Write PID file with current process information.

    Creates .shannon/ directory if it doesn't exist.
    Returns the path to the written PID file.
    """
    pid_path = _pid_file_path(project_root)
    pid_path.parent.mkdir(parents=True, exist_ok=True)

    info = ServerInfo(
        pid=os.getpid(),
        port=port,
        project_path=str(Path(project_root).resolve()),
    )

    pid_path.write_text(json.dumps(info.to_dict(), indent=2) + "\n")
    logger.debug("PID file written: %s", pid_path)
    return pid_path


def remove_pid_file(project_root: str) -> bool:
    """Remove the PID file for a project.

    Returns True if file was removed, False if it didn't exist.
    """
    pid_path = _pid_file_path(project_root)
    try:
        pid_path.unlink()
        logger.debug("PID file removed: %s", pid_path)
        return True
    except FileNotFoundError:
        return False


def validate_existing_server(project_root: str, host: str) -> ServerInfo | None:
    """Check if a server is already running for this project.

    Validates that:
    1. PID file exists
    2. Process is still alive
    3. Port is actually bound

    If PID file exists but process is dead, cleans up the stale file.
    Returns ServerInfo if server is alive, None otherwise.
    """
    info = read_pid_file(project_root)
    if info is None:
        return None

    # Check if the recorded process is still alive
    if not _is_process_alive(info.pid):
        logger.info("Stale PID file found (process %d is dead), cleaning up", info.pid)
        remove_pid_file(project_root)
        return None

    # Check if the port is actually bound
    if not _is_port_in_use(host, info.port):
        logger.info(
            "PID file exists (process %d alive) but port %d not bound, cleaning up",
            info.pid,
            info.port,
        )
        remove_pid_file(project_root)
        return None

    # Server is genuinely running
    return info


def find_available_port(
    host: str,
    preferred_port: int = DEFAULT_PORT,
    project_root: str | None = None,
) -> int:
    """Find an available port, starting from preferred_port.

    If preferred_port is in use:
    - Check if it's our own project (reuse it)
    - Otherwise, try the next port up to MAX_PORT

    Returns the port number to use.
    Raises RuntimeError if no port is available.
    """
    # First, try the preferred port
    if not _is_port_in_use(host, preferred_port):
        return preferred_port

    # Port is in use. Check if it's the same project
    if project_root is not None:
        info = read_pid_file(project_root)
        if info is not None and info.port == preferred_port:
            if _is_process_alive(info.pid):
                # Same project, same port, still alive - reuse
                return preferred_port

    # Port is in use by something else. Try next ports.
    for port in range(preferred_port + 1, MAX_PORT + 1):
        if not _is_port_in_use(host, port):
            return port

    raise RuntimeError(
        f"No available ports in range {preferred_port}-{MAX_PORT}. Stop some servers and try again."
    )


def check_port_ownership(host: str, port: int, project_root: str) -> str:
    """Determine who owns a port.

    Returns one of:
    - "available" - port is free
    - "same_project" - port is used by this project's server
    - "other_project" - port is used by another Shannon Insight server
    - "external" - port is used by a non-Shannon process
    """
    if not _is_port_in_use(host, port):
        return "available"

    info = read_pid_file(project_root)
    if info is not None and info.port == port and _is_process_alive(info.pid):
        return "same_project"

    # Could be another Shannon instance or an external process
    # We can't easily distinguish without scanning all .shannon dirs
    return "external"


def cleanup_stale_pid_files(project_root: str) -> None:
    """Clean up any stale PID files for this project."""
    info = read_pid_file(project_root)
    if info is not None and not _is_process_alive(info.pid):
        logger.info("Cleaning up stale PID file for dead process %d", info.pid)
        remove_pid_file(project_root)


def graceful_shutdown_existing(project_root: str, host: str) -> bool:
    """Try to gracefully shut down an existing server for this project.

    Sends SIGTERM to the process recorded in the PID file.
    Returns True if a signal was sent, False if no server was running.
    """
    info = validate_existing_server(project_root, host)
    if info is None:
        return False

    # Don't kill ourselves
    if info.pid == os.getpid():
        return False

    try:
        os.kill(info.pid, signal.SIGTERM)
        logger.info("Sent SIGTERM to existing server (PID %d)", info.pid)
        return True
    except ProcessLookupError:
        # Already dead
        remove_pid_file(project_root)
        return False
    except PermissionError:
        logger.warning("Cannot signal process %d (permission denied)", info.pid)
        return False
