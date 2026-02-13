"""Clean progress display for Shannon Insight CLI."""

from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table


@dataclass
class Phase:
    """A phase in the analysis pipeline."""

    name: str
    weight: int  # Relative weight for progress calculation
    description: str


# The 6 phases of analysis
PHASES = [
    Phase("scan", 15, "Scanning files"),
    Phase("parse", 20, "Parsing code"),
    Phase("graph", 20, "Building dependency graph"),
    Phase("temporal", 15, "Analyzing git history"),
    Phase("signals", 20, "Computing signals"),
    Phase("findings", 10, "Detecting issues"),
]


class AnalysisProgress:
    """Clean progress display for the analysis pipeline."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self._current_phase = 0
        self._progress: Progress | None = None
        self._task_id = None
        self._file_count = 0

    def start(self) -> None:
        """Start the progress display."""
        self.console.print()
        self.console.print("[bold cyan]SHANNON INSIGHT[/]")
        self.console.print("[dim]Codebase Quality Analysis[/]")
        self.console.print()

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=40, complete_style="cyan", finished_style="green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        )
        self._progress.start()
        self._task_id = self._progress.add_task("Initializing...", total=100)

    def update(self, message: str) -> None:
        """Update progress based on message from kernel."""
        if not self._progress or self._task_id is None:
            return

        # Map message to phase
        phase_idx = self._detect_phase(message)
        if phase_idx >= 0:
            self._current_phase = phase_idx

        # Calculate progress percentage
        completed = sum(PHASES[i].weight for i in range(self._current_phase))

        # Extract file count if present
        if "files" in message.lower():
            import re

            match = re.search(r"(\d+)\s*files", message.lower())
            if match:
                self._file_count = int(match.group(1))

        # Clean up the message
        display_msg = self._clean_message(message)

        self._progress.update(self._task_id, completed=completed, description=display_msg)

    def _detect_phase(self, message: str) -> int:
        """Detect which phase we're in based on message."""
        msg_lower = message.lower()

        if "scan" in msg_lower:
            return 0
        elif "pars" in msg_lower:
            return 1
        elif "depend" in msg_lower or "graph" in msg_lower or "structural" in msg_lower:
            return 2
        elif "temporal" in msg_lower or "git" in msg_lower or "history" in msg_lower:
            return 3
        elif "signal" in msg_lower or "fusion" in msg_lower or "comput" in msg_lower:
            return 4
        elif "detect" in msg_lower or "finding" in msg_lower or "issue" in msg_lower:
            return 5

        return self._current_phase

    def _clean_message(self, message: str) -> str:
        """Clean up progress message for display."""
        # Remove "Running " prefix
        if message.startswith("Running "):
            message = message[8:]

        # Capitalize first letter
        if message:
            message = message[0].upper() + message[1:]

        # Truncate if too long
        if len(message) > 50:
            message = message[:47] + "..."

        return message

    def finish(self, file_count: int, finding_count: int) -> None:
        """Finish the progress display."""
        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id,
                completed=100,
                description=f"[green]Done![/] {file_count} files analyzed",
            )
            self._progress.stop()

        self.console.print()


def create_summary_table(
    files: int,
    modules: int,
    commits: int,
    findings: int,
    health: float | None = None,
) -> Table:
    """Create a summary table for the analysis results."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column(style="bold")

    table.add_row("Files", str(files))
    table.add_row("Modules", str(modules))
    if commits > 0:
        table.add_row("Commits", str(commits))
    table.add_row(
        "Issues",
        f"[{'red' if findings > 10 else 'yellow' if findings > 0 else 'green'}]{findings}[/]",
    )

    if health is not None:
        color = "green" if health >= 7 else "yellow" if health >= 5 else "red"
        table.add_row("Health", f"[{color}]{health:.1f}/10[/]")

    return table
