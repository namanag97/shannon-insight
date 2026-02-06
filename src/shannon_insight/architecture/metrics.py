"""Martin metrics computation for Phase 4.

Computes per-module metrics:
- Afferent Coupling (Ca): incoming edges from other modules
- Efferent Coupling (Ce): outgoing edges to other modules
- Instability (I): Ce / (Ca + Ce), None if isolated
- Abstractness (A): abstract_symbols / total_symbols
- Main Sequence Distance (D): |A + I - 1|
- Role Consistency: max(role_count) / total_files
"""

from collections import Counter
from typing import Dict, List, Optional, Tuple

from ..graph.models import DependencyGraph
from .models import Module


def compute_coupling(
    module: Module,
    all_modules: Dict[str, Module],
    graph: DependencyGraph,
) -> Tuple[int, int]:
    """Compute afferent (Ca) and efferent (Ce) coupling for a module.

    Ca = edges FROM other modules TO this module's files
    Ce = edges FROM this module's files TO other modules

    Args:
        module: The module to analyze
        all_modules: All modules in the architecture
        graph: The dependency graph

    Returns:
        Tuple of (Ca, Ce)
    """
    module_files = set(module.files)

    # Build reverse lookup: file -> module
    file_to_module: Dict[str, str] = {}
    for mod_path, mod in all_modules.items():
        for f in mod.files:
            file_to_module[f] = mod_path

    ca = 0  # Incoming from other modules
    ce = 0  # Outgoing to other modules

    for file_path in module.files:
        # Outgoing edges (this file imports other files)
        for target in graph.adjacency.get(file_path, []):
            target_module = file_to_module.get(target)
            if target_module and target_module != module.path:
                ce += 1

        # Incoming edges (other files import this file)
        for source in graph.reverse.get(file_path, []):
            source_module = file_to_module.get(source)
            if source_module and source_module != module.path:
                ca += 1

    return ca, ce


def compute_instability(ca: int, ce: int) -> Optional[float]:
    """Compute instability I = Ce / (Ca + Ce).

    Args:
        ca: Afferent coupling (incoming edges)
        ce: Efferent coupling (outgoing edges)

    Returns:
        Instability in [0, 1], or None if isolated (Ca=Ce=0)
    """
    total = ca + ce
    if total == 0:
        return None  # Cannot measure - isolated module
    return ce / total


def compute_abstractness(
    class_count: int,
    abstract_class_count: int,
    protocol_count: int,
    abstract_method_count: int,
) -> float:
    """Compute abstractness A = abstract_symbols / total_symbols.

    For now, uses class-level abstraction:
    A = (abstract_classes + protocols) / total_classes

    Future: include abstract methods and "never-instantiated" classes
    (requires CALL edges from Phase 3b).

    Args:
        class_count: Total number of classes
        abstract_class_count: Classes with @abstractmethod or ABC base
        protocol_count: Protocol subclasses
        abstract_method_count: Individual abstract methods (unused for now)

    Returns:
        Abstractness in [0, 1]
    """
    if class_count == 0:
        return 0.0

    abstract_count = abstract_class_count + protocol_count
    return min(1.0, abstract_count / class_count)


def compute_main_seq_distance(
    abstractness: float,
    instability: Optional[float],
) -> float:
    """Compute main sequence distance D = |A + I - 1|.

    The main sequence is the line from (0, 1) to (1, 0) in the A-I plane.
    Distance from this line measures architectural health:
    - D ≈ 0: balanced module (on the main sequence)
    - D ≈ 1 with A=0, I=0: Zone of Pain (stable but concrete)
    - D ≈ 1 with A=1, I=1: Zone of Uselessness (abstract but unstable)

    Args:
        abstractness: Abstractness in [0, 1]
        instability: Instability in [0, 1], or None if isolated

    Returns:
        Distance from main sequence in [0, 1], or 0.0 if instability is None
    """
    if instability is None:
        return 0.0  # Cannot compute without instability
    return abs(abstractness + instability - 1.0)


def compute_role_consistency(
    files: List[str],
    roles: Dict[str, str],
) -> Tuple[float, str]:
    """Compute role consistency for a module.

    Role consistency = max(role_count) / total_files
    Measures how homogeneous the module is in terms of file roles.

    Args:
        files: List of file paths in the module
        roles: Mapping of file path to role

    Returns:
        Tuple of (consistency in [0, 1], dominant role)
    """
    if not files:
        return 0.0, "UNKNOWN"

    role_counts: Counter[str] = Counter()
    for f in files:
        role = roles.get(f, "UNKNOWN")
        role_counts[role] += 1

    if not role_counts:
        return 0.0, "UNKNOWN"

    dominant_role, max_count = role_counts.most_common(1)[0]
    consistency = max_count / len(files)

    return consistency, dominant_role


def compute_module_metrics(
    module: Module,
    all_modules: Dict[str, Module],
    graph: DependencyGraph,
    roles: Dict[str, str],
    file_class_counts: Optional[Dict[str, int]] = None,
    file_abstract_counts: Optional[Dict[str, int]] = None,
) -> None:
    """Compute all Martin metrics for a module (mutates module in place).

    Args:
        module: The module to update
        all_modules: All modules for coupling computation
        graph: The dependency graph
        roles: File -> role mapping
        file_class_counts: Optional per-file class counts
        file_abstract_counts: Optional per-file abstract class counts
    """
    # Coupling
    ca, ce = compute_coupling(module, all_modules, graph)
    module.afferent_coupling = ca
    module.efferent_coupling = ce

    # Instability
    module.instability = compute_instability(ca, ce)

    # Internal/external edge counts
    module_files = set(module.files)
    internal = 0
    external = 0
    for f in module.files:
        for target in graph.adjacency.get(f, []):
            if target in module_files:
                internal += 1
            else:
                external += 1
    module.internal_edges = internal
    module.external_edges = external

    # Cohesion and coupling ratios
    total_edges = internal + external
    if total_edges > 0:
        module.coupling = external / total_edges
    n = len(module.files)
    possible_internal = n * (n - 1)  # Max possible internal edges
    if possible_internal > 0:
        module.cohesion = internal / possible_internal

    # Abstractness (simplified - count from file metadata if available)
    total_classes = 0
    abstract_classes = 0
    if file_class_counts and file_abstract_counts:
        for f in module.files:
            total_classes += file_class_counts.get(f, 0)
            abstract_classes += file_abstract_counts.get(f, 0)
    module.abstractness = compute_abstractness(total_classes, abstract_classes, 0, 0)

    # Main sequence distance
    module.main_seq_distance = compute_main_seq_distance(module.abstractness, module.instability)

    # Role consistency
    consistency, dominant = compute_role_consistency(module.files, roles)
    module.role_consistency = consistency
    module.dominant_role = dominant
