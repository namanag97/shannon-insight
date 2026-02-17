"""FactStore — the unified store: entities + signals + relations + complex objects.

The FactStore is the single source of truth for all analysis data.
It combines four orthogonal data structures:

    - Entities:  a dict of EntityId -> Entity (files, modules, authors, etc.)
    - Signals:   a SignalStore (entity x signal -> value, with history)
    - Relations: a RelationGraph (typed edges between entities)
    - Objects:   typed slots for complex objects (graph, history, architecture)

Analyzers write signals, relations, and objects; finders read them.

When provenance tracking is enabled (via `enable_provenance=True`), each
`set_signal` call also records a `SignalProvenance` entry in the attached
`ProvenanceStore`. This is gated by the `--trace` CLI flag for performance.

Usage:
    from shannon_insight.infrastructure.store import FactStore
    from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType
    from shannon_insight.infrastructure.signals import Signal

    store = FactStore(root="/path/to/repo")

    # Register entities
    file_id = EntityId(EntityType.FILE, "src/main.py")
    store.add_entity(Entity(file_id))

    # Set signals
    store.set_signal(file_id, Signal.LINES, 150)

    # Query signals
    lines = store.get_signal(file_id, Signal.LINES)

    # Access complex objects
    graph = store.graph  # DependencyGraph
    history = store.git_history  # GitHistory

    # With provenance tracking:
    store = FactStore(root="/path/to/repo", enable_provenance=True)
    store.set_signal(file_id, Signal.LINES, 150, producer="scanning")
    explanation = store.explain_signal(file_id, Signal.LINES)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType
from shannon_insight.infrastructure.relations import Relation, RelationGraph, RelationType
from shannon_insight.infrastructure.signals import Signal, SignalStore

if TYPE_CHECKING:
    from shannon_insight.architecture.models import Architecture
    from shannon_insight.graph.models import CodebaseAnalysis, DependencyGraph, SpectralSummary
    from shannon_insight.scanning.syntax import FileSyntax
    from shannon_insight.session import AnalysisSession
    from shannon_insight.signals.models import SignalField
    from shannon_insight.temporal.models import ChurnSeries, CoChangeMatrix, GitHistory


class FactStore:
    """The unified store: entities + signals + relations + complex objects.

    Attributes:
        root:       Absolute path to the codebase root.
        timestamp:  When this store was created (snapshot identity).
        session:    Analysis session with config and tier.
        provenance: ProvenanceStore (only set when tracking is enabled).

    Complex Objects:
        file_syntax:   Dict[path, FileSyntax] from parsing
        structural:    CodebaseAnalysis with graph and metrics
        git_history:   GitHistory with commits
        churn:         Dict[path, ChurnSeries] with temporal signals
        cochange:      CoChangeMatrix with co-change patterns
        spectral:      SpectralSummary with eigenvalues
        architecture:  Architecture with modules and layers
        signal_field:  SignalField with all computed signals
    """

    def __init__(
        self,
        root: str,
        timestamp: datetime | None = None,
        enable_provenance: bool = False,
        provenance_session_id: str | None = None,
        provenance_retention_hours: int = 24,
        provenance_persist: bool = True,
        session: AnalysisSession | None = None,
    ) -> None:
        self.root = root
        self.timestamp = timestamp or datetime.now()
        self.session = session
        self._entities: dict[EntityId, Entity] = {}
        self._signals = SignalStore()
        self._relations = RelationGraph()

        # Complex object storage (replaces AnalysisStore slots)
        self._file_syntax: dict[str, FileSyntax] | None = None
        self._structural: CodebaseAnalysis | None = None
        self._git_history: GitHistory | None = None
        self._churn: dict[str, ChurnSeries] | None = None
        self._cochange: CoChangeMatrix | None = None
        self._spectral: SpectralSummary | None = None
        self._architecture: Architecture | None = None
        self._signal_field: SignalField | None = None
        self._clone_pairs: list | None = None
        self._author_distances: list | None = None

        # File content cache (for compression ratio, clone detection)
        self._content_cache: dict[str, str] = {}

        # Provenance tracking (optional, gated by --trace flag)
        self._provenance_enabled = enable_provenance
        self._provenance: Any = None  # Lazy import to avoid circular deps
        if enable_provenance:
            from shannon_insight.infrastructure.provenance import ProvenanceStore

            self._provenance = ProvenanceStore(
                session_id=provenance_session_id,
                retention_hours=provenance_retention_hours,
                persist=provenance_persist,
            )

    @property
    def provenance_enabled(self) -> bool:
        """Whether provenance tracking is active."""
        return self._provenance_enabled

    @property
    def provenance(self):
        """Access the ProvenanceStore. Returns None if tracking is disabled."""
        return self._provenance

    # -----------------------------------------------------------------
    # Complex object storage (replaces AnalysisStore slots)
    # -----------------------------------------------------------------

    @property
    def file_syntax(self) -> dict[str, FileSyntax] | None:
        """Parsed file syntax from tree-sitter/regex."""
        return self._file_syntax

    @file_syntax.setter
    def file_syntax(self, value: dict[str, FileSyntax]) -> None:
        self._file_syntax = value

    @property
    def structural(self) -> CodebaseAnalysis | None:
        """Structural analysis with graph and metrics."""
        return self._structural

    @structural.setter
    def structural(self, value: CodebaseAnalysis) -> None:
        self._structural = value

    @property
    def graph(self) -> DependencyGraph | None:
        """Shortcut to structural.graph."""
        return self._structural.graph if self._structural else None

    @property
    def git_history(self) -> GitHistory | None:
        """Git history with commits."""
        return self._git_history

    @git_history.setter
    def git_history(self, value: GitHistory) -> None:
        self._git_history = value

    @property
    def churn(self) -> dict[str, ChurnSeries] | None:
        """Per-file churn series."""
        return self._churn

    @churn.setter
    def churn(self, value: dict[str, ChurnSeries]) -> None:
        self._churn = value

    @property
    def cochange(self) -> CoChangeMatrix | None:
        """Co-change matrix."""
        return self._cochange

    @cochange.setter
    def cochange(self, value: CoChangeMatrix) -> None:
        self._cochange = value

    @property
    def spectral(self) -> SpectralSummary | None:
        """Spectral analysis summary."""
        return self._spectral

    @spectral.setter
    def spectral(self, value: SpectralSummary) -> None:
        self._spectral = value

    @property
    def architecture(self) -> Architecture | None:
        """Architecture with modules and layers."""
        return self._architecture

    @architecture.setter
    def architecture(self, value: Architecture) -> None:
        self._architecture = value

    @property
    def signal_field(self) -> SignalField | None:
        """Computed signal field with all signals."""
        return self._signal_field

    @signal_field.setter
    def signal_field(self, value: SignalField) -> None:
        self._signal_field = value

    @property
    def clone_pairs(self) -> list | None:
        """Detected clone pairs."""
        return self._clone_pairs

    @clone_pairs.setter
    def clone_pairs(self, value: list) -> None:
        self._clone_pairs = value

    @property
    def author_distances(self) -> list | None:
        """Author distance pairs."""
        return self._author_distances

    @author_distances.setter
    def author_distances(self, value: list) -> None:
        self._author_distances = value

    @property
    def file_paths(self) -> list[str]:
        """List of all file paths."""
        return list(self._file_syntax.keys()) if self._file_syntax else []

    @property
    def file_count(self) -> int:
        """Number of files."""
        return len(self._file_syntax) if self._file_syntax else 0

    def get_content(self, rel_path: str) -> str | None:
        """Get file content from cache or read from disk."""
        if rel_path in self._content_cache:
            return self._content_cache[rel_path]
        from pathlib import Path

        full_path = Path(self.root) / rel_path if self.root else Path(rel_path)
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            self._content_cache[rel_path] = content
            return content
        except OSError:
            return None

    def clear_content_cache(self) -> None:
        """Clear content cache to free memory."""
        self._content_cache.clear()

    @property
    def available(self) -> set[str]:
        """Set of available data sources."""
        avail: set[str] = set()
        if self._file_syntax:
            avail.add("file_syntax")
            avail.add("files")
        if self._structural:
            avail.add("structural")
        if self._git_history:
            avail.add("git_history")
        if self._churn:
            avail.add("churn")
        if self._cochange:
            avail.add("cochange")
        if self._spectral:
            avail.add("spectral")
        if self._architecture:
            avail.add("architecture")
        if self._signal_field:
            avail.add("signal_field")
        if self._clone_pairs is not None:
            avail.add("clone_pairs")
        if self._author_distances is not None:
            avail.add("author_distances")
        return avail

    def get_role(self, path: str) -> str | None:
        """Get file role from signal."""
        file_id = EntityId(EntityType.FILE, path)
        return self.get_signal(file_id, Signal.ROLE)

    # -----------------------------------------------------------------
    # Entity operations
    # -----------------------------------------------------------------

    def add_entity(self, entity: Entity) -> None:
        """Register an entity in the store."""
        self._entities[entity.id] = entity

    def get_entity(self, id: EntityId) -> Entity | None:
        """Look up an entity by its EntityId. Returns None if not found."""
        return self._entities.get(id)

    def entities(self) -> list[Entity]:
        """All entities in the store."""
        return list(self._entities.values())

    def files(self) -> list[EntityId]:
        """All FILE entity IDs."""
        return [eid for eid in self._entities if eid.type == EntityType.FILE]

    def modules(self) -> list[EntityId]:
        """All MODULE entity IDs."""
        return [eid for eid in self._entities if eid.type == EntityType.MODULE]

    # -----------------------------------------------------------------
    # Signal operations (delegate to SignalStore)
    # -----------------------------------------------------------------

    def set_signal(
        self,
        entity: EntityId,
        signal: Signal,
        value: Any,
        producer: str | None = None,
        inputs: list[str] | None = None,
        formula: str | None = None,
    ) -> None:
        """Set a signal value for an entity.

        When provenance tracking is enabled, also records provenance metadata.
        The producer, inputs, and formula parameters are only used when
        provenance is active; they are ignored otherwise for zero overhead.

        Args:
            entity: EntityId for the entity.
            signal: Signal enum member to set.
            value: The signal value.
            producer: Name of the producing analyzer (for provenance).
            inputs: Signal names used to compute this value (for provenance).
            formula: Human-readable formula (for provenance).
        """
        self._signals.set(entity, signal, value)

        # Record provenance if tracking is enabled
        if self._provenance_enabled and self._provenance is not None:
            self._provenance.record(
                entity_path=entity.key,
                signal=signal,
                value=value,
                producer=producer or "unknown",
                inputs=inputs,
                formula=formula,
            )

    def get_signal(self, entity: EntityId, signal: Signal, default: Any = None) -> Any:
        """Get the latest signal value for an entity."""
        return self._signals.get(entity, signal, default)

    def has_signal(self, entity: EntityId, signal: Signal) -> bool:
        """Check if a signal has been set for an entity."""
        return self._signals.has(entity, signal)

    def write_signals(
        self,
        entity: EntityId,
        signals: dict[Signal, Any],
        producer: str,
    ) -> None:
        """Write multiple signals for an entity at once.

        Convenience method for analyzers that compute many signals per entity.
        Equivalent to calling set_signal() for each signal.

        Args:
            entity: EntityId for the entity.
            signals: Dict mapping Signal enum to value.
            producer: Name of the producing analyzer.
        """
        for signal, value in signals.items():
            self.set_signal(entity, signal, value, producer=producer)

    # -----------------------------------------------------------------
    # Relation operations (delegate to RelationGraph)
    # -----------------------------------------------------------------

    def add_relation(self, relation: Relation) -> None:
        """Add a relation to the graph."""
        self._relations.add(relation)

    def has_relation(self, source: EntityId, type: RelationType, target: EntityId) -> bool:
        """Check if a specific relation exists."""
        return self._relations.has(source, type, target)

    def outgoing(self, entity: EntityId, type: RelationType | None = None) -> list[Relation]:
        """Get outgoing relations from an entity."""
        return self._relations.outgoing(entity, type)

    def incoming(self, entity: EntityId, type: RelationType | None = None) -> list[Relation]:
        """Get incoming relations to an entity."""
        return self._relations.incoming(entity, type)

    # -----------------------------------------------------------------
    # Provenance operations (delegate to ProvenanceStore)
    # -----------------------------------------------------------------

    def explain_signal(self, entity: EntityId, signal: Signal) -> str:
        """Get human-readable explanation of how a signal was computed.

        Requires provenance tracking to be enabled. Returns a helpful
        message if tracking is disabled.

        Args:
            entity: EntityId for the entity.
            signal: Signal enum member to explain.

        Returns:
            Multi-line explanation string.
        """
        if not self._provenance_enabled or self._provenance is None:
            return (
                f"Provenance tracking is not enabled. "
                f"Re-run with --trace to see computation details for {signal.value}."
            )
        return self._provenance.explain(entity.key, signal)

    def trace_signal(self, entity: EntityId, signal: Signal) -> list:
        """Get the full dependency tree for a signal computation.

        Requires provenance tracking to be enabled. Returns an empty
        list if tracking is disabled.

        Args:
            entity: EntityId for the entity.
            signal: Signal enum member to trace.

        Returns:
            List of SignalProvenance records forming the dependency tree.
        """
        if not self._provenance_enabled or self._provenance is None:
            return []
        return self._provenance.trace(entity.key, signal)

    def get_computation_tree(self, entity: EntityId, signal: Signal) -> dict:
        """Get the full dependency tree for a signal as a nested dict.

        Requires provenance tracking to be enabled. Returns an empty
        dict if tracking is disabled.

        Args:
            entity: EntityId for the entity.
            signal: Signal enum member to trace.

        Returns:
            Nested dict with signal, value, producer, phase, formula,
            inputs, and children keys. Empty dict if not available.
        """
        if not self._provenance_enabled or self._provenance is None:
            return {}
        return self._provenance.get_computation_tree(entity.key, signal)
