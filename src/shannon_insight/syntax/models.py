"""IR1 syntax models.

Pure functions of file content, keyed by content_hash. Every value derives
from the parse tree; nothing here knows about git or downstream signals.

Token convention: a "token" is a leaf node (named or anonymous) of the parse
tree. body_tokens counts leaves inside the function body; signature_tokens =
function leaves minus body leaves. Uniform across languages, stable under
pretty-printing.

Information-transfer rule: anything Phase B+ might need that is recoverable
from the tree for free is captured HERE, once — aliases, exports, packages,
visibility, docstrings, comment mass. Downstream contexts never re-parse.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SYNTAX_PARSER_VERSION = "4.1.0"


@dataclass(frozen=True)
class FunctionDef:
    name: str
    params: tuple[str, ...]
    start_line: int
    end_line: int
    body_tokens: int
    signature_tokens: int
    nesting_depth: int
    cyclomatic: int
    qualified_name: str = ""
    calls: tuple[str, ...] = ()
    decorators: tuple[str, ...] = ()
    is_method: bool = False
    class_name: str | None = None
    exported: bool = False
    visibility: str = "internal"
    is_async: bool = False
    has_docstring: bool = False
    is_hard_stub: bool = False
    return_type_raw: str | None = None

    @property
    def stub_score(self) -> float:
        """1.0 = pure declaration, 0.0 = substantial implementation."""
        if self.is_hard_stub or self.body_tokens == 0:
            return 1.0
        sig = max(self.signature_tokens, 1)
        ratio = self.body_tokens / (sig * 3)
        return round(max(0.0, 1.0 - min(1.0, ratio)), 4)

    @property
    def token_span(self) -> int:
        return max(1, self.end_line - self.start_line + 1)


@dataclass(frozen=True)
class ClassDef:
    name: str
    start_line: int
    end_line: int
    bases: tuple[str, ...] = ()
    method_names: tuple[str, ...] = ()
    field_names: tuple[str, ...] = ()
    is_abstract: bool = False
    is_interface: bool = False
    decorators: tuple[str, ...] = ()
    exported: bool = False

    @property
    def qualified_name(self) -> str:
        return self.name


@dataclass(frozen=True)
class ImportDecl:
    """A single import/use/require/include site.

    ``module`` is the raw target (dotted path, URL-ish specifier, include
    path). ``names`` lists bound symbols for from-style imports. ``alias`` is
    the local binding for statement-level renames (``import numpy as np`` ->
    alias="np"; ``import React from "react"`` -> alias="React").
    """

    module: str
    names: tuple[str, ...] = ()
    alias: str | None = None
    level: int = 0
    line: int = 0
    is_dynamic: bool = False
    is_system: bool = False

    @property
    def is_relative(self) -> bool:
        if self.level > 0:
            return True
        return self.module.startswith(("./", "../"))

    @property
    def local_binding(self) -> str | None:
        if self.alias:
            return self.alias
        if self.names:
            return self.names[-1]
        return self.module.rsplit(".", 1)[-1] if self.module else None


@dataclass(frozen=True)
class ExportDecl:
    name: str
    kind: str
    line: int


@dataclass(frozen=True)
class FileSyntax:
    path: str
    language: str
    content_hash: str
    lines: int
    functions: tuple[FunctionDef, ...] = ()
    classes: tuple[ClassDef, ...] = ()
    imports: tuple[ImportDecl, ...] = ()
    exports: tuple[ExportDecl, ...] = ()
    top_level_names: tuple[str, ...] = ()
    package: str | None = None
    has_errors: bool = False
    has_main_guard: bool = False
    parse_mode: str = "tree-sitter"
    parser_version: str = SYNTAX_PARSER_VERSION

    stub_ratio: float = field(default=0.0)
    impl_gini: float = field(default=0.0)
    cyclomatic: int = field(default=1)
    total_tokens: int = field(default=0)
    comment_tokens: int = field(default=0)
    identifiers: frozenset[str] = field(default=frozenset())
    comments: tuple[str, ...] = ()
    encoding: str = "utf-8"
    is_generated: bool = False
    occurrences: tuple[tuple[str, int], ...] = ()  # (name, 1-based line), definition+reference

    def name_uses(self, name: str) -> int:
        """Reference/usage count for a bound name — Phase-B binding fuel."""
        return sum(1 for n, _ in self.occurrences if n == name)

    @property
    def function_count(self) -> int:
        return len(self.functions)

    @property
    def class_count(self) -> int:
        return len(self.classes)

    @property
    def import_count(self) -> int:
        return len(self.imports)

    @property
    def max_nesting(self) -> int:
        return max((f.nesting_depth for f in self.functions), default=0)

    @property
    def exported_names(self) -> frozenset[str]:
        return frozenset(e.name for e in self.exports)


def compute_stub_ratio(functions: tuple[FunctionDef, ...]) -> float:
    if not functions:
        return 0.0
    return round(sum(f.stub_score for f in functions) / len(functions), 4)


def compute_impl_gini(functions: tuple[FunctionDef, ...]) -> float:
    sizes = sorted(f.body_tokens for f in functions)
    n = len(sizes)
    total = sum(sizes)
    if n < 2 or total == 0:
        return 0.0
    weighted = sum((2 * i - n - 1) * s for i, s in enumerate(sizes, start=1))
    return round(weighted / (n * total), 4)
