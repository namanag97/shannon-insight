"""Capture an analysis snapshot from the AnalysisStore and InsightResult.

V2 captures the full SignalField with FileSignals, ModuleSignals, GlobalSignals,
plus architecture data (modules, layers, violations) and health Laplacian delta_h.
"""

import subprocess
from datetime import datetime, timezone
from typing import Any, Optional

from .. import __version__
from ..cache import compute_config_hash
from ..session import AnalysisSession
from ..insights.models import InsightResult
from ..insights.store_v2 import AnalysisStore
from ..signals.models import FileSignals, GlobalSignals, ModuleSignals
from .identity import compute_identity_key
from .models import EvidenceRecord, FindingRecord, Snapshot, TensorSnapshot

# Trajectory string -> numeric encoding
_TRAJECTORY_MAP: dict[str, float] = {
    "dormant": 0.0,
    "stabilizing": 1.0,
    "churning": 2.0,
    "spiking": 3.0,
}


def capture_snapshot(
    store: AnalysisStore,
    result: InsightResult,
    settings: AnalysisSettings,
) -> Snapshot:
    """Build an immutable V1 Snapshot from the analysis store and result.

    DEPRECATED: Use capture_tensor_snapshot() for new code.

    Parameters
    ----------
    store:
        The populated ``AnalysisStore`` blackboard.
    result:
        The ``InsightResult`` returned by the kernel.
    settings:
        The ``AnalysisSettings`` used for this run.

    Returns
    -------
    Snapshot
        A complete, serialisable record of the analysis run.
    """
    file_signals = _collect_file_signals(store)
    codebase_signals = _collect_codebase_signals(store)
    findings = _convert_findings(result)
    dependency_edges = _collect_dependency_edges(store)
    commit_sha = _get_commit_sha(store.root_dir)
    config_hash = _compute_config_hash(settings)
    analyzers_ran = _determine_analyzers_ran(store)

    return Snapshot(
        schema_version=1,
        tool_version=__version__,
        commit_sha=commit_sha,
        timestamp=datetime.now(timezone.utc).isoformat(),
        analyzed_path=store.root_dir,
        file_count=result.store_summary.total_files,
        module_count=result.store_summary.total_modules,
        commits_analyzed=result.store_summary.commits_analyzed,
        analyzers_ran=analyzers_ran,
        config_hash=config_hash,
        file_signals=file_signals,
        codebase_signals=codebase_signals,
        findings=findings,
        dependency_edges=dependency_edges,
    )


def capture_tensor_snapshot(
    store: AnalysisStore,
    result: InsightResult,
    settings: AnalysisSettings,
) -> TensorSnapshot:
    """Build an immutable V2 TensorSnapshot from the analysis store and result.

    Captures the full SignalField with:
    - Per-file signals (FileSignals) including percentiles
    - Per-module signals (ModuleSignals)
    - Global signals (GlobalSignals)
    - Architecture data (modules, layers, violations)
    - Health Laplacian delta_h

    Parameters
    ----------
    store:
        The populated ``AnalysisStore`` blackboard.
    result:
        The ``InsightResult`` returned by the kernel.
    settings:
        The ``AnalysisSettings`` used for this run.

    Returns
    -------
    TensorSnapshot
        A complete V2 snapshot with full signal data.
    """
    commit_sha = _get_commit_sha(store.root_dir)
    config_hash = _compute_config_hash(settings)
    analyzers_ran = _determine_analyzers_ran(store)
    dependency_edges = _collect_dependency_edges(store)
    cochange_edges = _collect_cochange_edges(store)

    # Serialize SignalField if available
    file_signals: dict[str, dict[str, Any]] = {}
    module_signals: dict[str, dict[str, Any]] = {}
    global_signals: dict[str, Any] = {}
    delta_h: dict[str, float] = {}

    if store.signal_field.available:
        sf = store.signal_field.value
        # Per-file signals
        for path, fs in sf.per_file.items():
            file_signals[path] = _serialize_file_signals(fs)
        # Per-module signals
        for path, ms in sf.per_module.items():
            module_signals[path] = _serialize_module_signals(ms)
        # Global signals
        global_signals = _serialize_global_signals(sf.global_signals)
        # delta_h (health Laplacian)
        delta_h = dict(sf.delta_h)
    else:
        # Fallback to v1 collection if SignalField not available
        file_signals = _collect_file_signals(store)
        global_signals = _collect_codebase_signals(store)

    # Serialize architecture if available
    modules: list[str] = []
    layers: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    if store.architecture.available:
        arch = store.architecture.value
        modules = list(arch.modules.keys()) if hasattr(arch, "modules") else []
        if hasattr(arch, "layers"):
            layers = [{"depth": l.depth, "modules": l.modules} for l in arch.layers]
        if hasattr(arch, "violations"):
            violations = [
                {
                    "src": v.source_module,
                    "tgt": v.target_module,
                    "type": v.violation_type.value
                    if hasattr(v.violation_type, "value")
                    else str(v.violation_type),
                }
                for v in arch.violations
            ]

    # Serialize community data from structural analysis if available
    communities: list[dict[str, Any]] = []
    node_community: dict[str, int] = {}
    modularity_score: float = 0.0

    if store.structural.available:
        structural = store.structural.value
        if hasattr(structural, "graph_analysis"):
            ga = structural.graph_analysis
            communities = [
                {"id": c.id, "members": list(c.members), "size": len(c.members)}
                for c in ga.communities
            ]
            node_community = dict(ga.node_community)
            modularity_score = ga.modularity_score

    # Convert findings with v2 fields
    findings = _convert_findings_v2(result)

    return TensorSnapshot(
        schema_version=2,
        tool_version=__version__,
        commit_sha=commit_sha,
        timestamp=datetime.now(timezone.utc).isoformat(),
        analyzed_path=store.root_dir,
        file_count=result.store_summary.total_files,
        module_count=result.store_summary.total_modules,
        commits_analyzed=result.store_summary.commits_analyzed,
        analyzers_ran=analyzers_ran,
        config_hash=config_hash,
        file_signals=file_signals,
        module_signals=module_signals,
        global_signals=global_signals,
        findings=findings,
        dependency_edges=dependency_edges,
        cochange_edges=cochange_edges,
        modules=modules,
        layers=layers,
        violations=violations,
        delta_h=delta_h,
        communities=communities,
        node_community=node_community,
        modularity_score=modularity_score,
    )


# ── Private helpers ──────────────────────────────────────────────────


def _serialize_file_signals(fs: FileSignals) -> dict[str, Any]:
    """Serialize FileSignals to a dict for snapshot storage.

    Includes all scalar fields plus the percentiles dict.
    """
    result: dict[str, Any] = {}

    # Scalar fields (skip 'path' and 'percentiles')
    for field_name in [
        "lines",
        "function_count",
        "class_count",
        "max_nesting",
        "impl_gini",
        "stub_ratio",
        "import_count",
        "role",
        "concept_count",
        "concept_entropy",
        "naming_drift",
        "todo_density",
        "docstring_coverage",
        "pagerank",
        "betweenness",
        "in_degree",
        "out_degree",
        "blast_radius_size",
        "depth",
        "is_orphan",
        "phantom_import_count",
        "broken_call_count",
        "community",
        "compression_ratio",
        "semantic_coherence",
        "cognitive_load",
        "total_changes",
        "churn_trajectory",
        "churn_slope",
        "churn_cv",
        "bus_factor",
        "author_entropy",
        "fix_ratio",
        "refactor_ratio",
        "change_entropy",
        "raw_risk",
        "risk_score",
        "wiring_quality",
        "file_health_score",
    ]:
        val = getattr(fs, field_name, None)
        if val is not None:
            result[field_name] = val

    # Include percentiles as nested dict
    if fs.percentiles:
        result["percentiles"] = dict(fs.percentiles)

    return result


def _serialize_module_signals(ms: ModuleSignals) -> dict[str, Any]:
    """Serialize ModuleSignals to a dict for snapshot storage."""
    result: dict[str, Any] = {}

    for field_name in [
        "cohesion",
        "coupling",
        "instability",
        "abstractness",
        "main_seq_distance",
        "boundary_alignment",
        "layer_violation_count",
        "role_consistency",
        "velocity",
        "coordination_cost",
        "knowledge_gini",
        "module_bus_factor",
        "mean_cognitive_load",
        "file_count",
        "health_score",
    ]:
        val = getattr(ms, field_name, None)
        if val is not None:
            result[field_name] = val

    return result


def _serialize_global_signals(gs: GlobalSignals) -> dict[str, Any]:
    """Serialize GlobalSignals to a dict for snapshot storage."""
    result: dict[str, Any] = {}

    for field_name in [
        "modularity",
        "fiedler_value",
        "spectral_gap",
        "cycle_count",
        "centrality_gini",
        "orphan_ratio",
        "phantom_ratio",
        "glue_deficit",
        "clone_ratio",
        "violation_rate",
        "conway_alignment",
        "team_size",
        "wiring_score",
        "architecture_health",
        "team_risk",
        "codebase_health",
    ]:
        val = getattr(gs, field_name, None)
        if val is not None:
            result[field_name] = val

    return result


def _convert_findings_v2(result: InsightResult) -> list[FindingRecord]:
    """Convert Finding objects to FindingRecord with v2 fields (confidence, effort, scope)."""
    records: list[FindingRecord] = []
    for f in result.findings:
        identity_key = compute_identity_key(f.finding_type, f.files)
        evidence = [
            EvidenceRecord(
                signal=e.signal,
                value=e.value,
                percentile=e.percentile,
                description=e.description,
            )
            for e in f.evidence
        ]
        records.append(
            FindingRecord(
                finding_type=f.finding_type,
                identity_key=identity_key,
                severity=f.severity,
                title=f.title,
                files=list(f.files),
                evidence=evidence,
                suggestion=f.suggestion,
                confidence=getattr(f, "confidence", 1.0),
                effort=getattr(f, "effort", "MEDIUM"),
                scope=getattr(f, "scope", "FILE"),
            )
        )
    return records


def _collect_file_signals(store: AnalysisStore) -> dict[str, dict[str, float]]:
    """Merge per-file signals from store.structural.files and store.churn.

    In v2, file_signals is replaced by signal_field. This function
    collects raw signals for backward compatibility with v1 snapshots.
    """
    merged: dict[str, dict[str, float]] = {}

    # Source 1: store.structural.files (pagerank, betweenness, etc.)
    if store.structural.available:
        structural = store.structural.value
        if structural.files:
            for filepath, fa in structural.files.items():
                if filepath not in merged:
                    merged[filepath] = {}
                sigs = merged[filepath]
                sigs["pagerank"] = fa.pagerank
                sigs["betweenness"] = fa.betweenness
                sigs["blast_radius_size"] = float(fa.blast_radius_size)
                sigs["in_degree"] = float(fa.in_degree)
                sigs["out_degree"] = float(fa.out_degree)
                sigs["compression_ratio"] = fa.compression_ratio
                sigs["nesting_depth"] = float(fa.nesting_depth)
                sigs["function_count"] = float(fa.function_count)
                sigs["lines"] = float(fa.lines)

    # Source 2 (optional): store.churn (temporal signals)
    if store.churn.available:
        for filepath, churn_series in store.churn.value.items():
            if filepath not in merged:
                merged[filepath] = {}
            sigs = merged[filepath]
            sigs["total_changes"] = float(churn_series.total_changes)
            sigs["churn_slope"] = churn_series.slope
            sigs["trajectory"] = _TRAJECTORY_MAP.get(churn_series.trajectory, 0.0)

    return merged


def _collect_codebase_signals(store: AnalysisStore) -> dict[str, float]:
    """Extract codebase-level scalar signals."""
    signals: dict[str, float] = {}

    if store.spectral.available:
        spectral = store.spectral.value
        signals["fiedler_value"] = spectral.fiedler_value
        signals["spectral_gap"] = spectral.spectral_gap
        signals["num_components"] = float(spectral.num_components)

    if store.structural.available:
        structural = store.structural.value
        signals["modularity"] = structural.modularity
        signals["total_edges"] = float(structural.total_edges)
        signals["cycle_count"] = float(structural.cycle_count)

    return signals


def _convert_findings(result: InsightResult) -> list[FindingRecord]:
    """Convert Finding objects to FindingRecord with stable identity keys."""
    records: list[FindingRecord] = []
    for f in result.findings:
        identity_key = compute_identity_key(f.finding_type, f.files)
        evidence = [
            EvidenceRecord(
                signal=e.signal,
                value=e.value,
                percentile=e.percentile,
                description=e.description,
            )
            for e in f.evidence
        ]
        records.append(
            FindingRecord(
                finding_type=f.finding_type,
                identity_key=identity_key,
                severity=f.severity,
                title=f.title,
                files=list(f.files),
                evidence=evidence,
                suggestion=f.suggestion,
            )
        )
    return records


def _collect_cochange_edges(
    store: AnalysisStore,
) -> list[tuple]:
    """Collect cochange pairs as edge tuples for Parquet emission.

    Returns list of (file_a, file_b, weight, lift, conf_ab, conf_ba, count).
    """
    edges: list[tuple] = []
    if store.cochange.available:
        matrix = store.cochange.value
        for (file_a, file_b), pair in matrix.pairs.items():
            edges.append(
                (
                    file_a,
                    file_b,
                    pair.weight,
                    pair.lift,
                    pair.confidence_a_b,
                    pair.confidence_b_a,
                    pair.cochange_count,
                )
            )
    return edges


def _collect_dependency_edges(
    store: AnalysisStore,
) -> list[tuple[str, str]]:
    """Flatten the adjacency dict into a list of (src, dst) tuples."""
    edges: list[tuple[str, str]] = []
    if store.structural.available:
        structural = store.structural.value
        if structural.graph:
            for src, dsts in structural.graph.adjacency.items():
                for dst in dsts:
                    edges.append((src, dst))
    return edges


def _get_commit_sha(repo_path: str) -> Optional[str]:
    """Retrieve the current HEAD commit SHA, or None if not a git repo."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def _compute_config_hash(settings: AnalysisSettings) -> str:
    """Compute a config hash from the settings for cache-key purposes."""
    config_dict = settings.model_dump()
    return compute_config_hash(config_dict)


def _determine_analyzers_ran(store: AnalysisStore) -> list[str]:
    """Determine which analyzer categories actually ran from the store."""
    ran: list[str] = []
    if "structural" in store.available:
        ran.append("structural")
    if "signal_field" in store.available:
        ran.append("signal_field")
    if "git_history" in store.available or "churn" in store.available:
        ran.append("temporal")
    if "spectral" in store.available:
        ran.append("spectral")
    if "semantics" in store.available:
        ran.append("semantics")
    if "architecture" in store.available:
        ran.append("architecture")
    return ran
