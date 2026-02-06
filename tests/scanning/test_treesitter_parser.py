"""Tests for tree-sitter parser wrapper."""

import pytest

from shannon_insight.scanning.treesitter_parser import (
    TREE_SITTER_AVAILABLE,
    TreeSitterParser,
    get_supported_languages,
)


class TestTreeSitterAvailability:
    """Test tree-sitter availability detection."""

    def test_availability_flag_is_bool(self):
        """TREE_SITTER_AVAILABLE is a boolean."""
        assert isinstance(TREE_SITTER_AVAILABLE, bool)

    def test_supported_languages_returns_list(self):
        """get_supported_languages returns a list."""
        languages = get_supported_languages()
        assert isinstance(languages, list)

    def test_supported_languages_empty_when_unavailable(self):
        """If tree-sitter not installed, supported languages is empty."""
        if not TREE_SITTER_AVAILABLE:
            assert get_supported_languages() == []


@pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not installed")
class TestTreeSitterParser:
    """Tests that require tree-sitter to be installed."""

    def test_can_instantiate(self):
        """Can create TreeSitterParser."""
        parser = TreeSitterParser()
        assert parser is not None

    def test_python_in_supported_languages(self):
        """Python is a supported language."""
        languages = get_supported_languages()
        assert "python" in languages

    def test_parse_python_returns_tree(self):
        """parse() returns a tree for valid Python."""
        parser = TreeSitterParser()
        code = "def foo():\n    pass\n"
        tree = parser.parse(code.encode(), "python")
        assert tree is not None
        assert tree.root_node is not None

    def test_parse_invalid_language_returns_none(self):
        """parse() returns None for unsupported language."""
        parser = TreeSitterParser()
        tree = parser.parse(b"some code", "unknown_language")
        assert tree is None

    def test_query_returns_captures(self):
        """query() returns captures."""
        parser = TreeSitterParser()
        code = "def foo():\n    pass\n"
        tree = parser.parse(code.encode(), "python")

        # Simple query for function definitions
        query_str = "(function_definition name: (identifier) @name)"
        captures = parser.query(tree, query_str, "python")

        assert len(captures) > 0
        # Should find 'foo'
        names = [node.text.decode() for node, _ in captures if node.text]
        assert "foo" in names


class TestTreeSitterParserFallback:
    """Test behavior when tree-sitter not available."""

    def test_parser_handles_missing_gracefully(self):
        """Parser doesn't crash when tree-sitter missing."""
        # This test always runs, regardless of tree-sitter availability
        parser = TreeSitterParser()
        if not TREE_SITTER_AVAILABLE:
            # Should return None without crashing
            tree = parser.parse(b"def foo(): pass", "python")
            assert tree is None


@pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not installed")
class TestMultiLanguageSupport:
    """Test multiple language support."""

    def test_go_parse(self):
        """Can parse Go code."""
        languages = get_supported_languages()
        if "go" not in languages:
            pytest.skip("Go grammar not installed")

        parser = TreeSitterParser()
        code = "package main\n\nfunc main() {\n}\n"
        tree = parser.parse(code.encode(), "go")
        assert tree is not None

    def test_typescript_parse(self):
        """Can parse TypeScript code."""
        languages = get_supported_languages()
        if "typescript" not in languages:
            pytest.skip("TypeScript grammar not installed")

        parser = TreeSitterParser()
        code = "function greet(name: string): string { return name; }"
        tree = parser.parse(code.encode(), "typescript")
        assert tree is not None

    def test_javascript_parse(self):
        """Can parse JavaScript code."""
        languages = get_supported_languages()
        if "javascript" not in languages:
            pytest.skip("JavaScript grammar not installed")

        parser = TreeSitterParser()
        code = "function greet(name) { return name; }"
        tree = parser.parse(code.encode(), "javascript")
        assert tree is not None
