"""Tree-sitter parser wrapper.

Provides a unified interface for tree-sitter parsing across languages.
Handles missing tree-sitter dependency gracefully.

Usage:
    if TREE_SITTER_AVAILABLE:
        parser = TreeSitterParser()
        tree = parser.parse(code_bytes, "python")
        captures = parser.query(tree, query_str, "python")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Try to import tree-sitter
TREE_SITTER_AVAILABLE = False
_tree_sitter_module: Any = None
_language_modules: dict[str, Any] = {}

try:
    import tree_sitter as _tree_sitter_module  # type: ignore[import-not-found,no-redef]

    TREE_SITTER_AVAILABLE = True

    # Try to import language grammars
    try:
        import tree_sitter_python  # type: ignore

        _language_modules["python"] = tree_sitter_python
    except ImportError:
        pass

    try:
        import tree_sitter_go  # type: ignore

        _language_modules["go"] = tree_sitter_go
    except ImportError:
        pass

    try:
        import tree_sitter_typescript  # type: ignore

        _language_modules["typescript"] = tree_sitter_typescript
    except ImportError:
        pass

    try:
        import tree_sitter_javascript  # type: ignore

        _language_modules["javascript"] = tree_sitter_javascript
    except ImportError:
        pass

    try:
        import tree_sitter_java  # type: ignore

        _language_modules["java"] = tree_sitter_java
    except ImportError:
        pass

    try:
        import tree_sitter_rust  # type: ignore

        _language_modules["rust"] = tree_sitter_rust
    except ImportError:
        pass

    try:
        import tree_sitter_ruby  # type: ignore

        _language_modules["ruby"] = tree_sitter_ruby
    except ImportError:
        pass

    try:
        import tree_sitter_c  # type: ignore

        _language_modules["c"] = tree_sitter_c
    except ImportError:
        pass

    try:
        import tree_sitter_cpp  # type: ignore

        _language_modules["cpp"] = tree_sitter_cpp
    except ImportError:
        pass

except ImportError:
    TREE_SITTER_AVAILABLE = False


if TYPE_CHECKING:
    # Type stubs for tree-sitter (not installed, just for type checking)
    class Node:
        text: bytes | None
        type: str
        start_point: tuple[int, int]
        end_point: tuple[int, int]
        children: list[Node]

    class Tree:
        root_node: Node

    Capture = tuple[Node, str]


def get_supported_languages() -> list[str]:
    """Get list of languages with installed grammars."""
    if not TREE_SITTER_AVAILABLE:
        return []
    return list(_language_modules.keys())


class TreeSitterParser:
    """Wrapper around tree-sitter for multi-language parsing.

    Handles missing dependencies gracefully. Check TREE_SITTER_AVAILABLE
    before using, or check if parse() returns None.
    """

    def __init__(self) -> None:
        """Initialize parser with available languages."""
        self._parsers: dict[str, Any] = {}
        self._languages: dict[str, Any] = {}

        if not TREE_SITTER_AVAILABLE:
            return

        # Initialize parsers for available languages
        for lang_name, lang_module in _language_modules.items():
            try:
                parser = _tree_sitter_module.Parser(lang_module.language())
                self._parsers[lang_name] = parser
                self._languages[lang_name] = lang_module.language()
            except Exception:
                # Skip if parser creation fails
                pass

    def parse(self, code: bytes, language: str) -> Tree | None:
        """Parse code and return syntax tree.

        Args:
            code: Source code as bytes
            language: Language name (e.g., "python")

        Returns:
            Tree object if successful, None if language not supported
            or tree-sitter not available
        """
        if not TREE_SITTER_AVAILABLE:
            return None

        parser = self._parsers.get(language)
        if parser is None:
            return None

        try:
            result: Tree | None = parser.parse(code)
            return result
        except Exception:
            return None

    def query(self, tree: Tree | None, query_str: str, language: str) -> list[Capture]:
        """Run a query on a syntax tree.

        Args:
            tree: Syntax tree from parse()
            query_str: S-expression query string
            language: Language name

        Returns:
            List of (node, capture_name) tuples
        """
        if not TREE_SITTER_AVAILABLE or tree is None:
            return []

        lang = self._languages.get(language)
        if lang is None:
            return []

        try:
            query = _tree_sitter_module.Query(lang, query_str)
            result: list[Capture] = query.captures(tree.root_node)
            return result
        except Exception:
            return []

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in self._parsers
