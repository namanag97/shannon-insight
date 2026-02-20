"""Syntax extraction from source files."""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

from .models import FileSyntax, Function, Import

# Language detection by extension
LANG_MAP = {
    ".py": "python",
    ".go": "go",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".java": "java",
    ".rs": "rust",
    ".rb": "ruby",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
}


def detect_language(path: str) -> str:
    """Detect language from file extension."""
    suffix = Path(path).suffix.lower()
    return LANG_MAP.get(suffix, "unknown")


def extract_syntax(path: str, content: bytes) -> FileSyntax:
    """Extract syntax information from file content."""
    text = content.decode("utf-8", errors="replace")
    content_hash = hashlib.sha256(content).hexdigest()
    language = detect_language(path)

    lines = text.count("\n") + 1

    # Language-specific extraction
    if language == "python":
        return _extract_python(path, text, content_hash, lines)
    else:
        return _extract_generic(path, text, content_hash, lines, language)


def _extract_python(path: str, text: str, content_hash: str, lines: int) -> FileSyntax:
    """Extract syntax from Python file."""
    import ast

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _extract_generic(path, text, content_hash, lines, "python")

    functions = []
    classes = []
    imports = []
    identifiers = set()
    max_nesting = 0
    complexity = 1
    has_main_guard = False

    for node in ast.walk(tree):
        # Functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_tokens = sum(1 for _ in ast.walk(node)) - 1
            sig_tokens = len(node.args.args) + len(node.args.kwonlyargs)
            functions.append(Function(
                name=node.name,
                params=len(node.args.args),
                body_tokens=body_tokens,
                signature_tokens=sig_tokens,
                nesting_depth=0,  # Simplified
                start_line=node.lineno,
                end_line=node.end_lineno or node.lineno,
            ))
            identifiers.add(node.name)

        # Classes
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
            identifiers.add(node.name)

        # Imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(Import(
                    module=alias.name,
                    names=(),
                    level=0,
                    line=node.lineno,
                ))
        elif isinstance(node, ast.ImportFrom):
            imports.append(Import(
                module=node.module or "",
                names=tuple(a.name for a in node.names),
                level=node.level,
                line=node.lineno,
            ))

        # Complexity
        elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1

        # Names
        elif isinstance(node, ast.Name):
            identifiers.add(node.id)

    # Check for if __name__ == "__main__"
    # NOTE: ast.Str was deprecated in 3.8 and removed in 3.12; use ast.Constant instead.
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare):
                comparators = node.test.comparators
                for c in comparators:
                    # Python 3.8+: use ast.Constant; ast.Str removed in 3.12
                    if isinstance(c, ast.Constant) and c.value == "__main__":
                        has_main_guard = True
                        break

    return FileSyntax(
        path=path,
        language="python",
        content_hash=content_hash,
        lines=lines,
        functions=functions,
        classes=classes,
        imports=imports,
        identifiers=frozenset(identifiers),
        complexity=complexity,
        max_nesting=max_nesting,
        has_main_guard=has_main_guard,
    )


def _extract_generic(path: str, text: str, content_hash: str, lines: int, language: str) -> FileSyntax:
    """Fallback regex-based extraction."""
    # Simple patterns
    func_pattern = re.compile(r'\b(?:def|func|function|fn)\s+(\w+)')
    class_pattern = re.compile(r'\bclass\s+(\w+)')
    import_pattern = re.compile(r'(?:import|from|require|use)\s+["\']?(\w+)')

    functions = [
        Function(name=m.group(1), params=0, body_tokens=10, signature_tokens=2,
                 nesting_depth=0, start_line=0, end_line=0)
        for m in func_pattern.finditer(text)
    ]
    classes = [m.group(1) for m in class_pattern.finditer(text)]
    imports = [
        Import(module=m.group(1), names=(), level=0, line=0)
        for m in import_pattern.finditer(text)
    ]
    identifiers = frozenset(re.findall(r'\b[a-zA-Z_]\w*\b', text))

    return FileSyntax(
        path=path,
        language=language,
        content_hash=content_hash,
        lines=lines,
        functions=functions,
        classes=classes,
        imports=imports,
        identifiers=identifiers,
        complexity=1,
        max_nesting=0,
        has_main_guard=False,
    )
