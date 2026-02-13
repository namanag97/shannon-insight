"""Change-scoped analysis — focus insights on files touched by a commit or PR.

Given a set of changed files and a full-codebase Snapshot, this module
computes the *blast radius* (transitive dependents), filters findings to
those relevant to the change, and produces a risk-level assessment.
"""

import subprocess
from bisect import bisect_left
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Union

from .models import FindingRecord, Snapshot, TensorSnapshot


@dataclass
class FileRiskSummary:
    """Per-file risk summary within the change scope."""

    filepath: str
    signals: dict[str, float]
    percentiles: dict[str, float]  # percentile positions computed from all files
    dependents_count: int
    findings_count: int


@dataclass
class ChangeScopedReport:
    """Complete change-scoped risk report.

    Produced by :func:`build_scoped_report` — contains the changed files,
    their blast radius, filtered findings, per-file risk summaries, and
    an overall risk-level assessment.
    """

    changed_files: list[str]
    blast_radius_files: list[str]
    direct_findings: list[FindingRecord]  # findings where files intersect changed_files
    blast_findings: list[FindingRecord]  # findings where files intersect blast_radius
    file_risk: list[FileRiskSummary]
    risk_level: str  # "low" | "medium" | "high" | "critical"
    risk_reason: str


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def get_changed_files(repo_path: str, ref: str = "HEAD~1") -> list[str]:
    """Get files changed between *ref* and HEAD using ``git diff --name-only``.

    Parameters
    ----------
    repo_path:
        Absolute path to the git repository.
    ref:
        The git ref to diff against HEAD (e.g. ``"HEAD~1"``, a commit SHA).

    Returns
    -------
    List[str]
        Paths of changed files relative to the repository root.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--name-only", ref, "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().split("\n") if f]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def get_merge_base_files(repo_path: str, base_branch: str = "main") -> list[str]:
    """Get files changed on the current branch vs *base_branch*.

    Finds the merge-base between HEAD and *base_branch*, then returns
    the files changed from that merge-base to HEAD.

    Parameters
    ----------
    repo_path:
        Absolute path to the git repository.
    base_branch:
        The branch to compare against (default ``"main"``).

    Returns
    -------
    List[str]
        Paths of changed files relative to the repository root.
    """
    try:
        # 1. Find merge base
        mb = subprocess.run(
            ["git", "-C", repo_path, "merge-base", "HEAD", base_branch],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if mb.returncode != 0:
            return []
        merge_base = mb.stdout.strip()
        # 2. Diff from merge base to HEAD
        return get_changed_files(repo_path, merge_base)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


# ---------------------------------------------------------------------------
# Blast radius computation
# ---------------------------------------------------------------------------


def compute_blast_radius(
    changed_files: list[str], snapshot: Union[Snapshot, TensorSnapshot]
) -> list[str]:
    """Find all files transitively depending on the changed files.

    Builds a *reverse* dependency graph from ``snapshot.dependency_edges``
    (where each edge ``(A, B)`` means *A depends on B*), then performs a BFS
    from each changed file to discover all transitive dependents.

    Parameters
    ----------
    changed_files:
        Files directly modified in the change.
    snapshot:
        The full-codebase analysis snapshot.

    Returns
    -------
    List[str]
        Sorted list of affected files **excluding** the changed files
        themselves.
    """
    # Build reverse adjacency: for each file, which files depend on it?
    reverse: dict[str, set] = defaultdict(set)
    for src, dst in snapshot.dependency_edges:
        # src depends on dst  -->  dst is depended upon by src
        reverse[dst].add(src)

    affected: set = set()
    changed_set = set(changed_files)

    for f in changed_files:
        queue: deque = deque([f])
        visited = {f}
        while queue:
            node = queue.popleft()
            for dep in reverse.get(node, set()):
                if dep not in visited:
                    visited.add(dep)
                    affected.add(dep)
                    queue.append(dep)

    return sorted(affected - changed_set)


# ---------------------------------------------------------------------------
# Main report builder
# ---------------------------------------------------------------------------


def build_scoped_report(
    changed_files: list[str],
    snapshot: Union[Snapshot, TensorSnapshot],
) -> ChangeScopedReport:
    """Build a change-scoped risk report.

    Parameters
    ----------
    changed_files:
        Files directly modified in the change.
    snapshot:
        The full-codebase analysis snapshot.

    Returns
    -------
    ChangeScopedReport
        A complete risk report scoped to the change.
    """
    blast_radius = compute_blast_radius(changed_files, snapshot)
    changed_set = set(changed_files)
    blast_set = set(blast_radius)

    # ── Filter findings ───────────────────────────────────────────────
    direct_findings: list[FindingRecord] = []
    blast_findings: list[FindingRecord] = []
    for finding in snapshot.findings:
        finding_files = set(finding.files)
        if finding_files & changed_set:
            direct_findings.append(finding)
        elif finding_files & blast_set:
            blast_findings.append(finding)

    # ── Compute percentiles for all files ─────────────────────────────
    all_files_signals = snapshot.file_signals
    percentiles = _compute_file_percentiles(all_files_signals)

    # ── Build reverse graph once for dependents count ─────────────────
    reverse: dict[str, set] = defaultdict(set)
    for src, dst in snapshot.dependency_edges:
        reverse[dst].add(src)

    # ── Build per-file risk summaries for changed files ───────────────
    file_risk: list[FileRiskSummary] = []
    for fp in changed_files:
        signals = all_files_signals.get(fp, {})
        pcts = percentiles.get(fp, {})
        dep_count = len(reverse.get(fp, set()))
        f_count = sum(1 for finding in snapshot.findings if fp in finding.files)
        file_risk.append(
            FileRiskSummary(
                filepath=fp,
                signals=signals,
                percentiles=pcts,
                dependents_count=dep_count,
                findings_count=f_count,
            )
        )

    # ── Compute risk level ────────────────────────────────────────────
    risk_level, risk_reason = _compute_risk_level(changed_files, snapshot, direct_findings)

    return ChangeScopedReport(
        changed_files=changed_files,
        blast_radius_files=blast_radius,
        direct_findings=direct_findings,
        blast_findings=blast_findings,
        file_risk=file_risk,
        risk_level=risk_level,
        risk_reason=risk_reason,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _compute_file_percentiles(
    all_signals: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    """Compute percentile rank for each file on each metric.

    For every metric *m*, gather values across all files and compute
    each file's percentile as ``100 * rank / total``.

    Parameters
    ----------
    all_signals:
        Mapping of filepath -> signal_name -> value from the snapshot.

    Returns
    -------
    Dict[str, Dict[str, float]]
        Mapping of filepath -> signal_name -> percentile (0-100).
    """
    if not all_signals:
        return {}

    # Gather all numeric metric names (skip dicts, strings, bools)
    metrics: set = set()
    for sigs in all_signals.values():
        for k, v in sigs.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                metrics.add(k)

    # For each metric, build a sorted list of values
    metric_sorted: dict[str, list[float]] = {}
    for m in metrics:
        raw_vals: list[float] = []
        for sigs in all_signals.values():
            v = sigs.get(m)
            if v is not None and isinstance(v, (int, float)) and not isinstance(v, bool):
                raw_vals.append(float(v))
        raw_vals.sort()
        metric_sorted[m] = raw_vals

    # Compute percentiles per file
    result: dict[str, dict[str, float]] = {}
    for fp, sigs in all_signals.items():
        pcts: dict[str, float] = {}
        for m, v in sigs.items():
            # Skip non-numeric values
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            sorted_vals = metric_sorted.get(m, [])
            if sorted_vals:
                rank = bisect_left(sorted_vals, v)
                pcts[m] = 100.0 * rank / len(sorted_vals)
            else:
                pcts[m] = 0.0
        result[fp] = pcts

    return result


def _compute_risk_level(
    changed_files: list[str],
    snapshot: Union[Snapshot, TensorSnapshot],
    direct_findings: list[FindingRecord],
) -> tuple[str, str]:
    """Compute an overall risk level for the change.

    Heuristic tiers:
      - **critical** — a changed file is a high-risk hub with severity > 0.8.
      - **high** — cumulative finding severity > 1.5 or blast radius > 30%
        of the codebase.
      - **medium** — at least one finding involves a changed file.
      - **low** — no findings involve changed files.

    Parameters
    ----------
    changed_files:
        Files directly modified.
    snapshot:
        The full-codebase analysis snapshot.
    direct_findings:
        Findings whose files intersect the changed files.

    Returns
    -------
    Tuple[str, str]
        ``(risk_level, risk_reason)`` pair.
    """
    if not direct_findings:
        return "low", "No findings involve changed files"

    # Check for critical: changed file is a high-risk hub with high severity
    for finding in direct_findings:
        if finding.finding_type == "high_risk_hub" and finding.severity > 0.8:
            primary_file = finding.files[0] if finding.files else "unknown"
            return (
                "critical",
                f"Changed file {primary_file} is a high-risk hub (severity {finding.severity:.2f})",
            )

    # Check severity sum and blast radius percentage
    severity_sum = sum(f.severity for f in direct_findings)
    blast = compute_blast_radius(changed_files, snapshot)
    total_files = snapshot.file_count or 1
    blast_pct = len(blast) / total_files

    if severity_sum > 1.5 or blast_pct > 0.3:
        reason_parts: list[str] = []
        if severity_sum > 1.5:
            reason_parts.append(f"finding severity sum {severity_sum:.2f}")
        if blast_pct > 0.3:
            reason_parts.append(f"blast radius {len(blast)} files ({blast_pct:.0%} of codebase)")
        return "high", " and ".join(reason_parts)

    return "medium", f"{len(direct_findings)} finding(s) involve changed files"
