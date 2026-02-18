"""Tests for individual phase executors."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shannon_insight.infrastructure.runtime import Phase, RuntimeContext
from shannon_insight.kernel.phases import (
    DiscoveryExecutor,
    FusionExecutor,
    PatternsExecutor,
    ReportingExecutor,
    ScanningExecutor,
    StructuralExecutor,
    TemporalExecutor,
)
from shannon_insight.kernel.result import PhaseResult


@pytest.fixture
def mock_context(tmp_path):
    """Create a mock RuntimeContext."""
    ctx = RuntimeContext.create(root=tmp_path)
    return ctx


@pytest.fixture
def mock_store(tmp_path):
    """Create a mock AnalysisStore."""
    store = MagicMock()
    store.root_dir = str(tmp_path)
    store.file_count = 0
    store.available = set()
    store._content_cache = {}
    store.file_syntax = MagicMock()
    store.file_syntax.available = False
    store.structural = MagicMock()
    store.structural.available = False
    store.git_history = MagicMock()
    store.git_history.available = False
    store.signal_field = MagicMock()
    store.signal_field.available = False
    store.spectral = MagicMock()
    store.spectral.available = False
    store.fact_store = MagicMock()
    store.fact_store.files.return_value = []
    return store


@pytest.fixture
def mock_session(tmp_path):
    """Create a mock AnalysisSession."""
    session = MagicMock()
    session.env.root = tmp_path
    session.env.file_paths = []
    session.env.is_git_repo = False
    session.config.max_files = 1000
    session.config.max_findings = 10
    session.config.max_file_size_bytes = 10 * 1024 * 1024
    session.config.exclude_patterns = []
    session.config.git_max_commits = 1000
    session.config.git_min_commits = 5
    session.tier = MagicMock()
    session.tier.value = "full"
    return session


class TestDiscoveryExecutor:
    """Tests for DiscoveryExecutor."""

    def test_phase_is_discovery(self):
        """Test phase attribute is DISCOVERY."""
        executor = DiscoveryExecutor()
        assert executor.phase == Phase.DISCOVERY

    def test_name_attribute(self):
        """Test name attribute."""
        executor = DiscoveryExecutor()
        assert executor.name == "discovery"

    def test_execute_with_no_files(self, mock_context, mock_store, mock_session):
        """Test execute with empty directory."""
        executor = DiscoveryExecutor()
        result = executor.execute(mock_context, mock_store, mock_session)

        assert result.success is True
        assert result.items_processed == 0

    def test_execute_uses_env_paths(self, mock_context, mock_store, mock_session, tmp_path):
        """Test execute uses pre-discovered paths from env."""
        # Create some files
        (tmp_path / "test.py").write_text("print('hello')")
        mock_session.env.file_paths = ["test.py"]

        executor = DiscoveryExecutor()
        result = executor.execute(mock_context, mock_store, mock_session)

        assert result.success is True
        assert result.items_processed == 1


class TestScanningExecutor:
    """Tests for ScanningExecutor."""

    def test_phase_is_scanning(self):
        """Test phase attribute is SCANNING."""
        executor = ScanningExecutor()
        assert executor.phase == Phase.SCANNING

    def test_execute_with_no_files(self, mock_context, mock_store, mock_session):
        """Test execute with no discovered files."""
        executor = ScanningExecutor()
        result = executor.execute(mock_context, mock_store, mock_session)

        assert result.success is True
        assert result.items_processed == 0


class TestStructuralExecutor:
    """Tests for StructuralExecutor."""

    def test_phase_is_structural(self):
        """Test phase attribute is STRUCTURAL."""
        executor = StructuralExecutor()
        assert executor.phase == Phase.STRUCTURAL

    def test_execute_with_no_files(self, mock_context, mock_store, mock_session):
        """Test execute with no files in store."""
        mock_store.file_count = 0

        executor = StructuralExecutor()
        result = executor.execute(mock_context, mock_store, mock_session)

        assert result.success is True
        assert result.items_processed == 0


class TestTemporalExecutor:
    """Tests for TemporalExecutor."""

    def test_phase_is_temporal(self):
        """Test phase attribute is TEMPORAL."""
        executor = TemporalExecutor()
        assert executor.phase == Phase.TEMPORAL

    def test_execute_skips_when_no_git(self, mock_context, mock_store, mock_session):
        """Test execute skips when not a git repo."""
        mock_session.env.is_git_repo = False

        executor = TemporalExecutor()
        result = executor.execute(mock_context, mock_store, mock_session)

        assert result.success is True
        assert result.items_processed == 0


class TestFusionExecutor:
    """Tests for FusionExecutor."""

    def test_phase_is_fusion(self):
        """Test phase attribute is FUSION."""
        executor = FusionExecutor()
        assert executor.phase == Phase.FUSION

    def test_execute_with_no_files(self, mock_context, mock_store, mock_session):
        """Test execute with no files in store."""
        mock_store.file_count = 0

        executor = FusionExecutor()
        result = executor.execute(mock_context, mock_store, mock_session)

        assert result.success is True


class TestPatternsExecutor:
    """Tests for PatternsExecutor."""

    def test_phase_is_patterns(self):
        """Test phase attribute is PATTERNS."""
        executor = PatternsExecutor()
        assert executor.phase == Phase.PATTERNS

    def test_execute_with_no_files(self, mock_context, mock_store, mock_session):
        """Test execute with no files in store."""
        mock_store.file_count = 0

        executor = PatternsExecutor()
        result = executor.execute(mock_context, mock_store, mock_session)

        assert result.success is True
        assert result.items_processed == 0

        # Should set empty findings
        assert hasattr(mock_context, "_findings")


class TestReportingExecutor:
    """Tests for ReportingExecutor."""

    def test_phase_is_reporting(self):
        """Test phase attribute is REPORTING."""
        executor = ReportingExecutor()
        assert executor.phase == Phase.REPORTING

    def test_execute_builds_result(self, tmp_path):
        """Test execute builds InsightResult."""
        from shannon_insight.config import load_config
        from shannon_insight.environment import discover_environment
        from shannon_insight.insights.store import AnalysisStore
        from shannon_insight.session import AnalysisSession

        # Create real config and session for this test
        config = load_config()
        env = discover_environment(tmp_path)
        session = AnalysisSession(config=config, env=env)

        # Create real store and context
        ctx = RuntimeContext.create(root=tmp_path)
        store = AnalysisStore(
            root_dir=str(tmp_path),
            session=session,
        )

        # Set up empty findings
        ctx._findings = []  # type: ignore
        ctx._pattern_findings = []  # type: ignore

        executor = ReportingExecutor()
        result = executor.execute(ctx, store, session)

        assert result.success is True
        assert hasattr(ctx, "_insight_result")
        assert hasattr(ctx, "_snapshot")


class TestPhaseOrder:
    """Tests for phase executor ordering."""

    def test_executors_in_order(self):
        """Test that PHASE_EXECUTORS are in correct order."""
        from shannon_insight.kernel.phases import PHASE_EXECUTORS

        expected_order = [
            Phase.DISCOVERY,
            Phase.SCANNING,
            Phase.STRUCTURAL,
            Phase.TEMPORAL,
            Phase.FUSION,
            Phase.PATTERNS,
            Phase.REPORTING,
        ]

        actual_order = [e.phase for e in PHASE_EXECUTORS]
        assert actual_order == expected_order
