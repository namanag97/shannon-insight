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
from ._explain import explain as _explain  # noqa: F401, E402
from .analyze import main as _main_callback  # noqa: F401, E402
from .build_history import build_history as _build_history  # noqa: F401, E402
from .health import health as _health  # noqa: F401, E402
from .history import history as _history  # noqa: F401, E402
from .serve import serve as _serve  # noqa: F401, E402
