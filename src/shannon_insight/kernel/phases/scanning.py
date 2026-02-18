"""ScanningExecutor — Extract syntax from source files.

This phase reads each source file and extracts FileSyntax using
tree-sitter (if available) or regex fallback.

Populates:
- store.file_syntax: Dict[path, FileSyntax]
- store._content_cache: Dict[path, content] for later reuse
"""

from __future__ import annotations

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


class ScanningExecutor(BaseExecutor):
    """Extract syntax from source files.

    Uses SyntaxExtractor to parse files with tree-sitter or regex.
    Caches file content for later use by graph and compression analysis.
    """

    phase = Phase.SCANNING
    timeout_seconds = 300  # 5 minutes for parsing
    name = "scanning"

    def _execute(
        self,
        ctx: "RuntimeContext",
        store: "AnalysisStore",
        session: "AnalysisSession",
    ) -> PhaseResult:
        """Extract syntax from discovered files."""
        from ...scanning.syntax_extractor import SyntaxExtractor

        root = Path(store.root_dir)

        # Get discovered files from previous phase
        file_paths: list[Path] = getattr(ctx, "_discovered_files", [])
        if not file_paths:
            logger.warning("No files discovered, skipping scanning")
            return PhaseResult.ok(items_processed=0)

        ctx.set_phase_total(len(file_paths))
        extractor = SyntaxExtractor()

        # Extract syntax and cache content
        file_syntax = extractor.extract_all(
            file_paths,
            root,
            content_cache=store._content_cache,
        )

        # Store result
        store.file_syntax.set(file_syntax, produced_by=self.name)

        logger.info(
            f"Extracted syntax for {len(file_syntax)} files "
            f"(tree-sitter: {extractor.treesitter_count}, "
            f"fallback: {extractor.fallback_count})"
        )

        # Sync to FactStore for pattern-based finders
        self._sync_entities(store)

        return PhaseResult.ok(items_processed=len(file_syntax))

    def _sync_entities(self, store: "AnalysisStore") -> None:
        """Sync file_syntax to FactStore entities with basic signals."""
        from ...infrastructure.entities import Entity, EntityId, EntityType
        from ...infrastructure.signals import Signal

        if not store.file_syntax.available:
            return

        producer = self.name
        for path, syntax in store.file_syntax.value.items():
            entity_id = EntityId(EntityType.FILE, path)
            entity = Entity(id=entity_id, metadata={})
            store.fact_store.add_entity(entity)
            store.fact_store.set_signal(
                entity_id, Signal.LINES, syntax.lines, producer=producer
            )
            store.fact_store.set_signal(
                entity_id, Signal.FUNCTION_COUNT, syntax.function_count, producer=producer
            )
            store.fact_store.set_signal(
                entity_id, Signal.CLASS_COUNT, syntax.class_count, producer=producer
            )
            store.fact_store.set_signal(
                entity_id, Signal.IMPORT_COUNT, syntax.import_count, producer=producer
            )
