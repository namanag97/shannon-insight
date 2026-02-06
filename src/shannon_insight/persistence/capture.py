"""Capture an analysis snapshot from the AnalysisStore and InsightResult."""

import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .. import __version__
from ..cache import compute_config_hash
from ..config import AnalysisSettings
from ..insights.models import InsightResult
from ..insights.store import AnalysisStore
from .identity import compute_identity_key
from .models import EvidenceRecord, FindingRecord, Snapshot

# Trajectory string -> numeric encoding
_TRAJECTORY_MAP: Dict[str, float] = {
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
    """Build an immutable Snapshot from the analysis store and result.

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


# ── Private helpers ──────────────────────────────────────────────────


def _collect_file_signals(store: AnalysisStore) -> Dict[str, Dict[str, float]]:
    """Merge per-file signals from store.file_signals and store.structural.files."""
    merged: Dict[str, Dict[str, float]] = {}

    # Source 1: store.file_signals (cognitive_load, semantic_coherence, etc.)
    if store.file_signals:
        for filepath, signals in store.file_signals.items():
            merged[filepath] = dict(signals)

    # Source 2: store.structural.files (pagerank, betweenness, etc.)
    if store.structural and store.structural.files:
        for filepath, fa in store.structural.files.items():
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

    # Source 3 (optional): store.churn (temporal signals)
    if store.churn:
        for filepath, churn_series in store.churn.items():
            if filepath not in merged:
                merged[filepath] = {}
            sigs = merged[filepath]
            sigs["total_changes"] = float(churn_series.total_changes)
            sigs["churn_slope"] = churn_series.slope
            sigs["trajectory"] = _TRAJECTORY_MAP.get(churn_series.trajectory, 0.0)

    return merged


def _collect_codebase_signals(store: AnalysisStore) -> Dict[str, float]:
    """Extract codebase-level scalar signals."""
    signals: Dict[str, float] = {}

    if store.spectral:
        signals["fiedler_value"] = store.spectral.fiedler_value
        signals["spectral_gap"] = store.spectral.spectral_gap
        signals["num_components"] = float(store.spectral.num_components)

    if store.structural:
        signals["modularity"] = store.structural.modularity
        signals["total_edges"] = float(store.structural.total_edges)
        signals["cycle_count"] = float(store.structural.cycle_count)

    return signals


def _convert_findings(result: InsightResult) -> List[FindingRecord]:
    """Convert Finding objects to FindingRecord with stable identity keys."""
    records: List[FindingRecord] = []
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


def _collect_dependency_edges(
    store: AnalysisStore,
) -> List[Tuple[str, str]]:
    """Flatten the adjacency dict into a list of (src, dst) tuples."""
    edges: List[Tuple[str, str]] = []
    if store.structural and store.structural.graph:
        for src, dsts in store.structural.graph.adjacency.items():
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


def _determine_analyzers_ran(store: AnalysisStore) -> List[str]:
    """Determine which analyzer categories actually ran from the store."""
    ran: List[str] = []
    if "structural" in store.available:
        ran.append("structural")
    if "file_signals" in store.available:
        ran.append("file_signals")
    if "temporal" in store.available:
        ran.append("temporal")
    if "spectral" in store.available:
        ran.append("spectral")
    return ran
