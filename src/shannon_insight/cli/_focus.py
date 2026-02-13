"""Focus Point computation — the single most actionable file.

Theory: docs/research/OUTPUT_UX_THEORY.md

The focus point is the file with highest actionability, where:
    actionability = risk x impact x tractability x confidence

This answers the question: "What single file should I look at first?"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..insights.models import Finding
    from ..persistence.models import TensorSnapshot


@dataclass
class FocusPoint:
    """The single most actionable file in the codebase."""

    path: str
    actionability: float  # 0.0 - 1.0 combined score
    rank: int  # 1 = focus point, 2+ = alternatives

    # Contributing factors (for "why" explanation)
    risk_score: float
    impact_score: float
    tractability_score: float
    confidence_score: float

    # Raw signals for display
    pagerank: float
    blast_radius: int
    total_changes: int
    finding_count: int
    lines: int
    churn_cv: float

    # Findings on this file (for "what" explanation)
    findings: list[Finding]

    def why_summary(self) -> str:
        """One-line explanation of why this is the focus point."""
        reasons = []

        if self.pagerank > 0.1:
            reasons.append(f"{self.blast_radius} dependents")
        if self.total_changes > 20:
            reasons.append(f"{self.total_changes} changes")
        if self.finding_count > 0:
            reasons.append(f"{self.finding_count} finding{'s' if self.finding_count != 1 else ''}")
        if self.churn_cv > 1.0:
            reasons.append("unstable")

        if not reasons:
            reasons.append("elevated risk signals")

        return ", ".join(reasons)


def compute_actionability(
    path: str,
    signals: dict,
    finding_count: int,
    max_pagerank: float,
    max_blast: int,
    max_changes: int,
) -> tuple[float, float, float, float, float]:
    """Compute actionability score for a file.

    Returns: (actionability, risk, impact, tractability, confidence)
    """
    # Extract signals with defaults
    risk_score = signals.get("risk_score", 0.0)
    pagerank = signals.get("pagerank", 0.0)
    blast_radius = signals.get("blast_radius_size", 0)
    total_changes = signals.get("total_changes", 0)
    is_orphan = signals.get("is_orphan", False)
    lines = signals.get("lines", 0)
    depth = signals.get("depth", 0)

    # ══════════════════════════════════════════════════════════════════════════
    # RISK: How likely is this to cause problems?
    # Combines the pre-computed risk_score with finding density
    # ══════════════════════════════════════════════════════════════════════════
    finding_factor = min(finding_count / 3, 1.0)  # 3+ findings = max
    risk = risk_score * 0.6 + finding_factor * 0.4

    # ══════════════════════════════════════════════════════════════════════════
    # IMPACT: How much does fixing this help the codebase?
    # High centrality + high blast radius = high leverage
    # ══════════════════════════════════════════════════════════════════════════
    pr_norm = pagerank / max_pagerank if max_pagerank > 0 else 0.0
    blast_norm = blast_radius / max_blast if max_blast > 0 else 0.0
    churn_norm = total_changes / max_changes if max_changes > 0 else 0.0

    # Impact is about reach: how many other files does this affect?
    # PageRank captures transitive importance, blast_radius is direct
    impact = pr_norm * 0.5 + blast_norm * 0.3 + churn_norm * 0.2

    # ══════════════════════════════════════════════════════════════════════════
    # TRACTABILITY: Can a developer actually do something?
    # Penalize files that are hard to change or might be intentionally isolated
    # ══════════════════════════════════════════════════════════════════════════
    tractability = 1.0

    if is_orphan:
        # Orphans might be intentional (scripts, tests, entry points)
        tractability *= 0.6

    if lines > 1000:
        # Very large files are harder to refactor safely
        tractability *= 0.85
    elif lines > 500:
        tractability *= 0.95

    if depth == 0 and blast_radius == 0:
        # Entry points with no dependents - less leverage
        tractability *= 0.8

    # ══════════════════════════════════════════════════════════════════════════
    # CONFIDENCE: How reliable is our measurement?
    # Penalize files where we have incomplete data
    # ══════════════════════════════════════════════════════════════════════════
    confidence = 1.0

    if total_changes == 0:
        # No git history = no temporal signals
        confidence *= 0.75

    if pagerank == 0 and blast_radius == 0:
        # Not in dependency graph = structural signals unreliable
        confidence *= 0.8

    # ══════════════════════════════════════════════════════════════════════════
    # COMBINED ACTIONABILITY
    # Multiplicative so that zero in any dimension tanks the score
    # ══════════════════════════════════════════════════════════════════════════
    actionability = risk * impact * tractability * confidence

    return actionability, risk, impact, tractability, confidence


def identify_focus_point(
    snapshot: TensorSnapshot,
    findings: list[Finding],
    n_alternatives: int = 5,
) -> tuple[FocusPoint | None, list[FocusPoint]]:
    """Identify the focus point and alternatives.

    Args:
        snapshot: Analysis snapshot with file_signals
        findings: List of findings
        n_alternatives: Number of alternative files to return

    Returns:
        (focus_point, alternatives) where focus_point is the #1 file
        and alternatives are the next N files by actionability.
        Returns (None, []) if no actionable files found.
    """
    file_signals = snapshot.file_signals or {}
    if not file_signals:
        return None, []

    # Count and collect findings per file
    findings_per_file: dict[str, list[Finding]] = {}
    for f in findings:
        for path in f.files:
            findings_per_file.setdefault(path, []).append(f)

    # Compute normalization factors
    max_pagerank = max((s.get("pagerank", 0) for s in file_signals.values()), default=1.0) or 1.0
    max_blast = (
        max((s.get("blast_radius_size", 0) for s in file_signals.values()), default=50) or 50
    )
    max_changes = (
        max((s.get("total_changes", 0) for s in file_signals.values()), default=100) or 100
    )

    # Score all files
    scored: list[tuple[str, float, float, float, float, float, dict]] = []

    for path, signals in file_signals.items():
        finding_count = len(findings_per_file.get(path, []))

        actionability, risk, impact, tractability, confidence = compute_actionability(
            path=path,
            signals=signals,
            finding_count=finding_count,
            max_pagerank=max_pagerank,
            max_blast=max_blast,
            max_changes=max_changes,
        )

        # Filter out zero-actionability files
        if actionability > 0.001:
            scored.append((path, actionability, risk, impact, tractability, confidence, signals))

    if not scored:
        return None, []

    # Sort by actionability descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Build FocusPoint objects
    def make_focus_point(rank: int, item: tuple) -> FocusPoint:
        path, actionability, risk, impact, tractability, confidence, signals = item
        return FocusPoint(
            path=path,
            actionability=actionability,
            rank=rank,
            risk_score=risk,
            impact_score=impact,
            tractability_score=tractability,
            confidence_score=confidence,
            pagerank=signals.get("pagerank", 0.0),
            blast_radius=signals.get("blast_radius_size", 0),
            total_changes=signals.get("total_changes", 0),
            finding_count=len(findings_per_file.get(path, [])),
            lines=signals.get("lines", 0),
            churn_cv=signals.get("churn_cv", 0.0),
            findings=findings_per_file.get(path, []),
        )

    focus = make_focus_point(1, scored[0])
    alternatives = [
        make_focus_point(i + 2, item) for i, item in enumerate(scored[1 : n_alternatives + 1])
    ]

    return focus, alternatives


def get_verdict(
    health_score: float, focus: FocusPoint | None, finding_count: int
) -> tuple[str, str]:
    """Generate the one-line verdict.

    Returns: (verdict_text, verdict_color)
    """
    if health_score >= 0.8:
        if finding_count == 0:
            return "Healthy codebase, no issues detected", "green"
        else:
            return (
                f"Healthy codebase with {finding_count} minor issue{'s' if finding_count != 1 else ''}",
                "green",
            )

    elif health_score >= 0.6:
        if focus and focus.finding_count > 0:
            return (
                f"Moderate health — {finding_count} issue{'s' if finding_count != 1 else ''} found",
                "yellow",
            )
        else:
            return "Moderate health — some risk signals elevated", "yellow"

    elif health_score >= 0.4:
        return (
            f"At risk — {finding_count} issue{'s' if finding_count != 1 else ''} need attention",
            "orange1",
        )

    else:
        return (
            f"Critical — {finding_count} issue{'s' if finding_count != 1 else ''} require immediate attention",
            "red",
        )
