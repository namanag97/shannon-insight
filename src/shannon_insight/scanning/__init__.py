"""Language-aware file scanning.

Core components:
- FileSyntax: Unified syntax model for parsed files
- SyntaxExtractor: Parses files into FileSyntax (tree-sitter or regex)
- LanguageConfig: Language-specific patterns and settings
"""

from .fallback import RegexFallbackScanner
from .languages import (
    DEFAULT_SOURCE_EXTENSIONS,
    LANGUAGES,
    SKIP_DIRS,
    LanguageConfig,
    detect_language,
    get_all_known_extensions,
    get_language_config,
)
from .syntax import ClassDef, FileSyntax, FunctionDef, ImportDecl
from .syntax_extractor import SyntaxExtractor
from .treesitter_parser import TREE_SITTER_AVAILABLE, TreeSitterParser

__all__ = [
    # Language config
    "LanguageConfig",
    "LANGUAGES",
    "SKIP_DIRS",
    "DEFAULT_SOURCE_EXTENSIONS",
    "get_language_config",
    "get_all_known_extensions",
    "detect_language",
    # FileSyntax models
    "FileSyntax",
    "FunctionDef",
    "ClassDef",
    "ImportDecl",
    # Parsers
    "TREE_SITTER_AVAILABLE",
    "TreeSitterParser",
    "RegexFallbackScanner",
    "SyntaxExtractor",
]
