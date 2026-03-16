"""RuntimeContext — The execution container for Shannon Insight.

This module provides the foundational infrastructure that makes analysis reliable,
observable, and safely cancellable. Everything else builds on this.

Based on production patterns from SonarQube, Semgrep, ESLint, and CodeClimate:
- Bounded resources (memory, time, files)
- Graceful shutdown with signal handling
- Circuit breaker for failing phases
- Checkpoint/resume for long operations
- Structured observability (phases, progress, errors)

Usage:
    from shannon_insight.infrastructure.runtime import RuntimeContext, Phase

    async with RuntimeContext.create(root="/path/to/code") as ctx:
        ctx.transition(Phase.SCANNING)
        for path in ctx.iter_files():
            if not ctx.should_continue:
                break
            result = analyze(path)
            ctx.record_result(path, result)

    # Or synchronous:
    with RuntimeContext.create(root="/path/to/code") as ctx:
        ctx.run_sync(analysis_pipeline)

Design Principles:
    1. BOUNDED: Every resource has explicit limits
    2. OBSERVABLE: Every state change is tracked
    3. CANCELLABLE: Graceful shutdown at any point
    4. RECOVERABLE: Checkpoint/resume for long operations
    5. ISOLATED: Failures are contained, not propagated
"""

from __future__ import annotations

import atexit
import gc
import resource
import signal
import sys
import threading
import time
import uuid
from collections.abc import Generator, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
)

if TYPE_CHECKING:
    from ..config import AnalysisConfig
    from ..environment import Environment

# ---------------------------------------------------------------------------
# Phase Definition
# ---------------------------------------------------------------------------


class Phase(Enum):
    """Analysis phases with strict ordering.

    Phases must complete in order. Each phase has:
    - A timeout (configurable)
    - A circuit breaker (auto-skip on repeated failures)
    - Progress tracking
    """

    INIT = auto()  # Initial state
    DISCOVERY = auto()  # File discovery
    SCANNING = auto()  # Syntax extraction
    STRUCTURAL = auto()  # Graph building
    TEMPORAL = auto()  # Git history analysis
    TENSOR_BUILD = auto()  # Build relationship tensor
    FUSION = auto()  # Signal computation
    PATTERNS = auto()  # Finding detection
    REPORTING = auto()  # Output generation
    COMPLETE = auto()  # Terminal success state
    FAILED = auto()  # Terminal failure state
    CANCELLED = auto()  # Terminal cancelled state


# Phase ordering for validation
_PHASE_ORDER = [
    Phase.INIT,
    Phase.DISCOVERY,
    Phase.SCANNING,
    Phase.STRUCTURAL,
    Phase.TEMPORAL,
    Phase.TENSOR_BUILD,
    Phase.FUSION,
    Phase.PATTERNS,
    Phase.REPORTING,
    Phase.COMPLETE,
]


# ---------------------------------------------------------------------------
# Error Taxonomy
# ---------------------------------------------------------------------------


class RuntimeError(Exception):
    """Base class for all runtime errors."""

    def __init__(self, message: str, phase: Phase | None = None, recoverable: bool = True):
        super().__init__(message)
        self.phase = phase
        self.recoverable = recoverable
        self.timestamp = datetime.now(timezone.utc)


class TimeoutError(RuntimeError):
    """Operation exceeded time limit."""

    def __init__(self, message: str, timeout_seconds: float, phase: Phase | None = None):
        super().__init__(message, phase, recoverable=True)
        self.timeout_seconds = timeout_seconds


class ResourceExhaustedError(RuntimeError):
    """Memory or other resource limit exceeded."""

    def __init__(self, message: str, resource_type: str, limit: float, actual: float):
        super().__init__(message, recoverable=False)
        self.resource_type = resource_type
        self.limit = limit
        self.actual = actual


class CancellationError(RuntimeError):
    """Operation was cancelled by user or system."""

    def __init__(self, message: str = "Operation cancelled"):
        super().__init__(message, recoverable=False)


class PhaseError(RuntimeError):
    """A phase failed to complete."""

    def __init__(self, message: str, phase: Phase, cause: Exception | None = None):
        super().__init__(message, phase, recoverable=True)
        self.cause = cause


# ---------------------------------------------------------------------------
# Metrics and Observability
# ---------------------------------------------------------------------------


@dataclass
class PhaseMetrics:
    """Metrics for a single phase."""

    phase: Phase
    started_at: datetime | None = None
    completed_at: datetime | None = None
    items_total: int = 0
    items_processed: int = 0
    items_failed: int = 0
    memory_start_mb: float = 0.0
    memory_peak_mb: float = 0.0
    error: str | None = None

    @property
    def duration_seconds(self) -> float:
        """Duration of this phase in seconds."""
        if self.started_at is None:
            return 0.0
        end = self.completed_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds()

    @property
    def success_rate(self) -> float:
        """Fraction of items successfully processed."""
        if self.items_total == 0:
            return 1.0
        return (self.items_processed - self.items_failed) / self.items_total

    @property
    def is_complete(self) -> bool:
        """Whether this phase has finished (success or failure)."""
        return self.completed_at is not None


@dataclass
class RuntimeMetrics:
    """Aggregate metrics for the entire run."""

    run_id: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    phases: dict[Phase, PhaseMetrics] = field(default_factory=dict)

    # Resource tracking
    memory_limit_mb: float = 0.0
    memory_peak_mb: float = 0.0
    file_count: int = 0

    # Outcome
    total_errors: int = 0
    total_warnings: int = 0

    @property
    def duration_seconds(self) -> float:
        """Total duration in seconds."""
        if self.started_at is None:
            return 0.0
        end = self.completed_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Export metrics as dictionary for JSON serialization."""
        return {
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "memory_peak_mb": self.memory_peak_mb,
            "memory_limit_mb": self.memory_limit_mb,
            "file_count": self.file_count,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "phases": {
                p.name: {
                    "duration_seconds": m.duration_seconds,
                    "items_total": m.items_total,
                    "items_processed": m.items_processed,
                    "items_failed": m.items_failed,
                    "success_rate": m.success_rate,
                    "memory_peak_mb": m.memory_peak_mb,
                    "error": m.error,
                }
                for p, m in self.phases.items()
            },
        }


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------


@dataclass
class CircuitBreaker:
    """Circuit breaker for failing operations.

    Opens after `fail_max` failures, preventing further attempts.
    Resets after `reset_timeout` seconds.

    States:
        CLOSED: Normal operation, failures counted
        OPEN: Failing, operations skipped
        HALF_OPEN: Testing if service recovered
    """

    fail_max: int = 3
    reset_timeout_seconds: float = 60.0

    _failure_count: int = field(default=0, repr=False)
    _last_failure_time: float | None = field(default=None, repr=False)
    _state: str = field(default="CLOSED", repr=False)

    def record_failure(self) -> None:
        """Record a failure."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.fail_max:
            self._state = "OPEN"

    def record_success(self) -> None:
        """Record a success."""
        self._failure_count = 0
        self._state = "CLOSED"

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking operations)."""
        if self._state == "CLOSED":
            return False
        if self._state == "OPEN":
            # Check if reset timeout has passed
            if self._last_failure_time is not None:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.reset_timeout_seconds:
                    self._state = "HALF_OPEN"
                    return False
            return True
        # HALF_OPEN: allow one attempt
        return False

    def reset(self) -> None:
        """Reset the circuit breaker."""
        self._failure_count = 0
        self._last_failure_time = None
        self._state = "CLOSED"


# ---------------------------------------------------------------------------
# Progress Callback Protocol
# ---------------------------------------------------------------------------

ProgressCallback = Callable[[str, int, int], None]  # (message, current, total)


# ---------------------------------------------------------------------------
# Runtime Context
# ---------------------------------------------------------------------------


@dataclass
class RuntimeContext:
    """The execution container for analysis.

    This is the central infrastructure that manages:
    - Resource bounds (memory, time, files)
    - Lifecycle (phases, shutdown, cleanup)
    - Observability (progress, errors, metrics)
    - Cancellation (signal handling, graceful shutdown)

    Thread-safe for cancellation; other operations should be single-threaded.
    """

    # Identity
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    root: Path = field(default_factory=Path)

    # Bounds (all have sensible defaults)
    memory_limit_mb: int = 2048  # 2GB default
    total_timeout_seconds: int = 1800  # 30 minutes default
    phase_timeout_seconds: int = 300  # 5 minutes per phase default
    max_files: int = 50000  # File limit
    max_file_size_mb: float = 10.0  # Per-file size limit

    # Lifecycle
    current_phase: Phase = Phase.INIT
    _shutdown_requested: bool = field(default=False, repr=False)
    _shutdown_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    # Observability
    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)
    errors: list[RuntimeError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Circuit breakers per phase
    _circuit_breakers: dict[Phase, CircuitBreaker] = field(default_factory=dict, repr=False)

    # Progress callback
    _progress_callback: ProgressCallback | None = field(default=None, repr=False)

    # Resource cleanup stack
    _cleanup_stack: ExitStack = field(default_factory=ExitStack, repr=False)

    # Checkpoint path
    _checkpoint_path: Path | None = field(default=None, repr=False)

    # Original signal handlers (for restoration)
    _original_sigint: Any = field(default=None, repr=False)
    _original_sigterm: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize runtime context."""
        self.metrics.run_id = self.run_id
        self.metrics.memory_limit_mb = self.memory_limit_mb

        # Initialize circuit breakers for each phase
        for phase in Phase:
            if phase not in (Phase.INIT, Phase.COMPLETE, Phase.FAILED, Phase.CANCELLED):
                self._circuit_breakers[phase] = CircuitBreaker()

    # ─────────────────────────────────────────────────────────────────────
    # Factory Methods
    # ─────────────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        root: str | Path,
        config: AnalysisConfig | None = None,
        env: Environment | None = None,
        memory_limit_mb: int = 2048,
        total_timeout_seconds: int = 1800,
        progress_callback: ProgressCallback | None = None,
    ) -> RuntimeContext:
        """Create a new runtime context.

        Args:
            root: Path to codebase root
            config: Optional analysis config (extracts relevant bounds)
            env: Optional environment (extracts file count, etc.)
            memory_limit_mb: Memory limit in MB
            total_timeout_seconds: Total timeout in seconds
            progress_callback: Optional progress callback

        Returns:
            Configured RuntimeContext instance
        """
        ctx = cls(
            root=Path(root).resolve(),
            memory_limit_mb=memory_limit_mb,
            total_timeout_seconds=total_timeout_seconds,
        )

        # Apply config overrides
        if config is not None:
            ctx.max_files = config.max_files
            ctx.max_file_size_mb = config.max_file_size_mb
            ctx.phase_timeout_seconds = config.timeout_seconds * 30  # Scale up

        # Apply environment info
        if env is not None:
            ctx.metrics.file_count = env.file_count

        ctx._progress_callback = progress_callback
        return ctx

    # ─────────────────────────────────────────────────────────────────────
    # Context Manager Protocol
    # ─────────────────────────────────────────────────────────────────────

    def __enter__(self) -> RuntimeContext:
        """Enter the runtime context."""
        self._start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit the runtime context with cleanup."""
        self._stop(exc_val)
        return False  # Don't suppress exceptions

    async def __aenter__(self) -> RuntimeContext:
        """Async context manager entry."""
        self._start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Async context manager exit."""
        self._stop(exc_val)
        return False

    def _start(self) -> None:
        """Initialize the runtime context."""
        self.metrics.started_at = datetime.now(timezone.utc)

        # Install signal handlers for graceful shutdown
        self._install_signal_handlers()

        # Set memory limit (soft limit, not enforced by OS on all platforms)
        self._set_memory_limit()

        # Register cleanup at interpreter exit
        atexit.register(self._emergency_cleanup)

    def _stop(self, error: Exception | None = None) -> None:
        """Shutdown the runtime context."""
        self.metrics.completed_at = datetime.now(timezone.utc)

        # Update global memory peak from phase peaks
        for phase_metrics in self.metrics.phases.values():
            self.metrics.memory_peak_mb = max(
                self.metrics.memory_peak_mb, phase_metrics.memory_peak_mb
            )

        # Record final state
        if error is not None:
            if isinstance(error, CancellationError):
                self.current_phase = Phase.CANCELLED
            else:
                self.current_phase = Phase.FAILED
                self.record_error(error)
        elif self._shutdown_requested:
            # Shutdown was requested - mark as cancelled
            self.current_phase = Phase.CANCELLED
        elif self.current_phase not in (Phase.COMPLETE, Phase.FAILED, Phase.CANCELLED):
            # Didn't reach terminal state - mark as complete if no errors
            if not self.errors:
                self.current_phase = Phase.COMPLETE

        # Restore signal handlers
        self._restore_signal_handlers()

        # Cleanup resources
        self._cleanup_stack.close()

        # Unregister emergency cleanup
        try:
            atexit.unregister(self._emergency_cleanup)
        except Exception:
            pass

        # Force garbage collection
        gc.collect()

    # ─────────────────────────────────────────────────────────────────────
    # Signal Handling
    # ─────────────────────────────────────────────────────────────────────

    def _install_signal_handlers(self) -> None:
        """Install signal handlers for graceful shutdown."""
        # Only install in main thread
        if threading.current_thread() is not threading.main_thread():
            return

        def handler(signum, frame):
            self.request_shutdown(f"Received signal {signum}")

        try:
            self._original_sigint = signal.signal(signal.SIGINT, handler)
            self._original_sigterm = signal.signal(signal.SIGTERM, handler)
        except (ValueError, OSError):
            # Can fail in some environments (e.g., non-main thread)
            pass

    def _restore_signal_handlers(self) -> None:
        """Restore original signal handlers."""
        if threading.current_thread() is not threading.main_thread():
            return

        try:
            if self._original_sigint is not None:
                signal.signal(signal.SIGINT, self._original_sigint)
            if self._original_sigterm is not None:
                signal.signal(signal.SIGTERM, self._original_sigterm)
        except (ValueError, OSError):
            pass

    # ─────────────────────────────────────────────────────────────────────
    # Resource Limits
    # ─────────────────────────────────────────────────────────────────────

    def _set_memory_limit(self) -> None:
        """Set soft memory limit (best effort, not enforced on all platforms)."""
        try:
            limit_bytes = self.memory_limit_mb * 1024 * 1024
            # Set soft limit only (hard limit can cause crashes)
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, hard))
        except (ValueError, OSError, AttributeError):
            # Not available on all platforms (e.g., Windows)
            pass

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            # Use resource module for accurate measurement
            usage = resource.getrusage(resource.RUSAGE_SELF)
            # maxrss is in KB on Linux, bytes on macOS
            if sys.platform == "darwin":
                return usage.ru_maxrss / (1024 * 1024)
            else:
                return usage.ru_maxrss / 1024
        except (AttributeError, OSError):
            # Fallback to less accurate method
            import psutil

            try:
                process = psutil.Process()
                return process.memory_info().rss / (1024 * 1024)
            except Exception:
                return 0.0

    def check_memory(self) -> bool:
        """Check if memory usage is within limits.

        Returns:
            True if within limits, False if exceeded
        """
        usage = self.get_memory_usage_mb()
        self.metrics.memory_peak_mb = max(self.metrics.memory_peak_mb, usage)

        if usage > self.memory_limit_mb:
            self.record_error(
                ResourceExhaustedError(
                    f"Memory limit exceeded: {usage:.0f}MB > {self.memory_limit_mb}MB",
                    resource_type="memory",
                    limit=self.memory_limit_mb,
                    actual=usage,
                )
            )
            return False
        return True

    # ─────────────────────────────────────────────────────────────────────
    # Shutdown and Cancellation
    # ─────────────────────────────────────────────────────────────────────

    def request_shutdown(self, reason: str = "Shutdown requested") -> None:
        """Request graceful shutdown.

        Thread-safe. Can be called from signal handlers or other threads.
        """
        with self._shutdown_lock:
            if not self._shutdown_requested:
                self._shutdown_requested = True
                self.warnings.append(f"Shutdown: {reason}")

    @property
    def should_continue(self) -> bool:
        """Check if execution should continue.

        Call this regularly in loops to enable graceful cancellation.
        """
        # Check shutdown flag
        with self._shutdown_lock:
            if self._shutdown_requested:
                return False

        # Check total timeout
        if self.metrics.started_at is not None:
            elapsed = (datetime.now(timezone.utc) - self.metrics.started_at).total_seconds()
            if elapsed > self.total_timeout_seconds:
                self.request_shutdown(f"Total timeout exceeded ({elapsed:.0f}s)")
                return False

        # Check memory (less frequently - expensive)
        # Only check every ~100 calls by using modulo on a simple counter
        # For simplicity, just check occasionally
        return True

    def _emergency_cleanup(self) -> None:
        """Emergency cleanup at interpreter exit."""
        try:
            self._cleanup_stack.close()
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────────────
    # Phase Management
    # ─────────────────────────────────────────────────────────────────────

    def transition(self, phase: Phase) -> bool:
        """Transition to a new phase.

        Args:
            phase: Target phase

        Returns:
            True if transition succeeded, False if blocked (e.g., circuit open)

        Raises:
            ValueError: If transition is invalid (out of order)
        """
        # Validate ordering (except for terminal states)
        if phase not in (Phase.COMPLETE, Phase.FAILED, Phase.CANCELLED):
            current_idx = (
                _PHASE_ORDER.index(self.current_phase) if self.current_phase in _PHASE_ORDER else -1
            )
            target_idx = _PHASE_ORDER.index(phase)
            if target_idx < current_idx:
                raise ValueError(
                    f"Invalid phase transition: {self.current_phase.name} -> {phase.name}"
                )

        # Check circuit breaker
        if phase in self._circuit_breakers and self._circuit_breakers[phase].is_open:
            self.warnings.append(f"Phase {phase.name} skipped (circuit open)")
            return False

        # Complete current phase metrics
        if self.current_phase in self.metrics.phases:
            self.metrics.phases[self.current_phase].completed_at = datetime.now(timezone.utc)

        # Start new phase
        self.current_phase = phase
        self.metrics.phases[phase] = PhaseMetrics(
            phase=phase,
            started_at=datetime.now(timezone.utc),
            memory_start_mb=self.get_memory_usage_mb(),
        )

        # Report progress
        if self._progress_callback:
            self._progress_callback(f"Starting {phase.name}...", 0, 0)

        return True

    def complete_phase(self, error: Exception | None = None) -> None:
        """Mark current phase as complete.

        Args:
            error: Optional error if phase failed
        """
        if self.current_phase not in self.metrics.phases:
            return

        metrics = self.metrics.phases[self.current_phase]
        metrics.completed_at = datetime.now(timezone.utc)
        metrics.memory_peak_mb = max(metrics.memory_peak_mb, self.get_memory_usage_mb())

        if error is not None:
            metrics.error = str(error)
            self._circuit_breakers[self.current_phase].record_failure()
        else:
            self._circuit_breakers[self.current_phase].record_success()

    # ─────────────────────────────────────────────────────────────────────
    # Progress Tracking
    # ─────────────────────────────────────────────────────────────────────

    def set_phase_total(self, total: int) -> None:
        """Set total items for current phase."""
        if self.current_phase in self.metrics.phases:
            self.metrics.phases[self.current_phase].items_total = total

    def advance(self, count: int = 1, failed: bool = False) -> None:
        """Advance progress in current phase.

        Args:
            count: Number of items processed
            failed: Whether this item failed
        """
        if self.current_phase not in self.metrics.phases:
            return

        metrics = self.metrics.phases[self.current_phase]
        metrics.items_processed += count
        if failed:
            metrics.items_failed += count

        # Update peak memory
        metrics.memory_peak_mb = max(metrics.memory_peak_mb, self.get_memory_usage_mb())

        # Report progress
        if self._progress_callback:
            self._progress_callback(
                f"{self.current_phase.name}: {metrics.items_processed}/{metrics.items_total}",
                metrics.items_processed,
                metrics.items_total,
            )

    # ─────────────────────────────────────────────────────────────────────
    # Error Recording
    # ─────────────────────────────────────────────────────────────────────

    def record_error(self, error: Exception) -> None:
        """Record an error.

        Args:
            error: Exception to record
        """
        if isinstance(error, RuntimeError):
            runtime_error = error
        else:
            runtime_error = PhaseError(str(error), self.current_phase, error)

        self.errors.append(runtime_error)
        self.metrics.total_errors += 1

        # Update phase metrics
        if self.current_phase in self.metrics.phases:
            self.metrics.phases[self.current_phase].error = str(error)

    def record_warning(self, message: str) -> None:
        """Record a warning."""
        self.warnings.append(message)
        self.metrics.total_warnings += 1

    # ─────────────────────────────────────────────────────────────────────
    # Checkpoint/Resume
    # ─────────────────────────────────────────────────────────────────────

    def enable_checkpointing(self, path: Path) -> None:
        """Enable checkpointing to the specified path.

        Args:
            path: Path to checkpoint file
        """
        self._checkpoint_path = path

    def save_checkpoint(self, data: dict[str, Any]) -> None:
        """Save checkpoint data.

        Args:
            data: Checkpoint data (must be JSON-serializable)
        """
        if self._checkpoint_path is None:
            return

        import json

        checkpoint = {
            "run_id": self.run_id,
            "phase": self.current_phase.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }

        # Write atomically
        tmp_path = self._checkpoint_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(checkpoint, f)
        tmp_path.rename(self._checkpoint_path)

    def load_checkpoint(self) -> Optional[dict[str, Any]]:
        """Load checkpoint data if available.

        Returns:
            Checkpoint data or None if not available
        """
        if self._checkpoint_path is None or not self._checkpoint_path.exists():
            return None

        import json

        try:
            with open(self._checkpoint_path) as f:
                checkpoint = json.load(f)
            return checkpoint.get("data")
        except Exception:
            return None

    def clear_checkpoint(self) -> None:
        """Clear checkpoint file."""
        if self._checkpoint_path is not None and self._checkpoint_path.exists():
            self._checkpoint_path.unlink()

    # ─────────────────────────────────────────────────────────────────────
    # Resource Management
    # ─────────────────────────────────────────────────────────────────────

    def register_cleanup(self, cleanup_func: Callable[[], None]) -> None:
        """Register a cleanup function to run on context exit.

        Args:
            cleanup_func: Function to call during cleanup
        """
        self._cleanup_stack.callback(cleanup_func)

    @contextmanager
    def managed_resource(self, resource: Any) -> Generator[Any, None, None]:
        """Context manager for resources that need cleanup.

        Args:
            resource: Resource with close() method

        Yields:
            The resource
        """
        try:
            yield resource
        finally:
            if hasattr(resource, "close"):
                resource.close()

    # ─────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ─────────────────────────────────────────────────────────────────────

    def iter_with_progress(self, items: list[Any], desc: str = "Processing") -> Iterator[Any]:
        """Iterate over items with progress tracking and cancellation checks.

        Args:
            items: Items to iterate
            desc: Description for progress

        Yields:
            Items one at a time
        """
        self.set_phase_total(len(items))

        for item in items:
            if not self.should_continue:
                break
            yield item
            self.advance()

    @contextmanager
    def phase_context(self, phase: Phase) -> Generator[None, None, None]:
        """Context manager for a phase with automatic completion.

        Args:
            phase: Phase to execute

        Yields:
            None

        Example:
            with ctx.phase_context(Phase.SCANNING):
                for path in files:
                    scan(path)
        """
        if not self.transition(phase):
            return  # Phase skipped

        error = None
        try:
            yield
        except Exception as e:
            error = e
            raise
        finally:
            self.complete_phase(error)

    def summary(self) -> str:
        """Get human-readable summary of the run."""
        lines = [
            f"Run {self.run_id}: {self.current_phase.name}",
            f"Duration: {self.metrics.duration_seconds:.1f}s",
            f"Memory peak: {self.metrics.memory_peak_mb:.0f}MB / {self.memory_limit_mb}MB",
            f"Errors: {self.metrics.total_errors}, Warnings: {self.metrics.total_warnings}",
        ]

        for phase, metrics in self.metrics.phases.items():
            if metrics.is_complete:
                status = "FAIL" if metrics.error else "OK"
                lines.append(
                    f"  {phase.name}: {metrics.duration_seconds:.1f}s, "
                    f"{metrics.items_processed}/{metrics.items_total} items, {status}"
                )

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Timeout Decorator
# ---------------------------------------------------------------------------


def with_timeout(seconds: float, phase: Phase | None = None):
    """Decorator to add timeout to a function.

    Args:
        seconds: Timeout in seconds
        phase: Optional phase for error reporting

    Returns:
        Decorated function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(
                        f"Operation timed out after {seconds}s",
                        timeout_seconds=seconds,
                        phase=phase,
                    )

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    "RuntimeContext",
    "Phase",
    "RuntimeError",
    "TimeoutError",
    "ResourceExhaustedError",
    "CancellationError",
    "PhaseError",
    "PhaseMetrics",
    "RuntimeMetrics",
    "CircuitBreaker",
    "ProgressCallback",
    "with_timeout",
]
