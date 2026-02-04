"""CLI entry point — registers all subcommands."""

import typer

from .. import __version__
from ._common import console

app = typer.Typer(
    name="shannon-insight",
    help="Shannon Insight - Multi-Signal Codebase Quality Analyzer",
    add_completion=False,
    rich_markup_mode="rich",
)


# Import subcommands to register them
from .analyze import main as _main_callback  # noqa: F401, E402
from .baseline import baseline as _baseline  # noqa: F401, E402
from .cache import cache_info as _cache_info, cache_clear as _cache_clear  # noqa: F401, E402
from .structure import structure as _structure  # noqa: F401, E402
from .insights import insights as _insights  # noqa: F401, E402
