"""Command-line interface for Shannon Insight"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .core import CodebaseAnalyzer
from .config import load_settings, AnalysisSettings
from .logging_config import setup_logging
from .exceptions import ShannonInsightError

app = typer.Typer(
    name="shannon-insight",
    help="Shannon Insight - Multi-Signal Codebase Quality Analyzer",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    ctx: typer.Context,
    path: Path = typer.Argument(
        Path("."),
        help="Path to the codebase directory to analyze",
        exists=False,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    language: str = typer.Option(
        "auto",
        "--language",
        "-l",
        help="Programming language (auto, go, typescript, react, javascript, python)",
    ),
    top: int = typer.Option(
        15,
        "--top",
        "-t",
        help="Number of top files to display",
        min=1,
        max=1000,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output JSON file path",
        dir_okay=False,
    ),
    fmt: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich (default), json, csv, quiet",
    ),
    explain: Optional[str] = typer.Option(
        None,
        "--explain",
        "-e",
        help="Deep-dive explanation for a specific file (substring match)",
    ),
    fail_above: Optional[float] = typer.Option(
        None,
        "--fail-above",
        help="Exit 1 if any file's score exceeds this threshold (for CI gating)",
        min=0.0,
    ),
    threshold: Optional[float] = typer.Option(
        None,
        "--threshold",
        help="Z-score threshold for anomaly detection (0.0 - 10.0)",
        min=0.0,
        max=10.0,
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file path (TOML format)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose (DEBUG) logging",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all but ERROR logging",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable caching",
    ),
    clear_cache: bool = typer.Option(
        False,
        "--clear-cache",
        help="Clear cache before running",
    ),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Number of parallel workers (default: auto-detect)",
        min=1,
        max=32,
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
    ),
):
    """
    Analyze codebase quality using mathematical primitives.

    Named after Claude Shannon, father of information theory.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight /path/to/codebase

      shannon-insight /path/to/codebase --language go

      shannon-insight /path/to/codebase --top 20 --output results.json

      shannon-insight . --format json | jq .

      shannon-insight . --fail-above 2.0 --format quiet

      shannon-insight . --explain complex.go
    """
    # If subcommand is invoked, don't run main analysis
    if ctx.invoked_subcommand is not None:
        return

    # Handle version
    if version:
        console.print(
            f"[bold cyan]Shannon Insight[/bold cyan] version [green]{__version__}[/green]"
        )
        raise typer.Exit(0)

    # Validate mutually exclusive options
    if verbose and quiet:
        console.print("[red]Error:[/red] --verbose and --quiet are mutually exclusive")
        raise typer.Exit(1)

    # Validate format
    valid_formats = {"rich", "json", "csv", "quiet"}
    if fmt not in valid_formats:
        console.print(f"[red]Error:[/red] --format must be one of: {', '.join(sorted(valid_formats))}")
        raise typer.Exit(1)

    # Setup logging first
    logger = setup_logging(verbose=verbose, quiet=quiet)

    try:
        # Load settings from config file and environment
        overrides = {}

        # CLI overrides (highest priority)
        if threshold is not None:
            overrides["z_score_threshold"] = threshold
        if no_cache:
            overrides["enable_cache"] = False
        if workers is not None:
            overrides["parallel_workers"] = workers
        if verbose:
            overrides["verbose"] = True
        if quiet:
            overrides["quiet"] = True

        settings = load_settings(config_file=config, **overrides)

        # Log configuration
        logger.debug(f"Loaded settings: {settings.model_dump()}")

        # Create analyzer
        analyzer = CodebaseAnalyzer(root_dir=path, language=language, settings=settings)

        # Clear cache if requested
        if clear_cache:
            if hasattr(analyzer, "cache") and analyzer.cache:
                analyzer.cache.clear()
                console.print("[yellow]Cache cleared[/yellow]")

        # Run analysis
        reports = analyzer.analyze()

        # Handle results based on format
        if reports:
            if explain:
                # --explain mode: deep-dive on matching file(s)
                analyzer.print_explain(reports, explain)
            elif fmt == "json":
                # JSON to stdout
                print(analyzer.format_json(reports))
            elif fmt == "csv":
                # CSV to stdout
                print(analyzer.format_csv(reports), end="")
            elif fmt == "quiet":
                # Just file paths
                print(analyzer.format_quiet(reports))
            else:
                # Default rich output: summary + detailed report
                analyzer.print_summary(reports, top_n=top)
                analyzer.print_report(reports, top_n=top)

            # Export JSON file only if -o was explicitly provided
            if output is not None:
                analyzer.export_json(reports, filename=str(output))

            # --fail-above CI gating
            if fail_above is not None:
                max_score = max(r.overall_score for r in reports)
                if max_score > fail_above:
                    if fmt == "rich":
                        console.print(
                            f"\n[red]FAIL:[/red] Max score {max_score:.3f} "
                            f"exceeds threshold {fail_above:.3f}"
                        )
                    raise typer.Exit(1)

            if fmt == "rich":
                console.print()
                console.print("[bold green]ANALYSIS COMPLETE[/bold green]")
                console.print()
        else:
            if fmt == "json":
                print("[]")
            elif fmt == "csv":
                print("file,overall_score,confidence,structural_entropy,"
                      "network_centrality,churn_volatility,semantic_coherence,"
                      "cognitive_load,anomaly_flags")
            elif fmt == "rich":
                console.print(
                    "[bold green]No anomalies detected - codebase looks clean![/bold green]"
                )
            raise typer.Exit(0)

    except ShannonInsightError as e:
        # Handle known errors
        logger.error(f"{e.__class__.__name__}: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        console.print("\n[yellow]Analysis interrupted[/yellow]")
        raise typer.Exit(130)

    except Exception as e:
        # Handle unexpected errors
        logger.exception("Unexpected error during analysis")
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def cache_info():
    """Show cache information and statistics."""
    from .config import default_settings
    from .cache import AnalysisCache

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
    from .config import default_settings
    from .cache import AnalysisCache

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


if __name__ == "__main__":
    app()
