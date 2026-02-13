"""Developer Journey — show what we actually measured, not made-up estimates.

NO fake time estimates.
NO fake health impact numbers.
NO patronizing "quick wins" language.

Just: here's what we measured, here's what looks off, you decide what to do.

When a previous snapshot is available, show trends:
- What changed since last run
- Files that improved/degraded
- New/resolved findings
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..insights.models import Finding, InsightResult
    from ..persistence.models import TensorSnapshot


def render_journey(
    result: InsightResult,
    snapshot: TensorSnapshot,
    previous_snapshot: TensorSnapshot | None = None,
) -> str:
    """Show what we actually measured, with trends if previous snapshot available."""
    lines = []

    n_files = snapshot.file_count

    lines.append("")
    lines.append(f"  {n_files} files analyzed")

    # Show comparison if previous snapshot available
    if previous_snapshot and previous_snapshot.file_count > 0:
        prev_files = previous_snapshot.file_count
        file_delta = n_files - prev_files
        if file_delta > 0:
            lines.append(f"  [dim](+{file_delta} since last run)[/dim]")
        elif file_delta < 0:
            lines.append(f"  [dim]({file_delta} since last run)[/dim]")

    lines.append("")

    # Group findings by type
    by_type: dict[str, list[Finding]] = {}
    for f in result.findings:
        by_type.setdefault(f.finding_type, []).append(f)

    if not by_type:
        lines.append("  No issues detected.")
        lines.append("")
        return "\n".join(lines)

    # Comparison with previous findings
    if previous_snapshot and previous_snapshot.findings:
        prev_by_type: dict[str, int] = {}
        for fr in previous_snapshot.findings:
            prev_by_type[fr.finding_type] = prev_by_type.get(fr.finding_type, 0) + 1

        # Calculate deltas
        total_prev = sum(prev_by_type.values())
        total_now = len(result.findings)
        delta = total_now - total_prev

        lines.append("  CHANGES SINCE LAST RUN:")
        lines.append("  " + "─" * 50)
        if delta > 0:
            lines.append(f"  [yellow]+{delta} new findings[/yellow]")
        elif delta < 0:
            lines.append(f"  [green]{delta} findings (improved)[/green]")
        else:
            lines.append("  [dim]Same number of findings[/dim]")

        # Show type-level changes
        type_changes = []
        all_types = set(by_type.keys()) | set(prev_by_type.keys())
        for ftype in sorted(all_types):
            now = len(by_type.get(ftype, []))
            prev = prev_by_type.get(ftype, 0)
            if now != prev:
                label = ftype.replace("_", " ")
                if now > prev:
                    type_changes.append(f"    [yellow]+{now - prev} {label}[/yellow]")
                else:
                    type_changes.append(f"    [green]-{prev - now} {label}[/green]")

        if type_changes:
            for tc in type_changes[:5]:
                lines.append(tc)
            if len(type_changes) > 5:
                lines.append(f"    [dim]... and {len(type_changes) - 5} more changes[/dim]")

        lines.append("")

    # Show what we found, grouped meaningfully
    lines.append("  WHAT WE FOUND:")
    lines.append("  " + "─" * 50)
    lines.append("")

    # Structural issues (things that are facts about the code)
    structural_types = [
        "god_file",
        "orphan_code",
        "phantom_imports",
        "hollow_code",
        "dead_dependency",
    ]
    structural = [(t, by_type[t]) for t in structural_types if t in by_type]

    if structural:
        lines.append("  CODE STRUCTURE:")
        for ftype, findings in structural:
            label = ftype.replace("_", " ")
            files = [f.files[0] for f in findings if f.files][:3]
            if len(findings) > 3:
                files_str = ", ".join(files) + f" (+{len(findings) - 3} more)"
            else:
                files_str = ", ".join(files) if files else "(no files)"
            lines.append(f"    {len(findings)} {label}: {files_str}")
        lines.append("")

    # Risk issues
    risk_types = ["high_risk_hub", "zone_of_pain", "layer_violation", "bug_attractor", "weak_link"]
    risk = [(t, by_type[t]) for t in risk_types if t in by_type]

    if risk:
        lines.append("  RISK:")
        for ftype, findings in risk:
            label = ftype.replace("_", " ")
            files = [f.files[0] for f in findings if f.files][:3]
            if len(findings) > 3:
                files_str = ", ".join(files) + f" (+{len(findings) - 3} more)"
            else:
                files_str = ", ".join(files) if files else "(no files)"
            lines.append(f"    {len(findings)} {label}: {files_str}")
        lines.append("")

    # Coupling issues
    coupling_types = ["hidden_coupling", "accidental_coupling", "boundary_mismatch"]
    coupling = [(t, by_type[t]) for t in coupling_types if t in by_type]

    if coupling:
        lines.append("  COUPLING:")
        for ftype, findings in coupling:
            label = ftype.replace("_", " ")
            lines.append(f"    {len(findings)} {label}")
            for f in findings[:2]:
                if len(f.files) >= 2:
                    lines.append(f"      {f.files[0]} ↔ {f.files[1]}")
                elif f.files:
                    lines.append(f"      {f.files[0]}")
        lines.append("")

    # Temporal issues
    temporal_types = ["unstable_file", "chronic_problem", "thrashing_code"]
    temporal = [(t, by_type[t]) for t in temporal_types if t in by_type]

    if temporal:
        lines.append("  CHANGE PATTERNS:")
        for ftype, findings in temporal:
            label = ftype.replace("_", " ")
            files = [f.files[0] for f in findings if f.files][:3]
            if len(findings) > 3:
                files_str = ", ".join(files) + f" (+{len(findings) - 3} more)"
            else:
                files_str = ", ".join(files) if files else "(no files)"
            lines.append(f"    {len(findings)} {label}: {files_str}")
        lines.append("")

    # Team issues
    team_types = ["knowledge_silo", "review_blindspot", "truck_factor"]
    team = [(t, by_type[t]) for t in team_types if t in by_type]

    if team:
        lines.append("  TEAM:")
        for ftype, findings in team:
            label = ftype.replace("_", " ")
            files = [f.files[0] for f in findings if f.files][:3]
            if len(findings) > 3:
                files_str = ", ".join(files) + f" (+{len(findings) - 3} more)"
            else:
                files_str = ", ".join(files) if files else "(no files)"
            lines.append(f"    {len(findings)} {label}: {files_str}")
        lines.append("")

    # Naming/organization
    naming_types = ["naming_drift", "flat_architecture", "copy_paste_clone"]
    naming = [(t, by_type[t]) for t in naming_types if t in by_type]

    if naming:
        lines.append("  ORGANIZATION:")
        for ftype, findings in naming:
            label = ftype.replace("_", " ")
            files = [f.files[0] for f in findings if f.files][:3]
            if len(findings) > 3:
                files_str = ", ".join(files) + f" (+{len(findings) - 3} more)"
            else:
                files_str = ", ".join(files) if files else "(no files)"
            lines.append(f"    {len(findings)} {label}: {files_str}")
        lines.append("")

    # Show totals
    total = len(result.findings)
    high_sev = sum(1 for f in result.findings if f.severity >= 0.8)

    lines.append("  " + "─" * 50)
    lines.append(f"  {total} total findings ({high_sev} high severity)")
    lines.append("")
    lines.append("  Run 'shannon-insight explain <file>' to see details")
    lines.append("  Run 'shannon-insight --verbose' to see all evidence")
    lines.append("")

    return "\n".join(lines)


def render_journey_json(
    result: InsightResult,
    snapshot: TensorSnapshot,
    previous_snapshot: TensorSnapshot | None = None,
) -> dict:
    """Return findings as structured JSON with optional comparison."""
    by_type: dict[str, list[dict]] = {}

    for f in result.findings:
        by_type.setdefault(f.finding_type, []).append(
            {
                "files": f.files,
                "severity": round(f.severity, 2),
                "evidence": [{"signal": e.signal, "value": round(e.value, 4)} for e in f.evidence],
            }
        )

    output = {
        "files_analyzed": snapshot.file_count,
        "total_findings": len(result.findings),
        "high_severity_count": sum(1 for f in result.findings if f.severity >= 0.8),
        "by_type": by_type,
    }

    # Add comparison data if previous snapshot available
    if previous_snapshot and previous_snapshot.findings:
        prev_by_type: dict[str, int] = {}
        for fr in previous_snapshot.findings:
            prev_by_type[fr.finding_type] = prev_by_type.get(fr.finding_type, 0) + 1

        output["comparison"] = {
            "previous_files": previous_snapshot.file_count,
            "previous_findings": len(previous_snapshot.findings),
            "findings_delta": len(result.findings) - len(previous_snapshot.findings),
            "files_delta": snapshot.file_count - previous_snapshot.file_count,
            "type_changes": {
                ftype: len(by_type.get(ftype, [])) - prev_by_type.get(ftype, 0)
                for ftype in set(by_type.keys()) | set(prev_by_type.keys())
                if len(by_type.get(ftype, [])) != prev_by_type.get(ftype, 0)
            },
        }

    return output


def get_trend_indicator(current: float, previous: float) -> str:
    """Get a trend indicator for a metric.

    Returns: "↑" (worse), "↓" (better), or "→" (stable)
    """
    if current > previous * 1.05:  # 5% threshold
        return "↑"
    elif current < previous * 0.95:
        return "↓"
    return "→"


def format_delta(current: int, previous: int) -> str:
    """Format a delta for display.

    Examples: "+5", "-3", "same"
    """
    delta = current - previous
    if delta > 0:
        return f"+{delta}"
    elif delta < 0:
        return str(delta)
    return "same"
