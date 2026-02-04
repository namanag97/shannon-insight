"""Primitive definitions registry — the single source of truth for all primitives.

Adding a new primitive requires:
1. Add a PrimitiveDefinition entry to PRIMITIVE_REGISTRY below.
2. Add a ``_compute_<name>`` method in PrimitiveExtractor that returns Dict[str, float].
That's it — AnomalyDetector, SignalFusion, and formatters pick it up automatically.
"""

from dataclasses import dataclass
from typing import Callable, List


@dataclass
class PrimitiveDefinition:
    name: str             # "structural_entropy"
    display_name: str     # "Structural Entropy"
    short_name: str       # "entropy" (for compact table columns)
    description: str      # human-readable description
    direction: str        # "high_is_bad" | "low_is_bad" | "both_extreme_bad"
    default_weight: float # fusion weight (will be normalized)
    interpret: Callable[[float], str]  # raw value -> human-readable note


def _interpret_compression(v: float) -> str:
    if v < 0.20:
        return "highly repetitive (duplication?)"
    elif v < 0.45:
        return "normal complexity"
    elif v < 0.65:
        return "dense/complex"
    return "very dense"


def _interpret_centrality(v: float) -> str:
    if v > 0.5:
        return "high = heavily depended on"
    return "within typical range"


def _interpret_volatility(v: float) -> str:
    if v > 0.5:
        return "high = frequently changed"
    return "within typical range"


def _interpret_coherence(v: float) -> str:
    if v < 0.30:
        return "mixed responsibilities"
    elif v < 0.70:
        return "somewhat focused"
    return "highly focused"


def _interpret_cognitive(v: float) -> str:
    if v > 0.6:
        return "high = hard to understand"
    return "within typical range"


PRIMITIVE_REGISTRY: List[PrimitiveDefinition] = [
    PrimitiveDefinition(
        name="structural_entropy",
        display_name="Compression Complexity",
        short_name="compress",
        description="Compression-based complexity (Kolmogorov approximation)",
        direction="both_extreme_bad",
        default_weight=0.20,
        interpret=_interpret_compression,
    ),
    PrimitiveDefinition(
        name="network_centrality",
        display_name="Network Centrality",
        short_name="centrality",
        description="Importance in dependency graph (PageRank)",
        direction="high_is_bad",
        default_weight=0.25,
        interpret=_interpret_centrality,
    ),
    PrimitiveDefinition(
        name="churn_volatility",
        display_name="Churn Volatility",
        short_name="churn",
        description="Instability of change patterns",
        direction="high_is_bad",
        default_weight=0.20,
        interpret=_interpret_volatility,
    ),
    PrimitiveDefinition(
        name="semantic_coherence",
        display_name="Identifier Coherence",
        short_name="coherence",
        description="Responsibility focus (identifier clustering)",
        direction="both_extreme_bad",
        default_weight=0.15,
        interpret=_interpret_coherence,
    ),
    PrimitiveDefinition(
        name="cognitive_load",
        display_name="Cognitive Load",
        short_name="cog.load",
        description="Mental effort to understand (Gini-enhanced)",
        direction="high_is_bad",
        default_weight=0.20,
        interpret=_interpret_cognitive,
    ),
]


def get_registry() -> List[PrimitiveDefinition]:
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
