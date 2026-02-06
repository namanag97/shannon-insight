"""Scoped analysis output (--changed / --since)."""

import json

from ..insights import InsightResult
from ..persistence.models import FindingRecord
from ..persistence.scope import ChangeScopedReport
from ._common import console

_RISK_COLORS = {
    "low": "green",
    "medium": "yellow",
    "high": "red",
    "critical": "bold red",
}


def _output_scoped_json(report: ChangeScopedReport, result: InsightResult):
    """Machine-readable JSON output for a change-scoped report."""
    summary = result.store_summary
    output = {
        "mode": "scoped",
        "summary": {
            "total_files": summary.total_files,
            "total_modules": summary.total_modules,
            "commits_analyzed": summary.commits_analyzed,
            "git_available": summary.git_available,
            "fiedler_value": (
                round(summary.fiedler_value, 4) if summary.fiedler_value is not None else None
            ),
            "signals_available": summary.signals_available,
        },
        "scope": {
            "changed_files": report.changed_files,
            "blast_radius_files": report.blast_radius_files,
            "blast_radius_count": len(report.blast_radius_files),
            "risk_level": report.risk_level,
            "risk_reason": report.risk_reason,
        },
        "direct_findings": [_finding_record_to_dict(f) for f in report.direct_findings],
        "blast_findings": [_finding_record_to_dict(f) for f in report.blast_findings],
        "file_risk": [
            {
                "filepath": fr.filepath,
                "signals": {k: round(v, 4) for k, v in fr.signals.items()},
                "percentiles": {k: round(v, 1) for k, v in fr.percentiles.items()},
                "dependents_count": fr.dependents_count,
                "findings_count": fr.findings_count,
            }
            for fr in report.file_risk
        ],
    }
    print(json.dumps(output, indent=2))


def _finding_record_to_dict(f: FindingRecord) -> dict:
    """Convert a FindingRecord to a JSON-serializable dict."""
    return {
        "type": f.finding_type,
        "identity_key": f.identity_key,
        "severity": round(f.severity, 3),
        "title": f.title,
        "files": f.files,
        "evidence": [
            {
                "signal": e.signal,
                "value": round(e.value, 4),
                "percentile": round(e.percentile, 1),
                "description": e.description,
            }
            for e in f.evidence
        ],
        "suggestion": f.suggestion,
    }


def _output_scoped_rich(
    report: ChangeScopedReport,
    result: InsightResult,
    verbose: bool = False,
):
    """Human-readable Rich terminal output for a change-scoped report."""
    summary = result.store_summary
    console.print()

    console.print(
        "[bold cyan]SHANNON INSIGHT[/bold cyan] \u2014 [bold]Change-Scoped Analysis[/bold]"
    )
    parts = [f"[bold]{summary.total_files}[/bold] files"]
    if summary.total_modules:
        parts.append(f"[bold]{summary.total_modules}[/bold] modules")
    if summary.commits_analyzed:
        parts.append(f"[bold]{summary.commits_analyzed}[/bold] commits")
    console.print(f"  Full codebase: {', '.join(parts)} analyzed")
    console.print()

    risk_color = _RISK_COLORS.get(report.risk_level, "white")
    console.print(f"  Risk Level: [{risk_color}]{report.risk_level.upper()}[/{risk_color}]")
    console.print(f"  [dim]{report.risk_reason}[/dim]")
    console.print()

    console.print(f"  [bold]Changed files:[/bold] {len(report.changed_files)}")
    for fp in report.changed_files:
        console.print(f"    [dim]\u2022[/dim] {fp}")
    console.print()

    if report.blast_radius_files:
        console.print(
            f"  [bold]Blast radius:[/bold] "
            f"{len(report.blast_radius_files)} additional file(s) affected"
        )
        if verbose:
            for fp in report.blast_radius_files:
                console.print(f"    [dim]\u2022[/dim] {fp}")
        else:
            shown = report.blast_radius_files[:5]
            for fp in shown:
                console.print(f"    [dim]\u2022[/dim] {fp}")
            remaining = len(report.blast_radius_files) - len(shown)
            if remaining > 0:
                console.print(
                    f"    [dim]... and {remaining} more (use --verbose to show all)[/dim]"
                )
        console.print()

    if verbose and report.file_risk:
        console.print("  [bold]Per-file risk:[/bold]")
        for fr in report.file_risk:
            dep_str = (
                f"{fr.dependents_count} dependent(s)" if fr.dependents_count else "no dependents"
            )
            finding_str = f"{fr.findings_count} finding(s)" if fr.findings_count else "no findings"
            console.print(f"    [bold]{fr.filepath}[/bold] \u2014 {dep_str}, {finding_str}")
            if fr.percentiles:
                top_signals = sorted(
                    fr.percentiles.items(),
                    key=lambda kv: kv[1],
                    reverse=True,
                )[:3]
                for sig_name, pct in top_signals:
                    val = fr.signals.get(sig_name, 0.0)
                    console.print(f"      [dim]{sig_name}={val:.4f} (p{pct:.0f})[/dim]")
        console.print()

    # Group scoped findings
    all_scoped_findings = report.direct_findings + report.blast_findings
    if all_scoped_findings:
        console.print(f"  [bold]Findings in scope ({len(all_scoped_findings)}):[/bold]")
        console.print()
        for i, finding in enumerate(all_scoped_findings):
            _render_finding_record(finding, verbose, i + 1)
    else:
        console.print("  [bold green]No findings involve changed files.[/bold green]")
        console.print()

    total_scoped = len(all_scoped_findings)
    console.print(
        f"[dim]{total_scoped} scoped finding(s) from "
        f"{len(report.changed_files)} changed file(s) "
        f"(blast radius: {len(report.blast_radius_files)} file(s)).[/dim]"
    )
    if not verbose:
        console.print("[dim]Use --verbose for per-file risk details and full blast radius.[/dim]")
    console.print()


def _render_finding_record(
    finding: FindingRecord,
    verbose: bool,
    index: int,
):
    """Render a single FindingRecord (from the snapshot layer)."""
    type_colors = {
        "high_risk_hub": "red",
        "hidden_coupling": "yellow",
        "god_file": "magenta",
        "unstable_file": "yellow",
        "boundary_mismatch": "cyan",
        "dead_dependency": "dim",
    }
    type_labels = {
        "high_risk_hub": "HIGH RISK HUB",
        "hidden_coupling": "HIDDEN COUPLING",
        "god_file": "GOD FILE",
        "unstable_file": "UNSTABLE FILE",
        "boundary_mismatch": "BOUNDARY MISMATCH",
        "dead_dependency": "DEAD DEPENDENCY",
    }

    label = type_labels.get(finding.finding_type, finding.finding_type.upper())
    color = type_colors.get(finding.finding_type, "white")

    console.print(f"  [bold {color}]{index}. {label}[/bold {color}]")

    if len(finding.files) == 2:
        console.print(
            f"     [bold]{finding.files[0]}[/bold] \u2194 [bold]{finding.files[1]}[/bold]"
        )
    elif len(finding.files) > 2:
        console.print(f"     [bold]{finding.files[0]}[/bold]")
        for f in finding.files[1:]:
            console.print(f"     [bold]{f}[/bold]")
    else:
        console.print(f"     [bold]{finding.files[0]}[/bold]")

    for e in finding.evidence:
        console.print(f"     [dim]\u2022[/dim] {e.description}")

    if verbose:
        for e in finding.evidence:
            pct_str = f", p{e.percentile:.0f}" if e.percentile > 0 else ""
            console.print(f"       [dim]{e.signal}={e.value:.4f}{pct_str}[/dim]")

    suggestion_lines = finding.suggestion.split("\n")
    console.print(f"     [green]\u2192 {suggestion_lines[0]}[/green]")
    for line in suggestion_lines[1:]:
        console.print(f"     [green]  {line}[/green]")

    console.print()
