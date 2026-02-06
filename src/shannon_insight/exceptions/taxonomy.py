"""Enterprise error taxonomy with error codes and recovery strategies.

Error Code Convention:
    SC1xx - Scanning errors
    SC2xx - Semantic errors
    SC3xx - Graph errors
    SC4xx - Temporal errors
    SC5xx - Architecture errors
    SC6xx - Signal errors
    SC7xx - Finder errors
    SC8xx - Validation errors
    SC9xx - Persistence errors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorCode(Enum):
    """Structured error codes for observability and debugging."""

    # Scanning errors (SC1xx)
    SC100 = "SC100"  # File read error
    SC101 = "SC101"  # Encoding detection failed
    SC102 = "SC102"  # Tree-sitter parse failed
    SC103 = "SC103"  # Regex fallback failed

    # Semantic errors (SC2xx)
    SC200 = "SC200"  # Concept extraction failed (too few tokens)
    SC201 = "SC201"  # Role classification ambiguous
    SC202 = "SC202"  # TF-IDF computation failed

    # Graph errors (SC3xx)
    SC300 = "SC300"  # Import resolution failed
    SC301 = "SC301"  # Call resolution failed
    SC302 = "SC302"  # Clone detection timeout
    SC303 = "SC303"  # Graph has unreachable nodes

    # Temporal errors (SC4xx)
    SC400 = "SC400"  # Git not found
    SC401 = "SC401"  # Git log parse failed
    SC402 = "SC402"  # Git subprocess timeout
    SC403 = "SC403"  # Shallow clone detected

    # Architecture errors (SC5xx)
    SC500 = "SC500"  # Module detection failed
    SC501 = "SC501"  # Layer inference cycle detected
    SC502 = "SC502"  # Martin metrics undefined (isolated module)

    # Signal errors (SC6xx)
    SC600 = "SC600"  # Percentile on non-percentileable signal
    SC601 = "SC601"  # Composite input missing
    SC602 = "SC602"  # Normalization tier mismatch

    # Finder errors (SC7xx)
    SC700 = "SC700"  # Required signal unavailable
    SC701 = "SC701"  # Threshold evaluation failed
    SC702 = "SC702"  # Confidence computation failed

    # Validation errors (SC8xx)
    SC800 = "SC800"  # Phase contract violated
    SC801 = "SC801"  # Store slot type mismatch
    SC802 = "SC802"  # Adjacency/reverse inconsistent

    # Persistence errors (SC9xx)
    SC900 = "SC900"  # SQLite write failed
    SC901 = "SC901"  # Schema migration failed
    SC902 = "SC902"  # Snapshot corruption detected


@dataclass
class ShannonError(Exception):
    """Base exception with structured context for enterprise logging.

    Attributes:
        message: Human-readable error description
        code: Structured error code for categorization
        context: Additional context (file path, line number, etc.)
        recoverable: Whether the error can be recovered from
        recovery_hint: Suggested fix for the user
    """

    message: str
    code: ErrorCode
    context: dict[str, Any] = field(default_factory=dict)
    recoverable: bool = True
    recovery_hint: str | None = None

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"

    def __post_init__(self) -> None:
        # Initialize Exception with the string representation
        super().__init__(str(self))

    def to_json(self) -> dict[str, Any]:
        """Structured logging format."""
        return {
            "error_code": self.code.value,
            "message": self.message,
            "context": self.context,
            "recoverable": self.recoverable,
            "recovery_hint": self.recovery_hint,
        }


# Domain-specific exceptions for fine-grained error handling
class ScanningError(ShannonError):
    """Errors during file scanning and parsing (SC1xx)."""

    pass


class SemanticError(ShannonError):
    """Errors during semantic analysis (SC2xx)."""

    pass


class GraphError(ShannonError):
    """Errors during graph construction and analysis (SC3xx)."""

    pass


class TemporalError(ShannonError):
    """Errors during temporal/git analysis (SC4xx)."""

    pass


class ArchitectureError(ShannonError):
    """Errors during architecture analysis (SC5xx)."""

    pass


class SignalError(ShannonError):
    """Errors during signal computation (SC6xx)."""

    pass


class FinderError(ShannonError):
    """Errors during finder execution (SC7xx)."""

    pass


class ValidationError(ShannonError):
    """Errors during phase validation (SC8xx)."""

    pass


class PersistenceError(ShannonError):
    """Errors during persistence operations (SC9xx)."""

    pass
