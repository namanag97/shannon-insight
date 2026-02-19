"""Integration tests for FactStore wiring into the kernel pipeline.

Tests that:
1. FactStore is properly created and passed through the kernel
2. SyntaxExtractor receives the FactStore for caching
3. GitRawExtractor receives the FactStore for identity resolution
4. Backward compatibility is maintained (FactStore is optional)
5. Facts are persisted and cache is used on second run
"""

import pytest

from shannon_insight.config import load_config
from shannon_insight.environment import discover_environment
from shannon_insight.facts.store import FactStore
from shannon_insight.insights.kernel import InsightKernel
from shannon_insight.insights.store import AnalysisStore
from shannon_insight.kernel import RuntimeKernel
from shannon_insight.session import AnalysisSession


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


class TestAnalysisStoreFactsDb:
    """Test that AnalysisStore properly holds a persistent FactStore."""

    def test_facts_db_default_none(self):
        """facts_db should be None by default."""
        store = AnalysisStore(root_dir="/tmp/test")
        assert store.facts_db is None

    def test_facts_db_setter(self):
        """facts_db setter should work."""
        store = AnalysisStore(root_dir="/tmp/test")
        fs = FactStore.in_memory()
        store.facts_db = fs
        assert store.facts_db is fs

    def test_facts_db_setter_none(self):
        """facts_db can be set back to None."""
        store = AnalysisStore(root_dir="/tmp/test")
        fs = FactStore.in_memory()
        store.facts_db = fs
        store.facts_db = None
        assert store.facts_db is None


class TestInsightKernelFactStoreWiring:
    """Test InsightKernel wiring of persistent FactStore."""

    def test_default_no_fact_store(self, sample_codebase):
        """Without use_fact_store, no persistent FactStore is created."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = InsightKernel(session=session)
        assert kernel._use_fact_store is False
        assert kernel._get_facts_db() is None

    def test_fact_store_created_on_demand(self, sample_codebase):
        """With use_fact_store=True, a FactStore is created."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = InsightKernel(session=session, use_fact_store=True)
        facts_db = kernel._get_facts_db()

        assert facts_db is not None
        # Should be the persistent FactStore
        assert isinstance(facts_db, FactStore)

        # DB file should exist
        db_path = sample_codebase / ".shannon" / "facts.db"
        assert db_path.exists()

        # Clean up
        facts_db.close()

    def test_run_with_fact_store(self, sample_codebase):
        """Full run with use_fact_store=True should succeed."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = InsightKernel(session=session, use_fact_store=True)
        result, snapshot = kernel.run()

        # Should complete successfully
        assert result is not None
        assert snapshot is not None
        assert snapshot.file_count > 0

        # DB should have been created
        db_path = sample_codebase / ".shannon" / "facts.db"
        assert db_path.exists()

        # DB should have some parsed syntax cached
        facts_db = FactStore.open(db_path)
        stats = facts_db.get_stats()
        assert stats["parsed_syntax"] > 0
        facts_db.close()

    def test_run_without_fact_store_backward_compat(self, sample_codebase):
        """Run without use_fact_store should work as before."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = InsightKernel(session=session)
        result, snapshot = kernel.run()

        # Should complete successfully
        assert result is not None
        assert snapshot is not None
        assert snapshot.file_count > 0

        # No facts.db should be created
        db_path = sample_codebase / ".shannon" / "facts.db"
        assert not db_path.exists()


class TestRuntimeKernelFactStoreWiring:
    """Test RuntimeKernel wiring of persistent FactStore."""

    def test_default_no_fact_store(self, sample_codebase):
        """Without use_fact_store, no persistent FactStore is created."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session=session)
        assert kernel.use_fact_store is False
        assert kernel._get_facts_db() is None

    def test_fact_store_created_on_demand(self, sample_codebase):
        """With use_fact_store=True, a FactStore is created."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session=session, use_fact_store=True)
        facts_db = kernel._get_facts_db()

        assert facts_db is not None
        assert isinstance(facts_db, FactStore)

        # Clean up
        facts_db.close()

    def test_run_with_fact_store(self, sample_codebase):
        """Full run with use_fact_store=True should succeed."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        kernel = RuntimeKernel(session=session, use_fact_store=True)
        result = kernel.run()

        assert result is not None
        assert result.success is True or result.partial is True

        # DB should have been created
        db_path = sample_codebase / ".shannon" / "facts.db"
        assert db_path.exists()


class TestFactStoreCaching:
    """Test that FactStore caching works across runs."""

    def test_second_run_uses_cache(self, sample_codebase):
        """Second run with same FactStore should use cached syntax."""
        config = load_config()
        env = discover_environment(sample_codebase)
        session = AnalysisSession(config=config, env=env)

        # First run: populates cache
        kernel1 = InsightKernel(session=session, use_fact_store=True)
        result1, snapshot1 = kernel1.run()
        assert snapshot1.file_count > 0

        # Check parsed_syntax was stored
        db_path = sample_codebase / ".shannon" / "facts.db"
        facts_db = FactStore.open(db_path)
        stats = facts_db.get_stats()
        initial_syntax_count = stats["parsed_syntax"]
        assert initial_syntax_count > 0
        facts_db.close()

        # Second run: should reuse cached syntax
        env2 = discover_environment(sample_codebase)
        session2 = AnalysisSession(config=config, env=env2)
        kernel2 = InsightKernel(session=session2, use_fact_store=True)
        result2, snapshot2 = kernel2.run()
        assert snapshot2.file_count > 0

        # parsed_syntax count should not increase (cache reuse)
        facts_db2 = FactStore.open(db_path)
        stats2 = facts_db2.get_stats()
        assert stats2["parsed_syntax"] == initial_syntax_count
        facts_db2.close()
