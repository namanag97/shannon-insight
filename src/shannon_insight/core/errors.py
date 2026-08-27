"""Error taxonomy.

Every error carries a stable machine code so callers (CI gates, server) can
branch on semantics instead of string matching. Codes are grouped:

    SC0xx  registry / contract violations
    SC1xx  syntax context (parsing, grammars)
    SC2xx  facts context (discovery, identity, authors)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ErrorCode(Enum):
    # Registry / contracts (SC0xx)
    REGISTRY_DUPLICATE_SIGNAL = "SC001"
    CONTRACT_UNSATISFIED_REQUIREMENT = "SC002"
    CONTRACT_SINGLE_WRITER_VIOLATION = "SC003"

    # Syntax (SC1xx)
    SYNTAX_GRAMMAR_MISSING = "SC101"
    SYNTAX_PARSE_FAILED = "SC102"
    SYNTAX_UNSUPPORTED_LANGUAGE = "SC103"

    # Facts (SC2xx)
    FACTS_ROOT_NOT_FOUND = "SC201"
    FACTS_BLOB_CORRUPT = "SC202"
    FACTS_IDENTITY_ORDER_VIOLATION = "SC203"
    FACTS_REPO_TOO_LARGE = "SC204"
    FACTS_GIT_TIMEOUT = "SC205"


@dataclass(frozen=True)
class ShannonError(Exception):
    """Base error for all Shannon failures."""

    message: str
    code: ErrorCode
    recoverable: bool = False
    recovery_hint: str | None = None
    context: dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        base = f"[{self.code.value}] {self.message}"
        if self.recovery_hint:
            base += f" (hint: {self.recovery_hint})"
        return base


def grammar_missing(language: str) -> ShannonError:
    return ShannonError(
        message=f"tree-sitter grammar for '{language}' is not installed",
        code=ErrorCode.SYNTAX_GRAMMAR_MISSING,
        recoverable=True,
        recovery_hint=f"pip install tree-sitter-{language}",
        context={"language": language},
    )
