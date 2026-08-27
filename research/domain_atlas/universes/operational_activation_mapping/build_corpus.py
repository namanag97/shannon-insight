#!/usr/bin/env python3
"""Build the exact destination-profile, activation-plan and evaluation corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for row in rows) + "\n"


def S(ident: str, title: str, authority: str, url: str, supports: str, limitation: str) -> dict:
    return {
        "source_id": f"source.activation-mapping.{ident}", "title": title, "authority": authority,
        "url": url, "retrieved": AS_OF, "source_kind": "primary_or_official",
        "supports": supports, "does_not_prove": limitation,
    }


SOURCES = [
    S("hightouch.sync", "Syncs overview", "Hightouch", "https://hightouch.com/docs/syncs/overview", "separate model, destination object, mode, record matching, field mapping, delete behavior and per-run outcomes", "One product's configuration is not a universal activation contract."),
    S("hightouch.modes", "Sync types and modes", "Hightouch", "https://hightouch.com/docs/syncs/types-and-modes", "insert, update, upsert, add, remove, archive, mirror, snapshot and diff vary by destination and object", "Similar labels across providers do not prove equivalent effects."),
    S("hightouch.match", "Record matching", "Hightouch", "https://hightouch.com/docs/syncs/record-matching", "source key and destination identifier are distinct and require uniqueness, non-nullness and destination support", "Equality matching does not establish enterprise identity truth."),
    S("hightouch.mapping", "Field mapping", "Hightouch", "https://hightouch.com/docs/syncs/mapping-data", "field mapping changes can alter reprocessing behavior by sync mode", "UI mapping success does not prove losslessness or business correctness."),
    S("hightouch.cdc", "Change data capture", "Hightouch", "https://hightouch.com/docs/syncs/cdc", "row identity, prior snapshot, added/changed/removed classification and retry state", "Difference-based CDC does not define destination write authority."),
    S("hightouch.salesforce", "Salesforce destination", "Hightouch", "https://hightouch.com/docs/destinations/salesforce", "destination-specific permissions, external IDs, native upsert and delete requirements", "A connector profile does not own Salesforce object invariants."),
    S("rudderstack.reverse-etl", "Reverse ETL pipelines", "RudderStack", "https://www.rudderstack.com/product/reverse-etl/", "table sync, upsert, mirror, mappings and scheduling are separable activation choices", "A product page is weak evidence for exact error and atomicity semantics."),
    S("openapi", "OpenAPI Specification 3.1.1", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.1.1.html", "versioned operations, parameters, request schemas, responses, callbacks and security requirements", "An API description may be incomplete and does not grant authorization."),
    S("http", "RFC 9110 HTTP Semantics", "IETF", "https://datatracker.ietf.org/doc/html/rfc9110", "method safety and idempotency, conditional requests, preconditions and response semantics", "HTTP method properties do not prove provider-side business idempotency."),
    S("problem", "RFC 9457 Problem Details for HTTP APIs", "IETF", "https://datatracker.ietf.org/doc/html/rfc9457", "typed machine-readable API problem responses", "A problem document does not establish retryability or final effect state."),
    S("scim-protocol", "RFC 7644 SCIM Protocol", "IETF", "https://datatracker.ietf.org/doc/html/rfc7644", "discoverable provider capabilities, filter matching, POST/PUT/PATCH/DELETE, atomic resource patch and bulk partial-failure policy", "SCIM resource semantics are not universal destination semantics."),
    S("scim-schema", "RFC 7643 SCIM Core Schema", "IETF", "https://datatracker.ietf.org/doc/html/rfc7643", "server id and client externalId are distinct identity fields with mutability and uniqueness characteristics", "externalId correspondence is not enterprise identity adjudication."),
    S("json-patch", "RFC 6902 JSON Patch", "IETF", "https://datatracker.ietf.org/doc/html/rfc6902", "ordered add, remove, replace, move, copy and test operations", "Patch syntax does not determine domain authorization or compensation."),
    S("merge-patch", "RFC 7396 JSON Merge Patch", "IETF", "https://datatracker.ietf.org/doc/html/rfc7396", "object merge semantics where null has deletion meaning", "Merge Patch cannot preserve every source distinction or array edit intent."),
    S("oauth", "RFC 6749 OAuth 2.0", "IETF", "https://datatracker.ietf.org/doc/html/rfc6749", "scoped delegated access tokens and authorization grants", "Possessing a token does not prove business purpose or data-use permission."),
    S("xacml", "XACML 3.0 Core", "OASIS", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html", "Permit, Deny, Indeterminate and NotApplicable are distinct policy results", "Policy evaluation does not execute or prove an external effect."),
    S("abac", "NIST SP 800-162 ABAC", "NIST", "https://csrc.nist.gov/pubs/sp/800/162/upd2/final", "authorization evaluates subject, object, operation and environment attributes against policy", "ABAC is not a destination mapping or execution protocol."),
    S("stripe-idempotency", "Idempotent requests", "Stripe", "https://docs.stripe.com/api/idempotent_requests", "idempotency keys have provider-specific scope, retention, payload equality and cached-result behavior", "Stripe behavior cannot be assumed for another provider."),
    S("salesforce-upsert", "Upsert by external ID", "Salesforce", "https://developer.salesforce.com/docs/platform/mobile-sdk/guide/ref-rest-apis-upsert.html", "upsert outcome depends on an external-ID field and current destination state", "An external ID match does not prove a globally correct entity link."),
    S("salesforce-composite", "Composite requests", "Salesforce", "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_composite_composite_post.htm", "batched subrequests have provider-specific limits and dependency/rollback behavior", "Composite transport does not imply universal transaction atomicity."),
    S("hubspot-upsert", "Batch upsert CRM objects", "HubSpot", "https://developers.hubspot.com/docs/api-reference/crm-objects-v3/batch/post-crm-v3-objects-objectType-batch-upsert", "batch upsert uses a declared unique idProperty and per-input trace identity", "Provider uniqueness configuration is not source identity evidence."),
    S("google-customer-match", "Customer Match implementation", "Google Ads", "https://developers.google.com/google-ads/api/docs/remarketing/audience-segments/customer-match/get-started", "consent, account eligibility, create/remove separation, partial failure, concurrency and asynchronous job status", "Match rate and job success do not prove person identity or campaign outcome."),
    S("google-job", "Offline user data job", "Google Ads", "https://developers.google.com/google-ads/api/fields/v22/offline_user_data_job", "immutable job type and external id, total job states, failure reason and match-rate range", "Asynchronous job success does not prove every intended downstream consequence."),
    S("lra", "MicroProfile Long Running Actions 2.0", "Eclipse Foundation", "https://download.eclipse.org/microprofile/microprofile-lra-2.0/microprofile-lra-spec-2.0.pdf", "completion, compensation, unknown participant state and failed compensation are explicit", "Compensation is a new effect and is not guaranteed rollback."),
    S("cloudevents", "CloudEvents 1.0.2", "CNCF", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "provider-neutral event identity, source, type, subject and time metadata", "An event envelope does not establish truth, authority or effect completion."),
    S("prov", "PROV-DM", "W3C", "https://www.w3.org/TR/prov-dm/", "attributed entities, activities, agents, generation and derivation", "Provenance relations do not prove causality, completeness or acceptance."),
]


CONTEXTS = [
    {
        "context_id": "context.activation.destination_profile", "name": "Destination Activation Profile",
        "sovereign_question": "Given exact provider contracts and offers, which destination objects, identifiers, fields, operations, constraints, authority requirements and receipt semantics are available for activation?",
        "inside": ["provider contract ACL", "destination object/action profile", "match-key capabilities", "field constraints", "write and delete capabilities", "batch/atomicity limits", "idempotency and concurrency profile", "error and receipt profile"],
        "outside": ["provider API implementation", "credential custody", "destination business rules", "enterprise identity truth", "data-use authorization", "network I/O"],
        "owner": "authority.activation.destination_profile", "status": "specified_candidate",
    },
    {
        "context_id": "context.activation.mapping_plan", "name": "Activation Mapping Plan",
        "sovereign_question": "Given exact source and destination contracts, what deterministic match, field, operation, loss, idempotency and compensation plan is valid before any record is evaluated?",
        "inside": ["source/destination binding", "match-plan compilation", "field mapping", "null/missing/delete semantics", "write-mode lowering", "loss and residual classification", "plan digest", "compatibility and semantic diff"],
        "outside": ["record lookup", "identity adjudication", "effect authorization", "provider execution", "outcome acceptance"],
        "owner": "authority.activation.mapping_plan", "status": "specified_candidate",
    },
    {
        "context_id": "context.activation.mapping_evaluation", "name": "Activation Mapping Evaluation",
        "sovereign_question": "Given one accepted plan, one exact source occurrence and exact externally issued observations, what non-authoritative destination effect proposal and evidence can be derived?",
        "inside": ["record validation", "match-evidence evaluation", "field translation", "operation derivation", "idempotency material derivation", "proposal evidence", "batch classification", "explanation"],
        "outside": ["destination lookup I/O", "identity resolution authority", "purpose/policy decision", "effect authorization", "effect execution", "retry orchestration", "receipt reconciliation"],
        "owner": "authority.activation.mapping_evaluation", "status": "specified_candidate",
    },
]


DECISIONS = {
    "profile": ["provider_contract_identity", "provider_offer_identity", "destination_edition", "object_and_action_vocabulary", "resource_identity_and_addressing", "matchable_identifier_set", "identifier_normalization", "field_schema_and_constraints", "required_readonly_and_computed_fields", "write_mode_capabilities", "null_missing_empty_semantics", "delete_archive_clear_semantics", "patch_replace_merge_semantics", "batch_size_and_order", "atomicity_and_partial_failure", "idempotency_capability_and_scope", "conditional_write_and_concurrency", "asynchronous_job_lifecycle", "rate_and_payload_limits", "authority_and_scope_requirements", "error_taxonomy", "receipt_and_observation_semantics", "capability_freshness", "extension_and_unknown_posture", "canonicalization_and_digest", "resource_budget"],
    "compiler": ["source_contract_identity", "destination_profile_identity", "activation_mapping_identity", "source_record_identity", "destination_object_selection", "source_match_key", "destination_match_key", "match_relation", "match_cardinality", "match_uniqueness_and_nullability", "external_resolution_evidence_requirement", "field_correspondence", "field_cardinality", "type_translation", "constant_and_derived_values", "null_missing_empty_default", "unknown_field_and_enum", "redaction_and_omission", "write_mode", "create_update_upsert_add_remove", "delete_archive_clear", "patch_replace_merge", "change_classification", "reprocessing_posture", "idempotency_basis_and_scope", "concurrency_precondition", "batch_and_partial_failure", "operation_order", "compensation_availability", "loss_taxonomy_and_acceptance", "purpose_requirement_projection", "plan_compatibility", "plan_canonicalization_and_digest", "compile_budget"],
    "evaluator": ["plan_acceptance_reference", "source_occurrence_identity", "source_record_schema_validation", "source_record_identity_validation", "match_evidence_issuer_and_edition", "match_evidence_freshness", "zero_one_many_match_posture", "field_translation_residual", "operation_derivation", "delete_or_removal_evidence", "idempotency_material_derivation", "authority_request_projection", "proposal_identity", "batch_partitioning", "record_and_batch_order", "partial_evaluation_posture", "diagnostic_disclosure", "evaluation_trace", "determinism", "evaluation_budget"],
}


CONTEXT_FOR = {"profile": "context.activation.destination_profile", "compiler": "context.activation.mapping_plan", "evaluator": "context.activation.mapping_evaluation"}
DECISION_ROWS = [{"decision_id": f"decision.activation-mapping.{owner}.{name}", "owner_context": CONTEXT_FOR[owner], "question": f"What exact {name.replace('_', ' ')} applies?", "default": None, "default_law": "forbidden", "status": "declared"} for owner, names in DECISIONS.items() for name in names]


def O(owner: str, name: str, inputs: list[str], output: str) -> dict:
    return {"operation_ref": f"operation.activation-mapping.{owner}.{name}", "input_types": inputs, "output_type": f"Result<{output},ActivationMappingRefusal>", "purity": "pure"}


OPS = {
    "profile": [
        O("profile", "validate_destination_contract_closure", ["DestinationContractClosureRef", "ProviderOfferRef", "ProfilePolicy", "ResourceBudget"], "ValidatedDestinationContractClosure"),
        O("profile", "extract_destination_objects_and_actions", ["ValidatedDestinationContractClosure", "ObjectActionPolicy"], "DestinationObjectActionSet"),
        O("profile", "extract_match_and_field_capabilities", ["ValidatedDestinationContractClosure", "MatchFieldPolicy"], "DestinationMatchFieldCapabilities"),
        O("profile", "extract_write_and_failure_semantics", ["ValidatedDestinationContractClosure", "WriteFailurePolicy"], "DestinationWriteFailureCapabilities"),
        O("profile", "extract_authority_requirements", ["ValidatedDestinationContractClosure", "AuthorityProjectionPolicy"], "DestinationAuthorityRequirementSet"),
        O("profile", "compile_destination_activation_profile", ["DestinationObjectActionSet", "DestinationMatchFieldCapabilities", "DestinationWriteFailureCapabilities", "DestinationAuthorityRequirementSet", "ProfilePolicy"], "DestinationActivationProfile"),
        O("profile", "compare_destination_profiles", ["DestinationActivationProfile", "DestinationActivationProfile", "ProfileCompatibilityPolicy"], "DestinationProfileSemanticDiff"),
        O("profile", "explain_destination_profile", ["DestinationActivationProfile", "ExplanationScope", "ResourceBudget"], "DestinationProfileExplanation"),
    ],
    "compiler": [
        O("compiler", "validate_activation_mapping_context", ["SourceActivationContractRef", "DestinationActivationProfile", "ActivationMappingDeclaration", "ResourceBudget"], "ValidatedActivationMappingContext"),
        O("compiler", "compile_record_match_plan", ["ValidatedActivationMappingContext", "RecordMatchPolicy"], "CompiledRecordMatchPlan"),
        O("compiler", "compile_field_mapping_plan", ["ValidatedActivationMappingContext", "FieldMappingDeclarationSet", "SchemaMappingCompilerRef", "FieldMappingPolicy"], "CompiledActivationFieldPlan"),
        O("compiler", "compile_operation_plan", ["ValidatedActivationMappingContext", "CompiledRecordMatchPlan", "CompiledActivationFieldPlan", "OperationMappingPolicy"], "CompiledActivationOperationPlan"),
        O("compiler", "classify_mapping_residuals", ["CompiledRecordMatchPlan", "CompiledActivationFieldPlan", "CompiledActivationOperationPlan", "LossClassificationPolicy"], "ActivationMappingResidualSet"),
        O("compiler", "validate_loss_acceptance", ["ActivationMappingResidualSet", "LossAcceptanceRef", "LossAcceptancePolicy"], "AcceptedActivationResidualSet"),
        O("compiler", "compile_activation_mapping_plan", ["ValidatedActivationMappingContext", "CompiledRecordMatchPlan", "CompiledActivationFieldPlan", "CompiledActivationOperationPlan", "AcceptedActivationResidualSet", "ActivationPlanPolicy"], "ActivationMappingPlan"),
        O("compiler", "evaluate_mapping_compatibility", ["ActivationMappingPlan", "DestinationProfileSemanticDiff", "MappingCompatibilityPolicy"], "ActivationMappingCompatibility"),
        O("compiler", "explain_activation_mapping_plan", ["ActivationMappingPlan", "ExplanationScope", "ResourceBudget"], "ActivationMappingExplanation"),
    ],
    "evaluator": [
        O("evaluator", "validate_evaluation_context", ["AcceptedActivationMappingPlanRef", "SourceRecordOccurrence", "ExternalMatchObservationSet", "EvaluationPolicy"], "ValidatedActivationEvaluationContext"),
        O("evaluator", "evaluate_record_match", ["ValidatedActivationEvaluationContext", "MatchEvidencePolicy", "ResourceBudget"], "ActivationRecordMatchResult"),
        O("evaluator", "translate_activation_fields", ["ValidatedActivationEvaluationContext", "SchemaMappingExecutorRef", "FieldEvaluationPolicy"], "ActivationFieldResult"),
        O("evaluator", "derive_activation_operation", ["ActivationRecordMatchResult", "ActivationFieldResult", "OperationEvaluationPolicy"], "ProposedDestinationOperation"),
        O("evaluator", "derive_idempotency_material", ["ValidatedActivationEvaluationContext", "ProposedDestinationOperation", "IdempotencyDerivationPolicy"], "ActivationIdempotencyMaterial"),
        O("evaluator", "form_authority_request", ["ValidatedActivationEvaluationContext", "ProposedDestinationOperation", "DestinationAuthorityRequirementSet", "AuthorityRequestPolicy"], "ActivationAuthorityRequest"),
        O("evaluator", "form_activation_effect_proposal", ["ProposedDestinationOperation", "ActivationIdempotencyMaterial", "ActivationAuthorityRequest", "ProposalPolicy"], "ActivationEffectProposal"),
        O("evaluator", "evaluate_activation_batch", ["AcceptedActivationMappingPlanRef", "SourceRecordOccurrenceSet", "ExternalMatchObservationSet", "BatchEvaluationPolicy", "ResourceBudget"], "ActivationProposalBatch"),
        O("evaluator", "explain_activation_proposal", ["ActivationEffectProposal", "ExplanationScope", "ResourceBudget"], "ActivationProposalExplanation"),
    ],
}


COMMON_TYPES = ["ActivationMappingEdition", "ActivationMappingRefusal", "PolicyDigest", "ResourceBudget", "ExplanationScope", "SourceSchemaEditionRef", "DestinationSchemaEditionRef", "DestinationProviderEditionRef", "Diagnostic", "DiagnosticSet"]
TYPES = {
    "profile": COMMON_TYPES + ["DestinationContractClosureRef", "ProviderOfferRef", "ProfilePolicy", "ValidatedDestinationContractClosure", "DestinationObjectId", "DestinationActionId", "DestinationObjectAction", "DestinationObjectActionSet", "DestinationIdentifierCapability", "DestinationFieldCapability", "DestinationMatchFieldCapabilities", "DestinationWriteMode", "DestinationDeleteMode", "DestinationPatchMode", "BatchCapability", "AtomicityProfile", "PartialFailureProfile", "IdempotencyProfile", "ConcurrencyProfile", "AsyncJobProfile", "RateLimitProfile", "ErrorProfile", "ReceiptProfile", "WriteFailurePolicy", "DestinationWriteFailureCapabilities", "AuthorityRequirement", "DestinationAuthorityRequirementSet", "DestinationActivationProfile", "DestinationActivationProfileDigest", "DestinationProfileSemanticDiff", "ProfileCompatibilityPolicy", "DestinationProfileExplanation", "CapabilityFreshness", "ExtensionResidual", "CanonicalizationProfile"],
    "compiler": COMMON_TYPES + ["SourceActivationContractRef", "DestinationActivationProfile", "ActivationMappingDeclaration", "ValidatedActivationMappingContext", "SourceRecordIdentity", "DestinationObjectId", "SourceMatchKey", "DestinationMatchKey", "MatchRelation", "MatchCardinality", "RecordMatchPolicy", "CompiledRecordMatchPlan", "FieldMappingDeclaration", "FieldMappingDeclarationSet", "SchemaMappingCompilerRef", "FieldMappingPolicy", "CompiledActivationFieldPlan", "OperationMappingPolicy", "CompiledActivationOperationPlan", "ActivationMappingResidual", "ActivationMappingResidualSet", "LossClassificationPolicy", "LossAcceptanceRef", "LossAcceptancePolicy", "AcceptedActivationResidualSet", "ActivationPlanPolicy", "ActivationMappingPlan", "ActivationMappingPlanDigest", "DestinationProfileSemanticDiff", "MappingCompatibilityPolicy", "ActivationMappingCompatibility", "ActivationMappingExplanation", "PurposeRequirementProjection", "IdempotencyBasis", "CompensationCapability", "WriteMode", "DeletePosture", "ReprocessingPosture"],
    "evaluator": COMMON_TYPES + ["AcceptedActivationMappingPlanRef", "SourceRecordOccurrence", "SourceRecordOccurrenceSet", "ExternalMatchObservation", "ExternalMatchObservationSet", "MatchEvidenceRef", "MatchEvidenceIssuerRef", "EvaluationPolicy", "ValidatedActivationEvaluationContext", "MatchEvidencePolicy", "ActivationRecordMatchResult", "SchemaMappingExecutorRef", "FieldEvaluationPolicy", "ActivationFieldResult", "OperationEvaluationPolicy", "ProposedDestinationOperation", "IdempotencyDerivationPolicy", "ActivationIdempotencyMaterial", "DestinationAuthorityRequirementSet", "AuthorityRequestPolicy", "ActivationAuthorityRequest", "ProposalPolicy", "ActivationEffectProposal", "ActivationEffectProposalId", "ActivationProposalBatch", "BatchEvaluationPolicy", "ActivationProposalExplanation", "EvaluationTrace", "EvaluationResidual", "ZeroMatch", "UniqueMatch", "AmbiguousMatch", "DeletionEvidenceRef"],
}


SHARED_LAWS = [
    "Source record identity, source entity assertion, destination object identity, destination record identity and record-match evidence are distinct.",
    "A destination contract, normalized destination profile, activation mapping declaration, compiled mapping plan, source occurrence, effect proposal, authorization decision, execution attempt, provider receipt and business outcome are distinct identities.",
    "Proposal is not authorization; authorization is not execution; provider acknowledgement is not durable completion; destination completion is not the intended business outcome.",
    "Every provider-specific object, identifier, field, operation, error, atomicity, idempotency, concurrency and receipt behavior is explicit, editioned and capability checked.",
    "Create, update, upsert, add membership, remove membership, patch, replace, clear, archive and delete are distinct operation semantics.",
    "Null, missing, empty, default, clear and delete remain distinct unless an exact destination profile proves a declared correspondence.",
    "Zero, one and many destination matches are distinct; ambiguous matching emits no effect proposal.",
    "Identity resolution evidence is imported from an accountable issuer and cannot be manufactured by activation mapping.",
    "Unknown completion requires external reconciliation before retry; an idempotency key is evidence only under its exact provider scope and retention window.",
    "Partial failure, asynchronous acceptance, job completion, compensation and failed compensation remain distinct total states.",
    "All semantic operations are pure and finite-budgeted; destination lookup, policy evaluation, authorization and provider I/O occur beyond typed ports.",
    "A model or agent may propose attributed mappings or diagnostics but cannot choose hidden defaults, adjudicate identity, waive loss, authorize or execute effects, accept outcomes or qualify implementations.",
]


def lib(owner: str, library_id: str, name: str, responsibility: str, dependencies: list[str], extra_laws: list[str], refusals: list[str], exclusions: list[str], oracles: list[str]) -> dict:
    return {
        "library_id": library_id, "name": name, "library_kind": "semantic_pure" if owner != "evaluator" else "algorithm_pure", "semantic_owner_context": CONTEXT_FOR[owner], "status": "specified",
        "candidate_responsibility": responsibility, "effect_boundary": "pure_effect_proposals" if owner == "evaluator" else "pure_no_io",
        "public_types": TYPES[owner], "public_traits": ["".join(part.capitalize() for part in library_id.split(".")[1:]) + "Algebra"],
        "operation_refs": [row["operation_ref"] for row in OPS[owner]], "operations": OPS[owner],
        "decision_refs": [row["decision_id"] for row in DECISION_ROWS if f".{owner}." in row["decision_id"]],
        "configuration_contracts": [f"{owner.capitalize()}Policy"], "laws": SHARED_LAWS + extra_laws,
        "invariants": ["all decision points are explicit and no-default", "all identities, editions and evidence issuers are digest bound", "no ambient I/O occurs inside the semantic boundary", "optional model or agent proposals never acquire authority"],
        "error_contracts": refusals + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
        "dependencies": dependencies, "evidence_refs": [row["source_id"] for row in SOURCES], "oracles": oracles + ["two independent implementations and cross-provider differential results"],
        "gaps": ["No implementation is qualified; exact-scope conformance against at least two materially different destination providers remains required."],
        "must_not_own": exclusions, "qualification_required": False,
    }


LIBRARIES = [
    lib("profile", "library.activation.destination_profile.compiler", "Destination Activation Profile Compiler", "normalize an exact provider contract and offer into a deterministic provider-neutral activation capability profile without granting access", ["library.api.contract_parser", "library.provider_offer.reference_closure"], ["Unknown or undocumented provider behavior remains a residual and never becomes a permissive default.", "Security requirements are projected as requirements, not evaluated or satisfied by this compiler.", "Capability freshness is explicit; a stale profile cannot silently describe a current provider edition."], ["DestinationContractUnbound", "ProviderOfferUnbound", "ContractEditionUnsupported", "ObjectIdentityAmbiguous", "IdentifierCapabilityUnknown", "FieldConstraintIncomplete", "WriteSemanticsUnknown", "AtomicityUnknown", "PartialFailureUnknown", "IdempotencyUnknown", "ConcurrencySemanticsUnknown", "AuthorityRequirementUnknown", "ErrorTaxonomyIncomplete", "ReceiptSemanticsUnknown", "CapabilityProfileStale"], ["provider API calls", "credential custody", "destination business invariants", "enterprise identity", "policy decision", "effect execution", "provider qualification"], ["OpenAPI/SCIM/provider-contract normalization fixtures", "capability omission mutation tests", "cross-provider write-mode differential corpus", "stale-edition and undocumented-behavior negative twins"]),
    lib("compiler", "library.activation.mapping.compiler", "Activation Mapping Compiler", "compile exact source and destination contracts plus no-default match, field, operation, loss and recovery decisions into an immutable activation plan", ["library.activation.destination_profile.compiler", "library.schema_mapping.compiler", "library.reference_data.crosswalk_mapping"], ["A mapping plan binds requirements for external match evidence and authority; it does not resolve identity or authorize use.", "Loss acceptance is an external exact-scope reference and cannot be inferred from successful type conversion.", "Plan compatibility is semantic and operational; structural schema compatibility alone is insufficient."], ["SourceContractUnbound", "DestinationProfileUnbound", "MappingDeclarationIncomplete", "SourceIdentityAmbiguous", "DestinationObjectUnsupported", "MatchKeyAmbiguous", "MatchCardinalityUnsupported", "MatchEvidenceRequirementMissing", "FieldUnrepresentable", "NullSemanticsAmbiguous", "WriteModeUnsupported", "DeleteSemanticsUnsupported", "IdempotencyBasisMissing", "ConcurrencyPreconditionMissing", "PartialFailurePostureMissing", "CompensationUnsupported", "LossUnaccepted", "PurposeRequirementMissing", "PlanNondeterministic"], ["source analytical meaning", "provider contract parsing", "record lookup", "identity resolution or adjudication", "purpose authorization", "effect execution", "retry orchestration", "receipt reconciliation"], ["golden mapping-plan fixtures", "zero/one/many match decision tables", "null/missing/clear/delete cross-product tests", "write-mode lowering model tests", "loss-acceptance and semantic-diff mutation tests"]),
    lib("evaluator", "library.activation.mapping.evaluator", "Activation Mapping Evaluator", "evaluate one accepted plan over exact records and externally issued match observations to emit non-authoritative effect proposals and evidence", ["library.activation.mapping.compiler", "library.schema_mapping.executor"], ["The evaluator consumes observations supplied by ports and performs no destination lookup or identity search itself.", "Every proposal binds the accepted plan, source occurrence, match evidence, translation trace, operation and idempotency material.", "An authority request is a typed question to an external policy owner; it is never a Permit decision.", "A batch result preserves every record refusal and cannot turn partial evaluation into total success."], ["MappingPlanUnaccepted", "SourceOccurrenceUnbound", "SourceRecordInvalid", "SourceIdentityMissing", "MatchEvidenceUnbound", "MatchEvidenceStale", "MatchEvidenceIssuerUntrusted", "NoDestinationMatch", "AmbiguousDestinationMatch", "FieldTranslationResidual", "DeleteEvidenceMissing", "IdempotencyMaterialInvalid", "AuthorityRequestIncomplete", "ProposalNondeterministic", "BatchBudgetExceeded"], ["destination or identity lookup I/O", "identity evidence issuance", "data-use policy evaluation", "authorization decision", "effect execution", "retry and compensation execution", "provider receipt interpretation", "business outcome acceptance"], ["record-level golden proposal fixtures", "ambiguous-match no-effect properties", "proposal determinism tests", "batch partition/order metamorphic tests", "authority separation and agent-authority negative tests"]),
]


LENSES = [
    ("value", "Operators need one activation outcome, while destination ACLs, plan compilation and hot-path evaluation have independently reusable consumers.", "Retain one operated product composed from three pure libraries plus separately owned authorization, execution and receipt contracts."),
    ("semantic", "Provider capability, mapping-plan and record-evaluation vocabularies have different identities and truth owners.", "Use three contexts and published references; never let provider terminology become the canonical activation language."),
    ("behavior", "Profile compilation is contract normalization, plan compilation is constraint solving, and evaluation is a total per-record function.", "Split cold profile/plan compilation from hot evaluation and from effect execution."),
    ("authority", "Providers issue API contracts and receipts, identity owners issue match evidence, policy owners decide use, and effect ports execute.", "Mapping libraries only validate references and emit questions/proposals; they mint no authority."),
    ("consistency", "Profiles and plans require atomic digest integrity; evaluation binds one accepted plan and one exact record/evidence cut.", "Link aggregates with immutable refs and preserve per-record partial outcomes."),
    ("variability", "Objects, identifiers, fields, write modes, null/delete behavior, batches, atomicity, idempotency and consent vary independently.", "Expose every axis as editioned no-default decisions and capability constraints."),
    ("software", "The three seams have different dependencies, caches, change rates and test corpora.", "Split the coarse activation_mapping library into three exact libraries; import generic schema mapping and effect contracts."),
    ("operation", "Compilation is cold-path and pure; evaluation is hot-path and pure; lookups and writes are effectful and failure-prone.", "Represent observations, authority requests, effect proposals and receipts as distinct port carriers."),
    ("economics", "Contract refresh, compilation cost, evaluation throughput, lookup cost and destination API usage are separately measurable.", "Allow independent optimization and provider exit without pretending each library is a commercial product."),
    ("empirical", "Reverse-ETL products and provider APIs repeatedly expose matching, field mapping, modes, deletes, limits and per-record failures differently.", "Generalize the decision axes, not vendor defaults or names."),
    ("analytical", "Matching is a scoped relation with cardinality, mapping is partial typed transformation, and effect derivation is a total/refusal function.", "Make residual information loss, ambiguity and equivalence domains explicit."),
    ("system", "Wrong-person writes, destructive null/delete coercion, duplicate effects, stale authorization, partial failure and false success are primary hazards.", "Fail closed, bind exact evidence, emit no effect on ambiguity, and reconcile effects outside this boundary."),
]


LENS_METHODS = {
    "value": ["method.business.jtbd", "method.business.capability_map", "method.business.product_split_merge"], "semantic": ["method.domain.ddd", "method.domain.terminology", "method.information.conceptual_data"], "behavior": ["method.domain.eventstorming", "method.work.statecharts", "method.work.dmn"], "authority": ["method.trust.threat_model", "method.systems.stpa"], "consistency": ["method.domain.ddd", "method.formal.alloy", "method.formal.design_by_contract"], "variability": ["method.variability.foda", "method.variability.decision_model", "method.variability.product_line"], "software": ["method.architecture.coupling", "method.architecture.hexagonal", "method.variability.algebraic_api"], "operation": ["method.operations.resilience", "method.operations.capacity", "method.operations.sre"], "economics": ["method.operations.finops", "method.business.product_split_merge"], "empirical": ["method.evidence.systematic_review", "method.evidence.repository_mining", "method.evidence.red_team"], "analytical": ["method.analytics.or", "method.formal.property_testing", "method.formal.theorem_proving"], "system": ["method.systems.stpa", "method.trust.fmea_fta", "method.strategy.systems_thinking"],
}
LENS_ROWS = [{"lens_id": f"lens.activation-mapping.{name}", "lens": name, "question": "What does this lens require of the activation-mapping boundaries?", "finding": finding, "boundary_consequence": consequence, "method_refs": LENS_METHODS[name], "status": "applied"} for name, finding, consequence in LENSES]


BOUNDARY_VERDICTS = [
    {"verdict_id": "verdict.activation-mapping.split", "subject_refs": [row["library_id"] for row in LIBRARIES], "supersedes_abstract_ref": "library.activation_mapping", "disposition": "split_coarse_contract", "rationale": "Destination contract normalization, mapping constraint compilation and per-record proposal evaluation differ in owner vocabulary, lifecycle, dependencies, rate, failure states and substitution seam.", "shared_contract_types": ["DestinationActivationProfile", "ActivationMappingPlan", "ActivationMappingRefusal"], "merge_falsifier": "Merge only if profile refresh, plan compilation and record evaluation cannot be versioned, cached, tested or substituted independently.", "status": "candidate_boundary_adjudicated_not_ratified"},
    {"verdict_id": "verdict.activation-mapping.effect-boundary", "subject_refs": ["library.activation.mapping.evaluator", "library.csp.decision.effect-port", "library.spt.policy_enforcer", "library.lpe.runtime-receipt-core"], "disposition": "retain_separate_authority_and_effect_contracts", "rationale": "The evaluator emits an ActivationEffectProposal and ActivationAuthorityRequest. External policy owners authorize; effect ports execute; runtime receipt cores record and reconcile. Combining these would let a mapping authorize itself.", "status": "candidate_boundary_adjudicated_not_ratified"},
    {"verdict_id": "verdict.activation-mapping.imported-neighbors", "subject_refs": [row["library_id"] for row in LIBRARIES], "disposition": "retain_import_boundaries", "rationale": "API parsing, provider offers, schema mapping, reference crosswalks, identity/master evidence, data-use policy, authorization, execution, orchestration, receipt reconciliation and outcome acceptance are separately owned.", "imported_contract_refs": ["library.api.contract_parser", "library.provider_offer.reference_closure", "library.schema_mapping.compiler", "library.schema_mapping.executor", "library.reference_data.crosswalk_mapping", "library.csp.decision.effect-port", "library.spt.policy_enforcer", "library.lpe.runtime-receipt-core"], "status": "candidate_boundary_adjudicated_not_ratified"},
]


NEGATIVES = [
    ("contract_authority", "An OpenAPI or connector contract grants permission to invoke every described operation.", "Project security requirements and require a separate exact authorization decision."),
    ("latest_contract", "The current provider API documentation may be consulted during evaluation.", "Compile and digest an exact destination contract/profile edition before evaluation."),
    ("unknown_capability", "Undocumented provider behavior may use a reasonable default.", "Retain an explicit residual or refuse."),
    ("provider_names", "Provider object and action names are the canonical activation vocabulary.", "Normalize through a versioned ACL while retaining original identities."),
    ("external_id_identity", "Equal external IDs prove two records are the same real-world entity.", "Import scoped identity/match evidence from its accountable owner."),
    ("email_unique", "Email is a stable unique identity key by convention.", "Require exact uniqueness, normalization, scope and freshness evidence."),
    ("many_first", "When several destination rows match, update the first one.", "Refuse ambiguous matches and emit no proposal."),
    ("no_match_upsert", "No match always means create under upsert.", "Apply the exact compiled operation and authority policy."),
    ("field_name", "Equal field names imply equal meaning and safe mapping.", "Use exact schema/semantic bindings and classify residual loss."),
    ("null_clear", "Source null means clear the destination field.", "Keep null, missing, empty, default, clear and delete distinct."),
    ("missing_default", "A missing source field may use the provider default.", "Require an explicit construction policy and account for information loss."),
    ("upsert_equivalence", "Every destination implements upsert identically.", "Lower only through an exact destination capability profile."),
    ("patch_replace", "PATCH, merge and replacement are interchangeable.", "Preserve their field, array, null, atomicity and precondition semantics."),
    ("delete_archive", "Delete, archive, clear and membership removal have the same effect.", "Represent them as distinct operations and require exact authority."),
    ("batch_atomic", "A successful batch request means every record committed atomically.", "Interpret per-item and batch receipts under the provider profile."),
    ("async_success", "HTTP acceptance means the asynchronous destination job succeeded.", "Retain accepted/running/success/failed and unknown as distinct states."),
    ("partial_total", "Most records succeeded, therefore the activation succeeded.", "Preserve every record refusal and apply the declared partial-failure posture externally."),
    ("idempotency_universal", "Supplying any idempotency key makes any retry safe forever.", "Bind provider scope, payload equality, retention, operation and exact attempt identity."),
    ("http_idempotent", "PUT or DELETE guarantees the whole business effect is idempotent.", "Treat HTTP semantics as one premise and require provider/domain evidence."),
    ("retry_timeout", "A timed-out effect can be retried immediately.", "Reconcile unknown completion through the effect protocol before retry."),
    ("compensation_rollback", "Compensation restores the exact prior state.", "Model compensation as a separately authorized effect with possible failure and residual harm."),
    ("token_purpose", "A valid OAuth token proves the requested use has an allowed purpose.", "Obtain a distinct data-use/authorization decision."),
    ("mapping_permission", "An accepted field mapping authorizes disclosure to the destination.", "Project an authority request and wait for an external decision."),
    ("proposal_intent", "An effect proposal is an authorized effect intent.", "Keep proposal, authority decision, intent, attempt and receipt as distinct carriers."),
    ("receipt_outcome", "A destination success receipt proves the business outcome occurred.", "Measure and accept downstream outcome separately."),
    ("lookup_inside", "The pure evaluator may query the destination when match evidence is absent.", "Require exact externally issued observations or refuse."),
    ("plan_live_schema", "A compiled mapping plan remains valid after a destination schema change.", "Run semantic compatibility and compile a new edition when invalidated."),
    ("reprocess_safe", "Reprocessing all source rows is harmless.", "Bind operation, idempotency, change state and destructive behavior before reprocessing."),
    ("order_irrelevant", "Record and batch ordering never changes destination outcomes.", "Declare ordering and dependency semantics in the profile and plan."),
    ("loss_success", "Successful serialization proves the mapping is lossless.", "Classify semantic, identity, null, precision and operation loss separately."),
    ("agent_mapping", "An agent may choose a likely match or destructive mapping when confidence is high.", "Agents may only propose attributed candidates; deterministic rules and accountable authorities decide."),
    ("agent_waiver", "An agent may waive consent, partial failure or compensation requirements to finish a run.", "Refusals and authority gates are non-waivable by model or agent output."),
]
NEGATIVE_ROWS = [{"negative_id": f"negative.activation-mapping.{ident}", "unsafe_inference": unsafe, "required_behavior": required, "status": "active"} for ident, unsafe, required in NEGATIVES]


COMPILER_ROWS = []
for library in LIBRARIES:
    stem = library["library_id"].removeprefix("library.")
    requirement, offer = f"requirement.{stem}.implementation", f"offer.{stem}.reference"
    COMPILER_ROWS.extend([
        {"record_kind": "capability_requirement", "requirement_id": requirement, "subject_ref": library["library_id"], "required_operations": library["operation_refs"], "required_decisions": library["decision_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": offer, "subject_ref": library["library_id"], "claimed_operations": library["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": requirement, "offer_ref": offer, "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable implementation.", "selectable": False, "status": "declared"},
    ])


FILES = {"sources.jsonl": SOURCES, "bounded-contexts.jsonl": CONTEXTS, "decision-points.jsonl": DECISION_ROWS, "boundary-lens-adjudication.jsonl": LENS_ROWS, "boundary-verdicts.jsonl": BOUNDARY_VERDICTS, "library-contracts.jsonl": LIBRARIES, "compiler-contracts.jsonl": COMPILER_ROWS, "negative-twins.jsonl": NEGATIVE_ROWS}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id": "operational_activation_mapping_v0_1_0", "as_of": AS_OF, "edition": EDITION, "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False, "qualified_implementation_count": 0}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS activation mapping: {len(SOURCES)} sources, 3 contexts, {len(DECISION_ROWS)} decisions, 3 exact libraries, {sum(len(v) for v in OPS.values())} operations, 12 lenses")


if __name__ == "__main__":
    main()
