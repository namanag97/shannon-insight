"""``shannon-insight serve`` -- DEPRECATED, dashboard is now the default."""

from pathlib import Path

import typer

from . import app
from ._common import console


@app.command(hidden=True)
def serve(
    ctx: typer.Context,
    port: int = typer.Option(8765, help="Port to listen on"),
) -> None:
    """[DEPRECATED] Dashboard is now the default. Just run: shannon-insight"""
    console.print(
        "[yellow]'shannon-insight serve' is deprecated.[/yellow]\n"
        "Dashboard is now the default. Just run:\n\n"
        "  [bold]shannon-insight[/bold]          # opens dashboard\n"
        "  [bold]shannon-insight --cli[/bold]    # terminal output\n"
    )
    raise typer.Exit(0)
