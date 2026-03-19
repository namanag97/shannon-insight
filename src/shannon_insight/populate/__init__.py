"""Tensor population layer — fills RelationTensor from extracted data."""

from .authors import populate_authors
from .clones import populate_clones
from .cochange import populate_cochange
from .combined import populate_combined
from .imports import populate_imports
from .semantic import populate_semantic

__all__ = [
    "populate_imports",
    "populate_cochange",
    "populate_authors",
    "populate_semantic",
    "populate_clones",
    "populate_combined",
]
