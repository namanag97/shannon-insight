"""Entity model for Shannon Insight v2.

Entities are the things we analyze. They form a hierarchy:

    Codebase (root)
        ├── Module
        │       └── File
        │               └── Symbol (future)
        ├── Author
        └── Commit

Each entity has a unique EntityId (type + key) and an optional parent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EntityType(Enum):
    """The six kinds of entity in the codebase model."""

    CODEBASE = "codebase"
    MODULE = "module"
    FILE = "file"
    SYMBOL = "symbol"
    AUTHOR = "author"
    COMMIT = "commit"


@dataclass(frozen=True)
class EntityId:
    """Unique identifier for any entity.

    Key conventions:
        CODEBASE  - absolute path        e.g. /Users/dev/myproject
        MODULE    - module name           e.g. auth, graph, tests
        FILE      - relative path         e.g. src/auth/login.py
        SYMBOL    - file:line:name        e.g. src/auth/login.py:45:authenticate
        AUTHOR    - email                 e.g. alice@example.com
        COMMIT    - short SHA             e.g. abc1234
    """

    type: EntityType
    key: str

    def __hash__(self) -> int:
        return hash((self.type, self.key))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityId):
            return False
        return self.type == other.type and self.key == other.key


@dataclass
class Entity:
    """A concrete entity in the codebase model.

    Every entity has:
        - id:       unique EntityId (type + key)
        - parent:   optional parent EntityId (None for roots)
        - metadata: free-form dictionary for extra attributes
    """

    id: EntityId
    parent: Optional[EntityId] = None
    metadata: dict = field(default_factory=dict)

    @property
    def type(self) -> EntityType:
        """Shortcut to self.id.type."""
        return self.id.type

    @property
    def key(self) -> str:
        """Shortcut to self.id.key."""
        return self.id.key
