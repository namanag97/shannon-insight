"""All finders (10 of 22 implemented; 12 stubs left — see FRESH-BUILD.md refs).

The doc specifies 22 finders total. The catalog currently contains 10 canonical
ones. The remaining 12 are noted as TODO stubs at the bottom of this file.
"""
from __future__ import annotations

from .base import Finder, Finding, Evidence
from ..signals.models import FileSignals


# ── Implemented finders ──────────────────────────────────────────────────────

FINDERS = [
    Finder(
        name="HIGH_RISK_HUB",
        condition=lambda s: (
            s.percentiles.get("pagerank", 0) > 0.85
            and s.percentiles.get("blast_radius_size", 0) > 0.75
        ),
        severity="CRITICAL",
        title_template="{path} is a high-risk hub",
        description_template="Central file with large blast radius ({blast_radius_size} files affected)",
        suggestion="Consider extracting interfaces or splitting responsibilities",
        evidence_signals=["pagerank", "blast_radius_size"],
    ),

    Finder(
        name="GOD_FILE",
        condition=lambda s: (
            s.lines > 500
            and (s.percentiles.get("complexity", 0) > 0.90 or s.in_degree > 10)
        ),
        severity="HIGH",
        title_template="{path} is a god file",
        description_template="Large file ({lines} lines) with high complexity or many dependents",
        suggestion="Split into smaller, focused modules",
        evidence_signals=["lines", "complexity", "in_degree"],
    ),

    Finder(
        name="HIDDEN_COUPLING",
        condition=lambda s: s.hidden_coupling_count >= 2,
        severity="MEDIUM",
        title_template="{path} has hidden coupling",
        description_template="Co-changes with {hidden_coupling_count} files without explicit imports",
        suggestion="Make coupling explicit via imports or extract shared dependency",
        evidence_signals=["hidden_coupling_count"],
    ),

    Finder(
        name="ORPHAN_CODE",
        condition=lambda s: s.is_orphan and s.depth != 0,  # Not entry point
        severity="LOW",
        title_template="{path} is orphaned",
        description_template="No other files import this file",
        suggestion="Verify this code is still needed, or add proper imports",
        evidence_signals=["is_orphan", "in_degree"],
    ),

    Finder(
        name="UNSTABLE_FILE",
        condition=lambda s: s.churn_cv > 1.0 and s.total_changes > 10,
        severity="MEDIUM",
        title_template="{path} is unstable",
        description_template="High churn volatility (CV={churn_cv:.2f}) with {total_changes} changes",
        suggestion="Stabilize interfaces or add tests to prevent regressions",
        evidence_signals=["churn_cv", "total_changes"],
    ),

    Finder(
        name="CYCLE_MEMBER",
        condition=lambda s: s.cycle_member,
        severity="HIGH",
        title_template="{path} is in a dependency cycle",
        description_template="Part of a circular dependency chain",
        suggestion="Break cycle by extracting shared interface or inverting dependency",
        evidence_signals=["cycle_member"],
    ),

    Finder(
        name="BUS_FACTOR_RISK",
        condition=lambda s: (
            s.bus_factor < 2
            and s.percentiles.get("pagerank", 0) > 0.75
        ),
        severity="HIGH",
        title_template="{path} has bus factor risk",
        description_template="Important file ({pagerank:.3f} PageRank) maintained by <2 people",
        suggestion="Spread knowledge through pair programming or documentation",
        evidence_signals=["bus_factor", "pagerank"],
    ),

    Finder(
        name="HOLLOW_CODE",
        condition=lambda s: s.stub_ratio > 0.5 and s.function_count > 3,
        severity="LOW",
        title_template="{path} has hollow code",
        description_template="{stub_ratio:.0%} of functions are stubs",
        suggestion="Implement or remove placeholder code",
        evidence_signals=["stub_ratio", "function_count"],
    ),

    Finder(
        name="VOLATILE_CORE",
        condition=lambda s: (
            s.percentiles.get("pagerank", 0) > 0.75
            and s.churn_cv > 0.8
        ),
        severity="HIGH",
        title_template="{path} is a volatile core module",
        description_template="Central file with high change volatility",
        suggestion="Stabilize core module or reduce its responsibilities",
        evidence_signals=["pagerank", "churn_cv"],
    ),

    Finder(
        name="COMPLEX_HOTSPOT",
        condition=lambda s: (
            s.percentiles.get("complexity", 0) > 0.80
            and s.total_changes > 20
        ),
        severity="MEDIUM",
        title_template="{path} is a complex hotspot",
        description_template="Frequently changed ({total_changes}x) complex code",
        suggestion="Refactor to reduce complexity before next change",
        evidence_signals=["complexity", "total_changes"],
    ),

    # TODO: 12 more finders to reach the documented 22 total.
    # See docs/v2/registry/finders.md for full specifications:
    #   CONWAY_VIOLATION, PHANTOM_IMPORT, DEEP_MODULE, NARROW_INTERFACE,
    #   SEMANTIC_DRIFT, AUTHORITY_CONFLICT, TEMPORAL_DECAY, TANGLED_COMMIT,
    #   OVER_ABSTRACTED, ENTRY_POINT_RISK, KNOWLEDGE_SILO, CHURN_ACCELERATING
]


def run_finders(file_signals: dict[str, FileSignals]) -> list[Finding]:
    """Run all finders on signals and return findings."""
    findings = []

    for path, fs in file_signals.items():
        for finder in FINDERS:
            try:
                if finder.condition(fs):
                    evidence = []
                    for sig in finder.evidence_signals:
                        val = getattr(fs, sig, 0)
                        pctl = fs.percentiles.get(sig, 0)
                        evidence.append(Evidence(
                            signal=sig,
                            value=float(val) if not isinstance(val, bool) else float(int(val)),
                            percentile=pctl,
                            description=f"{sig}={val}",
                        ))

                    findings.append(Finding(
                        type=finder.name,
                        severity=finder.severity,
                        files=[path],
                        title=finder.title_template.format(path=path, **vars(fs)),
                        description=finder.description_template.format(**vars(fs)),
                        suggestion=finder.suggestion,
                        evidence=evidence,
                    ))
            except Exception:
                continue  # Skip on errors

    return findings
