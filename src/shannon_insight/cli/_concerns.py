"""Concern-based organization for insights.

Organizes findings into human-understandable concerns (dimensions of health):
1. COMPLEXITY - Files that are hard to understand
2. COUPLING - Files that are too interconnected
3. ARCHITECTURE - Structural problems in the codebase
4. STABILITY - Files that keep changing
5. TEAM - Knowledge and collaboration risks
6. BROKEN - Code that doesn't work properly

Each concern has:
- A health metric (0-10)
- Contributing attributes (signals)
- Root causes (findings)

This is the 3-Question RCA pattern:
  Q1: What's the concern? (dimension + metric)
  Q2: What attributes contribute? (signals)
  Q3: What are the root causes? (findings)
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..insights.models import Finding


@dataclass
class Concern:
    """A dimension of codebase health."""

    key: str
    name: str
    icon: str
    description: str
    finding_types: frozenset[str]  # Finding types that map to this concern
    metric_keys: list[str]  # Global/composite signals for this concern


# The 6 concerns (dimensions of health)
CONCERNS = [
    Concern(
        key="complexity",
        name="Complexity",
        icon="🧠",
        description="Code that's hard to understand and maintain",
        finding_types=frozenset(
            {
                "god_file",
                "high_risk_hub",
            }
        ),
        metric_keys=["avg_cognitive_load", "max_nesting", "avg_function_count"],
    ),
    Concern(
        key="coupling",
        name="Coupling",
        icon="🔗",
        description="Files that are too interconnected",
        finding_types=frozenset(
            {
                "hidden_coupling",
                "accidental_coupling",
                "dead_dependency",
                "copy_paste_clone",
            }
        ),
        metric_keys=["wiring_score", "cycle_count", "coupling_density"],
    ),
    Concern(
        key="architecture",
        name="Architecture",
        icon="🏛️",
        description="Structural problems in the design",
        finding_types=frozenset(
            {
                "layer_violation",
                "zone_of_pain",
                "boundary_mismatch",
                "flat_architecture",
            }
        ),
        metric_keys=["architecture_health", "modularity", "layer_violation_count"],
    ),
    Concern(
        key="stability",
        name="Stability",
        icon="📈",
        description="Files that keep changing without stabilizing",
        finding_types=frozenset(
            {
                "unstable_file",
                "chronic_problem",
                "thrashing_code",
            }
        ),
        metric_keys=["avg_churn_cv", "churning_file_count", "fix_ratio"],
    ),
    Concern(
        key="team",
        name="Team Risk",
        icon="👥",
        description="Knowledge and collaboration issues",
        finding_types=frozenset(
            {
                "knowledge_silo",
                "review_blindspot",
                "truck_factor",
                "conway_violation",
            }
        ),
        metric_keys=["team_risk", "min_bus_factor", "author_entropy"],
    ),
    Concern(
        key="broken",
        name="Broken Code",
        icon="⛔",
        description="Code that doesn't work properly",
        finding_types=frozenset(
            {
                "phantom_imports",
                "orphan_code",
                "hollow_code",
                "incomplete_implementation",
            }
        ),
        metric_keys=["phantom_import_count", "orphan_count", "stub_ratio"],
    ),
]

# Build reverse mapping: finding_type -> concern
FINDING_TO_CONCERN: dict[str, Concern] = {}
for concern in CONCERNS:
    for ftype in concern.finding_types:
        FINDING_TO_CONCERN[ftype] = concern


@dataclass
class ConcernReport:
    """Analysis results organized by concern."""

    concern: Concern
    score: float  # 0-10 health score for this concern
    attributes: dict[str, float]  # metric_key -> value
    findings: list["Finding"] = field(default_factory=list)
    file_count: int = 0  # Number of files affected

    @property
    def status(self) -> str:
        if self.score >= 8:
            return "healthy"
        if self.score >= 6:
            return "moderate"
        if self.score >= 4:
            return "at_risk"
        return "critical"

    @property
    def color(self) -> str:
        if self.score >= 8:
            return "green"
        if self.score >= 6:
            return "yellow"
        if self.score >= 4:
            return "orange1"
        return "red"


def organize_by_concerns(
    findings: list["Finding"],
    global_signals: dict[str, float],
) -> list[ConcernReport]:
    """Organize findings into concern-based reports.

    Args:
        findings: List of findings from analysis
        global_signals: Global/composite signals from snapshot

    Returns:
        List of ConcernReports, sorted by score (worst first)
    """
    reports = []

    for concern in CONCERNS:
        # Collect findings for this concern
        concern_findings = [f for f in findings if f.finding_type in concern.finding_types]

        # Count affected files
        affected_files = set()
        for f in concern_findings:
            affected_files.update(f.files)

        # Extract attributes for this concern
        attributes = {}
        for key in concern.metric_keys:
            if key in global_signals:
                attributes[key] = global_signals[key]

        # Compute concern score (inverse of problem severity)
        # If we have specific metrics, use them; otherwise derive from findings
        score = _compute_concern_score(concern, attributes, concern_findings)

        reports.append(
            ConcernReport(
                concern=concern,
                score=score,
                attributes=attributes,
                findings=concern_findings,
                file_count=len(affected_files),
            )
        )

    # Sort by score (worst concerns first)
    reports.sort(key=lambda r: r.score)

    return reports


def _compute_concern_score(
    concern: Concern,
    attributes: dict[str, float],
    findings: list["Finding"],
) -> float:
    """Compute a 0-10 health score for a concern.

    Uses available metrics, falling back to finding-based heuristics.
    """
    # Use primary metric if available
    primary_metrics = {
        "complexity": "avg_cognitive_load",
        "coupling": "wiring_score",
        "architecture": "architecture_health",
        "stability": "avg_churn_cv",
        "team": "team_risk",
        "broken": "phantom_import_count",
    }

    primary_key = primary_metrics.get(concern.key)

    if primary_key and primary_key in attributes:
        raw = attributes[primary_key]

        # Normalize based on metric type
        if concern.key == "complexity":
            # Higher cognitive_load = worse (0-15 typical range)
            score = max(0, 10 - (raw / 1.5))
        elif concern.key == "coupling":
            # wiring_score is 0-1, higher = better
            score = raw * 10
        elif concern.key == "architecture":
            # architecture_health is 0-1, higher = better
            score = raw * 10
        elif concern.key == "stability":
            # Higher churn CV = worse (0-2 typical range)
            score = max(0, 10 - (raw * 5))
        elif concern.key == "team":
            # team_risk is 0-1, higher = worse
            score = (1 - raw) * 10
        elif concern.key == "broken":
            # Count-based: 0 is perfect, more is worse
            score = max(0, 10 - raw)
        else:
            score = 5.0  # Default if unknown

        return round(max(0, min(10, score)), 1)

    # Fallback: derive from finding count
    if not findings:
        return 10.0  # No issues = perfect

    # More findings = worse score
    # Weighted by severity
    total_severity = sum(f.severity for f in findings)
    avg_severity = total_severity / len(findings)

    # Scale: 0 findings = 10, 5+ high-severity = 0
    score = 10 - (len(findings) * avg_severity * 2)
    return round(max(0, min(10, score)), 1)


def get_concern_summary(reports: list[ConcernReport]) -> dict[str, int]:
    """Get a summary of concerns for display.

    Returns dict of concern_key -> finding_count for non-zero concerns.
    """
    return {r.concern.key: len(r.findings) for r in reports if r.findings}
