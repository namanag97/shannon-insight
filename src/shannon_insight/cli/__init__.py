"""CLI entry point — registers all subcommands."""

import typer

from ._common import console

app: typer.Typer = typer.Typer(
    name="shannon-insight",
    help="Shannon Insight - Multi-Signal Codebase Quality Analyzer",
    add_completion=False,
    rich_markup_mode="rich",
)


# Import subcommands to register them
from .analyze import main as _main_callback  # noqa: F401, E402
from .diff import diff_cmd as _diff_cmd  # noqa: F401, E402
from .explain import explain as _explain  # noqa: F401, E402
from .health import health as _health  # noqa: F401, E402
from .history import history as _history  # noqa: F401, E402
from .report import report as _report  # noqa: F401, E402
