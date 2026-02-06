"""Documentation completeness metrics.

- todo_density: TODOs per 100 lines of code
- docstring_coverage: Ratio of documented functions/classes
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .models import Completeness

if TYPE_CHECKING:
    from ..scanning.models_v2 import FileSyntax


# TODO/FIXME/HACK patterns
TODO_PATTERNS = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\bHACK\b", re.IGNORECASE),
    re.compile(r"\bXXX\b"),
    re.compile(r"\bBUG\b", re.IGNORECASE),
)


def compute_completeness(syntax: FileSyntax, content: str) -> Completeness:
    """Compute documentation completeness metrics.

    Args:
        syntax: FileSyntax for the file
        content: Raw file content

    Returns:
        Completeness dataclass with todo_density and docstring_coverage
    """
    # Count TODOs
    todo_count = count_todos(content)

    # Count lines
    lines = content.count("\n") + 1 if content else 0

    # TODO density per 100 lines
    todo_density = (todo_count / lines * 100) if lines > 0 else 0.0

    # Docstring coverage (Python only)
    docstring_coverage, documented, documentable = compute_docstring_coverage(syntax, content)

    return Completeness(
        todo_density=todo_density,
        docstring_coverage=docstring_coverage,
        todo_count=todo_count,
        documented_count=documented,
        total_documentable=documentable,
    )


def count_todos(content: str) -> int:
    """Count TODO/FIXME/HACK/XXX/BUG markers in content."""
    count = 0
    for pattern in TODO_PATTERNS:
        count += len(pattern.findall(content))
    return count


def compute_docstring_coverage(syntax: FileSyntax, content: str) -> tuple[float | None, int, int]:
    """Compute docstring coverage for Python files.

    Args:
        syntax: FileSyntax
        content: Raw content

    Returns:
        (coverage, documented_count, total_documentable)
        coverage is None for non-Python files
    """
    # Only Python has reliable docstring detection
    if syntax.language != "python":
        return None, 0, 0

    # Count documentable items (functions and classes)
    total_documentable = syntax.function_count + syntax.class_count

    if total_documentable == 0:
        return 1.0, 0, 0  # Nothing to document = fully documented

    # Try to detect docstrings using AST if possible
    # Fall back to regex-based detection
    documented = 0

    for fn in syntax.functions:
        if has_docstring(content, fn.start_line, fn.end_line):
            documented += 1

    for cls in syntax.classes:
        # For classes, check if class itself has docstring
        # (we don't have start/end lines for classes in FileSyntax, use name search)
        if has_class_docstring(content, cls.name):
            documented += 1

    coverage = documented / total_documentable if total_documentable > 0 else 1.0
    return coverage, documented, total_documentable


def has_docstring(content: str, start_line: int, end_line: int) -> bool:
    """Check if function has a docstring.

    Looks for triple-quoted string on the line after function def.
    """
    lines = content.split("\n")

    if start_line < 1 or start_line > len(lines):
        return False

    # Look at lines after the def line
    for i in range(start_line, min(start_line + 3, end_line, len(lines))):
        line = lines[i].strip()
        if line.startswith('"""') or line.startswith("'''"):
            return True
        if line.startswith('r"""') or line.startswith("r'''"):
            return True
        # Non-empty, non-docstring line means no docstring
        if line and not line.startswith("#"):
            break

    return False


def has_class_docstring(content: str, class_name: str) -> bool:
    """Check if class has a docstring.

    Searches for class definition and checks next lines for docstring.
    """
    # Find class definition
    pattern = re.compile(rf"^\s*class\s+{re.escape(class_name)}\s*[:(]", re.MULTILINE)
    match = pattern.search(content)

    if not match:
        return False

    # Get content after class def
    after_def = content[match.end() :]
    lines = after_def.split("\n")

    # Look for docstring in first few lines after class:
    for line in lines[:5]:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            return True
        if stripped.startswith('r"""') or stripped.startswith("r'''"):
            return True
        # Skip empty lines and comments
        if stripped and not stripped.startswith("#") and stripped != ":":
            # Non-docstring content found
            break

    return False
