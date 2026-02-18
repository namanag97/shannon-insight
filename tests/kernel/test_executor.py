"""Tests for PhaseExecutor protocol and BaseExecutor."""

import pytest

from shannon_insight.infrastructure.runtime import Phase
from shannon_insight.kernel.executor import BaseExecutor, PhaseExecutor
from shannon_insight.kernel.result import PhaseResult


class TestPhaseExecutorProtocol:
    """Tests for PhaseExecutor protocol."""

    def test_protocol_defines_execute(self):
        """Test that protocol defines execute method."""
        # Protocol should have execute in annotations
        import typing

        assert "execute" in typing.get_type_hints(PhaseExecutor) or hasattr(
            PhaseExecutor, "execute"
        )

    def test_base_executor_has_required_attributes(self):
        """Test that BaseExecutor has attributes that fulfill protocol."""
        executor = BaseExecutor()
        # BaseExecutor should have the required attributes
        assert hasattr(executor, "phase")
        assert hasattr(executor, "timeout_seconds")
        assert hasattr(executor, "name")
        assert hasattr(executor, "execute")


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
