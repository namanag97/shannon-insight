"""Architecture analysis models for Phase 4.

Defines Module, Layer, Violation, and Architecture dataclasses for
representing detected module boundaries, inferred layers, and
architectural violations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ViolationType(Enum):
    """Types of layer dependency violations."""

    BACKWARD = "backward"  # lower layer imports upper layer
    SKIP = "skip"  # layer N imports layer N+2 (skipping N+1)


@dataclass
class Module:
    """A group of source files forming a logical unit.

    Typically corresponds to a directory, but for flat projects may be
    inferred from Louvain communities.
    """

    path: str  # directory path
    files: list[str] = field(default_factory=list)
    file_count: int = 0

    # Martin metrics
    afferent_coupling: int = 0  # Ca: incoming edges from other modules
    efferent_coupling: int = 0  # Ce: outgoing edges to other modules
    internal_edges: int = 0
    external_edges: int = 0
    cohesion: float = 0.0  # internal / possible_internal
    coupling: float = 0.0  # external / (internal + external)
    instability: Optional[float] = None  # Ce / (Ca + Ce), None if isolated (Ca=Ce=0)
    abstractness: float = 0.0  # abstract_symbols / total_symbols
    main_seq_distance: float = 0.0  # |A + I - 1|

    # Boundary analysis
    boundary_alignment: float = 0.0  # files in dominant community / total files
    role_consistency: float = 0.0  # max(role_count) / total files
    dominant_role: str = "UNKNOWN"

    # Layer assignment (set by layer inference)
    layer: int = -1  # -1 = unassigned


@dataclass
class Layer:
    """A depth level in the inferred architectural layering."""

    depth: int
    modules: list[str] = field(default_factory=list)  # module paths
    label: str = ""  # e.g., "entry", "service", "core", "foundation"


@dataclass
class Violation:
    """A dependency that breaks the inferred layer ordering."""

    source_module: str
    target_module: str
    source_layer: int
    target_layer: int
    violation_type: ViolationType
    edge_count: int = 1  # number of file-level edges causing this


@dataclass
class Architecture:
    """Top-level result of architectural analysis."""

    modules: dict[str, Module] = field(default_factory=dict)
    layers: list[Layer] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)
    violation_rate: float = 0.0  # violating edges / total cross-module edges

    # Patterns detected
    has_layering: bool = False  # True if 2+ layers inferred
    max_depth: int = 0
    module_count: int = 0
