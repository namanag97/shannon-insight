"""Tests for RuntimeContext — the execution container infrastructure."""

import tempfile
import threading
import time
from pathlib import Path

import pytest

from shannon_insight.infrastructure.runtime import (
    CancellationError,
    CircuitBreaker,
    Phase,
    PhaseError,
    PhaseMetrics,
    ResourceExhaustedError,
    RuntimeContext,
    RuntimeMetrics,
    TimeoutError,
    with_timeout,
)

# ---------------------------------------------------------------------------
# Phase Tests
# ---------------------------------------------------------------------------


class TestPhase:
    """Test Phase enum."""

    def test_phase_ordering(self):
        """Phases have correct ordering for pipeline."""
        phases = list(Phase)
        assert Phase.INIT in phases
        assert Phase.SCANNING in phases
        assert Phase.COMPLETE in phases
        assert Phase.FAILED in phases

    def test_all_phases_defined(self):
        """All expected phases are defined."""
        expected = {
            "INIT",
            "DISCOVERY",
            "SCANNING",
            "STRUCTURAL",
            "TEMPORAL",
            "TENSOR_BUILD",
            "FUSION",
            "PATTERNS",
            "REPORTING",
            "COMPLETE",
            "FAILED",
            "CANCELLED",
        }
        actual = {p.name for p in Phase}
        assert expected == actual


# ---------------------------------------------------------------------------
# Error Taxonomy Tests
# ---------------------------------------------------------------------------


class TestErrorTaxonomy:
    """Test error classes."""

    def test_timeout_error(self):
        """TimeoutError captures timeout details."""
        error = TimeoutError("Operation timed out", timeout_seconds=30.0, phase=Phase.SCANNING)
        assert "timed out" in str(error)
        assert error.timeout_seconds == 30.0
        assert error.phase == Phase.SCANNING
        assert error.recoverable is True

    def test_resource_exhausted_error(self):
        """ResourceExhaustedError captures resource details."""
        error = ResourceExhaustedError(
            "Memory limit exceeded",
            resource_type="memory",
            limit=2048.0,
            actual=3000.0,
        )
        assert error.resource_type == "memory"
        assert error.limit == 2048.0
        assert error.actual == 3000.0
        assert error.recoverable is False

    def test_cancellation_error(self):
        """CancellationError is not recoverable."""
        error = CancellationError()
        assert error.recoverable is False
        assert "cancelled" in str(error).lower()

    def test_phase_error(self):
        """PhaseError captures phase and cause."""
        cause = ValueError("bad value")
        error = PhaseError("Phase failed", Phase.STRUCTURAL, cause)
        assert error.phase == Phase.STRUCTURAL
        assert error.cause is cause


# ---------------------------------------------------------------------------
# Circuit Breaker Tests
# ---------------------------------------------------------------------------


class TestCircuitBreaker:
    """Test CircuitBreaker pattern."""

    def test_initial_state_closed(self):
        """Circuit starts closed."""
        cb = CircuitBreaker()
        assert not cb.is_open

    def test_opens_after_failures(self):
        """Circuit opens after fail_max failures."""
        cb = CircuitBreaker(fail_max=3)
        cb.record_failure()
        assert not cb.is_open
        cb.record_failure()
        assert not cb.is_open
        cb.record_failure()
        assert cb.is_open

    def test_success_resets(self):
        """Success resets failure count."""
        cb = CircuitBreaker(fail_max=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert not cb.is_open
        # Should need 3 more failures to open
        cb.record_failure()
        cb.record_failure()
        assert not cb.is_open

    def test_reset_timeout(self):
        """Circuit resets after timeout."""
        cb = CircuitBreaker(fail_max=1, reset_timeout_seconds=0.1)
        cb.record_failure()
        assert cb.is_open
        time.sleep(0.15)
        assert not cb.is_open  # Should be half-open now

    def test_manual_reset(self):
        """Manual reset clears circuit."""
        cb = CircuitBreaker(fail_max=1)
        cb.record_failure()
        assert cb.is_open
        cb.reset()
        assert not cb.is_open


# ---------------------------------------------------------------------------
# Metrics Tests
# ---------------------------------------------------------------------------


class TestPhaseMetrics:
    """Test PhaseMetrics dataclass."""

    def test_duration_calculation(self):
        """Duration is calculated correctly."""
        from datetime import datetime, timedelta, timezone

        metrics = PhaseMetrics(
            phase=Phase.SCANNING,
            started_at=datetime.now(timezone.utc) - timedelta(seconds=10),
            completed_at=datetime.now(timezone.utc),
            items_total=100,
            items_processed=100,
        )
        assert 9.5 < metrics.duration_seconds < 10.5

    def test_success_rate(self):
        """Success rate is calculated correctly."""
        metrics = PhaseMetrics(
            phase=Phase.SCANNING,
            items_total=100,
            items_processed=100,
            items_failed=10,
        )
        assert metrics.success_rate == 0.9

    def test_success_rate_empty(self):
        """Success rate is 1.0 when no items."""
        metrics = PhaseMetrics(phase=Phase.SCANNING, items_total=0)
        assert metrics.success_rate == 1.0


class TestRuntimeMetrics:
    """Test RuntimeMetrics dataclass."""

    def test_to_dict(self):
        """Metrics can be serialized to dict."""
        metrics = RuntimeMetrics(
            run_id="test123",
            file_count=100,
            memory_limit_mb=2048,
        )
        d = metrics.to_dict()
        assert d["run_id"] == "test123"
        assert d["file_count"] == 100
        assert "phases" in d


# ---------------------------------------------------------------------------
# RuntimeContext Tests
# ---------------------------------------------------------------------------


class TestRuntimeContextBasic:
    """Test basic RuntimeContext functionality."""

    def test_create_default(self):
        """Context can be created with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RuntimeContext.create(root=tmpdir)
            assert ctx.root == Path(tmpdir).resolve()
            assert ctx.memory_limit_mb == 2048
            assert ctx.current_phase == Phase.INIT

    def test_create_with_bounds(self):
        """Context respects custom bounds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RuntimeContext.create(
                root=tmpdir,
                memory_limit_mb=1024,
                total_timeout_seconds=60,
            )
            assert ctx.memory_limit_mb == 1024
            assert ctx.total_timeout_seconds == 60

    def test_context_manager(self):
        """Context manager protocol works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                assert ctx.metrics.started_at is not None
            assert ctx.metrics.completed_at is not None

    def test_run_id_unique(self):
        """Each context gets a unique run ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx1 = RuntimeContext.create(root=tmpdir)
            ctx2 = RuntimeContext.create(root=tmpdir)
            assert ctx1.run_id != ctx2.run_id


class TestRuntimeContextPhases:
    """Test phase management."""

    def test_transition_valid(self):
        """Valid phase transitions work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                assert ctx.transition(Phase.DISCOVERY)
                assert ctx.current_phase == Phase.DISCOVERY
                assert ctx.transition(Phase.SCANNING)
                assert ctx.current_phase == Phase.SCANNING

    def test_transition_invalid(self):
        """Invalid phase transitions raise error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.transition(Phase.SCANNING)
                with pytest.raises(ValueError):
                    ctx.transition(Phase.DISCOVERY)  # Can't go backwards

    def test_phase_context_manager(self):
        """Phase context manager tracks completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                with ctx.phase_context(Phase.SCANNING):
                    pass
                assert Phase.SCANNING in ctx.metrics.phases
                assert ctx.metrics.phases[Phase.SCANNING].is_complete

    def test_phase_context_error(self):
        """Phase context manager captures errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                with pytest.raises(ValueError):
                    with ctx.phase_context(Phase.SCANNING):
                        raise ValueError("test error")
                assert ctx.metrics.phases[Phase.SCANNING].error is not None


class TestRuntimeContextShutdown:
    """Test shutdown and cancellation."""

    def test_request_shutdown(self):
        """Shutdown can be requested."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RuntimeContext.create(root=tmpdir)
            assert ctx.should_continue
            ctx.request_shutdown("test")
            assert not ctx.should_continue

    def test_shutdown_thread_safe(self):
        """Shutdown request is thread-safe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RuntimeContext.create(root=tmpdir)

            def request():
                ctx.request_shutdown("from thread")

            threads = [threading.Thread(target=request) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert not ctx.should_continue
            # Should only have one warning despite multiple requests
            assert len([w for w in ctx.warnings if "Shutdown" in w]) == 1

    def test_timeout_triggers_shutdown(self):
        """Total timeout triggers shutdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = RuntimeContext.create(root=tmpdir, total_timeout_seconds=0)
            ctx._start()
            time.sleep(0.01)
            # should_continue should return False
            assert not ctx.should_continue


class TestRuntimeContextProgress:
    """Test progress tracking."""

    def test_progress_tracking(self):
        """Progress is tracked correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.transition(Phase.SCANNING)
                ctx.set_phase_total(10)
                for _i in range(10):
                    ctx.advance()
                metrics = ctx.metrics.phases[Phase.SCANNING]
                assert metrics.items_total == 10
                assert metrics.items_processed == 10

    def test_progress_callback(self):
        """Progress callback is invoked."""
        calls = []

        def callback(msg, current, total):
            calls.append((msg, current, total))

        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir, progress_callback=callback) as ctx:
                ctx.transition(Phase.SCANNING)
                ctx.set_phase_total(3)
                ctx.advance()
                ctx.advance()

        assert len(calls) > 0

    def test_iter_with_progress(self):
        """iter_with_progress tracks items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.transition(Phase.SCANNING)
                items = list(ctx.iter_with_progress([1, 2, 3]))
                assert items == [1, 2, 3]
                assert ctx.metrics.phases[Phase.SCANNING].items_processed == 3


class TestRuntimeContextErrors:
    """Test error recording."""

    def test_record_error(self):
        """Errors are recorded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.transition(Phase.SCANNING)
                ctx.record_error(ValueError("test"))
                assert ctx.metrics.total_errors == 1
                assert len(ctx.errors) == 1

    def test_record_warning(self):
        """Warnings are recorded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.record_warning("test warning")
                assert ctx.metrics.total_warnings == 1
                assert "test warning" in ctx.warnings


class TestRuntimeContextCheckpoint:
    """Test checkpoint/resume functionality."""

    def test_save_and_load_checkpoint(self):
        """Checkpoint can be saved and loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            # Save checkpoint
            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.enable_checkpointing(checkpoint_path)
                ctx.transition(Phase.SCANNING)
                ctx.save_checkpoint({"files_done": ["a.py", "b.py"]})

            assert checkpoint_path.exists()

            # Load checkpoint in new context
            with RuntimeContext.create(root=tmpdir) as ctx2:
                ctx2.enable_checkpointing(checkpoint_path)
                data = ctx2.load_checkpoint()
                assert data is not None
                assert data["files_done"] == ["a.py", "b.py"]

    def test_clear_checkpoint(self):
        """Checkpoint can be cleared."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.json"

            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.enable_checkpointing(checkpoint_path)
                ctx.save_checkpoint({"test": 1})
                assert checkpoint_path.exists()
                ctx.clear_checkpoint()
                assert not checkpoint_path.exists()


class TestRuntimeContextMemory:
    """Test memory management."""

    def test_memory_tracking(self):
        """Memory usage is tracked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.transition(Phase.SCANNING)
                # Allocate some memory
                _ = [0] * 1000000
                ctx.advance()
                # Phase-level memory is tracked during execution
                assert ctx.metrics.phases[Phase.SCANNING].memory_peak_mb > 0
            # Global memory_peak_mb is aggregated on exit
            assert ctx.metrics.memory_peak_mb > 0

    def test_check_memory(self):
        """Memory check returns correct status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set very high limit - should pass
            ctx = RuntimeContext.create(root=tmpdir, memory_limit_mb=10000)
            assert ctx.check_memory() is True


class TestRuntimeContextSummary:
    """Test summary generation."""

    def test_summary(self):
        """Summary is generated correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with RuntimeContext.create(root=tmpdir) as ctx:
                with ctx.phase_context(Phase.SCANNING):
                    ctx.set_phase_total(10)
                    for _ in range(10):
                        ctx.advance()

            summary = ctx.summary()
            assert ctx.run_id in summary
            assert "SCANNING" in summary
            assert "10/10" in summary


# ---------------------------------------------------------------------------
# Timeout Decorator Tests
# ---------------------------------------------------------------------------


class TestTimeoutDecorator:
    """Test with_timeout decorator."""

    def test_completes_in_time(self):
        """Function completes within timeout."""

        @with_timeout(1.0)
        def quick():
            return 42

        assert quick() == 42

    def test_times_out(self):
        """Function that exceeds timeout raises error."""

        @with_timeout(0.1)
        def slow():
            time.sleep(1.0)
            return 42

        with pytest.raises(TimeoutError) as exc_info:
            slow()
        assert exc_info.value.timeout_seconds == 0.1

    def test_timeout_with_phase(self):
        """Timeout error includes phase."""

        @with_timeout(0.1, phase=Phase.SCANNING)
        def slow():
            time.sleep(1.0)

        with pytest.raises(TimeoutError) as exc_info:
            slow()
        assert exc_info.value.phase == Phase.SCANNING


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------


class TestRuntimeContextIntegration:
    """Integration tests for RuntimeContext."""

    def test_full_pipeline_simulation(self):
        """Simulate a full analysis pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some fake files
            for i in range(5):
                (Path(tmpdir) / f"file{i}.py").write_text(f"# File {i}")

            results = {}
            with RuntimeContext.create(root=tmpdir) as ctx:
                # Discovery phase
                with ctx.phase_context(Phase.DISCOVERY):
                    files = list(Path(tmpdir).glob("*.py"))
                    ctx.set_phase_total(len(files))
                    for f in files:
                        ctx.advance()

                # Scanning phase
                with ctx.phase_context(Phase.SCANNING):
                    ctx.set_phase_total(len(files))
                    for f in ctx.iter_with_progress(files):
                        results[f.name] = f.read_text()

                ctx.transition(Phase.COMPLETE)

            assert ctx.current_phase == Phase.COMPLETE
            assert ctx.metrics.total_errors == 0
            assert len(results) == 5

    def test_pipeline_with_partial_failure(self):
        """Pipeline handles partial failures gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            items = ["good1", "bad", "good2"]
            results = []

            with RuntimeContext.create(root=tmpdir) as ctx:
                with ctx.phase_context(Phase.SCANNING):
                    ctx.set_phase_total(len(items))
                    for item in items:
                        try:
                            if item == "bad":
                                raise ValueError("Bad item")
                            results.append(item)
                            ctx.advance()
                        except ValueError as e:
                            ctx.record_error(e)
                            ctx.advance(failed=True)

            assert len(results) == 2
            assert ctx.metrics.total_errors == 1
            assert ctx.metrics.phases[Phase.SCANNING].items_failed == 1

    def test_early_cancellation(self):
        """Pipeline can be cancelled early."""
        with tempfile.TemporaryDirectory() as tmpdir:
            processed = 0

            with RuntimeContext.create(root=tmpdir) as ctx:
                ctx.transition(Phase.SCANNING)
                ctx.set_phase_total(100)

                for i in range(100):
                    if i == 5:
                        ctx.request_shutdown("test cancellation")
                    if not ctx.should_continue:
                        break
                    processed += 1
                    ctx.advance()

            assert processed == 5
            assert ctx.current_phase == Phase.CANCELLED
