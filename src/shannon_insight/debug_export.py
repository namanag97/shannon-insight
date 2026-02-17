"""Debug export — dump pipeline state to readable JSON at each stage.

Usage:
    shannon-insight --debug-export ./debug_output

This writes numbered JSON files for each pipeline stage:
    01_scanning.json       — FileMetrics per file
    02_syntax.json         — FileSyntax per file
    03_structural.json     — Graph, PageRank, cycles, communities
    04_temporal.json       — Git history, churn, co-change
    05_spectral.json       — Fiedler value, spectral gap
    06_semantic.json       — Roles, concepts, naming drift
    07_architecture.json   — Modules, layers, violations
    08_fusion.json         — All 62 signals unified
    09_findings.json       — Final findings

Each file includes:
    - stage metadata (name, data type, count)
    - readable per-file data grouped by file path
    - summary statistics where relevant
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .insights.models import Finding
    from .insights.store import AnalysisStore


def _safe_serialize(obj: Any) -> Any:
    """Convert object to JSON-serializable form."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_safe_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, Path):
        return str(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return _safe_serialize(asdict(obj))
    if hasattr(obj, "__dict__"):
        return _safe_serialize(obj.__dict__)
    return str(obj)


def _write_stage(output_dir: Path, filename: str, data: dict) -> None:
    """Write a stage's data to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


class DebugExporter:
    """Export pipeline state at each stage for debugging."""

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.timestamp = datetime.now().isoformat()

    def export_scanning(self, store: AnalysisStore) -> None:
        """Export after scanning phase (FileSyntax)."""
        files = store.files

        # Group by file for readability
        per_file = {}
        for path, fs in files.items():
            per_file[path] = {
                "lines": fs.lines,
                "tokens": fs.tokens,
                "functions": fs.function_count,
                "classes": fs.class_count,
                "complexity_score": round(fs.complexity, 4),
                "nesting_depth": fs.max_nesting,
                "imports": [imp.source for imp in fs.imports],
                "function_sizes": fs.function_sizes,
            }

        data = {
            "stage": "01_scanning",
            "description": "File syntax from parsing (FileSyntax)",
            "timestamp": self.timestamp,
            "summary": {
                "total_files": len(files),
                "total_lines": sum(fs.lines for fs in files.values()),
                "total_functions": sum(fs.function_count for fs in files.values()),
                "languages": {fs.language for fs in files.values()},
            },
            "per_file": per_file,
        }

        _write_stage(self.output_dir, "01_scanning.json", data)

    def export_syntax(self, store: AnalysisStore) -> None:
        """Export after syntax extraction (FileSyntax)."""
        if not store.file_syntax.available:
            return

        file_syntax = store.file_syntax.value

        per_file = {}
        for path, syntax in file_syntax.items():
            per_file[path] = {
                "language": getattr(syntax, "language", "unknown"),
                "imports": getattr(syntax, "imports", []),
                "exports": getattr(syntax, "exports", []),
                "functions": getattr(syntax, "functions", []),
                "classes": getattr(syntax, "classes", []),
                "decorators": getattr(syntax, "decorators", []),
                "has_main_guard": getattr(syntax, "has_main_guard", False),
            }

        data = {
            "stage": "02_syntax",
            "description": "Deep syntax extraction (tree-sitter or regex fallback)",
            "timestamp": self.timestamp,
            "produced_by": store.file_syntax.produced_by,
            "summary": {
                "total_files": len(file_syntax),
                "with_main_guard": sum(
                    1 for s in file_syntax.values() if getattr(s, "has_main_guard", False)
                ),
            },
            "per_file": per_file,
        }

        _write_stage(self.output_dir, "02_syntax.json", data)

    def export_structural(self, store: AnalysisStore) -> None:
        """Export after StructuralAnalyzer (graph, PageRank, cycles, communities)."""
        if not store.structural.available:
            return

        analysis = store.structural.value
        graph = analysis.graph
        # Graph metrics are in graph_analysis, not directly on CodebaseAnalysis
        ga = analysis.graph_analysis

        # Dependency edges (readable format)
        edges = []
        for source, targets in graph.adjacency.items():
            for target in targets:
                edges.append({"from": source, "to": target})

        # Per-file graph metrics
        per_file = {}
        for path in graph.all_nodes:
            per_file[path] = {
                "pagerank": round(ga.pagerank.get(path, 0), 6),
                "betweenness": round(ga.betweenness.get(path, 0), 6),
                "in_degree": ga.in_degree.get(path, 0),
                "out_degree": ga.out_degree.get(path, 0),
                "depth": ga.depth.get(path, -1),
                "is_orphan": ga.is_orphan.get(path, False),
                "community": ga.node_community.get(path, -1),
            }

        # Cycles (SCCs with > 1 node)
        cycles = []
        for cycle in ga.cycles:
            cycles.append(
                {
                    "files": list(cycle.nodes),
                    "size": len(cycle.nodes),
                }
            )

        # Communities
        communities = []
        for comm in ga.communities:
            communities.append(
                {
                    "id": comm.id,
                    "files": list(comm.members),
                    "size": len(comm.members),
                }
            )

        data = {
            "stage": "03_structural",
            "description": "Dependency graph analysis (PageRank, SCC, Louvain)",
            "timestamp": self.timestamp,
            "produced_by": store.structural.produced_by,
            "summary": {
                "total_nodes": len(graph.all_nodes),
                "total_edges": graph.edge_count,
                "cycle_count": len(cycles),
                "community_count": len(communities),
                "modularity": round(ga.modularity_score, 4),
                "centrality_gini": round(getattr(ga, "centrality_gini", 0), 4),
                "orphan_count": sum(1 for v in ga.is_orphan.values() if v),
            },
            "edges": edges[:100],  # Cap for readability
            "edges_truncated": len(edges) > 100,
            "cycles": cycles,
            "communities": communities,
            "per_file": per_file,
        }

        _write_stage(self.output_dir, "03_structural.json", data)

    def export_temporal(self, store: AnalysisStore) -> None:
        """Export after TemporalAnalyzer (git history, churn, co-change)."""
        data: dict[str, Any] = {
            "stage": "04_temporal",
            "description": "Git history analysis (churn, co-change, author metrics)",
            "timestamp": self.timestamp,
        }

        # Git history
        if store.git_history.available:
            history = store.git_history.value
            data["git_history"] = {
                "total_commits": history.total_commits,
                "span_days": history.span_days,
                "file_count": len(history.file_set),
                "sample_commits": [
                    {
                        "hash": c.hash[:8],
                        "author": c.author,
                        "files": len(c.files),
                        "subject": c.subject[:80] if c.subject else "",
                    }
                    for c in history.commits[:10]
                ],
            }
            data["produced_by_history"] = store.git_history.produced_by

        # Churn per file
        if store.churn.available:
            churn = store.churn.value
            per_file_churn = {}
            for path, series in churn.items():
                per_file_churn[path] = {
                    "total_changes": series.total_changes,
                    "trajectory": series.trajectory,
                    "slope": round(series.slope, 4),
                    "cv": round(series.cv, 4),
                    "bus_factor": round(series.bus_factor, 2),
                    "author_entropy": round(series.author_entropy, 4),
                    "fix_ratio": round(series.fix_ratio, 4),
                    "refactor_ratio": round(series.refactor_ratio, 4),
                    "change_entropy": round(getattr(series, "change_entropy", 0), 4),
                }
            data["churn"] = {
                "file_count": len(per_file_churn),
                "per_file": per_file_churn,
            }
            data["produced_by_churn"] = store.churn.produced_by

        # Co-change matrix
        if store.cochange.available:
            cochange = store.cochange.value
            # Top co-change pairs by lift
            pairs = []
            for (file_a, file_b), pair in cochange.pairs.items():
                pairs.append(
                    {
                        "file_a": file_a,
                        "file_b": file_b,
                        "cochange_count": pair.cochange_count,
                        "confidence_a_b": round(pair.confidence_a_b, 4),
                        "confidence_b_a": round(pair.confidence_b_a, 4),
                        "lift": round(pair.lift, 4),
                    }
                )
            pairs.sort(key=lambda p: p["lift"], reverse=True)
            data["cochange"] = {
                "pair_count": len(pairs),
                "top_pairs": pairs[:20],
            }
            data["produced_by_cochange"] = store.cochange.produced_by

        _write_stage(self.output_dir, "04_temporal.json", data)

    def export_spectral(self, store: AnalysisStore) -> None:
        """Export after SpectralAnalyzer (Fiedler value, spectral gap)."""
        if not store.spectral.available:
            return

        spectral = store.spectral.value

        data = {
            "stage": "05_spectral",
            "description": "Spectral analysis (Laplacian eigenvalues, algebraic connectivity)",
            "timestamp": self.timestamp,
            "produced_by": store.spectral.produced_by,
            "spectral": {
                "fiedler_value": round(spectral.fiedler_value, 6),
                "spectral_gap": round(spectral.spectral_gap, 6),
                "num_components": spectral.num_components,
                "eigenvalues": [round(e, 6) for e in spectral.eigenvalues[:10]],
            },
        }

        _write_stage(self.output_dir, "05_spectral.json", data)

    def export_semantic(self, store: AnalysisStore) -> None:
        """Export after SemanticAnalyzer (roles, concepts, naming drift)."""
        data: dict[str, Any] = {
            "stage": "06_semantic",
            "description": "Semantic analysis (roles, concepts, naming drift)",
            "timestamp": self.timestamp,
        }

        # Roles
        if store.roles.available:
            roles = store.roles.value
            role_counts: dict[str, int] = {}
            for role in roles.values():
                role_counts[role] = role_counts.get(role, 0) + 1
            data["roles"] = {
                "file_count": len(roles),
                "distribution": role_counts,
                "per_file": dict(roles),
            }
            data["produced_by_roles"] = store.roles.produced_by

        # Semantics
        if store.semantics.available:
            semantics = store.semantics.value
            per_file_sem = {}
            for path, sem in semantics.items():
                per_file_sem[path] = {
                    "role": getattr(sem, "role", "UNKNOWN"),
                    "concept_count": getattr(sem, "concept_count", 0),
                    "concept_entropy": round(getattr(sem, "concept_entropy", 0), 4),
                    "naming_drift": round(getattr(sem, "naming_drift", 0), 4),
                    "concepts": [
                        {"topic": c.topic, "weight": round(c.weight, 4)}
                        for c in getattr(sem, "concepts", [])[:5]
                    ],
                }
            data["semantics"] = {
                "file_count": len(per_file_sem),
                "per_file": per_file_sem,
            }
            data["produced_by_semantics"] = store.semantics.produced_by

        _write_stage(self.output_dir, "06_semantic.json", data)

    def export_architecture(self, store: AnalysisStore) -> None:
        """Export after ArchitectureAnalyzer (modules, layers, violations)."""
        if not store.architecture.available:
            return

        arch = store.architecture.value

        # Modules with Martin metrics
        modules = {}
        for path, mod in arch.modules.items():
            modules[path] = {
                "file_count": mod.file_count,
                "cohesion": round(mod.cohesion, 4),
                "coupling": round(mod.coupling, 4),
                "instability": round(mod.instability, 4) if mod.instability is not None else None,
                "abstractness": round(mod.abstractness, 4),
                "main_seq_distance": round(mod.main_seq_distance, 4)
                if mod.main_seq_distance
                else None,
                "afferent_coupling": mod.afferent_coupling,
                "efferent_coupling": mod.efferent_coupling,
                "layer": mod.layer,
                "dominant_role": mod.dominant_role,
            }

        # Layers
        layers = []
        for layer in arch.layers:
            layers.append(
                {
                    "depth": layer.depth,
                    "label": layer.label,
                    "modules": layer.modules,
                }
            )

        # Violations
        violations = []
        for v in arch.violations:
            violations.append(
                {
                    "source_module": v.source_module,
                    "target_module": v.target_module,
                    "violation_type": v.violation_type,
                    "edge_count": v.edge_count,
                }
            )

        data = {
            "stage": "07_architecture",
            "description": "Architecture analysis (modules, layers, Martin metrics, violations)",
            "timestamp": self.timestamp,
            "produced_by": store.architecture.produced_by,
            "summary": {
                "module_count": len(modules),
                "layer_count": len(layers),
                "violation_count": len(violations),
                "violation_rate": round(arch.violation_rate, 4),
                "has_layering": arch.has_layering,
                "max_depth": arch.max_depth,
            },
            "modules": modules,
            "layers": layers,
            "violations": violations,
        }

        _write_stage(self.output_dir, "07_architecture.json", data)

    def export_fusion(self, store: AnalysisStore) -> None:
        """Export after SignalFusionAnalyzer (all 62 signals unified)."""
        if not store.signal_field.available:
            return

        field = store.signal_field.value

        # Per-file signals
        per_file = {}
        for path, signals in field.per_file.items():
            per_file[path] = {
                # Hierarchical context
                "parent_dir": signals.parent_dir,
                "module_path": signals.module_path,
                "dir_depth": signals.dir_depth,
                "siblings_count": signals.siblings_count,
                # Scanning signals
                "lines": signals.lines,
                "function_count": signals.function_count,
                "class_count": signals.class_count,
                "max_nesting": signals.max_nesting,
                "import_count": signals.import_count,
                "stub_ratio": round(signals.stub_ratio, 4),
                # Graph signals
                "pagerank": round(signals.pagerank, 6),
                "betweenness": round(signals.betweenness, 6),
                "in_degree": signals.in_degree,
                "out_degree": signals.out_degree,
                "depth": signals.depth,
                "is_orphan": signals.is_orphan,
                "community": signals.community,
                # Semantic signals
                "role": signals.role,
                "concept_count": signals.concept_count,
                "concept_entropy": round(signals.concept_entropy, 4),
                "naming_drift": round(signals.naming_drift, 4),
                "cognitive_load": round(signals.cognitive_load, 4),
                # Temporal signals
                "total_changes": signals.total_changes,
                "churn_trajectory": signals.churn_trajectory,
                "churn_cv": round(signals.churn_cv, 4),
                "bus_factor": round(signals.bus_factor, 2),
                "author_entropy": round(signals.author_entropy, 4),
                "fix_ratio": round(signals.fix_ratio, 4),
                # Composites
                "risk_score": round(signals.risk_score, 4),
                "raw_risk": round(getattr(signals, "raw_risk", 0), 4),
            }

        # Per-module signals
        per_module = {}
        for path, mod in field.per_module.items():
            per_module[path] = {
                "file_count": mod.file_count,
                "cohesion": round(mod.cohesion, 4),
                "coupling": round(mod.coupling, 4),
                "instability": round(mod.instability, 4) if mod.instability is not None else None,
                "abstractness": round(mod.abstractness, 4),
                "health_score": round(mod.health_score, 4),
                "velocity": round(mod.velocity, 4),
                "knowledge_gini": round(mod.knowledge_gini, 4),
            }

        # Per-directory signals (NEW)
        per_directory = {}
        for path, ds in field.per_directory.items():
            per_directory[path] = {
                "file_count": ds.file_count,
                "total_lines": ds.total_lines,
                "total_functions": ds.total_functions,
                "avg_complexity": round(ds.avg_complexity, 4),
                "avg_churn": round(ds.avg_churn, 4),
                "avg_risk": round(ds.avg_risk, 4),
                "dominant_role": ds.dominant_role,
                "dominant_trajectory": ds.dominant_trajectory,
                "hotspot_file_count": ds.hotspot_file_count,
                "high_risk_file_count": ds.high_risk_file_count,
                "module_path": ds.module_path,
            }

        # Global signals
        global_signals = {
            "modularity": round(field.global_signals.modularity, 4),
            "fiedler_value": round(field.global_signals.fiedler_value, 6),
            "spectral_gap": round(field.global_signals.spectral_gap, 6),
            "cycle_count": field.global_signals.cycle_count,
            "centrality_gini": round(field.global_signals.centrality_gini, 4),
            "orphan_ratio": round(field.global_signals.orphan_ratio, 4),
            "codebase_health": round(field.global_signals.codebase_health, 4),
            "architecture_health": round(field.global_signals.architecture_health, 4),
            "wiring_score": round(field.global_signals.wiring_score, 4),
        }

        # Delta-h (health Laplacian impact)
        delta_h = {path: round(v, 4) for path, v in field.delta_h.items()}

        data = {
            "stage": "08_fusion",
            "description": "Signal fusion (all signals unified into SignalField)",
            "timestamp": self.timestamp,
            "produced_by": store.signal_field.produced_by,
            "summary": {
                "tier": field.tier.value,  # Convert Tier enum to string
                "file_count": len(per_file),
                "directory_count": len(per_directory),
                "module_count": len(per_module),
                "signal_count_per_file": 40,  # 36 + 4 hierarchical
                "signal_count_per_directory": 11,
                "signal_count_per_module": 15,
                "signal_count_global": 11,
            },
            "global_signals": global_signals,
            "per_file": per_file,
            "per_directory": per_directory,
            "per_module": per_module,
            "delta_h": delta_h,
        }

        _write_stage(self.output_dir, "08_fusion.json", data)

    def export_findings(self, findings: list[Finding]) -> None:
        """Export final findings."""
        # Group by type
        by_type: dict[str, list[dict]] = {}
        for f in findings:
            entry = {
                "title": f.title,
                "severity": round(f.severity, 4),
                "files": f.files,
                "confidence": round(f.confidence, 4),
                "effort": f.effort,
                "scope": f.scope,
                "suggestion": f.suggestion,
                "evidence": [
                    {
                        "signal": e.signal,
                        "value": round(e.value, 4),
                        "percentile": round(e.percentile, 1),
                        "description": e.description,
                    }
                    for e in f.evidence
                ],
            }
            by_type.setdefault(f.finding_type, []).append(entry)

        data = {
            "stage": "09_findings",
            "description": "Final findings (deduplicated, ranked, capped)",
            "timestamp": self.timestamp,
            "summary": {
                "total_findings": len(findings),
                "by_type": {k: len(v) for k, v in by_type.items()},
                "severity_distribution": {
                    "high": sum(1 for f in findings if f.severity > 0.8),
                    "medium": sum(1 for f in findings if 0.5 < f.severity <= 0.8),
                    "low": sum(1 for f in findings if f.severity <= 0.5),
                },
            },
            "by_type": by_type,
        }

        _write_stage(self.output_dir, "09_findings.json", data)

    def write_index(self, store: AnalysisStore, findings: list[Finding]) -> None:
        """Write index.json summarizing all stages."""
        stages = []

        # Check which stages produced data
        if store.files:
            stages.append(
                {
                    "file": "01_scanning.json",
                    "stage": "Scanning",
                    "description": "FileSyntax from parsing",
                    "items": store.file_count,
                }
            )

        if store.file_syntax.available:
            stages.append(
                {
                    "file": "02_syntax.json",
                    "stage": "Syntax Extraction",
                    "description": "FileSyntax (tree-sitter/regex)",
                    "items": len(store.file_syntax.value),
                }
            )

        if store.structural.available:
            analysis = store.structural.value
            stages.append(
                {
                    "file": "03_structural.json",
                    "stage": "Structural Analysis",
                    "description": "Graph, PageRank, cycles, communities",
                    "items": len(analysis.graph.all_nodes),
                }
            )

        if store.git_history.available or store.churn.available:
            stages.append(
                {
                    "file": "04_temporal.json",
                    "stage": "Temporal Analysis",
                    "description": "Git history, churn, co-change",
                    "items": store.git_history.value.total_commits
                    if store.git_history.available
                    else 0,
                }
            )

        if store.spectral.available:
            stages.append(
                {
                    "file": "05_spectral.json",
                    "stage": "Spectral Analysis",
                    "description": "Laplacian eigenvalues, Fiedler value",
                    "items": 1,
                }
            )

        if store.semantics.available or store.roles.available:
            stages.append(
                {
                    "file": "06_semantic.json",
                    "stage": "Semantic Analysis",
                    "description": "Roles, concepts, naming drift",
                    "items": len(store.semantics.value) if store.semantics.available else 0,
                }
            )

        if store.architecture.available:
            stages.append(
                {
                    "file": "07_architecture.json",
                    "stage": "Architecture Analysis",
                    "description": "Modules, layers, Martin metrics",
                    "items": len(store.architecture.value.modules),
                }
            )

        if store.signal_field.available:
            stages.append(
                {
                    "file": "08_fusion.json",
                    "stage": "Signal Fusion",
                    "description": "All 62 signals unified",
                    "items": len(store.signal_field.value.per_file),
                }
            )

        if findings:
            stages.append(
                {
                    "file": "09_findings.json",
                    "stage": "Findings",
                    "description": "Final prioritized findings",
                    "items": len(findings),
                }
            )

        index = {
            "title": "Shannon Insight Debug Export",
            "timestamp": self.timestamp,
            "root_dir": store.root_dir,
            "total_files": store.file_count,
            "available_slots": sorted(store.available),
            "stages": stages,
        }

        _write_stage(self.output_dir, "00_index.json", index)
