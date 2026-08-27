"""RELATE seam contracts (Phase 2).

Four seams, per ARCHITECTURE-V4 §Phase-B:
  ① ModuleIndex   — lookup substrate (pass-1 totality precondition)
  ② StrategyTable — declarative per-family semantics (languages as DATA)
  ③ BindingTable  — THE published artifact; everything else projects from it
  ④ PairFacts     — evidence-bearing set-algebra facts (severity lives LATER)

Verdict taxonomy is closed: RESOLVED | EXTERNAL | PHANTOM | SKIPPED.
No other verdict may ever exist (guards enforce at construction).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    RESOLVED = "RESOLVED"
    EXTERNAL = "EXTERNAL"
    PHANTOM = "PHANTOM"
    SKIPPED = "SKIPPED"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class BindMethod(str, Enum):
    EXACT_FILE = "EXACT_FILE"            # specifier mapped 1:1 onto indexed file
    INDEX_PACKAGE = "INDEX_PACKAGE"      # dir import → __init__/index/mod file
    ANCESTOR_WALK = "ANCESTOR_WALK"      # search-root iteration won
    PREFIX_STRIP = "PREFIX_STRIP"        # progressive prefix stripping won
    ALIAS_MAP = "ALIAS_MAP"              # tsconfig paths / package exports
    WORKSPACE_PKG = "WORKSPACE_PKG"      # monorepo workspace member name
    GO_PACKAGE_DIR = "GO_PACKAGE_DIR"    # import binds every file of a package dir
    JAVA_WILDCARD_DIR = "JAVA_WILDCARD_DIR"
    CASE_FOLD = "CASE_FOLD"              # case-insensitive rescue (portability smell)
    REEXPORT_HOP = "REEXPORT_HOP"        # barrel file passthrough (1 hop max)
    NONCODE_ASSET = "NONCODE_ASSET"      # bound to a known non-language file


#: ladder position — lower is stronger; consumers gate on this integer rank
METHOD_RANK: dict[str, int] = {
    BindMethod.ALIAS_MAP.value: 0,
    BindMethod.EXACT_FILE.value: 1,
    BindMethod.INDEX_PACKAGE.value: 2,
    BindMethod.WORKSPACE_PKG.value: 3,
    BindMethod.REEXPORT_HOP.value: 4,
    BindMethod.GO_PACKAGE_DIR.value: 4,
    BindMethod.JAVA_WILDCARD_DIR.value: 4,
    BindMethod.ANCESTOR_WALK.value: 5,
    BindMethod.PREFIX_STRIP.value: 6,
    BindMethod.NONCODE_ASSET.value: 6,
    BindMethod.CASE_FOLD.value: 9,
}


@dataclass(frozen=True)
class Candidate:
    rel_path: str
    method: BindMethod
    rank: int


@dataclass(frozen=True)
class BindingRecord:
    """Seam③ unit. One row per (source, specifier-site). Immutable."""

    source_rel: str
    specifier: str
    line: int
    language: str
    is_dynamic: bool = False

    verdict: Verdict = Verdict.PHANTOM
    target_rel: str | None = None
    target_file_id: str | None = None  # stamped at projection time
    method: BindMethod | None = None
    confidence: Confidence | None = None
    ambiguous_with: tuple[str, ...] = ()
    reason: str | None = None  # EXTERNAL name / PHANTOM cause / SKIP cause

    @property
    def key(self) -> tuple:
        return (self.source_rel, self.line, self.specifier)


@dataclass(frozen=True)
class EdgeRecord:
    src_file_id: str
    dst_file_id: str
    confidence: Confidence
    method: BindMethod


@dataclass(frozen=True)
class PhantomFact:
    source_rel: str
    specifier: str
    line: int
    reason: str


@dataclass(frozen=True)
class ExternalPkg:
    ecosystem: str
    name: str
    import_count: int


@dataclass
class RelateMetrics:
    total_specifiers: int = 0
    resolved: int = 0
    external: int = 0
    phantom: int = 0
    skipped: int = 0
    ambiguous: int = 0
    case_fold_rescues: int = 0
    untracked_endpoints: int = 0
    edges_emitted: int = 0

    @property
    def internal_attempts(self) -> int:
        return self.resolved + self.phantom

    @property
    def resolution_rate(self) -> float:
        return round(self.resolved / self.internal_attempts, 4) if self.internal_attempts else 1.0

    def summary(self) -> dict[str, object]:
        return {
            "specifiers": self.total_specifiers,
            "resolved": self.resolved,
            "external": self.external,
            "phantom": self.phantom,
            "skipped": self.skipped,
            "ambiguous": self.ambiguous,
            "case_fold_rescues": self.case_fold_rescues,
            "untracked_endpoints": self.untracked_endpoints,
            "edges": self.edges_emitted,
            "resolution_rate": self.resolution_rate,
        }


__all__ = [
    "BindMethod",
    "BindingRecord",
    "Candidate",
    "Confidence",
    "EdgeRecord",
    "ExternalPkg",
    "METHOD_RANK",
    "PhantomFact",
    "RelateMetrics",
    "Verdict",
]
