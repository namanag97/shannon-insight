"""StructuralAnalyzer — wraps existing AnalysisEngine.

Also runs Phase 3 clone detection (NCD) on file contents.
"""

from pathlib import Path

from ...graph.clone_detection import detect_clones
from ...graph.engine import AnalysisEngine
from ...infrastructure.entities import EntityId, EntityType
from ...infrastructure.relations import Relation, RelationType
from ...infrastructure.signals import Signal
from ...logging_config import get_logger
from ..store_v2 import AnalysisStore

logger = get_logger(__name__)


class StructuralAnalyzer:
    name = "structural"
    requires: set[str] = {"files"}
    provides: set[str] = {"structural", "clone_pairs"}

    def analyze(self, store: AnalysisStore) -> None:
        if not store.file_metrics:
            return

        # Pass content getter for cached file reads (avoids re-reading from disk)
        engine = AnalysisEngine(
            store.file_metrics,
            root_dir=store.root_dir,
            content_getter=store.get_content,
        )
        result = engine.run()
        store.structural.set(result, produced_by=self.name)
        logger.debug(f"Structural analysis: {result.total_files} files, {result.total_edges} edges")

        # Sync structural signals to FactStore
        self._sync_to_fact_store(store, result)

        # Phase 3: Clone detection via NCD
        self._detect_clones(store)

    def _sync_to_fact_store(self, store: AnalysisStore, result) -> None:
        """Sync structural analysis results to FactStore.

        Writes per-file graph signals (PAGERANK, BETWEENNESS, IN_DEGREE,
        OUT_DEGREE, BLAST_RADIUS_SIZE, COMMUNITY, DEPTH, IS_ORPHAN,
        PHANTOM_IMPORT_COUNT, COMPRESSION_RATIO, COGNITIVE_LOAD) and
        global signals (MODULARITY, CYCLE_COUNT, CENTRALITY_GINI).

        Also writes IMPORTS relations for every dependency edge.
        """
        if not hasattr(store, "fact_store"):
            return

        fs = store.fact_store
        ga = result.graph_analysis
        graph = result.graph

        # Per-file signals from graph analysis
        for path, fa in result.files.items():
            entity_id = EntityId(EntityType.FILE, path)
            fs.set_signal(entity_id, Signal.PAGERANK, fa.pagerank)
            fs.set_signal(entity_id, Signal.BETWEENNESS, fa.betweenness)
            fs.set_signal(entity_id, Signal.IN_DEGREE, fa.in_degree)
            fs.set_signal(entity_id, Signal.OUT_DEGREE, fa.out_degree)
            fs.set_signal(entity_id, Signal.BLAST_RADIUS_SIZE, fa.blast_radius_size)
            fs.set_signal(entity_id, Signal.COMMUNITY, fa.community_id)
            fs.set_signal(entity_id, Signal.DEPTH, fa.depth)
            fs.set_signal(entity_id, Signal.IS_ORPHAN, fa.is_orphan)
            fs.set_signal(entity_id, Signal.PHANTOM_IMPORT_COUNT, fa.phantom_import_count)
            fs.set_signal(entity_id, Signal.COMPRESSION_RATIO, fa.compression_ratio)
            fs.set_signal(entity_id, Signal.COGNITIVE_LOAD, fa.cognitive_load)

        # Global signals
        codebase_id = EntityId(EntityType.CODEBASE, store.root_dir)
        fs.set_signal(codebase_id, Signal.MODULARITY, result.modularity)
        fs.set_signal(codebase_id, Signal.CYCLE_COUNT, result.cycle_count)
        fs.set_signal(codebase_id, Signal.CENTRALITY_GINI, ga.centrality_gini)

        # IMPORTS relations from dependency graph
        for src, targets in graph.adjacency.items():
            src_id = EntityId(EntityType.FILE, src)
            for tgt in targets:
                tgt_id = EntityId(EntityType.FILE, tgt)
                fs.add_relation(
                    Relation(
                        type=RelationType.IMPORTS,
                        source=src_id,
                        target=tgt_id,
                    )
                )

        logger.debug(
            f"FactStore sync: {len(result.files)} files, "
            f"{sum(len(t) for t in graph.adjacency.values())} IMPORTS relations"
        )

    def _detect_clones(self, store: AnalysisStore) -> None:
        """Run NCD clone detection on file contents."""
        root = Path(store.root_dir) if store.root_dir else Path.cwd()

        # Get file contents from cache or disk
        file_contents: dict[str, bytes] = {}
        for fm in store.file_metrics:
            # Try cache first
            content = store.get_content(fm.path)
            if content is not None:
                file_contents[fm.path] = content.encode("utf-8")
            else:
                # Fallback to disk read
                try:
                    full_path = root / fm.path
                    file_contents[fm.path] = full_path.read_bytes()
                except OSError:
                    pass

        if len(file_contents) < 2:
            return

        # Get roles if available (for TEST/MIGRATION exclusion)
        roles: dict[str, str] = {}
        if store.roles.available:
            roles = store.roles.value

        clone_pairs = detect_clones(file_contents, roles)
        store.clone_pairs.set(clone_pairs, produced_by=self.name)
        logger.debug(f"Clone detection: {len(clone_pairs)} pairs found")
