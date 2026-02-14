"""Per-file quality signal computation (the 5 primitives)."""

from .registry import (
    PRIMITIVE_REGISTRY,
    PrimitiveDefinition,
    default_weights,
    get_definition,
    get_registry,
)

__all__ = [
    "PrimitiveDefinition",
    "PRIMITIVE_REGISTRY",
    "get_registry",
    "get_definition",
    "default_weights",
]
