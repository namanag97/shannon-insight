"""AnalysisResult for the FRESH-BUILD kernel.

Named fresh_result.py to avoid conflict with the existing kernel/result.py
(which contains RuntimeResult used by the production kernel).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from ..finders.base import Finding
from ..signals.models import FileSignals, GlobalSignals


@dataclass
class AnalysisResult:
    """Complete result of a FRESH-BUILD analysis run."""

    # Core outputs
    file_signals: dict[str, FileSignals] = field(default_factory=dict)
    global_signals: Optional[GlobalSignals] = None
    findings: list[Finding] = field(default_factory=list)

    # Metadata
    duration_seconds: float = 0.0
    file_count: int = 0
    commit_count: int = 0
    error_count: int = 0

    # Status
    success: bool = True
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "success": self.success,
            "duration_seconds": self.duration_seconds,
            "file_count": self.file_count,
            "commit_count": self.commit_count,
            "finding_count": len(self.findings),
            "findings": [
                {
                    "type": f.type,
                    "severity": f.severity,
                    "files": f.files,
                    "title": f.title,
                    "description": f.description,
                    "suggestion": f.suggestion,
                }
                for f in self.findings
            ],
            "global_signals": {
                "codebase_health": self.global_signals.codebase_health
                if self.global_signals
                else 0,
                "modularity": self.global_signals.modularity if self.global_signals else 0,
                "cycle_count": self.global_signals.cycle_count if self.global_signals else 0,
            },
            "errors": self.errors,
        }
