#!/usr/bin/env python3
"""Build the subject- and transition-positioned state/change ontology and P3S rebase."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
P3S_DOCKETS = SEM / "p3s_state_change_evidence/family-evidence-dockets.jsonl"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))

from member_axis_rebase import build_member_rebase  # noqa: E402


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {
        "source_id": "source.state.scxml",
        "title": "State Chart XML (SCXML): State Machine Notation for Control Abstraction",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/scxml/",
        "bounded_implication": "A state-machine configuration may contain multiple active states; transitions have source, event or eventless trigger, guard, target, conflict priority and executable content.",
        "authority_limit": "SCXML defines event-processor semantics, not domain aggregates, business authority, durable effects or universal lifecycle states.",
    },
    {
        "source_id": "source.state.kubernetes-api-conventions",
        "title": "Kubernetes API Conventions",
        "publisher": "Kubernetes",
        "url": "https://github.com/kubernetes/community/blob/main/contributors/devel/sig-architecture/api-conventions.md",
        "bounded_implication": "Desired spec, observed status, generation, resourceVersion and conditions are distinct; conditions are open-world observations rather than comprehensive state machines.",
        "authority_limit": "Kubernetes resource reconciliation does not define application-domain truth, business acceptance or irreversible external-effect completion.",
    },
    {
        "source_id": "source.state.prov-constraints",
        "title": "Constraints of the PROV Data Model",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/prov-constraints/",
        "bounded_implication": "Activity start/end and entity generation/use/invalidation are distinct instantaneous events with ordering constraints that delimit lifetimes.",
        "authority_limit": "PROV constrains provenance descriptions; it does not prove the described world event, authorization, deletion or acceptance.",
    },
    {
        "source_id": "source.state.http-semantics",
        "title": "RFC 9110: HTTP Semantics",
        "publisher": "IETF",
        "url": "https://www.rfc-editor.org/rfc/rfc9110.html",
        "bounded_implication": "Idempotence concerns the intended requested effect; repeated requests may still create separate logs, and DELETE removes a resource association without promising physical erasure.",
        "authority_limit": "HTTP method semantics do not define domain transitions, storage reclamation, legal erasure or downstream business acceptance.",
    },
    {
        "source_id": "source.state.json-patch",
        "title": "RFC 6902: JSON Patch",
        "publisher": "IETF",
        "url": "https://www.rfc-editor.org/rfc/rfc6902.html",
        "bounded_implication": "Patch operations apply sequentially to a target document until completion or error; test, add, remove, replace, move and copy are distinct operations.",
        "authority_limit": "JSON Patch changes a representation and does not supply target revision identity, domain invariants, authorization or business effect semantics by itself.",
    },
    {
        "source_id": "source.state.iceberg",
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "bounded_implication": "Table state changes through an atomic metadata swap and snapshots; append, replace, overwrite and delete have different logical and physical consequences under optimistic concurrency.",
        "authority_limit": "Iceberg table-format state does not define the source business event, cross-system authority, historical erasure or accepted analytical result.",
    },
    {
        "source_id": "source.state.temporal-workflow-execution",
        "title": "Temporal Workflow Execution overview",
        "publisher": "Temporal Technologies",
        "url": "https://docs.temporal.io/workflow-execution",
        "bounded_implication": "Workflow Id, Run Id, execution chain, command, recorded event, replay, retry, Continue-As-New and open/closed execution status are distinct lifecycle coordinates.",
        "authority_limit": "Temporal execution semantics do not prove external activity effects, domain acceptance or suitability of one workflow lifecycle for every process.",
    },
]


SUBJECT_ARCHETYPES = [
    ("domain_entity_or_aggregate", "A domain-identified entity or aggregate whose legal transitions enforce business invariants.", ["entity identity", "aggregate boundary", "lifecycle edition", "business authority"]),
    ("immutable_value_successor", "An immutable value or definition related to earlier editions without mutating them.", ["value identity", "successor relation", "compatibility", "supersession"]),
    ("resource_representation", "A server-managed resource representation with logical identity, versions and interaction outcomes.", ["resource identity", "representation version", "current selection", "history support"]),
    ("process_case_or_workflow", "A process, case or workflow with execution state, waiting points, events and compensation.", ["definition edition", "case/execution identity", "active configuration", "history cut"]),
    ("operation_run_attempt", "A job, query, task, solver or model execution with run and attempt outcomes.", ["operation definition", "run identity", "attempt identity", "terminality"]),
    ("desired_observed_control", "A control resource whose desired state and reported observations converge asynchronously.", ["desired edition", "observed edition", "observation freshness", "reconciliation authority"]),
    ("artifact_model_or_schema", "A model, schema, metric, plan or other governed artifact with edition, alias and publication lifecycle.", ["artifact identity", "edition", "alias/reference", "qualification and deployment state"]),
    ("authorization_or_credential", "A grant, credential, consent or delegation whose issuance, suspension, expiry and revocation differ.", ["grant identity", "credential identity", "authority", "propagation boundary"]),
    ("claim_evidence_or_conformance", "A claim, validation result, evidence item or verdict with revision, rebuttal and acceptance lifecycle.", ["claim identity", "evidence edition", "verdict authority", "defeaters"]),
    ("storage_table_or_snapshot", "A table, dataset, catalog resource or storage object with snapshots, commits and retention state.", ["logical object", "metadata edition", "snapshot", "physical retention"]),
    ("stream_log_or_progress", "An append-oriented log and separately tracked reader or application progress.", ["partition/log identity", "record position", "fetch position", "committed recovery position"]),
    ("external_effect_or_acceptance", "A proposed, attempted, acknowledged, observed and accepted real-world or downstream effect.", ["effect identity", "executor", "receipt", "acceptance authority"]),
]


def subject_archetype_rows() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "state_subject_archetype",
            "archetype_id": f"archetype.state-subject.{name}.v1",
            "meaning": meaning,
            "required_coordinates": coordinates,
            "applicability": "UNRESOLVED_PER_MEMBER_AND_USE_SITE",
            "completion_claim": False,
        }
        for name, meaning, coordinates in SUBJECT_ARCHETYPES
    ]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.state-change-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "state_and_change",
    "domain_question": "For which identified subject and lifecycle edition is state asserted; is the record a request, fact, observation, projection or accepted effect; and what guarded transition, history and concurrency laws connect it to other states?",
    "coordinate_key": [
        "bounded_context_ref",
        "subject_ref",
        "state_subject_archetype_ref",
        "lifecycle_ref",
        "lifecycle_edition_ref",
        "state_or_transition_ref",
    ],
    "state_coordinate": {
        "required_fields": [
            "subject_identity_ref",
            "state_subject_archetype_ref",
            "lifecycle_ref_and_edition",
            "state_vector_or_active_configuration",
            "assertion_position",
            "revision_coordinate",
            "history_model",
            "time_basis_refs",
            "authority_ref",
            "evidence_ref",
        ],
        "assertion_position": [
            "intent_or_desired",
            "command_or_effect_request",
            "recorded_fact_or_event",
            "reported_observation",
            "inferred_projection",
            "acknowledged_effect",
            "accepted_business_outcome",
        ],
        "state_shape": [
            "single_state",
            "orthogonal_active_configuration",
            "state_vector",
            "monotonic_condition_set",
            "open_world_observations",
            "projection_from_history",
            "explicit_extension",
        ],
        "revision_coordinate": [
            "logical_version",
            "opaque_revision",
            "event_sequence",
            "snapshot_id",
            "log_position",
            "valid_and_recording_time",
            "none_by_explicit_law",
        ],
        "history_model": [
            "current_only",
            "version_chain",
            "append_only_facts",
            "snapshot_plus_delta",
            "bitemporal_facts",
            "workflow_event_history",
            "provenance_or_audit_evidence",
            "external_observations",
        ],
    },
    "transition_contract": {
        "required_fields": [
            "transition_identity",
            "subject_and_lifecycle_ref",
            "source_state_or_configuration",
            "trigger_kind_and_identity",
            "command_identity_and_idempotency_scope",
            "authority_ref",
            "guard_and_preconditions",
            "expected_revision_or_history_cut",
            "target_state_or_configuration",
            "emitted_internal_facts",
            "proposed_external_effects",
            "effect_receipt_and_acceptance_requirements",
            "refusal_precedence",
        ],
        "trigger_kind": [
            "command",
            "external_event",
            "internal_event",
            "eventless_guard",
            "timer_or_expiry",
            "observation",
            "reconciliation_iteration",
            "migration_or_replay",
        ],
        "required_outcomes": [
            "transitioned",
            "no_op_by_law",
            "duplicate",
            "stale_revision",
            "guard_false",
            "illegal_transition",
            "authority_refused",
            "indeterminate_history",
            "concurrency_conflict",
            "partial_effect_reconciliation_required",
            "failed",
        ],
    },
    "change_relations": [
        "construct",
        "append_fact",
        "replace_representation",
        "patch_representation",
        "update_projection",
        "materialize_snapshot",
        "apply_delta",
        "supersede",
        "invalidate",
        "revoke",
        "expire",
        "logical_delete_or_tombstone",
        "physical_erase",
        "cancel",
        "retry_attempt",
        "replay_history",
        "resume",
        "continue_as_new",
        "compensate",
        "reverse",
        "rollback_restore",
        "reconcile",
    ],
    "effect_progression": [
        "proposed",
        "authorized",
        "dispatched",
        "acknowledged",
        "observed",
        "reconciled",
        "accepted",
        "compensation_requested",
        "compensated",
        "residual_effect_open",
    ],
    "dependency_axis_refs": [
        "identity_and_equality",
        "grain_and_cardinality",
        "time",
        "order_and_topology",
        "authority_and_trust",
        "effect_boundary",
        "partiality_and_uncertainty",
        "evidence_and_conformance",
        "compatibility_and_evolution",
    ],
    "discovery_projection_compatibility": {
        "existing_facets": [
            "immutable_value",
            "append_only_event",
            "lifecycle_transition",
            "versioned_mutation",
            "snapshot_and_delta",
            "compensation_or_reversal",
        ],
        "status": "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY",
        "prohibition": "A facet cannot choose the state subject, lifecycle edition, assertion position, transition contract, history completeness, effect stage or member applicability.",
    },
    "non_collapse_laws": [
        "library is not state subject",
        "state is not a status string",
        "command is not event and event is not current state",
        "desired state is not observed state and observed state is not accepted outcome",
        "condition observation is not a comprehensive state machine",
        "resource representation version is not real-world entity state",
        "state configuration is not its serialized snapshot",
        "snapshot is not checkpoint and checkpoint is not durable commit",
        "current projection is not complete history",
        "retry is not replay and replay is not resume",
        "idempotent request is not exactly-once execution",
        "cancel request is not confirmed cancellation",
        "delete association is not tombstone and neither is physical erasure",
        "supersession is not invalidation or revocation",
        "compensation is not reversal or rollback and may fail",
        "terminal execution is not accepted business effect",
    ],
    "primary_source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decision": "UNRESOLVED",
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


KERNEL_DEFINITIONS = [
    ("construct_or_initialize", "absent or pre-initial", "initial legal state/configuration", "Creation of a representation does not prove creation of the real-world subject."),
    ("immutable_value_successor", "prior immutable edition", "new separately identified edition", "A successor relation is not mutation or semantic compatibility."),
    ("guarded_state_transition", "legal source configuration", "guard-selected target configuration", "A matching event does not enable a transition when its guard or authority fails."),
    ("parallel_state_microstep", "orthogonal active configuration", "legal next active configuration", "Parallel active regions are not an unordered set of independent aggregate transactions."),
    ("append_fact_and_reduce", "history cut plus fact", "new history cut and projection", "Appending a fact does not prove the projection is complete or external effects occurred."),
    ("optimistic_replace", "expected revision plus replacement", "new revision or conflict", "Last-write success must not be inferred without a declared concurrency rule."),
    ("conditional_patch", "exact target/base plus ordered patch", "patched representation or atomic refusal", "A representation patch is not a domain transition unless invariants and base identity are bound."),
    ("snapshot_materialize", "state/history at declared cut", "snapshot with provenance to its cut", "A snapshot is not the subject, history or durable checkpoint."),
    ("delta_apply", "exact base plus applicable delta", "derived successor or refusal", "A delta without exact base, order and applicability is not meaningful."),
    ("desired_observed_reconcile", "desired edition plus observations", "effect request and later observation", "Writing intent does not prove convergence or accepted effect."),
    ("observe_or_report", "external or runtime condition", "time- and revision-scoped observation", "Observation may be stale, partial or unknown and is not a command."),
    ("validate_or_assess", "subject edition plus rule/profile edition", "report or verdict candidate", "Validation does not repair, approve or accept the subject."),
    ("approve_or_decide", "proposal plus evidence", "authorized decision record", "Approval does not issue a credential, execute an effect or prove completion."),
    ("issue_or_activate", "authorized decision plus issuance preconditions", "issued/active artifact and receipt", "Issued is not consumed, effective everywhere or accepted downstream."),
    ("pause_and_resume", "open execution", "paused then resumable execution", "Paused is not terminal and resume is not replay or retry."),
    ("complete_or_finalize", "open execution or process", "terminal execution result", "Execution completion does not prove result consumption or business acceptance."),
    ("fail_or_abort", "open transition/execution", "failed or aborted outcome plus residuals", "Failure may follow partial effects and is not automatic rollback."),
    ("cancel_request_confirm", "cancellable subject plus request", "requested, confirmed, refused or indeterminate cancellation", "Requesting cancellation is not successful cancellation."),
    ("timeout_or_expire", "time-bounded validity or execution", "expired/timeout observation and policy reaction", "Expiry observation does not by itself revoke every derived authorization or erase data."),
    ("retry_new_attempt", "failed/indeterminate attempt plus retry policy", "new attempt identity", "Retry is a new attempt and may duplicate effects without an idempotency contract."),
    ("replay_history", "recorded history plus deterministic definition", "reconstructed state and command comparison", "Replay is not re-occurrence of world events or re-execution of effects."),
    ("continue_as_new_or_chain", "execution/run near boundary", "new run linked in one execution chain", "Run identity, chain identity and business process identity remain distinct."),
    ("supersede_or_replace_current", "current artifact/version", "new selected current plus retained relation", "Superseded does not mean invalid, deleted or incompatible."),
    ("invalidate_or_revoke", "valid assertion/grant/credential", "invalidated or revoked state plus propagation", "Revocation is not physical deletion or retraction of historical actions."),
    ("logical_delete_or_tombstone", "addressable current resource", "unavailable association or tombstone", "Logical deletion does not prove physical erasure or removal from every replica."),
    ("physical_erase", "retained bytes under deletion authority", "erasure evidence or residual refusal", "An erasure request and an erasure receipt are different facts."),
    ("compensate_effect", "completed/partial effect plus compensation policy", "compensation outcome and residual effect", "Compensation is a new effect, may fail, and does not erase history."),
    ("reverse_business_entry", "posted business effect", "explicit counter-entry or reversal", "Reversal preserves the original occurrence and differs from rollback."),
    ("rollback_restore", "deployment/configuration/storage edition", "selected earlier or repaired edition", "Rollback does not undo external effects or erase intervening history."),
    ("migrate_or_upcast_history", "old edition state/history", "new representation with provenance and loss claims", "Upcasting representation does not rewrite the original world facts."),
    ("reconcile_partial_effect", "indeterminate or partial effect evidence", "observed/accepted/compensated/residual verdict", "Acknowledgement alone does not establish effect truth or acceptance."),
]


def transition_kernel_rows() -> list[dict[str, Any]]:
    source_refs = [row["source_id"] for row in PRIMARY_SOURCES]
    return [
        {
            "record_kind": "state_transition_kernel",
            "kernel_id": f"kernel.state-change.{name}.v1",
            "source_relation": source,
            "target_relation": target,
            "required_contract_fields": ONTOLOGY["transition_contract"]["required_fields"],
            "must_bind_dependency_axes": ONTOLOGY["dependency_axis_refs"],
            "negative_twin": negative,
            "bounded_primary_source_refs": source_refs,
            "applicability": "UNRESOLVED_PER_TRANSITION",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for name, source, target, negative in KERNEL_DEFINITIONS
    ]


def route_for_facets(facets: tuple[str, ...]) -> str:
    return (
        "LEXICAL_DISCOVERY_PROJECTION_ONLY_SUBJECT_LIFECYCLE_RESEARCH_REQUIRED"
        if facets
        else "NO_MEMBER_STATE_SUBJECT_EVIDENCE_VACANCY"
    )


def build() -> dict[str, Any]:
    rebase = build_member_rebase(
        axis="state_and_change",
        dockets_path=P3S_DOCKETS,
        preclassifications_path=PRECLASSIFICATIONS,
        cluster_prefix="cluster.p3s.state-change-rebase",
        cluster_route=route_for_facets,
    )
    clusters = []
    for row in rebase["clusters"]:
        clusters.append(
            {
                "record_kind": "state_change_member_research_cluster",
                **row,
                "required_next_evidence": [
                    "authoritative state-subject inventory",
                    "lifecycle definitions and editions per subject",
                    "state/observation/intent/effect-position inventory",
                    "transition and refusal inventory",
                    "history, revision and concurrency contract",
                    "negative twins and exception proof",
                ],
                "member_applicability": "UNRESOLVED",
                "owner_decision": "UNRESOLVED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    members = []
    for row in rebase["members"]:
        members.append(
            {
                "record_kind": "state_change_member_research_route",
                "route_id": f"route.p3s.state-change.{row['library_ref'].removeprefix('library.').replace('.', '-').replace('_', '-')}",
                **row,
                "flat_projection_effect": "DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY",
                "required_state_subject_profiles": "NOT_YET_SUPPLIED",
                "required_lifecycle_editions": "NOT_YET_SUPPLIED",
                "required_transition_inventory": "NOT_YET_SUPPLIED",
                "required_history_concurrency_effect_contracts": "NOT_YET_SUPPLIED",
                "member_applicability": "UNRESOLVED",
                "owner_decision": "UNRESOLVED",
                "canonical_gaps_closed": 0,
                "status": "LOSSLESSLY_ROUTED_RESEARCH_OPEN",
                "completion_claim": False,
            }
        )

    extensions = []
    for family_ref, docket in sorted(rebase["docket_by_family"].items()):
        short = family_ref.removeprefix("constitution.family.")
        extensions.append(
            {
                "record_kind": "state_change_exact_contract_extension_candidate",
                "extension_id": f"extension.p3s.state-change-coordinate.{short}.v1",
                "family_ref": family_ref,
                "family_evidence_docket_ref": docket["docket_id"],
                "represented_library_refs": docket["library_refs"],
                "represented_library_count": docket["library_count"],
                "required_record_kinds": [
                    "state_subject_profile",
                    "lifecycle_contract",
                    "state_coordinate",
                    "transition_contract",
                    "history_and_projection_contract",
                    "concurrency_and_idempotency_contract",
                    "effect_progression_contract",
                    "member_exception",
                ],
                "required_owner_action": "ratify subject-positioned lifecycles and transitions or preserve an explicit vacancy",
                "owner_decision": "UNRESOLVED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    kernels = transition_kernel_rows()
    summary = {
        "program_id": "program.p3s.state-change-coordinate-ontology-and-rebase.v1",
        "as_of": AS_OF,
        "axis": "state_and_change",
        "primary_sources": len(PRIMARY_SOURCES),
        "state_subject_archetypes": len(SUBJECT_ARCHETYPES),
        "transition_kernels": len(kernels),
        "family_extension_candidates": len(extensions),
        "research_clusters": len(clusters),
        "target_member_routes": len(members),
        "routes_with_lexical_discovery_projection": rebase["lexical_member_count"],
        "routes_with_no_member_state_subject_evidence": rebase["vacancy_member_count"],
        "state_subject_profiles_supplied": 0,
        "transition_inventories_supplied": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "archetypes": subject_archetype_rows(),
        "kernels": kernels,
        "clusters": clusters,
        "members": members,
        "extensions": extensions,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "state-change-coordinate-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "state-subject-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["archetypes"]),
        "transition-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["kernels"]),
        "member-research-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "member-state-routes.jsonl": "".join(canonical(row) + "\n" for row in built["members"]),
        "extension-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["extensions"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.p3s.state-change-coordinate-ontology-and-rebase.v1",
            "as_of": AS_OF,
            "files": claims,
            "completion_claim": False,
        },
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS P3S state/change coordinate ontology: "
        f"{summary['state_subject_archetypes']} subject archetypes, "
        f"{summary['transition_kernels']} kernels, {summary['research_clusters']} clusters and "
        f"{summary['target_member_routes']} exact routes; decisions and gap closure remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
