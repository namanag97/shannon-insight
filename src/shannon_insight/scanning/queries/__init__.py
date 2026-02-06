"""Tree-sitter query registry.

Maps language names to their query modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import c_cpp, go, java, javascript, python, ruby, rust, typescript

if TYPE_CHECKING:
    from types import ModuleType

# Language to query module mapping
QUERY_MODULES: dict[str, ModuleType] = {
    "python": python,
    "go": go,
    "typescript": typescript,
    "javascript": javascript,
    "java": java,
    "rust": rust,
    "ruby": ruby,
    "c": c_cpp,
    "cpp": c_cpp,
}


def get_queries(language: str) -> dict[str, str] | None:
    """Get all queries for a language.

    Args:
        language: Language name (e.g., "python", "go")

    Returns:
        Dict of query_name -> query_string, or None if language unsupported
    """
    module = QUERY_MODULES.get(language)
    if module is None:
        return None
    return module.get_all_queries()


def get_query(language: str, query_name: str) -> str | None:
    """Get a specific query for a language.

    Args:
        language: Language name
        query_name: Query name (e.g., "function", "class", "import")

    Returns:
        Query string or None if not found
    """
    queries = get_queries(language)
    if queries is None:
        return None
    return queries.get(query_name)


def supported_languages() -> list[str]:
    """Get list of languages with query modules."""
    return list(QUERY_MODULES.keys())


__all__ = [
    "QUERY_MODULES",
    "get_queries",
    "get_query",
    "supported_languages",
]
