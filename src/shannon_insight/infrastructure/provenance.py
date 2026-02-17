"""Provenance tracking for signal computation.

Records HOW each signal was computed, by whom, from what inputs, and with
what formula. This enables:
    - `explain(entity, signal)` for human-readable computation traces
    - `get_computation_tree(entity, signal)` for full dependency trees as dicts
    - `trace(entity, signal)` for full dependency trees as lists
    - Persistent storage in `/tmp/shannon-insight-{session_id}/provenance.jsonl`

Provenance is optional (gated by config.enable_provenance / --trace flag) to
avoid overhead during normal analysis. When enabled, each `set_signal` call
also records a SignalProvenance entry.

Automatic cleanup:
    - Session cleanup on exit (atexit + SIGTERM/SIGINT)
    - Stale session cleanup (dirs older than provenance_retention_hours)

Usage:
    from shannon_insight.infrastructure.provenance import ProvenanceStore, SignalProvenance
    from shannon_insight.infrastructure.signals import Signal

    prov = ProvenanceStore(phase=0)
    prov.record(
        entity_path="src/main.py",
        signal=Signal.PAGERANK,
        value=0.042,
        producer="StructuralAnalyzer",
        inputs=["in_degree", "out_degree"],
        formula="PR(v) = (1-d)/N + d * sum(PR(u)/out(u))",
    )

    explanation = prov.explain("src/main.py", Signal.PAGERANK)
    # "PAGERANK = 0.042  (by StructuralAnalyzer, phase 0)
    #  Formula: PR(v) = (1-d)/N + d * sum(PR(u)/out(u))
    #  Inputs: in_degree, out_degree"
"""

from __future__ import annotations

import atexit
import json
import logging
import shutil
import signal as signal_module
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from shannon_insight.infrastructure.signals import Signal

logger = logging.getLogger(__name__)

# Prefix for temp directories
TEMP_DIR_PREFIX = "shannon-insight-"

# Default retention for stale sessions
DEFAULT_RETENTION_HOURS = 24


@dataclass
class SignalProvenance:
    """Records how a single signal value was computed.

    Attributes:
        signal: The Signal enum member that was computed.
        value: The computed value.
        producer: Name of the analyzer/module that produced it (e.g., "StructuralAnalyzer").
        phase: Analysis phase when this was computed (0-5).
        timestamp: When the computation occurred.
        inputs: Signal names used to compute this value.
        formula: Human-readable formula (None for raw/collected signals).
        entity_path: File/module/codebase path this signal applies to.
    """

    signal: Signal
    value: Any
    producer: str
    phase: int
    timestamp: datetime
    inputs: list[str]
    formula: str | None
    entity_path: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "signal": self.signal.value,
            "value": _serialize_value(self.value),
            "producer": self.producer,
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat(),
            "inputs": self.inputs,
            "formula": self.formula,
            "entity_path": self.entity_path,
        }


def _serialize_value(value: Any) -> Any:
    """Serialize a signal value for JSON output."""
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _serialize_value(v) for k, v in value.items()}
    # Fallback: convert to string
    return str(value)


def _get_temp_base() -> Path:
    """Get the base temporary directory for provenance storage.

    Returns /tmp on macOS/Linux. Uses tempfile.gettempdir() for portability.
    """
    return Path(tempfile.gettempdir())


def cleanup_stale_sessions(retention_hours: int = DEFAULT_RETENTION_HOURS) -> int:
    """Delete provenance directories older than retention_hours.

    Scans the system temp directory for shannon-insight-* directories
    and removes those whose modification time exceeds the retention period.

    This should be called at the START of every analysis run to prevent
    accumulation of stale provenance data.

    Args:
        retention_hours: Hours before a session directory is considered stale.

    Returns:
        Number of stale directories removed.
    """
    temp_base = _get_temp_base()
    cutoff = datetime.now() - timedelta(hours=retention_hours)
    deleted = 0

    try:
        for d in temp_base.glob(f"{TEMP_DIR_PREFIX}*"):
            if not d.is_dir():
                continue
            try:
                mtime = datetime.fromtimestamp(d.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(d, ignore_errors=True)
                    deleted += 1
                    logger.debug(f"Cleaned up stale provenance dir: {d.name}")
            except OSError as e:
                logger.debug(f"Skipping stale dir cleanup for {d.name}: {e}")
    except OSError as e:
        logger.debug(f"Error scanning temp directory for stale sessions: {e}")

    if deleted > 0:
        logger.debug(f"Cleaned up {deleted} stale provenance session(s)")

    return deleted


class ProvenanceStore:
    """Persistent store for signal provenance records.

    Records are stored both in-memory (for fast access) and on disk in a
    temp directory at `/tmp/shannon-insight-{session_id}/provenance.jsonl`.

    Disk persistence allows provenance to survive restarts and enables
    post-hoc debugging of analysis runs.

    Keyed by (entity_path, signal) pairs, storing the most recent
    provenance for each. Also maintains a full history for trace().

    Automatic cleanup is installed via atexit and signal handlers.
    """

    def __init__(
        self,
        phase: int = 0,
        session_id: str | None = None,
        retention_hours: int = DEFAULT_RETENTION_HOURS,
        persist: bool = True,
    ) -> None:
        """Initialize provenance store.

        Args:
            phase: Default phase for provenance records. Analyzers
                   override this when recording.
            session_id: Unique session identifier. If None, a timestamp-based
                       ID is generated.
            retention_hours: Hours to retain provenance data before cleanup.
            persist: Whether to persist records to disk. Set False for
                    testing or pure in-memory usage.
        """
        self._phase = phase
        self._session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self._retention_hours = retention_hours
        self._persist = persist

        # Latest provenance per (entity_path, signal)
        self._latest: dict[tuple[str, Signal], SignalProvenance] = {}
        # Full history per (entity_path, signal)
        self._history: dict[tuple[str, Signal], list[SignalProvenance]] = defaultdict(list)
        # All records in insertion order (for export)
        self._all_records: list[SignalProvenance] = []

        # Disk persistence
        self._session_dir: Path | None = None
        self._provenance_file: Path | None = None
        self._file_handle = None
        self._handlers_installed = False
        self._cleanup_done = False
        self._original_sigterm = None
        self._original_sigint = None

        if self._persist:
            self._init_persistence()
            self._install_cleanup_handlers()

    @property
    def session_id(self) -> str:
        """Unique session identifier."""
        return self._session_id

    @property
    def session_dir(self) -> Path | None:
        """Path to the session's temp directory, or None if not persisting."""
        return self._session_dir

    @property
    def provenance_file(self) -> Path | None:
        """Path to the provenance JSONL file, or None if not persisting."""
        return self._provenance_file

    @property
    def phase(self) -> int:
        """Current default phase."""
        return self._phase

    @phase.setter
    def phase(self, value: int) -> None:
        """Update the default phase (as analysis progresses)."""
        self._phase = value

    def _init_persistence(self) -> None:
        """Create the session temp directory and open the provenance file."""
        temp_base = _get_temp_base()
        self._session_dir = temp_base / f"{TEMP_DIR_PREFIX}{self._session_id}"
        try:
            self._session_dir.mkdir(parents=True, exist_ok=True)
            self._provenance_file = self._session_dir / "provenance.jsonl"
            # Open in append mode for write-through
            self._file_handle = open(self._provenance_file, "a")
        except OSError as e:
            logger.warning(
                f"Failed to create provenance directory: {e}. Falling back to in-memory."
            )
            self._persist = False
            self._session_dir = None
            self._provenance_file = None
            self._file_handle = None

    def _install_cleanup_handlers(self) -> None:
        """Install atexit and signal handlers for automatic cleanup.

        Registers:
        - atexit handler for normal Python exit
        - SIGTERM handler for process termination
        - SIGINT handler for Ctrl+C

        Safe to call multiple times (idempotent).
        """
        if self._handlers_installed:
            return

        atexit.register(self._cleanup_handler)

        try:
            self._original_sigterm = signal_module.signal(
                signal_module.SIGTERM, self._signal_handler
            )
        except (OSError, ValueError):
            # Can't set signal handler (e.g., not main thread)
            pass

        try:
            self._original_sigint = signal_module.signal(signal_module.SIGINT, self._signal_handler)
        except (OSError, ValueError):
            pass

        self._handlers_installed = True
        logger.debug(f"Provenance cleanup handlers installed for session {self._session_id}")

    def _uninstall_cleanup_handlers(self) -> None:
        """Remove signal handlers. Useful for testing."""
        if not self._handlers_installed:
            return

        try:
            if self._original_sigterm is not None:
                signal_module.signal(signal_module.SIGTERM, self._original_sigterm)
        except (OSError, ValueError):
            pass

        try:
            if self._original_sigint is not None:
                signal_module.signal(signal_module.SIGINT, self._original_sigint)
        except (OSError, ValueError):
            pass

        self._handlers_installed = False

    def _cleanup_handler(self) -> None:
        """Cleanup handler called on normal exit (atexit)."""
        if self._cleanup_done:
            return
        self._cleanup_done = True

        try:
            self._close_file()
            if self._session_dir and self._session_dir.exists():
                shutil.rmtree(self._session_dir, ignore_errors=True)
                logger.debug(f"Cleaned up provenance dir: {self._session_dir}")
        except Exception:
            # Don't let cleanup errors prevent exit
            pass

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Cleanup handler called on SIGTERM/SIGINT."""
        if not self._cleanup_done:
            self._cleanup_done = True
            try:
                self._close_file()
                if self._session_dir and self._session_dir.exists():
                    shutil.rmtree(self._session_dir, ignore_errors=True)
            except Exception:
                pass

        # Chain to original handler
        if signum == signal_module.SIGTERM and self._original_sigterm:
            if callable(self._original_sigterm):
                self._original_sigterm(signum, frame)
        elif signum == signal_module.SIGINT and self._original_sigint:
            if callable(self._original_sigint):
                self._original_sigint(signum, frame)
            else:
                raise KeyboardInterrupt

    def _close_file(self) -> None:
        """Close the file handle if open."""
        if self._file_handle is not None:
            try:
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None

    def _write_to_disk(self, prov: SignalProvenance) -> None:
        """Write a single provenance record to the JSONL file."""
        if self._file_handle is not None:
            try:
                self._file_handle.write(json.dumps(prov.to_dict()) + "\n")
                self._file_handle.flush()
            except OSError as e:
                logger.debug(f"Failed to write provenance to disk: {e}")

    def record(
        self,
        entity_path: str,
        signal: Signal,
        value: Any,
        producer: str,
        inputs: list[str] | None = None,
        formula: str | None = None,
        phase: int | None = None,
    ) -> SignalProvenance:
        """Record provenance for a signal computation.

        Records are stored both in-memory and on disk (if persistence is enabled).

        Args:
            entity_path: File/module/codebase path.
            signal: The Signal enum member computed.
            value: The computed value.
            producer: Name of the producing analyzer.
            inputs: Signal names used to compute this (empty list if raw).
            formula: Human-readable formula (None for raw signals).
            phase: Override default phase.

        Returns:
            The created SignalProvenance record.
        """
        prov = SignalProvenance(
            signal=signal,
            value=value,
            producer=producer,
            phase=phase if phase is not None else self._phase,
            timestamp=datetime.now(),
            inputs=inputs or [],
            formula=formula,
            entity_path=entity_path,
        )

        key = (entity_path, signal)
        self._latest[key] = prov
        self._history[key].append(prov)
        self._all_records.append(prov)

        # Write-through to disk
        if self._persist:
            self._write_to_disk(prov)

        return prov

    def explain(self, entity_path: str, signal: Signal) -> str:
        """Get human-readable explanation of how a signal was computed.

        Args:
            entity_path: File/module/codebase path.
            signal: The Signal enum member to explain.

        Returns:
            Multi-line explanation string. Returns a "no provenance" message
            if the signal was not recorded.
        """
        key = (entity_path, signal)
        prov = self._latest.get(key)

        if prov is None:
            return f"No provenance recorded for {signal.value} on {entity_path}"

        lines = [f"{signal.value} = {prov.value}  (by {prov.producer}, phase {prov.phase})"]

        if prov.formula:
            lines.append(f"  Formula: {prov.formula}")

        if prov.inputs:
            lines.append(f"  Inputs: {', '.join(prov.inputs)}")

            # Recursively explain inputs that we have provenance for
            for input_name in prov.inputs:
                try:
                    input_signal = Signal(input_name)
                    input_key = (entity_path, input_signal)
                    input_prov = self._latest.get(input_key)
                    if input_prov is not None:
                        lines.append(
                            f"    {input_name} = {input_prov.value}  (by {input_prov.producer})"
                        )
                except ValueError:
                    # Not a valid Signal enum value, skip
                    pass

        return "\n".join(lines)

    def get_computation_tree(self, entity_path: str, signal: Signal) -> dict:
        """Get the full dependency tree for a signal computation as a nested dict.

        Builds a tree structure where each node contains the signal's provenance
        metadata and a list of child nodes for input signals.

        Args:
            entity_path: File/module/codebase path.
            signal: The Signal enum member to trace.

        Returns:
            Dict with keys: signal, value, producer, phase, formula, inputs,
            children. Returns empty dict if no provenance exists.
        """
        visited: set[tuple[str, str]] = set()
        return self._build_tree(entity_path, signal, visited)

    def _build_tree(
        self,
        entity_path: str,
        signal: Signal,
        visited: set[tuple[str, str]],
    ) -> dict:
        """Recursively build the computation tree."""
        key_str = (entity_path, signal.value)
        if key_str in visited:
            return {"signal": signal.value, "cycle": True}
        visited.add(key_str)

        key = (entity_path, signal)
        prov = self._latest.get(key)
        if prov is None:
            return {}

        children = []
        for input_name in prov.inputs:
            try:
                input_signal = Signal(input_name)
                child = self._build_tree(entity_path, input_signal, visited)
                if child:
                    children.append(child)
            except ValueError:
                # External input, not a tracked signal
                children.append({"signal": input_name, "external": True})

        return {
            "signal": signal.value,
            "value": _serialize_value(prov.value),
            "producer": prov.producer,
            "phase": prov.phase,
            "formula": prov.formula,
            "inputs": prov.inputs,
            "children": children,
        }

    def trace(self, entity_path: str, signal: Signal) -> list[SignalProvenance]:
        """Get the full dependency tree for a signal computation.

        Recursively follows input signals to build a computation trace.
        Returns records in dependency order (inputs before outputs).

        Args:
            entity_path: File/module/codebase path.
            signal: The Signal enum member to trace.

        Returns:
            List of SignalProvenance records forming the dependency tree.
            Empty list if no provenance exists for this signal.
        """
        visited: set[tuple[str, str]] = set()
        result: list[SignalProvenance] = []
        self._trace_recursive(entity_path, signal, visited, result)
        return result

    def _trace_recursive(
        self,
        entity_path: str,
        signal: Signal,
        visited: set[tuple[str, str]],
        result: list[SignalProvenance],
    ) -> None:
        """Recursively build the dependency trace."""
        key_str = (entity_path, signal.value)
        if key_str in visited:
            return
        visited.add(key_str)

        key = (entity_path, signal)
        prov = self._latest.get(key)
        if prov is None:
            return

        # First, trace all inputs
        for input_name in prov.inputs:
            try:
                input_signal = Signal(input_name)
                self._trace_recursive(entity_path, input_signal, visited, result)
            except ValueError:
                pass

        # Then add this signal (inputs before outputs)
        result.append(prov)

    def export_session_log(self, path: str) -> None:
        """Export all provenance records to a JSON Lines file.

        Each line is a JSON object representing one SignalProvenance record.
        This format is easy to parse incrementally and grep-friendly.

        Args:
            path: File path to write the JSON Lines log to.
        """
        with open(path, "w") as f:
            for record in self._all_records:
                f.write(json.dumps(record.to_dict()) + "\n")

    @property
    def record_count(self) -> int:
        """Total number of provenance records."""
        return len(self._all_records)

    @property
    def all_records(self) -> list[SignalProvenance]:
        """All provenance records in insertion order."""
        return list(self._all_records)

    def get_latest(self, entity_path: str, signal: Signal) -> SignalProvenance | None:
        """Get the latest provenance for a specific (entity, signal) pair."""
        return self._latest.get((entity_path, signal))

    def signals_for_entity(self, entity_path: str) -> dict[Signal, SignalProvenance]:
        """Get all latest provenance records for an entity.

        Args:
            entity_path: File/module/codebase path.

        Returns:
            Dict mapping Signal to its latest provenance record.
        """
        result: dict[Signal, SignalProvenance] = {}
        for (ep, sig), prov in self._latest.items():
            if ep == entity_path:
                result[sig] = prov
        return result

    def cleanup(self) -> None:
        """Delete all provenance data (in-memory and on disk).

        Closes the file handle and removes the session directory.
        Safe to call multiple times.
        """
        self._close_file()
        if self._session_dir and self._session_dir.exists():
            shutil.rmtree(self._session_dir, ignore_errors=True)
            logger.debug(f"Cleaned up provenance dir: {self._session_dir}")
        self._latest.clear()
        self._history.clear()
        self._all_records.clear()
        self._cleanup_done = True

    def clear(self) -> None:
        """Clear all in-memory provenance records.

        Does NOT remove the on-disk JSONL file. Use cleanup() for full removal.
        """
        self._latest.clear()
        self._history.clear()
        self._all_records.clear()
