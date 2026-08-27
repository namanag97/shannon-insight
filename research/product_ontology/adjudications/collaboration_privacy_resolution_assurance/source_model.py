#!/usr/bin/env python3
"""Canonical boundaries for collaboration, privacy, resolution and assurance.

The core is deterministic.  Predictive models and generative/agent assistance are
typed, optional method/provider extensions and never acquire semantic or effect
authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from product_ddd_enrichment import enrich_product_ddd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.json"
AXES = ["user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"]


def ev(ident: str, title: str, publisher: str, uri: str, claim: str, limit: str, cls: str = "official_specification_or_documentation") -> dict[str, Any]:
    return {
        "source_id": f"evidence.cpra.{ident}",
        "source_class": cls,
        "title": title,
        "publisher": publisher,
        "uri": uri,
        "retrieved_at": "2026-08-26",
        "claim": claim,
        "scope_limit": limit,
    }


def refs(*idents: str) -> list[str]:
    return [f"evidence.cpra.{ident}" for ident in idents]


def art(ident: str, kind: str, name: str, definition: str, evidence: list[str], owner: str | None = None, adoption: bool = False, operated: bool = False, **extra: Any) -> dict[str, Any]:
    return {
        "artifact_id": ident,
        "kind": kind,
        "name": name,
        "status": "candidate",
        "semantic_owner_ref": owner,
        "adoption_unit": adoption,
        "operated": operated,
        "definition": definition,
        "evidence_refs": evidence,
        **extra,
    }


def split(scores: list[int], evidence: list[str], label: str) -> dict[str, Any]:
    return {
        axis: {
            "score": score,
            "finding": f"{label}: scoped evidence for the {axis} boundary; no score qualifies a provider or makes a legal conclusion.",
            "evidence_refs": evidence,
        }
        for axis, score in zip(AXES, scores, strict=True)
    }


def camel(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").replace(".", "_").split("_"))


# id, title, publisher, URI, bounded claim, explicit limit, optional class
SOURCES = [
    ("nist_pf", "NIST Privacy Framework 1.0", "NIST", "https://www.nist.gov/privacy-framework/privacy-framework", "Defines a voluntary privacy-risk management core, profiles and implementation tiers.", "It neither decides applicable law nor authorizes a concrete data action."),
    ("nist_ir8062", "NISTIR 8062 Privacy Engineering and Risk Management", "NIST", "https://csrc.nist.gov/pubs/ir/8062/final", "Separates privacy engineering objectives, problematic data actions and risk analysis.", "Risk analysis is not a purpose authorization or system-specific conformance proof."),
    ("nist_188", "NIST SP 800-188 De-Identifying Government Datasets", "NIST", "https://csrc.nist.gov/pubs/sp/800/188/final", "Defines governance, release models, disclosure review and de-identification evaluation concerns.", "A technique or masked field does not by itself establish anonymity."),
    ("nist_226", "NIST SP 800-226 Evaluating Differential Privacy Guarantees", "NIST", "https://csrc.nist.gov/pubs/sp/800/226/final", "Defines evaluation factors and implementation hazards for differential privacy.", "A mathematical label does not prove correct implementation, composition or fitness."),
    ("nist_53", "NIST SP 800-53 Rev. 5", "NIST", "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final", "Defines security and privacy control families and control statements.", "A control catalog is not an assessment result or authorization decision."),
    ("nist_53a", "NIST SP 800-53A Rev. 5", "NIST", "https://csrc.nist.gov/pubs/sp/800/53/a/r5/final", "Defines customizable plans, procedures and analysis of security/privacy control assessments.", "A procedure or test result is not automatically an independent bounded verdict."),
    ("oscal_assessment", "OSCAL Assessment Layer", "NIST", "https://pages.nist.gov/OSCAL/learn/concepts/layer/assessment/", "Separates assessment plans, results, findings, risks and remediation records.", "OSCAL serializes assessment information; it does not establish evidence truth or assessor independence."),
    ("w3c_odrl", "ODRL Information Model 2.2", "W3C", "https://www.w3.org/TR/odrl-model/", "Defines permissions, prohibitions, duties, parties, actions, assets and constraints.", "A policy expression is not proof of interpretation, enforcement or completed effect."),
    ("w3c_dpv2", "Data Privacy Vocabulary 2.0", "W3C Data Privacy Vocabularies and Controls Community Group", "https://www.w3.org/community/reports/dpvcg/CG-FINAL-dpv-20240801/", "Defines machine-readable privacy, purpose, processing, entity, right, risk and technology vocabulary.", "This is a Community Group Report and does not decide jurisdictional applicability."),
    ("w3c_prov", "PROV Data Model", "W3C", "https://www.w3.org/TR/prov-dm/", "Defines entities, activities, agents and qualified provenance relations.", "Provenance identity and integrity do not establish truth, causation or authority."),
    ("w3c_earl", "Evaluation and Report Language 1.0 Schema", "W3C", "https://www.w3.org/TR/EARL10-Schema/", "Separates assertor, test subject, criterion, mode and result in machine-readable test assertions.", "EARL is a Working Group Note and not a complete assurance-case or test-procedure vocabulary."),
    ("w3c_shacl", "Shapes Constraint Language", "W3C", "https://www.w3.org/TR/shacl/", "Defines graph validation constraints and validation results.", "Shape conformance is not semantic truth, business fitness or an assurance verdict."),
    ("ietf_rats", "RFC 9334 RATS Architecture", "IETF", "https://www.rfc-editor.org/rfc/rfc9334.html", "Separates attester evidence, verifier appraisal, attestation result and relying-party appraisal policy.", "Remote attestation is not general business assurance or authorization by itself."),
    ("ietf_rfc3339", "RFC 3339 Date and Time on the Internet", "IETF", "https://www.rfc-editor.org/rfc/rfc3339.html", "Defines a timestamp representation profile.", "Timestamp syntax does not choose validity, recording, deadline or disposition semantics."),
    ("aws_overview", "What is AWS Clean Rooms?", "Amazon Web Services", "https://docs.aws.amazon.com/clean-rooms/latest/userguide/what-is.html", "Documents collaboration, linked data, analysis rules, logs and privacy-enhancing mechanisms.", "Provider behavior is one implementation profile and is unqualified here."),
    ("aws_rules", "Analysis rules in AWS Clean Rooms", "Amazon Web Services", "https://docs.aws.amazon.com/clean-rooms/latest/userguide/analysis-rules.html", "Documents aggregation, list and custom analysis rules and restrictive composition across participants.", "Supported SQL/rule forms are provider-specific and not a universal collaboration language."),
    ("aws_custom", "Custom analysis rule in AWS Clean Rooms", "Amazon Web Services", "https://docs.aws.amazon.com/clean-rooms/latest/userguide/analysis-rules-custom.html", "Documents reviewed templates, query-provider permissions and output constraints.", "Template approval does not prove release safety or business authority outside its scope."),
    ("snowflake_policies", "Understanding clean room table policies", "Snowflake", "https://docs.snowflake.com/en/user-guide/cleanrooms/policies", "Documents join, column, activation and aggregation policies for clean-room data.", "Snowflake policy procedures are a provider interface, not canonical semantics."),
    ("snowflake_consumer", "Snowflake Data Clean Rooms consumer reference", "Snowflake", "https://docs.snowflake.com/en/user-guide/cleanrooms/consumer", "Documents template approval, provider-run permissions, resource constraints and consumer datasets.", "A granted template permission remains scoped and does not imply unrestricted data use."),
    ("google_space", "Confidential Space overview", "Google Cloud", "https://docs.cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-overview", "Separates data collaborators, workload author, workload operator, attestation service and protected resources.", "A TEE and attestation are mechanisms; they do not define collaboration purpose or output policy."),
    ("google_resources", "Create and grant access to Confidential Space resources", "Google Cloud", "https://docs.cloud.google.com/confidential-computing/confidential-space/docs/create-grant-access-confidential-resources", "Documents workload authorization, encrypted inputs and result-destination choices.", "Cloud IAM binding does not establish cross-party analytical meaning or lawful purpose."),
    ("pysyft_requests", "PySyft Requests API", "OpenMined", "https://docs.openmined.org/en/latest/components/requests-api.html", "Documents data-owner review and approve/deny lifecycle for requested changes.", "Project workflow is one implementation and approval remains owner-scoped."),
    ("opendp", "OpenDP Documentation", "OpenDP", "https://docs.opendp.org/en/stable/", "Implements typed transformations, measurements, privacy maps and composition primitives.", "Library construction does not prove dataset fitness, policy authority or deployment conformance."),
    ("nara_schedule", "Scheduling Records", "US National Archives and Records Administration", "https://www.archives.gov/records-mgmt/scheduling/sch-records", "Separates record description, retention, destruction and transfer-to-archive instructions.", "US federal records authority is evidence for generic lifecycle distinctions, not global legal advice."),
    ("nara_grs", "General Records Schedules", "US National Archives and Records Administration", "https://www.archives.gov/records-mgmt/grs", "Documents versioned disposition authorities and current/superseded schedule concerns.", "A schedule must be bound to competent authority and scope before execution."),
    ("iso15489", "ISO 15489-1:2016 Records Management", "ISO", "https://www.iso.org/standard/62542.html", "Defines records, metadata, responsibilities, controls and lifecycle management principles.", "The catalog abstract does not replace licensed clauses or local authority."),
    ("iso27701", "ISO/IEC 27701:2025 Privacy Information Management Systems", "ISO", "https://www.iso.org/standard/27701", "Defines requirements and guidance for a privacy information management system.", "Management-system conformance is not a decision on a particular data request or effect."),
    ("iso27560", "ISO/IEC TS 27560:2023 Consent Record Information Structure", "ISO", "https://www.iso.org/standard/80392.html", "Defines interoperable consent records, receipts and lifecycle information.", "A recorded consent does not silently authorize every purpose, party, operation or time."),
    ("eu_gdpr", "Regulation (EU) 2016/679", "European Union", "https://eur-lex.europa.eu/eli/reg/2016/679/oj", "Primary text distinguishes processing roles, data-subject rights and obligations.", "The corpus does not interpret applicability, exceptions or legal conclusions."),
    ("transcend_overview", "Transcend DSR Automation Overview", "Transcend", "https://docs.transcend.io/docs/articles/dsr-automation/overview", "Documents intake, identity enrichment, preflight, system jobs, access/deletion effects and reports.", "Vendor workflows do not define universal privacy authority or connector conformance."),
    ("transcend_api", "Transcend Data Subject Request API", "Transcend", "https://docs.transcend.io/docs/api-reference/POST/v1/data-subject-request", "Documents typed request actions, subject types, workflow controls and completion states.", "API acceptance is not proof that a request is valid or every downstream effect completed."),
    ("onetrust_scopes", "OneTrust OAuth Scopes", "OneTrust", "https://developer.onetrust.com/onetrust/reference/oauth-20-scopes", "Documents separate read/write scopes for privacy-rights requests, assessments, policies and incidents.", "Permission scopes do not prove semantic correctness or operational completion."),
    ("fellegi_sunter", "A Theory for Record Linkage", "Journal of the American Statistical Association", "https://doi.org/10.1080/01621459.1969.10501049", "Introduces probabilistic link/non-link/clerical-review decision regions.", "Model assumptions and thresholds require population-specific validation.", "primary_research"),
    ("splink_theory", "The Fellegi-Sunter Model", "Splink", "https://moj-analytical-services.github.io/splink/topic_guides/theory/fellegi_sunter.html", "Documents match priors and m/u comparison probabilities used in Splink.", "An estimated probability is not a steward decision or merge authority."),
    ("splink_blocking", "Splink Blocking Rules", "Splink", "https://moj-analytical-services.github.io/splink/topic_guides/blocking/blocking_rules.html", "Documents candidate-pair reduction and recall/performance trade-offs.", "Blocking can omit true matches and must be evaluated for the target population."),
    ("splink_training", "Splink Training Rationale", "Splink", "https://moj-analytical-services.github.io/splink/topic_guides/training/training_rationale.html", "Documents parameter-estimation choices and convergence/data-quality concerns.", "Recommended training is implementation guidance, not universal optimality."),
    ("splink_evaluation", "Splink Evaluation Overview", "Splink", "https://moj-analytical-services.github.io/splink/topic_guides/evaluation/overview.html", "Separates model, edge and cluster evaluation across iterative versions.", "Evaluation aids do not establish business identity or mutation authority."),
    ("zingg_fields", "Zingg Field Definitions", "Zingg", "https://github.com/zinggAI/zingg/blob/main/docs/stepbystep/configuration/field-definitions.md", "Documents typed comparison features and field match modes.", "Provider feature labels and learned behavior require independent tests."),
    ("zingg_explain", "Zingg Explanation of Matches", "Zingg", "https://docs.zingg.ai/latest/explainoutput", "Documents pair-level cluster explanations and review uses.", "An explanation is evidence about a model result, not proof of real-world identity."),
    ("senzing_spec", "Senzing Entity Specification", "Senzing", "https://www.senzing.com/docs/entity_specification/", "Defines source records, features, attributes and source-system pointer identity.", "Mapping to a provider schema does not confer source or golden-record authority."),
    ("iso8000_115", "ISO 8000-115:2024", "ISO", "https://www.iso.org/standard/88847.html", "Defines syntax, semantics, ownership and resolution requirements for quality identifiers.", "It excludes identifier creation and resolution methods."),
    ("iso8000_116", "ISO 8000-116:2019", "ISO", "https://www.iso.org/standard/75117.html", "Specializes quality identifiers for authoritative legal-entity identifiers.", "An authoritative identifier is not probabilistic entity resolution or universal person identity."),
    ("dedupe_docs", "Dedupe Documentation", "Dedupe.io", "https://docs.dedupe.io/en/latest/", "Documents active-learning entity matching, clustering and gazetteer interfaces.", "Provider algorithms and defaults are unqualified here."),
    ("iso17029", "ISO/IEC 17029:2019", "ISO", "https://www.iso.org/standard/29352.html", "Defines competence, consistent operation and impartiality for validation/verification bodies.", "The catalog abstract does not prove a particular body's competence or independence."),
    ("iso19011", "ISO 19011:2018", "ISO", "https://www.iso.org/standard/70017.html", "Provides guidance for auditing management systems and audit programmes.", "Audit guidance is not an attestation, certification or product-acceptance decision."),
    ("iso27706", "ISO/IEC 27706:2025", "ISO", "https://www.iso.org/standard/27706", "Defines requirements for bodies auditing and certifying privacy information management systems.", "It applies to certification bodies and does not make platform automation independent."),
    ("slsa", "SLSA Provenance v1.1", "OpenSSF", "https://slsa.dev/spec/v1.1/provenance", "Defines authenticated build provenance predicates and subjects.", "Provenance integrity does not prove source quality, policy compliance or product fitness."),
    ("in_toto", "in-toto Attestation Framework", "in-toto", "https://github.com/in-toto/attestation/tree/main/spec", "Defines statement envelopes, subjects, predicates and predicate types.", "An attestation statement does not establish issuer authority or claim truth."),
    ("common_criteria", "Common Criteria Portal", "Common Criteria Recognition Arrangement", "https://www.commoncriteria.org/", "Publishes evaluation criteria, protection profiles, schemes and certified-product records.", "Recognition scope and assurance claims remain scheme-, version- and target-specific."),
]


PRODUCTS: dict[str, dict[str, Any]] = {
    "collaboration": {
        "id": "product.controlled_data_collaboration",
        "name": "Controlled Data Collaboration",
        "question": "How can mutually bounded parties run approved analyses over governed contributions and release only authorized outputs?",
        "sources": refs("aws_overview", "aws_rules", "snowflake_consumer", "google_space", "pysyft_requests", "nist_188", "nist_226"),
        "scores": [2, 2, 2, 2, 2, 2, 2, 1, 2, 2],
        "states": ["draft", "negotiating", "participants_admitted", "contributions_admitted", "enabled", "executing", "output_review", "released", "suspended", "closed"],
        "commands": ["declare_collaboration", "admit_participant", "admit_contribution", "approve_analysis", "execute_analysis", "review_output", "release_output", "suspend_collaboration", "close_collaboration"],
        "events": ["collaboration_declared", "participant_admitted", "contribution_admitted", "analysis_approved", "analysis_executed", "output_reviewed", "output_released", "collaboration_suspended", "collaboration_closed"],
        "invariants": ["every input retains participant authority", "every execution binds an approved analysis edition", "the most restrictive applicable output obligations are preserved", "release is a distinct authorized effect"],
        "refusals": ["participant_authority_unresolved", "contribution_contract_incompatible", "analysis_not_jointly_approved", "runtime_not_attested_when_required", "privacy_budget_unavailable", "output_release_refused"],
    },
    "privacy": {
        "id": "product.privacy_rights_retention",
        "name": "Privacy Rights and Retention Control",
        "question": "How can an organization receive, adjudicate, execute and evidence scoped rights and records-disposition cases across heterogeneous systems?",
        "sources": refs("nist_pf", "w3c_dpv2", "iso15489", "iso27701", "iso27560", "nara_schedule", "transcend_overview", "onetrust_scopes"),
        "scores": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        "states": ["received", "identity_pending", "scoped", "authority_review", "planned", "executing", "evidence_review", "fulfilled", "refused", "appealed", "recalled", "closed"],
        "commands": ["receive_case", "verify_requestor", "resolve_subject_scope", "bind_authority", "plan_effects", "place_hold", "execute_effect", "review_evidence", "fulfil_case", "refuse_case", "appeal_case", "recall_disposition"],
        "events": ["case_received", "requestor_verified", "subject_scope_resolved", "authority_bound", "effect_planned", "hold_placed", "effect_executed", "evidence_reviewed", "case_fulfilled", "case_refused", "appeal_received", "disposition_recalled"],
        "invariants": ["approval is not an effect", "request identity is not data-subject scope", "hold precedence is explicit", "every claimed disposition has target-specific evidence"],
        "refusals": ["requestor_unverified", "subject_scope_ambiguous", "authority_unbound", "active_hold_conflict", "effect_provider_unqualified", "evidence_incomplete", "deadline_semantics_unknown"],
    },
    "resolution": {
        "id": "product.entity_resolution",
        "name": "Entity Resolution and Identity Mapping",
        "question": "Which source records may refer to the same scoped real-world entity, with what evidence, uncertainty, review and reversibility?",
        "sources": refs("fellegi_sunter", "splink_blocking", "splink_training", "splink_evaluation", "zingg_explain", "senzing_spec", "iso8000_115"),
        "scores": [2, 2, 2, 2, 1, 2, 2, 1, 2, 2],
        "states": ["configured", "profiled", "candidates_generated", "scored", "review_pending", "links_decided", "clustered", "merge_proposed", "accepted", "rejected", "reversed", "retired"],
        "commands": ["bind_source_identity", "normalize_features", "generate_candidates", "score_pair", "request_clerical_review", "decide_link", "form_cluster", "propose_merge", "accept_merge", "reject_merge", "reverse_decision", "evaluate_population"],
        "events": ["source_identity_bound", "features_normalized", "candidates_generated", "pair_scored", "clerical_review_requested", "link_decided", "cluster_formed", "merge_proposed", "merge_accepted", "merge_rejected", "decision_reversed", "population_evaluated"],
        "invariants": ["score is not a link decision", "link decision is not source mutation", "cluster membership is versioned and explainable", "golden-record authority remains external"],
        "refusals": ["source_namespace_ambiguous", "feature_semantics_incompatible", "candidate_recall_unmeasured", "model_unqualified_for_population", "threshold_authority_missing", "review_conflict", "merge_authority_missing"],
    },
    "assurance": {
        "id": "product.assurance_case_appraisal",
        "name": "Assurance Case and Appraisal",
        "question": "How can a relying party obtain a scoped, evidence-linked and challengeable appraisal of a precise claim without confusing tests, attestations or approvals with truth?",
        "sources": refs("nist_53a", "oscal_assessment", "iso17029", "iso19011", "ietf_rats", "w3c_earl", "slsa", "in_toto"),
        "scores": [2, 2, 2, 2, 2, 2, 2, 1, 2, 1],
        "states": ["proposed", "scoped", "planned", "evidence_collecting", "appraising", "draft_findings", "challenge_open", "final", "superseded", "withdrawn"],
        "commands": ["open_assurance_case", "bind_criteria", "appoint_appraiser", "declare_conflicts", "plan_appraisal", "admit_evidence", "perform_appraisal", "record_finding", "raise_defeater", "answer_challenge", "issue_bounded_verdict", "supersede_verdict", "withdraw_verdict"],
        "events": ["assurance_case_opened", "criteria_bound", "appraiser_appointed", "conflicts_declared", "appraisal_planned", "evidence_admitted", "appraisal_performed", "finding_recorded", "defeater_raised", "challenge_answered", "bounded_verdict_issued", "verdict_superseded", "verdict_withdrawn"],
        "invariants": ["claim identity includes scope and criteria edition", "evidence is not truth", "independence is occurrence evidence not a product label", "verdict preserves limitations, defeaters and residual gaps"],
        "refusals": ["claim_ambiguous", "criteria_unbound", "appraiser_competence_unproved", "independence_conflict_unresolved", "evidence_custody_broken", "material_defeater_unresolved", "scope_exceeded"],
    },
}


# product key, suffix, semantic name, operation, decision, invariant, refusal,
# existing compiler library, evidence suffixes, effectful
LIBRARY_SPECS = [
    ("collaboration", "contract", "Collaboration contract", "compile_collaboration", "participant_purpose_and_term_profile", "participants_purposes_inputs_analyses_outputs_and_exit_are_editioned", "collaboration_contract_incomplete", "library.spt.privacy_vocabulary", ["w3c_dpv2", "w3c_odrl"], False),
    ("collaboration", "participant_authority", "Participant authority", "qualify_participant", "principal_role_and_delegation", "participant_identity_role_authority_and_delegation_are_distinct", "participant_authority_unresolved", "library.spt.principal_types", ["google_space", "w3c_odrl"], False),
    ("collaboration", "contribution_contract", "Contribution contract", "admit_contribution", "schema_identity_time_and_use_binding", "a_contribution_retains_source_owner_and_use_constraints", "contribution_contract_incompatible", ["library.data_contract.contract_identity", "library.data_contract.data_schema_binding", "library.data_use_policy.policy_edition"], ["aws_overview", "snowflake_policies"], False),
    ("collaboration", "analysis_policy", "Approved analysis policy", "compile_analysis_policy", "analysis_template_and_parameter_bounds", "analysis_approval_binds_exact_code_query_parameters_and_participants", "analysis_not_jointly_approved", "library.spt.use_policy_compiler", ["aws_rules", "aws_custom", "snowflake_consumer"], False),
    ("collaboration", "policy_evaluator", "Collaboration policy evaluator", "evaluate_collaboration_action", "restrictive_policy_composition", "applicable_participant_constraints_compose_without_silent_weakening", "collaboration_policy_indeterminate", "library.spt.policy_evaluator", ["aws_rules", "w3c_odrl"], False),
    ("collaboration", "input_admission", "Input admission gate", "enforce_input_admission", "cut_integrity_and_obligations", "only_admitted_source_cuts_enter_an_execution", "input_admission_refused", "library.spt.policy_enforcer", ["aws_overview", "google_resources"], True),
    ("collaboration", "deidentification_risk", "Disclosure-risk appraisal", "appraise_release_risk", "attacker_auxiliary_data_and_metric_profile", "masking_pseudonymization_deidentification_and_anonymity_claims_are_distinct", "release_risk_unbounded", "library.spt.deidentification_metrics", ["nist_188"], False),
    ("collaboration", "privacy_budget", "Privacy budget ledger", "reserve_and_spend_privacy_budget", "privacy_unit_adjacency_mechanism_and_accountant", "privacy_spend_is_atomic_and_composition_is_explicit", "privacy_budget_unavailable", "library.spt.privacy_accountant", ["nist_226", "opendp"], True),
    ("collaboration", "secure_compute_gateway", "Secure-computation gateway", "execute_secure_workload", "protocol_tee_and_corruption_assumptions", "secure_computation_mechanism_never_authorizes_an_unapproved_analysis", "secure_runtime_unqualified", "library.spt.secure_computation_protocol", ["google_space", "ietf_rats"], True),
    ("collaboration", "attestation_appraisal", "Workload attestation appraisal", "appraise_workload_attestation", "nonce_reference_values_and_appraisal_policy", "attestation_result_is_input_to_a_separate_relying_policy", "attestation_unacceptable", "library.spt.attestation_verifier", ["ietf_rats", "google_space"], False),
    ("collaboration", "output_release", "Output release gate", "release_collaboration_output", "recipient_projection_suppression_and_review", "execution_success_never_implies_output_release", "output_release_refused", "library.lpe.disclosure-core", ["aws_rules", "snowflake_policies", "nist_188"], True),
    ("collaboration", "receipt", "Collaboration execution receipt", "record_collaboration_receipt", "input_analysis_runtime_output_and_policy_identity", "every_execution_and_release_have_distinct_receipts", "collaboration_receipt_incomplete", "library.lpe.runtime-receipt-core", ["w3c_prov", "aws_overview"], True),
    ("privacy", "vocabulary", "Privacy action vocabulary", "type_privacy_case", "purpose_processing_right_and_role_profile", "legal_markers_are_imported_and_never_invented_by_the_platform", "privacy_semantics_unknown", "library.spt.privacy_vocabulary", ["w3c_dpv2", "nist_pf"], False),
    ("privacy", "rights_case", "Rights case state machine", "transition_rights_case", "request_type_deadline_and_appeal_profile", "case_transitions_are_total_and_refusals_are_recorded", "rights_case_transition_illegal", "library.spt.rights_case", ["transcend_overview", "transcend_api"], True),
    ("privacy", "subject_scope", "Requestor and subject scope", "resolve_subject_scope", "identity_delegation_and_identifier_expansion", "requestor_identity_subject_identity_and_record_scope_are_distinct", "subject_scope_ambiguous", "library.csp.identity.resolver-contract", ["transcend_overview", "w3c_dpv2"], False),
    ("privacy", "authority_policy", "Rights and records authority policy", "bind_case_authority", "jurisdiction_policy_and_exception_edition", "the_compiler_imports_competent_authority_and_does_not_practise_law", "authority_unbound", "library.gmo.policy_model", ["eu_gdpr", "nara_schedule", "iso27701"], False),
    ("privacy", "retention_calculus", "Retention calculus", "calculate_disposition_due", "trigger_duration_cutoff_and_calendar", "retention_due_date_binds_schedule_edition_trigger_and_time_basis", "retention_due_ambiguous", "library.spt.retention_calculus", ["nara_schedule", "iso15489", "ietf_rfc3339"], False),
    ("privacy", "hold_precedence", "Hold and exception precedence", "evaluate_hold_precedence", "hold_scope_priority_and_release", "no_disposition_executes_through_an_applicable_active_hold", "active_hold_conflict", "library.gmo.records_governance", ["nara_schedule", "transcend_api"], False),
    ("privacy", "effect_plan", "Cross-system disposition plan", "compile_case_effects", "target_action_order_compensation_and_evidence", "approval_plan_effect_attempt_and_verified_effect_have_distinct_identities", "effect_plan_incomplete", "library.spt.policy_enforcer", ["transcend_overview", "w3c_odrl"], False),
    ("privacy", "deletion_gateway", "Deletion and mutation gateway", "execute_privacy_effect", "provider_target_and_verification_profile", "provider_acknowledgement_is_not_verified_erasure", "effect_provider_unqualified", "library.spt.deletion_provider", ["transcend_overview", "nist_53"], True),
    ("privacy", "disclosure_package", "Access and portability disclosure", "construct_disclosure_package", "scope_redaction_format_and_recipient", "disclosure_contains_only_authorized_subject_and_projection", "disclosure_package_refused", "library.lpe.disclosure-core", ["transcend_api", "w3c_dpv2"], True),
    ("privacy", "evidence_bundle", "Privacy case evidence bundle", "qualify_case_evidence", "identity_integrity_coverage_freshness_and_custody", "evidence_quality_dimensions_never_collapse_to_one_boolean", "evidence_incomplete", "library.lpe.evidence-bundle", ["w3c_prov", "nist_53a"], False),
    ("privacy", "disposition_receipt", "Disposition receipt", "record_disposition_receipt", "target_attempt_result_and_verification", "a_case_closes_only_under_an_explicit_partial_or_complete_evidence_posture", "disposition_receipt_incomplete", "library.gmo.audit_receipts", ["transcend_overview", "iso15489"], True),
    ("privacy", "recall_impact", "Disposition recall and impact", "propagate_disposition_recall", "downstream_copy_disclosure_and_backup_scope", "correction_retraction_recall_and_deletion_are_distinct", "recall_scope_unknown", "library.lpe.impact-analysis", ["w3c_prov", "nara_grs"], True),
    ("resolution", "entity_identity", "Scoped entity identity", "declare_entity_scope", "entity_kind_namespace_and_population", "entity_identity_is_scoped_and_never_inferred_from_a_bare_identifier", "entity_scope_ambiguous", "library.csp.identity.identity-claim", ["iso8000_115", "senzing_spec"], False),
    ("resolution", "namespace_resolution", "Source namespace resolution", "resolve_source_namespace", "issuer_namespace_and_source_occurrence", "same_carrier_value_in_different_namespaces_is_not_the_same_identifier", "source_namespace_ambiguous", "library.csp.identity.namespace-registry", ["iso8000_115", "iso8000_116"], False),
    ("resolution", "normalization", "Comparison normalization", "normalize_comparison_features", "locale_script_phonetic_and_missingness_profile", "normalization_is_versioned_loss_accounted_and_reversible_where_claimed", "normalization_profile_missing", "library.csp.identity.canonicalization", ["zingg_fields", "senzing_spec"], False),
    ("resolution", "candidate_generation", "Candidate generation and blocking", "generate_candidate_pairs", "blocking_rules_and_recall_budget", "blocked_out_pairs_remain_unexamined_not_nonmatches", "candidate_recall_unmeasured", "library.csp.identity.entity-resolution", ["splink_blocking", "fellegi_sunter"], False),
    ("resolution", "comparison_features", "Pair comparison features", "compare_record_pair", "feature_similarity_missingness_and_frequency", "feature_evidence_preserves_source_values_and_method_edition", "feature_semantics_incompatible", "library.qor.duplicate_entity_resolution_kernel", ["splink_theory", "zingg_fields"], False),
    ("resolution", "match_model", "Match scoring method", "score_record_pair", "rule_probabilistic_or_predictive_method_profile", "model_output_is_a_typed_score_with_assumptions_not_a_link_decision", "model_unqualified_for_population", ["library.csp.identity.entity-resolution", "library.gmo.match_policy"], ["fellegi_sunter", "splink_training", "dedupe_docs"], False),
    ("resolution", "threshold_policy", "Link decision policy", "classify_match_score", "link_nonlink_review_thresholds_and_costs", "thresholds_bind_population_error_cost_and_authority", "threshold_authority_missing", "library.csp.authority.policy-algebra", ["fellegi_sunter", "splink_evaluation"], False),
    ("resolution", "link_decision", "Link decision ledger", "record_link_decision", "decision_author_mode_and_evidence", "prediction_review_and_authoritative_link_decision_are_distinct", "link_decision_refused", "library.csp.authority.policy-decision", ["fellegi_sunter", "zingg_explain"], True),
    ("resolution", "clerical_review", "Clerical review workflow", "adjudicate_uncertain_pair", "reviewer_competence_conflict_and_precedence", "human_review_is_recorded_with_inputs_and_can_be_challenged", "review_conflict", ["library.review.adjudication.reducer", "library.review.issue.lifecycle"], ["fellegi_sunter", "zingg_explain"], True),
    ("resolution", "cluster_graph", "Entity cluster formation", "form_entity_clusters", "transitivity_partition_and_conflict_policy", "pair_links_cluster_membership_and_entity_identity_are_distinct", "cluster_inconsistent", "library.csp.identity.entity-resolution", ["splink_evaluation", "zingg_explain"], False),
    ("resolution", "merge_split_ledger", "Merge, split and reversal ledger", "propose_merge_split", "authority_effective_time_and_reversal", "resolution_may_propose_but_cannot_mutate_master_or_source_without_authority", "merge_authority_missing", "library.csp.identity.merge-split-ledger", ["w3c_prov", "senzing_spec"], True),
    ("resolution", "master_gateway", "Master-authority gateway", "submit_master_change_proposal", "field_authority_survivorship_and_effect", "entity_resolution_does_not_own_the_golden_record", "master_change_refused", ["library.master_data.domain_identity", "library.master_data.source_authority", "library.master_data.survivorship_projection", "library.master_data.stewardship_case", "library.gmo.golden_record_edition"], ["iso8000_115", "w3c_prov"], True),
    ("resolution", "link_evidence", "Resolution evidence bundle", "explain_resolution_result", "pair_feature_model_threshold_review_and_cluster_trace", "generated_explanation_does_not_replace_exact_evidence", "resolution_evidence_incomplete", "library.lpe.evidence-bundle", ["zingg_explain", "splink_evaluation"], False),
    ("resolution", "evaluation_oracle", "Population evaluation oracle", "evaluate_resolution_population", "gold_labels_sampling_metrics_and_subgroup_profile", "quality_claims_bind_dataset_cut_population_and_error_cost", "evaluation_insufficient", "library.qor.duplicate_entity_resolution_kernel", ["splink_evaluation", "dedupe_docs"], False),
    ("assurance", "claim_argument", "Claim and argument graph", "construct_assurance_argument", "claim_scope_support_and_rebuttal", "claim_argument_evidence_and_verdict_are_distinct", "claim_ambiguous", "library.lpe.claim-argument-core", ["w3c_prov", "in_toto"], False),
    ("assurance", "criteria_profile", "Criteria and conformance profile", "bind_appraisal_criteria", "criterion_edition_applicability_and_interpretation", "a_pass_has_no_meaning_without_exact_subject_criterion_method_and_time", "criteria_unbound", "library.gmo.policy_model", ["nist_53a", "w3c_earl"], False),
    ("assurance", "appraisal_plan", "Appraisal plan", "plan_appraisal", "scope_assets_methods_sampling_and_schedule", "performed_work_is_compared_to_the_approved_plan_with_deviations", "appraisal_plan_incomplete", "library.gmo.assurance_appraisal_plan", ["oscal_assessment", "nist_53a"], False),
    ("assurance", "evidence_bundle", "Assurance evidence bundle", "admit_assurance_evidence", "claim_relevance_identity_integrity_and_freshness", "evidence_admission_does_not_accept_the_supported_claim", "evidence_inadmissible", "library.lpe.evidence-bundle", ["w3c_prov", "slsa", "in_toto"], False),
    ("assurance", "custody", "Evidence custody", "preserve_evidence_custody", "holder_transfer_access_and_integrity", "integrity_and_custody_do_not_prove_truth", "evidence_custody_broken", "library.lpe.custody-core", ["w3c_prov", "nist_53a"], True),
    ("assurance", "evidence_evaluation", "Evidence evaluation", "evaluate_claim_support", "authority_strength_freshness_coverage_and_defeaters", "blocking_defeaters_cannot_be_silently_offset_by_a_score", "material_defeater_unresolved", "library.lpe.evidence-evaluation", ["nist_53a", "ietf_rats"], False),
    ("assurance", "independence_conflict", "Appraiser independence and conflict", "qualify_appraiser_role", "competence_mandate_relationship_and_conflict", "independence_is_a_property_of_an_occurrence_not_software_or_a_brand", "independence_conflict_unresolved", "library.gmo.accountability", ["iso17029", "iso19011", "iso27706"], False),
    ("assurance", "appraisal_runtime", "Appraisal occurrence", "perform_appraisal", "appraiser_method_subject_and_time", "automated_manual_and_mixed_modes_are_explicit", "appraisal_execution_failed", "library.lpe.rats-appraisal", ["ietf_rats", "w3c_earl", "oscal_assessment"], True),
    ("assurance", "findings_defeaters", "Findings and defeaters", "record_finding_or_defeater", "severity_basis_rebuttal_and_disposition", "absence_of_recorded_findings_is_not_evidence_of_conformance", "finding_basis_missing", "library.lpe.evidence-evaluation", ["oscal_assessment", "nist_53a"], True),
    ("assurance", "bounded_verdict", "Bounded assurance verdict", "issue_bounded_verdict", "scope_criteria_time_limitations_and_residuals", "verdict_never_exceeds_appraised_scope_or_evidence", "scope_exceeded", "library.lpe.rats-appraisal", ["iso17029", "ietf_rats", "common_criteria"], True),
    ("assurance", "attestation", "Authenticated attestation", "verify_attestation", "issuer_subject_predicate_and_verification_method", "authenticated_statement_is_not_independent_appraisal", "attestation_unverified", "library.lpe.attestation-core", ["slsa", "in_toto", "ietf_rats"], False),
    ("assurance", "signature", "Verdict signature envelope", "seal_verdict", "canonical_representation_key_purpose_and_time", "signature_validity_does_not_prove_signer_mandate_or_claim_truth", "verdict_signature_invalid", "library.lpe.signature-envelope", ["in_toto", "slsa"], False),
    ("assurance", "lifecycle", "Verdict lifecycle", "supersede_or_withdraw_verdict", "validity_expiry_recheck_recall_and_supersession", "historical_verdicts_are_immutable_and_status_changes_are_append_only", "verdict_lifecycle_illegal", "library.lpe.record-lifecycle", ["oscal_assessment", "common_criteria"], True),
    ("assurance", "disclosure", "Assurance disclosure", "disclose_assurance_result", "recipient_projection_confidentiality_and_reliance", "public_summary_and_restricted_evidence_bundle_are_distinct", "assurance_disclosure_refused", "library.lpe.disclosure-core", ["common_criteria", "w3c_earl"], True),
    ("assurance", "conformance_oracle", "Executable conformance oracle", "execute_conformance_oracle", "test_subject_criterion_environment_and_expected_result", "test_pass_is_evidence_not_product_acceptance_or_production_truth", "conformance_oracle_inapplicable", "library.lpe.reproduction-evaluator", ["w3c_earl", "nist_53a", "w3c_shacl"], False),
]


SEMANTIC_GAPS = [
    ("cross_provider_collaboration_policy", "No complete portable policy language covers participant authority, approved computation, leakage, privacy accounting and output release across clean-room providers."),
    ("clean_room_exit", "Portable export of collaboration history, policy editions, receipts and revocations lacks a common conformance profile."),
    ("pet_composition", "TEE, MPC, cryptographic matching, de-identification and differential-privacy guarantees lack one compositional proof framework."),
    ("output_differencing", "Cross-run differencing and auxiliary-data risk remain data- and attacker-dependent."),
    ("privacy_rights_interchange", "Rights-case state, authority, identity evidence and downstream effect receipts lack a broadly adopted interchange contract."),
    ("retention_trigger_interchange", "Event-triggered retention schedules, calendars, holds and supersession do not port losslessly across providers."),
    ("verified_erasure", "Many effect providers expose acknowledgements without independently verifiable physical/logical deletion semantics."),
    ("backup_erasure_conflict", "Recovery copies, immutable archives, holds and erasure obligations need explicit authority precedence and future-restoration gates."),
    ("subject_scope_resolution", "Resolving all records for a person across changing identifiers cannot be proven complete in open heterogeneous systems."),
    ("entity_population_shift", "Entity-resolution quality and thresholds are population-specific and can drift as sources and behavior change."),
    ("blocking_recall", "Candidate-generation recall usually lacks complete ground truth and portable cut-scoped evidence."),
    ("cluster_error_propagation", "Pairwise accuracy does not directly bound cluster-level over-merge and under-merge harm."),
    ("entity_reversal", "Reversing links, clusters and downstream master effects lacks a universal compensation protocol."),
    ("identity_ground_truth", "Real-world identity truth may be unavailable, disputed, temporal or authority-dependent."),
    ("assurance_criteria_mapping", "Criteria mappings rarely prove semantic equivalence or preserve all obligations and test intent."),
    ("assessor_independence_evidence", "Machine-readable, privacy-preserving evidence for competence, mandate, independence and conflict is immature."),
    ("evidence_completeness", "No general mechanism proves that all material contrary evidence and defeaters were discovered."),
    ("continuous_assurance", "Continuous evidence streams and snapshot verdicts lack uniform finality, expiry and recheck semantics."),
    ("bounded_reliance", "Relying parties do not share one portable contract for acceptable residual risk, limitations and reliance purpose."),
    ("agent_explanation_evidence", "Generated explanations cannot be treated as evidence without exact source bindings, deterministic checks and accountable acceptance."),
]


def source() -> dict[str, Any]:
    sources = [ev(*row) for row in SOURCES]
    kinds = [
        {"kind": "product", "definition": "Independently adopted and operated outcome promise with lifecycle, authority, support and exit."},
        {"kind": "suite", "definition": "Commercial or administrative packaging of products; owns no merged semantics."},
        {"kind": "architecture_pattern", "definition": "Recurring arrangement of products, capabilities and mechanisms."},
        {"kind": "control_component", "definition": "Stateful or policy component inside a product boundary."},
        {"kind": "semantic_contract", "definition": "Owner of a term, identity, law, decision and refusal boundary."},
        {"kind": "capability", "definition": "Typed operation offered under a semantic contract."},
        {"kind": "standard", "definition": "Editioned external specification or profile; not a product or provider qualification."},
        {"kind": "implementation", "definition": "Observed implementation or provider; unqualified until conformance evidence exists."},
        {"kind": "neighbor", "definition": "Explicit adjacent semantic or product owner imported through an ACL."},
        {"kind": "optional_extension", "definition": "Removable method or assistance surface that cannot redefine core semantics or authority."},
    ]

    artifacts: list[dict[str, Any]] = []
    for key, product in PRODUCTS.items():
        artifacts.append(art(
            product["id"], "product", product["name"], product["question"], product["sources"],
            adoption=True, operated=True, sovereign_question=product["question"],
            lifecycle_states=product["states"], commands=product["commands"], events=product["events"],
            invariants=product["invariants"], refusals=product["refusals"],
            negative_mission="Does not invent legal, source, master-data, analytical, runtime, accreditation or relying-party authority.",
        ))

    artifacts.extend([
        art("suite.unified_data_governance", "suite", "Unified data governance suite", "Packaging of catalog, glossary, ontology, policy, quality, lineage, privacy, entity-resolution and assurance products; not one consistency boundary.", refs("nist_pf", "iso27701", "w3c_dpv2")),
        art("pattern.privacy_enhancing_collaboration", "architecture_pattern", "Privacy-enhancing collaboration pattern", "Controlled collaboration composed with selected PETs and qualified runtime mechanisms.", refs("nist_188", "nist_226", "google_space")),
        art("component.secure_enclave", "control_component", "Trusted execution mechanism", "An isolation and attestation mechanism selected by intent; never collaboration purpose or release authority.", refs("google_space", "ietf_rats")),
        art("component.match_scoring_method", "control_component", "Entity match method", "Rules, Fellegi-Sunter/probabilistic inference, supervised predictive models or ensembles behind the same typed scoring contract.", refs("fellegi_sunter", "splink_theory", "dedupe_docs")),
        art("component.optional_agent_assistance", "optional_extension", "Optional model or agent assistance", "Intent-selected drafting, evidence-navigation, triage or explanation over typed records. It can propose; it cannot decide, approve, execute, attest or issue a verdict.", refs("oscal_assessment", "w3c_earl")),
        art("standard.oscal_assessment", "standard", "OSCAL assessment models", "Machine-readable assessment planning, results and remediation models.", refs("oscal_assessment")),
        art("standard.dpv2", "standard", "Data Privacy Vocabulary 2.0", "Community specification for privacy metadata.", refs("w3c_dpv2")),
        art("standard.iso17029", "standard", "ISO/IEC 17029", "Validation/verification body principles and requirements.", refs("iso17029")),
        art("implementation.aws_clean_rooms", "implementation", "AWS Clean Rooms", "Observed controlled-collaboration implementation; unqualified here.", refs("aws_overview", "aws_rules", "aws_custom")),
        art("implementation.snowflake_clean_rooms", "implementation", "Snowflake Data Clean Rooms", "Observed controlled-collaboration implementation; unqualified here.", refs("snowflake_policies", "snowflake_consumer")),
        art("implementation.google_confidential_space", "implementation", "Google Confidential Space", "Observed confidential-compute mechanism and collaboration building block; not a complete collaboration semantic owner.", refs("google_space", "google_resources")),
        art("implementation.pysyft", "implementation", "PySyft", "Observed data-owner request and controlled-computation implementation; unqualified here.", refs("pysyft_requests")),
        art("implementation.transcend", "implementation", "Transcend DSR Automation", "Observed privacy-rights workflow and effect orchestration implementation; unqualified here.", refs("transcend_overview", "transcend_api")),
        art("implementation.onetrust", "implementation", "OneTrust Privacy Rights Automation", "Observed privacy-rights API surface; unqualified here.", refs("onetrust_scopes")),
        art("implementation.splink", "implementation", "Splink", "Observed probabilistic entity-resolution implementation; unqualified here.", refs("splink_theory", "splink_blocking", "splink_training", "splink_evaluation")),
        art("implementation.zingg", "implementation", "Zingg", "Observed predictive entity-resolution implementation; unqualified here.", refs("zingg_fields", "zingg_explain")),
        art("implementation.senzing", "implementation", "Senzing", "Observed entity-resolution engine and source-mapping interface; unqualified here.", refs("senzing_spec")),
        art("neighbor.legal_records_authority", "neighbor", "Legal and records authority", "Competent human/organizational authority owns applicability, interpretation, schedules and exceptions.", refs("eu_gdpr", "nara_schedule")),
        art("neighbor.identity_authority", "neighbor", "Identity and delegation authority", "Owns principal proof, representation and revocation.", refs("w3c_dpv2", "google_space")),
        art("neighbor.source_truth", "neighbor", "Source-system authority", "Owns source facts, corrections and mutation semantics.", refs("w3c_prov")),
        art("neighbor.master_data", "neighbor", "Master and reference data", "Owns authoritative field values, golden projections and approved mutations.", refs("iso8000_115", "iso8000_116")),
        art("neighbor.data_use_policy", "neighbor", "Data-use policy", "Owns purpose, permission, prohibition and duty semantics.", refs("w3c_odrl", "w3c_dpv2")),
        art("neighbor.query_compute", "neighbor", "Query and compute runtime", "Owns physical execution, scheduling, isolation and resource guarantees.", refs("google_space", "aws_overview")),
        art("neighbor.analytical_method", "neighbor", "Analytical method", "Owns statistical, predictive, optimization, simulation and other method semantics.", refs("fellegi_sunter", "nist_226")),
        art("neighbor.backup_archive", "neighbor", "Recovery and preservation", "Owns recoverability or long-term preservation mechanics under imported retention authority.", refs("nara_schedule", "iso15489")),
        art("neighbor.relying_authority", "neighbor", "Relying decision authority", "Owns what assurance result is sufficient for a subsequent business or authorization decision.", refs("ietf_rats", "iso17029")),
    ])

    ownership: list[dict[str, Any]] = []
    libraries: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    binding_maps: list[dict[str, Any]] = []
    for product_key, suffix, name, operation, decision, invariant, refusal, concrete, evidence_ids, effectful in LIBRARY_SPECS:
        product = PRODUCTS[product_key]
        owner = f"semantic.cpra.{product_key}.{suffix}"
        capability = f"capability.cpra.{product_key}.{suffix}"
        evidence = refs(*evidence_ids)
        artifacts.append(art(owner, "semantic_contract", name, f"Owns {name.lower()} identity, decision points, laws and refusals.", evidence))
        artifacts.append(art(capability, "capability", operation.replace("_", " ").title(), f"Typed capability to {operation.replace('_', ' ')} under the {name.lower()} contract.", evidence, owner=owner))
        ownership.append({
            "meaning_id": f"meaning.cpra.{product_key}.{suffix}", "term": name, "owner_ref": owner,
            "invariant": invariant,
            "must_not_be_owned_by": ["component.optional_agent_assistance", "neighbor.query_compute", "neighbor.analytical_method"],
        })
        type_name = camel(f"{product_key}_{suffix}")
        abstract = f"library.adjudicated.cpra.{product_key}.{suffix}"
        libraries.append({
            "library_id": abstract,
            "class": "runtime_boundary" if effectful else "semantic_pure",
            "product_ref": product["id"],
            "owner_ref": owner,
            "provides": [capability],
            "types": [type_name, f"{type_name}Decision", f"{type_name}Refusal", f"{type_name}Receipt"],
            "operations": [operation],
            "decisions": [decision],
            "invariants": [
                invariant,
                "provider_identity_does_not_change_semantics",
                "generated_or_agent_output_is_non_authoritative_until_typed_validated_and_accepted",
                "removing_model_and_agent_extensions_preserves_the_deterministic_core_contract",
            ],
            "refusals": [refusal, "unsupported_capability", "unresolved_authority", "resource_exhausted"],
            "dependencies": [],
            "effect_boundary": "effect_intents_attempts_and_receipts" if effectful else "pure_no_io",
            "evidence_refs": evidence,
        })
        requirements.append({
            "requirement_id": f"requirement.cpra.{product_key}.{suffix}",
            "consumer_ref": product["id"],
            "capability_ref": capability,
            "minimum_qualified_offers": 2,
            "binding_phase": "deployment_time" if effectful else "compile_time",
            "status": "unbound",
            "refusal": "refuse compilation or execution when no exact compatible qualified offer exists",
        })
        binding_maps.append({
            "binding_map_id": f"binding.cpra.{product_key}.{suffix}",
            "product_ref": product["id"],
            "abstract_library_ref": abstract,
            "compiler_disposition": "structurally_projected_unqualified",
            "concrete_library_refs": concrete if isinstance(concrete, list) else [concrete],
            "gap_ref": None,
            "portable_offer": False,
        })

    decisions = []
    for key, product in PRODUCTS.items():
        decisions.append({
            "decision_id": f"decision.cpra.{key}.product",
            "subject_ref": product["id"],
            "disposition": "strong_product_candidate",
            "rationale": f"{product['name']} has a distinct adopted job, semantic owner, lifecycle, authority boundary, operational promise, support surface and exit boundary. The product imports rather than absorbs adjacent legal, source, runtime, analytical and relying authority.",
            "evidence_refs": product["sources"],
            "split_test": split(product["scores"], product["sources"], product["name"]),
        })
    decisions.extend([
        {"decision_id": "decision.cpra.unified_governance", "subject_ref": "suite.unified_data_governance", "disposition": "reclassify_as_suite", "rationale": "Catalog, language, policy, quality, lineage, privacy, resolution and assurance have different authorities, states, failures and exit; one administrative SKU cannot merge them semantically.", "evidence_refs": refs("nist_pf", "iso27701", "w3c_dpv2")},
        {"decision_id": "decision.cpra.clean_room_pattern", "subject_ref": "pattern.privacy_enhancing_collaboration", "disposition": "retain_as_architecture_pattern", "rationale": "Clean room is a market label for controlled collaboration plus selected computation/privacy mechanisms; the product boundary is the governed collaboration promise.", "evidence_refs": refs("aws_overview", "google_space", "nist_188")},
        {"decision_id": "decision.cpra.tee_component", "subject_ref": "component.secure_enclave", "disposition": "retain_as_replaceable_mechanism", "rationale": "TEE, MPC and cryptographic protocols can satisfy runtime requirements but do not own purpose, participant agreement, analysis approval or release authority.", "evidence_refs": refs("google_space", "ietf_rats")},
        {"decision_id": "decision.cpra.match_method", "subject_ref": "component.match_scoring_method", "disposition": "retain_as_analytical_method_component", "rationale": "Deterministic rules, classical probabilistic linkage and predictive ML are substitutable scoring methods behind typed contracts; none is a link or merge authority.", "evidence_refs": refs("fellegi_sunter", "splink_theory", "zingg_fields")},
        {"decision_id": "decision.cpra.agent_optional", "subject_ref": "component.optional_agent_assistance", "disposition": "optional_non_authoritative_extension", "rationale": "LLMs or tool-using agents may draft intent, locate evidence, triage work or explain typed results only when selected. Parsing, typing, solving, numerical execution, policy, qualification, authorization, effects and receipts remain deterministic and authoritative.", "evidence_refs": refs("oscal_assessment", "w3c_earl", "w3c_shacl")},
    ])

    offers = [
        ("aws_clean_rooms", "implementation.aws_clean_rooms", "collaboration", ["contract", "analysis_policy", "policy_evaluator", "input_admission", "output_release", "receipt"]),
        ("snowflake_clean_rooms", "implementation.snowflake_clean_rooms", "collaboration", ["contract", "analysis_policy", "policy_evaluator", "output_release"]),
        ("google_confidential_space", "implementation.google_confidential_space", "collaboration", ["participant_authority", "input_admission", "secure_compute_gateway", "attestation_appraisal"]),
        ("pysyft", "implementation.pysyft", "collaboration", ["contract", "participant_authority", "analysis_policy"]),
        ("transcend", "implementation.transcend", "privacy", ["rights_case", "subject_scope", "effect_plan", "deletion_gateway", "disclosure_package", "disposition_receipt"]),
        ("onetrust", "implementation.onetrust", "privacy", ["rights_case", "authority_policy"]),
        ("splink", "implementation.splink", "resolution", ["candidate_generation", "comparison_features", "match_model", "threshold_policy", "cluster_graph", "evaluation_oracle"]),
        ("zingg", "implementation.zingg", "resolution", ["normalization", "comparison_features", "match_model", "clerical_review", "cluster_graph", "link_evidence"]),
        ("senzing", "implementation.senzing", "resolution", ["entity_identity", "namespace_resolution", "normalization", "cluster_graph", "master_gateway"]),
    ]
    offer_rows = [{
        "offer_id": f"offer.cpra.{name}",
        "provider_ref": provider,
        "capability_refs": [f"capability.cpra.{product_key}.{suffix}" for suffix in suffixes],
        "status": "observed_unqualified",
        "qualified_implementation_count": 0,
        "portable": False,
        "evidence_refs": artifacts[[a["artifact_id"] for a in artifacts].index(provider)]["evidence_refs"],
    } for name, provider, product_key, suffixes in offers]

    relations = [
        {"relation_id": "relation.cpra.suite_packages_collaboration", "from_ref": "suite.unified_data_governance", "predicate": "packages", "to_ref": PRODUCTS["collaboration"]["id"], "binding_phase": "authoring"},
        {"relation_id": "relation.cpra.suite_packages_privacy", "from_ref": "suite.unified_data_governance", "predicate": "packages", "to_ref": PRODUCTS["privacy"]["id"], "binding_phase": "authoring"},
        {"relation_id": "relation.cpra.suite_packages_resolution", "from_ref": "suite.unified_data_governance", "predicate": "packages", "to_ref": PRODUCTS["resolution"]["id"], "binding_phase": "authoring"},
        {"relation_id": "relation.cpra.suite_packages_assurance", "from_ref": "suite.unified_data_governance", "predicate": "packages", "to_ref": PRODUCTS["assurance"]["id"], "binding_phase": "authoring"},
        {"relation_id": "relation.cpra.clean_pattern_realizes_collaboration", "from_ref": "pattern.privacy_enhancing_collaboration", "predicate": "realizes", "to_ref": PRODUCTS["collaboration"]["id"], "binding_phase": "authoring"},
        {"relation_id": "relation.cpra.clean_pattern_requires_compute", "from_ref": "pattern.privacy_enhancing_collaboration", "predicate": "requires", "to_ref": "neighbor.query_compute", "binding_phase": "deployment_time"},
        {"relation_id": "relation.cpra.collaboration_governed_policy", "from_ref": PRODUCTS["collaboration"]["id"], "predicate": "governed_by", "to_ref": "neighbor.data_use_policy", "binding_phase": "runtime"},
        {"relation_id": "relation.cpra.privacy_imports_authority", "from_ref": PRODUCTS["privacy"]["id"], "predicate": "governed_by", "to_ref": "neighbor.legal_records_authority", "binding_phase": "authoring"},
        {"relation_id": "relation.cpra.privacy_requires_identity", "from_ref": PRODUCTS["privacy"]["id"], "predicate": "requires", "to_ref": "neighbor.identity_authority", "binding_phase": "runtime"},
        {"relation_id": "relation.cpra.privacy_requires_sources", "from_ref": PRODUCTS["privacy"]["id"], "predicate": "requires", "to_ref": "neighbor.source_truth", "binding_phase": "runtime"},
        {"relation_id": "relation.cpra.privacy_coordinates_archive", "from_ref": PRODUCTS["privacy"]["id"], "predicate": "requires", "to_ref": "neighbor.backup_archive", "binding_phase": "runtime"},
        {"relation_id": "relation.cpra.resolution_imports_sources", "from_ref": PRODUCTS["resolution"]["id"], "predicate": "requires", "to_ref": "neighbor.source_truth", "binding_phase": "runtime"},
        {"relation_id": "relation.cpra.resolution_proposes_master", "from_ref": PRODUCTS["resolution"]["id"], "predicate": "requires", "to_ref": "neighbor.master_data", "binding_phase": "runtime"},
        {"relation_id": "relation.cpra.resolution_uses_method", "from_ref": PRODUCTS["resolution"]["id"], "predicate": "requires", "to_ref": "neighbor.analytical_method", "binding_phase": "compile_time"},
        {"relation_id": "relation.cpra.assurance_imports_reliance", "from_ref": PRODUCTS["assurance"]["id"], "predicate": "governed_by", "to_ref": "neighbor.relying_authority", "binding_phase": "runtime"},
        {"relation_id": "relation.cpra.agent_assists_collaboration", "from_ref": "component.optional_agent_assistance", "predicate": "offers", "to_ref": PRODUCTS["collaboration"]["id"], "binding_phase": "deployment_time"},
        {"relation_id": "relation.cpra.agent_assists_privacy", "from_ref": "component.optional_agent_assistance", "predicate": "offers", "to_ref": PRODUCTS["privacy"]["id"], "binding_phase": "deployment_time"},
        {"relation_id": "relation.cpra.agent_assists_resolution", "from_ref": "component.optional_agent_assistance", "predicate": "offers", "to_ref": PRODUCTS["resolution"]["id"], "binding_phase": "deployment_time"},
        {"relation_id": "relation.cpra.agent_assists_assurance", "from_ref": "component.optional_agent_assistance", "predicate": "offers", "to_ref": PRODUCTS["assurance"]["id"], "binding_phase": "deployment_time"},
    ]

    crosswalks = [
        {"legacy_ref": "candidate.product.clean_room", "canonical_refs": [PRODUCTS["collaboration"]["id"], "pattern.privacy_enhancing_collaboration"], "disposition": "rename_product_and_retain_market_pattern"},
        {"legacy_ref": "candidate.product.privacy_rights_retention", "canonical_refs": [PRODUCTS["privacy"]["id"]], "disposition": "retain_product_with_authority_boundary"},
        {"legacy_ref": "candidate.product.entity_resolution", "canonical_refs": [PRODUCTS["resolution"]["id"]], "disposition": "retain_product_separate_from_mdm"},
        {"legacy_ref": "candidate.product.independent_assurance", "canonical_refs": [PRODUCTS["assurance"]["id"]], "disposition": "rename_product_independence_is_occurrence_evidence"},
        {"legacy_ref": "candidate.product.all_governance_bundle", "canonical_refs": ["suite.unified_data_governance"], "disposition": "reclassify_as_suite"},
        {"legacy_ref": "term.data_clean_room", "canonical_refs": [PRODUCTS["collaboration"]["id"], "pattern.privacy_enhancing_collaboration"], "disposition": "split_product_promise_from_architecture"},
        {"legacy_ref": "term.match", "canonical_refs": ["component.match_scoring_method", "semantic.cpra.resolution.link_decision"], "disposition": "split_score_from_decision"},
        {"legacy_ref": "term.independent_assurance", "canonical_refs": [PRODUCTS["assurance"]["id"], "semantic.cpra.assurance.independence_conflict"], "disposition": "split_product_from_occurrence_property"},
    ]

    negatives = [
        ("collab_warehouse", "a warehouse with access controls is automatically a clean room", "require collaboration identity, participant contracts, approved analysis and output-release lifecycle"),
        ("collab_tee", "a TEE is the controlled-collaboration product", "retain TEE as a replaceable runtime mechanism"),
        ("collab_attestation", "successful attestation authorizes data access or output release", "apply separate participant and relying policies"),
        ("collab_template", "one participant's template approval binds every participant", "require all applicable scoped approvals"),
        ("collab_restrictive", "policy composition may silently choose the least restrictive rule", "preserve all applicable constraints or refuse"),
        ("collab_query_success", "query success releases the result", "require a distinct output appraisal and release effect"),
        ("collab_mask", "masked or hashed identifiers prove anonymity", "bind attacker model, auxiliary data and release-risk evidence"),
        ("collab_dp", "the words differential privacy prove a valid guarantee", "verify privacy unit, adjacency, contribution bounds, mechanism and accountant"),
        ("collab_budget", "privacy budget can be checked after releasing output", "reserve and atomically spend before release"),
        ("collab_source", "linked data transfers source authority to the collaboration", "retain participant source and correction authority"),
        ("privacy_identity", "requestor authentication proves complete subject scope", "resolve identifiers, delegations and systems separately"),
        ("privacy_request", "receiving a request proves it must be executed", "bind competent authority, scope, exceptions and refusal rights"),
        ("privacy_consent", "a consent receipt is a general-purpose authorization token", "bind exact purpose, party, processing, data, time and withdrawal status"),
        ("privacy_schedule", "retention duration alone determines disposition", "bind trigger, cutoff, calendar, schedule edition, holds and authority"),
        ("privacy_hold", "erasure request overrides every active hold", "evaluate explicit authority precedence and record the outcome"),
        ("privacy_approval", "case approval means data was deleted or disclosed", "require target attempts and verified effect receipts"),
        ("privacy_ack", "provider 200 response proves physical erasure", "qualify provider semantics and verification evidence"),
        ("privacy_backup", "backup expiry and records disposition are the same", "keep recovery lifecycle and records authority separate"),
        ("privacy_archive", "permanent archive may ignore privacy/records authority", "bind preservation and access to an explicit authority profile"),
        ("privacy_close", "close a case when some systems timed out without declaring partiality", "record exact target coverage, gaps and residual owner"),
        ("resolution_identifier", "equal identifier carrier values prove the same entity", "bind namespace, issuer, scope and temporal validity"),
        ("resolution_normalize", "normalization is lossless and timeless", "version profiles and preserve loss/provenance"),
        ("resolution_blocked", "a pair excluded by blocking is a nonmatch", "classify it as unexamined"),
        ("resolution_score", "high model probability is an authoritative link", "apply an editioned decision policy and authority"),
        ("resolution_label", "human label is infallible ground truth", "record reviewer, evidence, uncertainty, conflicts and reversibility"),
        ("resolution_transitive", "pairwise links make every cluster pair equally supported", "retain edge and cluster evidence separately"),
        ("resolution_cluster", "cluster membership is a golden record", "submit a separate master-data change proposal"),
        ("resolution_merge", "resolution engine may mutate source systems", "require source/master authority and effect receipts"),
        ("resolution_accuracy", "one aggregate accuracy number proves fitness", "bind population, cut, subgroups, error costs and cluster metrics"),
        ("resolution_model", "predictive ML makes entity resolution agentic", "treat ML as one analytical method under deterministic contracts"),
        ("assurance_test", "all tests passed means the claim is true", "evaluate scope, criteria, method, evidence and defeaters"),
        ("assurance_attest", "authenticated attestation is independent assurance", "qualify issuer, appraiser independence and relying policy separately"),
        ("assurance_signature", "valid signature proves competence, mandate or truth", "verify those dimensions independently"),
        ("assurance_automation", "software can label its own result independent", "independence belongs to an evidenced appraisal occurrence"),
        ("assurance_no_findings", "no findings recorded means conformance", "require plan coverage and evidence of performed procedures"),
        ("assurance_score", "evidence strength is one compensating scalar", "keep blocking authority, integrity, freshness and defeater gates"),
        ("assurance_scope", "a verdict applies beyond its subject, criteria edition, cut and time", "make scope and validity part of identity"),
        ("assurance_approval", "positive assurance automatically authorizes production or purchase", "leave reliance decision with the relying authority"),
        ("assurance_cert", "certification, accreditation, validation, verification, inspection and testing are synonyms", "retain role, programme and activity distinctions"),
        ("assurance_history", "updated verdict overwrites the old verdict", "append supersession, withdrawal and recall events"),
        ("agent_legal", "an LLM decides which law applies", "require competent authority input and deterministic policy binding"),
        ("agent_policy", "generated text is an executable authorization policy", "parse to typed intent, validate, approve and compile or refuse"),
        ("agent_match", "agent explanation is match evidence", "bind exact pair features, method, threshold, review and occurrence receipts"),
        ("agent_assurance", "generated evidence summary is an independent appraisal", "retain accountable appraiser, source bindings and challenge lifecycle"),
        ("agent_effect", "a tool-using agent may execute deletion, merge or release from prose", "require typed command, authority, preconditions, budgets and effect gate"),
        ("agent_required", "agents are required for the platform to work", "remove every model/agent extension and preserve deterministic core behavior"),
        ("ai_prefix", "adding AI to clean room, privacy, resolution or assurance creates new product boundaries", "model exact optional method or extension without changing semantic ownership"),
        ("provider_docs", "official documentation qualifies a provider", "require exact versioned conformance receipts and operational evidence"),
        ("one_provider", "one working provider proves portability", "require at least two independent qualified implementations"),
        ("suite_semantics", "one governance console implies one bounded context", "keep independently owned products and ACLs"),
    ]
    negative_tests = [{"test_id": f"negative.cpra.{ident}", "prohibited_claim": prohibited, "expected_result": expected} for ident, prohibited, expected in negatives]
    semantic_gaps = [{
        "gap_id": f"gap.cpra.{ident}", "gap_class": "semantic_or_conformance", "statement": statement,
        "blocking": True,
        "closure_evidence": "Publish an exact owner and profile, typed refusal, executable law/conformance oracle, and evidence from two independent implementations or occurrences.",
    } for ident, statement in SEMANTIC_GAPS]

    return enrich_product_ddd({
        "contract_id": "contract.product_adjudication.collaboration_privacy_resolution_assurance.v0_1_0",
        "edition": 1,
        "status": "evidence_backed_adjudicated_candidate_not_ratified",
        "scope": "Controlled data collaboration, privacy-rights and records-disposition cases, entity resolution, and assurance-case appraisal, including deterministic compiler/library bindings and optional analytical/model/agent extensions.",
        "negative_scope": "Does not interpret law, own source/master truth, qualify providers, merge governance into one bounded context, make PETs products, or allow models/agents to decide authority or effects.",
        "artifact_kinds": kinds,
        "sources": sources,
        "artifacts": artifacts,
        "boundary_decisions": decisions,
        "ownership": ownership,
        "libraries": libraries,
        "requirements": requirements,
        "offers": offer_rows,
        "relations": relations,
        "crosswalks": crosswalks,
        "negative_tests": negative_tests,
        "binding_maps": binding_maps,
        "binding_gaps": [],
        "semantic_gaps": semantic_gaps,
        "non_collapse_laws": [
            "controlled collaboration != warehouse != TEE != MPC != differential privacy != approved output release",
            "requestor authentication != data-subject scope != authority != planned effect != verified effect",
            "retention schedule != backup expiry != preservation commitment != hold != disposition occurrence",
            "identifier equality != candidate pair != match score != link decision != entity cluster != master merge",
            "rules, probabilistic linkage and predictive ML are analytical methods, not effect authority",
            "test result != evidence sufficiency != attestation != independent appraisal != bounded verdict != relying decision",
            "independence is evidenced per appraisal occurrence; software and brands are not intrinsically independent",
            "suite packaging never merges semantic owners, consistency boundaries, refusals or exit rights",
            "provider documentation != conformance != qualification != portability",
            "optional model or agent output is a proposal, never semantic, legal, match, appraisal or effect authority",
            "removing all model and agent extensions preserves deterministic parsing, typing, constraint solving, numerical execution, qualification, policy, effects and receipts",
        ],
    })


def source_bytes() -> bytes:
    return (json.dumps(source(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


if __name__ == "__main__":
    SOURCE.write_bytes(source_bytes())
