"""Shannon Insight TUI - Interactive developer-focused interface.

Design philosophy: Feels like lazygit/k9s - keyboard-driven, discoverable, forgiving.

Key UX principles:
1. Show answer first, teach on-demand - Focus view immediately, help via ?
2. Arrow keys + Enter - Navigate lists, drill into details
3. ESC always goes back - Never leaves user stranded
4. Breadcrumb shows location - Know where you are
5. Footer shows keys - Discoverable without memorization

Layout:
┌─────────────────────────────────────────────────────────────────────┐
│ SHANNON INSIGHT — 218 files · 102 findings · Moderate health        │
│ [Focus] > insights/models.py                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  (Interactive content area - DataTable/OptionList/Detail)           │
│                                                                     │
│  ↑/↓ navigate   Enter drill-down   ESC back                         │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ h Hotspots  f Findings  s Signals  ? Help  q Quit                   │
└─────────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, OptionList, Rule, Static
from textual.widgets.option_list import Option

if TYPE_CHECKING:
    from ..insights.models import Finding, InsightResult
    from ..persistence.models import TensorSnapshot


# ══════════════════════════════════════════════════════════════════════════════
# Path Formatting
# ══════════════════════════════════════════════════════════════════════════════


def short_path(path: str, max_parts: int = 3) -> str:
    """Show last N path segments. Simple and readable."""
    parts = Path(path).parts
    if len(parts) <= max_parts:
        return path
    return str(Path(*parts[-max_parts:]))


def file_name(path: str) -> str:
    """Just the filename."""
    return Path(path).name


# ══════════════════════════════════════════════════════════════════════════════
# Severity & Health Helpers
# ══════════════════════════════════════════════════════════════════════════════


def health_label(score: float) -> tuple[str, str]:
    """Return (label, color) for health score 0-1."""
    if score >= 0.8:
        return "Good health", "green"
    if score >= 0.6:
        return "Moderate health", "yellow"
    if score >= 0.4:
        return "Needs attention", "orange1"
    return "Poor health", "red"


def risk_color(score: float) -> str:
    """Color for risk score."""
    if score >= 0.7:
        return "red"
    if score >= 0.4:
        return "yellow"
    return "green"


def percentile_to_level(pctl: float | None) -> tuple[str, str]:
    """Convert percentile to human label and color."""
    if pctl is None:
        return "—", "dim"
    if pctl >= 90:
        return "Very high", "red"
    if pctl >= 70:
        return "High", "yellow"
    if pctl >= 30:
        return "Moderate", "white"
    return "Low", "dim"


def _finding_category(finding_type: str) -> str:
    """Map finding type to category."""
    categories = {
        "coupling": {"hidden_coupling", "accidental_coupling"},
        "structural": {"phantom_imports", "orphan_code", "hollow_code", "dead_dependency"},
        "risk": {"high_risk_hub", "bug_attractor", "unstable_file", "thrashing_code"},
        "complexity": {"god_file", "copy_paste_clone", "naming_drift"},
        "architecture": {
            "layer_violation",
            "zone_of_pain",
            "boundary_mismatch",
            "flat_architecture",
        },
        "team": {"knowledge_silo", "review_blindspot", "chronic_problem", "truck_factor"},
    }
    for cat, types in categories.items():
        if finding_type in types:
            return cat
    return "other"


# ══════════════════════════════════════════════════════════════════════════════
# Navigation State
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class NavState:
    """Tracks navigation position for breadcrumb and back navigation."""

    view: str  # "focus", "hotspots", "findings", "signals", "detail"
    label: str  # Display in breadcrumb
    context: dict = field(default_factory=dict)  # {"path": "...", "finding_id": "..."}


# ══════════════════════════════════════════════════════════════════════════════
# Custom Messages
# ══════════════════════════════════════════════════════════════════════════════


class DrillDown(Message):
    """Request to drill into a file detail."""

    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = path


class NavigateBack(Message):
    """Request to go back in navigation stack."""


# ══════════════════════════════════════════════════════════════════════════════
# Views
# ══════════════════════════════════════════════════════════════════════════════


class FocusView(Container):
    """The main 'START HERE' view - explains what we found and where to focus."""

    BINDINGS = [
        Binding("enter", "select_item", "Select", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self, result: InsightResult, snapshot: TensorSnapshot) -> None:
        super().__init__(id="focus-view")
        self.result = result
        self.snapshot = snapshot

    def compose(self) -> ComposeResult:
        from ._hotspots import identify_hotspots

        finding_count = len(self.result.findings)
        high_sev = sum(1 for f in self.result.findings if f.severity >= 0.8)

        # Summary explanation
        if finding_count == 0:
            yield Static("[green bold]No issues found[/green bold]\n")
            yield Static(
                "Your codebase looks healthy. No structural issues or risk patterns detected."
            )
            return

        yield Static("[bold]WHAT WE FOUND[/bold]\n")

        if high_sev > 0:
            yield Static(f"  [red]{high_sev}[/red] high-severity issues that may need attention")
        if finding_count - high_sev > 0:
            yield Static(
                f"  [yellow]{finding_count - high_sev}[/yellow] lower-severity observations"
            )

        # Categorize and explain
        categories: dict[str, list] = {}
        for f in self.result.findings:
            cat = _finding_category(f.finding_type)
            categories.setdefault(cat, []).append(f)

        yield Static("")

        # Brief category explanations
        cat_explanations = {
            "coupling": "Files that are too tightly coupled or have hidden dependencies",
            "structural": "Orphan code, phantom imports, or dead dependencies",
            "risk": "High-traffic files that may be fragile or error-prone",
            "complexity": "Files that are large, complex, or have naming inconsistencies",
            "architecture": "Layer violations or boundary misalignment",
            "team": "Knowledge silos or review coverage gaps",
        }

        for cat, findings in sorted(categories.items(), key=lambda x: -len(x[1])):
            if cat in cat_explanations:
                yield Static(f"  [dim]•[/dim] {len(findings)} {cat}: {cat_explanations[cat]}")

        yield Static("")

        # Get hotspots for recommendations
        self._hotspots = identify_hotspots(self.snapshot, self.result.findings, n=20)
        self._findings_by_file: dict[str, list] = {}
        for f in self.result.findings:
            for p in f.files:
                self._findings_by_file.setdefault(p, []).append(f)

        if not self._hotspots:
            yield Static("[dim]No specific files to prioritize.[/dim]")
            return

        yield Static("[bold cyan]WHERE TO START[/bold cyan]")
        yield Static("[dim]These files have the highest combination of risk signals:[/dim]")
        yield Static("")

        option_list = OptionList(id="focus-list")
        yield option_list

        yield Static("")
        yield Static(
            "[dim]↑/↓ navigate · Enter for details · h all hotspots · f all findings[/dim]"
        )

    def on_mount(self) -> None:
        """Populate the option list after mounting."""
        if not self._hotspots:
            return

        option_list = self.query_one("#focus-list", OptionList)

        # Top recommendation
        top = self._hotspots[0]
        top_findings = self._findings_by_file.get(top.path, [])

        why_parts = []
        if top_findings:
            why_parts.append(f"{len(top_findings)} finding{'s' if len(top_findings) != 1 else ''}")
        why_parts.append(f"blast={top.blast_radius}")
        why_parts.append(f"changes={top.total_changes}")

        option_list.add_option(
            Option(
                f"[bold]#1[/bold]  {short_path(top.path)}\n    [dim]{' · '.join(why_parts)}[/dim]",
                id=top.path,
            )
        )

        # ALSO CONSIDER
        if len(self._hotspots) > 1:
            option_list.add_option(None)  # Separator
            for i, hs in enumerate(self._hotspots[1:10], start=2):
                hs_findings = self._findings_by_file.get(hs.path, [])
                finding_str = (
                    f"{len(hs_findings)} finding{'s' if len(hs_findings) != 1 else ''}"
                    if hs_findings
                    else ""
                )
                score_str = f"[{risk_color(hs.score)}]{hs.score:.3f}[/]"
                extra = f" · {finding_str}" if finding_str else ""

                option_list.add_option(
                    Option(
                        f"[dim]#{i:2d}[/dim]  {short_path(hs.path)}  {score_str}{extra}",
                        id=hs.path,
                    )
                )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle file selection."""
        if event.option_id:
            self.post_message(DrillDown(str(event.option_id)))

    def action_select_item(self) -> None:
        """Select current item."""
        try:
            option_list = self.query_one("#focus-list", OptionList)
            if option_list.highlighted is not None:
                option = option_list.get_option_at_index(option_list.highlighted)
                if option.id:
                    self.post_message(DrillDown(str(option.id)))
        except Exception:
            pass

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        try:
            option_list = self.query_one("#focus-list", OptionList)
            option_list.action_cursor_down()
        except Exception:
            pass

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        try:
            option_list = self.query_one("#focus-list", OptionList)
            option_list.action_cursor_up()
        except Exception:
            pass


class HotspotsView(Container):
    """Hotspots view with interactive DataTable."""

    BINDINGS = [
        Binding("enter", "select_row", "Select", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self, result: InsightResult, snapshot: TensorSnapshot) -> None:
        super().__init__(id="hotspots-view")
        self.result = result
        self.snapshot = snapshot

    def compose(self) -> ComposeResult:
        yield Static("[bold]HOTSPOTS[/bold] — files with highest combined risk signals\n")

        table: DataTable[str] = DataTable(
            id="hotspots-table", cursor_type="row", zebra_stripes=True
        )
        yield table

        yield Static("")
        yield Static(
            "[dim]Score = PageRank(30%) + Churn(25%) + CV(20%) + Blast(15%) + Issues(10%)[/dim]"
        )
        yield Static("[dim]↑/↓ navigate · Enter select · ESC back[/dim]")

    def on_mount(self) -> None:
        """Populate the DataTable after mounting."""
        from ._hotspots import identify_hotspots

        table = self.query_one("#hotspots-table", DataTable)

        # Add columns
        table.add_column("#", width=4)
        table.add_column("File", width=38)
        table.add_column("Score", width=8)
        table.add_column("PR", width=6)
        table.add_column("Chg", width=5)
        table.add_column("Blast", width=6)
        table.add_column("Issues", width=7)

        hotspots = identify_hotspots(self.snapshot, self.result.findings, n=30)

        # Count findings per file
        findings_by_file: dict[str, int] = {}
        for f in self.result.findings:
            for p in f.files:
                findings_by_file[p] = findings_by_file.get(p, 0) + 1

        for hs in hotspots:
            path_display = short_path(hs.path, max_parts=2)
            if len(path_display) > 36:
                path_display = "…" + path_display[-35:]

            score_color = risk_color(hs.score)
            issue_count = findings_by_file.get(hs.path, 0)
            issues_str = str(issue_count) if issue_count else "-"

            table.add_row(
                str(hs.rank),
                path_display,
                f"[{score_color}]{hs.score:.3f}[/]",
                f"{hs.pagerank:.2f}",
                str(hs.total_changes),
                str(hs.blast_radius),
                issues_str,
                key=hs.path,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        if event.row_key:
            self.post_message(DrillDown(str(event.row_key.value)))

    def action_select_row(self) -> None:
        """Select current row."""
        try:
            table = self.query_one("#hotspots-table", DataTable)
            if table.cursor_row is not None:
                cursor = table.cursor_coordinate
                cell_key = table.coordinate_to_cell_key(cursor)
                if cell_key.row_key:
                    self.post_message(DrillDown(str(cell_key.row_key.value)))
        except Exception:
            pass

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        try:
            table = self.query_one("#hotspots-table", DataTable)
            table.action_cursor_down()
        except Exception:
            pass

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        try:
            table = self.query_one("#hotspots-table", DataTable)
            table.action_cursor_up()
        except Exception:
            pass


class FindingsView(Container):
    """All findings grouped by category with explanations."""

    BINDINGS = [
        Binding("enter", "select_item", "Select", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self, result: InsightResult, snapshot: TensorSnapshot) -> None:
        super().__init__(id="findings-view")
        self.result = result
        self.snapshot = snapshot
        self._finding_paths: dict[str, str] = {}  # option_id -> first file path

    def compose(self) -> ComposeResult:
        findings = self.result.findings

        yield Static(f"[bold]ALL FINDINGS[/bold] — {len(findings)} issues detected\n")

        if not findings:
            yield Static("[green]No issues found. Your codebase looks healthy![/green]")
            return

        # Category explanations
        yield Static("[dim]Organized by category to help you understand patterns:[/dim]")
        yield Static("")

        option_list = OptionList(id="findings-list")
        yield option_list

        yield Static("")
        yield Static("[dim]↑/↓ navigate · Enter for file details · ESC back[/dim]")

    def on_mount(self) -> None:
        """Populate the option list after mounting."""
        findings = self.result.findings
        if not findings:
            return

        option_list = self.query_one("#findings-list", OptionList)

        # Group by category
        by_cat: dict[str, list] = {}
        for f in findings:
            cat = _finding_category(f.finding_type)
            by_cat.setdefault(cat, []).append(f)

        # Category metadata
        cat_info = {
            "risk": ("RISK", "red", "Files that may be fragile or error-prone"),
            "coupling": ("COUPLING", "yellow", "Dependencies that may cause cascading changes"),
            "structural": ("STRUCTURAL", "cyan", "Code organization issues"),
            "complexity": ("COMPLEXITY", "magenta", "Hard-to-maintain code"),
            "architecture": ("ARCHITECTURE", "blue", "Design pattern violations"),
            "team": ("TEAM", "green", "Knowledge distribution issues"),
            "other": ("OTHER", "dim", "Miscellaneous findings"),
        }

        # Order by severity (risk first)
        cat_order = [
            "risk",
            "coupling",
            "complexity",
            "structural",
            "architecture",
            "team",
            "other",
        ]
        idx = 0

        for cat in cat_order:
            if cat not in by_cat:
                continue

            findings_in_cat = sorted(by_cat[cat], key=lambda f: -f.severity)
            title, color, desc = cat_info.get(cat, (cat.upper(), "white", ""))

            # Category header with explanation
            high_count = sum(1 for f in findings_in_cat if f.severity >= 0.8)
            if high_count > 0:
                header = f"[{color} bold]{title} ({len(findings_in_cat)})[/] — [red]{high_count} high[/red]"
            else:
                header = f"[{color} bold]{title} ({len(findings_in_cat)})[/]"

            option_list.add_option(Option(header, disabled=True))
            option_list.add_option(Option(f"  [dim]{desc}[/dim]", disabled=True))

            # Findings in this category
            for f in findings_in_cat[:15]:
                self._add_finding_option(option_list, f, f"f_{idx}")
                idx += 1

            if len(findings_in_cat) > 15:
                option_list.add_option(
                    Option(f"  [dim]... and {len(findings_in_cat) - 15} more[/dim]", disabled=True)
                )

            option_list.add_option(None)  # Separator

    def _add_finding_option(self, option_list: OptionList, f: Finding, option_id: str) -> None:
        """Add a finding as an option."""
        type_name = f.finding_type.replace("_", " ").title()
        sev_marker = (
            "[red]![/red]"
            if f.severity >= 0.8
            else "[yellow]·[/yellow]"
            if f.severity >= 0.6
            else "[dim]·[/dim]"
        )

        if f.files:
            file_str = short_path(f.files[0])
            if len(f.files) > 1:
                file_str += f" +{len(f.files) - 1}"
            self._finding_paths[option_id] = f.files[0]
        else:
            file_str = "(codebase-wide)"
            self._finding_paths[option_id] = ""

        option_list.add_option(
            Option(f"  {sev_marker} {type_name}: [cyan]{file_str}[/cyan]", id=option_id)
        )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle finding selection."""
        if event.option_id:
            path = self._finding_paths.get(str(event.option_id), "")
            if path:
                self.post_message(DrillDown(path))

    def action_select_item(self) -> None:
        """Select current item."""
        try:
            option_list = self.query_one("#findings-list", OptionList)
            if option_list.highlighted is not None:
                option = option_list.get_option_at_index(option_list.highlighted)
                if option.id:
                    path = self._finding_paths.get(str(option.id), "")
                    if path:
                        self.post_message(DrillDown(path))
        except Exception:
            pass

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        try:
            option_list = self.query_one("#findings-list", OptionList)
            option_list.action_cursor_down()
        except Exception:
            pass

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        try:
            option_list = self.query_one("#findings-list", OptionList)
            option_list.action_cursor_up()
        except Exception:
            pass


class SignalsView(ScrollableContainer):
    """Global signals view (read-only, scrollable)."""

    def __init__(self, result: InsightResult, snapshot: TensorSnapshot) -> None:
        super().__init__(id="signals-view")
        self.result = result
        self.snapshot = snapshot

    def compose(self) -> ComposeResult:
        gs = self.snapshot.global_signals or {}

        yield Static("[bold]CODEBASE SIGNALS[/bold]\n")

        # Architecture
        yield Static("[bold]Architecture[/bold]")
        for name, label in [
            ("modularity", "Modularity"),
            ("cycle_count", "Dependency cycles"),
            ("centrality_gini", "Centrality inequality"),
            ("architecture_health", "Architecture health"),
        ]:
            if name in gs:
                val = gs[name]
                if name == "architecture_health":
                    val_str = f"{val * 10:.1f}/10"
                elif isinstance(val, float):
                    val_str = f"{val:.3f}"
                else:
                    val_str = str(val)
                yield Static(f"  {label:.<30} {val_str:>10}")

        yield Static("")

        # Code health
        yield Static("[bold]Code Health[/bold]")
        for name, label in [
            ("orphan_ratio", "Orphan files"),
            ("phantom_ratio", "Phantom imports"),
            ("wiring_score", "Wiring quality"),
            ("codebase_health", "Codebase health"),
        ]:
            if name in gs:
                val = gs[name]
                if name == "codebase_health":
                    val_str = f"{val * 10:.1f}/10"
                elif "ratio" in name:
                    val_str = f"{val * 100:.1f}%"
                elif isinstance(val, float):
                    val_str = f"{val:.3f}"
                else:
                    val_str = str(val)
                yield Static(f"  {label:.<30} {val_str:>10}")

        yield Static("")

        # Top files by risk
        yield Static("[bold]Top Files by Risk[/bold]")
        file_signals = self.snapshot.file_signals or {}
        sorted_files = sorted(
            file_signals.items(),
            key=lambda x: x[1].get("risk_score", 0),
            reverse=True,
        )[:10]

        for path, sigs in sorted_files:
            risk = sigs.get("risk_score", 0)
            churn = sigs.get("total_changes", 0)
            color = risk_color(risk)
            yield Static(
                f"  [{color}]{risk:.3f}[/{color}] {short_path(path):<35} [dim]Δ{churn}[/dim]"
            )

        yield Static("")
        yield Static("[dim]ESC back[/dim]")


class DetailView(ScrollableContainer):
    """Detail view for selected file - structured explanation of what we found."""

    def __init__(self, path: str, result: InsightResult, snapshot: TensorSnapshot) -> None:
        super().__init__(id="detail-view")
        self.path = path
        self.result = result
        self.snapshot = snapshot

    def compose(self) -> ComposeResult:
        yield Static(f"[bold cyan]{self.path}[/bold cyan]\n")

        sigs = self.snapshot.file_signals.get(self.path, {})
        if not sigs:
            yield Static("[dim]No analysis data available for this file.[/dim]")
            yield Static("")
            yield Static("[dim]ESC back[/dim]")
            return

        # ── RISK SUMMARY ──
        yield Static("[bold]RISK SUMMARY[/bold]")
        risk_pctl = sigs.get("risk_score_percentile")
        if risk_pctl is not None and risk_pctl >= 90:
            yield Static(
                f"  [red]High risk[/red] — This file is in the top {100 - risk_pctl:.0f}% of risky files"
            )
        elif risk_pctl is not None and risk_pctl >= 70:
            yield Static("  [yellow]Elevated risk[/yellow] — Above average for this codebase")
        else:
            yield Static("  [green]Normal risk[/green] — No unusual risk signals")

        # Quick why
        why_parts = []
        if sigs.get("cognitive_load_percentile", 0) >= 80:
            why_parts.append("complex code")
        if sigs.get("blast_radius_size_percentile", 0) >= 80:
            why_parts.append("many dependents")
        if sigs.get("total_changes_percentile", 0) >= 80:
            why_parts.append("frequently changed")
        if why_parts:
            yield Static(f"  [dim]Contributing factors: {', '.join(why_parts)}[/dim]")
        yield Static("")

        # ── COMPLEXITY ──
        yield Static("[bold]COMPLEXITY[/bold] — How hard is this code to work with?")

        cog = sigs.get("cognitive_load")
        cog_pctl = sigs.get("cognitive_load_percentile")
        if cog is not None:
            if cog_pctl is not None and cog_pctl >= 90:
                yield Static(
                    f"  [red]Very complex[/red] — cognitive load {cog:.1f} (top {100 - cog_pctl:.0f}%)"
                )
                yield Static(
                    "  [dim]This file may be difficult to understand and modify safely[/dim]"
                )
            elif cog_pctl is not None and cog_pctl >= 70:
                yield Static(f"  [yellow]Complex[/yellow] — cognitive load {cog:.1f}")
            else:
                yield Static(f"  [green]Manageable[/green] — cognitive load {cog:.1f}")

        coherence = sigs.get("semantic_coherence")
        coherence_pctl = sigs.get("semantic_coherence_percentile")
        if coherence is not None:
            if coherence_pctl is not None and coherence_pctl <= 20:
                yield Static(f"  [yellow]Unfocused[/yellow] — coherence {coherence:.2f} (low)")
                yield Static("  [dim]This file may be doing too many things[/dim]")
            elif coherence_pctl is not None and coherence_pctl >= 70:
                yield Static(f"  [green]Focused[/green] — coherence {coherence:.2f}")

        lines = sigs.get("lines", 0)
        funcs = sigs.get("function_count", 0)
        if lines:
            yield Static(f"  [dim]{lines} lines · {funcs} functions[/dim]")
        yield Static("")

        # ── IMPORTANCE ──
        yield Static("[bold]IMPORTANCE[/bold] — How central is this file?")

        pr_pctl = sigs.get("pagerank_percentile")
        blast = sigs.get("blast_radius_size", 0)
        in_deg = sigs.get("in_degree", 0)
        out_deg = sigs.get("out_degree", 0)

        if pr_pctl is not None and pr_pctl >= 90:
            yield Static(f"  [cyan]Critical hub[/cyan] — top {100 - pr_pctl:.0f}% most connected")
            yield Static("  [dim]Changes here have wide impact; review carefully[/dim]")
        elif pr_pctl is not None and pr_pctl >= 70:
            yield Static("  [white]Well-connected[/white] — above average centrality")
        else:
            yield Static("  [dim]Peripheral[/dim] — not a central dependency")

        if blast > 0:
            yield Static(f"  [dim]{blast} files depend on this (blast radius)[/dim]")
        yield Static(f"  [dim]imports {out_deg} · imported by {in_deg}[/dim]")
        yield Static("")

        # ── CHANGE HISTORY ──
        yield Static("[bold]CHANGE HISTORY[/bold] — What's the activity pattern?")

        changes = sigs.get("total_changes", 0)
        changes_pctl = sigs.get("total_changes_percentile")
        cv = sigs.get("churn_cv")
        bus = sigs.get("bus_factor")

        if changes_pctl is not None and changes_pctl >= 90:
            yield Static(
                f"  [yellow]Hotspot[/yellow] — {changes} changes (top {100 - changes_pctl:.0f}% most active)"
            )
            yield Static(
                "  [dim]Frequent changes may indicate instability or active development[/dim]"
            )
        elif changes > 0:
            yield Static(f"  [dim]{changes} changes in recent history[/dim]")
        else:
            yield Static("  [dim]No recent changes[/dim]")

        if cv is not None and cv > 1.5:
            yield Static(f"  [yellow]Unstable[/yellow] — change pattern is erratic (CV={cv:.1f})")
        elif cv is not None:
            yield Static(
                f"  [dim]Change pattern: {'stable' if cv < 0.5 else 'normal'} (CV={cv:.1f})[/dim]"
            )

        if bus is not None:
            if bus <= 1.5:
                yield Static(
                    f"  [yellow]Bus factor: {bus:.1f}[/yellow] — knowledge concentrated in few people"
                )
            else:
                yield Static(f"  [dim]Bus factor: {bus:.1f}[/dim]")
        yield Static("")

        # ── FINDINGS ──
        file_findings = [f for f in self.result.findings if self.path in f.files]
        if file_findings:
            yield Static(f"[bold]FINDINGS ({len(file_findings)})[/bold] — Issues detected")
            for f in file_findings:
                type_name = f.finding_type.replace("_", " ").title()
                sev_color = "red" if f.severity >= 0.8 else "yellow" if f.severity >= 0.6 else "dim"
                yield Static(f"  [{sev_color}]•[/{sev_color}] {type_name}")
                if f.suggestion:
                    # Show first sentence of suggestion
                    suggestion = f.suggestion.split(".")[0]
                    yield Static(f"    [dim]{suggestion}[/dim]")
        else:
            yield Static("[dim]No specific issues detected for this file.[/dim]")

        yield Static("")
        yield Static("[dim]ESC back[/dim]")


class HelpOverlay(Container):
    """Full-screen help overlay."""

    DEFAULT_CSS = """
    HelpOverlay {
        align: center middle;
        background: $surface 90%;
        width: 100%;
        height: 100%;
    }

    #help-content {
        width: 60;
        height: auto;
        max-height: 80%;
        background: $panel;
        border: round $primary;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="help-content"):
            yield Static("[bold cyan]KEYBOARD SHORTCUTS[/bold cyan]\n")

            yield Static("[bold]Navigation[/bold]")
            yield Static("  ↑/↓, j/k    Move up/down")
            yield Static("  Enter       Drill into selection")
            yield Static("  ESC, b      Go back")
            yield Static("")

            yield Static("[bold]Views[/bold]")
            yield Static("  h           Hotspots (ranked files)")
            yield Static("  f           Findings (all issues)")
            yield Static("  s           Signals (codebase metrics)")
            yield Static("  o           Focus (start here)")
            yield Static("")

            yield Static("[bold]Other[/bold]")
            yield Static("  ?           Toggle this help")
            yield Static("  q           Quit")
            yield Static("")

            yield Rule()
            yield Static("[dim]Press ? or ESC to close[/dim]")


# ══════════════════════════════════════════════════════════════════════════════
# Main Application
# ══════════════════════════════════════════════════════════════════════════════


class ShannonApp(App):
    """Shannon Insight TUI - Interactive and discoverable."""

    TITLE = "Shannon Insight"

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        width: 100%;
        height: 100%;
    }

    #header-bar {
        dock: top;
        height: 3;
        padding: 0 2;
        background: $primary-background;
    }

    #header-title {
        width: 100%;
    }

    #breadcrumb {
        width: 100%;
        color: $text-muted;
    }

    #content-area {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #focus-view, #hotspots-view, #findings-view, #signals-view, #detail-view {
        width: 100%;
        height: 100%;
    }

    #help-overlay {
        layer: overlay;
    }

    .hidden {
        display: none;
    }

    DataTable {
        height: auto;
        max-height: 70%;
    }

    OptionList {
        height: auto;
        max-height: 60%;
    }

    DataTable > .datatable--cursor {
        background: $accent;
    }

    OptionList > .option-list--option-highlighted {
        background: $accent;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "back", "Back", priority=True),
        Binding("b", "back", "Back", show=False),
        Binding("o", "focus_view", "Focus"),
        Binding("h", "hotspots", "Hotspots"),
        Binding("f", "findings", "Findings"),
        Binding("s", "signals", "Signals"),
        Binding("question_mark", "toggle_help", "Help"),
    ]

    current_view = reactive("focus")
    show_help = reactive(False)

    def __init__(self, result: InsightResult, snapshot: TensorSnapshot) -> None:
        super().__init__()
        self.result = result
        self.snapshot = snapshot
        self.nav_stack: list[NavState] = [NavState("focus", "Focus")]
        self._detail_view: DetailView | None = None

    def compose(self) -> ComposeResult:
        gs = getattr(self.snapshot, "global_signals", {}) or {}
        health = gs.get("codebase_health", 0.5)
        label, color = health_label(health)

        file_count = len(self.snapshot.file_signals or {})
        finding_count = len(self.result.findings)

        with Container(id="main-container"):
            with Container(id="header-bar"):
                yield Static(
                    f"[bold cyan]SHANNON INSIGHT[/bold cyan] — {file_count} files · {finding_count} findings · [{color}]{label}[/]",
                    id="header-title",
                )
                yield Static("", id="breadcrumb")

            with Container(id="content-area"):
                yield FocusView(self.result, self.snapshot)
                yield HotspotsView(self.result, self.snapshot)
                yield FindingsView(self.result, self.snapshot)
                yield SignalsView(self.result, self.snapshot)

            yield HelpOverlay(id="help-overlay", classes="hidden")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize views and show onboarding."""
        self._switch_view("focus")
        self._update_breadcrumb()

        # Onboarding hint for first launch
        self.notify(
            "↑/↓ to navigate · Enter to drill down · ? for help",
            title="Welcome to Shannon Insight",
            timeout=5,
        )

    def _update_breadcrumb(self) -> None:
        """Update the breadcrumb display from nav stack."""
        try:
            breadcrumb = self.query_one("#breadcrumb", Static)
            parts = [f"[bold][{s.label}][/bold]" for s in self.nav_stack]
            breadcrumb.update(" > ".join(parts))
        except Exception:
            pass

    def _switch_view(self, view_name: str) -> None:
        """Switch to a different view."""
        views = ["focus", "hotspots", "findings", "signals", "detail"]

        for v in views:
            try:
                widget = self.query_one(f"#{v}-view")
                if v == view_name:
                    widget.remove_class("hidden")
                    # Reset scroll position
                    if hasattr(widget, "scroll_home"):
                        widget.scroll_home()
                else:
                    widget.add_class("hidden")
            except Exception:
                pass  # View might not exist yet

        self.current_view = view_name

    def _push_nav(self, view: str, label: str, **context) -> None:
        """Push a new navigation state."""
        self.nav_stack.append(NavState(view, label, context))
        self._update_breadcrumb()

    def _pop_nav(self) -> bool:
        """Pop navigation state. Returns True if popped, False if at root."""
        if len(self.nav_stack) > 1:
            self.nav_stack.pop()
            self._update_breadcrumb()
            return True
        return False

    async def _show_detail(self, path: str) -> None:
        """Show detail view for a file."""
        # Remove existing detail view if any
        try:
            existing = self.query_one("#detail-view")
            await existing.remove()
        except Exception:
            pass

        # Create and mount new detail view
        content_area = self.query_one("#content-area")
        self._detail_view = DetailView(path, self.result, self.snapshot)
        await content_area.mount(self._detail_view)

        # Switch to it
        self._switch_view("detail")
        self._push_nav("detail", file_name(path), path=path)

    async def on_drill_down(self, message: DrillDown) -> None:
        """Handle drill-down requests."""
        await self._show_detail(message.path)

    async def action_back(self) -> None:
        """Go back in navigation stack."""
        # Close help if open
        if self.show_help:
            self.show_help = False
            return

        # Pop navigation
        if self._pop_nav():
            prev = self.nav_stack[-1]
            self._switch_view(prev.view)

    def action_focus_view(self) -> None:
        """Show focus view."""
        # Reset to focus
        self.nav_stack = [NavState("focus", "Focus")]
        self._update_breadcrumb()
        self._switch_view("focus")

    def action_hotspots(self) -> None:
        """Show hotspots view."""
        self.nav_stack = [NavState("hotspots", "Hotspots")]
        self._update_breadcrumb()
        self._switch_view("hotspots")

    def action_findings(self) -> None:
        """Show findings view."""
        self.nav_stack = [NavState("findings", "Findings")]
        self._update_breadcrumb()
        self._switch_view("findings")

    def action_signals(self) -> None:
        """Show signals view."""
        self.nav_stack = [NavState("signals", "Signals")]
        self._update_breadcrumb()
        self._switch_view("signals")

    def action_toggle_help(self) -> None:
        """Toggle help overlay."""
        self.show_help = not self.show_help

    def watch_show_help(self, show: bool) -> None:
        """React to help visibility changes."""
        try:
            help_overlay = self.query_one("#help-overlay")
            if show:
                help_overlay.remove_class("hidden")
            else:
                help_overlay.add_class("hidden")
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════════════


def run_tui(target: Path, settings, console=None) -> tuple:
    """Run analysis and launch TUI."""
    import sys

    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

    from ..insights import InsightKernel

    console = console or Console()

    if not sys.stdin.isatty():
        console.print("[red]TUI requires interactive terminal. Use --no-tui.[/]")
        raise SystemExit(1)

    console.print()
    console.print("[bold cyan]SHANNON INSIGHT[/] — Analyzing codebase...")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="cyan", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Starting...", total=100)

        kernel = InsightKernel(
            str(target), language="auto", settings=settings, enable_persistence_finders=True
        )

        phase_pct = {
            "scan": 10,
            "pars": 25,
            "depend": 40,
            "graph": 45,
            "structur": 50,
            "temporal": 60,
            "git": 65,
            "signal": 75,
            "fusion": 80,
            "comput": 85,
            "detect": 90,
            "finding": 95,
        }

        def update(msg):
            progress.update(task, description=msg[:50])
            for key, pct in phase_pct.items():
                if key in msg.lower():
                    progress.update(task, completed=pct)
                    break

        result, snapshot = kernel.run(max_findings=100, on_progress=update)
        progress.update(task, completed=100, description="Analysis complete!")

    issue_count = len(result.findings)
    if issue_count == 0:
        console.print("[green]✓[/] No issues found!")
    else:
        high = sum(1 for f in result.findings if f.severity >= 0.8)
        console.print(
            f"[yellow]![/] Found {issue_count} finding{'s' if issue_count != 1 else ''} ({high} high severity)"
        )

    console.print()
    console.print("[dim]Launching interactive view... (press ? for help, q to quit)[/]")
    console.print()

    app = ShannonApp(result, snapshot)
    try:
        app.run()
    except KeyboardInterrupt:
        console.print("\n[dim]Exited.[/]")
    except Exception as e:
        console.print(f"\n[red]TUI error:[/] {e}")
        console.print("[dim]Use --no-tui for CLI output.[/]")

    return result, snapshot
