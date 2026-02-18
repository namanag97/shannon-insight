"""Fact data models for Phase 1 storage.

These models represent the complete parsed facts about source files.
They are stored in the FactDatabase and used by the graph builder.

Key difference from FileSyntax:
- FileSyntax is ephemeral (in-memory during parsing)
- Facts are persistent (stored in DB with session metadata)
- Facts include session tracking for audit trail
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..scanning.syntax import ClassDef, FileSyntax, FunctionDef, ImportDecl


@dataclass
class FunctionFact:
    """Complete facts about a function.

    Stored per-function with file context and class context.
    """

    # Identity
    name: str
    qualified_name: str  # "ClassName.method" or "function_name"
    file_path: str  # Back-reference to containing file

    # Location
    start_line: int
    end_line: int

    # Signature
    params: list[str]
    signature_tokens: int
    decorators: list[str]

    # Body
    body_tokens: int
    nesting_depth: int

    # Relationships (THE KEY DATA)
    call_targets: list[str]  # What this function calls

    # Class context (None if top-level)
    class_name: str | None

    # Computed
    is_stub: bool
    stub_score: float

    @classmethod
    def from_function_def(cls, fn: FunctionDef, file_path: str) -> FunctionFact:
        """Create FunctionFact from FunctionDef."""
        return cls(
            name=fn.name,
            qualified_name=fn.qualified_name,
            file_path=file_path,
            start_line=fn.start_line,
            end_line=fn.end_line,
            params=list(fn.params),
            signature_tokens=fn.signature_tokens,
            decorators=list(fn.decorators),
            body_tokens=fn.body_tokens,
            nesting_depth=fn.nesting_depth,
            call_targets=list(fn.call_targets) if fn.call_targets else [],
            class_name=fn.class_name,
            is_stub=fn.is_stub,
            stub_score=fn.stub_score,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "qualified_name": self.qualified_name,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "params": self.params,
            "signature_tokens": self.signature_tokens,
            "decorators": self.decorators,
            "body_tokens": self.body_tokens,
            "nesting_depth": self.nesting_depth,
            "call_targets": self.call_targets,
            "class_name": self.class_name,
            "is_stub": self.is_stub,
            "stub_score": self.stub_score,
        }


@dataclass
class ClassFact:
    """Complete facts about a class."""

    # Identity
    name: str
    file_path: str

    # Location
    start_line: int
    end_line: int

    # Relationships (THE KEY DATA)
    bases: list[str]  # Inheritance

    # Contents
    method_names: list[str]  # Method names (details in FunctionFact)
    field_names: list[str]

    # Computed
    is_abstract: bool
    method_count: int

    @classmethod
    def from_class_def(cls, cd: ClassDef, file_path: str) -> ClassFact:
        """Create ClassFact from ClassDef."""
        return cls(
            name=cd.name,
            file_path=file_path,
            start_line=cd.start_line,
            end_line=cd.end_line,
            bases=list(cd.bases),
            method_names=[m.name for m in cd.methods],
            field_names=list(cd.fields),
            is_abstract=cd.is_abstract,
            method_count=cd.method_count,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "bases": self.bases,
            "method_names": self.method_names,
            "field_names": self.field_names,
            "is_abstract": self.is_abstract,
            "method_count": self.method_count,
        }


@dataclass
class ImportFact:
    """Complete facts about an import."""

    # Identity
    file_path: str  # Which file has this import

    # Import details
    source: str  # "os.path" or "..models"
    names: list[str]  # ["join", "dirname"] from "from X import Y"

    # Resolution (THE KEY DATA - don't recompute!)
    resolved_path: str | None  # Target file in codebase
    is_relative: bool  # Starts with "."
    is_phantom: bool  # True if unresolved internal
    is_stdlib: bool  # True if stdlib/third-party

    @classmethod
    def from_import_decl(cls, imp: ImportDecl, file_path: str) -> ImportFact:
        """Create ImportFact from ImportDecl."""
        return cls(
            file_path=file_path,
            source=imp.source,
            names=list(imp.names),
            resolved_path=imp.resolved_path,
            is_relative=imp.is_relative,
            is_phantom=imp.is_phantom,
            is_stdlib=imp.is_stdlib,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "source": self.source,
            "names": self.names,
            "resolved_path": self.resolved_path,
            "is_relative": self.is_relative,
            "is_phantom": self.is_phantom,
            "is_stdlib": self.is_stdlib,
        }


@dataclass
class FileFact:
    """Complete parsed facts about a single file.

    This is the source of truth for Phase 1 data.
    Immutable once created for a given (path, commit_sha, mtime).
    """

    # Identity
    path: str  # Relative path
    absolute_path: str  # For debugging
    content_hash: str  # SHA-256 of content (for dedup)

    # Session metadata
    session_id: str  # Analysis session
    parsed_at: datetime  # When this was parsed
    parser_type: str  # "tree-sitter" or "regex"
    tool_version: str  # Shannon version

    # File metadata
    language: str
    lines: int
    tokens: int
    complexity: float
    has_main_guard: bool
    mtime: float

    # Entities (full details, not summaries)
    functions: list[FunctionFact]
    classes: list[ClassFact]
    imports: list[ImportFact]

    # Computed aggregates (for quick queries)
    function_count: int
    class_count: int
    import_count: int
    max_nesting: int
    stub_ratio: float
    impl_gini: float

    @classmethod
    def from_file_syntax(
        cls,
        fs: FileSyntax,
        session_id: str,
        tool_version: str,
        parser_type: str = "tree-sitter",
    ) -> FileFact:
        """Create FileFact from FileSyntax.

        Args:
            fs: The FileSyntax to convert
            session_id: Current analysis session ID
            tool_version: Shannon version string
            parser_type: "tree-sitter" or "regex"
        """
        # Convert all entities
        functions = [FunctionFact.from_function_def(fn, fs.path) for fn in fs.functions]

        # Also extract methods from classes as functions
        for cd in fs.classes:
            for method in cd.methods:
                functions.append(FunctionFact.from_function_def(method, fs.path))

        classes = [ClassFact.from_class_def(cd, fs.path) for cd in fs.classes]
        imports = [ImportFact.from_import_decl(imp, fs.path) for imp in fs.imports]

        return cls(
            path=fs.path,
            absolute_path=fs.absolute_path,
            content_hash=fs.content_hash,
            session_id=session_id,
            parsed_at=datetime.utcnow(),
            parser_type=parser_type,
            tool_version=tool_version,
            language=fs.language,
            lines=fs.lines,
            tokens=fs.tokens,
            complexity=fs.complexity,
            has_main_guard=fs.has_main_guard,
            mtime=fs.mtime,
            functions=functions,
            classes=classes,
            imports=imports,
            function_count=fs.function_count,
            class_count=fs.class_count,
            import_count=fs.import_count,
            max_nesting=fs.max_nesting,
            stub_ratio=fs.stub_ratio,
            impl_gini=fs.impl_gini,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "absolute_path": self.absolute_path,
            "content_hash": self.content_hash,
            "session_id": self.session_id,
            "parsed_at": self.parsed_at.isoformat(),
            "parser_type": self.parser_type,
            "tool_version": self.tool_version,
            "language": self.language,
            "lines": self.lines,
            "tokens": self.tokens,
            "complexity": self.complexity,
            "has_main_guard": self.has_main_guard,
            "mtime": self.mtime,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "imports": [i.to_dict() for i in self.imports],
            "function_count": self.function_count,
            "class_count": self.class_count,
            "import_count": self.import_count,
            "max_nesting": self.max_nesting,
            "stub_ratio": self.stub_ratio,
            "impl_gini": self.impl_gini,
        }


@dataclass
class AnalysisSession:
    """Tracks a single analysis run.

    Every fact is associated with a session for audit trail.
    """

    id: str  # UUID
    started_at: datetime
    completed_at: datetime | None
    commit_sha: str | None  # Git commit when analyzed
    analyzed_path: str  # Root path analyzed
    tool_version: str
    config_hash: str  # Hash of config for reproducibility
    status: str  # "running", "completed", "failed"
    file_count: int = 0
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "commit_sha": self.commit_sha,
            "analyzed_path": self.analyzed_path,
            "tool_version": self.tool_version,
            "config_hash": self.config_hash,
            "status": self.status,
            "file_count": self.file_count,
            "error_message": self.error_message,
        }
