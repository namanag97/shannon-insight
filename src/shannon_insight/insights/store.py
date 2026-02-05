"""AnalysisStore — the blackboard that all analyzers write to and finders read from."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ..analysis.models import CodebaseAnalysis
from ..models import FileMetrics
from ..temporal.models import ChurnSeries, CoChangeMatrix, GitHistory, SpectralSummary


@dataclass
class AnalysisStore:
    # Inputs (set by kernel before analyzers run)
    root_dir: str = ""
    file_metrics: List[FileMetrics] = field(default_factory=list)

    # Structural signals (set by StructuralAnalyzer)
    structural: Optional[CodebaseAnalysis] = None

    # Temporal signals (set by TemporalAnalyzer)
    git_history: Optional[GitHistory] = None
    cochange: Optional[CoChangeMatrix] = None
    churn: Optional[Dict[str, ChurnSeries]] = None

    # Per-file signals (set by PerFileAnalyzer)
    file_signals: Optional[Dict[str, Dict[str, float]]] = None

    # Spectral signals (set by SpectralAnalyzer)
    spectral: Optional[SpectralSummary] = None

    @property
    def available(self) -> Set[str]:
        """Track what signal categories have been populated."""
        avail: Set[str] = {"files"}
        if self.structural:
            avail.add("structural")
        if self.cochange or self.churn:
            avail.add("temporal")
        if self.file_signals:
            avail.add("file_signals")
        if self.spectral:
            avail.add("spectral")
        return avail
