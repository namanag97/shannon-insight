"""Shared CLI helpers."""

from pathlib import Path
from typing import Optional

from rich.console import Console

from ..config import AnalysisSettings, load_settings

console = Console()


def resolve_settings(
    config: Optional[Path] = None,
    threshold: Optional[float] = None,
    no_cache: bool = False,
    workers: Optional[int] = None,
    verbose: bool = False,
) -> AnalysisSettings:
    """Build settings from CLI options."""
    overrides = {}
    if threshold is not None:
        overrides["z_score_threshold"] = threshold
    if no_cache:
        overrides["enable_cache"] = False
    if workers is not None:
        overrides["parallel_workers"] = workers
    if verbose:
        overrides["verbose"] = True
    return load_settings(config_file=config, **overrides)
