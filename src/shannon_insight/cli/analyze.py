"""Main analysis command."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from . import app
from ._common import console, resolve_settings
from ..core import CodebaseAnalyzer
from ..formatters import get_formatter, RichFormatter, JsonFormatter
from ..exceptions import ShannonInsightError
from ..logging_config import setup_logging
from .. import __version__


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
        "auto", "--language", "-l",
        help="Programming language (auto scans all detected languages; or: go, typescript, react, javascript, python)",
    ),
    top: int = typer.Option(
        15, "--top", "-t",
        help="Number of top files to display",
        min=1, max=1000,
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output JSON file path",
        dir_okay=False,
    ),
    fmt: str = typer.Option(
        "rich", "--format", "-f",
        help="Output format: rich (default), json, csv, quiet",
    ),
    explain: Optional[str] = typer.Option(
        None, "--explain", "-e",
        help="Deep-dive explanation for a specific file (substring match)",
    ),
    fail_above: Optional[float] = typer.Option(
        None, "--fail-above",
        help="Exit 1 if any file's score exceeds this threshold (for CI gating)",
        min=0.0,
    ),
    threshold: Optional[float] = typer.Option(
        None, "--threshold",
        help="Z-score threshold for anomaly detection (0.0 - 10.0)",
        min=0.0, max=10.0,
    ),
    diff: bool = typer.Option(
        False, "--diff",
        help="Compare against baseline, show deltas",
    ),
    base_ref: Optional[str] = typer.Option(
        None, "--base-ref",
        help="Git ref to diff against (default: baseline file)",
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Configuration file path (TOML format)",
        exists=True, file_okay=True, dir_okay=False, readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose (DEBUG) logging",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q",
        help="Suppress all but ERROR logging",
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache",
        help="Disable caching",
    ),
    clear_cache: bool = typer.Option(
        False, "--clear-cache",
        help="Clear cache before running",
    ),
    workers: Optional[int] = typer.Option(
        None, "--workers", "-w",
        help="Number of parallel workers (default: auto-detect)",
        min=1, max=32,
    ),
    version: bool = typer.Option(
        False, "--version",
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

      shannon-insight . --diff
    """
    if ctx.invoked_subcommand is not None:
        return

    if version:
        console.print(
            f"[bold cyan]Shannon Insight[/bold cyan] version [green]{__version__}[/green]"
        )
        raise typer.Exit(0)

    if verbose and quiet:
        console.print("[red]Error:[/red] --verbose and --quiet are mutually exclusive")
        raise typer.Exit(1)

    valid_formats = {"rich", "json", "csv", "quiet"}
    if fmt not in valid_formats:
        console.print(f"[red]Error:[/red] --format must be one of: {', '.join(sorted(valid_formats))}")
        raise typer.Exit(1)

    logger = setup_logging(verbose=verbose, quiet=quiet)

    try:
        settings = resolve_settings(
            config=config, threshold=threshold, no_cache=no_cache,
            workers=workers, verbose=verbose, quiet=quiet,
        )
        logger.debug(f"Loaded settings: {settings.model_dump()}")

        analyzer = CodebaseAnalyzer(root_dir=path, language=language, settings=settings)

        if clear_cache:
            if hasattr(analyzer, "cache") and analyzer.cache:
                analyzer.cache.clear()
                console.print("[yellow]Cache cleared[/yellow]")

        reports, analysis_context = analyzer.analyze()
        analysis_context.top_n = top
        analysis_context.explain_pattern = explain

        # --diff mode
        if diff:
            from ..baseline import load_baseline, diff_reports
            from ..formatters.diff_formatter import DiffFormatter

            baseline_path = Path(path) / ".shannon-insight-baseline.json"
            baseline_data = load_baseline(str(baseline_path))

            changed_files = None
            if base_ref:
                import subprocess
                result = subprocess.run(
                    ["git", "-C", str(path), "diff", "--name-only", base_ref],
                    capture_output=True, text=True,
                )
                if result.returncode == 0:
                    changed_files = set(result.stdout.strip().splitlines())

            diff_list = diff_reports(reports, baseline_data, changed_files)
            diff_fmt = DiffFormatter()
            diff_fmt.render(diff_list, analysis_context)
            raise typer.Exit(0)

        # Normal output
        if reports:
            formatter = get_formatter(fmt)

            if explain:
                if isinstance(formatter, RichFormatter):
                    formatter.render_explain(reports, analysis_context)
                else:
                    formatter.render(reports, analysis_context)
            else:
                formatter.render(reports, analysis_context)

            json_fmt = JsonFormatter()
            if output is not None:
                output_path = Path(output)
                with open(output_path, "w") as f:
                    f.write(json_fmt.format(reports, analysis_context))
                console.print(f"[green]Exported detailed report to {output_path}[/green]")
            elif fmt == "rich":
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                auto_path = f"analysis_report_{ts}.json"
                with open(auto_path, "w") as f:
                    f.write(json_fmt.format(reports, analysis_context))
                console.print(f"[green]Exported detailed report to {auto_path}[/green]")

            if fail_above is not None:
                max_score = max(r.overall_score for r in reports)
                if max_score > fail_above:
                    if fmt == "rich":
                        severity = CodebaseAnalyzer._severity_label(max_score)
                        console.print(
                            f"\n[red]FAIL:[/red] Max score {max_score:.3f} "
                            f"({severity}) exceeds threshold {fail_above:.3f}"
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

    except typer.Exit:
        raise

    except ShannonInsightError as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        console.print("\n[yellow]Analysis interrupted[/yellow]")
        raise typer.Exit(130)

    except Exception as e:
        logger.exception("Unexpected error during analysis")
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)
