"""Finder protocol and base classes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

from ..signals.models import FileSignals


@dataclass
class Evidence:
    signal: str
    value: float
    percentile: float
    description: str


@dataclass
class Finding:
    type: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    files: list[str]
    title: str
    description: str
    suggestion: str
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class Finder:
    name: str
    condition: Callable[[FileSignals], bool]
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    title_template: str
    description_template: str
    suggestion: str
    evidence_signals: list[str] = field(default_factory=list)
