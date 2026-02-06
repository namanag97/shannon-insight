"""Tests for SyntaxExtractor."""

import tempfile
from pathlib import Path

import pytest

from shannon_insight.scanning.models_v2 import FileSyntax
from shannon_insight.scanning.syntax_extractor import SyntaxExtractor
from shannon_insight.scanning.treesitter_parser import TREE_SITTER_AVAILABLE

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
            results = extractor.extract_all(
                [root / "a.py", root / "b.py", root / "c.py"],
                root
            )

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


@pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not installed")
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
