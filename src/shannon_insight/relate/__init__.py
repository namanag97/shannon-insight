"""RELATE context: binding kernel, G_import layer, set-algebra facts."""

from shannon_insight.relate.manifests import ManifestFacts, read_manifests
from shannon_insight.relate.protocols import (
    BindMethod,
    BindingRecord,
    Confidence,
    EdgeRecord,
    ExternalPkg,
    PhantomFact,
    RelateMetrics,
    Verdict,
)
from shannon_insight.relate.service import RelateConfig, RelateInputs, RelateResult, RelateService

__all__ = [
    "BindMethod", "BindingRecord", "Confidence", "EdgeRecord", "ExternalPkg",
    "ManifestFacts", "PhantomFact", "RelateConfig", "RelateInputs",
    "RelateMetrics", "RelateResult", "RelateService", "Verdict", "read_manifests",
]
