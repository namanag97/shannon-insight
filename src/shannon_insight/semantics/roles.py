"""Role classification decision tree.

Classifies files into semantic roles based on structural patterns.
First matching rule wins (priority-based).

See spec: docs/v2/phases/phase-2-semantics.md
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from .models import Role

if TYPE_CHECKING:
    from ..scanning.models_v2 import FileSyntax


# Test file patterns
TEST_PATH_PATTERNS = (
    re.compile(r"test_"),
    re.compile(r"_test\."),
    re.compile(r"tests[/\\]"),
    re.compile(r"spec[/\\]"),
    re.compile(r"_spec\."),
)

# Entry point decorators
ENTRY_POINT_DECORATORS = frozenset({
    "click.command",
    "click.group",
    "app.command",
    "main",
    "typer.command",
})

# Interface indicators
INTERFACE_BASES = frozenset({"ABC", "Protocol", "ABCMeta"})
INTERFACE_DECORATORS = frozenset({"abstractmethod", "abstractproperty"})

# CLI framework decorators
CLI_DECORATORS = frozenset({
    "app.route",
    "router.route",
    "app.get",
    "app.post",
    "app.put",
    "app.delete",
    "app.patch",
    "route",
    "get",
    "post",
    "put",
    "delete",
})

# HTTP service indicators
SERVICE_BASES = frozenset({
    "BaseHTTPRequestHandler",
    "HTTPServer",
    "View",
    "APIView",
    "Resource",
    "Handler",
    "Controller",
})

# Migration patterns
MIGRATION_PATTERNS = (
    re.compile(r"migrations?[/\\]"),
    re.compile(r"alembic[/\\]versions"),
    re.compile(r"\d{4}_\w+\.py$"),  # Django style: 0001_initial.py
)


def classify_role(syntax: FileSyntax) -> Role:
    """Classify file into a semantic role.

    Priority-based decision tree. First matching rule wins.

    Args:
        syntax: FileSyntax from tree-sitter or regex parsing

    Returns:
        Role enum value
    """
    path = syntax.path
    path_lower = path.lower()

    # 1. TEST - test file patterns
    if _is_test_file(path_lower):
        return Role.TEST

    # 2. ENTRY_POINT - __main__ guard or entry decorators
    if syntax.has_main_guard or _has_entry_decorators(syntax):
        return Role.ENTRY_POINT

    # 3. INTERFACE - ABC, Protocol, abstractmethod
    if _is_interface(syntax):
        return Role.INTERFACE

    # 4. CONSTANT - all UPPER_SNAKE_CASE
    if _is_constants_file(syntax):
        return Role.CONSTANT

    # 5. EXCEPTION - custom exception classes
    if _is_exception_module(syntax):
        return Role.EXCEPTION

    # 6. MODEL - field-heavy data classes
    if _is_model_file(syntax):
        return Role.MODEL

    # 7. CLI - CLI framework patterns
    if _has_cli_decorators(syntax):
        return Role.CLI

    # 8. SERVICE - HTTP handlers
    if _is_service(syntax):
        return Role.SERVICE

    # 9. MIGRATION - database migration
    if _is_migration(path_lower):
        return Role.MIGRATION

    # 10. SERVICE - stateful classes with methods (if not caught above)
    if _has_stateful_classes(syntax):
        return Role.SERVICE

    # 11. UTILITY - pure functions, no classes
    if _is_utility(syntax):
        return Role.UTILITY

    # 12. CONFIG - re-exports, __all__, __init__.py
    if _is_config(syntax, path_lower):
        return Role.CONFIG

    # 13. UNKNOWN - no pattern matched
    return Role.UNKNOWN


def _is_test_file(path_lower: str) -> bool:
    """Check if path matches test file patterns."""
    return any(pattern.search(path_lower) for pattern in TEST_PATH_PATTERNS)


def _has_entry_decorators(syntax: FileSyntax) -> bool:
    """Check for entry point decorators."""
    for fn in syntax.functions:
        for dec in fn.decorators:
            if dec in ENTRY_POINT_DECORATORS or "main" in dec.lower():
                return True
    return False


def _is_interface(syntax: FileSyntax) -> bool:
    """Check for ABC, Protocol, or abstractmethod."""
    for cls in syntax.classes:
        if cls.is_abstract:
            return True
        for base in cls.bases:
            if base in INTERFACE_BASES:
                return True
        for method in cls.methods:
            for dec in method.decorators:
                if dec in INTERFACE_DECORATORS:
                    return True
    # Also check top-level functions for abstractmethod
    for fn in syntax.functions:
        for dec in fn.decorators:
            if dec in INTERFACE_DECORATORS:
                return True
    return False


def _is_constants_file(syntax: FileSyntax) -> bool:
    """Check if all identifiers are UPPER_SNAKE_CASE."""
    if not syntax.functions and not syntax.classes:
        return False

    # Get all function names
    all_names = [fn.name for fn in syntax.functions]
    all_names.extend(cls.name for cls in syntax.classes)

    if not all_names:
        return False

    # Check if all are UPPER_SNAKE_CASE
    upper_snake = re.compile(r"^[A-Z][A-Z0-9_]*$")
    return all(upper_snake.match(name) for name in all_names)


def _is_exception_module(syntax: FileSyntax) -> bool:
    """Check if majority of classes are exceptions."""
    if not syntax.classes:
        return False

    exception_bases = {"Exception", "BaseException", "Error", "Warning"}
    exception_count = 0

    for cls in syntax.classes:
        for base in cls.bases:
            base_simple = base.split(".")[-1]  # Handle module.Exception
            if base_simple in exception_bases or "Error" in base_simple or "Exception" in base_simple:
                exception_count += 1
                break

    # Majority = more than half
    return exception_count > len(syntax.classes) / 2


def _is_model_file(syntax: FileSyntax) -> bool:
    """Check if classes are field-heavy (data classes/models)."""
    if not syntax.classes:
        return False

    model_indicators = {"dataclass", "BaseModel", "Model", "Schema", "NamedTuple", "TypedDict"}
    model_count = 0

    for cls in syntax.classes:
        # Check decorators for @dataclass
        # Note: decorators might not be populated if using regex fallback
        is_model = False

        # Check bases for Pydantic, Django, etc.
        for base in cls.bases:
            if any(ind in base for ind in model_indicators):
                is_model = True
                break

        # Check field-heavy heuristic: many fields, few methods
        if cls.fields and len(cls.fields) > 3 and len(cls.methods) <= len(cls.fields):
            is_model = True

        if is_model:
            model_count += 1

    # Majority of classes are models
    return model_count > len(syntax.classes) / 2


def _has_cli_decorators(syntax: FileSyntax) -> bool:
    """Check for CLI framework decorators."""
    for fn in syntax.functions:
        for dec in fn.decorators:
            if any(cli in dec for cli in CLI_DECORATORS):
                return True
    return False


def _is_service(syntax: FileSyntax) -> bool:
    """Check for HTTP service patterns."""
    for cls in syntax.classes:
        for base in cls.bases:
            base_simple = base.split(".")[-1]
            if base_simple in SERVICE_BASES or "Handler" in base_simple or "View" in base_simple:
                return True

    # Check for HTTP decorators
    for fn in syntax.functions:
        for dec in fn.decorators:
            if any(http in dec for http in ("get", "post", "put", "delete", "route")):
                return True

    return False


def _is_migration(path_lower: str) -> bool:
    """Check for database migration patterns."""
    return any(pattern.search(path_lower) for pattern in MIGRATION_PATTERNS)


def _has_stateful_classes(syntax: FileSyntax) -> bool:
    """Check for stateful classes with methods."""
    for cls in syntax.classes:
        # Has methods beyond __init__
        non_init_methods = [m for m in cls.methods if not m.name.startswith("__")]
        if non_init_methods:
            return True
    return False


def _is_utility(syntax: FileSyntax) -> bool:
    """Check if file is pure functions (utility module)."""
    # Has functions but no classes
    if syntax.functions and not syntax.classes:
        return True
    return False


def _is_config(syntax: FileSyntax, path_lower: str) -> bool:
    """Check for config/init patterns."""
    # __init__.py files
    if path_lower.endswith("__init__.py"):
        return True

    # Files with mostly imports and few definitions
    if syntax.import_count > 0 and syntax.function_count == 0 and syntax.class_count == 0:
        return True

    # config/settings patterns
    config_patterns = ("config", "settings", "conf")
    basename = Path(path_lower).stem
    if any(pattern in basename for pattern in config_patterns):
        return True

    return False
