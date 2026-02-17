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
    import tree_sitter as _tree_sitter_module  # type: ignore[no-redef]

    TREE_SITTER_AVAILABLE = True

    # Try to import language grammars
    try:
        import tree_sitter_python

        _language_modules["python"] = tree_sitter_python
    except ImportError:
        pass

    try:
        import tree_sitter_go

        _language_modules["go"] = tree_sitter_go
    except ImportError:
        pass

    try:
        import tree_sitter_typescript

        _language_modules["typescript"] = tree_sitter_typescript
        # TSX is bundled with tree-sitter-typescript, store it separately
        _language_modules["tsx"] = tree_sitter_typescript
    except ImportError:
        pass

    try:
        import tree_sitter_javascript

        _language_modules["javascript"] = tree_sitter_javascript
    except ImportError:
        pass

    try:
        import tree_sitter_java

        _language_modules["java"] = tree_sitter_java
    except ImportError:
        pass

    try:
        import tree_sitter_rust

        _language_modules["rust"] = tree_sitter_rust
    except ImportError:
        pass

    try:
        import tree_sitter_ruby

        _language_modules["ruby"] = tree_sitter_ruby
    except ImportError:
        pass

    try:
        import tree_sitter_c

        _language_modules["c"] = tree_sitter_c
    except ImportError:
        pass

    try:
        import tree_sitter_cpp

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
                # Some modules use language_<name>() instead of language()
                lang_fn = getattr(lang_module, f"language_{lang_name}", None)
                if lang_fn is None:
                    lang_fn = getattr(lang_module, "language", None)
                if lang_fn is None:
                    continue

                raw_lang = lang_fn()
                # tree-sitter >= 0.23 returns PyCapsule; wrap in Language()
                lang_obj = _tree_sitter_module.Language(raw_lang)
                parser = _tree_sitter_module.Parser(lang_obj)
                self._parsers[lang_name] = parser
                self._languages[lang_name] = lang_obj
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
            # tree-sitter 0.25+: use QueryCursor for execution
            cursor = _tree_sitter_module.QueryCursor(query)
            matches = cursor.matches(tree.root_node)
            # Convert from [(pattern_id, {name: [nodes]})] to [(node, name)]
            result: list[Capture] = []
            for _pattern_id, captures_dict in matches:
                for capture_name, nodes in captures_dict.items():
                    for node in nodes:
                        result.append((node, capture_name))
            return result
        except Exception:
            return []

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in self._parsers
