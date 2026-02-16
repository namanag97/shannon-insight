"""Pattern and Finding models for Shannon Insight v2.

Patterns are declarative rules that detect findings in analyzed codebases.
Each pattern specifies what signals it needs, a predicate to check, and
metadata for severity/description/remediation.

Findings are the output of pattern matching -- they record what was found,
where, with what confidence, and include evidence for the user.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Union

from shannon_insight.infrastructure.entities import EntityId


class PatternScope(Enum):
    """The scope at which a pattern operates."""

    FILE = "file"
    FILE_PAIR = "file_pair"
    MODULE = "module"
    MODULE_PAIR = "module_pair"
    CODEBASE = "codebase"


@dataclass
class Pattern:
    """A declarative rule that detects a finding.

    Attributes:
        name:        Unique pattern identifier (e.g. "god_file").
        scope:       What kind of entity this pattern targets.
        requires:    Set of slot/signal names that must be available.
        predicate:   Callable (store, target) -> bool.
        severity:    Base severity in [0, 1].
        description: Human-readable explanation of what this detects.
        remediation: Suggested fix.
        category:    Pattern category (structural, coupling, architecture, team).
        phase:       Phase in which this pattern becomes available.
    """

    name: str
    scope: PatternScope
    requires: set[str]
    predicate: Callable[..., bool]
    severity: float
    description: str
    remediation: str
    category: str = ""
    phase: int = 0


@dataclass
class Finding:
    """A concrete finding produced by a pattern match.

    Attributes:
        pattern:     Name of the pattern that fired.
        scope:       Scope of the finding.
        target:      The entity (or pair of entities) involved.
        severity:    Severity in [0, 1].
        confidence:  Confidence in [0, 1].
        evidence:    Dictionary of evidence that triggered this finding.
        description: Human-readable description.
        remediation: Suggested fix.
    """

    pattern: str
    scope: PatternScope
    target: Union[EntityId, tuple[EntityId, EntityId]]
    severity: float
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    remediation: str = ""

    @property
    def id(self) -> str:
        """Stable identity key for tracking across snapshots.

        Format:
            FILE scope:        pattern:file_key
            FILE_PAIR scope:   pattern:sorted_key_a:sorted_key_b
            MODULE scope:      pattern:module_key
            MODULE_PAIR scope: pattern:sorted_key_a:sorted_key_b
            CODEBASE scope:    pattern:
        """
        if isinstance(self.target, tuple):
            keys = sorted([self.target[0].key, self.target[1].key])
            target_key = f"{keys[0]}:{keys[1]}"
        else:
            target_key = self.target.key
        return f"{self.pattern}:{target_key}"
