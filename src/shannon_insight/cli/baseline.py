"""Baseline command."""

from pathlib import Path
from typing import Optional

import typer

from . import app
from ._common import console
from ..config import load_settings
from ..core import CodebaseAnalyzer
from ..exceptions import ShannonInsightError
from ..logging_config import setup_logging


@app.command()
def baseline(
    path: Path = typer.Argument(
        Path("."),
        help="Path to the codebase directory",
        exists=False, file_okay=False, dir_okay=True,
    ),
    show: bool = typer.Option(
        False, "--show",
        help="Show current baseline instead of saving",
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Configuration file path (TOML format)",
        exists=True, file_okay=True, dir_okay=False, readable=True,
    ),
):
    """Save current scores as baseline for --diff mode."""
    from ..baseline import save_baseline, load_baseline

    baseline_path = Path(path) / ".shannon-insight-baseline.json"

    if show:
        data = load_baseline(str(baseline_path))
        if not data:
            console.print("[yellow]No baseline found.[/yellow]")
            raise typer.Exit(0)
        console.print(f"[bold cyan]Baseline[/bold cyan] ({baseline_path})")
        for fpath, score in sorted(data.items(), key=lambda x: x[1], reverse=True):
            console.print(f"  {score:.4f}  {fpath}")
        raise typer.Exit(0)

    logger = setup_logging(verbose=False, quiet=True)
    try:
        settings = load_settings(config_file=config)
        analyzer = CodebaseAnalyzer(root_dir=path, settings=settings)
        reports, _ctx = analyzer.analyze()
        save_baseline(reports, str(baseline_path))
        console.print(f"[green]Baseline saved to {baseline_path} ({len(reports)} files)[/green]")
    except ShannonInsightError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
