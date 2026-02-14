"""``shannon-insight serve`` -- live dashboard with file watching."""

import logging
from pathlib import Path
from typing import Optional

import typer

from . import app
from ._common import console, resolve_settings

logger = logging.getLogger(__name__)


@app.command()
def serve(
    ctx: typer.Context,
    port: int = typer.Option(8765, help="Port to listen on"),
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open browser"),
    config: Optional[Path] = typer.Option(None, "-c", "--config", help="Config file"),
    workers: Optional[int] = typer.Option(None, "-w", "--workers", help="Parallel workers"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose logging"),
) -> None:
    """Start a live dashboard that watches for file changes."""
    console.print(
        "[yellow]Note: 'shannon-insight serve' is deprecated. "
        "Use 'shannon-insight' to open dashboard or 'shannon-insight --cli' for terminal output.[/yellow]\n"
    )
    # Check dependencies
    try:
        from ..server import _check_deps

        _check_deps()
    except ImportError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)

    # Get path from parent callback (shannon-insight [PATH] serve)
    root_dir = str(ctx.obj.get("path", Path.cwd()).resolve())
    settings = resolve_settings(config=config, workers=workers, verbose=verbose)

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Delegate to the lifecycle manager
    from ..server.lifecycle import launch_server

    launch_server(
        root_dir=root_dir,
        settings=settings,
        console=console,
        host=host,
        port=port,
        no_browser=no_browser,
        verbose=verbose,
    )
