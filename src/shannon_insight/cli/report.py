"""Report CLI command -- generate interactive HTML report."""

from pathlib import Path
from typing import Optional

import typer

from . import app
from ._common import console, resolve_settings
from ..logging_config import setup_logging


@app.command()
def report(
    path: Path = typer.Argument(
        Path("."),
        help="Project root to analyse",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    output: Path = typer.Option(
        Path("shannon-report.html"),
        "--output",
        "-o",
        help="Output HTML file path",
    ),
    metric: str = typer.Option(
        "cognitive_load",
        "--metric",
        "-m",
        help="Default metric for treemap colouring",
    ),
    include_trends: bool = typer.Option(
        True,
        "--trends/--no-trends",
        help="Include file trend sparklines (requires history)",
    ),
    language: str = typer.Option(
        "auto",
        "--language",
        "-l",
        help="Programming language (auto, python, go, typescript, etc.)",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (TOML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all but error logging",
    ),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Parallel workers",
        min=1,
        max=32,
    ),
    max_findings: int = typer.Option(
        10,
        "--max-findings",
        "-n",
        help="Maximum findings to include in the report",
        min=1,
        max=50,
    ),
):
    """
    Generate an interactive HTML report with treemap visualisation.

    Runs the full insight pipeline (scan, analyse, find) and writes a
    self-contained HTML file that can be opened in any browser.

    The report includes:
    - Interactive treemap sized by LOC, coloured by any signal
    - All findings with evidence and suggestions
    - File trend sparklines (when history is available)

    [bold cyan]Examples:[/bold cyan]

      shannon-insight . report

      shannon-insight . report --output my-report.html --metric entropy

      shannon-insight . report --no-trends --max-findings 20
    """
    logger = setup_logging(verbose=verbose, quiet=quiet)

    try:
        settings = resolve_settings(
            config=config,
            no_cache=False,
            workers=workers,
            verbose=verbose,
            quiet=quiet,
        )

        # ── Run the insight pipeline ──────────────────────────────
        from ..insights import InsightKernel

        kernel = InsightKernel(
            str(path), language=language, settings=settings,
        )
        result, snapshot = kernel.run_and_capture(max_findings=max_findings)

        # ── Persist snapshot if history is enabled ────────────────
        if settings.enable_history:
            try:
                from ..storage import HistoryDB
                from ..storage.writer import save_snapshot

                with HistoryDB(str(Path(path).resolve())) as db:
                    sid = save_snapshot(db.conn, snapshot)
                    logger.info(f"Snapshot saved (id={sid})")
            except Exception as e:
                logger.warning(f"Failed to save snapshot: {e}")

        # ── Load trend data if requested ──────────────────────────
        trends = None
        if include_trends:
            try:
                from ..storage import HistoryDB
                from ..storage.queries import HistoryQuery

                with HistoryDB(str(Path(path).resolve())) as db:
                    query = HistoryQuery(db.conn)
                    # Pick the top-20 files by the default colour metric.
                    top_files = sorted(
                        snapshot.file_signals.items(),
                        key=lambda x: x[1].get("cognitive_load", 0),
                        reverse=True,
                    )[:20]
                    trends = {
                        fp: query.file_trend(fp, "cognitive_load")
                        for fp, _ in top_files
                    }
                    # Drop files with no historical data points.
                    trends = {
                        fp: pts for fp, pts in trends.items() if pts
                    }
            except Exception:
                # History may not be available; that is fine.
                logger.debug("Trend data unavailable", exc_info=True)

        # ── Generate the HTML report ──────────────────────────────
        from ..visualization import generate_report

        report_path = generate_report(
            snapshot,
            trends=trends,
            output_path=str(output),
            default_metric=metric,
        )
        console.print(
            f"[bold green]Report generated:[/bold green] {report_path}"
        )

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception("Report generation failed")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
