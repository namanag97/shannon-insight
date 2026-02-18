"""Tests for API integration with RuntimeKernel."""

from pathlib import Path

import pytest

from shannon_insight.api import analyze_v2
from shannon_insight.kernel import RuntimeResult


@pytest.fixture
def sample_codebase(tmp_path):
    """Create a minimal codebase for testing."""
    (tmp_path / "main.py").write_text(
        '''"""Main module."""

def main():
    """Entry point."""
    print("Hello, world!")

if __name__ == "__main__":
    main()
'''
    )
    return tmp_path


class TestAnalyzeV2:
    """Tests for analyze_v2 function."""

    def test_returns_runtime_result(self, sample_codebase):
        """Test that analyze_v2 returns RuntimeResult."""
        result = analyze_v2(str(sample_codebase))
        assert isinstance(result, RuntimeResult)

    def test_has_metrics(self, sample_codebase):
        """Test that result has metrics."""
        result = analyze_v2(str(sample_codebase))
        assert result.metrics is not None
        assert result.metrics.duration_seconds >= 0

    def test_has_snapshot(self, sample_codebase):
        """Test that result has snapshot on success."""
        result = analyze_v2(str(sample_codebase))
        if result.success or result.partial:
            assert result.snapshot is not None

    def test_progress_callback(self, sample_codebase):
        """Test progress callback is called."""
        progress_calls = []

        def on_progress(msg, current, total):
            progress_calls.append((msg, current, total))

        analyze_v2(str(sample_codebase), on_progress=on_progress)
        assert len(progress_calls) > 0

    def test_with_verbose(self, sample_codebase):
        """Test with verbose option."""
        result = analyze_v2(str(sample_codebase), verbose=True)
        assert isinstance(result, RuntimeResult)

    def test_with_custom_timeout(self, sample_codebase):
        """Test with custom timeout."""
        result = analyze_v2(
            str(sample_codebase),
            total_timeout_seconds=60,
        )
        assert isinstance(result, RuntimeResult)

    def test_status_property(self, sample_codebase):
        """Test status property."""
        result = analyze_v2(str(sample_codebase))
        assert result.status in ["SUCCESS", "PARTIAL", "FAILED", "CANCELLED"]
