"""IR1 syntax context: tree-sitter parsing into FileSyntax records."""

from shannon_insight.syntax.models import (
    ClassDef,
    FileSyntax,
    FunctionDef,
    ImportDecl,
)
from shannon_insight.syntax.parser import ParserManager, analyze_source
from shannon_insight.syntax.packs import PackSpec, detect_language

__all__ = [
    "ClassDef",
    "FileSyntax",
    "FunctionDef",
    "ImportDecl",
    "PackSpec",
    "ParserManager",
    "analyze_source",
    "detect_language",
]
