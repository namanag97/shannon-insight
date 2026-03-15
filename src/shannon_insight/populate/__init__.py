"""Tensor population layer — fills RelationTensor from extracted data."""
from .imports import populate_imports
from .cochange import populate_cochange
from .authors import populate_authors
from .semantic import populate_semantic
from .combined import populate_combined

__all__ = [
    "populate_imports", "populate_cochange", "populate_authors",
    "populate_semantic", "populate_combined",
]
