"""Semantic data models for Phase 2 IR2 layer.

FileSemantics holds all semantic information about a file:
- Role classification (what kind of file is this?)
- Concept extraction (what topics does this file cover?)
- Naming drift (does the filename match the content?)
- Completeness metrics (TODOs, documentation coverage)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Role(Enum):
    """File role classification.

    Priority order (first match wins):
    1. TEST - test files
    2. ENTRY_POINT - has __main__ guard or CLI entry decorators
    3. INTERFACE - ABC, Protocol, or abstractmethod
    4. CONSTANT - all UPPER_SNAKE_CASE identifiers
    5. EXCEPTION - custom exception classes
    6. MODEL - field-heavy data classes
    7. CLI - CLI framework decorators
    8. SERVICE - HTTP handlers or stateful classes
    9. MIGRATION - database migration patterns
    10. UTILITY - pure functions, no classes
    11. CONFIG - re-exports, __all__, __init__.py
    12. UNKNOWN - no pattern matched
    """

    TEST = "test"
    ENTRY_POINT = "entry_point"
    INTERFACE = "interface"
    CONSTANT = "constant"
    EXCEPTION = "exception"
    MODEL = "model"
    CLI = "cli"
    SERVICE = "service"
    MIGRATION = "migration"
    UTILITY = "utility"
    CONFIG = "config"
    UNKNOWN = "unknown"


@dataclass
class Concept:
    """A semantic concept (topic) extracted from a file.

    Attributes:
        topic: Concept name/label (e.g., "authentication", "parsing")
        weight: Relative importance [0, 1]
        keywords: Representative keywords for this concept
    """

    topic: str
    weight: float
    keywords: list[str] = field(default_factory=list)


@dataclass
class Completeness:
    """Documentation and TODO metrics.

    Attributes:
        todo_density: TODOs per 100 lines of code
        docstring_coverage: Ratio of documented functions/classes [0, 1]
            None for non-Python (can't measure reliably)
        todo_count: Raw count of TODO/FIXME/HACK markers
        documented_count: Number of documented items
        total_documentable: Total items that could have docs
    """

    todo_density: float = 0.0
    docstring_coverage: Optional[float] = None
    todo_count: int = 0
    documented_count: int = 0
    total_documentable: int = 0


@dataclass
class FileSemantics:
    """Complete semantic analysis for a file.

    Produced by SemanticAnalyzer for each source file.

    Attributes:
        path: File path (relative)
        role: Classified file role
        concepts: Extracted concept clusters
        concept_count: Number of distinct concepts
        concept_entropy: Shannon entropy of concept weights
        naming_drift: Dissimilarity between filename and content [0, 1]
        completeness: TODO density and docstring coverage
        tier: Which extraction tier was used (1, 2, or 3)
    """

    path: str
    role: Role
    concepts: list[Concept] = field(default_factory=list)
    concept_count: int = 0
    concept_entropy: float = 0.0
    naming_drift: float = 0.0
    completeness: Completeness = field(default_factory=Completeness)
    tier: int = 1

    @property
    def todo_density(self) -> float:
        """Shortcut to completeness.todo_density."""
        return self.completeness.todo_density

    @property
    def docstring_coverage(self) -> Optional[float]:
        """Shortcut to completeness.docstring_coverage."""
        return self.completeness.docstring_coverage

    @property
    def primary_concept(self) -> str:
        """Get the highest-weight concept topic, or role name if no concepts."""
        if not self.concepts:
            return self.role.value
        return max(self.concepts, key=lambda c: c.weight).topic


# Generic filenames that should not trigger naming drift
GENERIC_FILENAMES = frozenset({
    "utils",
    "util",
    "utilities",
    "helpers",
    "helper",
    "common",
    "misc",
    "shared",
    "base",
    "core",
    "__init__",
    "index",
    "main",
    "app",
    "config",
    "settings",
    "constants",
    "types",
    "models",
    "schemas",
    "exceptions",
    "errors",
})
