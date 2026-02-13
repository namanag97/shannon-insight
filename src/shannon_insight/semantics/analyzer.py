"""SemanticAnalyzer - orchestrates Phase 2 semantic analysis.

Produces FileSemantics for each file in the codebase:
- Role classification
- Concept extraction (3-tier)
- Naming drift detection
- Completeness metrics

Writes to store.semantics and store.roles slots.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .completeness import compute_completeness
from .concepts import ConceptExtractor
from .models import FileSemantics
from .naming import compute_naming_drift
from .roles import classify_role

if TYPE_CHECKING:
    from ..insights.store_v2 import AnalysisStore
    from ..scanning.models_v2 import FileSyntax

logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """Analyzer that produces semantic information for all files.

    Implements the Analyzer protocol:
    - name: str
    - requires: set[str]
    - provides: set[str]
    - analyze(store) -> None

    Two-pass architecture:
    1. Build corpus-wide IDF for concept extraction
    2. Compute per-file semantics
    """

    name = "semantic"
    requires = frozenset({"file_syntax"})
    provides = frozenset({"semantics", "roles"})

    def analyze(self, store: AnalysisStore) -> None:
        """Run semantic analysis on all files.

        Args:
            store: AnalysisStore with file_syntax populated
        """
        if not store.file_syntax.available:
            logger.warning("SemanticAnalyzer: file_syntax not available, skipping")
            store.semantics.set_error("file_syntax not available", self.name)
            store.roles.set_error("file_syntax not available", self.name)
            return

        file_syntax: dict[str, FileSyntax] = store.file_syntax.value
        if not file_syntax:
            logger.debug("SemanticAnalyzer: no files to analyze")
            store.semantics.set({}, self.name)
            store.roles.set({}, self.name)
            return

        # Get file contents from cache or disk
        file_contents: dict[str, str] = {}
        for path in file_syntax:
            content = store.get_content(path)
            file_contents[path] = content if content is not None else ""

        # Pass 1: Build corpus IDF
        logger.debug(f"SemanticAnalyzer: Pass 1 - building IDF for {len(file_syntax)} files")
        extractor = ConceptExtractor()
        for syntax in file_syntax.values():
            extractor.add_file(syntax)
        extractor.compute_idf()

        # Pass 2: Compute per-file semantics
        logger.debug("SemanticAnalyzer: Pass 2 - computing semantics")
        semantics: dict[str, FileSemantics] = {}
        roles: dict[str, str] = {}

        for path, syntax in file_syntax.items():
            file_semantics = self._analyze_file(
                syntax,
                file_contents.get(path, ""),
                extractor,
                store.root_dir,
            )
            semantics[path] = file_semantics
            roles[path] = file_semantics.role.value

        # Write to store
        store.semantics.set(semantics, self.name)
        store.roles.set(roles, self.name)

        logger.info(
            f"SemanticAnalyzer: analyzed {len(semantics)} files, "
            f"roles: {self._summarize_roles(roles)}"
        )

    def _analyze_file(
        self,
        syntax: FileSyntax,
        content: str,
        extractor: ConceptExtractor,
        root_dir: str = "",
    ) -> FileSemantics:
        """Analyze a single file.

        Args:
            syntax: FileSyntax for the file
            content: Raw file content
            extractor: ConceptExtractor with IDF computed
            root_dir: Project root directory

        Returns:
            FileSemantics for the file
        """
        # 1. Classify role
        role = classify_role(syntax, root_dir)

        # 2. Extract concepts
        concepts, concept_entropy, tier = extractor.extract(syntax, role)

        # 3. Compute import fingerprint
        import_fingerprint = extractor.compute_import_fingerprint(syntax.path)

        # 4. Compute naming drift
        naming_drift = compute_naming_drift(syntax.path, concepts, tier)

        # 5. Compute completeness
        completeness = compute_completeness(syntax, content)

        return FileSemantics(
            path=syntax.path,
            role=role,
            concepts=concepts,
            concept_count=len(concepts),
            concept_entropy=concept_entropy,
            naming_drift=naming_drift,
            completeness=completeness,
            tier=tier,
            import_fingerprint=import_fingerprint,
        )

    def _summarize_roles(self, roles: dict[str, str]) -> str:
        """Summarize role distribution for logging."""
        from collections import Counter

        counter = Counter(roles.values())
        parts = [f"{role}={count}" for role, count in counter.most_common(5)]
        return ", ".join(parts)
