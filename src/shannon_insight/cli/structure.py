"""Structural analysis command — multi-level codebase intelligence."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from ..analysis.engine import AnalysisEngine
from ..analysis.models import CodebaseAnalysis
from ..core.scanner_factory import ScannerFactory
from ..exceptions import ShannonInsightError
from ..logging_config import setup_logging
from . import app
from ._common import console, resolve_settings

_MIN_FILES = 3


@app.command()
def structure(
    path: Path = typer.Argument(
        Path("."),
        help="Path to the codebase directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    language: str = typer.Option(
        "auto",
        "--language",
        "-l",
        help="Programming language (auto, python, go, typescript, etc.)",
    ),
    fmt: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich (human-readable) or json (for AI agents)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed metrics and all files",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress logging",
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
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Parallel workers",
        min=1,
        max=32,
    ),
):
    """
    Analyze codebase structure: dependencies, communities, cycles, blast radius.

    Produces actionable structural insights rather than scores. Output can
    be piped to an AI agent with --format json.

    [bold cyan]Examples:[/bold cyan]

      shannon-insight structure /path/to/codebase

      shannon-insight structure . --format json | pbcopy

      shannon-insight structure . --verbose
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

        # Phase 1: Scan
        if not quiet:
            console.print()
            console.print("[bold cyan]SHANNON INSIGHT — Structural Analysis[/bold cyan]")
            console.print()

        factory = ScannerFactory(Path(path), settings)
        scanners, detected = factory.create(language)

        # Only use language-specific scanners, not universal (which picks up
        # markdown, json, toml etc. that add noise to structural analysis)
        all_files = []
        for scanner, lang in scanners:
            if lang == "universal":
                continue
            all_files.extend(scanner.scan())

        # Filter out detected languages list
        detected = [d for d in detected if d != "universal"]

        if len(all_files) < _MIN_FILES:
            console.print(
                f"[yellow]Only {len(all_files)} files found — need at least {_MIN_FILES} for analysis[/yellow]"
            )
            raise typer.Exit(1)

        if not quiet:
            console.print(
                f"  Scanned [green]{len(all_files)}[/green] files ({', '.join(detected)})"
            )

        # Phase 2-5: Analysis engine
        engine = AnalysisEngine(all_files, root_dir=str(path))
        result = engine.run()

        if fmt == "json":
            _output_json(result)
        else:
            _output_rich(result, verbose=verbose)

    except typer.Exit:
        raise
    except ShannonInsightError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


def _output_json(result: CodebaseAnalysis):
    """Machine-readable output for AI agent consumption."""
    output = {
        "summary": {
            "total_files": result.total_files,
            "total_modules": result.total_modules,
            "total_edges": result.total_edges,
            "cycle_count": result.cycle_count,
            "modularity": round(result.modularity, 3),
            "community_count": len(result.graph_analysis.communities),
        },
        "cycles": [
            {
                "files": sorted(c.nodes),
                "internal_edges": c.internal_edge_count,
            }
            for c in result.graph_analysis.cycles
        ],
        "files": {
            path: {
                "lines": fa.lines,
                "depends_on": fa.depends_on,
                "depended_on_by": fa.depended_on_by,
                "blast_radius": fa.blast_radius_size,
                "pagerank": round(fa.pagerank, 4),
                "betweenness": round(fa.betweenness, 4),
                "in_degree": fa.in_degree,
                "out_degree": fa.out_degree,
                "compression_ratio": round(fa.compression_ratio, 3),
                "cognitive_load": round(fa.cognitive_load, 1),
                "function_count": fa.function_count,
                "function_size_gini": round(fa.function_size_gini, 3),
                "cycle_member": fa.cycle_member,
                "community_id": fa.community_id,
            }
            for path, fa in sorted(result.files.items())
        },
        "modules": {
            path: {
                "files": ma.files,
                "cohesion": round(ma.cohesion, 3),
                "coupling": round(ma.coupling, 3),
                "internal_edges": ma.internal_edges,
                "external_edges_out": ma.external_edges_out,
                "external_edges_in": ma.external_edges_in,
                "boundary_alignment": round(ma.boundary_alignment, 2),
            }
            for path, ma in sorted(result.modules.items())
        },
        "communities": [
            {"id": c.id, "members": sorted(c.members)}
            for c in sorted(result.graph_analysis.communities, key=lambda x: -len(x.members))
        ],
        "outliers": result.outliers,
        "boundary_mismatches": [
            {
                "module": bm.module_path,
                "community_distribution": bm.community_distribution,
                "misplaced_files": [
                    {"file": f, "suggested_module": s} for f, s in bm.misplaced_files
                ],
            }
            for bm in result.boundary_mismatches
        ],
    }
    print(json.dumps(output, indent=2))


def _output_rich(result: CodebaseAnalysis, verbose: bool = False):
    """Human-readable terminal output. Only shows issues unless verbose."""
    ga = result.graph_analysis
    has_issues = False

    # ── Summary ────────────────────────────────────────────────────
    mod_label = _modularity_label(result.modularity)
    console.print(
        f"  [bold]{result.total_files}[/bold] files across [bold]{result.total_modules}[/bold] modules"
    )
    console.print(f"  [bold]{result.total_edges}[/bold] dependency edges")
    console.print(
        f"  [bold]{len(ga.communities)}[/bold] natural communities (modularity: {result.modularity:.2f} — {mod_label})"
    )
    console.print()

    # ── Circular Dependencies ──────────────────────────────────────
    # Filter out Python package init cycles (init <-> submodule) as they're structural
    real_cycles = []
    for cycle in ga.cycles:
        init_files = [n for n in cycle.nodes if n.endswith("__init__.py")]
        non_init = [n for n in cycle.nodes if not n.endswith("__init__.py")]
        # If all non-init files share a parent dir with the init file, it's a package cycle
        if init_files and non_init:
            init_dir = str(Path(init_files[0]).parent)
            all_same_pkg = all(str(Path(n).parent) == init_dir for n in non_init)
            if all_same_pkg:
                if verbose:
                    console.print(
                        f"  [dim]Package cycle in {init_dir}/ (structural, not a problem)[/dim]"
                    )
                continue
        real_cycles.append(cycle)

    if real_cycles:
        has_issues = True
        console.print("[bold red]Circular Dependencies[/bold red]")
        for cycle in real_cycles:
            nodes = sorted(cycle.nodes)
            console.print(f"  {' <-> '.join(nodes)}")
            console.print(f"  [dim]({cycle.internal_edge_count} edges in cycle)[/dim]")
        console.print()

    # ── High-Impact Files ──────────────────────────────────────────
    high_impact = [
        (path, fa)
        for path, fa in result.files.items()
        if fa.blast_radius_size > result.total_files * 0.3  # affects > 30% of codebase
    ]
    high_impact.sort(key=lambda x: x[1].blast_radius_size, reverse=True)

    if high_impact:
        has_issues = True
        console.print(
            "[bold yellow]High-Impact Files[/bold yellow] (changing these affects >30% of codebase)"
        )
        for path, fa in high_impact:
            pct = fa.blast_radius_size * 100 // result.total_files
            console.print(
                f"  [bold]{path}[/bold] — {fa.in_degree} dependents, "
                f"blast radius {fa.blast_radius_size} files ({pct}%)"
            )
        console.print()

    # ── Boundary Mismatches ────────────────────────────────────────
    # Filter boundary mismatches to only show meaningful ones
    meaningful_mismatches = []
    for bm in result.boundary_mismatches:
        useful_misplaced = [
            (f, s) for f, s in bm.misplaced_files if s and s != bm.module_path and s != "unknown"
        ]
        if useful_misplaced:
            meaningful_mismatches.append((bm, useful_misplaced))

    if meaningful_mismatches:
        has_issues = True
        console.print(
            "[bold yellow]Boundary Mismatches[/bold yellow] (module boundaries don't match actual coupling)"
        )
        for bm, misplaced in meaningful_mismatches:
            console.print(
                f"  [bold]{bm.module_path}/[/bold] spans {len(bm.community_distribution)} communities"
            )
            for file, suggested in misplaced:
                console.print(f"    {file} is more connected to {suggested}/")
        console.print()

    # ── Complexity Outliers ────────────────────────────────────────
    # Only show outliers that are actionable (skip blast radius / circular — already shown above)
    # Sort by severity and limit to top entries to avoid noise
    scored_outliers: list = []
    for path, reasons in result.outliers.items():
        clean_reasons = []
        max_z = 0.0
        for r in reasons:
            if "blast radius" in r or "circular" in r:
                continue
            # Extract modified_z for sorting
            z_idx = r.find("modified_z=")
            if z_idx > 0:
                try:
                    z_val = float(r[z_idx + 11 : r.find(")", z_idx)])
                    max_z = max(max_z, z_val)
                except ValueError:
                    pass
            # Strip raw numbers for display unless verbose
            if not verbose:
                paren_idx = r.find(" (value=")
                if paren_idx > 0:
                    r = r[:paren_idx]
            clean_reasons.append(r)
        if clean_reasons:
            scored_outliers.append((max_z, path, clean_reasons))

    scored_outliers.sort(reverse=True)
    max_show = 10 if verbose else 5

    if scored_outliers:
        has_issues = True
        shown = scored_outliers[:max_show]
        remaining = len(scored_outliers) - len(shown)
        console.print("[bold yellow]Complexity Outliers[/bold yellow]")
        for _, path, reasons in shown:
            console.print(f"  [bold]{path}[/bold] — {'; '.join(reasons)}")
        if remaining > 0:
            console.print(f"  [dim]... and {remaining} more (use --verbose to see all)[/dim]")
        console.print()

    # ── Verbose: Module Details ────────────────────────────────────
    if verbose:
        console.print("[bold]Module Details[/bold]")
        table = Table(show_header=True)
        table.add_column("Module", style="cyan")
        table.add_column("Files", justify="right")
        table.add_column("Cohesion", justify="right")
        table.add_column("Coupling", justify="right")
        table.add_column("Alignment", justify="right")

        for mod_path in sorted(result.modules.keys()):
            ma = result.modules[mod_path]
            coh_style = "green" if ma.cohesion > 0.3 else "yellow" if ma.cohesion > 0.1 else "red"
            coup_style = "green" if ma.coupling < 0.5 else "yellow" if ma.coupling < 0.8 else "red"
            align_style = (
                "green"
                if ma.boundary_alignment > 0.8
                else "yellow"
                if ma.boundary_alignment > 0.5
                else "red"
            )

            table.add_row(
                ma.path,
                str(ma.file_count),
                f"[{coh_style}]{ma.cohesion:.2f}[/{coh_style}]",
                f"[{coup_style}]{ma.coupling:.2f}[/{coup_style}]",
                f"[{align_style}]{ma.boundary_alignment:.2f}[/{align_style}]",
            )
        console.print(table)
        console.print()

        # Communities
        console.print("[bold]Discovered Communities[/bold]")
        for comm in sorted(ga.communities, key=lambda x: -len(x.members)):
            if len(comm.members) > 1:
                members = sorted(comm.members)
                console.print(f"  Community ({len(members)} files): {', '.join(members)}")
        console.print()

    # ── All clear ──────────────────────────────────────────────────
    if not has_issues:
        console.print("[bold green]No structural issues found.[/bold green]")
    console.print()


def _modularity_label(q: float) -> str:
    if q > 0.5:
        return "well-separated modules"
    elif q > 0.3:
        return "moderate separation"
    elif q > 0.1:
        return "some coupling between modules"
    else:
        return "highly interconnected"
