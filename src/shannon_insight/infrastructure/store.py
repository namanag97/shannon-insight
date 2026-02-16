"""FactStore — the unified store: entities + signals + relations.

The FactStore is the v2 replacement for AnalysisStore (blackboard pattern).
Instead of typed slots, it uses three orthogonal data structures:

    - Entities:  a dict of EntityId -> Entity (files, modules, authors, etc.)
    - Signals:   a SignalStore (entity x signal -> value, with history)
    - Relations:  a RelationGraph (typed edges between entities)

Analyzers write signals and relations; finders read them.

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
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from shannon_insight.infrastructure.entities import Entity, EntityId, EntityType
from shannon_insight.infrastructure.relations import Relation, RelationGraph, RelationType
from shannon_insight.infrastructure.signals import Signal, SignalStore


class FactStore:
    """The unified store: entities + signals + relations.

    Attributes:
        root:       Absolute path to the codebase root.
        timestamp:  When this store was created (snapshot identity).
    """

    def __init__(self, root: str, timestamp: Optional[datetime] = None) -> None:
        self.root = root
        self.timestamp = timestamp or datetime.now()
        self._entities: dict[EntityId, Entity] = {}
        self._signals = SignalStore()
        self._relations = RelationGraph()

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

    def set_signal(self, entity: EntityId, signal: Signal, value: Any) -> None:
        """Set a signal value for an entity."""
        self._signals.set(entity, signal, value)

    def get_signal(self, entity: EntityId, signal: Signal, default: Any = None) -> Any:
        """Get the latest signal value for an entity."""
        return self._signals.get(entity, signal, default)

    def has_signal(self, entity: EntityId, signal: Signal) -> bool:
        """Check if a signal has been set for an entity."""
        return self._signals.has(entity, signal)

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
