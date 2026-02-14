"""Build the JSON dashboard state from analysis results."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from ..cli._common import display_score
from ..cli._concerns import organize_by_concerns
from ..cli._finding_display import get_display_config, get_severity_display
from ..cli._focus import get_verdict, identify_focus_point
from ..insights.models import Finding, InsightResult
from ..persistence.models import TensorSnapshot
from ..persistence.queries import HistoryQuery

logger = logging.getLogger(__name__)

# ── Category mapping (plan spec) ──────────────────────────────────────

CATEGORY_MAP: dict[str, str] = {
    # incomplete
    "hollow_code": "incomplete",
    "phantom_imports": "incomplete",
    "orphan_code": "incomplete",
    "incomplete_implementation": "incomplete",
    "duplicate_incomplete": "incomplete",
    # fragile
    "high_risk_hub": "fragile",
    "god_file": "fragile",
    "bug_magnet": "fragile",
    "thrashing_code": "fragile",
    "unstable_file": "fragile",
    "weak_link": "fragile",
    "bug_attractor": "fragile",
    "chronic_problem": "fragile",
    "directory_hotspot": "fragile",
    # tangled
    "hidden_coupling": "tangled",
    "accidental_coupling": "tangled",
    "dead_dependency": "tangled",
    "copy_paste_clone": "tangled",
    "layer_violation": "tangled",
    "zone_of_pain": "tangled",
    "boundary_mismatch": "tangled",
    "flat_architecture": "tangled",
    "architecture_erosion": "tangled",
    "naming_drift": "tangled",
    # team
    "knowledge_silo": "team",
    "truck_factor": "team",
    "review_blindspot": "team",
    "conway_violation": "team",
}

CATEGORY_LABELS = {
    "incomplete": "Incomplete",
    "fragile": "Fragile",
    "tangled": "Tangled",
    "team": "Team Risk",
}


def _health_label(score: float) -> str:
    """Map a 1-10 health score to a human label."""
    if score >= 8:
        return "Healthy"
    if score >= 6:
        return "Moderate"
    if score >= 4:
        return "At Risk"
    return "Critical"


def _finding_to_dict(f: Finding) -> dict[str, Any]:
    """Serialize a Finding to a JSON-safe dict."""
    display = get_display_config(f.finding_type)
    _icon, _color, sev_label = get_severity_display(f.severity)

    evidence = []
    for e in f.evidence:
        evidence.append(
            {
                "signal": e.signal,
                "value": e.value,
                "percentile": e.percentile,
                "description": e.description,
            }
        )

    return {
        "finding_type": f.finding_type,
        "label": display["label"],
        "icon": display["icon"],
        "severity": round(f.severity, 3),
        "severity_label": sev_label,
        "title": f.title,
        "files": list(f.files),
        "evidence": evidence,
        "suggestion": f.suggestion,
        "interpretation": display.get("interpretation", ""),
        "confidence": round(f.confidence, 3),
        "effort": f.effort,
        "scope": f.scope,
    }


def build_dashboard_state(
    result: InsightResult,
    snapshot: TensorSnapshot,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Convert analysis results to the full dashboard JSON state.

    This is the single source of truth for ``GET /api/state`` and
    the WebSocket ``complete`` message.

    Parameters
    ----------
    result:
        The InsightResult from analysis.
    snapshot:
        The TensorSnapshot from analysis.
    db_path:
        Optional path to .shannon/history.db for trend data.
    """
    findings = result.findings
    file_signals = snapshot.file_signals or {}
    global_signals = snapshot.global_signals or {}
    module_signals = snapshot.module_signals or {}

    # ── Health score ──────────────────────────────────────────────
    raw_health = global_signals.get("codebase_health", 0.5)
    health_display = display_score(raw_health)

    # ── Verdict ───────────────────────────────────────────────────
    total_findings = len(findings)
    focus, alternatives = identify_focus_point(snapshot, findings, n_alternatives=5)
    verdict_text, verdict_color = get_verdict(raw_health, focus, total_findings)

    # ── Categories ────────────────────────────────────────────────
    categories: dict[str, dict[str, Any]] = {}
    for cat_key in ("incomplete", "fragile", "tangled", "team"):
        cat_findings = [f for f in findings if CATEGORY_MAP.get(f.finding_type) == cat_key]
        high_count = sum(1 for f in cat_findings if f.severity >= 0.8)
        categories[cat_key] = {
            "label": CATEGORY_LABELS[cat_key],
            "count": len(cat_findings),
            "high_count": high_count,
            "findings": [_finding_to_dict(f) for f in cat_findings],
        }

    # ── Focus point ───────────────────────────────────────────────
    focus_data = None
    if focus:
        focus_data = {
            "path": focus.path,
            "actionability": round(focus.actionability, 3),
            "why": focus.why_summary(),
            "risk_score": round(focus.risk_score, 3),
            "impact_score": round(focus.impact_score, 3),
            "tractability_score": round(focus.tractability_score, 3),
            "confidence_score": round(focus.confidence_score, 3),
            "findings": [_finding_to_dict(f) for f in focus.findings],
            "alternatives": [
                {
                    "path": a.path,
                    "actionability": round(a.actionability, 3),
                    "why": a.why_summary(),
                }
                for a in alternatives
            ],
        }

    # ── File data ─────────────────────────────────────────────────
    files: dict[str, dict[str, Any]] = {}
    # Query per-file signal trends if db available
    file_trends: dict[str, dict[str, list[float]]] = {}
    if db_path:
        file_trends = _query_file_signal_trends(db_path, list(file_signals.keys()))

    for path, sig_dict in file_signals.items():
        # Collect findings for this file
        file_findings = [f for f in findings if path in f.files]
        file_data = {
            "health": round(display_score(sig_dict.get("file_health_score", 0.5)), 1),
            "role": sig_dict.get("role", "UNKNOWN"),
            "lines": sig_dict.get("lines", 0),
            "risk_score": round(sig_dict.get("risk_score", 0.0), 3),
            "pagerank": round(sig_dict.get("pagerank", 0.0), 4),
            "total_changes": sig_dict.get("total_changes", 0),
            "churn_cv": round(sig_dict.get("churn_cv", 0.0), 2),
            "bus_factor": round(sig_dict.get("bus_factor", 1.0), 1),
            "cognitive_load": round(sig_dict.get("cognitive_load", 0.0), 1),
            "blast_radius": sig_dict.get("blast_radius_size", 0),
            "is_orphan": sig_dict.get("is_orphan", False),
            "finding_count": len(file_findings),
            "signals": {k: round(v, 4) if isinstance(v, float) else v for k, v in sig_dict.items()},
        }
        # Add trends if available
        if path in file_trends:
            file_data["trends"] = file_trends[path]
        files[path] = file_data

    # ── Module data ───────────────────────────────────────────────
    modules: dict[str, dict[str, Any]] = {}
    for mod_path, mod_dict in module_signals.items():
        modules[mod_path] = {
            "health_score": round(display_score(mod_dict.get("health_score", 0.5)), 1),
            "instability": mod_dict.get("instability"),
            "abstractness": round(mod_dict.get("abstractness", 0.0), 2),
            "file_count": mod_dict.get("file_count", 0),
            "velocity": round(mod_dict.get("velocity", 0.0), 2),
        }

    # ── Concern reports ───────────────────────────────────────────
    concern_reports = organize_by_concerns(findings, global_signals)
    concerns = [
        {
            "key": r.concern.key,
            "name": r.concern.name,
            "score": round(r.score, 1),
            "status": r.status,
            "finding_count": len(r.findings),
            "description": r.concern.description,
            "attributes": {
                k: round(v, 4) if isinstance(v, float) else v for k, v in r.attributes.items()
            },
            "file_count": r.file_count,
        }
        for r in concern_reports
    ]

    # ── Dependency edges & architecture data ──────────────────────
    dependency_edges = [[src, tgt] for src, tgt in (snapshot.dependency_edges or [])]
    delta_h = {k: round(v, 4) for k, v in (snapshot.delta_h or {}).items()}
    violations = snapshot.violations or []
    layers = snapshot.layers or []

    # ── History / trend data (optional) ───────────────────────────
    trends: dict[str, Any] | None = None
    if db_path:
        trends = _query_trends(db_path)

    # ── Assemble ──────────────────────────────────────────────────
    state: dict[str, Any] = {
        "health": health_display,
        "health_label": _health_label(health_display),
        "verdict": verdict_text,
        "verdict_color": _map_rich_color(verdict_color),
        "file_count": snapshot.file_count,
        "module_count": snapshot.module_count,
        "commits_analyzed": snapshot.commits_analyzed,
        "timestamp": snapshot.timestamp,
        "commit_sha": snapshot.commit_sha or "",
        "analyzed_path": snapshot.analyzed_path or "",
        "analyzers_ran": snapshot.analyzers_ran or [],
        "categories": categories,
        "focus": focus_data,
        "files": files,
        "modules": modules,
        "global_signals": {
            k: round(v, 4) if isinstance(v, float) else v for k, v in global_signals.items()
        },
        "concerns": concerns,
        "dependency_edges": dependency_edges,
        "delta_h": delta_h,
        "violations": violations,
        "layers": layers,
    }
    if trends:
        state["trends"] = trends
    return state


def _map_rich_color(color: str) -> str:
    """Map Rich color names to CSS color variables."""
    mapping = {
        "green": "var(--green)",
        "yellow": "var(--yellow)",
        "orange1": "var(--orange)",
        "red": "var(--red)",
    }
    return mapping.get(color, "var(--text)")


def _query_trends(db_path: str) -> dict[str, Any] | None:
    """Query .shannon/history.db for trend data. Returns None on failure."""
    path = Path(db_path)
    if not path.exists():
        return None

    trends: dict[str, Any] = {}
    try:
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        hq = HistoryQuery(conn)

        # Health trend
        try:
            health_points = hq.codebase_health(last_n=20)
            if health_points:
                trends["health"] = [
                    {
                        "timestamp": hp.timestamp,
                        "health": round(hp.metrics.get("codebase_health", 0.5), 4),
                        "finding_count": int(hp.metrics.get("active_findings", 0)),
                    }
                    for hp in health_points
                ]
        except Exception:
            logger.debug("Failed to query codebase health trend", exc_info=True)

        # Top movers
        try:
            movers = hq.top_movers(last_n=5, metric="risk_score")
            if movers:
                trends["movers"] = [
                    {
                        "path": m["filepath"],
                        "old_value": round(m["old_value"], 3),
                        "new_value": round(m["new_value"], 3),
                        "delta": round(m["delta"], 3),
                    }
                    for m in movers
                ]
        except Exception:
            logger.debug("Failed to query top movers", exc_info=True)

        # Chronic findings
        try:
            chronic = hq.persistent_findings(min_snapshots=3)
            if chronic:
                trends["chronic"] = [
                    {
                        "finding_type": c["finding_type"],
                        "identity_key": c["identity_key"],
                        "title": c["title"],
                        "files": c["files"],
                        "severity": round(c["severity"], 3),
                        "count": c["count"],
                    }
                    for c in chronic
                ]
        except Exception:
            logger.debug("Failed to query chronic findings", exc_info=True)

        conn.close()
    except Exception:
        logger.debug("Failed to open history DB", exc_info=True)
        return None

    return trends if trends else None
