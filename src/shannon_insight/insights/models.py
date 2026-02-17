"""Data models for the insight engine."""

from dataclasses import dataclass, field
from typing import Optional


def compute_confidence(
    triggered_conditions: list[tuple[str, float, float, str]],
) -> float:
    """Compute confidence from triggered condition margins.

    Args:
        triggered_conditions: List of (signal_name, actual_value, threshold, polarity)
            polarity is "high_is_bad" or "high_is_good"

    Returns:
        Confidence in [0, 1], average of normalized margins across conditions.

    Example:
        >>> compute_confidence([("pagerank", 0.95, 0.90, "high_is_bad")])
        0.5  # margin = (0.95 - 0.90) / (1.0 - 0.90) = 0.5
    """
    if not triggered_conditions:
        return 0.0

    margins = []
    for _signal, actual, threshold, polarity in triggered_conditions:
        if polarity == "high_is_bad":
            # Higher value = worse. Margin = how much above threshold.
            # Handle edge case where threshold >= 1.0
            if threshold >= 1.0:
                margin = 0.0
            else:
                margin = (actual - threshold) / (1.0 - threshold)
        else:  # high_is_good
            # Lower value = worse. Margin = how much below threshold.
            # Handle edge case where threshold <= 0.0
            if threshold <= 0.0:
                margin = 0.0
            else:
                margin = (threshold - actual) / threshold
        margins.append(max(0.0, min(1.0, margin)))

    return sum(margins) / len(margins)


def compute_severity_from_percentiles(
    percentiles: dict[str, float],
    weights: dict[str, float],
    base_severity: float = 0.5,
    max_severity: float = 1.0,
) -> float:
    """Compute severity from weighted percentiles.

    Args:
        percentiles: Dict of signal_name -> percentile (0-100)
        weights: Dict of signal_name -> weight (should sum to 1.0)
        base_severity: Minimum severity floor
        max_severity: Maximum severity cap

    Returns:
        Severity in [base_severity, max_severity]
    """
    if not percentiles or not weights:
        return base_severity

    weighted_sum = 0.0
    total_weight = 0.0

    for signal, weight in weights.items():
        if signal in percentiles:
            # Convert 0-100 percentile to 0-1 for severity calculation
            weighted_sum += (percentiles[signal] / 100.0) * weight
            total_weight += weight

    if total_weight == 0:
        return base_severity

    normalized = weighted_sum / total_weight
    return base_severity + (max_severity - base_severity) * normalized


@dataclass
class Evidence:
    signal: str  # "pagerank", "blast_radius_pct", etc.
    value: float  # the raw value
    percentile: float  # 0-100, position in this codebase's distribution
    description: str  # "top 3% by PageRank"


@dataclass
class Finding:
    finding_type: str  # "high_risk_hub", "hidden_coupling", etc.
    severity: float  # 0.0 to 1.0
    title: str  # "analysis/engine.py is a high-risk hub"
    files: list[str]  # involved files
    evidence: list[Evidence]
    suggestion: str  # "Consider splitting this file..."
    confidence: float = 1.0  # 0.0-1.0, how sure we are (margin-based)
    effort: str = "MEDIUM"  # LOW | MEDIUM | HIGH
    scope: str = "FILE"  # FILE | FILE_PAIR | MODULE | MODULE_PAIR | CODEBASE


@dataclass
class StoreSummary:
    total_files: int = 0
    total_modules: int = 0
    commits_analyzed: int = 0
    git_available: bool = False
    fiedler_value: Optional[float] = None
    signals_available: list[str] = field(default_factory=list)


@dataclass
class InsightResult:
    findings: list[Finding]
    store_summary: StoreSummary
    diagnostic_report: object = None  # Optional DiagnosticReport
