"""Tests for RuntimeResult and PhaseResult."""

import pytest

from shannon_insight.kernel.result import PhaseResult, RuntimeResult


class TestPhaseResult:
    """Tests for PhaseResult dataclass."""

    def test_ok_result(self):
        """Test creating a successful phase result."""
        result = PhaseResult.ok(items_processed=10)
        assert result.success is True
        assert result.error is None
        assert result.items_processed == 10
        assert result.items_failed == 0

    def test_ok_result_with_data(self):
        """Test creating a successful phase result with data."""
        data = {"key": "value"}
        result = PhaseResult.ok(items_processed=5, data=data)
        assert result.success is True
        assert result.data == data

    def test_fail_result(self):
        """Test creating a failed phase result."""
        error = ValueError("test error")
        result = PhaseResult.fail(error, items_processed=3)
        assert result.success is False
        assert result.error is error
        assert result.items_processed == 3

    def test_default_values(self):
        """Test default values."""
        result = PhaseResult()
        assert result.success is True
        assert result.error is None
        assert result.data is None
        assert result.items_processed == 0
        assert result.items_failed == 0


class TestRuntimeResult:
    """Tests for RuntimeResult dataclass."""

    def test_success_status(self):
        """Test status property for success."""
        result = RuntimeResult(success=True)
        assert result.status == "SUCCESS"

    def test_failed_status(self):
        """Test status property for failure."""
        result = RuntimeResult(success=False)
        assert result.status == "FAILED"

    def test_partial_status(self):
        """Test status property for partial success."""
        result = RuntimeResult(success=False, partial=True)
        assert result.status == "PARTIAL"

    def test_cancelled_status(self):
        """Test status property for cancellation."""
        result = RuntimeResult(cancelled=True)
        assert result.status == "CANCELLED"

    def test_cancelled_takes_precedence(self):
        """Test that cancelled status takes precedence over success/partial."""
        result = RuntimeResult(success=True, partial=True, cancelled=True)
        assert result.status == "CANCELLED"

    def test_summary_success(self):
        """Test summary for successful run."""
        result = RuntimeResult(
            findings=[],
            success=True,
            errors=[],
            warnings=[],
        )
        summary = result.summary()
        assert "SUCCESS" in summary
        assert "Findings: 0" in summary

    def test_summary_with_errors(self):
        """Test summary includes errors."""
        result = RuntimeResult(
            findings=[],
            success=False,
            errors=[ValueError("test error 1"), TypeError("test error 2")],
            warnings=["warning 1"],
        )
        summary = result.summary()
        assert "FAILED" in summary
        assert "Errors: 2" in summary
        assert "ValueError" in summary
        assert "Warnings: 1" in summary

    def test_summary_truncates_many_errors(self):
        """Test summary truncates when many errors."""
        errors = [ValueError(f"error {i}") for i in range(10)]
        result = RuntimeResult(
            success=False,
            errors=errors,
        )
        summary = result.summary()
        assert "and 7 more" in summary

    def test_default_values(self):
        """Test default values."""
        result = RuntimeResult()
        assert result.findings == []
        assert result.snapshot is None
        assert result.metrics is None
        assert result.errors == []
        assert result.warnings == []
        assert result.success is False
        assert result.partial is False
        assert result.cancelled is False
