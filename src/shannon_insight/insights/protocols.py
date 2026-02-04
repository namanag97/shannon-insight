"""Protocol classes for Analyzer and Finder plugins."""

from typing import List, Protocol, Set

from .models import Finding
from .store import AnalysisStore


class Analyzer(Protocol):
    """Analyzers read from the store, compute, and write results back."""

    name: str
    requires: Set[str]  # what must be in store.available
    provides: Set[str]  # what this adds to store.available

    def analyze(self, store: AnalysisStore) -> None: ...


class Finder(Protocol):
    """Finders read from the store (NEVER write) and return findings."""

    name: str
    requires: Set[str]  # what must be in store.available

    def find(self, store: AnalysisStore) -> List[Finding]: ...
