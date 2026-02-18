"""Tests for PhaseExecutor protocol and BaseExecutor."""

import pytest

from shannon_insight.infrastructure.runtime import Phase
from shannon_insight.kernel.executor import BaseExecutor, PhaseExecutor
from shannon_insight.kernel.result import PhaseResult


class TestPhaseExecutorProtocol:
    """Tests for PhaseExecutor protocol."""

    def test_protocol_attributes(self):
        """Test that protocol defines required attributes."""
        # Check that PhaseExecutor has the expected attributes
        assert hasattr(PhaseExecutor, "phase")
        assert hasattr(PhaseExecutor, "timeout_seconds")
        assert hasattr(PhaseExecutor, "name")
        assert hasattr(PhaseExecutor, "execute")

    def test_isinstance_check(self):
        """Test that BaseExecutor is instance of PhaseExecutor protocol."""
        executor = BaseExecutor()
        # BaseExecutor should satisfy the protocol
        assert isinstance(executor, PhaseExecutor)


class TestBaseExecutor:
    """Tests for BaseExecutor base class."""

    def test_default_attributes(self):
        """Test default attribute values."""
        executor = BaseExecutor()
        assert executor.timeout_seconds == 300
        assert executor.name == "BaseExecutor"

    def test_execute_wraps_exceptions(self):
        """Test that execute wraps exceptions in PhaseResult."""

        class FailingExecutor(BaseExecutor):
            phase = Phase.SCANNING
            name = "failing"

            def _execute(self, ctx, store, session):
                raise ValueError("test error")

        executor = FailingExecutor()
        result = executor.execute(None, None, None)

        assert result.success is False
        assert isinstance(result.error, ValueError)
        assert str(result.error) == "test error"

    def test_execute_returns_phase_result(self):
        """Test that execute returns PhaseResult on success."""

        class SuccessExecutor(BaseExecutor):
            phase = Phase.SCANNING
            name = "success"

            def _execute(self, ctx, store, session):
                return PhaseResult.ok(items_processed=5)

        executor = SuccessExecutor()
        result = executor.execute(None, None, None)

        assert result.success is True
        assert result.items_processed == 5

    def test_base_execute_returns_ok(self):
        """Test that base _execute returns ok by default."""
        executor = BaseExecutor()
        result = executor._execute(None, None, None)
        assert result.success is True
