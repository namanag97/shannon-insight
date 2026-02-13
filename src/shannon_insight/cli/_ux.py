"""Radical UX improvements for Shannon Insight CLI.

Inspired by modern tools: ruff, uv, gh, cargo.
"""

import difflib
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from rich.console import Console
from rich.style import Style
from rich.text import Text

# ---------------------------------------------------------------------------
# Exit Codes (semantic, CI-friendly)
# ---------------------------------------------------------------------------


class ExitCode:
    """Semantic exit codes for CI observability.

    Ranges:
      0: Success
      1-9: Finding-based failures
      80-89: User errors (bad input)
      100+: Internal errors
    """

    SUCCESS = 0
    FINDINGS_EXIST = 1
    HIGH_SEVERITY = 2
    BAD_USAGE = 80
    CONFIG_ERROR = 81
    PATH_NOT_FOUND = 82
    GIT_ERROR = 83
    INTERNAL_ERROR = 100


# ---------------------------------------------------------------------------
# Terminal Hyperlinks (OSC 8)
# ---------------------------------------------------------------------------


def supports_hyperlinks() -> bool:
    """Check if terminal supports OSC 8 hyperlinks.

    Supported: iTerm2, Kitty, WezTerm, Windows Terminal, GNOME Terminal (VTE 0.50+)
    """
    if not sys.stdout.isatty():
        return False

    # Check known supporting terminals
    term_program = os.environ.get("TERM_PROGRAM", "")
    term = os.environ.get("TERM", "")
    wt_session = os.environ.get("WT_SESSION", "")  # Windows Terminal

    if term_program in ("iTerm.app", "WezTerm", "vscode"):
        return True
    if "kitty" in term.lower():
        return True
    if wt_session:  # Windows Terminal sets this
        return True
    if os.environ.get("VTE_VERSION", ""):
        # GNOME Terminal / VTE-based
        try:
            vte = int(os.environ["VTE_VERSION"])
            return vte >= 5000  # VTE 0.50+
        except ValueError:
            pass

    return False


def hyperlink(url: str, text: str) -> str:
    """Create OSC 8 terminal hyperlink.

    Returns plain text if terminal doesn't support hyperlinks.
    """
    if not supports_hyperlinks():
        return text
    # OSC 8 ; params ; URI ST text OSC 8 ; ; ST
    return f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\"


def file_link(path: str, line: Optional[int] = None, col: Optional[int] = None) -> str:
    """Create clickable file:line:col reference.

    Uses file:// protocol which opens in default editor for most terminals.
    """
    abs_path = Path(path).resolve()
    display = path

    if line:
        display = f"{path}:{line}"
        if col:
            display = f"{path}:{line}:{col}"

    # file:// URL - some editors (VSCode) support line numbers
    url = f"file://{abs_path}"
    if line:
        # VSCode and some editors support #L<line>
        url = f"{url}#L{line}"

    return hyperlink(url, display)


def rich_file_link(path: str, line: Optional[int] = None, style: str = "cyan") -> Text:
    """Create Rich Text with hyperlink for terminal rendering."""
    display = path
    if line:
        display = f"{path}:{line}"

    text = Text(display, style=style)

    if supports_hyperlinks():
        abs_path = Path(path).resolve()
        url = f"file://{abs_path}"
        if line:
            url = f"{url}#L{line}"
        text.stylize(Style(link=url))

    return text


# ---------------------------------------------------------------------------
# Timing Display
# ---------------------------------------------------------------------------


@dataclass
class AnalysisTimer:
    """Track analysis timing for display."""

    start_time: float
    file_count: int = 0
    loc_count: int = 0
    module_count: int = 0
    commit_count: int = 0

    @classmethod
    def start(cls) -> "AnalysisTimer":
        return cls(start_time=time.perf_counter())

    def elapsed(self) -> float:
        return time.perf_counter() - self.start_time

    def summary_line(self) -> str:
        """Generate timing summary: '✓ Analyzed 234 files in 0.8s'"""
        elapsed = self.elapsed()

        parts = [f"{self.file_count} files"]
        if self.loc_count:
            parts.append(f"{self.loc_count:,} LOC")
        if self.module_count:
            parts.append(f"{self.module_count} modules")
        if self.commit_count:
            parts.append(f"{self.commit_count} commits")

        return f"✓ Analyzed {' • '.join(parts)} in {elapsed:.1f}s"


# ---------------------------------------------------------------------------
# "Did You Mean?" Suggestions
# ---------------------------------------------------------------------------


def did_you_mean(
    unknown: str,
    candidates: list[str],
    threshold: float = 0.6,
    max_suggestions: int = 3,
) -> list[str]:
    """Find similar strings using Damerau-Levenshtein distance.

    Args:
        unknown: The unrecognized input
        candidates: Valid options to compare against
        threshold: Minimum similarity ratio (0-1)
        max_suggestions: Maximum suggestions to return

    Returns:
        List of similar candidates, best first
    """
    matches = difflib.get_close_matches(
        unknown,
        candidates,
        n=max_suggestions,
        cutoff=threshold,
    )
    return list(matches)


def format_did_you_mean(unknown: str, candidates: list[str], item_type: str = "command") -> str:
    """Format a helpful 'did you mean?' error message.

    Args:
        unknown: What the user typed
        candidates: Valid options
        item_type: What kind of thing it is (command, finder, file, etc.)

    Returns:
        Formatted error message
    """
    suggestions = did_you_mean(unknown, candidates)

    msg = f"Unknown {item_type}: '{unknown}'"

    if len(suggestions) == 1:
        msg += f"\n  Did you mean: {suggestions[0]}?"
    elif suggestions:
        msg += "\n  Did you mean one of these?"
        for s in suggestions:
            msg += f"\n    - {s}"

    return msg


# ---------------------------------------------------------------------------
# Codeframe Output (ruff-style)
# ---------------------------------------------------------------------------


@dataclass
class CodeframeContext:
    """Context for rendering a codeframe."""

    path: str
    line: int
    col_start: int = 1
    col_end: Optional[int] = None
    source_line: Optional[str] = None


def render_codeframe(
    ctx: CodeframeContext,
    title: str,
    evidence: list[str],
    fix: Optional[str] = None,
    console: Optional[Console] = None,
) -> None:
    """Render a ruff-style codeframe for a finding.

    Example:
        HIGH_RISK_HUB src/kernel.py:42
          42 │ class InsightKernel:
             │ ^^^^^^^^^^^^^^^^^^^^
          = 12 dependents • 89th percentile complexity
          = fix: Extract into separate modules
    """
    c = console or Console()

    # Title line with hyperlink
    file_text = rich_file_link(ctx.path, ctx.line, style="bold cyan")
    title_text = Text()
    title_text.append(title, style="bold yellow")
    title_text.append(" ")
    title_text.append_text(file_text)
    c.print(title_text)

    # Source line (if available)
    if ctx.source_line is not None:
        line_num = str(ctx.line).rjust(4)
        c.print(f"  [dim]{line_num}[/dim] │ {ctx.source_line}")

        # Underline
        col_start = ctx.col_start
        col_end = ctx.col_end or (col_start + len(ctx.source_line.strip()))
        underline_len = col_end - col_start
        padding = " " * (col_start - 1)
        c.print(f"       │ {padding}[yellow]{'─' * max(underline_len, 1)}[/yellow]")

    # Evidence bullets
    for e in evidence:
        c.print(f"  [dim]=[/dim] {e}")

    # Fix suggestion
    if fix:
        c.print(f"  [dim]=[/dim] [italic]fix: {fix}[/italic]")

    c.print()


# ---------------------------------------------------------------------------
# GitHub Actions Output Format
# ---------------------------------------------------------------------------


class GitHubActionsFormatter:
    """Format output for GitHub Actions workflow commands.

    Produces annotations that appear inline on PR diffs:
    ::warning file=path,line=42::Message here
    """

    @staticmethod
    def warning(path: str, message: str, line: Optional[int] = None) -> str:
        loc = f"file={path}"
        if line:
            loc += f",line={line}"
        return f"::warning {loc}::{message}"

    @staticmethod
    def error(path: str, message: str, line: Optional[int] = None) -> str:
        loc = f"file={path}"
        if line:
            loc += f",line={line}"
        return f"::error {loc}::{message}"

    @staticmethod
    def notice(path: str, message: str, line: Optional[int] = None) -> str:
        loc = f"file={path}"
        if line:
            loc += f",line={line}"
        return f"::notice {loc}::{message}"

    @staticmethod
    def group(title: str) -> str:
        return f"::group::{title}"

    @staticmethod
    def endgroup() -> str:
        return "::endgroup::"


def is_github_actions() -> bool:
    """Check if running in GitHub Actions."""
    return os.environ.get("GITHUB_ACTIONS") == "true"


# ---------------------------------------------------------------------------
# Severity Display Helpers
# ---------------------------------------------------------------------------


def severity_label(score: float) -> tuple[str, str]:
    """Get severity label and color for a 0-1 score.

    Returns:
        (label, color) tuple for Rich formatting
    """
    if score >= 0.9:
        return ("CRITICAL", "bold red")
    if score >= 0.8:
        return ("HIGH", "red")
    if score >= 0.6:
        return ("MEDIUM", "yellow")
    if score >= 0.4:
        return ("LOW", "blue")
    return ("INFO", "dim")


def severity_emoji(score: float) -> str:
    """Get severity emoji for a 0-1 score."""
    if score >= 0.9:
        return "🔴"
    if score >= 0.8:
        return "🟠"
    if score >= 0.6:
        return "🟡"
    if score >= 0.4:
        return "🔵"
    return "⚪"


# ---------------------------------------------------------------------------
# Progress Display with Phases
# ---------------------------------------------------------------------------


@dataclass
class PhaseProgress:
    """Track progress through analysis phases."""

    phases: list[tuple[str, float]]  # (name, weight)
    current_phase: int = 0
    phase_progress: float = 0.0
    on_update: Optional[Callable[[str, float], None]] = None

    @classmethod
    def default_phases(cls) -> "PhaseProgress":
        """Standard analysis phases with weights."""
        return cls(
            phases=[
                ("Scanning files", 0.15),
                ("Parsing code", 0.20),
                ("Building graph", 0.20),
                ("Analyzing history", 0.15),
                ("Computing signals", 0.20),
                ("Finding issues", 0.10),
            ]
        )

    def advance_phase(self, phase_name: Optional[str] = None) -> None:
        """Move to next phase."""
        if self.current_phase < len(self.phases):
            self.current_phase += 1
            self.phase_progress = 0.0
            if self.on_update:
                name = phase_name or self.current_phase_name
                self.on_update(name, self.overall_progress)

    def update_phase_progress(self, progress: float, message: Optional[str] = None) -> None:
        """Update progress within current phase (0-1)."""
        self.phase_progress = min(1.0, max(0.0, progress))
        if self.on_update:
            msg = message or self.current_phase_name
            self.on_update(msg, self.overall_progress)

    @property
    def current_phase_name(self) -> str:
        if 0 <= self.current_phase < len(self.phases):
            return self.phases[self.current_phase][0]
        return "Completing"

    @property
    def overall_progress(self) -> float:
        """Calculate overall progress (0-1)."""
        if not self.phases:
            return 0.0

        completed = sum(w for _, w in self.phases[: self.current_phase])
        if self.current_phase < len(self.phases):
            _, current_weight = self.phases[self.current_phase]
            completed += current_weight * self.phase_progress

        return completed


# ---------------------------------------------------------------------------
# First-Run Experience
# ---------------------------------------------------------------------------


def is_first_run(repo_path: Path) -> bool:
    """Check if this is the first analysis of this repo."""
    shannon_dir = repo_path / ".shannon"
    return not shannon_dir.exists()


def show_first_run_hint(console: Console) -> None:
    """Show helpful hints for first-time users."""
    console.print()
    console.print("[bold cyan]First time analyzing this project![/bold cyan]")
    console.print()
    console.print("  [dim]Tips:[/dim]")
    console.print("  • Run [cyan]shannon-insight explain <file>[/cyan] for file deep-dive")
    console.print("  • Run [cyan]shannon-insight health[/cyan] to track trends over time")
    console.print("  • Add [cyan]--json[/cyan] for CI/automation integration")
    console.print()


# ---------------------------------------------------------------------------
# Compact Summary Line
# ---------------------------------------------------------------------------


def compact_summary(
    file_count: int,
    finding_count: int,
    elapsed_secs: float,
    high_severity_count: int = 0,
) -> str:
    """Generate a compact one-line summary.

    Examples:
        ✓ 234 files • 0 issues • 0.8s
        ⚠ 234 files • 12 issues (3 high) • 1.2s
    """
    icon = "✓" if finding_count == 0 else "⚠"

    parts = [f"{file_count} files"]

    if finding_count == 0:
        parts.append("0 issues")
    elif high_severity_count:
        parts.append(f"{finding_count} issues ({high_severity_count} high)")
    else:
        parts.append(f"{finding_count} issues")

    parts.append(f"{elapsed_secs:.1f}s")

    return f"{icon} {' • '.join(parts)}"
