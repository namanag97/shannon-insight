"""Progress reporting — wraps Rich or runs silently."""

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TextColumn,
)


class ProgressReporter:
    """Rich progress bar wrapper."""

    def __init__(self, console: Console):
        self.console = console

    def run(self, callback):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        ) as progress:
            return callback(progress)


class SilentReporter:
    """No-op reporter for tests and --quiet mode."""

    def run(self, callback):
        return callback(None)
