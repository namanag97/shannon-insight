"""AnalysisStore v2 — typed Slot[T] blackboard pattern.

The Slot[T] wrapper provides:
    - Type safety: Generic type parameter for compile-time checking
    - Availability tracking: .available property replaces scattered None checks
    - Error context: .error property captures WHY something is missing
    - Provenance: .produced_by tracks which analyzer populated the slot

Slots prevent FM-12 (Slot not populated) crashes by requiring explicit checks.

The AnalysisStore now bridges to FactStore (v2 infrastructure), enabling
incremental migration. The fact_store property exposes the underlying
FactStore, and _sync_entities() pushes file_metrics into it as entities
with basic signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType
from shannon_insight.infrastructure.signals import Signal
from shannon_insight.infrastructure.store import FactStore

if TYPE_CHECKING:
    from shannon_insight.signals.models import SignalField

T = TypeVar("T")


@dataclass
class Slot(Generic[T]):
    """A typed blackboard slot. Wraps Optional with provenance and error context.

    Usage:
        # Check before access (REQUIRED)
        if store.structural.available:
            graph = store.structural.value  # Safe
        else:
            return []  # Graceful degradation

        # Or use get() with default
        graph = store.structural.get(default=empty_graph)

    Never access .value without checking .available first!
    """

    _value: T | None = None
    _error: str | None = None
    _produced_by: str = ""

    @property
    def available(self) -> bool:
        """True if value has been set."""
        return self._value is not None

    @property
    def value(self) -> T:
        """Get the value. Raises LookupError if not populated.

        ALWAYS check .available before accessing .value!
        """
        if self._value is None:
            if self._error:
                raise LookupError(
                    f"Slot not populated (produced_by={self._produced_by}): {self._error}"
                )
            raise LookupError("Slot not populated. Check .available before accessing .value")
        return self._value

    def get(self, default: T | None = None) -> T | None:
        """Get value or default if not available."""
        return self._value if self._value is not None else default

    def set(self, value: T, produced_by: str) -> None:
        """Set the slot value with provenance."""
        self._value = value
        self._produced_by = produced_by
        self._error = None

    def set_error(self, error: str, produced_by: str) -> None:
        """Mark slot as failed with error message."""
        self._error = error
        self._produced_by = produced_by
        self._value = None

    @property
    def produced_by(self) -> str:
        """Who populated this slot."""
        return self._produced_by

    @property
    def error(self) -> str | None:
        """Error message if set_error was called."""
        return self._error


@dataclass
class AnalysisStore:
    """The blackboard that all analyzers write to and finders read from.

    All optional data is wrapped in Slot[T] for type safety and error context.
    Finders MUST check .available before accessing .value.

    Slots (from v2 spec):
        - file_syntax: Dict[path, FileSyntax] from tree-sitter/regex parsing
        - structural: CodebaseAnalysis with graph, PageRank, SCC, Louvain
        - git_history: GitHistory with commits and file changes
        - churn: Dict[path, ChurnSeries] with per-file churn stats
        - cochange: CoChangeMatrix with file co-change patterns
        - semantics: Dict[path, FileSemantics] with concepts and coherence
        - roles: Dict[path, str] with file role classifications
        - spectral: SpectralSummary with Fiedler value and spectral gap
        - clone_pairs: List[ClonePair] with detected clones
        - author_distances: List[AuthorDistance] with author overlap metrics
        - architecture: Architecture with modules, layers, Martin metrics
        - signal_field: SignalField with all computed signals per file/module
    """

    # Always-available inputs (set by kernel before analyzers run)
    root_dir: str = ""
    file_metrics: list[Any] = field(default_factory=list)

    # File content cache (populated during syntax extraction to avoid re-reads)
    # Maps relative path -> file content. Cleared after graph analysis completes.
    _content_cache: dict[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Initialize the underlying FactStore for v2 bridge."""
        self._fact_store = FactStore(root=self.root_dir)

    @property
    def fact_store(self) -> FactStore:
        """Expose the underlying FactStore for v2 consumers."""
        return self._fact_store

    def _sync_entities(self) -> None:
        """Sync file_metrics to FactStore entities.

        Creates a FILE entity for each FileMetrics and sets the basic
        scanning signals (LINES, FUNCTION_COUNT, CLASS_COUNT, IMPORT_COUNT).

        This bridge enables v2 analyzers/finders to read from FactStore
        while v1 code continues using the slot-based AnalysisStore.

        Uses the actual FileMetrics field names:
            - fm.functions  (not function_count)
            - fm.structs    (not class_count)
            - fm.imports    (list, len() for count)
        """
        for fm in self.file_metrics:
            entity_id = EntityId(EntityType.FILE, fm.path)
            entity = Entity(id=entity_id, metadata={})
            self._fact_store.add_entity(entity)
            # Set basic signals using actual FileMetrics field names
            self._fact_store.set_signal(entity_id, Signal.LINES, fm.lines)
            self._fact_store.set_signal(entity_id, Signal.FUNCTION_COUNT, fm.functions)
            self._fact_store.set_signal(entity_id, Signal.CLASS_COUNT, fm.structs)
            self._fact_store.set_signal(entity_id, Signal.IMPORT_COUNT, len(fm.imports))

    def get_content(self, rel_path: str) -> str | None:
        """Get file content from cache or read from disk (caches result)."""
        if rel_path in self._content_cache:
            return self._content_cache[rel_path]
        # Fallback to disk read (shouldn't happen if cache is populated correctly)
        from pathlib import Path

        full_path = Path(self.root_dir) / rel_path if self.root_dir else Path(rel_path)
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            self._content_cache[rel_path] = content
            return content
        except OSError:
            return None

    def clear_content_cache(self) -> None:
        """Clear content cache to free memory after graph analysis."""
        self._content_cache.clear()

    # Typed slots — each knows if it's populated, why not, and who wrote it
    file_syntax: Slot[dict[str, Any]] = field(default_factory=Slot)
    structural: Slot[Any] = field(default_factory=Slot)
    git_history: Slot[Any] = field(default_factory=Slot)
    churn: Slot[dict[str, Any]] = field(default_factory=Slot)
    cochange: Slot[Any] = field(default_factory=Slot)
    semantics: Slot[dict[str, Any]] = field(default_factory=Slot)
    roles: Slot[dict[str, str]] = field(default_factory=Slot)
    spectral: Slot[Any] = field(default_factory=Slot)
    clone_pairs: Slot[list[Any]] = field(default_factory=Slot)
    author_distances: Slot[list[Any]] = field(default_factory=Slot)
    architecture: Slot[Any] = field(default_factory=Slot)
    signal_field: Slot[SignalField] = field(default_factory=Slot)

    @property
    def available(self) -> set[str]:
        """Track what signal categories have been populated.

        Returns set of slot names that have data. 'files' is always present
        (represents file_metrics which is never wrapped in Slot).
        """
        avail: set[str] = {"files"}
        for name in self._slot_names():
            slot = getattr(self, name)
            if isinstance(slot, Slot) and slot.available:
                avail.add(name)
        return avail

    @staticmethod
    def _slot_names() -> list[str]:
        """Return all slot names in order."""
        return [
            "file_syntax",
            "structural",
            "git_history",
            "churn",
            "cochange",
            "semantics",
            "roles",
            "spectral",
            "clone_pairs",
            "author_distances",
            "architecture",
            "signal_field",
        ]

    def slot_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all slots for debugging.

        Returns dict mapping slot name to:
            - available: bool
            - produced_by: str (if available or errored)
            - error: str (if error)
        """
        status = {}
        for name in self._slot_names():
            slot = getattr(self, name)
            if isinstance(slot, Slot):
                info: dict[str, Any] = {"available": slot.available}
                if slot.produced_by:
                    info["produced_by"] = slot.produced_by
                if slot.error:
                    info["error"] = slot.error
                status[name] = info
        return status
