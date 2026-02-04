"""Pipeline stages — each is an independent, composable unit."""

from ..models import PipelineContext


class ExtractStage:
    name = "extract"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .extractor import PrimitiveExtractor
        extractor = PrimitiveExtractor(
            ctx.files, cache=ctx.cache,
            config_hash=ctx.config_hash, root_dir=ctx.root_dir,
        )
        ctx.primitives = extractor.extract_all()
        return ctx


class DetectStage:
    name = "detect"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .detector import AnomalyDetector
        detector = AnomalyDetector(
            ctx.primitives, threshold=ctx.settings.z_score_threshold,
        )
        ctx.normalized = detector.normalize()
        ctx.anomalies = detector.detect_anomalies(ctx.normalized)
        return ctx


class FuseStage:
    name = "fuse"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .fusion import SignalFusion
        fusion = SignalFusion(
            ctx.primitives, ctx.normalized, weights=ctx.settings.fusion_weights,
        )
        ctx.fused_scores = fusion.fuse()
        return ctx


class RecommendStage:
    name = "recommend"

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from .recommendations import RecommendationEngine
        engine = RecommendationEngine(
            ctx.files, ctx.primitives, ctx.normalized,
            ctx.anomalies, ctx.fused_scores, root_dir=ctx.root_dir,
        )
        ctx.reports = engine.generate()
        return ctx
