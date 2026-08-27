#!/usr/bin/env python3
"""Build exact, provider-neutral data-use-policy semantic and compiler contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for r in rows)


def S(ident: str, title: str, publisher: str, url: str, scope: str, limit: str, kind: str = "official_specification") -> dict:
    return {"source_id": f"source.data-use-policy.{ident}", "title": title, "publisher": publisher,
            "url": url, "source_kind": kind, "claim_scope": scope, "scope_limit": limit}


SOURCES = [
    S("oasis.xacml3", "eXtensible Access Control Markup Language Version 3.0", "OASIS Open", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html", "PAP/PDP/PEP/PIP roles, request context, policy sets, effects, combining algorithms, obligations, advice and four-valued decisions", "XACML is an authorization language and processing model; it does not establish resource truth, legal validity, consent, enforcement completion or universal data-use semantics."),
    S("oasis.xacml-admin", "XACML 3.0 Administration and Delegation Profile Version 1.0", "OASIS Open", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-administration-v1-spec-en.html", "issuer authority, administrative policy, delegation reduction and constrained policy issuance", "A signed or supplied policy is only a candidate until issuer authority is established; the profile leaves revocation mechanisms open."),
    S("oasis.xacml-sod", "XACML v3.0 Separation of Duties Version 1.0", "OASIS Open", "https://docs.oasis-open.org/xacml/xacml-3.0-duties/v1.0/xacml-3.0-duties-v1.0.html", "dynamic and static separation-of-duty policy patterns", "The profile supplies authorization patterns, not enterprise role truth or workflow execution evidence."),
    S("w3c.odrl22", "ODRL Information Model 2.2", "W3C", "https://www.w3.org/TR/odrl-model/", "permissions, prohibitions, duties, constraints, parties, assets and conflict strategies", "ODRL expresses policies but does not prescribe enforcement, legal validity, identity resolution or one universal conflict strategy."),
    S("nist.800-162", "SP 800-162: Guide to Attribute Based Access Control", "NIST", "https://csrc.nist.gov/pubs/sp/800/162/upd2/final", "subject, object, operation and environment attributes plus PDP, PEP and attribute-source separation", "ABAC guidance does not establish attribute correctness, purpose compatibility, consent or enforcement completion."),
    S("nist.800-207", "SP 800-207: Zero Trust Architecture", "NIST", "https://csrc.nist.gov/pubs/sp/800/207/final", "policy engine, policy administrator, enforcement point, continuous evaluation and resource-centric control", "Zero-trust architecture is not a domain policy language, privacy-law adjudicator or proof of correct deployment."),
    S("ietf.rfc3198", "RFC 3198: Terminology for Policy-Based Management", "IETF", "https://www.rfc-editor.org/rfc/rfc3198.html", "policy rule, repository, decision point, enforcement point, decision process and result distinctions", "Terminology does not define one executable policy language or qualify a provider."),
    S("openid.authzen1", "Authorization API 1.0", "OpenID Foundation", "https://openid.net/specs/authorization-api-1_0.html", "interoperable request/decision protocol between PEPs and PDPs", "Protocol interoperability does not establish policy semantics, input truth, enforcement or obligation discharge."),
    S("w3c.dpv2", "Data Privacy Vocabulary Version 2.0", "W3C Data Privacy Vocabularies and Controls CG", "https://www.w3.org/community/reports/dpvcg/CG-FINAL-dpv-20240801/", "purpose, processing, personal-data, legal-basis, consent-status and privacy-control vocabulary", "DPV is a Community Group vocabulary, not a legal determination, policy evaluator or enforcement receipt."),
    S("iso.27560", "ISO/IEC TS 27560:2023 Consent Record Information Structure", "ISO", "https://www.iso.org/standard/80392.html", "interoperable consent records, receipts and lifecycle information", "Consent records are evidence inputs; their presence alone does not prove lawful processing or current valid consent."),
    S("eu.gdpr", "Regulation (EU) 2016/679", "European Union", "https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng", "purpose limitation, lawful basis, consent evidence, withdrawal and data-subject rights", "Jurisdictional law must be lowered through separately governed legal/policy packs; this corpus does not adjudicate legal compliance."),
    S("park-sandhu.uconabc", "The UCONABC Usage Control Model", "ACM", "https://doi.org/10.1145/984334.984339", "authorizations, obligations, conditions, continuity and mutable attributes before, during and after usage", "UCON is a conceptual family, not an interoperable API or qualified runtime implementation.", "primary_research_paper"),
    S("opa.management", "OPA Management APIs and Architecture", "Open Policy Agent", "https://www.openpolicyagent.org/docs/management-introduction", "distributed policy bundles, decision telemetry, status and dynamic configuration", "OPA documents one implementation architecture; Rego and its management APIs are provider-specific." , "official_implementation_documentation"),
    S("opa.decision-logs", "OPA Decision Logs", "Open Policy Agent", "https://www.openpolicyagent.org/docs/management-decision-logs", "decision identity, input, policy-bundle revision, result, trace and sensitive-field masking", "A decision log proves a reported evaluation occurrence, not enforcement, obligation fulfillment or legal correctness.", "official_implementation_documentation"),
    S("cedar.authorization", "Cedar Authorization", "Cedar Policy", "https://docs.cedarpolicy.com/auth/authorization.html", "principal-action-resource-context requests and permit/forbid evaluation", "Cedar's allow/deny and skip-on-error semantics are one language profile, not universal policy semantics.", "official_implementation_documentation"),
    S("cedar.validation", "Cedar Policy Validation", "Cedar Policy", "https://docs.cedarpolicy.com/policies/validation.html", "schema-bound static validation and validation-soundness boundary", "Static validity does not prove policy intent, data completeness, legal validity or enforcement.", "official_implementation_documentation"),
    S("google.zanzibar", "Zanzibar: Google's Consistent, Global Authorization System", "USENIX", "https://www.usenix.org/system/files/atc19-pang.pdf", "relationship-based authorization, external consistency, causal ordering and consistency tokens", "Zanzibar is production evidence for a relationship authorization design, not a universal data-use policy language.", "primary_research_paper"),
]


def C(slug: str, name: str, question: str, outside: list[str]) -> dict:
    return {"context_id": f"context.data_use_policy.{slug}", "name": name, "sovereign_question": question,
            "inside": ["exact identities", "editioned decisions", "typed refusals", "replayable laws"],
            "outside": outside + ["provider qualification", "ambient persistence", "unauthorized external effects"],
            "owner": f"authority.data_use_policy.{slug}", "status": "specified_candidate"}


CONTEXTS = [
    C("administration", "Policy Definition and Administration", "Which authority-issued policy edition is valid for which scope and time, and how is it validated, published, superseded or revoked?", ["principal identity", "resource truth", "purpose or classification taxonomy ownership", "consent or legal-basis adjudication"]),
    C("decision", "Policy Decision", "For exact policy and attribute cuts, what deterministic decision, reasons, advice and obligations result for a subject, action, resource, purpose and environment?", ["attribute-source truth", "policy enforcement", "business-command authorization", "legal compliance verdict"]),
    C("usage", "Usage Obligation and Decision Evidence", "Which decision-derived obligations or reevaluation requirements must be handed to external enforcement, and what evaluation and effect receipts remain provable?", ["effect execution", "entitlement issuance", "data mutation or disclosure", "obligation self-attestation"]),
]


CONTEXT_BY_SEAM = {
    "policy_edition": "administration", "request_context": "decision", "rule_combination": "administration",
    "decision_evaluation": "decision", "obligation_protocol": "usage", "decision_evidence": "usage",
}


DECISIONS = {
    "policy_edition": ["language_profile", "identity_and_version", "issuer_authority_and_delegation", "validity_and_activation", "supersession_and_revocation", "publication_integrity"],
    "request_context": ["principal_and_subject_binding", "action_vocabulary", "resource_identity", "purpose_processing_and_legal_basis", "attribute_source_and_cut", "missing_conflict_and_redaction"],
    "rule_combination": ["applicability", "effect_lattice", "combining_algorithm", "ordering_and_specificity", "function_profile", "indeterminate_and_error_semantics"],
    "decision_evaluation": ["policy_cut", "request_cut", "decision_mode", "explanation_and_disclosure", "cache_and_replay", "reevaluation_trigger"],
    "obligation_protocol": ["obligation_versus_advice", "recipient_and_capability", "timing_and_continuity", "dispatch_retry_and_idempotency", "outcome_and_failure", "termination_and_compensation"],
    "decision_evidence": ["occurrence_identity", "evidence_content", "policy_input_and_engine_digest", "sensitive_field_protection", "append_and_retention", "disclosure_and_verification"],
}


DECISION_ROWS = [{"decision_id": f"decision.data_use_policy.{seam}.{d}",
                  "owner_context": f"context.data_use_policy.{CONTEXT_BY_SEAM[seam]}",
                  "question": f"What exact {d.replace('_', ' ')} applies?", "default": None,
                  "default_law": "forbidden", "status": "declared"}
                 for seam, values in DECISIONS.items() for d in values]


def O(seam: str, name: str, inputs: list[str], output: str) -> dict:
    return {"operation_ref": f"operation.data_use_policy.{seam}.{name}", "input_types": inputs,
            "output_type": f"Result<{output},{''.join(x.title() for x in seam.split('_'))}Refusal>", "purity": "pure"}


SPECS = [
    {"id": "library.data_use_policy.policy_edition", "seam": "policy_edition", "name": "Policy Edition and Administration", "kind": "effect_port",
     "types": ["PolicyId", "PolicyEditionId", "PolicyLanguageProfile", "PolicyDocument", "PolicySet", "PolicyRule", "Permission", "Prohibition", "DutyExpression", "AdviceExpression", "PolicyScope", "IssuerRef", "IssuerAuthorityEvidence", "DelegationChain", "ValidityInterval", "ActivationCut", "PolicyDigest", "PolicyPublicationIntent", "PolicyPublicationReceipt", "PolicyRevocationIntent", "PolicyRevocationReceipt", "PolicyEditionRefusal"],
     "ops": [O("policy_edition", "validate_policy_edition", ["PolicyDocument", "PolicyLanguageProfile", "PolicySchema", "IssuerAuthorityEvidence"], "ValidatedPolicyEdition"), O("policy_edition", "plan_policy_publication", ["ValidatedPolicyEdition", "ActivationPolicy", "PublicationAuthority"], "PolicyPublicationIntent"), O("policy_edition", "plan_policy_revocation", ["PolicyEditionId", "RevocationEvidence", "RevocationPolicy"], "PolicyRevocationIntent"), O("policy_edition", "reconcile_policy_effect", ["PolicyLifecycleIntent", "PolicyLifecycleReceipt"], "PolicyLifecycleState")],
     "laws": ["Policy identity, immutable edition, document occurrence, active deployment and provider bundle are distinct.", "Syntax validity, schema validity, issuer authority, policy approval, activation and legal validity are distinct.", "A supplied or signed policy without an authorized issuer chain is not eligible for evaluation.", "Publication, activation, supersession, revocation and physical deletion are distinct lifecycle facts.", "Revocation changes current eligibility without erasing the policy edition or historical decisions.", "Policy publication and revocation are explicit effect intents reconciled from receipts; a pure library never mutates a repository."],
     "errors": ["LanguageProfileUnsupported", "PolicyIdentityCollision", "PolicyInvalid", "IssuerUnbound", "DelegationInvalid", "ValidityAmbiguous", "PublicationAuthorityMissing", "LifecycleCompletionUnknown"], "deps": [],
     "evidence": ["source.data-use-policy.oasis.xacml3", "source.data-use-policy.oasis.xacml-admin", "source.data-use-policy.w3c.odrl22", "source.data-use-policy.opa.management"]},
    {"id": "library.data_use_policy.request_context", "seam": "request_context", "name": "Policy Request Context Binding", "kind": "algorithm_pure",
     "types": ["DecisionRequestId", "PrincipalRef", "SubjectRef", "ActionRef", "ResourceRef", "PurposeRef", "ProcessingRef", "DataCategoryRef", "LegalBasisRef", "ConsentRecordRef", "EnvironmentAttribute", "AttributeName", "AttributeValue", "AttributeIssuerRef", "AttributeEvidence", "AttributeValidity", "AttributeRecordingTime", "AttributeCut", "MissingAttributeSet", "ConflictingAttributeSet", "SensitiveAttributeSet", "BoundDecisionRequest", "RequestContextRefusal"],
     "ops": [O("request_context", "bind_decision_request", ["RawDecisionRequest", "RequestVocabularyProfile", "IdentityBindings", "AttributeEvidenceSet"], "BoundDecisionRequest"), O("request_context", "validate_attribute_cut", ["BoundDecisionRequest", "AttributeSourcePolicy", "TemporalCut", "MissingAttributePolicy"], "ValidatedRequestCut"), O("request_context", "derive_sensitive_view", ["ValidatedRequestCut", "DisclosurePolicy"], "ProtectedRequestView"), O("request_context", "compare_request_cuts", ["ValidatedRequestCut", "ValidatedRequestCut", "ComparisonPolicy"], "RequestCutDiff")],
     "laws": ["Principal, authenticated subject, acting subject, data subject, issuer and policy author are distinct roles.", "Purpose, processing operation, requested action, resource, data category, legal basis and consent record are distinct references.", "The policy product consumes externally owned editioned vocabulary and evidence references; it never registers purposes, classifies data, issues identity or adjudicates lawfulness.", "Attribute value, attribute issuer, observation time, validity time, recording time and evidence remain explicit.", "Missing, unknown, inapplicable, withheld, redacted, stale and conflicting attributes remain distinct.", "A classification, consent record, legal-basis reference or relationship tuple is input evidence and never grants access by itself."],
     "errors": ["PrincipalUnresolved", "ActionUnresolved", "ResourceUnresolved", "PurposeUnresolved", "AttributeIssuerUnbound", "AttributeMissing", "AttributeConflict", "AttributeStale", "SensitiveDisclosureForbidden"], "deps": [],
     "evidence": ["source.data-use-policy.nist.800-162", "source.data-use-policy.w3c.dpv2", "source.data-use-policy.iso.27560", "source.data-use-policy.google.zanzibar"]},
    {"id": "library.data_use_policy.rule_combination", "seam": "rule_combination", "name": "Policy Rule Compilation and Combination", "kind": "algorithm_pure",
     "types": ["RuleId", "RuleEdition", "RuleTarget", "RuleCondition", "RuleEffect", "ApplicabilityResult", "DecisionEffect", "ExtendedIndeterminate", "NotApplicable", "CombiningAlgorithmId", "CombiningAlgorithmEdition", "RuleOrder", "SpecificityRelation", "FunctionProfile", "CompiledRule", "CompiledPolicySet", "ConflictSet", "CombinationTrace", "ResidualDecision", "RuleCombinationRefusal"],
     "ops": [O("rule_combination", "compile_policy_set", ["ValidatedPolicyEditionSet", "RequestVocabularyProfile", "FunctionProfile"], "CompiledPolicySet"), O("rule_combination", "evaluate_applicability", ["CompiledPolicySet", "ValidatedRequestCut"], "ApplicabilityVector"), O("rule_combination", "combine_rule_results", ["RuleEvaluationVector", "CombiningAlgorithmEdition", "CombinationBudget"], "CombinedPolicyResult"), O("rule_combination", "explain_combination", ["CombinedPolicyResult", "DisclosurePolicy"], "CombinationTrace")],
     "laws": ["Permission, prohibition, duty, advice, applicability and final decision are distinct semantic types.", "Permit, deny, not-applicable and indeterminate remain distinct; no result is collapsed into a boolean before an explicit lowering policy.", "Rule order has meaning only for an explicitly ordered combining algorithm; file or retrieval order never creates ambient precedence.", "Every custom function and combining algorithm has an exact identity, edition, totality contract and resource budget.", "Unsupported function, missing attribute, evaluation error and conflicting applicable policies follow declared semantics and remain replayable.", "Compilation and combination are deterministic over exact policy, function, algorithm and request cuts or return a typed refusal."],
     "errors": ["PolicySetOpen", "FunctionUnsupported", "AlgorithmUnbound", "ApplicabilityIndeterminate", "PrecedenceCycle", "EvaluationError", "CombinationBudgetExceeded", "CombinationNondeterministic"], "deps": ["library.data_use_policy.policy_edition", "library.data_use_policy.request_context"],
     "evidence": ["source.data-use-policy.oasis.xacml3", "source.data-use-policy.w3c.odrl22", "source.data-use-policy.cedar.authorization", "source.data-use-policy.cedar.validation"]},
    {"id": "library.data_use_policy.decision_evaluation", "seam": "decision_evaluation", "name": "Policy Decision Evaluation", "kind": "algorithm_pure",
     "types": ["PolicyCutId", "RequestCutId", "EvaluatorProfile", "EvaluatorEdition", "DecisionOccurrenceId", "DecisionEffect", "DecisionStatus", "DecisionReason", "DeterminingRuleRef", "DecisionObligation", "DecisionAdvice", "DecisionTrace", "DecisionExplanation", "DecisionCacheKey", "ReevaluationTrigger", "EvaluationBudget", "PolicyDecision", "PolicyDecisionRefusal"],
     "ops": [O("decision_evaluation", "evaluate_decision", ["CompiledPolicySet", "ValidatedRequestCut", "EvaluatorProfile", "EvaluationBudget"], "PolicyDecision"), O("decision_evaluation", "explain_decision", ["PolicyDecision", "DecisionTrace", "ExplanationPolicy"], "DecisionExplanation"), O("decision_evaluation", "derive_cache_key", ["PolicyCutId", "RequestCutId", "EvaluatorEdition", "CachePolicy"], "DecisionCacheKey"), O("decision_evaluation", "replay_decision", ["PolicyDecision", "CompiledPolicySet", "ValidatedRequestCut", "EvaluatorProfile"], "DecisionReplayResult")],
     "laws": ["A decision binds exact policy, request, attribute, evaluator, function and clock cuts.", "A policy decision is not authentication, entitlement issuance, approval, enforcement, disclosure, mutation or obligation fulfillment.", "Returned obligations and advice are decision outputs; only obligations understood by an enforcement capability may participate in a permitted effect.", "Cached decisions are reusable only under the declared key, validity, revocation and causal-consistency policy.", "Explanation is a disclosure-controlled projection of a trace and never changes the decision.", "Ongoing use requires explicit reevaluation triggers; a prior permit does not authorize an unbounded future session."],
     "errors": ["PolicyCutUnavailable", "RequestCutInvalid", "EvaluatorUnsupported", "DecisionIndeterminate", "ObligationUnsupported", "CacheKeyIncomplete", "ReevaluationRequired", "EvaluationBudgetExceeded"], "deps": ["library.data_use_policy.rule_combination"],
     "evidence": ["source.data-use-policy.oasis.xacml3", "source.data-use-policy.nist.800-162", "source.data-use-policy.openid.authzen1", "source.data-use-policy.park-sandhu.uconabc", "source.data-use-policy.google.zanzibar"]},
    {"id": "library.data_use_policy.obligation_protocol", "seam": "obligation_protocol", "name": "Usage Obligation and Enforcement Protocol", "kind": "effect_port",
     "types": ["ObligationId", "ObligationEdition", "ObligationAssignment", "ObligationRecipientRef", "EnforcementCapabilityRef", "ObligationTiming", "BeforeUse", "OngoingUse", "AfterUse", "ObligationDispatchIntent", "ObligationDispatchReceipt", "ObligationOutcome", "ObligationEvidence", "UsageSessionRef", "ReevaluationIntent", "TerminationIntent", "CompensationIntent", "EnforcementReceiptRef", "ObligationState", "ObligationProtocolRefusal"],
     "ops": [O("obligation_protocol", "plan_obligation_dispatch", ["PolicyDecision", "EnforcementCapabilitySet", "ObligationDispatchPolicy"], "ObligationDispatchPlan"), O("obligation_protocol", "reconcile_obligation_receipt", ["ObligationDispatchIntent", "ObligationDispatchReceipt", "ReceiptPolicy"], "ObligationState"), O("obligation_protocol", "plan_usage_reevaluation", ["UsageSessionRef", "ReevaluationTrigger", "UsageObservationSet"], "ReevaluationIntent"), O("obligation_protocol", "plan_usage_termination", ["UsageSessionRef", "PolicyDecision", "EnforcementCapabilitySet", "TerminationPolicy"], "TerminationIntent")],
     "laws": ["Obligation expression, returned obligation, assignment, dispatch intent, dispatch receipt, execution outcome and verified fulfillment are distinct.", "Advice may be ignored under its language profile; an obligation cannot be silently ignored or treated as fulfilled.", "The policy product coordinates effect intents but does not execute access, disclosure, deletion, masking, notification, payment or other business effects.", "Unknown dispatch completion is reconciled before retry; idempotency and effect identity are explicit.", "Before-use, ongoing-use and after-use obligations have distinct timing and failure postures.", "Revocation or failed reevaluation may produce termination and compensation intents but never self-attests that termination occurred."],
     "errors": ["RecipientUnresolved", "CapabilityUnsupported", "TimingAmbiguous", "DispatchCompletionUnknown", "ReceiptInvalid", "ObligationOverdue", "ReevaluationUnavailable", "TerminationUnconfirmed"], "deps": ["library.data_use_policy.decision_evaluation"],
     "evidence": ["source.data-use-policy.oasis.xacml3", "source.data-use-policy.nist.800-207", "source.data-use-policy.openid.authzen1", "source.data-use-policy.park-sandhu.uconabc", "source.data-use-policy.ietf.rfc3198"]},
    {"id": "library.data_use_policy.decision_evidence", "seam": "decision_evidence", "name": "Policy Decision Evidence", "kind": "effect_port",
     "types": ["DecisionEvidenceId", "DecisionOccurrence", "PolicyCutDigest", "RequestCutDigest", "AttributeCutDigest", "EvaluatorDigest", "DecisionTraceDigest", "DecisionEvidenceRecord", "SensitiveFieldMask", "ProtectedDecisionRecord", "DecisionEvidenceAppendIntent", "DecisionEvidenceAppendReceipt", "DecisionDisclosureView", "EvidenceRetentionBinding", "EnforcementReceiptRef", "ObligationReceiptRef", "VerificationResult", "DecisionEvidenceRefusal"],
     "ops": [O("decision_evidence", "assemble_decision_evidence", ["PolicyDecision", "DecisionTrace", "EvidenceAssemblyPolicy"], "DecisionEvidenceRecord"), O("decision_evidence", "protect_sensitive_fields", ["DecisionEvidenceRecord", "SensitiveFieldPolicy"], "ProtectedDecisionRecord"), O("decision_evidence", "plan_evidence_append", ["ProtectedDecisionRecord", "EvidenceStoreRef", "RetentionBinding"], "DecisionEvidenceAppendIntent"), O("decision_evidence", "verify_decision_evidence", ["DecisionEvidenceRecord", "EvidenceDependencySet", "VerificationPolicy"], "VerificationResult")],
     "laws": ["Decision occurrence, decision evidence record, append receipt, enforcement receipt and obligation receipt are distinct.", "A decision evidence record proves only the represented evaluation under exact digests; it does not prove enforcement or correctness of external attributes.", "Sensitive inputs, reasons and policies are protected through explicit masking and disclosure policies while integrity remains verifiable.", "Decision evidence binds policy, request, attribute, evaluator, function and trace identities and editions.", "Retention, legal hold, disclosure and erasure authority are imported bindings, not invented by the evidence library.", "Absence of a decision log is not proof that no decision occurred unless the exact population and completeness guarantees are supplied."],
     "errors": ["DecisionOccurrenceUnbound", "DigestIncomplete", "SensitiveFieldLeak", "MaskOverbroad", "RetentionUnbound", "AppendCompletionUnknown", "EvidenceDependencyMissing", "VerificationFailed"], "deps": ["library.data_use_policy.decision_evaluation", "library.data_use_policy.obligation_protocol"],
     "evidence": ["source.data-use-policy.opa.decision-logs", "source.data-use-policy.oasis.xacml3", "source.data-use-policy.iso.27560", "source.data-use-policy.openid.authzen1"]},
]


def materialize(s: dict) -> dict:
    seam = s["seam"]
    return {"library_id": s["id"], "name": s["name"], "library_kind": s["kind"],
            "semantic_owner_context": f"context.data_use_policy.{CONTEXT_BY_SEAM[seam]}", "status": "specified",
            "candidate_responsibility": s["name"].lower(),
            "effect_boundary": "pure_effect_intents" if s["kind"] == "effect_port" else "pure_no_io",
            "public_types": s["types"], "public_traits": [s["name"].replace(" ", "") + "Algebra"],
            "operation_refs": [o["operation_ref"] for o in s["ops"]], "operations": s["ops"],
            "decision_refs": [f"decision.data_use_policy.{seam}.{d}" for d in DECISIONS[seam]],
            "configuration_contracts": [s["name"].replace(" ", "") + "Policy"], "laws": s["laws"],
            "invariants": ["all policy, request, attribute, evaluator and evidence cuts are exact and edition bound",
                           "unknown, missing, inapplicable, indeterminate, denied, revoked, expired, refused and completion-unknown remain distinct",
                           "no model or agent may issue policy, establish authority, decide, enforce, waive a refusal, fulfill an obligation or accept an effect"],
            "error_contracts": s["errors"] + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
            "dependencies": s["deps"], "evidence_refs": s["evidence"],
            "oracles": ["canonical positive fixtures", "negative twins", "property and metamorphic laws", "state-machine model tests", "policy-language differential corpus", "revocation and causal-cut corpus", "two independent differential implementations"],
            "gaps": ["No implementation is qualified; two independent implementations and executed conformance remain required."],
            "must_not_own": ["principal identity or authentication", "resource, data-category, purpose, consent or legal-basis truth", "business approval or entitlement issuance", "enforcement execution or business effect", "legal compliance adjudication", "provider qualification"],
            "qualification_required": False}


LIBRARIES = [materialize(s) for s in SPECS]


NEGATIVES = [
    ("policy_product", "A policy document, active bundle and policy product are the same identity.", "Keep semantic edition, repository occurrence, deployment cut and product distinct."),
    ("signature_authority", "A signed policy is authorized and applicable.", "Verify scoped issuer and delegation authority independently."),
    ("syntax_approval", "A syntactically valid policy is approved, correct or lawful.", "Keep validation, approval, activation, intent and legal validity separate."),
    ("purpose_text", "A free-text purpose has stable policy semantics.", "Consume an editioned purpose reference from its semantic owner."),
    ("classification_grant", "A data classification or relationship tuple grants access.", "Treat it as attributed input evidence evaluated by an exact policy."),
    ("consent_lawful", "A consent record proves current consent or lawful processing.", "Evaluate exact lifecycle evidence and imported jurisdictional rules without claiming legal adjudication."),
    ("missing_deny", "Missing, not-applicable, indeterminate and deny are interchangeable.", "Preserve the four-valued decision and typed missing/error causes until explicit lowering."),
    ("retrieval_precedence", "Policy retrieval or file order establishes precedence.", "Require an exact combining algorithm and ordered semantics where applicable."),
    ("permit_effect", "Permit proves access, disclosure or mutation occurred.", "Require a separately authorized effect intent and external execution receipt."),
    ("permit_approval", "Permit is business approval or entitlement issuance.", "Return a scoped policy decision only; owning domains authorize commands and issue entitlements."),
    ("obligation_returned", "A returned obligation is fulfilled.", "Track assignment, dispatch, execution receipt and verified outcome separately."),
    ("advice_obligation", "Advice and obligation have the same failure semantics.", "Honor the selected language profile and keep ignorable advice distinct."),
    ("prior_permit", "A prior permit authorizes an unbounded future use.", "Bind validity and causal cuts and require explicit ongoing reevaluation triggers."),
    ("cache_forever", "A cached decision survives policy, attribute, relationship or revocation changes.", "Use an exact cache key and declared invalidation/consistency policy."),
    ("decision_log_effect", "A decision log proves enforcement or obligation fulfillment.", "Treat it only as evidence of a represented evaluation occurrence."),
    ("empty_log_absence", "No log entry proves no decision occurred.", "Require exact occurrence population and completeness evidence."),
    ("engine_semantics", "Provider or engine identity may silently change decision semantics.", "Bind language, evaluator, function and combining-algorithm editions explicitly."),
    ("agent_authority", "A model or agent may author, approve, interpret, decide, waive, enforce or fulfill policy.", "Permit attributed proposals only; deterministic laws and named authorities retain every consequential role."),
]


NEGATIVE_ROWS = [{"negative_id": f"negative.data-use-policy.{s}", "unsafe_inference": u, "required_behavior": b, "status": "active"} for s, u, b in NEGATIVES]


COMPILER_ROWS = []
for lib in LIBRARIES:
    stem = lib["library_id"].removeprefix("library.")
    COMPILER_ROWS += [
        {"record_kind": "capability_requirement", "requirement_id": f"requirement.{stem}.implementation", "subject_ref": lib["library_id"], "required_operations": lib["operation_refs"], "required_decisions": lib["decision_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": f"offer.{stem}.reference", "subject_ref": lib["library_id"], "claimed_operations": lib["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": f"requirement.{stem}.implementation", "offer_ref": f"offer.{stem}.reference", "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable implementation.", "selectable": False, "status": "declared"},
    ]


FILES = {"sources.jsonl": SOURCES, "bounded-contexts.jsonl": CONTEXTS, "decision-points.jsonl": DECISION_ROWS,
         "library-contracts.jsonl": LIBRARIES, "compiler-contracts.jsonl": COMPILER_ROWS, "negative-twins.jsonl": NEGATIVE_ROWS}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id": "data_use_policy_governance_v0_1_0", "as_of": AS_OF, "edition": EDITION,
                "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False,
                "qualified_implementation_count": 0}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS data use policy: {len(SOURCES)} sources, {len(CONTEXTS)} contexts, {len(DECISION_ROWS)} decisions, {len(LIBRARIES)} exact libraries, {len(COMPILER_ROWS)} compiler contracts")


if __name__ == "__main__":
    main()
