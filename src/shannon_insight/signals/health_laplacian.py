"""Health Laplacian computation for signal fusion.

The health Laplacian detects files that are worse than their neighbors,
using a degree-weighted (normalized) graph Laplacian:

    delta_h(f) = sqrt(degree(f)) * (raw_risk(f) - mean(raw_risk(neighbors(f))))

Where:
- raw_risk is the pre-percentile weighted risk (NOT the percentile-based risk_score)
- neighbors are files that import f OR that f imports (undirected)
- degree(f) is the number of neighbors of f

The sqrt(degree) scaling ensures that hub files (high degree) with even
slightly-above-average risk produce a much larger delta_h than leaf files
(low degree) with the same excess.  This matches the normalized graph
Laplacian: L_norm = D^{1/2} (D^{-1} L) = D^{1/2} (I - D^{-1} A),
applied to the raw_risk signal vector.

Interpretation:
- delta_h > 0: file is worse than its neighborhood
- delta_h > 0.4: triggers WEAK_LINK finder
- Orphans (no neighbors): delta_h = 0.0

Using raw values avoids circularity of computing Laplacian on percentile-uniform data.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shannon_insight.graph.models import DependencyGraph
    from shannon_insight.signals.models import FileSignals, SignalField


def compute_health_laplacian(field: SignalField, graph: DependencyGraph) -> dict[str, float]:
    """Compute delta_h for all files using a degree-weighted graph Laplacian.

    delta_h(f) = sqrt(degree(f)) * (raw_risk(f) - mean(raw_risk(neighbors)))

    The sqrt(degree) factor amplifies the signal for hub files: a hub with
    20 neighbors that is slightly above its neighborhood average will produce
    a much larger delta_h than a leaf with 2 neighbors and the same excess.

    Args:
        field: SignalField with per_file containing raw_risk values
        graph: DependencyGraph with adjacency and reverse maps

    Returns:
        Dict mapping file path to delta_h value
    """
    delta_h: dict[str, float] = {}

    # Pre-compute neighbor sets for all files to avoid repeated set operations
    neighbor_cache: dict[str, list[str]] = {}
    for path in field.per_file:
        importers = graph.reverse.get(path, [])
        imported = graph.adjacency.get(path, [])
        neighbors = set(importers) | set(imported)
        # Filter to files we have signals for
        neighbor_cache[path] = [n for n in neighbors if n in field.per_file]

    for path, fs in field.per_file.items():
        neighbors_in_field = neighbor_cache[path]
        degree = len(neighbors_in_field)

        if degree == 0:
            # Orphan: no neighbors, delta_h = 0.0
            delta_h[path] = 0.0
            continue

        # Compute mean raw_risk of neighbors
        neighbor_risks = [field.per_file[n].raw_risk for n in neighbors_in_field]
        mean_neighbor_risk = sum(neighbor_risks) / degree

        # Degree-weighted Laplacian: scale by sqrt(degree) so hub files
        # with above-average risk get amplified delta_h
        delta_h[path] = math.sqrt(degree) * (fs.raw_risk - mean_neighbor_risk)

    return delta_h


_SAFE_BUS_FACTOR = 5.0  # Must match composites.py — raw_risk and risk_score formulas must agree


def compute_raw_risk(
    fs: FileSignals,
    max_pagerank: float,
    max_blast: float,
    max_cognitive: float,
) -> float:
    """Compute pre-percentile weighted risk for a file.

    Same weights as risk_score but on raw (normalized-by-max) values:

    graph_impact_raw = max(pagerank / max_pagerank, blast_radius_size / max_blast)

    raw_risk = 0.35 * graph_impact_raw
             + 0.25 * (cognitive_load / max_cognitive)
             + 0.25 * instability_factor
             + 0.15 * (1 - bus_factor / SAFE_BUS_FACTOR)

    graph_impact_raw merges pagerank and blast_radius into a single term because
    both derive from the same import graph and are highly correlated.
    Using max() avoids double-counting while still capturing the stronger signal.

    bus_factor uses fixed cap (SAFE_BUS_FACTOR=5.0), not relative-to-max,
    to match the composites.py formula exactly.

    Returns:
        Raw risk value in [0, 1]
    """
    pr_term = fs.pagerank / max_pagerank if max_pagerank > 0 else 0.0
    blast_term = fs.blast_radius_size / max_blast if max_blast > 0 else 0.0
    cog_term = fs.cognitive_load / max_cognitive if max_cognitive > 0 else 0.0
    graph_impact_raw = max(pr_term, blast_term)
    instab_factor = min(fs.churn_cv / 2.0, 1.0) if fs.churn_cv > 0 else 0.0
    bf_term = max(0.0, 1.0 - fs.bus_factor / _SAFE_BUS_FACTOR)

    raw_risk = (
        0.35 * graph_impact_raw + 0.25 * cog_term + 0.25 * instab_factor + 0.15 * bf_term
    )

    return max(0.0, min(1.0, raw_risk))


def compute_all_raw_risks(field: SignalField) -> None:
    """Compute raw_risk for all files in SignalField.

    Modifies field.per_file[*].raw_risk in place.
    """
    if not field.per_file:
        return

    max_pr = max((fs.pagerank for fs in field.per_file.values()), default=0.0)
    max_blast = max((fs.blast_radius_size for fs in field.per_file.values()), default=0.0)
    max_cog = max((fs.cognitive_load for fs in field.per_file.values()), default=0.0)

    for fs in field.per_file.values():
        fs.raw_risk = compute_raw_risk(fs, max_pr, max_blast, max_cog)
