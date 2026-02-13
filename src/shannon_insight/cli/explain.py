"""Explain command — deep-dive on a specific file."""

import difflib
import json as json_mod
from pathlib import Path
from typing import Any, Optional

import typer

from ..insights import InsightKernel
from ..logging_config import setup_logging
from . import app
from ._common import console, resolve_settings

# Signal name translation: internal -> developer-friendly
SIGNAL_LABELS: dict[str, tuple] = {
    "cognitive_load": ("Complexity", "higher means harder to understand"),
    "semantic_coherence": ("Focus", "higher means more single-purpose"),
    "pagerank": ("Importance", "how many files depend on this"),
    "in_degree": ("Direct importers", "files that import this directly"),
    "blast_radius_size": ("Blast radius", "files affected if this breaks"),
    "compression_ratio": ("Code density", "information per line"),
    "network_centrality": ("Centrality", "position in dependency network"),
    "total_changes": ("Recent changes", "times modified in git history"),
    "churn_slope": ("Churn trend", "whether change frequency is increasing"),
    "churn_volatility": ("Churn volatility", "how irregular the change pattern is"),
    "function_count": ("Functions", "number of functions/methods"),
    "lines": ("Lines", "total lines of code"),
    "nesting_depth": ("Max nesting", "deepest nesting level"),
}

# Signals to show in the default explain view
VISIBLE_SIGNALS = [
    "cognitive_load",
    "semantic_coherence",
    "pagerank",
    "blast_radius_size",
    "total_changes",
    "function_count",
    "lines",
    "nesting_depth",
]


def _sparkline(values: list) -> str:
    """Generate an ASCII sparkline from a list of numeric values."""
    if not values:
        return ""
    blocks = " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
    mn, mx = min(values), max(values)
    if mx == mn:
        return blocks[4] * len(values)
    return "".join(blocks[min(8, int((v - mn) / (mx - mn) * 8))] for v in values)


def _interpret_percentile(percentile: float) -> str:
    """Turn a percentile into a human-readable level."""
    if percentile >= 90:
        return "Very high"
    elif percentile >= 70:
        return "High"
    elif percentile >= 30:
        return "Moderate"
    else:
        return "Low"


def _load_trends(target: Path, filepath: str) -> Optional[dict[str, list]]:
    """Load trend data from history for a file, if available."""
    try:
        from ..persistence import HistoryDB
        from ..persistence.queries import HistoryQuery

        resolved = target.resolve()
        db_path = resolved / ".shannon" / "history.db"
        if not db_path.exists():
            return None

        with HistoryDB(str(resolved)) as db:
            query = HistoryQuery(db.conn)
            trends = {}
            for metric in ["cognitive_load", "semantic_coherence", "pagerank"]:
                points = query.file_trend(filepath, metric, last_n=20)
                if points:
                    trends[metric] = points
            return trends if trends else None
    except Exception:
        return None


@app.command()
def explain(
    ctx: typer.Context,
    file: str = typer.Argument(..., help="File to explain (substring match)"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show all signals"),
):
    """Deep-dive on a specific file: signals, findings, and trends."""
    target = ctx.obj.get("path", Path.cwd())
    # Don't pass verbose to logging — verbose here controls display detail, not log level
    setup_logging(verbose=False)

    settings = resolve_settings()
    kernel = InsightKernel(str(target.resolve()), language="auto", settings=settings)

    # For explain, get more findings so we can show those related to the file
    result, snapshot = kernel.run(max_findings=500)

    # Find matching files
    all_files = sorted(snapshot.file_signals.keys())

    # Case-insensitive substring match
    pattern_lower = file.lower()
    matches = [f for f in all_files if pattern_lower in f.lower()]

    if not matches:
        console.print(f"[yellow]No file matching '{file}' found.[/yellow]")
        close = difflib.get_close_matches(file, all_files, n=5, cutoff=0.3)
        if close:
            console.print("Did you mean:")
            for c in close:
                console.print(f"  {c}")
        raise typer.Exit(1)

    if len(matches) > 1:
        console.print(f"[yellow]Multiple files match '{file}':[/yellow]")
        for m in sorted(matches):
            console.print(f"  {m}")
        console.print("\nUse a more specific name to select one.")
        raise typer.Exit(1)

    matched_file = matches[0]

    # Get signals for the file
    file_signals = snapshot.file_signals.get(matched_file, {})

    # Compute percentiles for this file across the codebase
    percentiles = _compute_percentiles(matched_file, snapshot.file_signals)

    # Get findings involving this file
    related_findings = [f for f in snapshot.findings if matched_file in f.files]

    # Get trends from history
    trends = _load_trends(target, matched_file)

    if json_output:
        _output_json(matched_file, file_signals, percentiles, related_findings, trends)
    else:
        _output_rich(matched_file, file_signals, percentiles, related_findings, trends, verbose)


def _compute_percentiles(
    filepath: str, all_signals: dict[str, dict[str, float]]
) -> dict[str, float]:
    """Compute percentile rank for a file on each metric."""
    from bisect import bisect_left

    file_sigs = all_signals.get(filepath, {})
    if not file_sigs:
        return {}

    # For each metric, build sorted values
    # Skip non-numeric values (dicts like 'percentiles', strings like 'role', bools)
    result: dict[str, float] = {}
    for metric, value in file_sigs.items():
        # Only process numeric metrics
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue

        # Collect values for this metric across all files
        vals = sorted(
            v
            for sigs in all_signals.values()
            if (v := sigs.get(metric)) is not None
            and isinstance(v, (int, float))
            and not isinstance(v, bool)
        )
        if vals:
            rank = bisect_left(vals, value)
            result[metric] = 100.0 * rank / len(vals)
        else:
            result[metric] = 0.0
    return result


def _output_json(matched_file, file_signals, percentiles, related_findings, trends):
    """JSON output for explain."""
    # Filter and round numeric values, pass through strings/bools as-is, skip dicts
    filtered_signals: dict[str, Any] = {}
    for k, v in file_signals.items():
        if isinstance(v, bool):
            filtered_signals[k] = v
        elif isinstance(v, (int, float)):
            filtered_signals[k] = round(v, 4)
        elif isinstance(v, str):
            filtered_signals[k] = v
        # Skip dicts like 'percentiles'

    output = {
        "file": matched_file,
        "signals": filtered_signals,
        "percentiles": {k: round(v, 1) for k, v in percentiles.items()},
        "findings": [
            {
                "type": f.finding_type,
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
            for f in related_findings
        ],
    }
    if trends:
        output["trends"] = {
            metric: [{"timestamp": p.timestamp, "value": p.value} for p in points]
            for metric, points in trends.items()
        }
    print(json_mod.dumps(output, indent=2))


def _output_rich(matched_file, file_signals, percentiles, related_findings, trends, verbose):
    """Rich terminal output for explain."""
    console.print()
    console.print(f"[bold cyan]EXPLAIN:[/bold cyan] [bold]{matched_file}[/bold]")
    console.print()

    # Signals section — translated labels
    if file_signals:
        console.print("  [bold]Signals:[/bold]")
        if verbose:
            # Show all signals: translated ones first, then raw ones
            # Skip internal signals like 'percentiles', 'role' (strings)
            skip = {"percentiles", "role", "churn_trajectory", "parent_dir", "module_path"}
            known = [s for s in VISIBLE_SIGNALS if s in file_signals]
            extra_known = [s for s in file_signals if s in SIGNAL_LABELS and s not in known]
            unknown = [s for s in sorted(file_signals) if s not in SIGNAL_LABELS and s not in skip]
            signals_to_show = known + extra_known + unknown
        else:
            signals_to_show = VISIBLE_SIGNALS

        for sig_name in signals_to_show:
            if sig_name not in file_signals:
                continue
            value = file_signals[sig_name]
            pct = percentiles.get(sig_name, 0.0)
            label_info = SIGNAL_LABELS.get(sig_name)

            if label_info:
                label, desc = label_info
                level = _interpret_percentile(pct)
                console.print(f"    {label:<20s} {level} \u2014 {desc} (p{int(pct)})")
            else:
                # Handle non-numeric values (strings, bools, dicts)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    value_str = f"{value:.4f}"
                else:
                    value_str = str(value)
                console.print(f"    [dim]{sig_name:<20s} {value_str} (p{int(pct)})[/dim]")

        if not verbose:
            hidden_count = len(file_signals) - len(
                [s for s in VISIBLE_SIGNALS if s in file_signals]
            )
            if hidden_count > 0:
                console.print(f"    [dim]... {hidden_count} more signals (use --verbose)[/dim]")

        console.print()

    # Trends section
    if trends:
        console.print("  [bold]Trends:[/bold]")
        for metric, points in trends.items():
            label_info = SIGNAL_LABELS.get(metric)
            label = label_info[0] if label_info else metric
            values = [p.value for p in points]
            spark = _sparkline(values)
            console.print(f"    {label:<20s} {spark}")
        console.print()

    # Findings section
    if related_findings:
        console.print(f"  [bold]Findings ({len(related_findings)}):[/bold]")
        console.print()

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

        for i, finding in enumerate(related_findings):
            label = type_labels.get(finding.finding_type, finding.finding_type.upper())
            color = type_colors.get(finding.finding_type, "white")

            console.print(f"    [bold {color}]{i + 1}. {label}[/bold {color}]")
            for e in finding.evidence:
                console.print(f"       [dim]\u2022[/dim] {e.description}")
            suggestion_lines = finding.suggestion.split("\n")
            console.print(f"       [green]\u2192 {suggestion_lines[0]}[/green]")
            for line in suggestion_lines[1:]:
                console.print(f"       [green]  {line}[/green]")
            console.print()
    else:
        console.print("  [dim]No findings involve this file.[/dim]")
        console.print()
