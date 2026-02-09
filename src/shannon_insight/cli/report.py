"""Report CLI command -- generate interactive HTML report."""

from pathlib import Path
from typing import Optional

import typer

from ..logging_config import setup_logging
from . import app
from ._common import console, resolve_settings


@app.command()
def report(
    ctx: typer.Context,
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
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (TOML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        hidden=True,
    ),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Parallel workers",
        min=1,
        max=32,
        hidden=True,
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

      shannon-insight report

      shannon-insight report --output my-report.html --metric entropy

      shannon-insight report --no-trends
    """
    target = ctx.obj.get("path", Path.cwd())
    logger = setup_logging(verbose=verbose)

    try:
        settings = resolve_settings(
            config=config,
            no_cache=False,
            workers=workers,
            verbose=verbose,
        )

        max_findings = settings.insights_max_findings

        # -- Run the insight pipeline --
        from ..insights import InsightKernel

        kernel = InsightKernel(
            str(target),
            language="auto",
            settings=settings,
        )
        result, snapshot = kernel.run(max_findings=max_findings)

        # -- Persist snapshot if history is enabled --
        if settings.enable_history:
            try:
                from ..persistence import HistoryDB
                from ..persistence.writer import save_tensor_snapshot

                with HistoryDB(str(Path(target).resolve())) as db:
                    sid = save_tensor_snapshot(db.conn, snapshot)
                    logger.info(f"Snapshot saved (id={sid})")
            except Exception as e:
                logger.warning(f"Failed to save snapshot: {e}")

        # -- Load trend data if requested --
        trends = None
        if include_trends:
            try:
                from ..persistence import HistoryDB
                from ..persistence.queries import HistoryQuery

                with HistoryDB(str(Path(target).resolve())) as db:
                    query = HistoryQuery(db.conn)
                    # Pick the top-20 files by the default colour metric.
                    top_files = sorted(
                        snapshot.file_signals.items(),
                        key=lambda x: x[1].get("cognitive_load", 0),
                        reverse=True,
                    )[:20]
                    trends = {fp: query.file_trend(fp, "cognitive_load") for fp, _ in top_files}
                    # Drop files with no historical data points.
                    trends = {fp: pts for fp, pts in trends.items() if pts}
            except Exception:
                # History may not be available; that is fine.
                logger.debug("Trend data unavailable", exc_info=True)

        # -- Generate the HTML report --
        from ..visualization import generate_report

        report_path = generate_report(
            snapshot,
            trends=trends,
            output_path=str(output),
            default_metric=metric,
        )
        console.print(f"\nReport saved to: [bold green]{report_path}[/bold green]")

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception("Report generation failed")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
