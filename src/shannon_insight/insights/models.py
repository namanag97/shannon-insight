"""Data models for the insight engine."""

from dataclasses import dataclass, field
from typing import Optional


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
