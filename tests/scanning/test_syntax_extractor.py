"""Tests for SyntaxExtractor."""

import tempfile
from pathlib import Path

import pytest

from shannon_insight.facts.store import FactStore
from shannon_insight.scanning.syntax import FileSyntax
from shannon_insight.scanning.syntax_extractor import SyntaxExtractor
from shannon_insight.scanning.treesitter_parser import (
    TREE_SITTER_AVAILABLE,
    get_supported_languages,
)

_PYTHON_SUPPORTED = TREE_SITTER_AVAILABLE and "python" in get_supported_languages()

SAMPLE_PYTHON = '''
"""A sample Python module."""

import os
from pathlib import Path

def hello(name):
    """Say hello."""
    print(f"Hello, {name}")
    return name

class Greeter:
    def greet(self):
        hello("world")

if __name__ == "__main__":
    hello("main")
'''


class TestSyntaxExtractorBasic:
    """Basic SyntaxExtractor tests."""

    def test_extract_returns_file_syntax(self):
        """extract() returns FileSyntax."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test.py"
            test_file.write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor()
            result = extractor.extract(test_file, root)

            assert isinstance(result, FileSyntax)
            assert result.path == "test.py"
            assert result.language == "python"

    def test_extract_detects_functions(self):
        """extract() detects functions."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test.py"
            test_file.write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor()
            result = extractor.extract(test_file, root)

            fn_names = [fn.name for fn in result.functions]
            assert "hello" in fn_names

    def test_extract_detects_classes(self):
        """extract() detects classes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test.py"
            test_file.write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor()
            result = extractor.extract(test_file, root)

            class_names = [cls.name for cls in result.classes]
            assert "Greeter" in class_names

    def test_extract_detects_main_guard(self):
        """extract() detects __main__ guard."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "test.py"
            test_file.write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor()
            result = extractor.extract(test_file, root)

            assert result.has_main_guard is True

    def test_extract_nonexistent_file(self):
        """extract() returns None for nonexistent file."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_file = root / "nonexistent.py"

            extractor = SyntaxExtractor()
            result = extractor.extract(test_file, root)

            assert result is None

    def test_extract_all_processes_multiple_files(self):
        """extract_all() processes multiple files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Create test files
            (root / "a.py").write_text("def a(): pass")
            (root / "b.py").write_text("def b(): pass")
            (root / "c.py").write_text("def c(): pass")

            extractor = SyntaxExtractor()
            results = extractor.extract_all([root / "a.py", root / "b.py", root / "c.py"], root)

            assert len(results) == 3
            assert "a.py" in results
            assert "b.py" in results
            assert "c.py" in results

    def test_extract_all_returns_dict(self):
        """extract_all() returns dict mapping path to FileSyntax."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor()
            results = extractor.extract_all([root / "test.py"], root)

            assert isinstance(results, dict)
            assert isinstance(results["test.py"], FileSyntax)


class TestSyntaxExtractorStats:
    """Test SyntaxExtractor statistics tracking."""

    def test_tracks_total_count(self):
        """Tracks total files processed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("def a(): pass")
            (root / "b.py").write_text("def b(): pass")

            extractor = SyntaxExtractor()
            extractor.extract_all([root / "a.py", root / "b.py"], root)

            assert extractor.total_count == 2

    def test_fallback_rate_property(self):
        """fallback_rate returns ratio of fallback to total."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor()
            extractor.extract(root / "test.py", root)

            # Rate should be between 0 and 1
            assert 0.0 <= extractor.fallback_rate <= 1.0

    def test_reset_stats(self):
        """reset_stats() clears counters."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor()
            extractor.extract(root / "test.py", root)

            assert extractor.total_count > 0

            extractor.reset_stats()

            assert extractor.total_count == 0
            assert extractor.fallback_count == 0
            assert extractor.treesitter_count == 0

    def test_fallback_rate_empty(self):
        """fallback_rate returns 0 when no files processed."""
        extractor = SyntaxExtractor()
        assert extractor.fallback_rate == 0.0


class TestSyntaxExtractorFallback:
    """Test fallback behavior."""

    def test_uses_fallback_when_treesitter_unavailable(self):
        """Uses regex fallback when tree-sitter unavailable."""
        if TREE_SITTER_AVAILABLE:
            pytest.skip("tree-sitter is installed, can't test fallback")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor()
            result = extractor.extract(root / "test.py", root)

            # Should still get a result via fallback
            assert result is not None
            assert extractor.fallback_count == 1

    def test_call_targets_none_in_fallback(self):
        """call_targets is None when using fallback."""
        if TREE_SITTER_AVAILABLE:
            pytest.skip("tree-sitter is installed, can't test fallback")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): bar()")

            extractor = SyntaxExtractor()
            result = extractor.extract(root / "test.py", root)

            for fn in result.functions:
                assert fn.call_targets is None


@pytest.mark.skipif(not _PYTHON_SUPPORTED, reason="tree-sitter-python not installed")
class TestSyntaxExtractorTreeSitter:
    """Tests requiring tree-sitter."""

    def test_uses_treesitter_when_available(self):
        """Uses tree-sitter when installed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor()
            extractor.extract(root / "test.py", root)

            assert extractor.treesitter_count == 1

    def test_call_targets_populated(self):
        """call_targets is populated when using tree-sitter."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): bar()")

            extractor = SyntaxExtractor()
            result = extractor.extract(root / "test.py", root)

            # Should have call_targets as list (possibly empty)
            has_targets = any(fn.call_targets is not None for fn in result.functions)
            assert has_targets


class TestSyntaxExtractorMultiLanguage:
    """Test multiple language support."""

    def test_go_files(self):
        """Processes Go files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.go").write_text("package main\n\nfunc main() {}")

            extractor = SyntaxExtractor()
            result = extractor.extract(root / "main.go", root)

            assert result is not None
            assert result.language == "go"

    def test_typescript_files(self):
        """Processes TypeScript files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.ts").write_text("function greet(): string { return 'hi'; }")

            extractor = SyntaxExtractor()
            result = extractor.extract(root / "test.ts", root)

            assert result is not None
            assert result.language == "typescript"

    def test_java_files(self):
        """Processes Java files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Test.java").write_text("public class Test { void foo() {} }")

            extractor = SyntaxExtractor()
            result = extractor.extract(root / "Test.java", root)

            assert result is not None
            assert result.language == "java"

    def test_unknown_language(self):
        """Falls back to unknown for unrecognized extensions."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.xyz").write_text("some content")

            extractor = SyntaxExtractor()
            result = extractor.extract(root / "test.xyz", root)

            assert result is not None
            assert result.language == "unknown"


class TestSyntaxExtractorCaching:
    """Tests for content-hash caching via FactStore."""

    def test_cache_miss_on_first_parse(self):
        """First extraction is a cache miss."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            result = extractor.extract(root / "test.py", root)

            assert result is not None
            stats = extractor.cache_stats()
            assert stats["misses"] == 1
            assert stats["hits"] == 0

    def test_cache_hit_on_second_parse(self):
        """Second extraction of same content is a cache hit."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "test.py", root)
            second = extractor.extract(root / "test.py", root)

            assert first is not None
            assert second is not None
            stats = extractor.cache_stats()
            assert stats["misses"] == 1
            assert stats["hits"] == 1
            assert stats["hit_rate"] == 0.5

    def test_different_content_is_cache_miss(self):
        """Different content produces a different hash and a cache miss."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("def a(): pass")
            (root / "b.py").write_text("def b(): return 42")

            extractor = SyntaxExtractor(fact_store=store)
            extractor.extract(root / "a.py", root)
            extractor.extract(root / "b.py", root)

            stats = extractor.cache_stats()
            assert stats["misses"] == 2
            assert stats["hits"] == 0

    def test_same_content_different_path_is_cache_hit(self):
        """Same content at a different path produces a cache hit (rename scenario)."""
        store = FactStore.in_memory()
        content = "def hello(): return 'world'"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "original.py").write_text(content)
            (root / "renamed.py").write_text(content)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "original.py", root)
            second = extractor.extract(root / "renamed.py", root)

            assert first is not None
            assert second is not None
            # First parse: miss; second parse: hit (same content)
            stats = extractor.cache_stats()
            assert stats["misses"] == 1
            assert stats["hits"] == 1

            # Path should reflect current file, not original
            assert first.path == "original.py"
            assert second.path == "renamed.py"

    def test_rehydrated_syntax_preserves_language(self):
        """Rehydrated FileSyntax has correct language."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "test.py", root)
            second = extractor.extract(root / "test.py", root)

            assert second.language == first.language == "python"

    def test_rehydrated_syntax_preserves_functions(self):
        """Rehydrated FileSyntax has same function names."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "test.py", root)
            second = extractor.extract(root / "test.py", root)

            first_fn_names = sorted(fn.name for fn in first.functions)
            second_fn_names = sorted(fn.name for fn in second.functions)
            assert first_fn_names == second_fn_names

    def test_rehydrated_syntax_preserves_classes(self):
        """Rehydrated FileSyntax has same class names."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "test.py", root)
            second = extractor.extract(root / "test.py", root)

            first_cls_names = sorted(cls.name for cls in first.classes)
            second_cls_names = sorted(cls.name for cls in second.classes)
            assert first_cls_names == second_cls_names

    def test_rehydrated_syntax_preserves_imports(self):
        """Rehydrated FileSyntax has same import sources."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "test.py", root)
            second = extractor.extract(root / "test.py", root)

            first_imp_sources = sorted(imp.source for imp in first.imports)
            second_imp_sources = sorted(imp.source for imp in second.imports)
            assert first_imp_sources == second_imp_sources

    def test_rehydrated_syntax_preserves_metrics(self):
        """Rehydrated FileSyntax has same scalar metrics."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "test.py", root)
            second = extractor.extract(root / "test.py", root)

            assert second.lines == first.lines
            assert second.has_main_guard == first.has_main_guard
            assert second.content_hash == first.content_hash

    def test_rehydrated_syntax_preserves_main_guard(self):
        """Rehydrated FileSyntax correctly preserves has_main_guard."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor(fact_store=store)
            first = extractor.extract(root / "test.py", root)
            second = extractor.extract(root / "test.py", root)

            assert first.has_main_guard is True
            assert second.has_main_guard is True

    def test_no_caching_without_fact_store(self):
        """Without FactStore, no caching occurs (backward compatible)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text(SAMPLE_PYTHON)

            extractor = SyntaxExtractor()
            extractor.extract(root / "test.py", root)
            extractor.extract(root / "test.py", root)

            stats = extractor.cache_stats()
            # Without fact_store, everything is a cache miss (no cache lookup)
            assert stats["hits"] == 0
            assert stats["misses"] == 2

    def test_cache_stats_hit_rate(self):
        """cache_stats() returns correct hit_rate."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor(fact_store=store)
            extractor.extract(root / "test.py", root)  # miss
            extractor.extract(root / "test.py", root)  # hit
            extractor.extract(root / "test.py", root)  # hit

            stats = extractor.cache_stats()
            assert stats["hits"] == 2
            assert stats["misses"] == 1
            assert abs(stats["hit_rate"] - 2.0 / 3.0) < 0.01

    def test_cache_stats_empty(self):
        """cache_stats() returns 0 hit_rate when no files processed."""
        extractor = SyntaxExtractor()
        stats = extractor.cache_stats()
        assert stats["hit_rate"] == 0.0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_reset_stats_clears_cache_counters(self):
        """reset_stats() also clears cache hit/miss counters."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor(fact_store=store)
            extractor.extract(root / "test.py", root)
            extractor.extract(root / "test.py", root)

            extractor.reset_stats()

            stats = extractor.cache_stats()
            assert stats["hits"] == 0
            assert stats["misses"] == 0

    def test_file_id_field_on_file_syntax(self):
        """FileSyntax has file_id field defaulting to None."""
        store = FactStore.in_memory()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test.py").write_text("def foo(): pass")

            extractor = SyntaxExtractor(fact_store=store)
            result = extractor.extract(root / "test.py", root)

            assert result is not None
            assert result.file_id is None  # default
