#!/usr/bin/env python3
"""Build bounded primary-evidence candidates for partiality and uncertainty."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
TARGETS = SEM / "structured_projection/targeted-evidence-work-packages.jsonl"
AS_OF = "2026-08-27"
sys.path.insert(0, str(SEM))

from axis_evidence_campaign import build_campaign, campaign_outputs, write_outputs  # noqa: E402


CLAIMS: dict[str, dict[str, Any]] = {
    "constitution.family.query_compilation_execution": {
        "title": "Substrait Type System",
        "publisher": "Substrait",
        "url": "https://substrait.io/types/type_system/",
        "claim": "Every Substrait type declares nullability separately from its class, variation and parameters; null is a special value of a nullable type rather than a standalone null type. Partially bound plans may also carry an unbound placeholder until a downstream binder assigns a concrete type, and type changes require explicit casts.",
        "coordinates": ["nullable_value", "required_value", "unbound_type_placeholder", "explicit_cast", "representation_variation"],
        "limit": "Substrait specifies plan interchange types. It does not encode why a value is missing, make SQL null equal to an unbound type or failed expression, define all function-level propagation, or prove that a downstream engine preserves source missingness and error semantics.",
        "negative": "nullable, absent, unbound, invalid, failed and unknown query results are one state that can be propagated by a universal optional-value rule",
    },
    "constitution.family.runtime_resource_control": {
        "title": "Kubernetes API Conventions",
        "publisher": "Kubernetes SIG Architecture",
        "url": "https://github.com/kubernetes/community/blob/main/contributors/devel/sig-architecture/api-conventions.md",
        "claim": "Kubernetes conditions carry True, False or Unknown, treat an absent known condition as Unknown, and bind an observation to an observed generation so consumers can detect stale status. Condition polarity is type-specific, so generic aggregation cannot infer a universal health truth.",
        "coordinates": ["condition_true_false_unknown", "absent_condition_unknown", "observed_generation", "stale_observation", "condition_specific_polarity"],
        "limit": "The conventions describe Kubernetes API observations. They do not make Unknown equivalent to timeout or failure, prove an effect completed, define retry safety, preserve every historical observation, or supply one readiness lattice for all runtime resources and providers.",
        "negative": "missing or stale runtime status is false, every condition has positive polarity, and a generic boolean fold proves current completion and retry safety",
    },
    "constitution.family.forecasting_lifecycle": {
        "title": "Forecasting: Principles and Practice, 3rd edition — Distributional forecasts and prediction intervals",
        "publisher": "Rob J. Hyndman and George Athanasopoulos",
        "url": "https://otexts.com/fpp3/prediction-intervals.html",
        "claim": "Forecast uncertainty may be represented by a forecast distribution, quantiles, prediction intervals or simulated sample paths rather than only a point value. Interval construction depends on model and residual assumptions, and uncertainty generally grows with the forecast horizon.",
        "coordinates": ["point_forecast", "forecast_distribution", "quantile", "prediction_interval", "sample_path", "horizon_dependent_uncertainty"],
        "limit": "The text explains statistical forecasting under stated assumptions. A prediction interval is not a confidence interval for a fixed parameter, a guarantee for an individual future value, evidence that omitted predictor uncertainty was included, or authorization to publish or override a forecast.",
        "negative": "one point estimate and a generic confidence number fully represent forecast uncertainty, and equal-width intervals are comparable across horizons, populations, models and assumptions",
    },
    "constitution.family.persistence_lakehouse": {
        "title": "PostgreSQL 18 Documentation — CREATE VIEW",
        "publisher": "PostgreSQL Global Development Group",
        "url": "https://www.postgresql.org/docs/current/sql-createview.html",
        "claim": "A PostgreSQL view is a named query evaluated whenever referenced rather than a physically materialized relation. Replacement preserves a required visible column shape while calculations may change, and update/check behavior is partial: local and cascaded checks differ and some view forms are not automatically updatable.",
        "coordinates": ["virtual_relation_definition", "evaluation_time_result", "shape_preserving_replacement", "partial_updateability", "local_or_cascaded_check"],
        "limit": "PostgreSQL documents one database's view lifecycle. It does not give a view result snapshot completeness, preserve historical evaluation inputs, prove two same-shaped definitions equivalent, generalize updateability to federated views, or turn successful query evaluation into durable materialization.",
        "negative": "a virtual relation is a stored complete dataset, same output columns preserve its meaning, and every view row has total update and visibility behavior",
    },
    "constitution.family.geospatial_analytics": {
        "title": "OGC Moving Features Encoding Extension — JSON 1.0",
        "publisher": "Open Geospatial Consortium",
        "url": "https://docs.ogc.org/is/19-045r3/19-045r3.html",
        "claim": "OGC Moving Features models discrete, step and continuous phenomena differently, defines temporal geometry as geometry parameterized by time over a temporal domain, and defines a life span as the period during which something exists. Observation at one instant is therefore a temporally scoped leaf, not a total timeless geometry.",
        "coordinates": ["temporal_domain", "lifespan", "discrete_phenomenon", "step_phenomenon", "continuous_phenomenon", "instant_leaf"],
        "limit": "The standard defines an interchange encoding for moving-feature geometry and temporal properties. It explicitly excludes some partial motions, deformation and succession, and does not infer unobserved positions, quantify measurement uncertainty, prove occurrence continuity or establish business-event lifecycle authority.",
        "negative": "a missing position means the feature does not exist, observations interpolate a total trajectory automatically, and discrete, step and continuous occurrence lifecycles share one completion rule",
    },
}


def build() -> dict[str, Any]:
    return build_campaign(
        axis="partiality_and_uncertainty",
        campaign_key="p3u",
        program_id="program.p3u.partiality-uncertainty-evidence.v1",
        claims=CLAIMS,
        targets_path=TARGETS,
        as_of=AS_OF,
    )


def outputs() -> dict[str, str]:
    return campaign_outputs(
        built=build(),
        manifest_id="manifest.p3u.partiality-uncertainty-evidence.v1",
        as_of=AS_OF,
    )


def main() -> int:
    write_outputs(HERE, outputs())
    summary = build()["summary"]
    print(
        "BUILD PASS P3U partiality/uncertainty: "
        f"{summary['primary_evidence_candidates']} bounded candidates route "
        f"{summary['represented_library_occurrences']} library occurrences; "
        "owner decisions and gap closures remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
