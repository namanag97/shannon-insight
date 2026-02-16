"""Syntax models for parsed source files.

FileSyntax provides structured AST data for each file:
    - Per-function: body_tokens, nesting_depth, call_targets, decorators
    - Per-class: bases, methods, fields, is_abstract
    - Per-import: source, names, resolved_path

Both tree-sitter and regex fallback produce FileSyntax.
Consumers check `fn.call_targets is not None` to detect tree-sitter parsing.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FunctionDef:
    """A function or method definition.

    Attributes:
        name: Function name
        params: Parameter names
        body_tokens: Token count in function body (for impl_gini, stub detection)
        signature_tokens: Token count in signature (for stub_score formula)
        nesting_depth: Max nesting depth within this function
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        call_targets: Syntactic call targets (None if regex-parsed)
        decorators: Decorator names (e.g., ["property", "abstractmethod"])
    """

    name: str
    params: list[str]
    body_tokens: int
    signature_tokens: int
    nesting_depth: int
    start_line: int
    end_line: int
    call_targets: list[str] | None = None
    decorators: list[str] = field(default_factory=list)

    @property
    def is_stub(self) -> bool:
        """True if function body is too small to be meaningful.

        Hard threshold: body_tokens < 3 is definitely a stub.
        Single return statements, property getters are NOT stubs.
        """
        # Empty or trivial (just pass/...)
        return self.body_tokens < 3

    @property
    def stub_score(self) -> float:
        """Stub score: how "stub-like" is this function?

        Range [0, 1]:
            0 = fully implemented
            1 = pure stub (empty body)

        Logic:
        - Empty body (< 3 tokens): 1.0 (pure stub)
        - Property/one-liner (< 10 tokens): 0.0 (valid implementation)
        - Otherwise: scale based on body/signature ratio
        """
        # Empty or trivial body is a pure stub
        if self.body_tokens < 3:
            return 1.0

        # Small but non-trivial body (property getters, one-liners) are NOT stubs
        # These are valid implementations, just concise
        if self.body_tokens < 10:
            return 0.0

        # For larger functions, use ratio-based scoring
        # Require body >= signature (not 3x) for full implementation
        if self.signature_tokens <= 0:
            return 0.0
        ratio = self.body_tokens / self.signature_tokens
        # body >= signature -> 0.0, body < signature/2 -> approaching 1.0
        return max(0.0, min(1.0, 1 - ratio))


@dataclass
class ClassDef:
    """A class definition.

    Attributes:
        name: Class name
        bases: Base class names
        methods: Methods defined in this class
        fields: Field/attribute names
        is_abstract: True if ABC, Protocol, or has abstractmethod
    """

    name: str
    bases: list[str]
    methods: list[FunctionDef]
    fields: list[str]
    is_abstract: bool = False


@dataclass
class ImportDecl:
    """An import declaration.

    Attributes:
        source: Module being imported (e.g., "os.path")
        names: Names imported (e.g., ["join", "dirname"])
        resolved_path: Resolved file path (None = phantom/external)
    """

    source: str
    names: list[str]
    resolved_path: str | None = None

    @property
    def is_phantom(self) -> bool:
        """True if import cannot be resolved to a file."""
        return self.resolved_path is None


@dataclass
class FileSyntax:
    """Complete syntax extraction for a file.

    Produced by tree-sitter parser or regex fallback.
    Consumers check `fn.call_targets is not None` to detect tree-sitter parsing.

    Attributes:
        path: File path (relative to codebase root)
        functions: Top-level and nested function definitions
        classes: Class definitions
        imports: Import declarations
        language: Detected language
        has_main_guard: True if `if __name__ == "__main__":` detected
        mtime: Last modified timestamp (for cache invalidation)
        _lines: Cached line count (set during parsing)
        _tokens: Cached token count (set during parsing)
        _complexity: Cached complexity score (set during parsing)
    """

    path: str
    functions: list[FunctionDef]
    classes: list[ClassDef]
    imports: list[ImportDecl]
    language: str
    has_main_guard: bool = False
    mtime: float = 0.0
    # Cached metrics (set during parsing to avoid re-reading content)
    _lines: int = 0
    _tokens: int = 0
    _complexity: float = 1.0

    @property
    def function_count(self) -> int:
        """Number of functions in this file."""
        return len(self.functions)

    @property
    def class_count(self) -> int:
        """Number of classes in this file."""
        return len(self.classes)

    @property
    def import_count(self) -> int:
        """Number of import declarations in this file."""
        return len(self.imports)

    @property
    def max_nesting(self) -> int:
        """Maximum nesting depth across all functions."""
        if not self.functions:
            return 0
        return max(fn.nesting_depth for fn in self.functions)

    @property
    def stub_ratio(self) -> float:
        """Mean stub_score across functions.

        Range [0, 1]:
            0 = all functions fully implemented
            1 = all functions are stubs
        """
        if not self.functions:
            return 0.0
        return sum(fn.stub_score for fn in self.functions) / len(self.functions)

    @property
    def impl_gini(self) -> float:
        """Gini coefficient of body_token distribution.

        Measures implementation inequality:
            0 = all functions same size
            1 = maximum inequality
        """
        if len(self.functions) <= 1:
            return 0.0

        values = sorted(fn.body_tokens for fn in self.functions)
        n = len(values)
        total = sum(values)

        if total == 0:
            return 0.0

        # Gini formula: G = (2 * sum(i * x_i)) / (n * sum(x_i)) - (n + 1) / n
        # where i is 1-indexed
        numerator = sum((i + 1) * v for i, v in enumerate(values))
        return (2 * numerator) / (n * total) - (n + 1) / n

    # ── Metrics properties (for FileMetrics compatibility) ──────────────

    @property
    def lines(self) -> int:
        """Line count (cached during parsing)."""
        return self._lines

    @property
    def tokens(self) -> int:
        """Token count (cached during parsing)."""
        return self._tokens

    @property
    def complexity(self) -> float:
        """Cyclomatic complexity estimate (cached during parsing)."""
        return self._complexity

    @property
    def import_sources(self) -> list[str]:
        """List of import source strings (for dependency graph building)."""
        return [imp.source for imp in self.imports]

    @property
    def function_sizes(self) -> list[int]:
        """List of function sizes in lines (end_line - start_line + 1)."""
        return [max(1, fn.end_line - fn.start_line + 1) for fn in self.functions]

    @property
    def total_tokens(self) -> int:
        """Sum of all function body tokens."""
        return sum(fn.body_tokens for fn in self.functions)
