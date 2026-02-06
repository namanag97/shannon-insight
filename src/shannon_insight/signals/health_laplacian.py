"""Health Laplacian computation for signal fusion.

The health Laplacian detects files that are worse than their neighbors:

    delta_h(f) = raw_risk(f) - mean(raw_risk(neighbors(f)))

Where:
- raw_risk is the pre-percentile weighted risk (NOT the percentile-based risk_score)
- neighbors are files that import f OR that f imports (undirected)

Interpretation:
- delta_h > 0: file is worse than its neighborhood
- delta_h > 0.4: triggers WEAK_LINK finder
- Orphans (no neighbors): delta_h = 0.0

Using raw values avoids circularity of computing Laplacian on percentile-uniform data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from shannon_insight.graph.models import DependencyGraph
    from shannon_insight.signals.models import FileSignals, SignalField


def compute_health_laplacian(field: SignalField, graph: DependencyGraph) -> Dict[str, float]:
    """Compute delta_h for all files.

    delta_h(f) = raw_risk(f) - mean(raw_risk(neighbors))

    Args:
        field: SignalField with per_file containing raw_risk values
        graph: DependencyGraph with adjacency and reverse maps

    Returns:
        Dict mapping file path to delta_h value
    """
    delta_h: Dict[str, float] = {}

    for path, fs in field.per_file.items():
        # Get neighbors: files that import this file OR that this file imports
        importers = graph.reverse.get(path, [])  # files that import this one
        imported = graph.adjacency.get(path, [])  # files this one imports
        neighbors = set(importers) | set(imported)

        # Filter to files we have signals for
        neighbors_in_field = [n for n in neighbors if n in field.per_file]

        if not neighbors_in_field:
            # Orphan: no neighbors, delta_h = 0.0
            delta_h[path] = 0.0
            continue

        # Compute mean raw_risk of neighbors
        neighbor_risks = [field.per_file[n].raw_risk for n in neighbors_in_field]
        mean_neighbor_risk = sum(neighbor_risks) / len(neighbor_risks)

        # delta_h = this file's risk - neighborhood mean
        delta_h[path] = fs.raw_risk - mean_neighbor_risk

    return delta_h


def compute_raw_risk(
    fs: FileSignals,
    max_pagerank: float,
    max_blast: float,
    max_cognitive: float,
    max_bus_factor: float,
) -> float:
    """Compute pre-percentile weighted risk for a file.

    Same weights as risk_score but on raw (normalized-by-max) values:

    raw_risk = 0.25 * (pagerank / max_pagerank)
             + 0.20 * (blast_radius_size / max_blast)
             + 0.20 * (cognitive_load / max_cognitive)
             + 0.20 * instability_factor
             + 0.15 * (1 - bus_factor / max_bus_factor)

    Args:
        fs: FileSignals with raw signal values
        max_pagerank: Max pagerank across all files (0 -> term = 0)
        max_blast: Max blast_radius_size across all files
        max_cognitive: Max cognitive_load across all files
        max_bus_factor: Max bus_factor across all files

    Returns:
        Raw risk value in [0, 1]
    """
    # Normalize by max (division-by-zero guarded)
    pr_term = fs.pagerank / max_pagerank if max_pagerank > 0 else 0.0
    blast_term = fs.blast_radius_size / max_blast if max_blast > 0 else 0.0
    cog_term = fs.cognitive_load / max_cognitive if max_cognitive > 0 else 0.0

    # Instability factor based on churn trajectory
    instab_factor = 1.0 if fs.churn_trajectory in ("CHURNING", "SPIKING") else 0.3

    # Bus factor: higher is better, so 1 - normalized
    bf_term = 1 - fs.bus_factor / max_bus_factor if max_bus_factor > 0 else 0.0

    raw_risk = (
        0.25 * pr_term + 0.20 * blast_term + 0.20 * cog_term + 0.20 * instab_factor + 0.15 * bf_term
    )

    return max(0.0, min(1.0, raw_risk))


def compute_all_raw_risks(field: SignalField) -> None:
    """Compute raw_risk for all files in SignalField.

    Modifies field.per_file[*].raw_risk in place.
    """
    if not field.per_file:
        return

    # Find max values across all files
    max_pr = max((fs.pagerank for fs in field.per_file.values()), default=0.0)
    max_blast = max((fs.blast_radius_size for fs in field.per_file.values()), default=0.0)
    max_cog = max((fs.cognitive_load for fs in field.per_file.values()), default=0.0)
    max_bf = max((fs.bus_factor for fs in field.per_file.values()), default=1.0)

    # Compute raw_risk for each file
    for fs in field.per_file.values():
        fs.raw_risk = compute_raw_risk(fs, max_pr, max_blast, max_cog, max_bf)
