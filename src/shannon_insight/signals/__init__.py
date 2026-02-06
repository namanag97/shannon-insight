"""Per-file quality signal computation (the 5 primitives)."""

from .extractor import PrimitiveExtractor
from .registry import (
    PRIMITIVE_REGISTRY,
    PrimitiveDefinition,
    default_weights,
    get_definition,
    get_registry,
)

__all__ = [
    "PrimitiveExtractor",
    "PrimitiveDefinition",
    "PRIMITIVE_REGISTRY",
    "get_registry",
    "get_definition",
    "default_weights",
]
