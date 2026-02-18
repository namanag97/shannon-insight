#!/usr/bin/env python3
"""
UAT Phase 1 & Phase 2 QA Script

Runs full Phase 1 (parsing) and Phase 2 (graph) analysis on all UAT codebases
and generates a comparison report.

Usage:
    python run_phase1_phase2_qa.py [--codebases-dir PATH] [--output-dir PATH]
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

# Add src to path if running from uat directory
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shannon_insight.scanning import SyntaxExtractor, resolve_all_imports
from shannon_insight.persistence.facts import FactDatabase
from shannon_insight.persistence.fact_models import FileFact, AnalysisSession
from shannon_insight.graph.builder import build_code_graph_from_facts
from shannon_insight.persistence.graph_store import GraphStore
from shannon_insight.graph.algorithms import run_graph_algorithms, run_code_graph_algorithms
from shannon_insight.graph.models import DependencyGraph


@dataclass
class QAResult:
    """Results from Phase 1 & 2 QA on a single codebase."""

    name: str
    path: str

    # Phase 1 metrics
    files_scanned: int = 0
    functions: int = 0
    classes: int = 0
    imports: int = 0

    imports_resolved: int = 0
    imports_stdlib: int = 0
    imports_phantom: int = 0

    return_type_coverage: float = 0.0
    param_type_coverage: float = 0.0
    field_type_coverage: float = 0.0

    # Phase 2 metrics
    file_nodes: int = 0
    function_nodes: int = 0
    class_nodes: int = 0
    type_nodes: int = 0

    import_edges: int = 0
    call_edges: int = 0
    inherit_edges: int = 0
    contains_edges: int = 0
    returns_edges: int = 0
    param_type_edges: int = 0
    field_type_edges: int = 0

    file_cycles: int = 0
    function_cycles: int = 0
    dead_functions: int = 0
    communities: int = 0
    modularity: float = 0.0

    # Performance
    scan_time: float = 0.0
    resolve_time: float = 0.0
    store_time: float = 0.0
    build_time: float = 0.0
    algo_time: float = 0.0
    total_time: float = 0.0
    files_per_second: float = 0.0

    # Storage
    db_size_kb: float = 0.0
    kb_per_file: float = 0.0

    # Languages detected
    languages: dict[str, int] = field(default_factory=dict)

    # Errors
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "phase1": {
                "files": self.files_scanned,
                "functions": self.functions,
                "classes": self.classes,
                "imports": self.imports,
                "resolution": {
                    "resolved": self.imports_resolved,
                    "stdlib": self.imports_stdlib,
                    "phantom": self.imports_phantom,
                },
                "type_coverage": {
                    "return_type": self.return_type_coverage,
                    "param_types": self.param_type_coverage,
                    "field_types": self.field_type_coverage,
                },
                "languages": self.languages,
            },
            "phase2": {
                "nodes": {
                    "files": self.file_nodes,
                    "functions": self.function_nodes,
                    "classes": self.class_nodes,
                    "types": self.type_nodes,
                },
                "edges": {
                    "imports": self.import_edges,
                    "calls": self.call_edges,
                    "inherits": self.inherit_edges,
                    "contains": self.contains_edges,
                    "returns": self.returns_edges,
                    "param_type": self.param_type_edges,
                    "field_type": self.field_type_edges,
                },
                "analysis": {
                    "file_cycles": self.file_cycles,
                    "function_cycles": self.function_cycles,
                    "dead_functions": self.dead_functions,
                    "communities": self.communities,
                    "modularity": self.modularity,
                },
            },
            "performance": {
                "scan_time": self.scan_time,
                "resolve_time": self.resolve_time,
                "store_time": self.store_time,
                "build_time": self.build_time,
                "algo_time": self.algo_time,
                "total_time": self.total_time,
                "files_per_second": self.files_per_second,
            },
            "storage": {
                "db_size_kb": self.db_size_kb,
                "kb_per_file": self.kb_per_file,
            },
            "errors": self.errors,
        }


def run_qa_on_codebase(codebase_path: Path, output_dir: Path) -> QAResult:
    """Run Phase 1 & 2 QA on a single codebase."""

    name = codebase_path.name
    result = QAResult(name=name, path=str(codebase_path))

    db_path = output_dir / f"{name}_qa.db"
    if db_path.exists():
        db_path.unlink()

    try:
        fact_db = FactDatabase(str(db_path))
        graph_store = GraphStore(str(db_path))

        session_id = str(uuid.uuid4())
        session = AnalysisSession(
            id=session_id,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
            commit_sha="uat-test",
            analyzed_path=str(codebase_path),
            tool_version="0.1.0",
            config_hash="uat",
            status="running",
        )
        fact_db.create_session(session)

        # ═══════════════════════════════════════════════════════════════
        # PHASE 1: Scanning (parallel)
        # ═══════════════════════════════════════════════════════════════

        extractor = SyntaxExtractor()

        # Find all source files (Python, TypeScript, Go, etc.)
        extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".rs", ".rb"}
        all_files = []
        for ext in extensions:
            all_files.extend(codebase_path.rglob(f"*{ext}"))

        # Filter out test files and node_modules
        all_files = [
            f for f in all_files
            if "__pycache__" not in str(f)
            and "node_modules" not in str(f)
            and ".git" not in str(f)
            and "vendor" not in str(f)
            and "dist" not in str(f)
            and "build" not in str(f)
        ]

        # Scan files in parallel
        t0 = time.time()
        file_syntaxes = extractor.extract_all(all_files, codebase_path, parallel=True)
        result.scan_time = time.time() - t0
        result.files_scanned = len(file_syntaxes)

        # Track languages
        for fs in file_syntaxes.values():
            lang = fs.language
            result.languages[lang] = result.languages.get(lang, 0) + 1

        if result.files_scanned == 0:
            result.errors.append("No files scanned")
            return result

        # Resolve imports
        t0 = time.time()
        resolve_all_imports(file_syntaxes)
        result.resolve_time = time.time() - t0

        # Count resolution stats
        for fs in file_syntaxes.values():
            for imp in fs.imports:
                if imp.resolved_path:
                    result.imports_resolved += 1
                elif imp.is_stdlib:
                    result.imports_stdlib += 1
                else:
                    result.imports_phantom += 1

        # Store facts
        t0 = time.time()
        for fs in file_syntaxes.values():
            ff = FileFact.from_file_syntax(fs, session_id, "0.1.0", "tree-sitter")
            fact_db.store_file_fact(ff)
        result.store_time = time.time() - t0

        # Get stats from DB
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("SELECT COUNT(*) FROM function_facts")
        result.functions = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM class_facts")
        result.classes = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM import_facts")
        result.imports = cursor.fetchone()[0]

        # Type coverage
        if result.functions > 0:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM function_facts WHERE return_type IS NOT NULL AND return_type != ''"
            )
            result.return_type_coverage = cursor.fetchone()[0] / result.functions * 100

            cursor = conn.execute(
                "SELECT COUNT(*) FROM function_facts WHERE param_types != '{}' AND param_types IS NOT NULL"
            )
            result.param_type_coverage = cursor.fetchone()[0] / result.functions * 100

        if result.classes > 0:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM class_facts WHERE field_types != '{}' AND field_types IS NOT NULL"
            )
            result.field_type_coverage = cursor.fetchone()[0] / result.classes * 100

        # ═══════════════════════════════════════════════════════════════
        # PHASE 2: Graph Building
        # ═══════════════════════════════════════════════════════════════

        file_facts = fact_db.get_file_facts_for_session(session_id)
        call_targets = fact_db.get_call_targets_for_session(session_id)
        class_bases = fact_db.get_class_bases_for_session(session_id)
        imports = fact_db.get_imports_for_session(session_id)

        t0 = time.time()
        graph = build_code_graph_from_facts(file_facts, call_targets, class_bases, imports)
        result.build_time = time.time() - t0

        # Node counts
        result.file_nodes = len(graph.file_nodes)
        result.function_nodes = len(graph.function_nodes)
        result.class_nodes = len(graph.class_nodes)
        result.type_nodes = len(graph.type_nodes)

        # Edge counts
        result.import_edges = sum(len(v) for v in graph.import_edges.values())
        result.call_edges = sum(len(v) for v in graph.call_edges.values())
        result.inherit_edges = sum(len(v) for v in graph.inherit_edges.values())
        result.contains_edges = sum(len(v) for v in graph.contains_edges.values())
        result.returns_edges = len(graph.returns_edges)
        result.param_type_edges = sum(len(v) for v in graph.param_type_edges.values())
        result.field_type_edges = sum(len(v) for v in graph.field_type_edges.values())

        # Store graph
        graph_store.store_code_graph(session_id, graph)

        # Run algorithms
        dep_graph = DependencyGraph()
        dep_graph.adjacency = {f: list(graph.import_edges.get(f, [])) for f in graph.file_nodes}
        dep_graph.reverse = {f: list(graph.imported_by.get(f, [])) for f in graph.file_nodes}
        dep_graph.all_nodes = graph.file_nodes
        dep_graph.edge_count = result.import_edges

        t0 = time.time()
        analysis = run_graph_algorithms(dep_graph)
        analysis = run_code_graph_algorithms(graph, analysis)
        result.algo_time = time.time() - t0

        result.file_cycles = len(analysis.cycles)
        result.function_cycles = len(analysis.function_cycles)
        result.dead_functions = len(analysis.dead_functions)
        result.communities = len(analysis.communities)
        result.modularity = analysis.modularity_score

        # Store analysis
        graph_store.store_graph_analysis(session_id, analysis, graph)

        conn.close()

        # Storage stats
        result.db_size_kb = os.path.getsize(str(db_path)) / 1024
        result.kb_per_file = result.db_size_kb / max(result.files_scanned, 1)

        # Performance summary
        result.total_time = (
            result.scan_time + result.resolve_time + result.store_time +
            result.build_time + result.algo_time
        )
        result.files_per_second = result.files_scanned / max(result.total_time, 0.001)

    except Exception as e:
        result.errors.append(f"Fatal error: {str(e)}")

    return result


def print_summary(results: list[QAResult]) -> None:
    """Print a summary table of all QA results."""

    print("\n" + "=" * 100)
    print("PHASE 1 & 2 UAT RESULTS SUMMARY")
    print("=" * 100)

    # Header
    print(f"\n{'Codebase':<15} {'Files':>7} {'Funcs':>7} {'Classes':>7} {'Edges':>8} "
          f"{'Types%':>7} {'Phantom':>8} {'Time':>7} {'KB/file':>8}")
    print("-" * 100)

    for r in results:
        total_edges = (r.import_edges + r.call_edges + r.inherit_edges +
                      r.contains_edges + r.returns_edges + r.param_type_edges + r.field_type_edges)
        phantom_pct = (r.imports_phantom / max(r.imports, 1)) * 100

        print(f"{r.name:<15} {r.files_scanned:>7} {r.functions:>7} {r.classes:>7} "
              f"{total_edges:>8} {r.return_type_coverage:>6.1f}% {phantom_pct:>7.1f}% "
              f"{r.total_time:>6.1f}s {r.kb_per_file:>7.1f}")

    print("-" * 100)

    # Totals
    total_files = sum(r.files_scanned for r in results)
    total_funcs = sum(r.functions for r in results)
    total_classes = sum(r.classes for r in results)
    total_time = sum(r.total_time for r in results)
    total_size = sum(r.db_size_kb for r in results)

    print(f"\nTOTALS: {total_files} files, {total_funcs} functions, {total_classes} classes")
    print(f"PERFORMANCE: {total_time:.1f}s total, {total_files/max(total_time, 0.001):.1f} files/s avg")
    print(f"STORAGE: {total_size/1024:.2f} MB total")

    # Errors
    errors = [(r.name, e) for r in results for e in r.errors]
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for name, err in errors[:10]:
            print(f"  [{name}] {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")


def main():
    parser = argparse.ArgumentParser(description="Run Phase 1 & 2 QA on UAT codebases")
    parser.add_argument(
        "--codebases-dir",
        type=Path,
        default=Path(__file__).parent / "codebases",
        help="Directory containing UAT codebases",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "results",
        help="Directory for output databases and reports",
    )
    args = parser.parse_args()

    if not args.codebases_dir.exists():
        print(f"ERROR: Codebases directory not found: {args.codebases_dir}")
        print("Run download_codebases.sh first!")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Find all codebases
    codebases = [d for d in args.codebases_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    codebases.sort(key=lambda x: x.name)

    print(f"Found {len(codebases)} codebases to analyze")

    results = []
    for i, codebase in enumerate(codebases, 1):
        print(f"\n▶ [{i}/{len(codebases)}] Analyzing {codebase.name}...")
        result = run_qa_on_codebase(codebase, args.output_dir)
        results.append(result)
        print(f"  Files: {result.files_scanned}, Time: {result.total_time:.1f}s, "
              f"Errors: {len(result.errors)}")

    # Print summary
    print_summary(results)

    # Save JSON report
    report_path = args.output_dir / "qa_report.json"
    with open(report_path, "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=2)
    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    main()
