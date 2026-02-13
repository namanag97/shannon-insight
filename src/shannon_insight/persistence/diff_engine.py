"""Diff engine — computes structured deltas between two Snapshots.

The algorithm works in three passes:
  1. Finding-level: match by identity_key, classify as new/resolved/worsened/improved.
  2. File-level: union of file paths, compute per-metric deltas.
  3. Codebase-level: diff each codebase signal.

V2 adds:
  - TensorSnapshot diffing with SignalDelta and trend detection
  - Finding lifecycle tracking (new/persisting/resolved/regression)
  - debt_velocity calculation

Rename-aware: an optional rename map transforms old paths before comparison
so that renamed files are matched correctly rather than appearing as
remove+add pairs.
"""

from __future__ import annotations

from typing import Any

from .diff_models import (
    FileDelta,
    FindingDelta,
    MetricDelta,
    SignalDelta,
    SnapshotDiff,
    TensorSnapshotDiff,
)
from .models import FindingRecord, Snapshot, TensorSnapshot

# ── Metric direction classification ──────────────────────────────────────────
# HIGH_IS_BAD: lower values are better
# HIGH_IS_GOOD: higher values are better
# NEUTRAL: changes have no inherent good/bad direction

_LOWER_IS_BETTER = frozenset(
    {
        "cognitive_load",
        "blast_radius_size",
        "nesting_depth",
        "cycle_count",
        "coupling",
        "total_changes",
        "churn_slope",
        # Phase 5/6 signals
        "risk_score",
        "raw_risk",
        "stub_ratio",
        "naming_drift",
        "todo_density",
        "phantom_import_count",
        "broken_call_count",
        "churn_cv",
        "fix_ratio",
        "main_seq_distance",
        "layer_violation_count",
        "coordination_cost",
        "knowledge_gini",
        "orphan_ratio",
        "phantom_ratio",
        "glue_deficit",
        "clone_ratio",
        "violation_rate",
        "team_risk",
    }
)

_HIGHER_IS_BETTER = frozenset(
    {
        "semantic_coherence",
        "fiedler_value",
        "modularity",
        "cohesion",
        "boundary_alignment",
        "spectral_gap",
        # Phase 5/6 signals
        "wiring_quality",
        "bus_factor",
        "author_entropy",
        "docstring_coverage",
        "role_consistency",
        "module_bus_factor",
        "health_score",
        "conway_alignment",
        "wiring_score",
        "architecture_health",
        "codebase_health",
    }
)

_NEUTRAL = frozenset(
    {
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
        # Non-directional signals
        "class_count",
        "max_nesting",
        "import_count",
        "concept_count",
        "concept_entropy",
        "depth",
        "community",
        "refactor_ratio",
        "impl_gini",
        "velocity",
        "mean_cognitive_load",
        "file_count",
        "abstractness",
        "instability",
        "team_size",
    }
)


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
    file_signals: dict[str, dict[str, float]],
    rename_map: dict[str, str],
) -> dict[str, dict[str, float]]:
    """Return a new file_signals dict with old paths replaced by new paths."""
    result: dict[str, dict[str, float]] = {}
    for path, signals in file_signals.items():
        new_path = rename_map.get(path, path)
        result[new_path] = signals
    return result


def _apply_renames_to_finding(
    finding: FindingRecord,
    rename_map: dict[str, str],
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
    old_findings: list[FindingRecord],
    new_findings: list[FindingRecord],
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
    worsened: list[FindingDelta] = []
    improved: list[FindingDelta] = []

    for key in sorted(old_keys & new_keys):
        old_f = old_by_key[key]
        new_f = new_by_key[key]
        sev_delta = new_f.severity - old_f.severity

        if sev_delta > severity_threshold:
            worsened.append(
                FindingDelta(
                    status="worsened",
                    finding=new_f,
                    old_severity=old_f.severity,
                    new_severity=new_f.severity,
                    severity_delta=sev_delta,
                )
            )
        elif sev_delta < -severity_threshold:
            improved.append(
                FindingDelta(
                    status="improved",
                    finding=new_f,
                    old_severity=old_f.severity,
                    new_severity=new_f.severity,
                    severity_delta=sev_delta,
                )
            )

    return only_new, only_old, worsened, improved


def _diff_file_signals(
    old_signals: dict[str, dict[str, float]],
    new_signals: dict[str, dict[str, float]],
    metric_threshold: float,
) -> list[FileDelta]:
    """Compute per-file metric deltas across the union of file paths."""
    old_files = set(old_signals.keys())
    new_files = set(new_signals.keys())
    all_files = sorted(old_files | new_files)

    deltas: list[FileDelta] = []

    for filepath in all_files:
        in_old = filepath in old_files
        in_new = filepath in new_files

        if in_old and in_new:
            # File exists in both — compute per-metric deltas
            old_m = old_signals[filepath]
            new_m = new_signals[filepath]
            all_metrics = sorted(set(old_m.keys()) | set(new_m.keys()))

            metric_deltas: dict[str, MetricDelta] = {}
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
                deltas.append(
                    FileDelta(
                        filepath=filepath,
                        status="changed",
                        metric_deltas=metric_deltas,
                    )
                )
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
            deltas.append(
                FileDelta(
                    filepath=filepath,
                    status="new",
                    metric_deltas=metric_deltas,
                )
            )

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
            deltas.append(
                FileDelta(
                    filepath=filepath,
                    status="removed",
                    metric_deltas=metric_deltas,
                )
            )

    return deltas


def _diff_codebase_signals(
    old_signals: dict[str, float],
    new_signals: dict[str, float],
) -> dict[str, MetricDelta]:
    """Diff codebase-level aggregate signals."""
    all_metrics = sorted(set(old_signals.keys()) | set(new_signals.keys()))
    deltas: dict[str, MetricDelta] = {}

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
    old: Snapshot | TensorSnapshot,
    new: Snapshot | TensorSnapshot,
    renames: dict[str, str] | None = None,
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
            old.file_signals,
            rename_map,
        )
        old_findings = [_apply_renames_to_finding(f, rename_map) for f in old.findings]
    else:
        old_file_signals = old.file_signals
        old_findings = old.findings

    # ── Step 1: Finding-level diff ───────────────────────────────────────
    new_f, resolved_f, worsened_f, improved_f = _diff_findings(
        old_findings,
        new.findings,
    )

    # ── Step 2: File-level diff ──────────────────────────────────────────
    file_deltas = _diff_file_signals(
        old_file_signals,
        new.file_signals,
        metric_threshold,
    )

    # ── Step 3: Codebase-level diff ──────────────────────────────────────
    # Handle both v1 (codebase_signals) and v2 (global_signals) snapshots
    old_codebase = getattr(old, "codebase_signals", None) or getattr(old, "global_signals", {})
    new_codebase = getattr(new, "codebase_signals", None) or getattr(new, "global_signals", {})
    codebase_deltas = _diff_codebase_signals(old_codebase, new_codebase)

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


# ── TensorSnapshot Diff (V2) ─────────────────────────────────────────────────


def _classify_trend(signal: str, delta: float, threshold: float = 0.001) -> str:
    """Classify a signal delta as improving, stable, or worsening.

    Based on signal polarity from the registry.
    """
    if abs(delta) < threshold:
        return "stable"

    if signal in _LOWER_IS_BETTER:
        return "improving" if delta < 0 else "worsening"
    elif signal in _HIGHER_IS_BETTER:
        return "improving" if delta > 0 else "worsening"
    else:
        # Neutral signals: just report direction
        return "stable"


def _diff_signal_dicts(
    old_signals: dict[str, Any],
    new_signals: dict[str, Any],
    threshold: float = 0.001,
) -> list[SignalDelta]:
    """Compute SignalDeltas between two signal dicts."""
    deltas: list[SignalDelta] = []
    all_signals = sorted(set(old_signals.keys()) | set(new_signals.keys()))

    for signal in all_signals:
        # Skip non-numeric values
        old_val = old_signals.get(signal)
        new_val = new_signals.get(signal)

        if old_val is None or new_val is None:
            continue
        if not isinstance(old_val, (int, float)) or not isinstance(new_val, (int, float)):
            continue

        delta = float(new_val) - float(old_val)
        if abs(delta) > threshold:
            deltas.append(
                SignalDelta(
                    signal_name=signal,
                    old_value=float(old_val),
                    new_value=float(new_val),
                    delta=delta,
                    trend=_classify_trend(signal, delta, threshold),
                )
            )

    return deltas


def _classify_file_health(deltas: list[SignalDelta]) -> str:
    """Classify overall file health change based on signal deltas."""
    improving = sum(1 for d in deltas if d.trend == "improving")
    worsening = sum(1 for d in deltas if d.trend == "worsening")

    if improving > worsening:
        return "improving"
    elif worsening > improving:
        return "worsening"
    else:
        return "stable"


def _diff_tensor_findings(
    old_findings: list[FindingRecord],
    new_findings: list[FindingRecord],
    finding_lifecycle: dict[str, dict] | None = None,
) -> tuple[list[FindingDelta], list[FindingRecord], list[FindingRecord]]:
    """Match findings by identity_key and classify lifecycle.

    Returns:
        (all_deltas, new_list, resolved_list)
    """
    old_by_key = {f.identity_key: f for f in old_findings}
    new_by_key = {f.identity_key: f for f in new_findings}

    old_keys = set(old_by_key.keys())
    new_keys = set(new_by_key.keys())

    deltas: list[FindingDelta] = []
    new_list: list[FindingRecord] = []
    resolved_list: list[FindingRecord] = []

    # New findings (only in new snapshot)
    for key in sorted(new_keys - old_keys):
        finding = new_by_key[key]
        # Check if this is a regression (was resolved before)
        lifecycle = finding_lifecycle.get(key, {}) if finding_lifecycle else {}
        was_resolved = lifecycle.get("current_status") == "resolved"

        status = "regression" if was_resolved else "new"
        new_list.append(finding)
        deltas.append(
            FindingDelta(
                status=status,
                finding=finding,
                old_severity=None,
                new_severity=finding.severity,
                severity_delta=None,
                persistence_count=lifecycle.get("persistence_count", 0) + 1,
            )
        )

    # Resolved findings (only in old snapshot)
    for key in sorted(old_keys - new_keys):
        finding = old_by_key[key]
        resolved_list.append(finding)
        deltas.append(
            FindingDelta(
                status="resolved",
                finding=finding,
                old_severity=finding.severity,
                new_severity=None,
                severity_delta=None,
            )
        )

    # Persisting findings (in both snapshots)
    for key in sorted(old_keys & new_keys):
        old_f = old_by_key[key]
        new_f = new_by_key[key]
        sev_delta = new_f.severity - old_f.severity

        lifecycle = finding_lifecycle.get(key, {}) if finding_lifecycle else {}
        persistence = lifecycle.get("persistence_count", 1) + 1

        if abs(sev_delta) > 0.01:
            status = "worsened" if sev_delta > 0 else "improved"
        else:
            status = "persisting"

        deltas.append(
            FindingDelta(
                status=status,
                finding=new_f,
                old_severity=old_f.severity,
                new_severity=new_f.severity,
                severity_delta=sev_delta,
                persistence_count=persistence,
            )
        )

    return deltas, new_list, resolved_list


def diff_tensor_snapshots(
    old: TensorSnapshot,
    new: TensorSnapshot,
    renames: dict[str, str] | None = None,
    finding_lifecycle: dict[str, dict] | None = None,
    metric_threshold: float = 0.01,
) -> TensorSnapshotDiff:
    """Compute a structured diff between two TensorSnapshots.

    Args:
        old: The earlier snapshot (baseline or previous run).
        new: The later snapshot (current run).
        renames: Optional mapping of {old_path: new_path} for renamed files.
        finding_lifecycle: Optional dict of identity_key -> lifecycle data from DB.
        metric_threshold: Minimum absolute delta for a signal to be included.

    Returns:
        A TensorSnapshotDiff with signal deltas, finding lifecycle, and summary.
    """
    rename_map = renames or {}
    rename_pairs = sorted(rename_map.items())

    # Apply renames to old snapshot paths
    old_file_signals = {
        rename_map.get(path, path): signals for path, signals in old.file_signals.items()
    }

    # Compute file additions/removals
    old_files = set(old_file_signals.keys())
    new_files = set(new.file_signals.keys())
    files_added = sorted(new_files - old_files)
    files_removed = sorted(old_files - new_files)

    # Compute per-file signal deltas
    signal_deltas: dict[str, list[SignalDelta]] = {}
    improving_files: list[str] = []
    worsening_files: list[str] = []

    for filepath in sorted(old_files & new_files):
        old_sigs = old_file_signals.get(filepath, {})
        new_sigs = new.file_signals.get(filepath, {})
        deltas = _diff_signal_dicts(old_sigs, new_sigs, metric_threshold)
        if deltas:
            signal_deltas[filepath] = deltas
            health = _classify_file_health(deltas)
            if health == "improving":
                improving_files.append(filepath)
            elif health == "worsening":
                worsening_files.append(filepath)

    # Compute per-module signal deltas
    module_deltas: dict[str, list[SignalDelta]] = {}
    old_modules = set(old.module_signals.keys())
    new_modules = set(new.module_signals.keys())

    for module in sorted(old_modules & new_modules):
        old_sigs = old.module_signals.get(module, {})
        new_sigs = new.module_signals.get(module, {})
        deltas = _diff_signal_dicts(old_sigs, new_sigs, metric_threshold)
        if deltas:
            module_deltas[module] = deltas

    # Compute global signal deltas
    global_deltas = _diff_signal_dicts(old.global_signals, new.global_signals, metric_threshold)

    # Compute finding lifecycle
    finding_deltas, new_findings, resolved_findings = _diff_tensor_findings(
        old.findings, new.findings, finding_lifecycle
    )

    # Calculate debt_velocity
    debt_velocity = len(new_findings) - len(resolved_findings)

    # Also compute V1-compatible file_deltas and codebase_deltas
    file_deltas = _diff_file_signals(
        old_file_signals,
        new.file_signals,
        metric_threshold,
    )
    codebase_deltas = _diff_codebase_signals(
        old.global_signals,
        new.global_signals,
    )

    return TensorSnapshotDiff(
        old_commit=old.commit_sha,
        new_commit=new.commit_sha,
        old_timestamp=old.timestamp,
        new_timestamp=new.timestamp,
        files_added=files_added,
        files_removed=files_removed,
        signal_deltas=signal_deltas,
        module_deltas=module_deltas,
        global_deltas=global_deltas,
        finding_deltas=finding_deltas,
        debt_velocity=debt_velocity,
        improving_files=improving_files,
        worsening_files=worsening_files,
        new_findings=new_findings,
        resolved_findings=resolved_findings,
        file_deltas=file_deltas,
        codebase_deltas=codebase_deltas,
        renames=rename_pairs,
    )
