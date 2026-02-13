"""Finding display configuration - Informative, not prescriptive.

Philosophy: INFORM developers, don't PRESCRIBE fixes.

Each finding shows:
  1. WHAT: Finding type + title
  2. DATA: Raw signals that triggered the finding
  3. MEANING: Neutral interpretation of what the data means

NO suggestions, NO action verbs ("split", "extract", "fix").
Developers are smart - show them the data, let them decide.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..insights.models import Finding

MAX_FILES_PER_GROUP = 20  # Increased from 10 for better visibility


# ══════════════════════════════════════════════════════════════════════════════
# Severity Display
# ══════════════════════════════════════════════════════════════════════════════


SEVERITY_DISPLAY = {
    "critical": ("🔴", "bold red"),
    "high": ("🟠", "red"),
    "medium": ("🟡", "yellow"),
    "low": ("🔵", "blue"),
    "info": ("⚪", "dim"),
}


def get_severity_display(severity: float) -> tuple[str, str, str]:
    """Get (icon, color, label) for a severity score (0-1)."""
    if severity >= 0.9:
        return "🔴", "bold red", "CRITICAL"
    if severity >= 0.8:
        return "🟠", "red", "HIGH"
    if severity >= 0.6:
        return "🟡", "yellow", "MEDIUM"
    if severity >= 0.4:
        return "🔵", "blue", "LOW"
    return "⚪", "dim", "INFO"


# ══════════════════════════════════════════════════════════════════════════════
# Data Point Extraction
# ══════════════════════════════════════════════════════════════════════════════


def _extract_data_points(finding: Finding) -> list[tuple[str, str]]:
    """Extract key data points from finding evidence.

    Returns list of (label, value_string) tuples.
    """
    points = []
    for e in finding.evidence:
        # Format value with percentile if available
        if e.percentile and e.percentile > 0:
            pctl_str = f"({e.percentile:.0f}th pctl)"
        else:
            pctl_str = ""

        # Format based on signal type
        signal = e.signal.lower()
        if "ratio" in signal or "score" in signal or "gini" in signal:
            val_str = f"{e.value:.2f}"
        elif "count" in signal or "degree" in signal or "radius" in signal:
            val_str = f"{int(e.value)}"
        elif signal in ("pagerank", "betweenness", "coherence"):
            val_str = f"{e.value:.3f}"
        else:
            val_str = f"{e.value:.2f}"

        label = e.signal.replace("_", " ")
        points.append((label, f"{val_str} {pctl_str}".strip()))

    return points


def _format_data_line(finding: Finding) -> str:
    """Format a single line showing key data."""
    points = _extract_data_points(finding)
    if not points:
        return ""

    # Take top 3 data points
    parts = [f"{label}: {val}" for label, val in points[:3]]
    return "  ".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# Finding Type Configuration
# ══════════════════════════════════════════════════════════════════════════════


# Each finding has:
# - label: Human-readable name
# - icon: Visual indicator
# - color: Rich color for display
# - data_points: Signal names that are most relevant
# - interpretation: Neutral explanation of what the finding means

FINDING_DISPLAY: dict = {
    # === Structural Issues ===
    "high_risk_hub": {
        "label": "High-Centrality File",
        "icon": "🎯",
        "color": "red",
        "data_points": ["pagerank", "blast_radius_size", "in_degree"],
        "interpretation": "Central in the dependency graph. Changes here propagate to many dependents.",
    },
    "god_file": {
        "label": "Large Complex File",
        "icon": "👑",
        "color": "magenta",
        "data_points": ["function_count", "cognitive_load", "lines"],
        "interpretation": "High function count and complexity. Multiple responsibilities likely.",
    },
    "orphan_code": {
        "label": "Orphan File",
        "icon": "🔌",
        "color": "dim",
        "data_points": ["in_degree", "is_orphan"],
        "interpretation": "No other files import this. Either standalone or unused.",
    },
    "hollow_code": {
        "label": "Stub-Heavy File",
        "icon": "🕳️",
        "color": "yellow",
        "data_points": ["stub_ratio", "function_count"],
        "interpretation": "High ratio of stub/empty functions. Implementation may be incomplete.",
    },
    "phantom_imports": {
        "label": "Missing Import Target",
        "icon": "👻",
        "color": "red",
        "data_points": ["phantom_import_count", "out_degree"],
        "interpretation": "Imports reference files that don't exist in the codebase.",
    },
    "flat_architecture": {
        "label": "No Composition Layer",
        "icon": "📦",
        "color": "cyan",
        "data_points": ["depth", "modularity"],
        "interpretation": "All files at same depth level. No orchestration modules composing others.",
    },
    "copy_paste_clone": {
        "label": "Near-Duplicate Code",
        "icon": "📋",
        "color": "yellow",
        "data_points": ["compression_ratio", "lines"],
        "interpretation": "Files with very similar content detected by compression analysis.",
    },
    # === Coupling Issues ===
    "hidden_coupling": {
        "label": "Co-Change Without Import",
        "icon": "🔗",
        "color": "yellow",
        "data_points": ["cochange_count", "lift"],
        "interpretation": "Files change together frequently but have no direct import relationship.",
    },
    "accidental_coupling": {
        "label": "Unrelated Files Co-Changing",
        "icon": "⚡",
        "color": "yellow",
        "data_points": ["concept_overlap", "cochange_count"],
        "interpretation": "Files share few concepts but change together. Coupling may be incidental.",
    },
    "dead_dependency": {
        "label": "Import Without Co-Change",
        "icon": "💀",
        "color": "dim",
        "data_points": ["cochange_count", "out_degree"],
        "interpretation": "Import exists but files never change together. Import may be obsolete.",
    },
    # === Architecture Issues ===
    "boundary_mismatch": {
        "label": "Directory vs Dependency Mismatch",
        "icon": "📐",
        "color": "cyan",
        "data_points": ["boundary_alignment", "community"],
        "interpretation": "File organization doesn't match actual dependency patterns.",
    },
    "layer_violation": {
        "label": "Layer Dependency Violation",
        "icon": "🏛️",
        "color": "red",
        "data_points": ["layer_violation_count", "depth"],
        "interpretation": "Dependency skips architectural layers (e.g., presentation directly imports data).",
    },
    "zone_of_pain": {
        "label": "Unstable Abstraction",
        "icon": "💢",
        "color": "red",
        "data_points": ["instability", "abstractness", "main_seq_distance"],
        "interpretation": "Module is both abstract and unstable. High abstractness + high instability = pain zone.",
    },
    "architecture_erosion": {
        "label": "Architecture Erosion",
        "icon": "🏚️",
        "color": "red",
        "data_points": ["violation_rate", "architecture_health"],
        "interpretation": "Multiple architectural violations detected. Design rules being bypassed.",
    },
    # === Temporal Issues ===
    "unstable_file": {
        "label": "High-Churn File",
        "icon": "📈",
        "color": "yellow",
        "data_points": ["total_changes", "churn_cv", "churn_trajectory"],
        "interpretation": "Frequent changes with high variability. Not stabilizing over time.",
    },
    "chronic_problem": {
        "label": "Repeated Bugfix Target",
        "icon": "🔄",
        "color": "red",
        "data_points": ["fix_ratio", "total_changes"],
        "interpretation": "High proportion of commits are bugfixes. Recurring issues in this area.",
    },
    "thrashing_code": {
        "label": "Code Thrashing",
        "icon": "🌀",
        "color": "red",
        "data_points": ["churn_cv", "churn_slope", "refactor_ratio"],
        "interpretation": "Very high change volatility. Code being rewritten repeatedly.",
    },
    # === Team Issues ===
    "knowledge_silo": {
        "label": "Single-Author Code",
        "icon": "🏝️",
        "color": "yellow",
        "data_points": ["bus_factor", "author_entropy"],
        "interpretation": "Only one person has worked on this code. Knowledge concentrated.",
    },
    "review_blindspot": {
        "label": "Low Review Coverage",
        "icon": "👁️",
        "color": "yellow",
        "data_points": ["review_coverage", "total_changes"],
        "interpretation": "Changes to this file often bypass review process.",
    },
    "truck_factor": {
        "label": "Low Bus Factor",
        "icon": "🚌",
        "color": "yellow",
        "data_points": ["bus_factor", "author_entropy"],
        "interpretation": "Few contributors understand this area. Knowledge risk if people leave.",
    },
    "conway_violation": {
        "label": "Cross-Team Coupling",
        "icon": "🏢",
        "color": "cyan",
        "data_points": ["conway_alignment", "coordination_cost"],
        "interpretation": "Files owned by different teams are tightly coupled.",
    },
    # === Broken/Incomplete ===
    "incomplete_implementation": {
        "label": "Incomplete Code",
        "icon": "🚧",
        "color": "red",
        "data_points": ["phantom_import_count", "stub_ratio"],
        "interpretation": "Missing imports or high stub ratio. Implementation not finished.",
    },
    "bug_attractor": {
        "label": "Bug Attractor",
        "icon": "🪲",
        "color": "red",
        "data_points": ["fix_ratio", "churn_cv", "cognitive_load"],
        "interpretation": "Combination of complexity and bugfix history makes this a likely bug location.",
    },
    "weak_link": {
        "label": "Critical Dependency",
        "icon": "⚠️",
        "color": "yellow",
        "data_points": ["pagerank", "bus_factor", "churn_cv"],
        "interpretation": "High centrality combined with low bus factor. Critical and fragile.",
    },
    "naming_drift": {
        "label": "Naming Inconsistency",
        "icon": "📝",
        "color": "dim",
        "data_points": ["naming_drift", "concept_count"],
        "interpretation": "File/function names don't match content patterns in this area.",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════


def get_display_config(finding_type: str) -> dict:
    """Get display config for a finding type, with sensible defaults."""
    if finding_type in FINDING_DISPLAY:
        return dict(FINDING_DISPLAY[finding_type])

    # Generate defaults for unknown types
    label = finding_type.replace("_", " ").title()
    return {
        "label": label,
        "icon": "⚠️",
        "color": "white",
        "data_points": [],
        "interpretation": "",
    }


def format_finding_data(finding: Finding) -> str:
    """Format a finding's data points as a single line.

    Example output: "pagerank: 0.89 (95th pctl)  blast_radius: 23  importers: 18"
    """
    return _format_data_line(finding)


def format_finding_detail(finding: Finding) -> list[str]:
    """Format a finding for detailed display.

    Returns list of lines showing:
    - Type and severity
    - Files affected
    - Data points from evidence
    - Neutral interpretation
    """
    lines = []
    display = get_display_config(finding.finding_type)
    icon, color, label = get_severity_display(finding.severity)

    # Header
    lines.append(f"[{color} bold]{display['icon']} {display['label']}[/]  [{color}]{label}[/]")

    # Files
    if finding.files:
        if len(finding.files) == 1:
            lines.append(f"[cyan]{finding.files[0]}[/cyan]")
        else:
            for path in finding.files[:5]:
                lines.append(f"  [cyan]{path}[/cyan]")
            if len(finding.files) > 5:
                lines.append(f"  [dim]... and {len(finding.files) - 5} more[/dim]")
    else:
        lines.append("[dim](codebase-level)[/dim]")

    lines.append("")

    # Data points
    points = _extract_data_points(finding)
    if points:
        lines.append("[bold]Data:[/bold]")
        for label, val in points:
            lines.append(f"  {label}: {val}")
        lines.append("")

    # Interpretation
    interp = display.get("interpretation", "")
    if interp:
        lines.append(f"[dim]{interp}[/dim]")

    return lines


def get_finding_interpretation(finding_type: str) -> str:
    """Get the interpretation text for a finding type."""
    display = get_display_config(finding_type)
    return display.get("interpretation", "")


def get_finding_data_points(finding_type: str) -> list[str]:
    """Get the list of relevant signal names for a finding type."""
    display = get_display_config(finding_type)
    return display.get("data_points", [])
