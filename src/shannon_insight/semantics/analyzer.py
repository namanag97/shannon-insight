"""SemanticAnalyzer - orchestrates Phase 2 semantic analysis.

Produces FileSemantics for each file in the codebase:
- Role classification
- Concept extraction (3-tier)
- Naming drift detection
- Completeness metrics

Writes to store.semantics and store.roles slots.
Also writes semantic signals to FactStore.
"""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

from ..infrastructure.entities import EntityId, EntityType
from ..infrastructure.relations import Relation, RelationType
from ..infrastructure.signals import Signal
from .completeness import compute_completeness
from .concepts import ConceptExtractor
from .models import FileSemantics
from .naming import compute_naming_drift
from .roles import classify_role

if TYPE_CHECKING:
    from ..insights.store import AnalysisStore
    from ..scanning.syntax import FileSyntax

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

        # Sync semantic signals to FactStore
        self._sync_to_fact_store(store, semantics)

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

    def _sync_to_fact_store(
        self, store: AnalysisStore, semantics: dict[str, FileSemantics]
    ) -> None:
        """Sync semantic analysis results to FactStore.

        Writes per-file semantic signals (CONCEPT_COUNT, CONCEPT_ENTROPY,
        NAMING_DRIFT, TODO_DENSITY, DOCSTRING_COVERAGE, ROLE) and
        SIMILAR_TO relations between semantically similar files.
        """
        if not hasattr(store, "fact_store"):
            return

        fs = store.fact_store

        # Per-file semantic signals
        for path, sem in semantics.items():
            entity_id = EntityId(EntityType.FILE, path)
            fs.set_signal(entity_id, Signal.CONCEPT_COUNT, sem.concept_count)
            fs.set_signal(entity_id, Signal.CONCEPT_ENTROPY, sem.concept_entropy)
            fs.set_signal(entity_id, Signal.NAMING_DRIFT, sem.naming_drift)
            fs.set_signal(entity_id, Signal.TODO_DENSITY, sem.todo_density)
            fs.set_signal(entity_id, Signal.DOCSTRING_COVERAGE, sem.docstring_coverage)
            fs.set_signal(entity_id, Signal.ROLE, sem.role.value)

        # SIMILAR_TO relations based on import fingerprint similarity
        self._compute_similarity_relations(store, semantics)

        logger.debug(f"FactStore sync: {len(semantics)} files with semantic signals")

    def _compute_similarity_relations(
        self, store: AnalysisStore, semantics: dict[str, FileSemantics]
    ) -> None:
        """Compute SIMILAR_TO relations between semantically similar files.

        Uses import fingerprint cosine similarity. Only creates relations
        for pairs with similarity >= 0.5.
        """
        fs = store.fact_store
        paths = list(semantics.keys())

        # Minimum similarity threshold for creating a relation
        MIN_SIMILARITY = 0.5

        # Compare all pairs (only compute once per pair)
        for i, path_a in enumerate(paths):
            sem_a = semantics[path_a]
            if not sem_a.import_fingerprint:
                continue

            for path_b in paths[i + 1 :]:
                sem_b = semantics[path_b]
                if not sem_b.import_fingerprint:
                    continue

                # Compute cosine similarity between import fingerprints
                similarity = self._fingerprint_similarity(
                    sem_a.import_fingerprint, sem_b.import_fingerprint
                )

                if similarity >= MIN_SIMILARITY:
                    file_a = EntityId(EntityType.FILE, path_a)
                    file_b = EntityId(EntityType.FILE, path_b)

                    # SIMILAR_TO is symmetric, but we only add it in one direction
                    # to avoid duplicates
                    fs.add_relation(
                        Relation(
                            type=RelationType.SIMILAR_TO,
                            source=file_a,
                            target=file_b,
                            weight=similarity,
                        )
                    )

    def _fingerprint_similarity(self, fp_a: dict[str, float], fp_b: dict[str, float]) -> float:
        """Compute cosine similarity between two import fingerprints.

        Args:
            fp_a: First import fingerprint (module -> weight)
            fp_b: Second import fingerprint (module -> weight)

        Returns:
            Cosine similarity [0, 1]
        """
        if not fp_a or not fp_b:
            return 0.0

        # Get all unique modules
        all_modules = set(fp_a.keys()) | set(fp_b.keys())

        # Compute dot product and magnitudes
        dot_product = 0.0
        mag_a = 0.0
        mag_b = 0.0

        for module in all_modules:
            a_val = fp_a.get(module, 0.0)
            b_val = fp_b.get(module, 0.0)
            dot_product += a_val * b_val
            mag_a += a_val * a_val
            mag_b += b_val * b_val

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot_product / (math.sqrt(mag_a) * math.sqrt(mag_b))
