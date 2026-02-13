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

# Cache for pyproject.toml entry points (computed once per session)
_ENTRY_POINT_CACHE: dict[str, set[str]] | None = None


# Test file patterns
TEST_PATH_PATTERNS = (
    re.compile(r"test_"),
    re.compile(r"_test\."),
    re.compile(r"tests[/\\]"),
    re.compile(r"spec[/\\]"),
    re.compile(r"_spec\."),
)

# Entry point decorators
ENTRY_POINT_DECORATORS = frozenset(
    {
        "click.command",
        "click.group",
        "app.command",
        "main",
        "typer.command",
    }
)

# Interface indicators
INTERFACE_BASES = frozenset({"ABC", "Protocol", "ABCMeta"})
INTERFACE_DECORATORS = frozenset({"abstractmethod", "abstractproperty"})

# CLI framework decorators
CLI_DECORATORS = frozenset(
    {
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
    }
)

# HTTP service indicators
SERVICE_BASES = frozenset(
    {
        "BaseHTTPRequestHandler",
        "HTTPServer",
        "View",
        "APIView",
        "Resource",
        "Handler",
        "Controller",
    }
)

# Migration patterns
MIGRATION_PATTERNS = (
    re.compile(r"migrations?[/\\]"),
    re.compile(r"alembic[/\\]versions"),
    re.compile(r"\d{4}_\w+\.py$"),  # Django style: 0001_initial.py
)


def _get_pyproject_entry_points(root_dir: str = "") -> set[str]:
    """Parse pyproject.toml to find script entry points.

    Returns set of file paths that are CLI entry points.
    Caches result for the session.
    """
    global _ENTRY_POINT_CACHE

    if _ENTRY_POINT_CACHE is not None:
        return _ENTRY_POINT_CACHE.get(root_dir, set())

    _ENTRY_POINT_CACHE = {}
    entry_points: set[str] = set()

    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[import-not-found]
        except ImportError:
            _ENTRY_POINT_CACHE[root_dir] = entry_points
            return entry_points

    pyproject_path = Path(root_dir) / "pyproject.toml" if root_dir else Path("pyproject.toml")
    if not pyproject_path.exists():
        _ENTRY_POINT_CACHE[root_dir] = entry_points
        return entry_points

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        # [project.scripts] and [project.gui-scripts]
        for section in ("scripts", "gui-scripts"):
            scripts = data.get("project", {}).get(section, {})
            for _name, target in scripts.items():
                # target is like "shannon_insight.cli:app"
                module_path = target.split(":")[0]
                # Convert to file path: "shannon_insight.cli" -> "shannon_insight/cli/__init__.py" or "shannon_insight/cli.py"
                file_path = module_path.replace(".", "/")
                entry_points.add(f"{file_path}.py")
                entry_points.add(f"{file_path}/__init__.py")
                entry_points.add(f"src/{file_path}.py")
                entry_points.add(f"src/{file_path}/__init__.py")

        # [project.entry-points] for plugins
        eps = data.get("project", {}).get("entry-points", {})
        for _group, entries in eps.items():
            if isinstance(entries, dict):
                for _name, target in entries.items():
                    module_path = target.split(":")[0]
                    file_path = module_path.replace(".", "/")
                    entry_points.add(f"{file_path}.py")
                    entry_points.add(f"{file_path}/__init__.py")
                    entry_points.add(f"src/{file_path}.py")
                    entry_points.add(f"src/{file_path}/__init__.py")
    except Exception:
        pass

    _ENTRY_POINT_CACHE[root_dir] = entry_points
    return entry_points


def classify_role(syntax: FileSyntax, root_dir: str = "") -> Role:
    """Classify file into a semantic role.

    Priority-based decision tree. First matching rule wins.

    Args:
        syntax: FileSyntax from tree-sitter or regex parsing
        root_dir: Project root directory for pyproject.toml lookup

    Returns:
        Role enum value
    """
    path = syntax.path
    path_lower = path.lower()

    # 1. TEST - test file patterns
    if _is_test_file(path_lower):
        return Role.TEST

    # 2. ENTRY_POINT - __main__ guard, entry decorators, or pyproject.toml scripts
    if syntax.has_main_guard or _has_entry_decorators(syntax):
        return Role.ENTRY_POINT

    # Check pyproject.toml entry points
    entry_points = _get_pyproject_entry_points(root_dir)
    if path in entry_points or any(path.endswith(ep) for ep in entry_points):
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

    # 10.5. Filename heuristic — soft fallback before UTILITY/CONFIG
    filename_role = _filename_heuristic(syntax, path_lower)
    if filename_role is not None:
        return filename_role

    # 11. UTILITY - functions with at most one small class
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
            if (
                base_simple in exception_bases
                or "Error" in base_simple
                or "Exception" in base_simple
            ):
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

    # Filename hint: "models.py" or "schemas.py" with classes having >= 2 fields
    stem = Path(syntax.path).stem.lower()
    filename_is_model = stem in ("models", "schemas", "model", "schema")

    for cls in syntax.classes:
        is_model = False

        # Check bases for Pydantic, Django, etc.
        for base in cls.bases:
            if any(ind in base for ind in model_indicators):
                is_model = True
                break

        # Check field-heavy heuristic: many fields, few methods
        if cls.fields and len(cls.fields) > 3 and len(cls.methods) <= len(cls.fields):
            is_model = True

        # Filename hint + any fields → model
        if filename_is_model and cls.fields and len(cls.fields) >= 2:
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
    """Check for stateful classes with methods.

    Requires >= 3 non-dunder methods AND __init__ with state storage.
    This avoids classifying analyzer/finder classes (1-2 public methods) as SERVICE.
    """
    for cls in syntax.classes:
        non_dunder_methods = [m for m in cls.methods if not m.name.startswith("__")]
        has_init = any(m.name == "__init__" for m in cls.methods)
        has_fields = bool(cls.fields)

        # Need substantial method surface AND state
        if len(non_dunder_methods) >= 3 and (has_init or has_fields):
            return True
    return False


def _is_utility(syntax: FileSyntax) -> bool:
    """Check if file is primarily functions (utility module).

    Allows at most 1 small helper class alongside functions.
    """
    if syntax.functions and syntax.function_count > syntax.class_count and syntax.class_count <= 1:
        return True
    return False


def _filename_heuristic(syntax: FileSyntax, path_lower: str) -> Role | None:
    """Soft fallback: classify by filename/directory when structural checks fail.

    Only fires after all structural checks. Returns None if no match.
    """
    stem = Path(path_lower).stem
    parts = Path(path_lower).parts

    # Model/schema files with classes
    if stem in ("models", "schemas", "model", "schema") and syntax.classes:
        return Role.MODEL

    # Finder/analyzer/extractor/plugin patterns → UTILITY
    utility_stems = {"finder", "analyzer", "extractor", "plugin", "scanner", "builder"}
    if stem in utility_stems or any(s in stem for s in utility_stems):
        return Role.UTILITY

    # Directory-based patterns
    utility_dirs = {"finders", "analyzers", "plugins", "scanners", "extractors", "builders"}
    if any(d in parts for d in utility_dirs):
        return Role.UTILITY

    # conftest.py → CONFIG
    if stem == "conftest":
        return Role.CONFIG

    return None


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
