"""Cache management commands."""

import typer

from . import app
from ._common import console


@app.command()
def cache_info():
    """Show cache information and statistics."""
    from ..config import default_settings
    from ..cache import AnalysisCache

    cache = AnalysisCache(
        cache_dir=default_settings.cache_dir,
        ttl_hours=default_settings.cache_ttl_hours,
        enabled=default_settings.enable_cache,
    )

    stats = cache.stats()

    console.print("[bold cyan]Shannon Insight Cache Info[/bold cyan]")
    console.print()

    if stats.get("enabled"):
        console.print(f"Status: [green]Enabled[/green]")
        console.print(f"Directory: [blue]{stats.get('directory', 'N/A')}[/blue]")
        console.print(f"Entries: [yellow]{stats.get('size', 0)}[/yellow]")
        console.print(f"Size: [yellow]{stats.get('volume', 0)} bytes[/yellow]")
    else:
        console.print(f"Status: [red]Disabled[/red]")


@app.command()
def cache_clear():
    """Clear the analysis cache."""
    from ..config import default_settings
    from ..cache import AnalysisCache

    cache = AnalysisCache(
        cache_dir=default_settings.cache_dir,
        ttl_hours=default_settings.cache_ttl_hours,
        enabled=default_settings.enable_cache,
    )

    if not default_settings.enable_cache:
        console.print("[yellow]Cache is disabled[/yellow]")
        raise typer.Exit(0)

    cache.clear()
    console.print("[green]Cache cleared successfully[/green]")
