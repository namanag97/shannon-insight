"""Authoring model for the application-behavior universe.

The records in this module are deliberately provider-neutral.  They describe a
candidate semantic contract surface for enterprise applications; they do not
claim that a framework, database, broker, workflow engine, or vertical domain
has been qualified against it.
"""

from __future__ import annotations

from typing import Any

AS_OF = "2026-08-27"
EDITION = 1
STATUS = "specified_candidate"


def _evidence(*source_ids: str) -> list[str]:
    return list(source_ids)


SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "source.application.json_schema",
        "title": "JSON Schema Core and Validation vocabularies, Draft 2020-12",
        "authority": "JSON Schema specification",
        "source_kind": "specification",
        "url": "https://json-schema.org/draft/2020-12/json-schema-core.html",
        "retrieved": AS_OF,
        "supports": [
            "machine-readable instance structure and validation vocabulary",
            "schema documents can describe required structure without supplying domain authority",
        ],
        "does_not_prove": [
            "business meaning",
            "runtime behavior or implementation qualification",
            "authorization or effect safety",
        ],
    },
    {
        "source_id": "source.application.openapi",
        "title": "OpenAPI Specification 3.2.0",
        "authority": "OpenAPI Initiative",
        "source_kind": "specification",
        "url": "https://spec.openapis.org/oas/v3.2.0.html",
        "retrieved": AS_OF,
        "supports": [
            "language-agnostic description of HTTP interfaces",
            "machine-readable discovery and interaction surface for a service",
        ],
        "does_not_prove": [
            "domain command/query meaning",
            "state transition correctness",
            "authorization or side-effect safety",
        ],
    },
    {
        "source_id": "source.application.http",
        "title": "HTTP Semantics, RFC 9110",
        "authority": "IETF HTTP Working Group",
        "source_kind": "standard",
        "url": "https://www.rfc-editor.org/rfc/rfc9110.html",
        "retrieved": AS_OF,
        "supports": [
            "transport-level safe and idempotent method semantics",
            "retry-relevant method properties are distinct from absence of all incidental effects",
        ],
        "does_not_prove": [
            "domain-level idempotency",
            "transactional atomicity",
            "authorization or business acceptance",
        ],
    },
    {
        "source_id": "source.application.cloudevents",
        "title": "CloudEvents Specification 1.0.x",
        "authority": "Cloud Native Computing Foundation CloudEvents project",
        "source_kind": "specification",
        "url": "https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md",
        "retrieved": AS_OF,
        "supports": [
            "event context attributes, source, id, type and serialization-independent envelope metadata",
            "event interoperability across protocols and formats",
        ],
        "does_not_prove": [
            "event processing guarantees",
            "domain meaning or consumer authorization",
            "delivery exactly-once behavior",
        ],
    },
    {
        "source_id": "source.application.scxml",
        "title": "State Chart XML (SCXML) 1.0",
        "authority": "W3C",
        "source_kind": "standard",
        "url": "https://www.w3.org/TR/scxml/",
        "retrieved": AS_OF,
        "supports": [
            "event-driven state transition notation",
            "explicit state configurations and transition processing",
        ],
        "does_not_prove": [
            "domain state ownership",
            "persistence durability",
            "effect authorization or workflow provider qualification",
        ],
    },
    {
        "source_id": "source.application.bpmn",
        "title": "Business Process Model and Notation (BPMN) 2.0.2",
        "authority": "Object Management Group",
        "source_kind": "specification",
        "url": "https://www.omg.org/spec/BPMN/2.0.2",
        "retrieved": AS_OF,
        "supports": [
            "business-process notation and workflow control-flow vocabulary",
        ],
        "does_not_prove": [
            "application aggregate invariants",
            "execution semantics of a specific engine",
            "authority to perform an effect",
        ],
    },
    {
        "source_id": "source.application.dmn",
        "title": "Decision Model and Notation (DMN) 1.4",
        "authority": "Object Management Group",
        "source_kind": "specification",
        "url": "https://www.omg.org/spec/DMN/1.4",
        "retrieved": AS_OF,
        "supports": [
            "decision logic and decision-table notation",
        ],
        "does_not_prove": [
            "who is authorized to decide",
            "the truth or quality of input facts",
            "automatic effect execution",
        ],
    },
    {
        "source_id": "source.application.prov_dm",
        "title": "PROV-DM: The PROV Data Model",
        "authority": "W3C",
        "source_kind": "standard",
        "url": "https://www.w3.org/TR/prov-dm/Overview.html",
        "retrieved": AS_OF,
        "supports": [
            "provenance distinction between entities, activities, agents and their relations",
            "usage, generation, communication, invalidation and collection relations for evidence graphs",
        ],
        "does_not_prove": [
            "truth of a recorded outcome",
            "independent assurance",
            "business authority or policy compliance",
        ],
    },
    {
        "source_id": "source.application.saga",
        "title": "Sagas",
        "authority": "Hector Garcia-Molina and Kenneth Salem, ACM SIGMOD 1987",
        "source_kind": "primary_paper",
        "url": "https://doi.org/10.1145/38713.38742",
        "retrieved": AS_OF,
        "supports": [
            "long-lived transaction decomposition into transactions and compensating transactions",
            "compensation is an explicit application strategy for partial execution",
        ],
        "does_not_prove": [
            "automatic rollback or atomicity",
            "semantic correctness of a compensation",
            "workflow-engine interoperability",
        ],
    },
    {
        "source_id": "source.application.states_language",
        "title": "Amazon States Language specification",
        "authority": "Amazon Web Services",
        "source_kind": "product_specification",
        "url": "https://states-language.net/spec.html",
        "retrieved": AS_OF,
        "supports": [
            "one concrete retry and catch representation for state-machine runtimes",
            "error matching, retry interval, attempt and backoff configuration concepts",
        ],
        "does_not_prove": [
            "portable workflow semantics",
            "domain retry policy",
            "compensation or effect authority",
        ],
    },
    {
        "source_id": "source.application.problem_details",
        "title": "Problem Details for HTTP APIs, RFC 9457",
        "authority": "IETF",
        "source_kind": "standard",
        "url": "https://www.rfc-editor.org/rfc/rfc9457.html",
        "retrieved": AS_OF,
        "supports": [
            "machine-readable error detail representation for HTTP interfaces",
        ],
        "does_not_prove": [
            "that a refusal is the correct domain decision",
            "retry safety",
            "state or effect semantics",
        ],
    },
]


def _common(record_id: str, *, lifecycle: list[str], time_roles: list[str], authority: str,
            resources: list[str], side_effects: str, invariants: list[str], refusals: list[str],
            evidence: list[str], status: str = STATUS) -> dict[str, Any]:
    return {
        "id": record_id,
        "edition": EDITION,
        "status": status,
        "completion_claim": False,
        "lifecycle": lifecycle,
        "time_model": {"roles": time_roles, "ambient_time_allowed": False, "clock_ref": None},
        "authority_model": authority,
        "resource_assumptions": resources,
        "side_effects": side_effects,
        "invariants": invariants,
        "refusals": refusals,
        "evidence_refs": evidence,
    }


CONTEXTS: list[dict[str, Any]] = []


def _context(cid: str, name: str, question: str, inside: list[str], outside: list[str],
             imports: list[str], exports: list[str], owner: str, evidence: list[str]) -> dict[str, Any]:
    row = _common(
        cid,
        lifecycle=["candidate", "adjudicated", "ratified", "superseded", "retired"],
        time_roles=["request_time", "effective_time", "recording_time", "observation_time"],
        authority="Application context owns contract meaning only; caller, policy and physical effect authorities remain external.",
        resources=["finite request payload", "bounded validation work", "explicit persistence/broker/runtime offers"],
        side_effects="semantic declarations are pure; execution side effects are represented as intents or observations",
        invariants=["one sovereign question per context", "imports do not transfer semantic ownership", "unresolved authority is a refusal"],
        refusals=["refuse provider-name dispatch", "refuse ambient resource access", "refuse silent cross-context meaning transfer"],
        evidence=evidence,
    )
    row.update({
        "context_id": cid,
        "name": name,
        "sovereign_question": question,
        "inside": inside,
        "outside": outside,
        "imports": imports,
        "exports": exports,
        "semantic_owner": owner,
        "required_adjudications": ["owner identity", "edition", "negative scope", "authority and time policy"],
    })
    CONTEXTS.append(row)


_context(
    "context.application.interaction", "Application Interaction Contract",
    "What typed command or query interaction may be accepted, refused, or observed at an application boundary?",
    ["command/query distinction", "request and response contract", "identity and correlation", "transport mapping", "refusal shape", "idempotency declaration"],
    ["business state ownership", "authorization decision", "persistence", "broker delivery", "UI product promise"],
    ["universe.data_type", "universe.operation", "universe.security_privacy_trust"],
    ["contract.application.command", "contract.application.query"],
    "authority.application.interaction",
    _evidence("source.application.openapi", "source.application.http", "source.application.json_schema", "source.application.problem_details"),
)
_context(
    "context.application.aggregate_state", "Application Aggregate State",
    "Which application-owned state transition preserves an invariant for one consistency identity and expected version?",
    ["aggregate identity", "state snapshot", "version", "invariant gate", "transition decision", "conflict classification"],
    ["database schema", "transaction isolation implementation", "business vocabulary authority", "effect execution", "analytics truth"],
    ["universe.data_type", "universe.persistence", "universe.security_privacy_trust"],
    ["contract.application.aggregate_state", "contract.application.state_transition"],
    "authority.application.aggregate_state",
    _evidence("source.application.scxml", "source.application.json_schema"),
)
_context(
    "context.application.workflow_coordination", "Application Workflow Coordination",
    "How does a long-lived application coordination instance advance, wait, retry, compensate, complete, fail, or become unknown?",
    ["workflow definition", "instance identity", "step state", "retry budget", "wait condition", "compensation relation", "terminal classification"],
    ["generic dataflow scheduling", "aggregate invariant ownership", "authorization", "physical effect execution", "product support lifecycle"],
    ["universe.pipeline_dataflow", "universe.operation", "universe.runtime_resource"],
    ["contract.application.workflow_instance", "contract.application.saga_compensation"],
    "authority.application.workflow_coordination",
    _evidence("source.application.scxml", "source.application.bpmn", "source.application.saga", "source.application.states_language"),
)
_context(
    "context.application.event_publication", "Application Event Publication",
    "What immutable application occurrence is emitted after a declared state decision, and what delivery evidence exists?",
    ["event identity", "event type and edition", "causal relation", "domain/integration distinction", "publication intent", "delivery observation"],
    ["transport protocol", "consumer processing", "schema registry authority", "business outcome", "exactly-once guarantee"],
    ["universe.data_type", "universe.pipeline_dataflow", "universe.lineage_provenance_evidence"],
    ["contract.application.domain_event", "contract.application.integration_event"],
    "authority.application.event_publication",
    _evidence("source.application.cloudevents", "source.application.prov_dm", "source.application.json_schema"),
)
_context(
    "context.application.projection", "Application Projection",
    "How is a derived read model declared, advanced, rebuilt, lagged, invalidated, and distinguished from source state?",
    ["projection identity", "source event/cut", "derivation edition", "checkpoint", "lag", "rebuild", "read consistency classification"],
    ["source-system authority", "analytical metric meaning", "database implementation", "query user interface", "business truth claim"],
    ["universe.pipeline_dataflow", "universe.persistence", "universe.consumption"],
    ["contract.application.projection"],
    "authority.application.projection",
    _evidence("source.application.json_schema", "source.application.prov_dm"),
)
_context(
    "context.application.effect_handoff", "Application Effect Handoff",
    "How is a proposed external effect separated from authorization, submission, physical execution, and receipt reconciliation?",
    ["effect intent", "target identity", "requested parameters", "authority reference", "executor handoff", "receipt status", "reconciliation"],
    ["policy authority", "human approval", "physical effect", "provider capability", "business outcome", "automatic compensation"],
    ["universe.security_privacy_trust", "universe.runtime_resource", "universe.lineage_provenance_evidence"],
    ["contract.application.effect_intent", "contract.application.effect_receipt"],
    "authority.application.effect_handoff",
    _evidence("source.application.prov_dm", "source.application.json_schema", "source.application.problem_details"),
)
_context(
    "context.application.execution_evidence", "Application Execution Evidence",
    "What was declared, attempted, observed, refused, retried, or left unknown for one application execution?",
    ["correlation", "attempt", "input/output digests", "state and effect receipts", "provenance links", "diagnostics", "evidence completeness"],
    ["independent audit", "truth of business outcome", "security approval", "runtime log retention policy", "customer acceptance"],
    ["universe.lineage_provenance_evidence", "universe.quality_reconciliation", "universe.consumption"],
    ["contract.application.execution_receipt"],
    "authority.application.execution_evidence",
    _evidence("source.application.prov_dm", "source.application.json_schema"),
)


def _contract(cid: str, owner: str, kind: str, definition: str, identity: list[str], states: list[str],
              evidence: list[str], *, imports: list[str], forbidden: list[str], time_roles: list[str]) -> dict[str, Any]:
    row = _common(
        cid,
        lifecycle=["declared", "validated", "accepted", "refused", "superseded", "retired"],
        time_roles=time_roles,
        authority="The owning application context defines contract semantics; external policy and effect authorities must be referenced, never inferred.",
        resources=["finite payload", "bounded state snapshot", "explicit clock/cut", "qualified or explicitly unqualified execution offer"],
        side_effects="contract values are inert; operations declare intent or observation when execution is involved",
        invariants=["identity is explicit", "edition is carried", "unknown and refusal are not success", "imported semantics retain their owner"],
        refusals=["missing identity", "unbounded payload or recursion", "implicit current time", "missing authority reference", "ambiguous state transition"],
        evidence=evidence,
    )
    row.update({
        "contract_id": cid,
        "owner_context_ref": owner,
        "kind": kind,
        "definition": definition,
        "identity_rules": identity,
        "lifecycle_states": states,
        "imports": imports,
        "forbidden_collapses": forbidden,
        "allowed_compositions": ["explicit reference with edition", "loss-aware crosswalk", "receipt-linked handoff"],
    })
    return row


CONTRACTS = [
    _contract("contract.application.command", "context.application.interaction", "request", "A requested state-changing interaction whose acceptance does not itself authorize an effect.", ["command_id", "command_type", "command_edition", "aggregate_ref", "request_id"], ["declared", "validated", "accepted", "rejected", "conflicted", "cancelled", "unknown"], _evidence("source.application.openapi", "source.application.http", "source.application.json_schema", "source.application.problem_details"), imports=["universe.data_type", "universe.operation", "universe.security_privacy_trust"], forbidden=["command equals event", "HTTP method proves domain intent", "accepted request equals committed state", "requester identity equals authorization"], time_roles=["requested_at", "effective_at", "recorded_at"]),
    _contract("contract.application.query", "context.application.interaction", "request", "A read interaction that declares its consistency/cut and must not request a state transition.", ["query_id", "query_type", "query_edition", "request_id", "read_cut"], ["declared", "validated", "executed", "refused", "partial", "unknown"], _evidence("source.application.openapi", "source.application.http", "source.application.json_schema", "source.application.problem_details"), imports=["universe.data_type", "universe.operation", "universe.consumption"], forbidden=["query equals projection", "read response equals current truth", "safe transport method proves no application-side audit or cache effect"], time_roles=["requested_at", "read_cut_at", "recorded_at"]),
    _contract("contract.application.aggregate_state", "context.application.aggregate_state", "state", "A versioned application consistency snapshot for one aggregate identity.", ["aggregate_ref", "state_edition", "state_version", "snapshot_digest"], ["unloaded", "loaded", "transition_proposed", "accepted", "rejected", "conflicted", "committed_observed", "unknown"], _evidence("source.application.scxml", "source.application.json_schema"), imports=["universe.data_type", "universe.persistence", "universe.security_privacy_trust"], forbidden=["aggregate equals table", "loaded equals authoritative persistence", "version conflict equals retry permission", "state equals analytical fact"], time_roles=["valid_at", "transition_at", "recorded_at", "observed_at"]),
    _contract("contract.application.state_transition", "context.application.aggregate_state", "transition", "A pure decision or explicit commit intent that maps one expected state version and command to an accepted or refused next state.", ["transition_id", "aggregate_ref", "from_version", "command_id", "transition_edition"], ["proposed", "accepted", "rejected", "conflicted", "committed_observed", "unknown"], _evidence("source.application.scxml", "source.application.json_schema"), imports=["universe.data_type", "universe.operation", "universe.persistence"], forbidden=["accepted decision equals durable commit", "state mutation without receipt", "retry after unknown without policy", "invariant bypass by caller"], time_roles=["decision_at", "effective_at", "commit_requested_at", "observed_at"]),
    _contract("contract.application.domain_event", "context.application.event_publication", "event", "An immutable application occurrence describing an accepted domain transition, distinct from its transport envelope.", ["event_id", "event_type", "event_edition", "aggregate_ref", "causation_ref", "occurrence_time"], ["formed", "accepted", "publication_proposed", "published_observed", "invalidated", "unknown"], _evidence("source.application.cloudevents", "source.application.json_schema", "source.application.prov_dm"), imports=["universe.data_type", "universe.lineage_provenance_evidence"], forbidden=["event equals command", "event equals transport delivery", "event schema proves consumer processing", "published equals business outcome"], time_roles=["occurred_at", "published_at", "recorded_at", "observed_at"]),
    _contract("contract.application.integration_event", "context.application.event_publication", "event", "A cross-boundary event envelope carrying a declared application event reference and delivery identity.", ["message_id", "source_ref", "event_type", "event_edition", "partition_or_order_key"], ["formed", "validated", "delivery_proposed", "delivered_observed", "duplicate_observed", "rejected", "unknown"], _evidence("source.application.cloudevents", "source.application.json_schema"), imports=["universe.data_type", "universe.pipeline_dataflow", "universe.lineage_provenance_evidence"], forbidden=["CloudEvents metadata equals domain meaning", "delivery equals processing", "message id equals business id", "duplicate observation equals data loss"], time_roles=["occurred_at", "sent_at", "received_at", "processed_at"]),
    _contract("contract.application.workflow_instance", "context.application.workflow_coordination", "workflow", "A long-lived coordination instance with explicit step state, retry budget, wait, compensation and terminal outcome classification.", ["workflow_id", "workflow_definition_edition", "instance_id", "correlation_ref"], ["defined", "ready", "running", "waiting", "retrying", "compensating", "completed", "failed", "cancelled", "unknown"], _evidence("source.application.scxml", "source.application.bpmn", "source.application.states_language"), imports=["universe.pipeline_dataflow", "universe.operation", "universe.runtime_resource"], forbidden=["workflow equals dataflow pipeline", "retry equals compensation", "failed equals compensated", "unknown equals failed"], time_roles=["started_at", "step_started_at", "retry_at", "deadline_at", "observed_at"]),
    _contract("contract.application.saga_compensation", "context.application.workflow_coordination", "workflow", "An explicit forward compensation action for a completed or partially completed saga step; it is not rollback.", ["saga_id", "step_id", "compensation_id", "forward_action_ref"], ["planned", "authorized", "proposed", "submitted", "observed", "rejected", "unknown"], _evidence("source.application.saga", "source.application.json_schema"), imports=["universe.operation", "universe.security_privacy_trust", "universe.runtime_resource"], forbidden=["compensation equals inverse in all domains", "compensation restores atomicity", "compensation without authority", "unknown equals successful undo"], time_roles=["forward_completed_at", "compensation_requested_at", "observed_at"]),
    _contract("contract.application.projection", "context.application.projection", "projection", "A derived read model with an explicit source cut, derivation edition, checkpoint and lag/rebuild classification.", ["projection_id", "projection_edition", "source_cut", "checkpoint", "materialization_digest"], ["declared", "building", "current", "lagging", "invalid", "rebuilding", "unknown"], _evidence("source.application.json_schema", "source.application.prov_dm"), imports=["universe.pipeline_dataflow", "universe.persistence", "universe.consumption"], forbidden=["projection equals source authority", "current means business truth", "lag hidden as success", "rebuild changes source events"], time_roles=["source_cut_at", "derived_at", "checkpoint_at", "observed_at"]),
    _contract("contract.application.effect_intent", "context.application.effect_handoff", "effect", "A proposed physical or external effect with target, parameters, policy reference, and executor handoff requirements.", ["effect_intent_id", "effect_type", "target_ref", "idempotency_key", "authority_ref"], ["proposed", "authorized", "rejected", "submitted", "unknown", "cancelled"], _evidence("source.application.json_schema", "source.application.prov_dm", "source.application.problem_details"), imports=["universe.security_privacy_trust", "universe.runtime_resource", "universe.lineage_provenance_evidence"], forbidden=["proposal equals authorization", "authorization equals execution", "analytical result equals effect authority", "missing target treated as broadcast"], time_roles=["proposed_at", "authorized_at", "submitted_at", "expires_at"]),
    _contract("contract.application.effect_receipt", "context.application.effect_handoff", "effect", "An observation of an executor handoff, including accepted, rejected, unknown and reconciled states without asserting business success.", ["effect_intent_id", "attempt_id", "executor_ref", "receipt_id", "observed_at"], ["accepted", "rejected", "unknown", "partially_observed", "reconciled", "invalidated"], _evidence("source.application.prov_dm", "source.application.json_schema", "source.application.problem_details"), imports=["universe.runtime_resource", "universe.lineage_provenance_evidence"], forbidden=["receipt equals business outcome", "timeout equals failure", "accepted handoff equals durable effect", "missing receipt equals no effect"], time_roles=["submitted_at", "accepted_at", "observed_at", "reconciled_at"]),
    _contract("contract.application.execution_receipt", "context.application.execution_evidence", "evidence", "A bounded provenance-linked observation of application declaration, attempt, refusal, state, event, projection, or effect activity.", ["receipt_id", "execution_id", "attempt_id", "subject_ref", "observed_at"], ["started", "completed_observed", "refused_observed", "failed_observed", "partial", "unknown", "invalidated"], _evidence("source.application.prov_dm", "source.application.json_schema"), imports=["universe.lineage_provenance_evidence", "universe.quality_reconciliation", "universe.consumption"], forbidden=["receipt equals proof of truth", "log presence equals execution completeness", "provenance equals authorization", "unknown elided"], time_roles=["started_at", "completed_at", "recorded_at", "observed_at"]),
]


LIBRARY_SPECS = [
    ("library.application.interaction_contracts", "context.application.interaction", "Normalize commands, queries and boundary refusals", ["contract.application.command", "contract.application.query"], ["operation.application.validate_command", "operation.application.validate_query"], ["source.application.openapi", "source.application.http", "source.application.json_schema", "source.application.problem_details"], "pure", ["HTTP/transport mapping is supplied", "schema edition is pinned", "policy reference is explicit"], ["does not own domain state", "does not authorize effects", "does not infer command meaning from HTTP verb"]),
    ("library.application.aggregate_transition", "context.application.aggregate_state", "Decide versioned aggregate transitions and form persistence intents", ["contract.application.aggregate_state", "contract.application.state_transition"], ["operation.application.decide_state_transition", "operation.application.form_state_commit_intent", "operation.application.reconcile_state_commit_receipt"], ["source.application.scxml", "source.application.json_schema"], "pure_then_intent", ["expected version is present", "invariant policy is bound", "persistence offer is explicit"], ["does not own a database", "does not claim durable commit", "does not bypass invariant refusal"]),
    ("library.application.workflow_saga", "context.application.workflow_coordination", "Represent long-lived coordination, retry budgets and explicit compensation", ["contract.application.workflow_instance", "contract.application.saga_compensation"], ["operation.application.start_workflow", "operation.application.advance_workflow", "operation.application.retry_workflow_step", "operation.application.compensate_workflow_step"], ["source.application.scxml", "source.application.bpmn", "source.application.saga", "source.application.states_language"], "intent_and_observation", ["workflow definition is editioned", "retry and compensation policies are separate", "deadlines and cancellation are finite"], ["does not become generic pipeline scheduling", "does not promise rollback", "does not authorize external effects"]),
    ("library.application.event_publication", "context.application.event_publication", "Form and observe domain/integration event publication without owning transport", ["contract.application.domain_event", "contract.application.integration_event"], ["operation.application.publish_domain_event", "operation.application.deliver_integration_event"], ["source.application.cloudevents", "source.application.json_schema", "source.application.prov_dm"], "intent_and_observation", ["event identity and edition are fixed", "delivery and processing are separately observed", "duplicate handling is explicit"], ["does not own broker semantics", "does not assert exactly-once", "does not turn envelope metadata into business meaning"]),
    ("library.application.projection_read_model", "context.application.projection", "Declare and observe derived read models, lag and rebuild behavior", ["contract.application.projection", "contract.application.query"], ["operation.application.execute_query", "operation.application.rebuild_projection"], ["source.application.json_schema", "source.application.prov_dm"], "intent_and_observation", ["source cut is explicit", "rebuild is bounded and repeatable", "lag is observable"], ["does not own source truth", "does not define analytical metric semantics", "does not hide stale reads"]),
    ("library.application.effect_handoff", "context.application.effect_handoff", "Separate effect proposal, authority reference, execution handoff and receipt reconciliation", ["contract.application.effect_intent", "contract.application.effect_receipt"], ["operation.application.issue_effect_intent", "operation.application.reconcile_effect_receipt"], ["source.application.json_schema", "source.application.prov_dm", "source.application.problem_details"], "intent_and_observation", ["authority reference is supplied", "target and idempotency key are fixed", "unknown executor state is retained"], ["does not grant authority", "does not execute physical effects", "does not equate receipt with outcome"]),
    ("library.application.execution_evidence", "context.application.execution_evidence", "Construct bounded execution observations and provenance links", ["contract.application.execution_receipt", "contract.application.effect_receipt"], ["operation.application.form_application_execution_receipt"], ["source.application.prov_dm", "source.application.json_schema"], "observation_only", ["attempt identity is unique", "observed fields are distinguished from asserted fields", "retention and completeness are declared"], ["does not audit independently", "does not assert business truth", "does not fill missing receipts"]),
    ("library.application.assembly", "context.application.execution_evidence", "Compose application contracts with imported data, analytics, policy, runtime and product boundaries", ["contract.application.command", "contract.application.query", "contract.application.state_transition", "contract.application.integration_event", "contract.application.effect_intent", "contract.application.execution_receipt"], ["operation.application.assemble_application_surface"], ["source.application.json_schema", "source.application.prov_dm"], "pure_graph_then_explicit_handoff", ["each edge has an owning authority", "resolution mechanism is named", "loss and refusal are retained"], ["does not collapse all assembly into compiler terminology", "does not transfer imported ownership", "does not declare a complete product or solution pack"]),
]


def _library(spec: Any) -> dict[str, Any]:
    lid, owner, responsibility, types, ops, evidence, side_effects, configs, forbidden = spec
    row = _common(
        lid,
        lifecycle=["candidate", "specified", "implemented", "qualified", "portable", "superseded", "retired"],
        time_roles=["declaration_time", "execution_time", "effective_time", "observation_time"],
        authority="Library owns reusable semantics within one context; callers must supply policy, authority, provider and vertical meaning.",
        resources=["bounded input", "finite recursion/retry budget", "explicit runtime/persistence/transport capability offer"],
        side_effects=side_effects,
        invariants=["public types belong to declared contexts", "operation laws are explicit", "unqualified offers are not bindable", "unknown is preserved"],
        refusals=["missing required imported contract", "unresolved owner", "unsupported edition", "unbounded resource request", "authority omitted"],
        evidence=evidence,
    )
    row.update({
        "library_id": lid,
        "semantic_owner_context_ref": owner,
        # Explicit adapter fields consumed by the global library-registry
        # source projection. They are not a second semantic model.
        "owner_context_ref": owner,
        "library_kind": {
            "interaction_contracts": "semantic_pure",
            "aggregate_transition": "semantic_pure",
            "workflow_saga": "runtime_mechanism",
            "event_publication": "effect_port_contract",
            "projection_read_model": "runtime_mechanism",
            "effect_handoff": "effect_port_contract",
            "execution_evidence": "test_oracle",
            "assembly": "semantic_pure",
        }.get(lid.removeprefix("library.application."), "semantic_pure"),
        "responsibility": responsibility,
        "public_types": types,
        "public_operations": ops,
        "configuration_points": configs,
        "compatibility_laws": ["edition changes require explicit compatibility relation", "lossy crosswalks cannot silently become identity", "refusal behavior is part of compatibility"],
        "imports": ["universe.data_type", "universe.operation", "universe.security_privacy_trust", "universe.runtime_resource", "universe.lineage_provenance_evidence"],
        "forbidden_responsibilities": forbidden,
        "qualification_status": "unqualified",
    })
    return row


LIBRARIES = [_library(item) for item in LIBRARY_SPECS]


def _operation(oid: str, library: str, inputs: list[str], outputs: list[str], purity: str, determinism: str,
               idempotency: str, pre: list[str], post: list[str], failures: list[str], effects: str,
               configs: list[str], evidence: list[str]) -> dict[str, Any]:
    row = _common(
        oid,
        lifecycle=["declared", "validated", "ready", "running", "completed", "refused", "failed", "unknown"],
        time_roles=["requested_at", "decision_at", "effective_at", "observed_at"],
        authority="Operation may validate a supplied authority reference but cannot grant authority or infer one.",
        resources=["finite input", "explicit clock", "bounded CPU/memory/retry budget", "supplied capability offer"],
        side_effects=effects,
        invariants=["input/output editions are explicit", "failure and unknown are typed outcomes", "no ambient I/O"],
        refusals=["missing input identity", "unbound required capability", "missing authority or time policy", "budget exceeded"],
        evidence=evidence,
    )
    row.update({
        "operation_id": oid,
        "owner_library_ref": library,
        "input_contract_refs": inputs,
        "output_contract_refs": outputs,
        "purity": purity,
        "determinism": determinism,
        "idempotency": idempotency,
        "preconditions": pre,
        "postconditions": post,
        "failure_states": failures,
        "configuration_points": configs,
        "side_effect_contract": effects,
        "refusal_precedence": ["invalid identity", "missing authority", "unsupported edition", "resource exhaustion", "execution failure", "unknown"],
    })
    return row


OPERATION_SPECS = [
    ("operation.application.validate_command", "library.application.interaction_contracts", ["contract.application.command"], ["contract.application.command"], "pure", "deterministic_given_inputs", "same_request_id_same_validation", ["command schema and edition supplied", "aggregate identity supplied"], ["validated command or typed refusal"], ["invalid_schema", "unsupported_edition", "missing_identity"], "none", ["schema_edition", "maximum_payload_bytes"], ["source.application.openapi", "source.application.json_schema", "source.application.problem_details"]),
    ("operation.application.validate_query", "library.application.interaction_contracts", ["contract.application.query"], ["contract.application.query"], "pure", "deterministic_given_inputs", "same_request_id_same_validation", ["query schema and cut supplied"], ["validated query or typed refusal"], ["invalid_schema", "unsupported_edition", "unbounded_query"], "none", ["schema_edition", "maximum_result_rows"], ["source.application.openapi", "source.application.http", "source.application.json_schema"]),
    ("operation.application.decide_state_transition", "library.application.aggregate_transition", ["contract.application.aggregate_state", "contract.application.command"], ["contract.application.state_transition"], "pure", "deterministic_given_inputs", "same_state_version_same_command_same_decision", ["expected version matches supplied snapshot", "invariants and clock are bound"], ["accepted or refused transition with next-state digest"], ["invariant_violation", "version_conflict", "unsupported_command", "ambiguous_time"], "none", ["invariant_profile", "clock_cut"], ["source.application.scxml", "source.application.json_schema"]),
    ("operation.application.form_state_commit_intent", "library.application.aggregate_transition", ["contract.application.state_transition"], ["contract.application.state_transition"], "effect_intent", "deterministic_given_inputs", "idempotency_key_required", ["transition is accepted", "persistence capability offer is explicit"], ["commit intent or refusal; no durable claim"], ["missing_persistence_offer", "duplicate_intent", "budget_exhausted"], "forms persistence intent; does not write", ["persistence_target", "idempotency_key", "timeout"], ["source.application.json_schema", "source.application.prov_dm"]),
    ("operation.application.reconcile_state_commit_receipt", "library.application.aggregate_transition", ["contract.application.state_transition", "contract.application.execution_receipt"], ["contract.application.aggregate_state"], "effect_observation", "deterministic_given_inputs", "same_receipt_same_reconciliation", ["receipt is linked to intent and observed cut"], ["committed_observed, conflicted, rejected or unknown classification"], ["unlinked_receipt", "contradictory_receipt", "unknown"], "observes supplied receipt only", ["reconciliation_policy", "observation_cut"], ["source.application.prov_dm", "source.application.json_schema"]),
    ("operation.application.publish_domain_event", "library.application.event_publication", ["contract.application.state_transition", "contract.application.domain_event"], ["contract.application.integration_event"], "effect_intent", "deterministic_given_inputs", "event_id_and_idempotency_key_required", ["transition is accepted", "event identity and edition are fixed"], ["publication intent or refusal"], ["missing_event_identity", "schema_mismatch", "missing_transport_offer"], "forms publication intent; does not deliver", ["envelope_edition", "partition_key"], ["source.application.cloudevents", "source.application.json_schema"]),
    ("operation.application.deliver_integration_event", "library.application.event_publication", ["contract.application.integration_event"], ["contract.application.execution_receipt"], "effect_observation", "observation_ordered", "duplicate_delivery_is_observable", ["transport offer and destination are explicit"], ["delivery receipt retaining duplicate/unknown status"], ["destination_rejected", "timeout", "duplicate", "unknown"], "observes supplied transport receipt", ["retry_policy", "delivery_timeout"], ["source.application.cloudevents", "source.application.prov_dm"]),
    ("operation.application.start_workflow", "library.application.workflow_saga", ["contract.application.command", "contract.application.workflow_instance"], ["contract.application.workflow_instance"], "effect_intent", "deterministic_given_inputs", "instance_id_required", ["definition edition and correlation supplied"], ["ready/running instance or refusal"], ["definition_missing", "duplicate_instance", "deadline_invalid"], "forms workflow-start intent", ["workflow_definition_edition", "deadline"], ["source.application.scxml", "source.application.bpmn", "source.application.json_schema"]),
    ("operation.application.advance_workflow", "library.application.workflow_saga", ["contract.application.workflow_instance", "contract.application.execution_receipt"], ["contract.application.workflow_instance"], "pure_then_intent", "deterministic_given_inputs", "step_attempt_id_required", ["current step and receipt cut supplied"], ["next state, wait, retry, compensation, terminal or unknown classification"], ["stale_instance", "guard_failed", "unknown"], "may form next-step intent", ["retry_policy", "cancellation", "deadline"], ["source.application.scxml", "source.application.bpmn", "source.application.states_language"]),
    ("operation.application.retry_workflow_step", "library.application.workflow_saga", ["contract.application.workflow_instance"], ["contract.application.workflow_instance"], "effect_intent", "deterministic_given_inputs", "attempt_id_required", ["retry policy permits another attempt", "previous result is retryable"], ["retry intent with incremented attempt"], ["retry_budget_exhausted", "non_retryable", "deadline_expired"], "forms retry intent", ["max_attempts", "backoff", "jitter_policy"], ["source.application.states_language", "source.application.json_schema"]),
    ("operation.application.compensate_workflow_step", "library.application.workflow_saga", ["contract.application.workflow_instance", "contract.application.saga_compensation"], ["contract.application.effect_intent"], "effect_intent", "deterministic_given_inputs", "compensation_id_required", ["compensation is explicitly defined and authorized externally"], ["compensation intent or refusal; no rollback claim"], ["no_compensation_defined", "authority_missing", "deadline_expired"], "forms compensation intent", ["compensation_policy", "authority_ref", "deadline"], ["source.application.saga", "source.application.json_schema"]),
    ("operation.application.execute_query", "library.application.projection_read_model", ["contract.application.query", "contract.application.projection"], ["contract.application.execution_receipt"], "effect_intent", "deterministic_given_inputs", "query_id_and_cut_required", ["projection cut and query limits supplied"], ["query execution observation with cut/lag"], ["projection_stale", "query_limit", "authorization_missing", "unknown"], "forms read-execution intent; result is observed", ["read_consistency", "max_rows", "timeout"], ["source.application.openapi", "source.application.http", "source.application.json_schema"]),
    ("operation.application.rebuild_projection", "library.application.projection_read_model", ["contract.application.projection"], ["contract.application.projection", "contract.application.execution_receipt"], "effect_intent", "deterministic_given_inputs", "rebuild_id_required", ["source cut and rebuild bounds supplied"], ["rebuild intent and eventual observation"], ["source_cut_missing", "resource_budget", "rebuild_conflict"], "forms rebuild intent", ["source_cut", "parallelism", "checkpoint_policy"], ["source.application.json_schema", "source.application.prov_dm"]),
    ("operation.application.issue_effect_intent", "library.application.effect_handoff", ["contract.application.effect_intent"], ["contract.application.effect_intent"], "pure", "deterministic_given_inputs", "effect_intent_id_and_idempotency_key_required", ["target, parameters, authority reference and expiry supplied"], ["validated intent or refusal; no authorization"], ["target_missing", "authority_reference_missing", "expiry_invalid"], "none", ["target_ref", "authority_ref", "expires_at"], ["source.application.json_schema", "source.application.prov_dm"]),
    ("operation.application.reconcile_effect_receipt", "library.application.effect_handoff", ["contract.application.effect_intent", "contract.application.effect_receipt"], ["contract.application.effect_receipt"], "effect_observation", "deterministic_given_inputs", "same_receipt_same_classification", ["receipt links intent and executor attempt"], ["accepted, rejected, unknown or reconciled classification"], ["unlinked_receipt", "contradiction", "unknown"], "observes supplied executor receipt", ["reconciliation_cut", "duplicate_policy"], ["source.application.prov_dm", "source.application.problem_details"]),
    ("operation.application.form_application_execution_receipt", "library.application.execution_evidence", ["contract.application.command", "contract.application.execution_receipt"], ["contract.application.execution_receipt"], "observation", "deterministic_given_inputs", "receipt_id_and_attempt_id_required", ["observed fields and provenance links supplied"], ["bounded receipt or incompleteness refusal"], ["missing_provenance_link", "retention_boundary", "unknown"], "records supplied observation only", ["retention_profile", "redaction_policy", "observation_cut"], ["source.application.prov_dm", "source.application.json_schema"]),
    ("operation.application.assemble_application_surface", "library.application.assembly", ["contract.application.command", "contract.application.query", "contract.application.state_transition", "contract.application.integration_event", "contract.application.effect_intent", "contract.application.execution_receipt"], ["contract.application.execution_receipt"], "pure_graph_then_explicit_handoff", "deterministic_given_inputs", "assembly_id_required", ["every edge has mechanism, owner and loss/refusal law"], ["assembly graph or typed unsatisfied gap; no completion claim"], ["unowned_edge", "implicit_compiler_default", "missing_authority", "incompatible_edition"], "forms graph and explicit intents only", ["resolution_mechanism", "loss_policy", "authority_owner"], ["source.application.json_schema", "source.application.prov_dm"]),
]

OPERATIONS = [_operation(*item) for item in OPERATION_SPECS]


def _transition(tid: str, machine: str, source: str, target: str, trigger: str, guard: str,
                result: str, refusal: str, evidence: list[str]) -> dict[str, Any]:
    row = _common(
        tid,
        lifecycle=["declared", "evaluated", "accepted", "refused", "superseded"],
        time_roles=["triggered_at", "effective_at", "observed_at"],
        authority="Transition authority is supplied by the owning application contract; transport/runtime does not grant it.",
        resources=["bounded guard evaluation", "explicit event/input", "finite retry/deadline budget"],
        side_effects="transition record is a decision/observation; physical persistence/effect is separate",
        invariants=["source and target states are from one editioned machine", "guard result is retained", "unknown transition is not silently mapped to failure"],
        refusals=["invalid source state", "missing trigger", "guard unavailable", "authority absent", "deadline exceeded"],
        evidence=evidence,
    )
    row.update({"transition_id": tid, "state_machine_ref": machine, "from_state": source, "to_state": target, "trigger": trigger, "guard": guard, "result_observation": result, "refusal_observation": refusal})
    return row


TRANSITIONS = [
    _transition("transition.application.aggregate.load", "machine.application.aggregate_state", "unloaded", "loaded", "load_observed", "snapshot identity and edition valid", "state snapshot observed", "refuse missing snapshot or ambiguous identity", ["source.application.json_schema"]),
    _transition("transition.application.aggregate.accept", "machine.application.aggregate_state", "loaded", "accepted", "transition_decided", "expected version and invariant gate pass", "accepted transition decision", "refuse invariant failure or version conflict", ["source.application.scxml"]),
    _transition("transition.application.aggregate.conflict", "machine.application.aggregate_state", "loaded", "conflicted", "commit_receipt_observed", "observed version differs from expected", "conflict receipt", "refuse silent last-write-wins", ["source.application.json_schema"]),
    _transition("transition.application.aggregate.unknown", "machine.application.aggregate_state", "transition_proposed", "unknown", "observation_missing", "no authoritative commit receipt by observation cut", "commit state unknown", "retain unknown until policy permits reconciliation", ["source.application.prov_dm"]),
    _transition("transition.application.workflow.start", "machine.application.workflow", "ready", "running", "start_accepted", "definition and correlation valid", "running instance observed", "refuse missing definition or duplicate instance", ["source.application.scxml", "source.application.bpmn"]),
    _transition("transition.application.workflow.wait", "machine.application.workflow", "running", "waiting", "wait_condition", "condition and deadline are explicit", "wait state recorded", "refuse ambient wait or missing deadline", ["source.application.scxml"]),
    _transition("transition.application.workflow.retry", "machine.application.workflow", "running", "retrying", "step_failed", "retry budget and error class permit retry", "new attempt intent", "refuse retry if non-retryable or budget exhausted", ["source.application.states_language"]),
    _transition("transition.application.workflow.compensate", "machine.application.workflow", "failed", "compensating", "compensation_requested", "compensation definition and external authority supplied", "compensation intent", "refuse to call compensation rollback", ["source.application.saga"]),
    _transition("transition.application.workflow.complete", "machine.application.workflow", "running", "completed", "terminal_step_observed", "terminal receipt is linked", "completion observed", "refuse completion without linked receipt", ["source.application.prov_dm"]),
    _transition("transition.application.workflow.unknown", "machine.application.workflow", "running", "unknown", "executor_timeout", "no authoritative receipt by observation cut", "unknown execution state", "retain unknown; do not infer failure", ["source.application.prov_dm"]),
    _transition("transition.application.projection.build", "machine.application.projection", "declared", "building", "build_intent", "source cut and derivation edition fixed", "build started", "refuse open-ended source scan", ["source.application.json_schema"]),
    _transition("transition.application.projection.current", "machine.application.projection", "building", "current", "checkpoint_observed", "checkpoint reaches declared cut", "projection current at cut", "refuse current without cut", ["source.application.prov_dm"]),
    _transition("transition.application.projection.lagging", "machine.application.projection", "current", "lagging", "new_source_observed", "source advances beyond checkpoint", "lag observed", "refuse hiding lag as current", ["source.application.prov_dm"]),
    _transition("transition.application.projection.rebuild", "machine.application.projection", "lagging", "rebuilding", "rebuild_intent", "bounded rebuild policy supplied", "rebuild started", "refuse mutable source cut", ["source.application.json_schema"]),
    _transition("transition.application.effect.authorize", "machine.application.effect", "proposed", "authorized", "external_authorization_observed", "authority receipt is linked and unexpired", "authorization observed", "refuse inferred or stale authority", ["source.application.prov_dm"]),
    _transition("transition.application.effect.submit", "machine.application.effect", "authorized", "submitted", "executor_handoff", "executor offer and target are explicit", "submission observed", "refuse direct physical effect from semantic library", ["source.application.json_schema"]),
    _transition("transition.application.effect.unknown", "machine.application.effect", "submitted", "unknown", "receipt_missing_at_cut", "no authoritative receipt", "unknown effect state", "retain unknown; do not call rejected", ["source.application.prov_dm"]),
]


STATE_MACHINES = [
    {"state_machine_id": "machine.application.aggregate_state", "owner_context_ref": "context.application.aggregate_state", "states": ["unloaded", "loaded", "transition_proposed", "accepted", "rejected", "conflicted", "committed_observed", "unknown"], "initial_state": "unloaded", "terminal_states": ["committed_observed", "rejected", "conflicted", "unknown"], "evidence_refs": ["source.application.scxml"], "status": STATUS, "completion_claim": False},
    {"state_machine_id": "machine.application.workflow", "owner_context_ref": "context.application.workflow_coordination", "states": ["defined", "ready", "running", "waiting", "retrying", "compensating", "completed", "failed", "cancelled", "unknown"], "initial_state": "defined", "terminal_states": ["completed", "failed", "cancelled", "unknown"], "evidence_refs": ["source.application.scxml", "source.application.bpmn", "source.application.saga"], "status": STATUS, "completion_claim": False},
    {"state_machine_id": "machine.application.projection", "owner_context_ref": "context.application.projection", "states": ["declared", "building", "current", "lagging", "invalid", "rebuilding", "unknown"], "initial_state": "declared", "terminal_states": ["current", "invalid", "unknown"], "evidence_refs": ["source.application.json_schema", "source.application.prov_dm"], "status": STATUS, "completion_claim": False},
    {"state_machine_id": "machine.application.effect", "owner_context_ref": "context.application.effect_handoff", "states": ["proposed", "authorized", "rejected", "submitted", "accepted", "unknown", "reconciled"], "initial_state": "proposed", "terminal_states": ["rejected", "accepted", "unknown", "reconciled"], "evidence_refs": ["source.application.prov_dm"], "status": STATUS, "completion_claim": False},
]


BOUNDARIES = [
    ("boundary.application.command_event", "command", "domain_event", "A command requests a decision; an event records an occurrence after a decision.", ["source.application.openapi", "source.application.cloudevents"]),
    ("boundary.application.query_projection", "query", "projection", "A query requests a read; a projection is a derived stateful read model.", ["source.application.openapi", "source.application.prov_dm"]),
    ("boundary.application.aggregate_persistence", "aggregate_state", "persistence", "Aggregate invariants and state transitions are application semantics; persistence supplies storage behavior.", ["source.application.scxml", "source.application.json_schema"]),
    ("boundary.application.workflow_dataflow", "workflow_instance", "pipeline_dataflow", "Application coordination may use dataflow capabilities but retains workflow meaning, waits and compensation.", ["source.application.bpmn", "source.application.scxml"]),
    ("boundary.application.compensation_rollback", "saga_compensation", "rollback", "Compensation is a forward action with its own effects; it does not restore atomicity by definition.", ["source.application.saga"]),
    ("boundary.application.decision_authority", "decision_result", "authorization", "Decision logic can propose a result; authority to act is a separate policy/approval contract.", ["source.application.dmn", "source.application.prov_dm"]),
    ("boundary.application.envelope_meaning", "integration_event", "event_meaning", "CloudEvents-style envelope metadata interoperates transport; it does not own business event meaning.", ["source.application.cloudevents"]),
    ("boundary.application.receipt_outcome", "execution_receipt", "business_outcome", "A receipt records an observation of execution; it does not prove the intended business outcome.", ["source.application.prov_dm"]),
]


def _boundary(item: Any) -> dict[str, Any]:
    bid, left, right, decision, evidence = item
    return {"boundary_id": bid, "left_concept": left, "right_concept": right, "decision": decision, "status": "proposed_unratified", "completion_claim": False, "evidence_refs": evidence, "required_adjudication": "independent context-owner review and executable counterexample"}


BOUNDARY_DECISIONS = [_boundary(item) for item in BOUNDARIES]


CROSSWALKS = [
    {"crosswalk_id": "crosswalk.application.openapi_interaction", "source_ref": "source.application.openapi", "target_refs": ["contract.application.command", "contract.application.query"], "direction": "source_to_candidate", "preservation": ["interface identity", "request/response schemas", "HTTP operation metadata"], "losses": ["domain meaning", "state authority", "effect authorization"], "prerequisites": ["OpenAPI edition and server/profile pinned"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.http_transport_laws", "source_ref": "source.application.http", "target_refs": ["contract.application.command", "contract.application.query"], "direction": "law_import", "preservation": ["transport safe/idempotent method properties"], "losses": ["domain idempotency", "transactionality", "absence of incidental effects"], "prerequisites": ["method and retry policy explicit"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.cloudevents_envelope", "source_ref": "source.application.cloudevents", "target_refs": ["contract.application.integration_event"], "direction": "source_to_candidate", "preservation": ["event context attributes and serialization envelope"], "losses": ["consumer processing", "business event semantics", "delivery guarantee"], "prerequisites": ["source, id, type and edition supplied"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.scxml_state", "source_ref": "source.application.scxml", "target_refs": ["contract.application.aggregate_state", "contract.application.workflow_instance"], "direction": "notation_to_candidate", "preservation": ["states, events and transition guards"], "losses": ["application owner, persistence and authority"], "prerequisites": ["state machine edition and event queue policy supplied"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.bpmn_workflow", "source_ref": "source.application.bpmn", "target_refs": ["contract.application.workflow_instance"], "direction": "notation_to_candidate", "preservation": ["process and flow vocabulary"], "losses": ["engine execution, retry, compensation and authority"], "prerequisites": ["BPMN profile and executable subset declared"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.dmn_decision", "source_ref": "source.application.dmn", "target_refs": ["contract.application.state_transition", "contract.application.effect_intent"], "direction": "logic_to_candidate", "preservation": ["decision logic structure"], "losses": ["input truth, decision authority, effect authorization"], "prerequisites": ["decision table edition and policy binding supplied"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.saga_compensation", "source_ref": "source.application.saga", "target_refs": ["contract.application.workflow_instance", "contract.application.saga_compensation"], "direction": "paper_to_candidate", "preservation": ["long-lived transaction decomposition and compensation relation"], "losses": ["compensation correctness, isolation and operational execution"], "prerequisites": ["forward step and compensating step explicitly paired"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.prov_receipt", "source_ref": "source.application.prov_dm", "target_refs": ["contract.application.effect_receipt", "contract.application.execution_receipt"], "direction": "provenance_to_candidate", "preservation": ["entity/activity/agent relations and observation links"], "losses": ["truth, assurance, authority and retention completeness"], "prerequisites": ["provenance graph and observation cut supplied"], "status": "partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.asl_retry", "source_ref": "source.application.states_language", "target_refs": ["contract.application.workflow_instance"], "direction": "runtime_to_candidate", "preservation": ["one concrete retry/catch parameterization"], "losses": ["portable semantics, domain retry law, compensation"], "prerequisites": ["runtime version and error taxonomy supplied"], "status": "runtime_specific_partial", "completion_claim": False},
    {"crosswalk_id": "crosswalk.application.json_validation", "source_ref": "source.application.json_schema", "target_refs": ["contract.application.command", "contract.application.query", "contract.application.execution_receipt"], "direction": "schema_to_candidate", "preservation": ["structural constraints"], "losses": ["semantic invariants, temporal/authority laws, execution behavior"], "prerequisites": ["dialect and schema identifier pinned"], "status": "partial", "completion_claim": False},
]


def _requirement(library: dict[str, Any]) -> dict[str, Any]:
    stem = library["library_id"].removeprefix("library.application.")
    return {"requirement_id": f"requirement.application.{stem}.implementation", "subject_ref": library["library_id"], "required_contract_refs": library["public_types"], "required_operation_refs": library["public_operations"], "required_evidence": ["implementation manifest", "law-oracle results", "resource bounds", "negative-twin results"], "binding_phase": "qualification", "fallback_law": "refuse", "status": "declared_unqualified", "completion_claim": False, "qualification_receipt_refs": [], "evidence_refs": library["evidence_refs"]}


def _offer(library: dict[str, Any]) -> dict[str, Any]:
    stem = library["library_id"].removeprefix("library.application.")
    return {"offer_id": f"offer.application.{stem}.reference_unimplemented", "subject_ref": library["library_id"], "offer_kind": "unimplemented_reference_offer", "claimed_contract_refs": library["public_types"], "claimed_operation_refs": library["public_operations"], "implementation_refs": [], "qualification_status": "unqualified", "qualification_receipt_refs": [], "binding_eligible": False, "portable": False, "status": "specified_unimplemented", "completion_claim": False, "limitations": ["no executable implementation attached", "no runtime receipt", "no portability evidence", "no vertical acceptance"], "exclusions": library["forbidden_responsibilities"], "evidence_refs": library["evidence_refs"]}


REQUIREMENTS_OFFERS = []
for _lib in LIBRARIES:
    REQUIREMENTS_OFFERS.extend([_requirement(_lib), _offer(_lib)])


TEST_SPECS = [
    ("test.application.command_event_separation", "command and event retain distinct identities and lifecycle", ["contract.application.command", "contract.application.domain_event"], "same identifier or lifecycle cannot be accepted for both roles", ["source.application.openapi", "source.application.cloudevents"]),
    ("test.application.query_no_state_change", "query validation rejects a state-changing request", ["contract.application.query"], "query with transition intent is refused", ["source.application.http", "source.application.openapi"]),
    ("test.application.aggregate_version_conflict", "expected version conflict is not silently overwritten", ["contract.application.aggregate_state", "contract.application.state_transition"], "conflicting version yields conflicted or refused, never accepted", ["source.application.scxml"]),
    ("test.application.transition_invariant_refusal", "invariant failure produces a typed refusal", ["contract.application.state_transition"], "missing invariant proof cannot produce accepted transition", ["source.application.scxml", "source.application.json_schema"]),
    ("test.application.event_duplicate_delivery", "duplicate event delivery remains observable and idempotency is explicit", ["contract.application.integration_event"], "duplicate message is not treated as a new business occurrence", ["source.application.cloudevents"]),
    ("test.application.event_edition_mismatch", "event schema edition mismatch fails closed", ["contract.application.domain_event", "contract.application.integration_event"], "unsupported edition is refused or unknown, never coerced silently", ["source.application.cloudevents", "source.application.json_schema"]),
    ("test.application.workflow_retry_budget", "retry stops at configured attempts/deadline", ["contract.application.workflow_instance"], "attempt count and deadline are bounded", ["source.application.states_language"]),
    ("test.application.retry_not_compensation", "retry and compensation are distinct transitions", ["contract.application.workflow_instance", "contract.application.saga_compensation"], "a retry cannot satisfy a compensation assertion", ["source.application.saga", "source.application.states_language"]),
    ("test.application.compensation_not_rollback", "compensation does not claim atomic rollback", ["contract.application.saga_compensation"], "compensation receipt cannot establish original state restoration", ["source.application.saga"]),
    ("test.application.projection_lag_rebuild", "projection lag and rebuild are visible states", ["contract.application.projection"], "a stale checkpoint cannot be labeled current", ["source.application.prov_dm"]),
    ("test.application.effect_authorization_missing", "effect intent without authority is refused", ["contract.application.effect_intent"], "missing or stale authority reference is a hard refusal", ["source.application.prov_dm"]),
    ("test.application.effect_unknown_receipt", "missing effect receipt yields unknown rather than rejected", ["contract.application.effect_receipt"], "timeout at observation cut remains unknown", ["source.application.prov_dm"]),
    ("test.application.receipt_provenance_chain", "execution receipt links supplied activity and subject", ["contract.application.execution_receipt"], "unlinked observation is incomplete/refused", ["source.application.prov_dm"]),
    ("test.application.http_idempotency_mapping", "transport idempotency law is not promoted to domain idempotency", ["contract.application.command", "contract.application.query"], "HTTP method metadata alone cannot satisfy domain retry law", ["source.application.http"]),
    ("test.application.deterministic_replay", "same pinned inputs and cuts replay to same decision digest", ["contract.application.state_transition", "contract.application.execution_receipt"], "ambient clock or unpinned schema causes refusal", ["source.application.json_schema", "source.application.prov_dm"]),
    ("test.application.non_compiler_assembly", "assembly graph accepts runtime, human and dataflow mechanisms", ["contract.application.execution_receipt"], "compiler terminology cannot be the only resolution mechanism", ["source.application.json_schema", "source.application.prov_dm"]),
]


CONFORMANCE_TESTS = [
    {"test_id": tid, "purpose": purpose, "subject_refs": refs, "oracle": oracle, "fixture_refs": [], "required_receipt_fields": ["test_id", "input_digest", "output_digest", "observed_at", "status", "refusal_or_failure"], "execution_status": "not_executed", "receipt_refs": [], "failure_behavior": "fail_closed_and_preserve_unknown", "status": "specified_not_executed", "completion_claim": False, "evidence_refs": evidence}
    for tid, purpose, refs, oracle, evidence in TEST_SPECS
]


NEGATIVE_TWINS = [
    {"negative_twin_id": f"negative-twin.application.{i}", "paired_test_ref": tid, "unsafe_inference": oracle, "expected_refusal": "refuse or retain unknown; never promote the inference to completion", "status": "active_candidate", "completion_claim": False, "evidence_refs": evidence}
    for i, (tid, _purpose, _refs, oracle, evidence) in enumerate(TEST_SPECS, 1)
]


ASSEMBLY_EDGES = [
    {"assembly_edge_id": "assembly.application.intent_to_interaction", "source_ref": "vertical.intent", "target_ref": "contract.application.command", "resolution_mechanism": "human_adjudication_then_structural_validation", "semantic_owner_ref": "context.application.interaction", "required_decisions": ["command meaning", "request identity", "authority reference"], "loss_or_refusal": "ambiguous intent is a gap; no guessed endpoint", "time_rule": "intent and contract editions are pinned", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.openapi", "source.application.json_schema"]},
    {"assembly_edge_id": "assembly.application.interaction_to_state", "source_ref": "contract.application.command", "target_ref": "contract.application.state_transition", "resolution_mechanism": "application_runtime", "semantic_owner_ref": "context.application.aggregate_state", "required_decisions": ["aggregate owner", "invariant profile", "expected version"], "loss_or_refusal": "missing owner/version yields refusal", "time_rule": "transition clock is explicit", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.scxml"]},
    {"assembly_edge_id": "assembly.application.state_to_event", "source_ref": "contract.application.state_transition", "target_ref": "contract.application.domain_event", "resolution_mechanism": "application_runtime", "semantic_owner_ref": "context.application.event_publication", "required_decisions": ["event type", "causation", "publication condition"], "loss_or_refusal": "unaccepted transition cannot emit accepted domain event", "time_rule": "occurrence time differs from publication time", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.cloudevents", "source.application.prov_dm"]},
    {"assembly_edge_id": "assembly.application.event_to_dataflow", "source_ref": "contract.application.integration_event", "target_ref": "universe.pipeline_dataflow", "resolution_mechanism": "dataflow_composition", "semantic_owner_ref": "context.application.event_publication", "required_decisions": ["admission contract", "deduplication", "ordering", "consumer authority"], "loss_or_refusal": "delivery does not prove processing; unsupported admission is refused", "time_rule": "delivery and processing cuts are distinct", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.cloudevents", "source.application.prov_dm"]},
    {"assembly_edge_id": "assembly.application.data_to_projection", "source_ref": "universe.pipeline_dataflow", "target_ref": "contract.application.projection", "resolution_mechanism": "dataflow_composition", "semantic_owner_ref": "context.application.projection", "required_decisions": ["source cut", "derivation edition", "checkpoint policy"], "loss_or_refusal": "missing cut yields lagging/unknown, not current", "time_rule": "source cut and materialization time are retained", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.prov_dm", "source.application.json_schema"]},
    {"assembly_edge_id": "assembly.application.analytics_to_effect", "source_ref": "analytics.proposal", "target_ref": "contract.application.effect_intent", "resolution_mechanism": "human_adjudication_then_effect_gateway", "semantic_owner_ref": "context.application.effect_handoff", "required_decisions": ["analytical method validity", "purpose/policy", "human or service approval", "target and expiry"], "loss_or_refusal": "analysis result is not authority; absent approval is refused", "time_rule": "proposal, authorization and execution times are distinct", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.dmn", "source.application.prov_dm"]},
    {"assembly_edge_id": "assembly.application.workflow_to_effect", "source_ref": "contract.application.workflow_instance", "target_ref": "contract.application.effect_intent", "resolution_mechanism": "explicit_effect_gateway", "semantic_owner_ref": "context.application.effect_handoff", "required_decisions": ["step guard", "authority", "idempotency", "executor offer"], "loss_or_refusal": "workflow advancement cannot directly perform physical effect", "time_rule": "deadline and expiry are explicit", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.saga", "source.application.prov_dm"]},
    {"assembly_edge_id": "assembly.application.receipt_to_evidence", "source_ref": "contract.application.effect_receipt", "target_ref": "contract.application.execution_receipt", "resolution_mechanism": "semantic_import_then_human_review", "semantic_owner_ref": "context.application.execution_evidence", "required_decisions": ["observation cut", "provenance links", "retention/quality policy"], "loss_or_refusal": "receipt is retained as observation; no truth or assurance promotion", "time_rule": "recorded and observed timestamps remain distinct", "status": "candidate_unratified", "completion_claim": False, "evidence_refs": ["source.application.prov_dm"]},
]


GAPS = [
    {"gap_id": "gap.application.context_owner_adjudication", "category": "semantic_ownership", "status": "OPEN", "scope_refs": [c["context_id"] for c in CONTEXTS], "blocking_outputs": ["ratified context map", "canonical cross-context ACLs"], "evidence_needed": ["independent owner review", "merge/split decisions", "vertical counterexamples"], "completion_effect": "candidate only; cannot claim universal application ontology", "completion_claim": False},
    {"gap_id": "gap.application.aggregate_authority", "category": "domain_semantics", "status": "OPEN", "scope_refs": ["contract.application.aggregate_state", "contract.application.state_transition"], "blocking_outputs": ["portable aggregate laws", "vertical acceptance"], "evidence_needed": ["domain-owner adjudication", "conformance across dissimilar aggregates"], "completion_effect": "aggregate is a candidate contract, not a universal DDD law", "completion_claim": False},
    {"gap_id": "gap.application.implementation_qualification", "category": "implementation", "status": "OPEN", "scope_refs": [l["library_id"] for l in LIBRARIES], "blocking_outputs": ["qualified offers", "executable law receipts"], "evidence_needed": ["two independent implementations", "resource and failure receipts", "security review"], "completion_effect": "all reference offers remain unqualified and unbindable", "completion_claim": False},
    {"gap_id": "gap.application.provider_portability", "category": "portability", "status": "OPEN", "scope_refs": ["library.application.workflow_saga", "library.application.event_publication", "library.application.effect_handoff"], "blocking_outputs": ["portable runtime bindings", "substitution proof"], "evidence_needed": ["two independent runtime/provider offers", "edition and limit crosswalk", "replay evidence"], "completion_effect": "runtime-specific evidence cannot be generalized", "completion_claim": False},
    {"gap_id": "gap.application.vertical_acceptance", "category": "vertical", "status": "OPEN", "scope_refs": ["library.application.assembly"], "blocking_outputs": ["accepted enterprise application pack", "mixed vertical proof"], "evidence_needed": ["two unrelated verticals", "live or replayable receipts", "negative twins"], "completion_effect": "no product or solution-pack acceptance claim", "completion_claim": False},
    {"gap_id": "gap.application.effect_authority", "category": "authority", "status": "OPEN", "scope_refs": ["context.application.effect_handoff", "contract.application.effect_intent"], "blocking_outputs": ["authorized effect path"], "evidence_needed": ["policy/approval binding", "executor identity", "revocation and reconciliation receipts"], "completion_effect": "application behavior can form intent but cannot authorize or execute effects", "completion_claim": False},
    {"gap_id": "gap.application.open_world_saturation", "category": "coverage", "status": "OPEN", "scope_refs": ["context.application.interaction", "context.application.execution_evidence"], "blocking_outputs": ["completeness claim"], "evidence_needed": ["independent taxonomy challenge", "new-family search", "counterexample review"], "completion_effect": "finite records do not prove coverage of every enterprise application", "completion_claim": False},
]


def records() -> dict[str, list[dict[str, Any]]]:
    result = {
        "sources.jsonl": SOURCES,
        "bounded-contexts.jsonl": CONTEXTS,
        "semantic-contracts.jsonl": CONTRACTS,
        "state-machines.jsonl": STATE_MACHINES,
        "state-transitions.jsonl": TRANSITIONS,
        "library-contracts.jsonl": LIBRARIES,
        "operations.jsonl": OPERATIONS,
        "boundary-decisions.jsonl": BOUNDARY_DECISIONS,
        "crosswalks.jsonl": CROSSWALKS,
        "requirements-offers.jsonl": REQUIREMENTS_OFFERS,
        "conformance-tests.jsonl": CONFORMANCE_TESTS,
        "negative-twins.jsonl": NEGATIVE_TWINS,
        "assembly-edges.jsonl": ASSEMBLY_EDGES,
        "gaps.jsonl": GAPS,
    }
    # Keep every JSONL row an editioned, explicitly non-final record.  Evidence
    # rows do not cite themselves; structural rows without a more specific
    # source citation inherit the JSON Schema specification as their serialization
    # evidence, while their semantic limitations remain explicit in the row.
    for name, items in result.items():
        for row in items:
            row.setdefault("edition", EDITION)
            row.setdefault("status", "primary_source" if name == "sources.jsonl" else STATUS)
            row.setdefault("completion_claim", False)
            row.setdefault("evidence_refs", [] if name == "sources.jsonl" else ["source.application.json_schema"])
            if name != "sources.jsonl":
                row.setdefault("lifecycle", ["candidate", "accepted", "superseded", "retired"])
                row.setdefault("time_model", {"roles": ["declared_at", "effective_at", "observed_at"], "ambient_time_allowed": False, "clock_ref": None})
                row.setdefault("authority_model", "Semantic authority remains with the referenced application context or imported universe; this record cannot infer it.")
                row.setdefault("resource_assumptions", ["finite record", "bounded validator/generator work"])
                row.setdefault("side_effects", "record is declarative; execution effects require an explicit intent and receipt")
                row.setdefault("invariants", ["stable identity and edition are explicit", "unknown and refusal are retained"])
                row.setdefault("refusals", ["missing identity", "unsupported edition", "ambiguous authority", "unbounded resource request"])
    return result
