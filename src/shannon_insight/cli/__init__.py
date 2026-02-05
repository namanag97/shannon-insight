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
from .history import history as _history  # noqa: F401, E402
from .trend import trend as _trend  # noqa: F401, E402
from .health import health as _health  # noqa: F401, E402
from .diff import insights_baseline as _insights_baseline, insights_diff as _insights_diff  # noqa: F401, E402
from .report import report as _report  # noqa: F401, E402
