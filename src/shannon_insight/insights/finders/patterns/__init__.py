"""Pattern definitions organized by category.

Mirrors the canonical v2 architecture docs structure:
- existing.py: 7 v1 patterns upgraded
- ai_quality.py: 6 AI code quality patterns
- social_team.py: 3 social/team patterns
- architecture.py: 3 architecture patterns
- cross_dimensional.py: 3 cross-dimensional patterns
"""

from .ai_quality import COPY_PASTE_CLONE, FLAT_ARCHITECTURE, HOLLOW_CODE, NAMING_DRIFT, ORPHAN_CODE, PHANTOM_IMPORTS
from .architecture import ARCHITECTURE_EROSION, LAYER_VIOLATION, ZONE_OF_PAIN
from .cross_dimensional import ACCIDENTAL_COUPLING, BUG_ATTRACTOR, WEAK_LINK
from .existing import (
    BOUNDARY_MISMATCH,
    CHRONIC_PROBLEM,
    DEAD_DEPENDENCY,
    GOD_FILE,
    HIDDEN_COUPLING,
    HIGH_RISK_HUB,
    UNSTABLE_FILE,
)
from .social_team import CONWAY_VIOLATION, KNOWLEDGE_SILO, REVIEW_BLINDSPOT

__all__ = [
    # Existing (7)
    "HIGH_RISK_HUB",
    "HIDDEN_COUPLING",
    "GOD_FILE",
    "UNSTABLE_FILE",
    "BOUNDARY_MISMATCH",
    "DEAD_DEPENDENCY",
    "CHRONIC_PROBLEM",
    # AI Quality (6)
    "ORPHAN_CODE",
    "HOLLOW_CODE",
    "PHANTOM_IMPORTS",
    "COPY_PASTE_CLONE",
    "FLAT_ARCHITECTURE",
    "NAMING_DRIFT",
    # Social/Team (3)
    "KNOWLEDGE_SILO",
    "CONWAY_VIOLATION",
    "REVIEW_BLINDSPOT",
    # Architecture (3)
    "LAYER_VIOLATION",
    "ZONE_OF_PAIN",
    "ARCHITECTURE_EROSION",
    # Cross-Dimensional (3)
    "WEAK_LINK",
    "BUG_ATTRACTOR",
    "ACCIDENTAL_COUPLING",
]
