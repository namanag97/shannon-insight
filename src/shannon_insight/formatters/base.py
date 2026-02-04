"""Base formatter interface for Shannon Insight output rendering."""

from abc import ABC, abstractmethod
from typing import List

from ..models import AnomalyReport, AnalysisContext


class BaseFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def render(self, reports: List[AnomalyReport], context: AnalysisContext) -> None:
        """Render reports to stderr/stdout as appropriate."""

    @abstractmethod
    def format(self, reports: List[AnomalyReport], context: AnalysisContext) -> str:
        """Return formatted string representation of reports."""
