"""Composite score computation for signal fusion.

Implements all 7 composites from registry/composites.md:
- risk_score (per-file #35)
- wiring_quality (per-file #36)
- health_score (per-module #51)
- wiring_score (global #60)
- architecture_health (global #61)
- team_risk (global, unnumbered)
- codebase_health (global #62)

All composites computed as [0,1]. Display uses to_display_scale() for [1,10].
ABSOLUTE tier (<15 files): composites NOT computed (needs percentiles).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shannon_insight.signals.models import (
        FileSignals,
        ModuleSignals,
        SignalField,
    )


def compute_composites(field: SignalField) -> None:
    """Compute all composite scores.

    Requires percentiles to be filled. Modifies field in place.
    Skips computation for ABSOLUTE tier.
    """
    if field.tier == "ABSOLUTE":
        # < 15 files: composites not computed, show raw signals only
        return

    # Per-file composites
    max_bus_factor = _get_max_bus_factor(field)
    for fs in field.per_file.values():
        fs.risk_score = _compute_risk_score(fs, max_bus_factor)
        fs.wiring_quality = _compute_wiring_quality(fs)
        fs.file_health_score = _compute_file_health_score(fs)

    # Per-module composites
    for ms in field.per_module.values():
        ms.health_score = _compute_health_score(ms, field)

    # Global composites
    g = field.global_signals
    g.wiring_score = _compute_wiring_score(field)
    g.architecture_health = _compute_architecture_health(field)
    g.team_risk = _compute_team_risk(field)
    g.codebase_health = _compute_codebase_health(field)


# ── Per-file composites ────────────────────────────────────────────────


def _compute_risk_score(fs: FileSignals, max_bus_factor: float) -> float:
    """Signal #35: How dangerous is this file?

    risk_score = 0.25 * pctl(pagerank)
               + 0.20 * pctl(blast_radius_size)
               + 0.20 * pctl(cognitive_load)
               + 0.20 * instability_factor
               + 0.15 * (1 - bus_factor / max_bus_factor)

    instability_factor = 1.0 if trajectory in {CHURNING, SPIKING} else 0.3
    """
    pctl_pr = fs.percentiles.get("pagerank", 0.0)
    pctl_blast = fs.percentiles.get("blast_radius_size", 0.0)
    pctl_cog = fs.percentiles.get("cognitive_load", 0.0)

    # Instability factor based on churn trajectory
    instab_factor = 1.0 if fs.churn_trajectory in ("CHURNING", "SPIKING") else 0.3

    # Bus factor contribution (higher bus factor = lower risk)
    bf_term = 1 - fs.bus_factor / max(max_bus_factor, 1.0)

    risk = (
        0.25 * pctl_pr + 0.20 * pctl_blast + 0.20 * pctl_cog + 0.20 * instab_factor + 0.15 * bf_term
    )

    return max(0.0, min(1.0, risk))


def _compute_wiring_quality(fs: FileSignals) -> float:
    """Signal #36: How well-connected and implemented is this file?

    wiring_quality = 1 - (
        0.30 * is_orphan
      + 0.25 * stub_ratio
      + 0.25 * (phantom_import_count / max(import_count, 1))
      + 0.20 * (broken_call_count / max(total_calls, 1))
    )

    Higher = better wired.
    """
    orphan_term = 1.0 if fs.is_orphan else 0.0
    phantom_ratio = fs.phantom_import_count / max(fs.import_count, 1)

    # broken_call_count / total_calls - for now total_calls not tracked,
    # so we use in_degree + out_degree as proxy for connectedness
    total_calls = fs.in_degree + fs.out_degree
    broken_ratio = fs.broken_call_count / max(total_calls, 1)

    penalty = 0.30 * orphan_term + 0.25 * fs.stub_ratio + 0.25 * phantom_ratio + 0.20 * broken_ratio

    quality = 1.0 - penalty
    return max(0.0, min(1.0, quality))


def _compute_file_health_score(fs: FileSignals) -> float:
    """Per-file health composite.

    file_health = 1 - (0.25*risk_score + 0.25*(1-wiring_quality)
                     + 0.20*pctl(cognitive_load) + 0.15*stub_ratio
                     + 0.15*is_orphan)
    """
    pctl_cog = fs.percentiles.get("cognitive_load", 0.0)
    orphan_term = 1.0 if fs.is_orphan else 0.0

    penalty = (
        0.25 * fs.risk_score
        + 0.25 * (1.0 - fs.wiring_quality)
        + 0.20 * pctl_cog
        + 0.15 * fs.stub_ratio
        + 0.15 * orphan_term
    )

    return max(0.0, min(1.0, 1.0 - penalty))


# ── Per-module composites ──────────────────────────────────────────────


def _compute_health_score(ms: ModuleSignals, field: SignalField) -> float:
    """Signal #51: Overall module health.

    health_score = 0.20 * cohesion
                 + 0.15 * (1 - coupling)
                 + 0.20 * (1 - main_seq_distance)  # SKIP if instability=None
                 + 0.15 * boundary_alignment
                 + 0.15 * role_consistency
                 + 0.15 * (1 - mean_stub_ratio)

    If instability is None (isolated module), skip main_seq_distance term
    and redistribute its 0.20 weight to other terms (scale by 1.25).
    """
    # Get mean stub ratio for files in this module
    mean_stub = _get_mean_stub_ratio_for_module(ms, field)

    if ms.instability is None:
        # Redistribute 0.20 weight proportionally to remaining 5 terms
        # Original sum of other weights: 0.80
        # Scale factor: 1.0 / 0.80 = 1.25
        scale = 1.25
        health = (
            0.20 * scale * ms.cohesion
            + 0.15 * scale * (1 - ms.coupling)
            + 0.15 * scale * ms.boundary_alignment
            + 0.15 * scale * ms.role_consistency
            + 0.15 * scale * (1 - mean_stub)
        )
    else:
        health = (
            0.20 * ms.cohesion
            + 0.15 * (1 - ms.coupling)
            + 0.20 * (1 - ms.main_seq_distance)
            + 0.15 * ms.boundary_alignment
            + 0.15 * ms.role_consistency
            + 0.15 * (1 - mean_stub)
        )

    return max(0.0, min(1.0, health))


def _get_mean_stub_ratio_for_module(ms: ModuleSignals, field: SignalField) -> float:
    """Get mean stub_ratio for files in this module."""
    # Module path tells us which files belong to it
    # Files in module if their path starts with module path
    stub_ratios = []
    module_prefix = ms.path
    for path, fs in field.per_file.items():
        if path.startswith(module_prefix):
            stub_ratios.append(fs.stub_ratio)

    if not stub_ratios:
        return 0.0
    return sum(stub_ratios) / len(stub_ratios)


# ── Global composites ──────────────────────────────────────────────────


def _compute_wiring_score(field: SignalField) -> float:
    """Signal #60: Codebase-level AI code quality.

    wiring_score = 1 - (
        0.25 * orphan_ratio
      + 0.25 * phantom_ratio
      + 0.20 * glue_deficit
      + 0.15 * mean(stub_ratio)
      + 0.15 * clone_ratio
    )

    Higher = better wired.
    """
    g = field.global_signals
    mean_stub = _get_mean_stub_ratio(field)
    clone_ratio = _get_clone_ratio(field)

    penalty = (
        0.25 * g.orphan_ratio
        + 0.25 * g.phantom_ratio
        + 0.20 * g.glue_deficit
        + 0.15 * mean_stub
        + 0.15 * clone_ratio
    )

    return max(0.0, min(1.0, 1.0 - penalty))


def _compute_architecture_health(field: SignalField) -> float:
    """Signal #61: How well the system is structured.

    architecture_health = 0.25 * (1 - violation_rate)
                        + 0.20 * mean(cohesion)
                        + 0.20 * (1 - mean(coupling))
                        + 0.20 * (1 - mean(D))  # Guard instability=None
                        + 0.15 * mean(boundary_alignment)

    D = main_seq_distance (only for modules with instability != None)
    """
    if not field.per_module:
        return 0.0

    # Collect module metrics, guarding for None instability
    cohesions = []
    couplings = []
    distances = []  # Only modules with instability
    alignments = []

    for ms in field.per_module.values():
        cohesions.append(ms.cohesion)
        couplings.append(ms.coupling)
        alignments.append(ms.boundary_alignment)
        if ms.instability is not None:
            distances.append(ms.main_seq_distance)

    mean_cohesion = sum(cohesions) / len(cohesions) if cohesions else 0.0
    mean_coupling = sum(couplings) / len(couplings) if couplings else 0.0
    mean_D = sum(distances) / len(distances) if distances else 0.0
    mean_alignment = sum(alignments) / len(alignments) if alignments else 0.0

    # Get violation rate from global signals or compute
    # For now, assume violation_rate is pre-computed in global_signals
    # or we can compute from architecture if available
    violation_rate = _get_violation_rate(field)

    health = (
        0.25 * (1 - violation_rate)
        + 0.20 * mean_cohesion
        + 0.20 * (1 - mean_coupling)
        + 0.20 * (1 - mean_D)
        + 0.15 * mean_alignment
    )

    return max(0.0, min(1.0, health))


def _compute_team_risk(field: SignalField) -> float:
    """Unnumbered: Social/organizational risk score.

    team_risk = 1 - (
        0.30 * (min_bus_factor_critical / 3.0)  # capped at 3
      + 0.25 * (1 - max(knowledge_gini))
      + 0.25 * (1 - mean(coordination_cost) / 5.0)  # capped at 5
      + 0.20 * conway_alignment
    )

    Higher = more team risk (bad).
    """
    # min_bus_factor_critical: min(bus_factor) across high centrality files
    # (files with pctl(pagerank) > 0.75)
    min_bf_crit = _get_min_bus_factor_critical(field)

    # Max knowledge gini across modules
    max_kg = 0.0
    mean_coord = 0.0
    if field.per_module:
        ginis = [ms.knowledge_gini for ms in field.per_module.values()]
        max_kg = max(ginis) if ginis else 0.0
        coords = [ms.coordination_cost for ms in field.per_module.values()]
        mean_coord = sum(coords) / len(coords) if coords else 0.0

    # Conway alignment (for now, assume 1.0 if not computed)
    conway = _get_conway_alignment(field)

    bf_term = min(min_bf_crit, 3.0) / 3.0
    coord_term = min(mean_coord, 5.0) / 5.0

    good_score = 0.30 * bf_term + 0.25 * (1 - max_kg) + 0.25 * (1 - coord_term) + 0.20 * conway

    # team_risk = 1 - good_score (high risk = bad)
    return max(0.0, min(1.0, 1.0 - good_score))


def _compute_codebase_health(field: SignalField) -> float:
    """Signal #62: The one number.

    codebase_health = 0.30 * architecture_health
                    + 0.30 * wiring_score
                    + 0.20 * (global_bus_factor / team_size)
                    + 0.20 * modularity

    global_bus_factor = min_bus_factor_critical (capped at team_size)
    """
    g = field.global_signals

    # Team size: distinct authors (use a reasonable default if not available)
    team_size = _get_team_size(field)
    global_bf = min(_get_min_bus_factor_critical(field), team_size)

    bf_ratio = global_bf / max(team_size, 1)

    health = (
        0.30 * g.architecture_health + 0.30 * g.wiring_score + 0.20 * bf_ratio + 0.20 * g.modularity
    )

    return max(0.0, min(1.0, health))


# ── Helper functions ───────────────────────────────────────────────────


def _get_max_bus_factor(field: SignalField) -> float:
    """Get maximum bus factor across all files."""
    if not field.per_file:
        return 1.0
    bfs = [fs.bus_factor for fs in field.per_file.values()]
    return max(bfs) if bfs else 1.0


def _get_mean_stub_ratio(field: SignalField) -> float:
    """Get mean stub ratio across all files."""
    if not field.per_file:
        return 0.0
    stubs = [fs.stub_ratio for fs in field.per_file.values()]
    return sum(stubs) / len(stubs) if stubs else 0.0


def _get_clone_ratio(field: SignalField) -> float:
    """Get clone ratio (files in NCD clone pairs / total files).

    Pre-computed in fusion from Phase 3 clone detection.
    """
    return field.global_signals.clone_ratio


def _get_violation_rate(field: SignalField) -> float:
    """Get layer violation rate from architecture.

    violation_rate = violating_cross_module_edges / total_cross_module_edges

    Pre-computed in fusion from Phase 4 architecture.
    """
    return field.global_signals.violation_rate


def _get_min_bus_factor_critical(field: SignalField) -> float:
    """Get min bus factor across high-centrality files.

    High centrality = pctl(pagerank) > 0.75
    """
    critical_bfs = []
    for fs in field.per_file.values():
        pctl_pr = fs.percentiles.get("pagerank", 0.0)
        if pctl_pr > 0.75:
            critical_bfs.append(fs.bus_factor)

    if not critical_bfs:
        # No high-centrality files, use overall min
        all_bfs = [fs.bus_factor for fs in field.per_file.values()]
        return min(all_bfs) if all_bfs else 1.0

    return min(critical_bfs)


def _get_conway_alignment(field: SignalField) -> float:
    """Get Conway's Law alignment: 1 - mean(author_distance).

    Author distance measures team overlap between modules.
    If not available (solo project), return 1.0 (no team risk).

    Pre-computed in fusion from Phase 3 author distances.
    """
    return field.global_signals.conway_alignment


def _get_team_size(field: SignalField) -> int:
    """Get team size (distinct authors in recent window).

    Should come from git_history. Default to 1 for solo projects.

    Pre-computed in fusion from Phase 3 git history.
    """
    return field.global_signals.team_size
