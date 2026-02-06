"""Topological sorting for analyzer ordering using graphlib.

Uses Python's graphlib.TopologicalSorter to order analyzers based on
their requires/provides declarations. Detects cycles and slot collisions
at startup time, not runtime.

Key features:
    - Single-owner rule: Each slot can only be provided by one analyzer
    - Cycle detection: Catches cycles immediately, not at runtime
    - Wave 2 support: run_last analyzers are sorted to the end
    - Diamond handling: Supports diamond dependencies correctly

Inspired by SonarQube's DirectAcyclicGraph.sort() for MeasureComputers.
"""

from __future__ import annotations

from graphlib import CycleError, TopologicalSorter
from typing import Any


class SlotCollisionError(ValueError):
    """Raised when multiple analyzers provide the same slot."""

    pass


class AnalyzerCycleError(ValueError):
    """Raised when analyzer dependencies form a cycle."""

    pass


def resolve_analyzer_order(analyzers: list[Any]) -> list[Any]:
    """Topologically sort analyzers based on requires/provides.

    Args:
        analyzers: List of analyzer objects with requires, provides, run_last attributes

    Returns:
        Analyzers in dependency order (Wave 1 first, then Wave 2 run_last)

    Raises:
        SlotCollisionError: If two analyzers provide the same slot
        AnalyzerCycleError: If there's a dependency cycle
    """
    if not analyzers:
        return []

    # Separate Wave 1 and Wave 2 (run_last) analyzers
    wave1 = [a for a in analyzers if not getattr(a, "run_last", False)]
    wave2 = [a for a in analyzers if getattr(a, "run_last", False)]

    # Sort Wave 1
    sorted_wave1 = _toposort_analyzers(wave1)

    # Sort Wave 2 (respecting any dependencies among them)
    # Wave 2 analyzers can depend on Wave 1 outputs but not vice versa
    sorted_wave2 = _toposort_analyzers(wave2)

    return sorted_wave1 + sorted_wave2


def _toposort_analyzers(analyzers: list[Any]) -> list[Any]:
    """Internal topological sort for a single wave of analyzers."""
    if not analyzers:
        return []

    # Build slot -> analyzer_name mapping
    provides_map: dict[str, str] = {}
    for analyzer in analyzers:
        for slot in getattr(analyzer, "provides", set()):
            if slot in provides_map:
                raise SlotCollisionError(
                    f"Slot '{slot}' provided by both '{provides_map[slot]}' "
                    f"and '{analyzer.name}'"
                )
            provides_map[slot] = analyzer.name

    # Build dependency graph
    ts: TopologicalSorter[str] = TopologicalSorter()
    name_to_analyzer: dict[str, Any] = {}

    for analyzer in analyzers:
        name = analyzer.name
        name_to_analyzer[name] = analyzer

        # Add node (even if no dependencies)
        ts.add(name)

        # Add edges for each requirement
        for req in getattr(analyzer, "requires", set()):
            if req in provides_map:
                # This analyzer depends on whoever provides req
                provider = provides_map[req]
                ts.add(name, provider)
            # If req is not in provides_map, it's either:
            # - An external requirement (handled at runtime)
            # - A requirement from another wave (Wave 2 depending on Wave 1)
            # We don't error here; the kernel skips at runtime if not available

    # Execute topological sort
    try:
        order = list(ts.static_order())
    except CycleError as e:
        raise AnalyzerCycleError(f"Analyzer dependency cycle detected: {e}") from e

    # Convert names back to analyzer objects
    return [name_to_analyzer[name] for name in order if name in name_to_analyzer]
