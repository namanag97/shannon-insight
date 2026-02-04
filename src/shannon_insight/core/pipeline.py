"""Composable pipeline runner."""

from typing import List, Optional

from ..models import FileMetrics, AnomalyReport, PipelineContext
from ..primitives.stages import ExtractStage, DetectStage, FuseStage, RecommendStage
from ..config import AnalysisSettings
from ..logging_config import get_logger

logger = get_logger(__name__)

DEFAULT_STAGES = [ExtractStage(), DetectStage(), FuseStage(), RecommendStage()]


class AnalysisPipeline:
    """Runs layers 2-5 on a group of files."""

    def __init__(self, settings: AnalysisSettings, cache=None, config_hash="",
                 root_dir="", stages: Optional[List] = None):
        self.settings = settings
        self.cache = cache
        self.config_hash = config_hash
        self.root_dir = root_dir
        self.stages = stages or list(DEFAULT_STAGES)

    def add_stage(self, stage, after: Optional[str] = None):
        """Insert a custom stage after a named stage (or at the end)."""
        if after is None:
            self.stages.append(stage)
            return
        for i, s in enumerate(self.stages):
            if s.name == after:
                self.stages.insert(i + 1, stage)
                return
        self.stages.append(stage)

    def run(self, files: List[FileMetrics]) -> List[AnomalyReport]:
        """Run all stages. Returns list of AnomalyReport."""
        ctx = PipelineContext(
            files=files,
            settings=self.settings,
            root_dir=self.root_dir,
            cache=self.cache,
            config_hash=self.config_hash,
        )
        for stage in self.stages:
            ctx = stage.run(ctx)
            logger.info(f"Stage '{stage.name}' complete")

        return ctx.reports or []

    def run_context(self, files: List[FileMetrics]) -> PipelineContext:
        """Run all stages and return the full context (for inspection)."""
        ctx = PipelineContext(
            files=files,
            settings=self.settings,
            root_dir=self.root_dir,
            cache=self.cache,
            config_hash=self.config_hash,
        )
        for stage in self.stages:
            ctx = stage.run(ctx)
        return ctx
