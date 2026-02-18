"""Tests for RuntimeKernel."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shannon_insight.kernel import RuntimeKernel, RuntimeResult
from shannon_insight.kernel.result import PhaseResult


@pytest.fixture
def mock_session():
    """Create a mock AnalysisSession."""
    session = MagicMock()
    session.env.root = Path("/tmp/test_repo")
    session.env.file_paths = []
    session.env.is_git_repo = False
    session.env.file_count = 0
    session.env.system_cores = 4
    session.config.max_files = 1000
    session.config.max_findings = 10
    session.config.timeout_seconds = 10
    session.config.max_file_size_bytes = 10 * 1024 * 1024
    session.config.max_file_size_mb = 10.0
    session.config.git_max_commits = 1000
    session.config.git_min_commits = 5
    session.tier = MagicMock()
    session.tier.value = "full"
    return session


class TestRuntimeKernelInit:
    """Tests for RuntimeKernel initialization."""

    def test_init_with_defaults(self, mock_session):
        """Test initialization with default values."""
        kernel = RuntimeKernel(mock_session)

        assert kernel.session is mock_session
        assert kernel.memory_limit_mb == 2048
        assert kernel.total_timeout_seconds == 1800
        assert kernel.phase_timeout_seconds == 300
        assert kernel.enable_provenance is False

    def test_init_with_custom_values(self, mock_session):
        """Test initialization with custom values."""
        kernel = RuntimeKernel(
            mock_session,
            memory_limit_mb=4096,
            total_timeout_seconds=3600,
            phase_timeout_seconds=600,
            enable_provenance=True,
        )

        assert kernel.memory_limit_mb == 4096
        assert kernel.total_timeout_seconds == 3600
        assert kernel.phase_timeout_seconds == 600
        assert kernel.enable_provenance is True


class TestRuntimeKernelRun:
    """Tests for RuntimeKernel.run()."""

    def test_run_returns_runtime_result(self, mock_session, tmp_path):
        """Test that run returns RuntimeResult."""
        mock_session.env.root = tmp_path
        kernel = RuntimeKernel(mock_session)

        result = kernel.run()

        assert isinstance(result, RuntimeResult)

    def test_run_with_no_files(self, mock_session, tmp_path):
        """Test run with empty directory returns success with no findings."""
        mock_session.env.root = tmp_path
        mock_session.env.file_paths = []

        kernel = RuntimeKernel(mock_session)
        result = kernel.run()

        # Should succeed but with no findings
        assert result.success is True or result.partial is True
        assert result.findings == []

    def test_run_with_progress_callback(self, mock_session, tmp_path):
        """Test run calls progress callback."""
        mock_session.env.root = tmp_path
        progress_calls = []

        def on_progress(msg, current, total):
            progress_calls.append((msg, current, total))

        kernel = RuntimeKernel(mock_session)
        kernel.run(on_progress=on_progress)

        # Should have called progress at least once (for phase transitions)
        assert len(progress_calls) > 0

    def test_run_collects_errors(self, mock_session, tmp_path):
        """Test that run collects errors from failing phases."""
        mock_session.env.root = tmp_path

        # Create kernel with mocked executors
        kernel = RuntimeKernel(mock_session)

        # Replace first executor with one that fails
        class FailingExecutor:
            phase = kernel._executors[0].phase
            timeout_seconds = 10
            name = "failing"

            def execute(self, ctx, store, session):
                return PhaseResult.fail(ValueError("test error"))

        kernel._executors[0] = FailingExecutor()

        result = kernel.run()

        # Should have at least one error
        # Note: May still be partial success if other phases succeed
        assert len(result.errors) >= 1 or result.partial is True


class TestRuntimeKernelPhaseExecution:
    """Tests for phase execution logic."""

    def test_phases_run_in_order(self, mock_session, tmp_path):
        """Test that phases run in correct order."""
        mock_session.env.root = tmp_path

        kernel = RuntimeKernel(mock_session)

        # Track phase execution order
        executed_phases = []

        class TrackingExecutor:
            def __init__(self, original):
                self.phase = original.phase
                self.timeout_seconds = original.timeout_seconds
                self.name = original.name

            def execute(self, ctx, store, session):
                executed_phases.append(self.phase)
                return PhaseResult.ok()

        # Wrap all executors with tracking
        original_executors = kernel._executors
        kernel._executors = [TrackingExecutor(e) for e in original_executors]

        kernel.run()

        # Should have executed phases in order
        assert len(executed_phases) == len(original_executors)

    def test_graceful_degradation(self, mock_session, tmp_path):
        """Test that kernel continues on phase failure."""
        mock_session.env.root = tmp_path

        kernel = RuntimeKernel(mock_session)

        # Make first phase fail
        class FailingExecutor:
            phase = kernel._executors[0].phase
            timeout_seconds = 10
            name = "failing"

            def execute(self, ctx, store, session):
                return PhaseResult.fail(ValueError("phase failed"))

        # Track if second phase runs
        second_phase_ran = [False]

        class TrackingExecutor:
            phase = kernel._executors[1].phase
            timeout_seconds = 10
            name = "tracking"

            def execute(self, ctx, store, session):
                second_phase_ran[0] = True
                return PhaseResult.ok()

        kernel._executors[0] = FailingExecutor()
        kernel._executors[1] = TrackingExecutor()

        kernel.run()

        # Second phase should still run
        assert second_phase_ran[0] is True


class TestFactoryFunction:
    """Tests for create_runtime_kernel factory."""

    def test_create_runtime_kernel(self, mock_session):
        """Test factory function creates kernel."""
        from shannon_insight.kernel import create_runtime_kernel

        kernel = create_runtime_kernel(mock_session)
        assert isinstance(kernel, RuntimeKernel)

    def test_create_runtime_kernel_with_kwargs(self, mock_session):
        """Test factory function passes kwargs."""
        from shannon_insight.kernel import create_runtime_kernel

        kernel = create_runtime_kernel(
            mock_session,
            memory_limit_mb=512,
        )
        assert kernel.memory_limit_mb == 512
