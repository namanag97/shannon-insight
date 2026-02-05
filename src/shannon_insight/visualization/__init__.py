"""Visualization layer — HTML report generation with interactive treemap."""

from .report import generate_report
from .treemap import build_treemap_data

__all__ = [
    "generate_report",
    "build_treemap_data",
]
