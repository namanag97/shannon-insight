"""Protocol classes for Analyzer and Finder plugins."""

from typing import Protocol

from .models import Finding
from .store import AnalysisStore


class Analyzer(Protocol):
    """Analyzers read from the store, compute, and write results back."""

    name: str
    requires: set[str]  # what must be in store.available
    provides: set[str]  # what this adds to store.available

    def analyze(self, store: AnalysisStore) -> None: ...


class Finder(Protocol):
    """Finders read from the store (NEVER write) and return findings."""

    name: str
    requires: set[str]  # what must be in store.available

    def find(self, store: AnalysisStore) -> list[Finding]: ...
