"""Build the JSON dashboard state from analysis results."""

from __future__ import annotations

import html
from typing import Any

from ..cli._common import display_score
from ..cli._concerns import organize_by_concerns
from ..cli._finding_display import get_display_config, get_severity_display
from ..cli._focus import identify_focus_point
from ..insights.models import Finding, InsightResult
from ..persistence.models import TensorSnapshot

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
        "files": [html.escape(p) for p in f.files],
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
) -> dict[str, Any]:
    """Convert analysis results to the full dashboard JSON state.

    This is the single source of truth for ``GET /api/state`` and
    the WebSocket ``complete`` message.
    """
    findings = result.findings
    file_signals = snapshot.file_signals or {}
    global_signals = snapshot.global_signals or {}
    module_signals = snapshot.module_signals or {}

    # ── Health score ──────────────────────────────────────────────
    raw_health = global_signals.get("codebase_health", 0.5)
    health_display = display_score(raw_health)

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
    focus, alternatives = identify_focus_point(snapshot, findings, n_alternatives=5)
    if focus:
        focus_data = {
            "path": html.escape(focus.path),
            "actionability": round(focus.actionability, 3),
            "why": focus.why_summary(),
            "findings": [_finding_to_dict(f) for f in focus.findings],
            "alternatives": [
                {
                    "path": html.escape(a.path),
                    "actionability": round(a.actionability, 3),
                    "why": a.why_summary(),
                }
                for a in alternatives
            ],
        }

    # ── File data ─────────────────────────────────────────────────
    files: dict[str, dict[str, Any]] = {}
    for path, sig_dict in file_signals.items():
        # Collect findings for this file
        file_findings = [f for f in findings if path in f.files]
        files[html.escape(path)] = {
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

    # ── Module data ───────────────────────────────────────────────
    modules: dict[str, dict[str, Any]] = {}
    for mod_path, mod_dict in module_signals.items():
        modules[html.escape(mod_path)] = {
            "health_score": round(display_score(mod_dict.get("health_score", 0.5)), 1),
            "instability": mod_dict.get("instability"),
            "abstractness": round(mod_dict.get("abstractness", 0.0), 2),
            "file_count": mod_dict.get("file_count", 0),
            "velocity": round(mod_dict.get("velocity", 0.0), 2),
        }

    # ── Concern reports (for trends screen) ───────────────────────
    concern_reports = organize_by_concerns(findings, global_signals)
    concerns = [
        {
            "key": r.concern.key,
            "name": r.concern.name,
            "score": round(r.score, 1),
            "status": r.status,
            "finding_count": len(r.findings),
        }
        for r in concern_reports
    ]

    # ── Assemble ──────────────────────────────────────────────────
    return {
        "health": health_display,
        "health_label": _health_label(health_display),
        "file_count": snapshot.file_count,
        "module_count": snapshot.module_count,
        "commits_analyzed": snapshot.commits_analyzed,
        "timestamp": snapshot.timestamp,
        "commit_sha": snapshot.commit_sha or "",
        "categories": categories,
        "focus": focus_data,
        "files": files,
        "modules": modules,
        "global_signals": {
            k: round(v, 4) if isinstance(v, float) else v for k, v in global_signals.items()
        },
        "concerns": concerns,
    }
