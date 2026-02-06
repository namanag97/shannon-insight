"""Data models for temporal (git-based) analysis."""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass
class Commit:
    hash: str
    timestamp: int  # unix seconds
    author: str
    files: List[str]  # relative paths changed
    subject: str = ""  # Phase 3: commit message subject for fix_ratio/refactor_ratio


@dataclass
class GitHistory:
    commits: List[Commit]  # newest first
    file_set: Set[str]  # all files ever seen
    span_days: int  # time range covered

    @property
    def total_commits(self) -> int:
        return len(self.commits)


@dataclass
class CoChangePair:
    file_a: str
    file_b: str
    cochange_count: int  # times in same commit
    total_a: int  # times file_a changed
    total_b: int  # times file_b changed
    confidence_a_b: float  # P(B | A changed)
    confidence_b_a: float  # P(A | B changed)
    lift: float  # observed / expected


@dataclass
class CoChangeMatrix:
    pairs: Dict[Tuple[str, str], CoChangePair]  # sparse, only non-zero
    total_commits: int
    file_change_counts: Dict[str, int]


@dataclass
class ChurnSeries:
    file_path: str
    window_counts: List[int]  # changes per time window
    total_changes: int
    trajectory: str  # "stabilizing"|"churning"|"spiking"|"dormant"
    slope: float  # linear regression slope

    # Phase 3 additions:
    cv: float = 0.0  # Coefficient of variation (was computed but discarded)
    bus_factor: float = 1.0  # 2^H where H = Shannon entropy of author distribution
    author_entropy: float = 0.0  # Shannon entropy of per-file author commit distribution
    fix_ratio: float = 0.0  # fraction of commits with fix keywords in subject
    refactor_ratio: float = 0.0  # fraction of commits with refactor keywords in subject


@dataclass
class SpectralSummary:
    fiedler_value: float  # algebraic connectivity
    num_components: int
    eigenvalues: List[float]  # sorted ascending
    spectral_gap: float  # ratio of 2nd to 3rd eigenvalue
