"""TensorBuildExecutor — Build the 4D RelationTensor from store data.

This phase constructs a RelationTensor with layers:
- IMPORT: from file_syntax import declarations
- COCHANGE: from git_history co-change patterns
- AUTHOR: from git_history author overlap (Jaccard)
- SEMANTIC: from TF-IDF concept vectors (if available)
- CLONE: from NCD clone detection (if clone_pairs available)
- COMBINED: weighted sum of all available layers

Populates:
- store.tensor: RelationTensor

Graceful degradation:
- If git_history unavailable: skip COCHANGE and AUTHOR layers
- If semantics unavailable: skip SEMANTIC layer
- If clone_pairs unavailable: skip CLONE layer
- Always populate IMPORT (only needs file_syntax)
- Always populate COMBINED (works with whatever layers exist)
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

from ...infrastructure.runtime import Phase
from ...logging_config import get_logger
from ..executor import BaseExecutor
from ..result import PhaseResult

if TYPE_CHECKING:
    from ...infrastructure.runtime import RuntimeContext
    from ...insights.store import AnalysisStore
    from ...session import AnalysisSession

logger = get_logger(__name__)


class TensorBuildExecutor(BaseExecutor):
    """Build the 4D RelationTensor from extracted data.

    Reads file_syntax, git_history, and semantics from the store,
    populates tensor layers, and stores the result.
    """

    phase = Phase.TENSOR_BUILD
    timeout_seconds = 180  # 3 minutes
    name = "tensor_build"

    def _execute(
        self,
        ctx: RuntimeContext,
        store: AnalysisStore,
        session: AnalysisSession,
    ) -> PhaseResult:
        """Build the RelationTensor."""
        if not store.file_syntax.available:
            logger.info("No file_syntax available, skipping tensor build")
            return PhaseResult.ok(items_processed=0)

        syntax_map = store.file_syntax.value
        n_files = len(syntax_map)

        if n_files == 0:
            logger.info("No files in store, skipping tensor build")
            return PhaseResult.ok(items_processed=0)

        try:
            from ...populate import (
                populate_authors,
                populate_clones,
                populate_cochange,
                populate_combined,
                populate_imports,
                populate_semantic,
            )
            from ...tensor.core import RelationTensor

            # Create tensor
            tensor = RelationTensor(n_files=n_files)

            # Register all file paths as nodes
            for path in syntax_map:
                tensor.register_node(path)

            layers_populated = []

            # IMPORT layer — always available (needs only file_syntax)
            try:
                populate_imports(tensor, syntax_map)
                layers_populated.append("IMPORT")
            except Exception as e:
                logger.warning(f"Failed to populate IMPORT layer: {e}")

            # COCHANGE layer — needs git_history
            if store.git_history.available:
                try:
                    now_ts = int(time.time())
                    populate_cochange(tensor, store.git_history.value, now_ts)
                    layers_populated.append("COCHANGE")
                except Exception as e:
                    logger.warning(f"Failed to populate COCHANGE layer: {e}")

                # AUTHOR layer — also needs git_history
                try:
                    populate_authors(tensor, store.git_history.value)
                    layers_populated.append("AUTHOR")
                except Exception as e:
                    logger.warning(f"Failed to populate AUTHOR layer: {e}")
            else:
                logger.debug("No git_history available, skipping COCHANGE and AUTHOR layers")

            # SEMANTIC layer — needs semantics with TF-IDF vectors
            if store.semantics.available:
                try:
                    semantics_map = store.semantics.value
                    # Extract TF-IDF vectors from FileSemantics objects
                    tfidf_vectors: dict[str, dict[str, float]] = {}
                    for path, sem in semantics_map.items():
                        # Prefer import_fingerprint (dict[str,float]) if available
                        if hasattr(sem, "import_fingerprint") and sem.import_fingerprint:
                            tfidf_vectors[path] = sem.import_fingerprint
                        # Fall back to concepts list → convert to dict
                        elif hasattr(sem, "concepts") and sem.concepts:
                            vec: dict[str, float] = {}
                            for concept in sem.concepts:
                                if hasattr(concept, "topic") and hasattr(concept, "weight"):
                                    vec[concept.topic] = concept.weight
                                elif hasattr(concept, "name") and hasattr(concept, "score"):
                                    vec[concept.name] = concept.score
                            if vec:
                                tfidf_vectors[path] = vec
                    if tfidf_vectors:
                        populate_semantic(tensor, tfidf_vectors)
                        layers_populated.append("SEMANTIC")
                except Exception as e:
                    logger.warning(f"Failed to populate SEMANTIC layer: {e}")
            else:
                logger.debug("No semantics available, skipping SEMANTIC layer")

            # CLONE layer — needs clone_pairs
            if store.clone_pairs.available:
                try:
                    populate_clones(tensor, store.clone_pairs.value)
                    layers_populated.append("CLONE")
                except Exception as e:
                    logger.warning(f"Failed to populate CLONE layer: {e}")
            else:
                logger.debug("No clone_pairs available, skipping CLONE layer")

            # COMBINED layer — always runs (works with whatever layers exist)
            try:
                populate_combined(tensor)
                layers_populated.append("COMBINED")
            except Exception as e:
                logger.warning(f"Failed to populate COMBINED layer: {e}")

            # Store tensor in slot
            store.tensor.set(tensor, produced_by="tensor_build")

            # Persist to disk if .shannon directory exists (persistence enabled)
            try:
                from ...tensor.persistence import save_tensor

                shannon_dir = Path(store.root_dir) / ".shannon"
                if shannon_dir.exists():
                    save_tensor(tensor, Path(store.root_dir))
                    logger.debug("Tensor saved to disk")
            except Exception as e:
                logger.debug(f"Tensor persistence skipped: {e}")

            logger.info(
                f"Tensor built: {tensor.n_nodes} nodes, {tensor.n_edges} edges, "
                f"layers={layers_populated}"
            )
            return PhaseResult.ok(items_processed=n_files)

        except Exception as e:
            logger.warning(f"Tensor build failed: {e}")
            store.tensor.set_error(str(e), produced_by="tensor_build")
            return PhaseResult.ok(items_processed=0)
