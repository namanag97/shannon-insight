"""Hotspot analysis and display.

Ranks files by combined churn, coupling, and centrality signals.
Shows where risk is concentrated without prescribing fixes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..insights.models import Finding
    from ..persistence.models import TensorSnapshot


@dataclass
class Hotspot:
    """A file identified as a hotspot."""

    path: str
    score: float  # 0.0 - 1.0 combined hotspot score
    rank: int  # 1-indexed rank

    # Contributing signals
    pagerank: float
    total_changes: int
    churn_cv: float
    blast_radius: int
    finding_count: int

    # Percentiles (if available)
    pagerank_pctl: float | None = None
    churn_pctl: float | None = None

    # Trend (if previous snapshot available)
    trend: str = "stable"  # "up" | "down" | "stable" | "new"
    rank_change: int = 0  # Positive = moved up (worse), negative = moved down (better)


def compute_hotspot_score(
    pagerank: float,
    total_changes: int,
    churn_cv: float,
    blast_radius: int,
    finding_count: int,
    *,
    max_pagerank: float = 1.0,
    max_changes: int = 100,
    max_blast: int = 50,
    max_findings: int = 10,
) -> float:
    """Compute a combined hotspot score from contributing signals.

    Weights:
    - PageRank: 30% (graph centrality)
    - Total changes: 25% (activity level)
    - Churn CV: 20% (instability)
    - Blast radius: 15% (downstream impact)
    - Finding count: 10% (existing issues)

    Returns score in range [0.0, 1.0].
    """
    # Normalize each component to 0-1
    pr_norm = min(pagerank / max_pagerank, 1.0) if max_pagerank > 0 else 0.0
    chg_norm = min(total_changes / max_changes, 1.0) if max_changes > 0 else 0.0
    cv_norm = min(churn_cv / 2.0, 1.0)  # CV of 2.0 = max instability
    blast_norm = min(blast_radius / max_blast, 1.0) if max_blast > 0 else 0.0
    find_norm = min(finding_count / max_findings, 1.0) if max_findings > 0 else 0.0

    # Weighted sum
    score = pr_norm * 0.30 + chg_norm * 0.25 + cv_norm * 0.20 + blast_norm * 0.15 + find_norm * 0.10

    return round(score, 4)


def identify_hotspots(
    snapshot: TensorSnapshot,
    findings: list[Finding],
    n: int = 20,
    min_score: float = 0.0,
) -> list[Hotspot]:
    """Identify the top N hotspots in the codebase.

    Args:
        snapshot: Analysis snapshot with file_signals
        findings: List of findings (used for finding_count per file)
        n: Maximum number of hotspots to return
        min_score: Minimum score to be considered a hotspot

    Returns:
        List of Hotspot objects, sorted by score descending.
    """
    file_signals = snapshot.file_signals or {}
    if not file_signals:
        return []

    # Count findings per file
    findings_per_file: dict[str, int] = {}
    for f in findings:
        for path in f.files:
            findings_per_file[path] = findings_per_file.get(path, 0) + 1

    # Compute max values for normalization
    max_pagerank = max((s.get("pagerank", 0) for s in file_signals.values()), default=1.0) or 1.0
    max_changes = (
        max((s.get("total_changes", 0) for s in file_signals.values()), default=100) or 100
    )
    max_blast = (
        max((s.get("blast_radius_size", 0) for s in file_signals.values()), default=50) or 50
    )
    max_findings = max(findings_per_file.values(), default=1) or 1

    # Score all files
    scored_files: list[tuple[str, float, dict]] = []
    for path, sig_dict in file_signals.items():
        pagerank = sig_dict.get("pagerank", 0.0)
        total_changes = sig_dict.get("total_changes", 0)
        churn_cv = sig_dict.get("churn_cv", 0.0)
        blast_radius = sig_dict.get("blast_radius_size", 0)
        finding_count = findings_per_file.get(path, 0)

        score = compute_hotspot_score(
            pagerank=pagerank,
            total_changes=total_changes,
            churn_cv=churn_cv,
            blast_radius=blast_radius,
            finding_count=finding_count,
            max_pagerank=max_pagerank,
            max_changes=max_changes,
            max_blast=max_blast,
            max_findings=max_findings,
        )

        if score >= min_score:
            scored_files.append((path, score, sig_dict))

    # Sort by score descending
    scored_files.sort(key=lambda x: x[1], reverse=True)

    # Build Hotspot objects
    hotspots = []
    for rank, (path, score, sig_dict) in enumerate(scored_files[:n], start=1):
        hotspots.append(
            Hotspot(
                path=path,
                score=score,
                rank=rank,
                pagerank=sig_dict.get("pagerank", 0.0),
                total_changes=sig_dict.get("total_changes", 0),
                churn_cv=sig_dict.get("churn_cv", 0.0),
                blast_radius=sig_dict.get("blast_radius_size", 0),
                finding_count=findings_per_file.get(path, 0),
                pagerank_pctl=sig_dict.get("percentiles", {}).get("pagerank"),
                churn_pctl=sig_dict.get("percentiles", {}).get("total_changes"),
            )
        )

    return hotspots


def compute_trends(
    current: list[Hotspot],
    previous_file_signals: dict[str, dict] | None,
) -> list[Hotspot]:
    """Update hotspots with trend information from previous snapshot.

    Args:
        current: Current hotspots
        previous_file_signals: file_signals from previous snapshot

    Returns:
        Hotspots with trend and rank_change populated.
    """
    if not previous_file_signals:
        return current

    # Compute previous scores
    prev_scores: dict[str, float] = {}
    for path, sig_dict in previous_file_signals.items():
        pagerank = sig_dict.get("pagerank", 0.0)
        total_changes = sig_dict.get("total_changes", 0)
        churn_cv = sig_dict.get("churn_cv", 0.0)
        blast_radius = sig_dict.get("blast_radius_size", 0)

        # Use default normalization for historical comparison
        score = compute_hotspot_score(
            pagerank=pagerank,
            total_changes=total_changes,
            churn_cv=churn_cv,
            blast_radius=blast_radius,
            finding_count=0,  # Don't have historical findings
        )
        prev_scores[path] = score

    # Sort previous by score to get previous ranks
    prev_ranked = sorted(prev_scores.items(), key=lambda x: x[1], reverse=True)
    prev_ranks = {path: rank for rank, (path, _) in enumerate(prev_ranked, start=1)}

    # Update current hotspots
    for hs in current:
        if hs.path in prev_scores:
            prev_rank = prev_ranks[hs.path]
            hs.rank_change = prev_rank - hs.rank  # Positive = moved up (worse)

            score_change = hs.score - prev_scores[hs.path]
            if score_change > 0.05:
                hs.trend = "up"
            elif score_change < -0.05:
                hs.trend = "down"
            else:
                hs.trend = "stable"
        else:
            hs.trend = "new"

    return current


# ══════════════════════════════════════════════════════════════════════════════
# Display Functions
# ══════════════════════════════════════════════════════════════════════════════


def format_hotspot_row(hs: Hotspot, show_trend: bool = False) -> str:
    """Format a single hotspot as a display row.

    Returns a Rich-formatted string.
    """
    # Truncate long paths
    if len(hs.path) > 35:
        display_path = "..." + hs.path[-32:]
    else:
        display_path = hs.path

    # Score color
    if hs.score >= 0.7:
        score_color = "red"
    elif hs.score >= 0.4:
        score_color = "yellow"
    else:
        score_color = "green"

    # Trend indicator
    trend_str = ""
    if show_trend:
        if hs.trend == "up":
            trend_str = " [red]↑[/red]"
        elif hs.trend == "down":
            trend_str = " [green]↓[/green]"
        elif hs.trend == "new":
            trend_str = " [cyan]new[/cyan]"
        elif hs.rank_change != 0:
            if hs.rank_change > 0:
                trend_str = f" [green]↓{hs.rank_change}[/green]"
            else:
                trend_str = f" [red]↑{-hs.rank_change}[/red]"

    findings_str = f"{hs.finding_count}" if hs.finding_count > 0 else "-"

    return (
        f"[bold]#{hs.rank:2d}[/bold]  "
        f"[cyan]{display_path:<37}[/cyan]  "
        f"[{score_color}]{hs.score:.3f}[/{score_color}]  "
        f"pr={hs.pagerank:.2f}  "
        f"chg={hs.total_changes:3d}  "
        f"cv={hs.churn_cv:.1f}  "
        f"blast={hs.blast_radius:2d}  "
        f"issues={findings_str}"
        f"{trend_str}"
    )


def render_hotspots_table(
    snapshot: TensorSnapshot,
    findings: list[Finding],
    n: int = 15,
    previous_snapshot: TensorSnapshot | None = None,
) -> str:
    """Render hotspots as a formatted table for CLI output.

    Args:
        snapshot: Current analysis snapshot
        findings: Current findings
        n: Number of hotspots to show
        previous_snapshot: Previous snapshot for trend comparison

    Returns:
        Rich-formatted string ready for console.print()
    """
    hotspots = identify_hotspots(snapshot, findings, n=n)

    if not hotspots:
        return "[dim]No hotspots identified (no files with activity)[/dim]"

    # Add trends if previous snapshot available
    show_trend = False
    if previous_snapshot and previous_snapshot.file_signals:
        hotspots = compute_trends(hotspots, previous_snapshot.file_signals)
        show_trend = True

    lines = []
    lines.append("[bold]HOTSPOTS[/bold] — files with highest combined risk signals")
    lines.append("")

    # Header
    lines.append(
        "[dim]      File                                    Score   PageRank  Churn  CV    Blast  Issues[/dim]"
    )
    lines.append("  " + "─" * 90)

    for hs in hotspots:
        lines.append("  " + format_hotspot_row(hs, show_trend=show_trend))

    lines.append("")

    # Summary
    high_risk = sum(1 for h in hotspots if h.score >= 0.7)
    med_risk = sum(1 for h in hotspots if 0.4 <= h.score < 0.7)

    if high_risk > 0:
        lines.append(
            f"[red]{high_risk}[/red] high-risk hotspots, [yellow]{med_risk}[/yellow] moderate"
        )
    elif med_risk > 0:
        lines.append(f"[yellow]{med_risk}[/yellow] moderate-risk hotspots")
    else:
        lines.append("[green]No high-risk hotspots[/green]")

    lines.append("")
    lines.append(
        "[dim]Score combines: PageRank (30%), Churn (25%), CV (20%), Blast (15%), Issues (10%)[/dim]"
    )

    return "\n".join(lines)


def get_hotspot_summary(
    snapshot: TensorSnapshot,
    findings: list[Finding],
) -> dict[str, int | float]:
    """Get summary statistics for hotspots.

    Returns dict with:
    - total_hotspots: count of files with score > 0.1
    - high_risk_count: count with score >= 0.7
    - medium_risk_count: count with score >= 0.4
    - top_hotspot_path: path of #1 hotspot
    - top_hotspot_score: score of #1 hotspot
    """
    hotspots = identify_hotspots(snapshot, findings, n=100, min_score=0.1)

    if not hotspots:
        return {
            "total_hotspots": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "top_hotspot_path": "",
            "top_hotspot_score": 0.0,
        }

    return {
        "total_hotspots": len(hotspots),
        "high_risk_count": sum(1 for h in hotspots if h.score >= 0.7),
        "medium_risk_count": sum(1 for h in hotspots if 0.4 <= h.score < 0.7),
        "top_hotspot_path": hotspots[0].path,
        "top_hotspot_score": hotspots[0].score,
    }
