#!/usr/bin/env python3
"""Build the Phase-2 state/time/order/partiality constitution candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
AS_OF = "2026-08-26"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build() -> dict[str, Any]:
    sources = [
        {"source_id": "source.semantic-phase2.w3c.scxml", "publisher": "W3C", "source_kind": "recommendation", "title": "State Chart XML (SCXML): State Machine Notation for Control Abstraction", "url": "https://www.w3.org/TR/scxml/", "claim_scope": "states, events, transitions, executable content and deterministic processing", "authority_limit": "SCXML specifies its state-machine notation and processor semantics, not every enterprise aggregate lifecycle or effect authority."},
        {"source_id": "source.semantic-phase2.lamport.clocks", "publisher": "ACM / Leslie Lamport", "source_kind": "original_research", "title": "Time, Clocks, and the Ordering of Events in a Distributed System", "url": "https://lamport.azurewebsites.net/pubs/time-clocks.pdf", "claim_scope": "happened-before partial order and logical clocks", "authority_limit": "Logical clocks establish ordering properties, not physical occurrence time, business causality or source truth."},
        {"source_id": "source.semantic-phase2.w3c.owl-time", "publisher": "W3C", "source_kind": "recommendation", "title": "Time Ontology in OWL", "url": "https://www.w3.org/TR/owl-time/", "claim_scope": "instants, intervals, durations, temporal positions and reference systems", "authority_limit": "OWL-Time does not choose application time roles, clock authority, lateness, database recording policy or correction semantics."},
        {"source_id": "source.semantic-phase2.apache.beam", "publisher": "Apache Software Foundation", "source_kind": "official_documentation", "title": "Apache Beam Programming Guide", "url": "https://beam.apache.org/documentation/programming-guide/", "claim_scope": "bounded/unbounded collections, event time, windows, watermarks, triggers, state and timers", "authority_limit": "Beam defines its portable dataflow model, not universal business finality, source completeness or acceptance."},
        {"source_id": "source.semantic-phase2.apache.arrow", "publisher": "Apache Software Foundation", "source_kind": "open_specification", "title": "Apache Arrow Columnar Format", "url": "https://arrow.apache.org/docs/format/Columnar.html", "claim_scope": "array validity bitmap, null count, typed slots and physical layout", "authority_limit": "A physical null marker carries no missingness reason, observation mechanism, imputation authority or domain validity."},
        {"source_id": "source.semantic-phase2.oasis.xacml", "publisher": "OASIS", "source_kind": "standard", "title": "XACML 3.0 Core", "url": "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-en.html", "claim_scope": "Permit, Deny, Indeterminate, NotApplicable and combining behavior", "authority_limit": "XACML decision states do not define all partial-information domains and do not prove enforcement or business truth."},
        {"source_id": "source.semantic-phase2.otel.metrics", "publisher": "OpenTelemetry / CNCF", "source_kind": "official_specification", "title": "OpenTelemetry Metrics Data Model", "url": "https://opentelemetry.io/docs/specs/otel/metrics/data-model/", "claim_scope": "metric stream identity, timestamps, delta/cumulative temporality, gaps and no-recorded-value", "authority_limit": "Telemetry gaps and staleness markers do not define generic missingness, business measure semantics or analytical completeness."},
    ]
    constitution = {
        "record_kind": "semantic_axis_phase_constitution_candidate",
        "constitution_id": "constitution.semantic-axis.phase2.dynamics-information.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "EVIDENCE_BACKED_CANDIDATE_PENDING_OWNER_RATIFICATION",
        "completion_claim": False,
        "sovereign_question": "How does an exact subject change, when does each fact apply or become known, what order/topology is proved, and what information remains absent, uncertain, partial or unresolved?",
        "negative_mission": "Do not infer lifecycle from status strings, time role from timestamps, causality from clock order, completeness from bounded storage, or missingness and uncertainty from null markers.",
        "modules": [
            {
                "module_id": "module.semantic-axis.state-change.v1",
                "axis": "state_and_change",
                "coordinates": [
                    "subject and aggregate identity", "state-machine edition", "current revision",
                    "command identity and authority", "event/fact identity", "transition precondition",
                    "next state and emitted facts", "history cut and completeness", "concurrency relation",
                    "snapshot identity", "delta base and applicability", "irreversibility and compensation",
                ],
                "non_collapse_laws": [
                    "command request is not event fact",
                    "event history is not current state",
                    "state is not snapshot representation",
                    "snapshot is not checkpoint or durable commit",
                    "delta is meaningless without exact base and applicability",
                    "retry is not replay and replay is not re-execution of effects",
                    "supersession recall reversal rollback and compensation are distinct",
                    "illegal transition stale revision duplicate command and incomplete history are distinct refusals",
                    "external side effects are observations consumed by a reducer, not hidden transition behavior",
                ],
                "required_outcomes": ["transitioned", "no_op_by_law", "duplicate", "stale", "illegal", "indeterminate_history", "effect_reconciliation_required", "refused"],
            },
            {
                "module_id": "module.semantic-axis.time.v1",
                "axis": "time",
                "carrier_coordinates": [
                    "temporal reference system", "clock or calendar authority", "instant/local/offset/zoned carrier",
                    "interval endpoint and inclusivity", "elapsed duration versus calendar period",
                    "precision resolution and uncertainty", "zone-rules edition", "leap/fold/gap policy",
                ],
                "role_coordinates": [
                    "occurrence time", "observation time", "valid time", "recording time",
                    "transaction time", "processing time", "decision time", "correction time",
                    "deadline", "TTL age origin", "schedule/calendar applicability",
                ],
                "non_collapse_laws": [
                    "instant is not local date-time or textual timestamp",
                    "offset is not time zone and zone rules are editioned",
                    "elapsed duration is not calendar period",
                    "occurrence observation validity recording transaction processing decision and correction times are separate roles",
                    "deadline is not occurrence time and TTL requires an age origin",
                    "wall-clock reading does not prove causal order",
                    "window membership lateness trigger firing and business finality are distinct",
                    "bitemporality requires independently queryable validity and recording axes",
                    "precision uncertainty and unknown time are not zero duration",
                ],
                "required_outcomes": ["exact", "interval_bounded", "uncertain", "ambiguous_fold", "nonexistent_gap", "role_unbound", "clock_untrusted", "out_of_range", "refused"],
            },
            {
                "module_id": "module.semantic-axis.order-topology.v1",
                "axis": "order_and_topology",
                "order_coordinates": [
                    "ordered subject domain", "relation edition", "total partial preorder or sequence",
                    "tie and stability policy", "partition scope", "causal witness", "arrival/source/event/processing order role",
                ],
                "topology_coordinates": [
                    "node and edge identity", "direction", "multiplicity", "hierarchy versus general graph",
                    "cycle policy", "path semantics", "spatial reference and precision", "boundary/interior model",
                ],
                "non_collapse_laws": [
                    "arrival order is not source order event order or causal order",
                    "total order is not partial order and incomparable is a valid result",
                    "a deterministic tie-break extension does not manufacture causality",
                    "partition-local order is not global order",
                    "hierarchy DAG multigraph hypergraph and spatial topology are distinct models",
                    "reachability is not causality and correlation is not causal effect",
                    "graph isomorphism is not subject identity or semantic equivalence",
                    "coordinate equality without CRS precision and boundary policy does not prove spatial equality",
                ],
                "required_outcomes": ["before", "after", "equal_under_relation", "concurrent", "incomparable", "cycle_detected", "topology_invalid", "relation_unbound", "refused"],
            },
            {
                "module_id": "module.semantic-axis.partiality-uncertainty.v1",
                "axis": "partiality_and_uncertainty",
                "information_states": [
                    "present", "missing_with_reason", "unknown", "not_applicable", "withheld_by_authority",
                    "invalid", "censored_with_bound", "truncated", "not_yet_observed", "deleted_or_expired",
                    "partial_result", "indeterminate", "unknown_completion",
                ],
                "uncertainty_coordinates": [
                    "uncertainty kind", "population or sample space", "distribution or bound semantics",
                    "confidence/coverage/credibility interpretation", "calibration evidence",
                    "numerical approximation and tolerance", "propagation rule", "correlation assumptions",
                    "decision threshold and residual owner",
                ],
                "non_collapse_laws": [
                    "missing null empty zero false and default are distinct",
                    "unknown is not false deny or not-applicable",
                    "withheld is not absent and carries authority scope",
                    "censored is not missing because it carries an observation mechanism or bound",
                    "invalid is not missing and may require quarantine or refusal",
                    "partial result is not complete result and carries coverage residual",
                    "probability confidence score likelihood and uncertainty are distinct",
                    "approximate is not exact and error/failure guarantees are explicit",
                    "timeout unknown completion infeasible and unbounded are distinct",
                    "imputation is a derived value with method/version evidence, not recovery of an observed fact",
                ],
                "required_outcomes": ["present", "partial", "missing", "censored", "withheld", "not_applicable", "invalid", "indeterminate", "unknown_completion", "refused"],
            },
        ],
        "cross_module_laws": [
            "Every event and state observation binds subject identity, grain, time role and order domain independently.",
            "A state transition may consume time/order/information witnesses but cannot invent them.",
            "Finality is a policy conclusion over progress, completeness and authority evidence; no watermark timestamp or closed file proves business finality alone.",
            "Corrections preserve prior recording history unless an explicit retention/erasure authority says otherwise.",
            "Uncertainty and partiality propagate through transformations according to declared laws or remain residuals.",
        ],
        "imported_foundation_refs": [
            "library.csp.time.instant-core", "library.csp.time.interval-algebra", "library.csp.time.duration-core",
            "library.csp.time.calendar-period", "library.csp.time.recurrence", "library.csp.time.business-calendar",
            "library.csp.time.bitemporal-ledger", "library.csp.time.causal-clock",
            "library.csp.quantity.partial-information", "library.csp.quantity.probability-core",
            "library.csp.quantity.uncertainty-propagation", "library.csp.decision.compensation",
            "library.runtime-resource.attempt-state", "library.runtime-resource.deadline-cancellation",
        ],
        "prohibited_new_facades": ["universal_state", "universal_event", "universal_timestamp", "universal_order", "universal_null", "universal_uncertainty"],
        "ratification_gate": "Named foundation owners accept coordinates, information states, outcomes, non-collapse laws and imports; all family matrices record applicability, profiles and exceptions.",
    }
    claims = [
        {"claim_id": "claim.phase2.scxml-transition", "source_ref": "source.semantic-phase2.w3c.scxml", "bounded_claim": "SCXML defines event-driven state configurations and legal transitions; absent external processors a conforming machine reacts deterministically to the same input event sequence unless explicitly nondeterministic.", "supports_module_refs": ["module.semantic-axis.state-change.v1"], "authority_limit": sources[0]["authority_limit"]},
        {"claim_id": "claim.phase2.lamport-partial-order", "source_ref": "source.semantic-phase2.lamport.clocks", "bounded_claim": "The happened-before relation is a partial order over distributed events; logical clocks can extend ordering but a total tie-break does not turn concurrent events into causally related events.", "supports_module_refs": ["module.semantic-axis.order-topology.v1", "module.semantic-axis.time.v1"], "authority_limit": sources[1]["authority_limit"]},
        {"claim_id": "claim.phase2.owl-time-carriers", "source_ref": "source.semantic-phase2.w3c.owl-time", "bounded_claim": "OWL-Time distinguishes instants, intervals, durations and temporal reference systems while leaving application-specific occurrence, validity and recording roles to profiles.", "supports_module_refs": ["module.semantic-axis.time.v1"], "authority_limit": sources[2]["authority_limit"]},
        {"claim_id": "claim.phase2.beam-time-progress", "source_ref": "source.semantic-phase2.apache.beam", "bounded_claim": "Beam separates boundedness, event-time windows, watermarks, triggers, state and timers; a watermark is a progress estimate rather than proof of source or business finality.", "supports_module_refs": ["module.semantic-axis.state-change.v1", "module.semantic-axis.time.v1", "module.semantic-axis.order-topology.v1"], "authority_limit": sources[3]["authority_limit"]},
        {"claim_id": "claim.phase2.arrow-null-carrier", "source_ref": "source.semantic-phase2.apache.arrow", "bounded_claim": "Arrow encodes per-slot nullness with validity bitmaps and a null count, while masked value bytes are not semantically meaningful.", "supports_module_refs": ["module.semantic-axis.partiality-uncertainty.v1"], "authority_limit": sources[4]["authority_limit"]},
        {"claim_id": "claim.phase2.xacml-indeterminate", "source_ref": "source.semantic-phase2.oasis.xacml", "bounded_claim": "XACML keeps Permit, Deny, Indeterminate and NotApplicable distinct and makes combining behavior explicit.", "supports_module_refs": ["module.semantic-axis.partiality-uncertainty.v1"], "authority_limit": sources[5]["authority_limit"]},
        {"claim_id": "claim.phase2.otel-gap-and-temporality", "source_ref": "source.semantic-phase2.otel.metrics", "bounded_claim": "OpenTelemetry metrics separates delta/cumulative temporality, observation/start timestamps, stream gaps and an explicit no-recorded-value marker.", "supports_module_refs": ["module.semantic-axis.time.v1", "module.semantic-axis.partiality-uncertainty.v1"], "authority_limit": sources[6]["authority_limit"]},
    ]
    projection = {
        "record_kind": "semantic_axis_compiler_projection_candidate",
        "projection_id": "projection.compiler.semantic-axis.phase2.v1",
        "edition": 1,
        "status": "STRUCTURAL_PROJECTION_NOT_IR_AUTHORITY",
        "required_ir_roles": [
            "LifecycleEditionRef", "RevisionRef", "CommandRef", "DomainEventRef", "TransitionOutcome",
            "SnapshotRef", "DeltaRef", "HistoryCutRef", "TemporalRoleRef", "TemporalValue",
            "ClockAuthorityRef", "OrderRelationRef", "TopologyProfileRef", "InformationState",
            "UncertaintyProfileRef", "ProgressWitnessRef", "FinalityPolicyRef", "Residual",
        ],
        "binding_sequence": [
            "bind subject identity and grain from Phase 1",
            "bind lifecycle edition revision history cut and transition law",
            "bind each temporal carrier to one explicit time role and authority",
            "bind order/topology relation and partition scope",
            "bind information state and uncertainty interpretation",
            "compare producer/consumer progress finality and partiality requirements",
            "insert only proved conversions with preserved set loss residual and authority",
            "refuse unresolved causality finality missingness or uncertainty semantics",
        ],
        "required_adapter_proofs": [
            "transition/history preservation", "time-role preservation", "precision and interval preservation",
            "order and concurrency preservation", "topology preservation", "information-state preservation",
            "uncertainty propagation", "progress/finality non-escalation", "unknown-completion reconciliation",
        ],
        "refusal_roles": [
            "lifecycle_unbound", "stale_revision", "illegal_transition", "history_incomplete",
            "time_role_unbound", "clock_authority_unbound", "temporal_ambiguity", "order_relation_unbound",
            "incomparable", "topology_incompatible", "missingness_reason_unbound", "uncertainty_unbound",
            "approximation_unaccepted", "progress_insufficient", "finality_unproved", "unknown_completion",
        ],
        "generation_prohibition": "Do not infer lifecycle, time role, causality, finality, missingness or uncertainty from field names, timestamps, status strings, null markers or provider acknowledgements.",
    }
    summary = {
        "program_id": "program.semantic-axis.phase2.dynamics-information.v1", "edition": 1,
        "as_of": AS_OF, "status": "ACTIVE_PENDING_OWNER_RATIFICATION", "completion_claim": False,
        "modules": 4, "primary_sources": len(sources), "bounded_primary_evidence_claims": len(claims),
        "time_role_coordinates": 11, "information_states": 13,
        "canonical_exact_gaps_closed": 0, "remaining_gate": constitution["ratification_gate"],
    }
    return {"sources": sources, "constitution": constitution, "claims": claims, "projection": projection, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "constitution.json": json.dumps(built["constitution"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "evidence-claims.jsonl": "".join(canonical(row) + "\n" for row in built["claims"]),
        "compiler-projection.json": json.dumps(built["projection"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.semantic-axis.phase2.v1", "as_of": AS_OF, "files": manifest}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text: stale.append(name)
        else: path.write_text(text, encoding="utf-8")
    if stale: print("STALE " + ", ".join(stale)); return 1
    s = build()["summary"]
    print(f"{'CHECK' if args.check else 'BUILD'} PASS Phase 2 semantic constitution: {s['modules']} modules, {s['primary_sources']} sources, {s['bounded_primary_evidence_claims']} claims, zero canonical gaps closed")
    return 0


if __name__ == "__main__": raise SystemExit(main())
