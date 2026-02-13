"""``shannon-insight serve`` — live dashboard with file watching."""

import logging
import threading
import webbrowser
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
    # Check dependencies
    try:
        from ..server import _check_deps

        _check_deps()
    except ImportError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)

    import uvicorn

    from ..server.app import create_app
    from ..server.state import ServerState
    from ..server.watcher import FileWatcher

    # Get path from parent callback (shannon-insight [PATH] serve)
    root_dir = str(ctx.obj.get("path", Path.cwd()).resolve())
    settings = resolve_settings(config=config, workers=workers, verbose=verbose)

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    state = ServerState()
    watcher = FileWatcher(root_dir=root_dir, settings=settings, state=state)

    # Run initial analysis with spinner
    console.print(f"[bold]Analyzing[/bold] {root_dir}")
    with console.status("[cyan]Running initial analysis..."):
        watcher.run_analysis()

    initial = state.get_state()
    if initial:
        health = initial.get("health", "?")
        n_issues = sum(c["count"] for c in initial.get("categories", {}).values())
        console.print(f"[green]Ready[/green] — health {health}, {n_issues} issue(s)")
    else:
        console.print("[yellow]Analysis produced no results[/yellow]")

    # Start file watcher
    watcher.start()

    # Open browser
    url = f"http://{host}:{port}"
    if not no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    console.print(f"[bold]Dashboard[/bold] → [link={url}]{url}[/link]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")

    # Start ASGI server (blocks until Ctrl+C)
    asgi_app = create_app(state)
    try:
        uvicorn.run(
            asgi_app,
            host=host,
            port=port,
            log_level="warning" if not verbose else "info",
        )
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop()
        console.print("\n[dim]Stopped.[/dim]")
