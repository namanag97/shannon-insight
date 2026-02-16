"""Self-diagnostic mode: detect analysis quality issues.

Reports uninformative signals, noisy finders, and data quality problems.
Outputs as DiagnosticReport when --verbose is enabled.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Finding
    from .store import AnalysisStore


@dataclass
class DiagnosticIssue:
    """A detected quality issue in the analysis."""

    category: str  # "signal" | "finder" | "data" | "team"
    severity: str  # "info" | "warning"
    message: str
    detail: str = ""


@dataclass
class DiagnosticReport:
    """Summary of analysis quality issues."""

    issues: list[DiagnosticIssue] = field(default_factory=list)
    signal_information_gains: dict[str, float] = field(default_factory=dict)
    total_files: int = 0
    total_findings: int = 0

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def summary(self) -> str:
        if not self.issues:
            return "No analysis quality issues detected."
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        infos = sum(1 for i in self.issues if i.severity == "info")
        parts = []
        if warnings:
            parts.append(f"{warnings} warning(s)")
        if infos:
            parts.append(f"{infos} info(s)")
        return f"Analysis quality: {', '.join(parts)}"


def run_diagnostics(
    store: AnalysisStore,
    findings: list[Finding],
) -> DiagnosticReport:
    """Run all diagnostic checks on the analysis output.

    Args:
        store: The analysis store after all analyzers have run
        findings: All findings produced by finders

    Returns:
        DiagnosticReport with detected issues
    """
    report = DiagnosticReport(
        total_files=store.file_count,
        total_findings=len(findings),
    )

    _check_concept_quality(store, report)
    _check_cochange_noise(store, report)
    _check_team_size(store, report)
    _check_finder_noise(findings, report)
    _check_signal_information_gain(store, report)
    _check_codebase_size(store, report)
    _check_git_history_depth(store, report)
    _check_orphan_ratio(store, report)

    return report


def _check_concept_quality(store: AnalysisStore, report: DiagnosticReport) -> None:
    """Check if concept extraction is producing useful data."""
    if not store.semantics.available:
        return

    semantics = store.semantics.value
    if not semantics:
        return

    low_concept_count = sum(
        1 for sem in semantics.values() if hasattr(sem, "concept_count") and sem.concept_count <= 1
    )
    total = len(semantics)
    pct = low_concept_count / total if total > 0 else 0

    if pct > 0.5:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="warning",
                message=f"Concept extraction quality low: {low_concept_count}/{total} files ({pct:.0%}) have <= 1 concept",
                detail="ACCIDENTAL_COUPLING findings may be unreliable. Consider improving naming or file organization.",
            )
        )


def _check_cochange_noise(store: AnalysisStore, report: DiagnosticReport) -> None:
    """Check if co-change data is noisy from bulk commits."""
    if not store.git_history.available:
        return

    git = store.git_history.value
    if not git.commits:
        return

    large_commits = sum(1 for c in git.commits if len(c.files) > 30)
    total = len(git.commits)
    pct = large_commits / total if total > 0 else 0

    if pct > 0.2:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="warning",
                message=f"Co-change data noisy: {large_commits}/{total} commits ({pct:.0%}) touch > 30 files",
                detail="Bulk refactors or renames inflate co-change signal. Consider using --since to limit history.",
            )
        )


def _check_team_size(store: AnalysisStore, report: DiagnosticReport) -> None:
    """Check if team-based findings make sense."""
    if not store.signal_field.available:
        return

    field = store.signal_field.value
    if field.global_signals.team_size <= 1:
        report.issues.append(
            DiagnosticIssue(
                category="team",
                severity="info",
                message="Solo project: team-based findings disabled",
                detail="KNOWLEDGE_SILO, REVIEW_BLINDSPOT, CONWAY_VIOLATION skipped for solo projects.",
            )
        )


def _check_finder_noise(findings: list[Finding], report: DiagnosticReport) -> None:
    """Check if any single finder produces > 30% of findings."""
    if not findings:
        return

    counts = Counter(f.finding_type for f in findings)
    total = len(findings)

    for ftype, count in counts.most_common():
        pct = count / total
        if pct > 0.3:
            report.issues.append(
                DiagnosticIssue(
                    category="finder",
                    severity="warning",
                    message=f"Finder '{ftype}' is noisy: {count}/{total} findings ({pct:.0%})",
                    detail="This finder dominates output. Consider adjusting thresholds or investigating root cause.",
                )
            )


def _check_signal_information_gain(store: AnalysisStore, report: DiagnosticReport) -> None:
    """Compute information gain for key signals.

    IG(S) = H(risk) - H(risk|S)
    If a signal has the same value for all files, its IG = 0.
    """
    if not store.signal_field.available:
        return

    field = store.signal_field.value
    if not field.per_file:
        return

    # Signals to check
    signals_to_check = ["bus_factor", "cognitive_load", "pagerank", "churn_cv"]

    for signal_name in signals_to_check:
        values = []
        for fs in field.per_file.values():
            val = getattr(fs, signal_name, None)
            if val is not None:
                values.append(float(val))

        if not values:
            continue

        # Check if signal is constant (zero information)
        unique_vals = {round(v, 4) for v in values}
        if len(unique_vals) <= 1:
            ig = 0.0
            report.signal_information_gains[signal_name] = ig
            report.issues.append(
                DiagnosticIssue(
                    category="signal",
                    severity="info",
                    message=f"Signal '{signal_name}' carries zero information (constant = {values[0]:.2f})",
                    detail="This signal does not differentiate files. Consider if the data source is available.",
                )
            )
        else:
            # Estimate IG via entropy of binned distribution
            ig = _estimate_information_gain(values)
            report.signal_information_gains[signal_name] = ig


def _estimate_information_gain(values: list[float]) -> float:
    """Estimate information gain via binned entropy reduction.

    Simple approach: bin values into 5 bins and compute entropy.
    """
    if not values:
        return 0.0

    # Bin into 5 equal-width bins
    min_val = min(values)
    max_val = max(values)
    if min_val == max_val:
        return 0.0

    n_bins = 5
    bin_width = (max_val - min_val) / n_bins
    bins = [0] * n_bins
    for v in values:
        idx = min(int((v - min_val) / bin_width), n_bins - 1)
        bins[idx] += 1

    # Compute entropy
    n = len(values)
    entropy = 0.0
    for count in bins:
        if count > 0:
            p = count / n
            entropy -= p * math.log2(p)

    return entropy


def _check_codebase_size(store: AnalysisStore, report: DiagnosticReport) -> None:
    """Check if codebase is large enough for meaningful analysis."""
    n_files = store.file_count

    if n_files < 3:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="warning",
                message=f"Very small codebase ({n_files} files): limited analysis value",
                detail="Most finders need 5+ files to produce meaningful findings.",
            )
        )
    elif n_files < 15:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="info",
                message=f"Small codebase ({n_files} files): using ABSOLUTE tier (no percentiles)",
                detail="Percentile-based findings disabled. Architecture-level findings may be limited.",
            )
        )


def _check_git_history_depth(store: AnalysisStore, report: DiagnosticReport) -> None:
    """Check if git history is deep enough for temporal analysis."""
    if not store.git_history.available:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="warning",
                message="No git history available: temporal analysis disabled",
                detail="Churn, bus_factor, co-change findings will not be produced.",
            )
        )
        return

    git = store.git_history.value
    if git.total_commits < 50:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="info",
                message=f"Shallow git history ({git.total_commits} commits): temporal signals may be noisy",
                detail="Consider using --since to focus on recent history if available.",
            )
        )

    # Check if history spans enough time
    if git.span_days < 30:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="info",
                message=f"Short history span ({git.span_days} days): churn trajectory unreliable",
                detail="Churn classification needs 30+ days to detect STABILIZING vs CHURNING.",
            )
        )


def _check_orphan_ratio(store: AnalysisStore, report: DiagnosticReport) -> None:
    """Check if too many files are orphans (possible resolution issues)."""
    if not store.signal_field.available:
        return

    field = store.signal_field.value
    if not field.per_file:
        return

    orphan_count = sum(1 for fs in field.per_file.values() if fs.is_orphan)
    total = len(field.per_file)
    ratio = orphan_count / total if total > 0 else 0

    if ratio > 0.5:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="warning",
                message=f"High orphan ratio ({orphan_count}/{total} = {ratio:.0%}): possible import resolution issues",
                detail="Check if imports use dynamic paths, aliases, or non-standard patterns.",
            )
        )
    elif ratio > 0.3:
        report.issues.append(
            DiagnosticIssue(
                category="data",
                severity="info",
                message=f"Many orphan files ({orphan_count}/{total} = {ratio:.0%})",
                detail="These files have no importers. May be entry points, utilities, or dead code.",
            )
        )
