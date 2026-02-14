"""Primitive definitions registry — the single source of truth for all primitives.

Now backed by plugin classes. The PrimitiveDefinition dataclass is built
automatically from each plugin's attributes for backward compatibility.
"""

from dataclasses import dataclass
from typing import Callable

from .base import PrimitivePlugin
from .plugins.cognitive_load import CognitiveLoadPrimitive
from .plugins.coherence import CoherencePrimitive
from .plugins.compression import CompressionPrimitive
from .plugins.volatility import VolatilityPrimitive


@dataclass
class PrimitiveDefinition:
    name: str
    display_name: str
    short_name: str
    description: str
    direction: str
    default_weight: float
    interpret: Callable[[float], str]


# ── Plugin instances ───────────────────────────────────────────────

_ALL_PLUGINS: list[PrimitivePlugin] = [
    CompressionPrimitive(),
    VolatilityPrimitive(),
    CoherencePrimitive(),
    CognitiveLoadPrimitive(),
]


def get_plugins() -> list[PrimitivePlugin]:
    """Return all registered plugin instances."""
    return list(_ALL_PLUGINS)


def get_plugin(name: str) -> PrimitivePlugin:
    """Look up a plugin by name."""
    for p in _ALL_PLUGINS:
        if p.name == name:
            return p
    raise KeyError(f"Unknown primitive: {name!r}")


# ── Backward-compatible registry (PrimitiveDefinition list) ────────


def _plugin_to_defn(plugin: PrimitivePlugin) -> PrimitiveDefinition:
    return PrimitiveDefinition(
        name=plugin.name,
        display_name=plugin.display_name,
        short_name=plugin.short_name,
        description=plugin.description,
        direction=plugin.direction,
        default_weight=plugin.default_weight,
        interpret=plugin.interpret,
    )


PRIMITIVE_REGISTRY: list[PrimitiveDefinition] = [_plugin_to_defn(p) for p in _ALL_PLUGINS]


def get_registry() -> list[PrimitiveDefinition]:
    """Return the current registry (snapshot)."""
    return list(PRIMITIVE_REGISTRY)


def get_definition(name: str) -> PrimitiveDefinition:
    """Look up a primitive by name."""
    for defn in PRIMITIVE_REGISTRY:
        if defn.name == name:
            return defn
    raise KeyError(f"Unknown primitive: {name!r}")


def default_weights() -> dict:
    """Return {name: weight} from the registry, normalized to sum to 1."""
    total = sum(d.default_weight for d in PRIMITIVE_REGISTRY)
    if total == 0:
        total = 1.0
    return {d.name: d.default_weight / total for d in PRIMITIVE_REGISTRY}
