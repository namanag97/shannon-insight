"""Raw signal display for informative (non-prescriptive) output.

Formats signals for human consumption:
- Shows actual values, not interpretations
- Groups by category (structural, temporal, architectural)
- Includes percentiles where available
- No prescriptive language - just facts
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..persistence.models import TensorSnapshot
    from ..signals.models import FileSignals


# ══════════════════════════════════════════════════════════════════════════════
# Signal Categories
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class SignalCategory:
    """A category of related signals."""

    key: str
    name: str
    icon: str
    signals: list[str]  # Signal names in this category
    description: str


SIGNAL_CATEGORIES = [
    SignalCategory(
        key="size",
        name="Size & Complexity",
        icon="📏",
        signals=["lines", "function_count", "class_count", "max_nesting", "cognitive_load"],
        description="How big and complex the code is",
    ),
    SignalCategory(
        key="structure",
        name="Graph Position",
        icon="🔗",
        signals=[
            "pagerank",
            "betweenness",
            "in_degree",
            "out_degree",
            "blast_radius_size",
            "depth",
        ],
        description="Where the file sits in the dependency graph",
    ),
    SignalCategory(
        key="health",
        name="Code Health",
        icon="💊",
        signals=[
            "stub_ratio",
            "is_orphan",
            "phantom_import_count",
            "compression_ratio",
            "semantic_coherence",
        ],
        description="Code quality indicators",
    ),
    SignalCategory(
        key="temporal",
        name="Change History",
        icon="📈",
        signals=[
            "total_changes",
            "churn_trajectory",
            "churn_cv",
            "bus_factor",
            "fix_ratio",
            "change_entropy",
        ],
        description="How the file has changed over time",
    ),
    SignalCategory(
        key="team",
        name="Team Context",
        icon="👥",
        signals=["author_entropy", "bus_factor"],
        description="Who works on this code",
    ),
    SignalCategory(
        key="risk",
        name="Computed Risk",
        icon="⚠️",
        signals=["risk_score", "wiring_quality", "file_health_score", "raw_risk"],
        description="Composite risk indicators",
    ),
]

# Build signal -> category mapping
SIGNAL_TO_CATEGORY: dict[str, SignalCategory] = {}
for cat in SIGNAL_CATEGORIES:
    for sig in cat.signals:
        SIGNAL_TO_CATEGORY[sig] = cat


# ══════════════════════════════════════════════════════════════════════════════
# Human-Readable Signal Names
# ══════════════════════════════════════════════════════════════════════════════


SIGNAL_LABELS: dict[str, str] = {
    # Size & complexity
    "lines": "Lines of code",
    "function_count": "Functions",
    "class_count": "Classes/Structs",
    "max_nesting": "Max nesting depth",
    "cognitive_load": "Cognitive load",
    "impl_gini": "Function size inequality",
    # Graph position
    "pagerank": "PageRank centrality",
    "betweenness": "Betweenness centrality",
    "in_degree": "Files that import this",
    "out_degree": "Files this imports",
    "blast_radius_size": "Blast radius (files affected)",
    "depth": "DAG depth from entry",
    "community": "Louvain community",
    # Health
    "stub_ratio": "Stub/empty functions",
    "is_orphan": "Is orphan (no importers)",
    "phantom_import_count": "Missing imports",
    "compression_ratio": "Compression ratio",
    "semantic_coherence": "Semantic coherence",
    # Temporal
    "total_changes": "Total commits",
    "churn_trajectory": "Churn trend",
    "churn_slope": "Churn slope",
    "churn_cv": "Churn volatility (CV)",
    "bus_factor": "Bus factor",
    "author_entropy": "Author diversity",
    "fix_ratio": "Bugfix ratio",
    "refactor_ratio": "Refactor ratio",
    "change_entropy": "Change distribution",
    # Risk composites
    "risk_score": "Risk score",
    "wiring_quality": "Wiring quality",
    "file_health_score": "File health",
    "raw_risk": "Raw risk (pre-percentile)",
}


# ══════════════════════════════════════════════════════════════════════════════
# Formatting Functions
# ══════════════════════════════════════════════════════════════════════════════


def format_signal_value(name: str, value: float | int | bool | str | None) -> str:
    """Format a signal value for display.

    Returns a human-readable string representation.
    """
    if value is None:
        return "—"

    if isinstance(value, bool):
        return "yes" if value else "no"

    if isinstance(value, str):
        return value

    if isinstance(value, int):
        return f"{value:,}"

    # Float formatting based on signal type
    if name in ("pagerank", "betweenness", "risk_score", "wiring_quality", "semantic_coherence"):
        return f"{value:.3f}"
    if name in ("stub_ratio", "fix_ratio", "refactor_ratio"):
        return f"{value * 100:.1f}%"
    if name in ("churn_cv", "compression_ratio", "author_entropy"):
        return f"{value:.2f}"
    if name == "cognitive_load":
        return f"{value:.1f}"
    if name == "bus_factor":
        return f"{value:.1f} authors"

    return f"{value:.2f}"


def format_signal_with_percentile(
    name: str,
    value: float | int | bool | str | None,
    percentile: float | None = None,
) -> str:
    """Format a signal with its percentile.

    Returns: "value  (Nth percentile)" or just "value" if no percentile.
    """
    val_str = format_signal_value(name, value)

    if percentile is not None and not isinstance(value, (bool, str)):
        pctl_str = f"({percentile:.0f}th pctl)"
        return f"{val_str:>10}  {pctl_str}"

    return f"{val_str:>10}"


def get_signal_label(name: str) -> str:
    """Get human-readable label for a signal name."""
    return SIGNAL_LABELS.get(name, name.replace("_", " ").title())


# ══════════════════════════════════════════════════════════════════════════════
# File Signal Display
# ══════════════════════════════════════════════════════════════════════════════


def format_file_signals(signals: FileSignals, show_all: bool = False) -> list[str]:
    """Format all signals for a file as display lines.

    Args:
        signals: FileSignals dataclass
        show_all: If True, show all signals. If False, show key signals only.

    Returns:
        List of formatted lines ready for display.
    """
    lines = []

    # Convert signals to dict for easy access
    sig_dict: dict[str, float | int | bool | str | None] = {
        "lines": signals.lines,
        "function_count": signals.function_count,
        "class_count": signals.class_count,
        "max_nesting": signals.max_nesting,
        "cognitive_load": signals.cognitive_load,
        "impl_gini": signals.impl_gini,
        "stub_ratio": signals.stub_ratio,
        "pagerank": signals.pagerank,
        "betweenness": signals.betweenness,
        "in_degree": signals.in_degree,
        "out_degree": signals.out_degree,
        "blast_radius_size": signals.blast_radius_size,
        "depth": signals.depth,
        "is_orphan": signals.is_orphan,
        "phantom_import_count": signals.phantom_import_count,
        "compression_ratio": signals.compression_ratio,
        "semantic_coherence": signals.semantic_coherence,
        "total_changes": signals.total_changes,
        "churn_trajectory": signals.churn_trajectory,
        "churn_cv": signals.churn_cv,
        "bus_factor": signals.bus_factor,
        "author_entropy": signals.author_entropy,
        "fix_ratio": signals.fix_ratio,
        "risk_score": signals.risk_score,
        "wiring_quality": signals.wiring_quality,
        "file_health_score": signals.file_health_score,
        "role": signals.role,
    }

    percentiles = signals.percentiles

    # Key signals to show by default
    key_signals = [
        "lines",
        "function_count",
        "cognitive_load",
        "pagerank",
        "blast_radius_size",
        "total_changes",
        "churn_cv",
        "bus_factor",
        "risk_score",
    ]

    if show_all:
        # Group by category
        for cat in SIGNAL_CATEGORIES:
            cat_signals = [(s, sig_dict.get(s)) for s in cat.signals if s in sig_dict]
            if not cat_signals:
                continue

            lines.append(f"{cat.icon} {cat.name}")

            for name, value in cat_signals:
                if value is None:
                    continue
                label = get_signal_label(name)
                pctl = percentiles.get(name)
                val_str = format_signal_with_percentile(name, value, pctl)
                lines.append(f"  {label:.<30} {val_str}")

            lines.append("")
    else:
        # Just key signals in compact form
        for name in key_signals:
            value = sig_dict.get(name)
            if value is None:
                continue
            label = get_signal_label(name)
            pctl = percentiles.get(name)
            val_str = format_signal_with_percentile(name, value, pctl)
            lines.append(f"  {label:.<30} {val_str}")

    return lines


# ══════════════════════════════════════════════════════════════════════════════
# Codebase Signal Display
# ══════════════════════════════════════════════════════════════════════════════


def format_global_signals(global_signals: dict[str, float]) -> list[str]:
    """Format global/codebase signals for display.

    Args:
        global_signals: Dict of signal name -> value from snapshot.global_signals

    Returns:
        List of formatted lines.
    """
    lines = []

    # Key codebase metrics
    key_metrics = [
        ("modularity", "Modularity"),
        ("fiedler_value", "Fiedler value (connectivity)"),
        ("cycle_count", "Dependency cycles"),
        ("centrality_gini", "Centrality inequality"),
        ("orphan_ratio", "Orphan files"),
        ("phantom_ratio", "Phantom imports"),
        ("wiring_score", "Wiring quality"),
        ("architecture_health", "Architecture health"),
        ("codebase_health", "Codebase health"),
        ("team_risk", "Team risk"),
    ]

    for name, label in key_metrics:
        value = global_signals.get(name)
        if value is not None:
            val_str = format_signal_value(name, value)
            lines.append(f"  {label:.<35} {val_str:>10}")

    return lines


# ══════════════════════════════════════════════════════════════════════════════
# Signal Table for CLI Output
# ══════════════════════════════════════════════════════════════════════════════


def render_signals_table(
    snapshot: TensorSnapshot,
    file_path: str | None = None,
) -> str:
    """Render signals as a table for CLI --signals output.

    Args:
        snapshot: The analysis snapshot
        file_path: If provided, show signals for this file only.
                   If None, show top files by risk.

    Returns:
        Formatted string ready for console.print()
    """
    lines = []

    if file_path:
        # Single file view
        file_signals = snapshot.file_signals.get(file_path)
        if not file_signals:
            return f"No signals found for: {file_path}"

        lines.append(f"[bold]Signals for:[/bold] [cyan]{file_path}[/cyan]")
        lines.append("")

        # Create a minimal FileSignals-like object from the dict
        from ..signals.models import FileSignals

        fs = FileSignals(path=file_path)
        for key, value in file_signals.items():
            if hasattr(fs, key) and value is not None:
                setattr(fs, key, value)

        signal_lines = format_file_signals(fs, show_all=True)
        lines.extend(signal_lines)

    else:
        # Top files by risk
        lines.append("[bold]CODEBASE SIGNALS[/bold]")
        lines.append("")
        lines.extend(format_global_signals(snapshot.global_signals or {}))
        lines.append("")

        # Top 10 files by risk
        lines.append("[bold]TOP FILES BY RISK[/bold]")
        lines.append("")

        # Sort files by risk_score
        file_risks = []
        for path, sig_dict in snapshot.file_signals.items():
            risk = sig_dict.get("risk_score", 0.0)
            file_risks.append((path, risk, sig_dict))

        file_risks.sort(key=lambda x: x[1], reverse=True)

        # Header
        lines.append(f"  {'File':<40} {'Risk':>8} {'Churn':>8} {'PageRank':>10} {'Cognitive':>10}")
        lines.append("  " + "-" * 80)

        for path, risk, sig_dict in file_risks[:15]:
            # Truncate long paths
            if len(path) > 38:
                display_path = "..." + path[-35:]
            else:
                display_path = path

            churn = sig_dict.get("total_changes", 0)
            pagerank = sig_dict.get("pagerank", 0.0)
            cognitive = sig_dict.get("cognitive_load", 0.0)

            lines.append(
                f"  {display_path:<40} {risk:>8.3f} {churn:>8} {pagerank:>10.3f} {cognitive:>10.1f}"
            )

        lines.append("")
        lines.append("[dim]Use 'shannon-insight --signals <file>' for detailed view[/dim]")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# Signal Color-Coding
# ══════════════════════════════════════════════════════════════════════════════


# Signal polarity: True = higher is worse, False = higher is better, None = neutral
SIGNAL_POLARITY: dict[str, bool | None] = {
    # Higher is WORSE (red when high)
    "risk_score": True,
    "raw_risk": True,
    "churn_cv": True,
    "cognitive_load": True,
    "max_nesting": True,
    "stub_ratio": True,
    "phantom_import_count": True,
    "fix_ratio": True,
    "blast_radius_size": True,
    # Higher is BETTER (green when high)
    "wiring_quality": False,
    "file_health_score": False,
    "semantic_coherence": False,
    "bus_factor": False,
    "compression_ratio": False,
    "architecture_health": False,
    "codebase_health": False,
    "modularity": False,
    # Neutral (cyan, just informational)
    "pagerank": None,
    "betweenness": None,
    "in_degree": None,
    "out_degree": None,
    "depth": None,
    "lines": None,
    "function_count": None,
    "class_count": None,
    "total_changes": None,
    "author_entropy": None,
    "community": None,
}


def get_signal_color(
    name: str,
    value: float | int | bool | None,
    percentile: float | None = None,
) -> str:
    """Get color for a signal value based on polarity and percentile.

    Returns a Rich color string:
    - red/orange: Bad (high value for high_is_bad, low value for high_is_good)
    - yellow: Caution
    - green: Good
    - cyan: Neutral/informational
    """
    if value is None:
        return "dim"

    if isinstance(value, bool):
        # Boolean signals: is_orphan=True is bad
        if name == "is_orphan":
            return "red" if value else "green"
        return "cyan"

    polarity = SIGNAL_POLARITY.get(name)

    # Use percentile if available for more accurate coloring
    if percentile is not None:
        if polarity is True:  # Higher is worse
            if percentile >= 90:
                return "bold red"
            if percentile >= 75:
                return "red"
            if percentile >= 50:
                return "yellow"
            return "green"
        elif polarity is False:  # Higher is better
            if percentile >= 75:
                return "green"
            if percentile >= 50:
                return "yellow"
            if percentile >= 25:
                return "orange1"
            return "red"

    # Fallback to threshold-based coloring
    if polarity is True:  # Higher is worse
        if name == "risk_score":
            if value >= 0.7:
                return "bold red"
            if value >= 0.4:
                return "yellow"
            return "green"
        if name in ("churn_cv", "cognitive_load"):
            if value >= 1.5:
                return "bold red"
            if value >= 0.8:
                return "yellow"
            return "green"
        if name == "stub_ratio":
            if value >= 0.5:
                return "red"
            if value >= 0.3:
                return "yellow"
            return "green"
    elif polarity is False:  # Higher is better
        if name in ("wiring_quality", "file_health_score", "semantic_coherence"):
            if value >= 0.7:
                return "green"
            if value >= 0.4:
                return "yellow"
            return "red"
        if name == "bus_factor":
            if value >= 3:
                return "green"
            if value >= 2:
                return "yellow"
            return "red"

    return "cyan"  # Neutral


def format_signal_bar(
    value: float, max_value: float = 1.0, width: int = 10, color: str = "cyan"
) -> str:
    """Create a visual bar representation of a value.

    Returns a string like: '[cyan]████[/cyan][dim]░░░░░░[/dim]'
    """
    normalized = min(1.0, max(0.0, value / max_value))
    filled = int(normalized * width)
    empty = width - filled
    return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"


def format_signal_with_color(
    name: str,
    value: float | int | bool | str | None,
    percentile: float | None = None,
    show_bar: bool = False,
) -> str:
    """Format a signal value with appropriate coloring.

    Returns a Rich markup string ready for display.
    """
    if value is None:
        return "[dim]—[/dim]"

    # String values don't have polarity coloring
    if isinstance(value, str):
        return f"[cyan]{value}[/cyan]"

    color = get_signal_color(name, value, percentile)
    val_str = format_signal_value(name, value)

    result = f"[{color}]{val_str}[/{color}]"

    # Add percentile bar for key metrics
    if show_bar and percentile is not None and isinstance(value, (int, float)):
        bar = format_signal_bar(percentile / 100.0, width=8, color=color)
        result = f"{bar} {result} [dim]{percentile:.0f}th[/dim]"

    return result


# ══════════════════════════════════════════════════════════════════════════════
# Signal Interpretation (Neutral, Non-Prescriptive)
# ══════════════════════════════════════════════════════════════════════════════


def interpret_signal(name: str, value: float, percentile: float | None = None) -> str:
    """Provide a neutral interpretation of a signal value.

    This is NOT prescriptive - it describes what the value means,
    not what the developer should do about it.
    """
    interpretations: dict[str, list[tuple[float, str]]] = {
        "pagerank": [
            (0.1, "Central in the import graph - many other files depend on this"),
            (0.05, "Moderately connected in the dependency graph"),
            (0.0, "Peripheral in the dependency graph"),
        ],
        "blast_radius_size": [
            (20, "Changes here affect many files downstream"),
            (10, "Changes here have moderate downstream impact"),
            (0, "Changes here have limited downstream impact"),
        ],
        "churn_cv": [
            (1.5, "Highly variable change rate - spiky commit history"),
            (0.8, "Moderate change variability"),
            (0.0, "Consistent change rate"),
        ],
        "bus_factor": [
            (3, "Multiple contributors have worked on this code"),
            (2, "A couple of people know this code"),
            (0, "Single contributor has most knowledge here"),
        ],
        "cognitive_load": [
            (15, "High complexity - many branches and nesting"),
            (8, "Moderate complexity"),
            (0, "Low complexity"),
        ],
        "risk_score": [
            (0.7, "Multiple risk signals are elevated"),
            (0.4, "Some risk signals are present"),
            (0.0, "Risk signals are low"),
        ],
    }

    if name not in interpretations:
        return ""

    thresholds = interpretations[name]
    for threshold, text in thresholds:
        if value >= threshold:
            return text

    return thresholds[-1][1]  # Default to lowest threshold interpretation
