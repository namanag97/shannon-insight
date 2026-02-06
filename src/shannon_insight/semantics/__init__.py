"""Semantic analysis package (Phase 2 IR2 layer).

Provides file role classification, concept extraction, naming drift detection,
and documentation completeness metrics.

Usage:
    from shannon_insight.semantics import SemanticAnalyzer, FileSemantics, Role

    analyzer = SemanticAnalyzer()
    analyzer.analyze(store)  # Populates store.semantics and store.roles
"""

from .analyzer import SemanticAnalyzer
from .completeness import compute_completeness, count_todos
from .concepts import ConceptExtractor, extract_identifiers
from .models import (
    GENERIC_FILENAMES,
    Completeness,
    Concept,
    FileSemantics,
    Role,
)
from .naming import compute_naming_drift, cosine_similarity
from .roles import classify_role

__all__ = [
    # Main analyzer
    "SemanticAnalyzer",
    # Models
    "Completeness",
    "Concept",
    "FileSemantics",
    "GENERIC_FILENAMES",
    "Role",
    # Functions
    "classify_role",
    "compute_completeness",
    "compute_naming_drift",
    "cosine_similarity",
    "count_todos",
    "extract_identifiers",
    "ConceptExtractor",
]
