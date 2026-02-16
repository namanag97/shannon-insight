"""Relation model for Shannon Insight v2.

Relations are typed edges between entities. There are 8 relation types:

    IMPORTS         File -> File          (static dependency)
    COCHANGES_WITH  File -> File          (symmetric, weighted by lift)
    SIMILAR_TO      File -> File          (symmetric, weighted by cosine)
    AUTHORED_BY     File -> Author        (authorship)
    IN_MODULE       File -> Module        (membership)
    CONTAINS        Module -> File        (containment, inverse of IN_MODULE)
    DEPENDS_ON      Module -> Module      (aggregated from IMPORTS)
    CLONED_FROM     File -> File          (symmetric, weighted by similarity)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from shannon_insight.infrastructure.entities import EntityId


class RelationType(Enum):
    """All 8 relation types."""

    IMPORTS = "imports"               # File -> File
    COCHANGES_WITH = "cochanges"      # File -> File (symmetric, weighted)
    SIMILAR_TO = "similar"            # File -> File (weighted)
    AUTHORED_BY = "authored"          # File -> Author
    IN_MODULE = "in_module"           # File -> Module
    CONTAINS = "contains"             # Module -> File, Codebase -> Module
    DEPENDS_ON = "depends"            # Module -> Module
    CLONED_FROM = "cloned"            # File -> File (weighted)


@dataclass
class Relation:
    """A typed, weighted edge between two entities.

    Attributes:
        type:     One of the 8 RelationType values.
        source:   The entity this relation originates from.
        target:   The entity this relation points to.
        weight:   Edge weight (default 1.0). Meaning depends on type:
                  - IMPORTS: 1.0 (exists or not)
                  - COCHANGES_WITH: lift score
                  - SIMILAR_TO: cosine similarity [0, 1]
                  - AUTHORED_BY: 1.0
                  - IN_MODULE: 1.0
                  - CONTAINS: 1.0
                  - DEPENDS_ON: edge count
                  - CLONED_FROM: 1 - NCD similarity [0, 1]
        metadata: Free-form dictionary for extra attributes.
    """

    type: RelationType
    source: EntityId
    target: EntityId
    weight: float = 1.0
    metadata: dict = field(default_factory=dict)


class RelationGraph:
    """Queryable collection of all relations.

    Maintains three indexes for efficient lookup:
        - by type: all relations of a given RelationType
        - by source: all outgoing relations from an entity
        - by target: all incoming relations to an entity
    """

    def __init__(self) -> None:
        self._edges: list[Relation] = []
        self._by_type: dict[RelationType, list[Relation]] = {}
        self._by_source: dict[EntityId, list[Relation]] = {}
        self._by_target: dict[EntityId, list[Relation]] = {}

    def add(self, relation: Relation) -> None:
        """Add a relation to the graph."""
        self._edges.append(relation)
        self._by_type.setdefault(relation.type, []).append(relation)
        self._by_source.setdefault(relation.source, []).append(relation)
        self._by_target.setdefault(relation.target, []).append(relation)

    def by_type(self, type: RelationType) -> list[Relation]:
        """Get all relations of a given type."""
        return self._by_type.get(type, [])

    def outgoing(
        self,
        entity: EntityId,
        type: Optional[RelationType] = None,
    ) -> list[Relation]:
        """Get outgoing relations from an entity.

        Args:
            entity: The source entity to query.
            type:   Optional filter by relation type.

        Returns:
            List of relations where entity is the source.
        """
        rels = self._by_source.get(entity, [])
        if type is not None:
            rels = [r for r in rels if r.type == type]
        return rels

    def incoming(
        self,
        entity: EntityId,
        type: Optional[RelationType] = None,
    ) -> list[Relation]:
        """Get incoming relations to an entity.

        Args:
            entity: The target entity to query.
            type:   Optional filter by relation type.

        Returns:
            List of relations where entity is the target.
        """
        rels = self._by_target.get(entity, [])
        if type is not None:
            rels = [r for r in rels if r.type == type]
        return rels

    def has(
        self,
        source: EntityId,
        type: RelationType,
        target: EntityId,
    ) -> bool:
        """Check if a specific relation exists."""
        for r in self.outgoing(source, type):
            if r.target == target:
                return True
        return False

    def weight(
        self,
        source: EntityId,
        type: RelationType,
        target: EntityId,
    ) -> float:
        """Get the weight of a specific relation.

        Returns 0.0 if the relation does not exist.
        """
        for r in self.outgoing(source, type):
            if r.target == target:
                return r.weight
        return 0.0
