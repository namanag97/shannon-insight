"""Diff engine — computes structured deltas between two Snapshots.

The algorithm works in three passes:
  1. Finding-level: match by identity_key, classify as new/resolved/worsened/improved.
  2. File-level: union of file paths, compute per-metric deltas.
  3. Codebase-level: diff each codebase signal.

Rename-aware: an optional rename map transforms old paths before comparison
so that renamed files are matched correctly rather than appearing as
remove+add pairs.
"""

import copy
from typing import Dict, List, Optional

from ..snapshot.models import FindingRecord, Snapshot
from .models import FileDelta, FindingDelta, MetricDelta, SnapshotDiff

# ── Metric direction classification ──────────────────────────────────────────

_LOWER_IS_BETTER = frozenset({
    "cognitive_load",
    "blast_radius_size",
    "nesting_depth",
    "cycle_count",
    "coupling",
    "total_changes",
    "churn_slope",
})

_HIGHER_IS_BETTER = frozenset({
    "semantic_coherence",
    "fiedler_value",
    "modularity",
    "cohesion",
    "boundary_alignment",
    "spectral_gap",
})

_NEUTRAL = frozenset({
    "pagerank",
    "betweenness",
    "in_degree",
    "out_degree",
    "structural_entropy",
    "network_centrality",
    "churn_volatility",
    "lines",
    "function_count",
    "compression_ratio",
})


def _classify_direction(metric: str, delta: float) -> str:
    """Return 'better', 'worse', or 'neutral' for a given metric delta.

    Direction is determined by whether the metric belongs to the
    lower-is-better, higher-is-better, or neutral set.  Unknown
    metrics default to 'neutral'.
    """
    if abs(delta) < 0.001:
        return "neutral"
    if metric in _LOWER_IS_BETTER:
        return "better" if delta < 0 else "worse"
    if metric in _HIGHER_IS_BETTER:
        return "better" if delta > 0 else "worse"
    return "neutral"


# ── Rename helpers ───────────────────────────────────────────────────────────

def _apply_renames_to_file_signals(
    file_signals: Dict[str, Dict[str, float]],
    rename_map: Dict[str, str],
) -> Dict[str, Dict[str, float]]:
    """Return a new file_signals dict with old paths replaced by new paths."""
    result: Dict[str, Dict[str, float]] = {}
    for path, signals in file_signals.items():
        new_path = rename_map.get(path, path)
        result[new_path] = signals
    return result


def _apply_renames_to_finding(
    finding: FindingRecord,
    rename_map: Dict[str, str],
) -> FindingRecord:
    """Return a copy of the finding with file paths updated via rename_map."""
    new_files = [rename_map.get(f, f) for f in finding.files]
    return FindingRecord(
        finding_type=finding.finding_type,
        identity_key=finding.identity_key,
        severity=finding.severity,
        title=finding.title,
        files=new_files,
        evidence=list(finding.evidence),
        suggestion=finding.suggestion,
    )


# ── Core diff logic ─────────────────────────────────────────────────────────

def _diff_findings(
    old_findings: List[FindingRecord],
    new_findings: List[FindingRecord],
    severity_threshold: float = 0.01,
) -> tuple:
    """Match findings by identity_key and classify changes.

    Returns:
        (new_list, resolved_list, worsened_list, improved_list)
    """
    old_by_key = {f.identity_key: f for f in old_findings}
    new_by_key = {f.identity_key: f for f in new_findings}

    old_keys = set(old_by_key.keys())
    new_keys = set(new_by_key.keys())

    # Findings that only exist in the new snapshot
    only_new = [new_by_key[k] for k in sorted(new_keys - old_keys)]

    # Findings that only existed in the old snapshot (now resolved)
    only_old = [old_by_key[k] for k in sorted(old_keys - new_keys)]

    # Findings in both — check for severity changes
    worsened: List[FindingDelta] = []
    improved: List[FindingDelta] = []

    for key in sorted(old_keys & new_keys):
        old_f = old_by_key[key]
        new_f = new_by_key[key]
        sev_delta = new_f.severity - old_f.severity

        if sev_delta > severity_threshold:
            worsened.append(FindingDelta(
                status="worsened",
                finding=new_f,
                old_severity=old_f.severity,
                new_severity=new_f.severity,
                severity_delta=sev_delta,
            ))
        elif sev_delta < -severity_threshold:
            improved.append(FindingDelta(
                status="improved",
                finding=new_f,
                old_severity=old_f.severity,
                new_severity=new_f.severity,
                severity_delta=sev_delta,
            ))

    return only_new, only_old, worsened, improved


def _diff_file_signals(
    old_signals: Dict[str, Dict[str, float]],
    new_signals: Dict[str, Dict[str, float]],
    metric_threshold: float,
) -> List[FileDelta]:
    """Compute per-file metric deltas across the union of file paths."""
    old_files = set(old_signals.keys())
    new_files = set(new_signals.keys())
    all_files = sorted(old_files | new_files)

    deltas: List[FileDelta] = []

    for filepath in all_files:
        in_old = filepath in old_files
        in_new = filepath in new_files

        if in_old and in_new:
            # File exists in both — compute per-metric deltas
            old_m = old_signals[filepath]
            new_m = new_signals[filepath]
            all_metrics = sorted(set(old_m.keys()) | set(new_m.keys()))

            metric_deltas: Dict[str, MetricDelta] = {}
            for metric in all_metrics:
                old_val = old_m.get(metric, 0.0)
                new_val = new_m.get(metric, 0.0)
                delta = new_val - old_val

                if abs(delta) > metric_threshold:
                    metric_deltas[metric] = MetricDelta(
                        old_value=old_val,
                        new_value=new_val,
                        delta=delta,
                        direction=_classify_direction(metric, delta),
                    )

            if metric_deltas:
                deltas.append(FileDelta(
                    filepath=filepath,
                    status="changed",
                    metric_deltas=metric_deltas,
                ))
            # else: unchanged — skip

        elif in_new and not in_old:
            # New file — include all its metrics as deltas from 0
            new_m = new_signals[filepath]
            metric_deltas = {}
            for metric, val in sorted(new_m.items()):
                metric_deltas[metric] = MetricDelta(
                    old_value=0.0,
                    new_value=val,
                    delta=val,
                    direction=_classify_direction(metric, val),
                )
            deltas.append(FileDelta(
                filepath=filepath,
                status="new",
                metric_deltas=metric_deltas,
            ))

        else:
            # Removed file — include all its metrics as deltas to 0
            old_m = old_signals[filepath]
            metric_deltas = {}
            for metric, val in sorted(old_m.items()):
                metric_deltas[metric] = MetricDelta(
                    old_value=val,
                    new_value=0.0,
                    delta=-val,
                    direction=_classify_direction(metric, -val),
                )
            deltas.append(FileDelta(
                filepath=filepath,
                status="removed",
                metric_deltas=metric_deltas,
            ))

    return deltas


def _diff_codebase_signals(
    old_signals: Dict[str, float],
    new_signals: Dict[str, float],
) -> Dict[str, MetricDelta]:
    """Diff codebase-level aggregate signals."""
    all_metrics = sorted(set(old_signals.keys()) | set(new_signals.keys()))
    deltas: Dict[str, MetricDelta] = {}

    for metric in all_metrics:
        old_val = old_signals.get(metric, 0.0)
        new_val = new_signals.get(metric, 0.0)
        delta = new_val - old_val

        deltas[metric] = MetricDelta(
            old_value=old_val,
            new_value=new_val,
            delta=delta,
            direction=_classify_direction(metric, delta),
        )

    return deltas


# ── Public API ───────────────────────────────────────────────────────────────

def diff_snapshots(
    old: Snapshot,
    new: Snapshot,
    renames: Optional[Dict[str, str]] = None,
    metric_threshold: float = 0.01,
) -> SnapshotDiff:
    """Compute a structured diff between two analysis snapshots.

    Args:
        old: The earlier snapshot (baseline or previous run).
        new: The later snapshot (current run).
        renames: Optional mapping of {old_path: new_path} for renamed files.
                 If provided, old paths are rewritten before comparison so
                 that renamed files are matched instead of appearing as
                 remove+add pairs.
        metric_threshold: Minimum absolute delta for a per-file metric to
                          be included.  Defaults to 0.01.

    Returns:
        A SnapshotDiff containing categorized finding deltas, per-file
        metric deltas, and codebase-level signal deltas.
    """
    rename_map = renames or {}
    rename_pairs = sorted(rename_map.items())

    # ── Step 0: Apply renames to old snapshot data ───────────────────────
    if rename_map:
        old_file_signals = _apply_renames_to_file_signals(
            old.file_signals, rename_map,
        )
        old_findings = [
            _apply_renames_to_finding(f, rename_map) for f in old.findings
        ]
    else:
        old_file_signals = old.file_signals
        old_findings = old.findings

    # ── Step 1: Finding-level diff ───────────────────────────────────────
    new_f, resolved_f, worsened_f, improved_f = _diff_findings(
        old_findings, new.findings,
    )

    # ── Step 2: File-level diff ──────────────────────────────────────────
    file_deltas = _diff_file_signals(
        old_file_signals, new.file_signals, metric_threshold,
    )

    # ── Step 3: Codebase-level diff ──────────────────────────────────────
    codebase_deltas = _diff_codebase_signals(
        old.codebase_signals, new.codebase_signals,
    )

    return SnapshotDiff(
        old_commit=old.commit_sha,
        new_commit=new.commit_sha,
        old_timestamp=old.timestamp,
        new_timestamp=new.timestamp,
        new_findings=new_f,
        resolved_findings=resolved_f,
        worsened_findings=worsened_f,
        improved_findings=improved_f,
        file_deltas=file_deltas,
        codebase_deltas=codebase_deltas,
        renames=rename_pairs,
    )
