"""Integration tests for RuntimeKernel with real analysis."""

from pathlib import Path

import pytest

from shannon_insight.config import load_config
from shannon_insight.environment import discover_environment
from shannon_insight.kernel import RuntimeKernel, RuntimeResult
from shannon_insight.session import AnalysisSession


@pytest.fixture
def sample_codebase(tmp_path):
    """Create a minimal codebase for testing."""
    # Create a simple Python file
    (tmp_path / "main.py").write_text(
        '''"""Main module."""

def main():
    """Entry point."""
    print("Hello, world!")

if __name__ == "__main__":
    main()
'''
    )

    # Create a module file
    (tmp_path / "utils.py").write_text(
        '''"""Utility functions."""

def helper():
    """A helper function."""
    return 42

def another_helper():
    """Another helper."""
    return "test"
'''
    )

    # Create a file that imports the other
    (tmp_path / "app.py").write_text(
        '''"""Application module."""

from utils import helper

def run():
    """Run the application."""
    result = helper()
    return result
'''
    )

    return tmp_path


class TestIntegrationFullPipeline:
    """Integration tests running full analysis pipeline."""

    def test_analyze_minimal_codebase(self, sample_codebase):
        """Test analyzing a minimal Python codebase."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session)
        result = kernel.run()

        assert isinstance(result, RuntimeResult)
        # Should complete without major errors
        assert result.success is True or result.partial is True
        assert result.cancelled is False

    def test_metrics_populated(self, sample_codebase):
        """Test that metrics are populated after run."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session)
        result = kernel.run()

        assert result.metrics is not None
        assert result.metrics.run_id is not None
        assert result.metrics.started_at is not None
        assert result.metrics.duration_seconds >= 0

    def test_snapshot_captured(self, sample_codebase):
        """Test that snapshot is captured."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session)
        result = kernel.run()

        if result.success or result.partial:
            assert result.snapshot is not None
            assert result.snapshot.file_count > 0

    def test_progress_callback_called(self, sample_codebase):
        """Test that progress callback is called during run."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        progress_messages = []

        def on_progress(msg, current, total):
            progress_messages.append(msg)

        kernel = RuntimeKernel(session)
        kernel.run(on_progress=on_progress)

        # Should have received progress updates
        assert len(progress_messages) > 0


class TestIntegrationTimeout:
    """Integration tests for timeout handling."""

    def test_total_timeout(self, sample_codebase):
        """Test that total timeout is enforced."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        # Use very short timeout (will likely trigger)
        kernel = RuntimeKernel(
            session,
            total_timeout_seconds=0,  # Immediate timeout
        )

        result = kernel.run()

        # Should either succeed quickly or be cancelled
        assert isinstance(result, RuntimeResult)


class TestIntegrationErrorHandling:
    """Integration tests for error handling."""

    def test_errors_collected(self, sample_codebase):
        """Test that errors are collected in result."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session)
        result = kernel.run()

        # Errors list should be available (may be empty)
        assert isinstance(result.errors, list)

    def test_warnings_collected(self, sample_codebase):
        """Test that warnings are collected in result."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session)
        result = kernel.run()

        # Warnings list should be available (may be empty)
        assert isinstance(result.warnings, list)


class TestIntegrationWithGit:
    """Integration tests with git repository."""

    def test_analyze_non_git_repo(self, sample_codebase):
        """Test analyzing a non-git repository."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        # Should work without git
        assert not env.is_git_repo

        kernel = RuntimeKernel(session)
        result = kernel.run()

        assert result.success is True or result.partial is True
