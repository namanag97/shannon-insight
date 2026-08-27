#!/usr/bin/env python3
"""Build non-authoritative semantic-axis signatures for every open exact-contract gap."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
GENERATION = HERE.parent
REGISTRY = GENERATION.parent
AS_OF = "2026-08-26"


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def facet(short: str, patterns: list[str], laws: list[str]) -> dict[str, Any]:
    return {"facet": short, "discovery_patterns": patterns, "constitutional_laws": laws}


AXES: list[dict[str, Any]] = [
    {"axis": "semantic_object", "question": "What kind of thing does this contract mean or govern?", "non_collapse": ["value is not occurrence", "event is not state", "claim is not evidence", "plan is not execution"], "facets": [
        facet("value", [r"\b(value|quantity|measure|unit|money|ratio)\b"], ["value equality is declared explicitly"]),
        facet("entity_or_occurrence", [r"\b(entity|record|occurrence|object|asset|subject)\b"], ["identity survives mutable attributes only under an explicit lifecycle"]),
        facet("event_or_fact", [r"\b(event|fact|observation|signal)\b"], ["a recorded fact is not a requested command"]),
        facet("state_or_snapshot", [r"\b(state|snapshot|checkpoint|view)\b"], ["snapshot identity is scoped to its cut and source"]),
        facet("relation_or_graph", [r"\b(graph|edge|relation|lineage|topology)\b"], ["edge identity and node identity are independent decisions"]),
        facet("rule_or_policy", [r"\b(policy|rule|constraint|specification)\b"], ["policy edition and selection authority are explicit"]),
        facet("plan_or_intent", [r"\b(plan|intent|command|request|proposal)\b"], ["intent is not effect"]),
        facet("claim_or_evidence", [r"\b(claim|evidence|proof|attestation|receipt)\b"], ["integrity is not truth and evidence is scope-bound"]),
        facet("resource_or_capability", [r"\b(resource|capacity|capability|quota|budget)\b"], ["availability and entitlement are distinct"]),
        facet("representation_artifact", [r"\b(format|schema|document|message|file|encoding|artifact)\b"], ["representation conformance is not domain validity"]),
    ]},
    {"axis": "semantic_role", "question": "What transformation or judgment is owned?", "non_collapse": ["observe is not decide", "validate is not authorize", "compile is not execute", "publish is not accept"], "facets": [
        facet("describe_or_observe", [r"\b(observe|describe|inspect|profile|measure)\w*\b"], ["observations retain source and recording context"]),
        facet("validate_or_conform", [r"\b(validate|conform|verify|check|lint)\w*\b"], ["validation is relative to an exact profile"]),
        facet("derive_or_transform", [r"\b(derive|transform|convert|map|normalize|encode|decode|parse)\w*\b"], ["preservation and loss are explicit"]),
        facet("compare_or_reconcile", [r"\b(compare|diff|match|reconcile|merge|resolve)\w*\b"], ["conflict and residual remain first-class"]),
        facet("decide_or_optimize", [r"\b(decide|evaluate|optimi[sz]|solve|rank|select)\w*\b"], ["feasible, optimal, unknown and refused are distinct"]),
        facet("plan_or_compile", [r"\b(plan|compile|lower|bind)\w*\b"], ["a verified plan proves no execution"]),
        facet("coordinate_lifecycle", [r"\b(schedule|orchestrat|lifecycle|transition|workflow|saga)\w*\b"], ["legal state transitions are total and editioned"]),
        facet("execute_effect", [r"\b(execute|write|publish|send|delete|allocate|start|cancel)\w*\b"], ["attempt, observation, receipt and accepted outcome are distinct"]),
        facet("persist_or_retrieve", [r"\b(store|persist|load|query|read|repository|cache)\w*\b"], ["storage occurrence is not semantic identity"]),
    ]},
    {"axis": "identity_and_equality", "question": "What is identical, equal, equivalent or merely correlated?", "non_collapse": ["name is not identity", "byte equality is not semantic equality", "version identity is not occurrence identity"], "facets": [
        facet("opaque_identity", [r"\b(id|identity|identifier|key|reference|ref)\b"], ["opaque identifiers are compared only within their declared domain"]),
        facet("value_equality", [r"\b(equal|equality|compare|ordering)\w*\b"], ["equality relation and domain are editioned"]),
        facet("canonical_equivalence", [r"\b(canonical|normal form|equivalence|digest|hash)\w*\b"], ["canonical form is scoped to one equivalence relation"]),
        facet("versioned_identity", [r"\b(version|edition|revision|generation)\w*\b"], ["mutable reference and immutable version are distinct"]),
        facet("occurrence_identity", [r"\b(occurrence|attempt|instance|run|execution)\w*\b"], ["logical subject and physical occurrence are distinct"]),
        facet("content_addressed", [r"\b(content.address|digest|merkle|checksum)\w*\b"], ["content identity proves bytes under an algorithm, not truth"]),
    ]},
    {"axis": "grain_and_cardinality", "question": "At what grain and cardinality does meaning hold?", "non_collapse": ["scalar is not collection", "partition is not whole", "page is not result set"], "facets": [
        facet("scalar_or_single", [r"\b(scalar|single|one|datum)\b"], ["single-subject scope is explicit"]),
        facet("record_or_tuple", [r"\b(record|row|tuple|item|object)\b"], ["field and record validity are distinct"]),
        facet("collection_or_set", [r"\b(collection|set|batch|list|group)\b"], ["set, bag and sequence semantics are distinct"]),
        facet("partitioned", [r"\b(partition|shard|bucket|segment)\w*\b"], ["partition-local order or completeness is not global"]),
        facet("stream_or_unbounded", [r"\b(stream|continuous|unbounded|feed)\w*\b"], ["bounded and unbounded inputs have distinct completion laws"]),
        facet("graph_or_network", [r"\b(graph|network|topology|edge|node)\w*\b"], ["graph closure and traversal scope are explicit"]),
    ]},
    {"axis": "state_and_change", "question": "How can the subject change, and what history is retained?", "non_collapse": ["command is not event", "snapshot is not delta", "supersede is not delete", "retry is not replay"], "facets": [
        facet("immutable_value", [r"\b(immutable|value object|pure)\b"], ["change creates a new value"]),
        facet("append_only_event", [r"\b(append.only|event log|journal|audit log)\b"], ["correction is a new fact, not mutation of history"]),
        facet("lifecycle_transition", [r"\b(lifecycle|state machine|transition|status)\w*\b"], ["illegal transitions refuse"]),
        facet("versioned_mutation", [r"\b(update|revision|optimistic|concurrency|mutable)\w*\b"], ["expected version and race outcome are explicit"]),
        facet("snapshot_and_delta", [r"\b(snapshot|delta|change data|cdc|diff)\w*\b"], ["base identity and applicability precede delta application"]),
        facet("compensation_or_reversal", [r"\b(compensat|rollback|reversal|recall|supersed)\w*\b"], ["compensation is not erasure and may fail"]),
    ]},
    {"axis": "time", "question": "Which time domains, intervals and clocks affect truth?", "non_collapse": ["event time is not recording time", "validity is not availability", "deadline is not event time"], "facets": [
        facet("event_time", [r"\b(event time|occurred at|occurrence time)\b"], ["event-time source and precision are explicit"]),
        facet("recording_or_processing_time", [r"\b(recording time|processing time|ingest time|observed at)\b"], ["recording order cannot silently replace event order"]),
        facet("validity_time", [r"\b(valid time|validity|effective|effective time)\w*\b"], ["validity interval boundaries are explicit"]),
        facet("bitemporal", [r"\b(bitemporal|bi.temporal)\b"], ["valid and recording axes remain independently queryable"]),
        facet("interval_or_window", [r"\b(window|interval|range|period)\w*\b"], ["open, closed and unbounded endpoints are explicit"]),
        facet("deadline_or_timeout", [r"\b(deadline|timeout)\w*\b"], ["clock source, deadline domain and timeout consequence are explicit"]),
        facet("ttl_or_expiry", [r"\b(ttl|expiry|expiration)\w*\b"], ["age origin, clock, renewal and expiry consequence are explicit"]),
        facet("schedule_or_calendar", [r"\b(schedule|calendar|recurrence|cron)\w*\b"], ["civil time, instant and recurrence identity remain distinct"]),
    ]},
    {"axis": "order_and_topology", "question": "What ordering, hierarchy, geometry or connectivity laws hold?", "non_collapse": ["arrival order is not event order", "total order is not partial order", "hierarchy is not arbitrary graph"], "facets": [
        facet("total_order", [r"\b(total order|sorted|sequence|offset|rank)\w*\b"], ["tie and stability laws are explicit"]),
        facet("partial_order", [r"\b(partial order|frontier|antichain|causal|happens.before)\w*\b"], ["incomparability is a valid outcome"]),
        facet("hierarchy", [r"\b(tree|hierarch|parent|child|taxonomy)\w*\b"], ["multiple parenthood and cycles are declared"]),
        facet("graph_topology", [r"\b(graph|edge|node|path|reachab)\w*\b"], ["direction, multiplicity and path semantics are explicit"]),
        facet("spatial_topology", [r"\b(spatial|geometry|geograph|coordinate|topology)\w*\b"], ["CRS, precision and boundary model are explicit"]),
        facet("unordered", [r"\b(unordered|set semantics)\b"], ["iteration order cannot acquire meaning"]),
    ]},
    {"axis": "partiality_and_uncertainty", "question": "How are missingness, ambiguity, approximation and unknown outcomes represented?", "non_collapse": ["unknown is not false", "missing is not null", "approximate is not exact", "timeout is not infeasible"], "facets": [
        facet("optional_missing_null", [r"\b(optional|missing|null|absent|empty)\w*\b"], ["missing null empty zero and default remain distinct"]),
        facet("three_or_multi_valued", [r"\b(indeterminate|three.valued|unknown|ambiguous)\w*\b"], ["unknown is preserved through composition"]),
        facet("probabilistic", [r"\b(probabil|distribution|confidence|likelihood|bayes)\w*\b"], ["calibration population and uncertainty type are explicit"]),
        facet("interval_or_bound", [r"\b(bound|interval estimate|confidence interval|error bar)\w*\b"], ["lower upper and confidence semantics are explicit"]),
        facet("approximate_or_lossy", [r"\b(approx|lossy|error tolerance|sketch)\w*\b"], ["error guarantee and failure probability are explicit"]),
        facet("unknown_completion", [r"\b(unknown completion|ambiguous completion|reconcile before retry)\b"], ["unknown completion reconciles before retry"]),
    ]},
    {"axis": "authority_and_trust", "question": "Who may assert, decide, approve, execute or accept?", "non_collapse": ["proposal is not authorization", "approval is not issuance", "receipt is not acceptance", "proof is not authority"], "facets": [
        facet("issuer_or_source_authority", [r"\b(issuer authority|source authority|system of record|authoritative source)\w*\b"], ["authority scope and edition are explicit"]),
        facet("policy_decision", [r"\b(policy decision|permit|deny|authorize|authorization)\w*\b"], ["decision and enforcement are distinct"]),
        facet("delegation_or_approval", [r"\b(delegat|approval|maker.checker|separation of duties)\w*\b"], ["delegation is bounded and revocable"]),
        facet("provider_claim", [r"\b(provider (claim|offer|qualification|capability)|vendor (claim|offer|qualification)|service capability claim)\w*\b"], ["provider claims require independent qualification"]),
        facet("evidence_scoped_trust", [r"\b(claim.evidence|evidence strength|trust evidence|attestation trust|credential proof|defeater)\w*\b"], ["trust conclusion is scoped to exact evidence and defeaters"]),
    ]},
    {"axis": "effect_boundary", "question": "Is the contract pure, an effect proposal, or an executor?", "non_collapse": ["pure decision is not effect", "intent is not attempt", "observation is not accepted outcome"], "facets": [
        facet("pure_no_io", [], ["ambient clock randomness filesystem network environment and mutable global state are forbidden"]),
        facet("pure_effect_intents", [], ["the core emits intents but performs no external effect"]),
        facet("effectful_runtime", [], ["attempt lifecycle cancellation partial failure and recovery are total states"]),
        facet("ffi_boundary", [], ["layout ownership lifetime panic and callback rules are explicit"]),
        facet("generated_boundary", [], ["generator version inputs and digest are evidence, not semantic authority"]),
        facet("unresolved_refuse", [], ["no executable surface is generated before boundary adjudication"]),
    ]},
    {"axis": "representation", "question": "Which semantic, logical, wire, byte or physical layer is owned?", "non_collapse": ["format is not semantic type", "schema valid is not domain valid", "DTO is not domain object", "roundtrip is scoped to a preservation set"], "facets": [
        facet("semantic_native", [r"\b(semantic|domain model|value object|aggregate)\w*\b"], ["semantic core imports no provider DTO"]),
        facet("published_language_or_profile", [r"\b(profile|standard|published language|implementation guide)\w*\b"], ["profile conformance is editioned and authority-scoped"]),
        facet("logical_schema", [r"\b(schema|type system|logical type|field)\w*\b"], ["logical schema cannot silently acquire business meaning"]),
        facet("wire_protocol_or_dto", [r"\b(protocol|wire|dto|request|response|message)\w*\b"], ["wire compatibility and semantic compatibility are distinct"]),
        facet("encoded_bytes_or_container", [r"\b(codec|encode|decode|bytes|file format|container|compression)\w*\b"], ["malformed input and resource bombs refuse"]),
        facet("physical_layout", [r"\b(layout|columnar|row oriented|page|block|segment|index)\w*\b"], ["physical optimization cannot redefine logical truth"]),
        facet("provider_native", [r"\b(provider dto|provider native|vendor api|vendor sdk|provider sdk)\w*\b"], ["provider vocabulary stays behind an anti-corruption boundary"]),
    ]},
    {"axis": "composition_algebra", "question": "How do values, decisions or behaviors compose?", "non_collapse": ["merge is not overwrite", "join is not union", "workflow sequence is not commutative", "optimization is not policy"], "facets": [
        facet("set_or_lattice", [r"\b(union|intersection|set|lattice|meet|join|monotonic)\w*\b"], ["identity zero order and conflict laws are explicit"]),
        facet("relational", [r"\b(relational|join|group by|projection|predicate)\w*\b"], ["bag set null and ordering semantics are explicit"]),
        facet("graph", [r"\b(graph|path|travers|reachab)\w*\b"], ["composition preserves direction and edge semantics"]),
        facet("sequential_or_process", [r"\b(sequence|workflow|pipeline|process|chain)\w*\b"], ["ordering compensation and interruption are explicit"]),
        facet("parallel_or_distributed", [r"\b(parallel|distributed|concurrent|fan.out|fan.in)\w*\b"], ["race merge and consistency laws are explicit"]),
        facet("objective_and_constraints", [r"\b(objective|constraint|solver|optimi[sz])\w*\b"], ["objective policy and feasibility evidence are explicit"]),
        facet("policy_precedence", [r"\b(precedence|override|deny.overrides|conflict resolution)\w*\b"], ["conflicting decisions have a total adjudication outcome"]),
    ]},
    {"axis": "compatibility_and_evolution", "question": "What may change while which consumers remain valid?", "non_collapse": ["source compatibility is not behavioral compatibility", "upcast is not historical truth", "migration is not aliasing"], "facets": [
        facet("semantic_edition", [r"\b(semantic edition|meaning change|edition)\w*\b"], ["semantic compatibility relation is explicit"]),
        facet("schema_or_wire", [r"\b(schema compatibility|wire compatibility|backward|forward compatible)\w*\b"], ["reader and writer compatibility directions are distinct"]),
        facet("behavioral", [r"\b(behavioral compatibility|behavior edition|law compatibility|refusal precedence change)\w*\b"], ["new success and new refusal can both be breaking"]),
        facet("provider_capability", [r"\b(capability profile|provider edition|version skew)\w*\b"], ["capability freshness and negotiation are explicit"]),
        facet("migration_or_upcast", [r"\b(migration|upcast|backfill|transform|rollout)\w*\b"], ["loss residual and historical replay are explicit"]),
        facet("decommission_or_exit", [r"\b(decommission|sunset|supplier exit|portability|removal seam)\w*\b"], ["old identity disposition and in-flight work are explicit"]),
    ]},
    {"axis": "resources_and_failure", "question": "Which finite budgets and failure states bound execution?", "non_collapse": ["timeout is not cancellation", "overload is not provider failure", "partial failure is not success"], "facets": [
        facet("finite_budget", [r"\b(resource budget|finite|limit|bounded)\w*\b"], ["budget exhaustion refuses rather than weakens semantics"]),
        facet("deadline_or_timeout", [r"\b(deadline|timeout)\w*\b"], ["deadline source and timeout outcome are explicit"]),
        facet("capacity_or_quota", [r"\b(capacity|quota|rate limit|admission)\w*\b"], ["admission and execution completion are distinct"]),
        facet("backpressure_or_overload", [r"\b(backpressure|overload|load shed|queue full)\w*\b"], ["overload behavior is bounded and observable"]),
        facet("cancellation", [r"\b(cancel|cancellation|abort)\w*\b"], ["requested and observed cancellation are distinct"]),
        facet("partial_or_partition_failure", [r"\b(partial failure|partition|failover|degraded)\w*\b"], ["partial outcomes enumerate completed and residual work"]),
        facet("retry_and_idempotency", [r"\b(retry|idempoten|dedup)\w*\b"], ["idempotency scope key and retention window are explicit"]),
    ]},
    {"axis": "evidence_and_conformance", "question": "What evidence can establish which bounded claim?", "non_collapse": ["test pass is not product acceptance", "benchmark is not universal performance", "receipt is not truth"], "facets": [
        facet("law_or_property_oracle", [r"\b(property test|law oracle|invariant oracle|algebraic propert)\w*\b"], ["oracle edition and quantified domain are explicit"]),
        facet("model_or_state_oracle", [r"\b(model test|state machine|model check)\w*\b"], ["model abstraction and coverage limits are explicit"]),
        facet("differential_oracle", [r"\b(differential|independent implementation|cross.provider)\w*\b"], ["shared implementation ancestry cannot prove independence"]),
        facet("fuzz_or_adversarial", [r"\b(fuzz|mutation|negative twin|adversarial|fault injection)\w*\b"], ["generator and shrinking evidence are retained"]),
        facet("runtime_observation", [r"\b(observation|telemetry|metric|trace|log)\w*\b"], ["observation scope and missing telemetry are explicit"]),
        facet("receipt_or_attestation", [r"\b(receipt|attestation|signature|proof)\w*\b"], ["receipt binds exact intent occurrence and evidence scope"]),
        facet("benchmark_or_statistical", [r"\b(benchmark|confidence interval|sample|statistical)\w*\b"], ["workload population environment and uncertainty are explicit"]),
    ]},
    {"axis": "privacy_security_safety", "question": "Which trust boundary, purpose, harm or secrecy constraints apply?", "non_collapse": ["authentication is not authorization", "encryption is not consent", "retention is not availability", "safe failure is not silent degradation"], "facets": [
        facet("confidentiality_or_secret", [r"\b(confidential|secret|encrypt|key management|token)\w*\b"], ["plaintext exposure boundaries and key purpose are explicit"]),
        facet("purpose_or_consent", [r"\b(purpose|consent|lawful basis|use limitation)\w*\b"], ["purpose is evaluated per use, not inherited from possession"]),
        facet("residency_or_locality", [r"\b(residency|locality|region|jurisdiction)\w*\b"], ["data, key, processing and control-plane locality are distinct"]),
        facet("retention_or_erasure", [r"\b(retention|erase|erasure|delete|right to be forgotten)\w*\b"], ["logical deletion physical reclamation and proof are distinct"]),
        facet("integrity_or_provenance", [r"\b(integrity|provenance|signature|digest|tamper)\w*\b"], ["integrity does not prove source truth"]),
        facet("hazard_or_fail_safe", [r"\b(hazard|safety|fail.safe|harm|risk control)\w*\b"], ["unsafe uncertainty refuses or enters an explicit degraded state"]),
        facet("least_privilege", [r"\b(least privilege|permission|scope|credential|access control)\w*\b"], ["grants are minimal revocable and purpose-bound"]),
    ]},
]


# A facet is a question/module, not automatically a library. These curated bindings resolve
# high-leverage horizontal meanings to already-inventoried foundations. Unlisted facets remain
# domain/family constitution slots until a separate owner is proved necessary.
FACET_BINDINGS: dict[str, dict[str, Any]] = {
    "identity_and_equality.opaque_identity": {"kind": "IMPORT_FOUNDATION", "refs": ["library.csp.identity.scoped-identifier", "library.csp.identity.namespace-registry"]},
    "identity_and_equality.value_equality": {"kind": "DOMAIN_PARAMETER_OVER_FOUNDATION", "refs": ["library.csp.identity.scoped-identifier"]},
    "identity_and_equality.canonical_equivalence": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.identity.canonicalization", "library.san_canonical"]},
    "identity_and_equality.versioned_identity": {"kind": "IMPORT_FOUNDATION", "refs": ["library.csp.identity.version-identity"]},
    "identity_and_equality.occurrence_identity": {"kind": "DOMAIN_PARAMETER_OVER_FOUNDATION", "refs": ["library.csp.identity.scoped-identifier"]},
    "identity_and_equality.content_addressed": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.san_content_identity", "library.san_integrity"]},

    "time.event_time": {"kind": "DOMAIN_ROLE_OVER_FOUNDATION", "refs": ["library.csp.time.instant-core"]},
    "time.recording_or_processing_time": {"kind": "DOMAIN_ROLE_OVER_FOUNDATION", "refs": ["library.csp.time.instant-core"]},
    "time.validity_time": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.time.instant-core", "library.csp.time.interval-algebra"]},
    "time.bitemporal": {"kind": "IMPORT_FOUNDATION", "refs": ["library.csp.time.bitemporal-ledger"]},
    "time.interval_or_window": {"kind": "IMPORT_FOUNDATION", "refs": ["library.csp.time.interval-algebra"]},
    "time.deadline_or_timeout": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.time.instant-core", "library.csp.time.duration-core", "library.runtime-resource.deadline-cancellation"]},
    "time.ttl_or_expiry": {"kind": "DOMAIN_LIFECYCLE_OVER_FOUNDATION", "refs": ["library.csp.time.instant-core", "library.csp.time.duration-core"]},
    "time.schedule_or_calendar": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.time.recurrence", "library.csp.time.business-calendar", "library.csp.time.calendar-period"]},

    "state_and_change.immutable_value": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.value_type_system"]},
    "state_and_change.append_only_event": {"kind": "DOMAIN_EVENT_PROFILE", "refs": []},
    "state_and_change.lifecycle_transition": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.lifecycle_reducer"]},
    "state_and_change.versioned_mutation": {"kind": "DOMAIN_CONCURRENCY_PROFILE", "refs": ["library.csp.identity.version-identity"]},
    "state_and_change.snapshot_and_delta": {"kind": "DOMAIN_STATE_PROFILE", "refs": ["archetype.contract.lifecycle_reducer"]},
    "state_and_change.compensation_or_reversal": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.decision.compensation", "archetype.contract.lifecycle_reducer"]},

    "partiality_and_uncertainty.optional_missing_null": {"kind": "IMPORT_FOUNDATION", "refs": ["library.csp.quantity.partial-information"]},
    "partiality_and_uncertainty.three_or_multi_valued": {"kind": "DOMAIN_PARAMETER_OVER_FOUNDATION", "refs": ["library.csp.quantity.partial-information"]},
    "partiality_and_uncertainty.probabilistic": {"kind": "IMPORT_FOUNDATION", "refs": ["library.csp.quantity.probability-core"]},
    "partiality_and_uncertainty.interval_or_bound": {"kind": "DOMAIN_PARAMETER_OVER_FOUNDATION", "refs": ["library.csp.quantity.uncertainty-propagation"]},
    "partiality_and_uncertainty.approximate_or_lossy": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.quantity.uncertainty-propagation", "library.san_loss_contract"]},
    "partiality_and_uncertainty.unknown_completion": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.runtime-resource.attempt-state", "library.csp.decision.effect-port"]},

    "authority_and_trust.issuer_or_source_authority": {"kind": "DOMAIN_AUTHORITY_OVER_FOUNDATION", "refs": ["library.csp.authority.authority-scope", "library.csp.authority.issuance"]},
    "authority_and_trust.policy_decision": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.authority.policy-algebra", "library.csp.authority.policy-decision"]},
    "authority_and_trust.delegation_or_approval": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.authority.delegation-graph", "library.csp.authority.approval-ledger"]},
    "authority_and_trust.provider_claim": {"kind": "EVIDENCE_QUALIFICATION_PROFILE", "refs": ["library.lpe.attestation-core", "library.lpe.evidence-evaluation"]},
    "authority_and_trust.evidence_scoped_trust": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.lpe.claim-argument-core", "library.lpe.evidence-evaluation"]},

    "effect_boundary.pure_no_io": {"kind": "STRUCTURAL_EFFECT_CONSTRAINT", "refs": []},
    "effect_boundary.pure_effect_intents": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["archetype.contract.effect_port", "library.csp.decision.effect-port"]},
    "effect_boundary.effectful_runtime": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.runtime_mechanism"]},
    "effect_boundary.ffi_boundary": {"kind": "STRUCTURAL_EFFECT_CONSTRAINT", "refs": []},
    "effect_boundary.generated_boundary": {"kind": "STRUCTURAL_EFFECT_CONSTRAINT", "refs": []},
    "effect_boundary.unresolved_refuse": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.boundary_unresolved"]},

    "representation.semantic_native": {"kind": "DOMAIN_CONSTITUTION_SLOT", "refs": []},
    "representation.published_language_or_profile": {"kind": "DOMAIN_PROFILE_OVER_FOUNDATION", "refs": ["library.schema_registry.artifact_profile"]},
    "representation.logical_schema": {"kind": "DOMAIN_SCHEMA_OVER_FOUNDATION", "refs": ["library.data_contract.data_schema_binding"]},
    "representation.wire_protocol_or_dto": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.san_wire_schema", "library.cp.protocol_codec"]},
    "representation.encoded_bytes_or_container": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.san_codec_kernel", "library.san_carrier", "library.san_loss_contract"]},
    "representation.physical_layout": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.san_layout", "library.san_nested_layout"]},
    "representation.provider_native": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.provider_adapter"]},

    "compatibility_and_evolution.semantic_edition": {"kind": "DOMAIN_COMPATIBILITY_RELATION", "refs": ["library.csp.identity.version-identity"]},
    "compatibility_and_evolution.schema_or_wire": {"kind": "IMPORT_FOUNDATION", "refs": ["library.schema_registry.compatibility"]},
    "compatibility_and_evolution.behavioral": {"kind": "DOMAIN_COMPATIBILITY_RELATION", "refs": []},
    "compatibility_and_evolution.provider_capability": {"kind": "PROVIDER_QUALIFICATION_PROFILE", "refs": ["archetype.contract.provider_adapter"]},
    "compatibility_and_evolution.migration_or_upcast": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.schema_registry.migration_lifecycle", "archetype.contract.planner_compiler_pass"]},
    "compatibility_and_evolution.decommission_or_exit": {"kind": "DOMAIN_LIFECYCLE_PROFILE", "refs": ["archetype.contract.lifecycle_reducer"]},

    "resources_and_failure.finite_budget": {"kind": "IMPORT_FOUNDATION", "refs": ["library.runtime-resource.budget-precharge"]},
    "resources_and_failure.deadline_or_timeout": {"kind": "IMPORT_FOUNDATION", "refs": ["library.runtime-resource.deadline-cancellation"]},
    "resources_and_failure.capacity_or_quota": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.runtime-resource.admission", "library.runtime-resource.quota-ledger"]},
    "resources_and_failure.backpressure_or_overload": {"kind": "IMPORT_FOUNDATION", "refs": ["library.runtime-resource.backpressure"]},
    "resources_and_failure.cancellation": {"kind": "IMPORT_FOUNDATION", "refs": ["library.runtime-resource.deadline-cancellation"]},
    "resources_and_failure.partial_or_partition_failure": {"kind": "RUNTIME_FAILURE_PROFILE", "refs": ["library.runtime-resource.attempt-state", "library.runtime-resource.runtime-receipts"]},
    "resources_and_failure.retry_and_idempotency": {"kind": "DOMAIN_ATTEMPT_PROFILE", "refs": ["library.runtime-resource.attempt-state"]},

    "evidence_and_conformance.law_or_property_oracle": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.conformance_oracle"]},
    "evidence_and_conformance.model_or_state_oracle": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.conformance_oracle"]},
    "evidence_and_conformance.differential_oracle": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.conformance_oracle"]},
    "evidence_and_conformance.fuzz_or_adversarial": {"kind": "IMPORT_ARCHETYPE", "refs": ["archetype.contract.conformance_oracle"]},
    "evidence_and_conformance.runtime_observation": {"kind": "EVIDENCE_PROFILE", "refs": ["library.telemetry.observation_reduction"]},
    "evidence_and_conformance.receipt_or_attestation": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.lpe.runtime-receipt-core", "library.lpe.attestation-core"]},
    "evidence_and_conformance.benchmark_or_statistical": {"kind": "DOMAIN_EVIDENCE_PROFILE", "refs": ["library.csp.quantity.uncertainty-propagation"]},

    "privacy_security_safety.confidentiality_or_secret": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.spt.secret_handles", "library.spt.crypto_types"]},
    "privacy_security_safety.purpose_or_consent": {"kind": "IMPORT_FOUNDATION", "refs": ["library.spt.privacy_vocabulary", "library.spt.use_policy_compiler"]},
    "privacy_security_safety.residency_or_locality": {"kind": "DOMAIN_POLICY_PROFILE", "refs": []},
    "privacy_security_safety.retention_or_erasure": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.spt.retention_calculus", "library.spt.deletion_provider"]},
    "privacy_security_safety.integrity_or_provenance": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.san_integrity", "library.lpe.provenance-assertion"]},
    "privacy_security_safety.hazard_or_fail_safe": {"kind": "DOMAIN_SAFETY_PROFILE", "refs": []},
    "privacy_security_safety.least_privilege": {"kind": "COMPOSE_FOUNDATIONS", "refs": ["library.csp.authority.entitlement", "library.spt.policy_evaluator"]},
}

SEMANTIC_PHASES = [
    ("phase1_subject_and_grain", ["semantic_object", "identity_and_equality", "grain_and_cardinality"]),
    ("phase2_dynamics_and_information", ["state_and_change", "time", "order_and_topology", "partiality_and_uncertainty"]),
    ("phase3_authority_effect_and_safety", ["authority_and_trust", "privacy_security_safety", "effect_boundary"]),
    ("phase4_representation_and_evolution", ["representation", "compatibility_and_evolution"]),
    ("phase5_behavior_resources_and_proof", ["semantic_role", "composition_algebra", "resources_and_failure", "evidence_and_conformance"]),
]


def searchable_text(library: dict[str, Any]) -> str:
    # Deliberately exclude generic behavior laws, refusal templates, conformance boilerplate and
    # evidence references. Those repeat across source universes and would manufacture apparent
    # semantic coverage. Only the declared boundary and concrete public vocabulary may produce a
    # lexical discovery candidate.
    parts = [library.get("name", "")]
    parts.extend(library.get("scope", {}).get("responsibilities", []))
    for operation in library.get("api_contract", {}).get("operations", []):
        parts.extend([operation.get("name", ""), *operation.get("input_types", []), operation.get("output_type", "")])
    for public_type in library.get("api_contract", {}).get("types", []):
        parts.append(public_type.get("name", ""))
    return " ".join(parts).lower().replace("_", " ").replace("-", " ")


def build() -> dict[str, Any]:
    proposals = rows(GENERATION / "library-instance-proposals.jsonl")
    closure_items = {row["library_ref"]: row for row in rows(REGISTRY / "exact_api_closure/closure-queue.jsonl")}
    libraries = {row["library_id"]: row for row in rows(REGISTRY / "library-contributions.jsonl")}
    archetype_refs = {row["archetype_id"] for row in rows(GENERATION / "contract-archetypes.jsonl")}
    ontology = {
        "record_kind": "semantic_decomposition_ontology",
        "ontology_id": "ontology.library-semantic-axes.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "CONTROLLED_FACET_VOCABULARY_NOT_DOMAIN_AUTHORITY",
        "axes": AXES,
        "laws": [
            "Axes are orthogonal questions, not bounded contexts, products, packages or ownership claims.",
            "A library may select zero, one or several facets on an axis; zero remains explicit unresolved work.",
            "Pattern matches are discovery candidates and never establish applicability or semantic truth.",
            "Family constitutions may ratify shared facet modules; each library records applicability and exceptions.",
            "Only owner-published source contracts can close canonical exact-API gaps.",
        ],
    }
    realizations = []
    for axis in AXES:
        for candidate in axis["facets"]:
            key = f"{axis['axis']}.{candidate['facet']}"
            binding = FACET_BINDINGS.get(key, {"kind": "DOMAIN_CONSTITUTION_SLOT_NOT_LIBRARY", "refs": []})
            refs = binding["refs"]
            for ref in refs:
                assert ref in libraries or ref in archetype_refs, (key, ref)
            realizations.append({
                "record_kind": "semantic_facet_realization",
                "realization_id": "realization.semantic-facet." + key.replace("_", "-"),
                "edition": 1,
                "status": "CANDIDATE_OWNERSHIP_RESOLUTION_NOT_EXACT_CONTRACT",
                "axis": axis["axis"],
                "facet": candidate["facet"],
                "realization_kind": binding["kind"],
                "foundation_or_archetype_refs": refs,
                "domain_overlay_required": binding["kind"] not in {"IMPORT_FOUNDATION", "IMPORT_ARCHETYPE"},
                "compiler_binding_rule": "Bind by exact semantic identity, edition, laws and guarantees; never by facet label, package name or provider name.",
                "anti_explosion_law": "This facet does not create a new library unless removal, substitution, independent ownership and unrelated-vertical tests prove a separate boundary.",
            })
    realization_by_key = {(row["axis"], row["facet"]): row for row in realizations}
    evidence_claims = [
        {
            "record_kind": "semantic_foundation_evidence_claim",
            "claim_id": "claim.semantic-foundation.uri-comparison-is-purpose-scoped",
            "source_ref": "source.csp.ietf-rfc3986",
            "source_registry_path": "research/domain_atlas/universes/core_semantic_primitives/sources.jsonl",
            "url": "https://www.rfc-editor.org/rfc/rfc3986.html",
            "bounded_claim": "RFC 3986 defines a purpose- and scheme-sensitive comparison ladder; URI comparison may establish scoped equivalence but cannot generally establish that differently written identifiers denote different resources.",
            "supports_realization_refs": [
                realization_by_key[("identity_and_equality", "opaque_identity")]["realization_id"],
                realization_by_key[("identity_and_equality", "canonical_equivalence")]["realization_id"],
            ],
            "authority_limit": "Normative for URI syntax and comparison only; it does not define enterprise subject identity, entity resolution or historical continuity.",
        },
        {
            "record_kind": "semantic_foundation_evidence_claim",
            "claim_id": "claim.semantic-foundation.temporal-carriers-need-domain-roles",
            "source_ref": "source.csp.w3c-owl-time",
            "source_registry_path": "research/domain_atlas/universes/core_semantic_primitives/sources.jsonl",
            "url": "https://www.w3.org/TR/owl-time/",
            "bounded_claim": "OWL-Time distinguishes temporal entities including instants, intervals, durations and temporal reference systems; applications must still declare whether a carrier denotes occurrence, observation, validity, recording, processing or decision time.",
            "supports_realization_refs": [
                realization_by_key[("time", "event_time")]["realization_id"],
                realization_by_key[("time", "validity_time")]["realization_id"],
                realization_by_key[("time", "recording_or_processing_time")]["realization_id"],
            ],
            "authority_limit": "The ontology defines temporal vocabulary and relations, not application clock authority, database bitemporality policy, lateness or correction semantics.",
        },
        {
            "record_kind": "semantic_foundation_evidence_claim",
            "claim_id": "claim.semantic-foundation.policy-decision-is-not-enforcement",
            "source_ref": "source.csp.oasis-xacml",
            "source_registry_path": "research/domain_atlas/universes/core_semantic_primitives/sources.jsonl",
            "url": "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-en.html",
            "bounded_claim": "XACML separates policy administration, information, decision and enforcement roles and preserves Permit, Deny, Indeterminate and NotApplicable through explicit combining behavior.",
            "supports_realization_refs": [
                realization_by_key[("authority_and_trust", "policy_decision")]["realization_id"],
                realization_by_key[("partiality_and_uncertainty", "three_or_multi_valued")]["realization_id"],
            ],
            "authority_limit": "XACML governs its authorization processing model; it does not prove policy issuer authority, resource truth, effect completion, consent or business acceptance.",
        },
        {
            "record_kind": "semantic_foundation_evidence_claim",
            "claim_id": "claim.semantic-foundation.telemetry-signals-are-observations",
            "source_ref": "source.telemetry.otel.overview",
            "source_registry_path": "research/domain_atlas/universes/telemetry_signals/sources.jsonl",
            "url": "https://opentelemetry.io/docs/specs/otel/overview/",
            "bounded_claim": "OpenTelemetry defines independently functioning trace, metric, log and baggage signals over shared context; their resource and signal identities describe telemetry attribution rather than enterprise master identity or business truth.",
            "supports_realization_refs": [realization_by_key[("evidence_and_conformance", "runtime_observation")]["realization_id"]],
            "authority_limit": "Normative for OpenTelemetry signals and data models only; telemetry presence, absence or correlation does not prove causality, completeness, service health or domain-event truth.",
        },
        {
            "record_kind": "semantic_foundation_evidence_claim",
            "claim_id": "claim.semantic-foundation.schema-assertion-is-not-domain-validity",
            "source_ref": "source.schema-contract.jsonschema.core.2020-12",
            "source_registry_path": "research/domain_atlas/universes/schema_data_contract_governance/sources.jsonl",
            "url": "https://json-schema.org/draft/2020-12/json-schema-core",
            "bounded_claim": "JSON Schema defines dialects, vocabularies, assertions, annotations and applicators over JSON instances; an assertion pass covers only constraints present in the selected schema and vocabulary support.",
            "supports_realization_refs": [
                realization_by_key[("representation", "published_language_or_profile")]["realization_id"],
                realization_by_key[("representation", "logical_schema")]["realization_id"],
            ],
            "authority_limit": "JSON Schema validity does not establish reader/writer compatibility, source truth, business validity, semantic substitutability or authorization.",
        },
        {
            "record_kind": "semantic_foundation_evidence_claim",
            "claim_id": "claim.semantic-foundation.physical-layout-is-not-domain-semantics",
            "source_ref": "source.schema-mapping.arrow.columnar.1.5",
            "source_registry_path": "research/domain_atlas/universes/schema_mapping_translation/sources.jsonl",
            "url": "https://arrow.apache.org/docs/format/Columnar.html",
            "bounded_claim": "Apache Arrow defines language-neutral arrays, parametric data types, buffers and physical memory layouts optimized for analytical access; physical layout compatibility remains distinct from application semantic equivalence.",
            "supports_realization_refs": [
                realization_by_key[("representation", "logical_schema")]["realization_id"],
                realization_by_key[("representation", "physical_layout")]["realization_id"],
            ],
            "authority_limit": "The Arrow format does not define application meaning, master identity, mutation coordination, business validity or lossless mapping to unrelated carriers.",
        },
    ]
    signatures = []
    for proposal in proposals:
        library = libraries[proposal["library_ref"]]
        text = searchable_text(library)
        selections = []
        for axis in AXES:
            matches = []
            if axis["axis"] == "effect_boundary":
                boundary = library["effects"]["boundary"]
                matches = [{"facet": boundary, "evidence": ["library.effects.boundary"], "confidence": "EXPLICIT_SOURCE_FIELD"}]
            else:
                for candidate in axis["facets"]:
                    hit_patterns = [pattern for pattern in candidate["discovery_patterns"] if re.search(pattern, text)]
                    if hit_patterns:
                        matches.append({
                            "facet": candidate["facet"],
                            "evidence": hit_patterns,
                            "confidence": "LEXICAL_DISCOVERY_ONLY",
                            "realization_ref": realization_by_key[(axis["axis"], candidate["facet"])]["realization_id"],
                        })
            if axis["axis"] == "effect_boundary":
                matches[0]["realization_ref"] = realization_by_key[(axis["axis"], matches[0]["facet"])]["realization_id"]
            selections.append({
                "axis": axis["axis"],
                "status": "EXPLICIT_CANDIDATE_SET_UNRATIFIED" if matches else "UNRESOLVED_OWNER_INPUT_REQUIRED",
                "candidate_facets": matches,
                "owner_must": "accept, reject or replace every candidate and record any missing facet with bounded evidence",
            })
        signatures.append({
            "record_kind": "library_semantic_axis_signature_candidate",
            "signature_id": "signature.semantic." + proposal["library_ref"].removeprefix("library."),
            "edition": 1,
            "status": "DISCOVERY_SIGNATURE_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP",
            "library_ref": proposal["library_ref"],
            "source_gap_ref": proposal["source_gap_ref"],
            "family_id": proposal["family_id"],
            "semantic_owner_refs": proposal["semantic_owner_refs"],
            "archetype_refs": [proposal["primary_archetype_proposal"], *proposal["alternate_archetype_proposals"]],
            "axis_selections": selections,
            "ratification_rule": "Owner ratifies the complete axis vector; absence of a lexical candidate is unresolved rather than inapplicable.",
        })

    by_family_axis: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for signature in signatures:
        for selection in signature["axis_selections"]:
            by_family_axis[(signature["family_id"], selection["axis"])].append({
                "signature_ref": signature["signature_id"],
                "candidate_facets": [row["facet"] for row in selection["candidate_facets"]],
                "status": selection["status"],
            })
    review_packages = []
    for ordinal, ((family_id, axis), members) in enumerate(sorted(by_family_axis.items()), start=1):
        facet_counts = Counter(facet for member in members for facet in member["candidate_facets"])
        review_packages.append({
            "record_kind": "family_semantic_axis_review_package",
            "work_package_id": f"work.semantic-axis.{ordinal:04d}",
            "edition": 1,
            "status": "OWNER_RATIFICATION_REQUIRED",
            "family_id": family_id,
            "axis": axis,
            "library_count": len(members),
            "member_signatures": members,
            "candidate_facet_counts": dict(sorted(facet_counts.items())),
            "review_method": [
                "ratify shared facet modules once for the family",
                "record per-library applicability attestations",
                "author only library-specific additions refusals and exceptions",
                "test non-collapse laws and cross-owner collisions",
            ],
            "completion_effect": "Freezes one family-axis constitution module; no canonical gap closes until exact source contracts import it.",
        })
    signature_to_library = {row["signature_id"]: row["library_ref"] for row in signatures}
    axis_leverage = {
        "identity_and_equality": 80, "time": 80, "state_and_change": 75,
        "partiality_and_uncertainty": 75, "authority_and_trust": 75,
        "representation": 70, "grain_and_cardinality": 65, "order_and_topology": 65,
        "resources_and_failure": 65, "compatibility_and_evolution": 60,
        "composition_algebra": 60, "evidence_and_conformance": 55,
        "privacy_security_safety": 55, "semantic_object": 50, "semantic_role": 50,
        "effect_boundary": 40,
    }
    research_queue = []
    for package in review_packages:
        library_refs = [signature_to_library[row["signature_ref"]] for row in package["member_signatures"]]
        items = [closure_items[ref] for ref in library_refs]
        unresolved_refs = [
            signature_to_library[row["signature_ref"]]
            for row in package["member_signatures"]
            if row["status"] == "UNRESOLVED_OWNER_INPUT_REQUIRED"
        ]
        band_counts = Counter(item["priority_band"] for item in items)
        product_refs = sorted({ref for item in items for ref in item["product_refs"]})
        score = (
            sum(item["priority_score"] for item in items)
            + 100 * band_counts.get("P0_PRODUCT_AND_VERTICAL", 0)
            + 35 * band_counts.get("P1_PRODUCT", 0)
            + 12 * len(unresolved_refs)
            + axis_leverage[package["axis"]]
        )
        research_queue.append({
            "record_kind": "semantic_axis_research_queue_item",
            "queue_id": package["work_package_id"].replace("work.semantic-axis", "queue.semantic-axis"),
            "edition": 1,
            "status": "OPEN_FAMILY_AXIS_RESEARCH_AND_RATIFICATION",
            "work_package_ref": package["work_package_id"],
            "family_id": package["family_id"],
            "axis": package["axis"],
            "library_count": len(library_refs),
            "unresolved_library_count": len(unresolved_refs),
            "candidate_ratification_count": len(library_refs) - len(unresolved_refs),
            "unresolved_library_refs": unresolved_refs,
            "priority_band_counts": dict(sorted(band_counts.items())),
            "retained_product_refs": product_refs,
            "priority_score": score,
            "work_mode": "DISCOVER_AND_RATIFY" if unresolved_refs else "RATIFY_EXISTING_CANDIDATES",
            "research_contract": [
                "extract family vocabulary and explicit non-collapse distinctions from primary standards and original research",
                "separate universal carrier laws from family policy and library-local semantics",
                "adjudicate every lexical candidate and every unresolved member",
                "bind bounded claims, authority limits, counterexamples and conflicting sources",
                "freeze a versioned family-axis module and record per-library applicability or exception",
            ],
            "completion_law": "All members have owner-ratified facet applicability and exceptions; the result remains noncanonical until exact source contracts import the module.",
        })
    research_queue.sort(key=lambda row: (-row["priority_score"], row["queue_id"]))
    for rank, item in enumerate(research_queue, start=1):
        item["rank"] = rank
    queue_by_package = {row["work_package_ref"]: row for row in research_queue}
    axis_lanes = []
    for axis in (axis for _, axes in SEMANTIC_PHASES for axis in axes):
        packages = [row for row in review_packages if row["axis"] == axis]
        packages.sort(key=lambda row: (-queue_by_package[row["work_package_id"]]["priority_score"], row["work_package_id"]))
        axis_realizations = [row for row in realizations if row["axis"] == axis]
        axis_claim_refs = [claim["claim_id"] for claim in evidence_claims if any(ref in {item["realization_id"] for item in axis_realizations} for ref in claim["supports_realization_refs"])]
        axis_lanes.append({
            "record_kind": "semantic_axis_execution_lane",
            "lane_id": "lane.semantic-axis." + axis.replace("_", "-"),
            "edition": 1,
            "status": "PLANNED_INCOMPLETE",
            "axis": axis,
            "facet_realization_refs": [row["realization_id"] for row in axis_realizations],
            "bounded_evidence_claim_refs": axis_claim_refs,
            "family_work_package_refs_in_priority_order": [row["work_package_id"] for row in packages],
            "family_count": len(packages),
            "execution_model": "Freeze the global axis vocabulary/non-collapse/realization constitution once, then ratify independent family matrices in parallel and store only library exceptions.",
            "global_gate": "Every facet has a realization disposition, evidence scope or explicit evidence vacancy, and no facet label is treated as a library identity.",
            "family_gate": "Every family member has applicable, inapplicable, prohibited or unresolved status with evidence and exceptions.",
        })
    lane_by_axis = {row["axis"]: row for row in axis_lanes}
    execution_phases = []
    previous = []
    for ordinal, (name, axes) in enumerate(SEMANTIC_PHASES, start=1):
        phase_id = f"phase.semantic-axis.{ordinal}.{name.replace('_', '-')}"
        execution_phases.append({
            "record_kind": "semantic_axis_execution_phase",
            "phase_id": phase_id,
            "edition": 1,
            "status": "PLANNED_INCOMPLETE",
            "axis_lane_refs": [lane_by_axis[axis]["lane_id"] for axis in axes],
            "depends_on_phase_refs": previous[-1:] if previous else [],
            "parallelism": "Axis lanes in this phase and family attestations within each lane may proceed in parallel when ownership and evidence sources are independent.",
            "exit_gate": "All lanes freeze an editioned global constitution and every family matrix records applicability, exceptions, evidence vacancies and conflicts.",
        })
        previous.append(phase_id)
    unresolved = sum(selection["status"].startswith("UNRESOLVED") for signature in signatures for selection in signature["axis_selections"])
    candidate_cells = sum(bool(selection["candidate_facets"]) for signature in signatures for selection in signature["axis_selections"])
    coverage_by_axis = {}
    for axis in (row["axis"] for row in AXES):
        axis_selections = [selection for signature in signatures for selection in signature["axis_selections"] if selection["axis"] == axis]
        facets = Counter(candidate["facet"] for selection in axis_selections for candidate in selection["candidate_facets"])
        covered = sum(bool(selection["candidate_facets"]) for selection in axis_selections)
        coverage_by_axis[axis] = {
            "candidate_cells": covered,
            "unresolved_cells": len(axis_selections) - covered,
            "candidate_facet_occurrences": sum(facets.values()),
            "candidate_facet_counts": dict(sorted(facets.items())),
        }
    summary = {
        "program_id": "program.semantic-axis-decomposition.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "ACTIVE_INCOMPLETE",
        "completion_claim": False,
        "axes": len(AXES),
        "facet_modules": sum(len(axis["facets"]) for axis in AXES),
        "library_signatures": len(signatures),
        "axis_cells": len(signatures) * len(AXES),
        "candidate_cells": candidate_cells,
        "unresolved_cells": unresolved,
        "family_axis_review_packages": len(review_packages),
        "semantic_research_queue_items": len(research_queue),
        "semantic_axis_execution_lanes": len(axis_lanes),
        "semantic_axis_execution_phases": len(execution_phases),
        "facet_realizations": len(realizations),
        "realization_counts_by_kind": dict(sorted(Counter(row["realization_kind"] for row in realizations).items())),
        "facet_realizations_with_existing_refs": sum(bool(row["foundation_or_archetype_refs"]) for row in realizations),
        "bounded_primary_evidence_claims": len(evidence_claims),
        "coverage_by_axis": coverage_by_axis,
        "scaling_law": "Ratify reusable family-axis modules and store only per-library applicability and exceptions; never infer authority from lexical matches.",
    }
    return {"ontology": ontology, "realizations": realizations, "evidence_claims": evidence_claims, "signatures": signatures, "review_packages": review_packages, "research_queue": research_queue, "axis_lanes": axis_lanes, "execution_phases": execution_phases, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "semantic-axis-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "facet-realizations.jsonl": "".join(canonical(row) + "\n" for row in built["realizations"]),
        "foundation-evidence-claims.jsonl": "".join(canonical(row) + "\n" for row in built["evidence_claims"]),
        "library-semantic-signatures.jsonl": "".join(canonical(row) + "\n" for row in built["signatures"]),
        "family-axis-review-packages.jsonl": "".join(canonical(row) + "\n" for row in built["review_packages"]),
        "semantic-research-queue.jsonl": "".join(canonical(row) + "\n" for row in built["research_queue"]),
        "semantic-axis-lanes.jsonl": "".join(canonical(row) + "\n" for row in built["axis_lanes"]),
        "semantic-execution-phases.jsonl": "".join(canonical(row) + "\n" for row in built["execution_phases"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.semantic-axis-decomposition.v1", "as_of": AS_OF, "files": claims}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = build()["summary"]
    print(f"{'CHECK' if args.check else 'BUILD'} PASS semantic decomposition: {summary['library_signatures']} libraries x {summary['axes']} axes, {summary['facet_modules']} reusable facet modules, {summary['family_axis_review_packages']} family-axis packages, {summary['unresolved_cells']} unresolved cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
