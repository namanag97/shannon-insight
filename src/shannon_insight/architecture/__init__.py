"""Architecture analysis: module detection, Martin metrics, layer inference."""

from .analyzer import ArchitectureAnalyzer
from .models import Architecture, Layer, Module, Violation, ViolationType

__all__ = [
    "Architecture",
    "ArchitectureAnalyzer",
    "Layer",
    "Module",
    "Violation",
    "ViolationType",
]
