#!/usr/bin/env python3
"""Deepen the nine remaining governance products from the researched GMO universe.

The GMO compiler contributions are useful candidate projections, but their own records say that
exact APIs, effect classifications, owner cardinality and independent implementations are missing.
Consequently every new product seam is represented and attributed. A seam remains a typed blocking
gap unless an independently owned exact compiler contract has since been published.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
GMO = ROOT / "research/domain_atlas/universes/governance_metadata_ontology_mdm"
RETIRED_GMO_UPSTREAMS = {
    "gmo.library.assurance_workflow", "gmo.library.catalog_discovery",
    "gmo.library.classification_privacy", "gmo.library.entity_resolution",
    "gmo.library.master_authority",
    "gmo.library.identity_kernel", "gmo.library.schema_contracts", "gmo.library.semantic_query",
    "gmo.library.data_product_contracts", "gmo.library.ontology_core", "gmo.library.lineage_core",
    "gmo.library.reference_core",
}

PRODUCTS = {
    "metadata": "product.metadata_discovery",
    "glossary": "product.business_glossary",
    "ontology": "product.ontology_knowledge_model",
    "schema": "product.schema_registry",
    "contract": "product.data_contract_registry",
    "master": "product.master_reference_data",
    "policy": "product.data_use_policy",
    "publication": "product.data_product_publication",
    "marketplace": "product.data_marketplace",
}

PRODUCT_FIELDS = {
    "sovereign_question", "users", "harmed_parties", "jobs", "outcomes", "negative_mission",
    "lifecycle_states", "commands", "events", "invariants", "refusals", "automation_modality",
}
DDD_FIELDS = {
    "domain_vision_statement", "subdomain_classification", "bounded_context_boundary",
    "ubiquitous_language_policy", "context_map", "anti_corruption_layers", "published_language",
    "value_objects", "entities", "aggregates", "aggregate_roots", "aggregate_invariants",
    "commands", "domain_events", "refusal_failure_catalog", "domain_services",
    "application_services", "repositories", "factories", "specifications", "state_machine",
    "policies_and_reactions", "sagas_and_process_managers", "read_models_and_projections",
    "integration_event_policy", "concurrency_and_idempotency", "time_model",
    "event_storming_swimlanes", "nonfunctional_laws",
}

AUTOMATION = {
    "default": "DETERMINISTIC_CORE_ONLY",
    "postures": ["PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"],
    "law": "Models and agents may propose classifications, mappings, definitions, matches, policies, listings or change plans only; deterministic owners validate every proposal and retain semantic, lifecycle, evidence and authority control.",
    "removal_law": "Removing every optional model or agent preserves identity, vocabulary, lifecycle, compatibility, inference, policy, publication, request, evidence and refusal behavior; an intent that explicitly requires unavailable assistance yields capability_unavailable.",
    "hard_work_law": "Automation never replaces vocabulary enumeration, homonym resolution, invariants, temporal identity, compatibility laws, authority, evidence, qualification, acceptance, effects or reconciliation.",
}


def jl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


GMO_SOURCES = {row["source_id"]: row for row in jl(GMO / "evidence-sources.jsonl")}
GMO_CONTEXTS = {row["context_id"]: row for row in jl(GMO / "bounded-context-candidates.jsonl")}
GMO_LIBRARIES = {row["library_id"]: row for row in jl(GMO / "library-boundaries.jsonl")}
GMO_REPLACEMENTS = {
    "gmo.library." + row["retired_library_ref"].removeprefix("library.gmo."): row
    for row in jl(GMO / "retired-compositions.jsonl")
}


def pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_"))


def local_library(product_key: str, key: str) -> str:
    return f"library.governance_{product_key}.{key}"


def local_capability(product_key: str, key: str) -> str:
    return f"capability.governance_{product_key}.{key}"


def local_semantic(product_key: str, key: str) -> str:
    return f"semantic.governance_{product_key}.{key}"


def L(product: str, key: str, upstream: str, types: list[str], operations: list[str], decisions: list[str], laws: list[str], refusals: list[str], deps: list[str] | None = None, effect: str = "pure_no_io") -> dict[str, Any]:
    return {"product": product, "key": key, "upstream": f"gmo.library.{upstream}", "types": types, "operations": operations, "decisions": decisions, "laws": laws, "refusals": refusals, "deps": deps or [], "effect": effect}


LIBRARY_SPECS = [
    # Metadata discovery owns projections and their observation evidence, never source truth.
    L("metadata", "acquisition_port", "metadata_acquisition", ["HarvestIntent", "HarvestCursor", "SourceOccurrenceRef", "ExtractionReceipt"], ["plan_harvest", "ingest_snapshot", "ingest_change", "reconcile_cursor"], ["connector_profile", "cursor_identity", "deletion_posture", "normalization_profile"], ["harvested metadata remains source-attributed", "cursor advancement requires a receipt", "absence in one harvest is not source deletion"], ["source_occurrence_unbound", "cursor_conflict", "normalization_loss_undeclared", "completion_unknown"], effect="effect_intents_and_receipts"),
    L("metadata", "assertion_record", "metadata_assertions", ["MetadataAssertion", "AssertionEdition", "StatementProvenance", "ValidityInterval"], ["publish_assertion", "retract_assertion", "query_effective_assertions", "compare_editions"], ["assertion_identity", "source_precedence", "validity_model", "conflict_posture"], ["metadata assertion is not described asset", "observed declared and inferred assertions remain distinct", "retraction preserves history"], ["subject_unresolved", "publisher_unattributed", "validity_ambiguous", "conflict_unresolved"]),
    L("metadata", "discovery_projection", "catalog_discovery", ["DiscoveryDocument", "Facet", "BrowseNode", "ProjectionCut"], ["project_listing", "build_facets", "browse_projection", "remove_projection"], ["projection_schema", "facet_policy", "visibility_cut", "ranking_signal_policy"], ["projection is not source record", "listing is not certification or access grant", "visibility is cut-bound"], ["projection_schema_unbound", "visibility_unknown", "stale_projection", "policy_denied"], ["assertion_record"], effect="effect_intents_and_receipts"),
    L("metadata", "search_browse", "catalog_discovery", ["DiscoveryQuery", "DiscoveryResult", "RankingEvidence", "CoverageStatement"], ["search_metadata", "browse_metadata", "explain_ranking", "report_coverage"], ["query_profile", "ranking_profile", "freshness_requirement", "coverage_semantics"], ["rank is not relevance truth", "empty result is not proof of absence", "coverage unknown remains explicit"], ["query_unsupported", "freshness_unsatisfied", "coverage_unknown", "result_truncated"], ["discovery_projection"]),
    L("metadata", "federation", "federation", ["CatalogPeer", "HarvestToken", "FederatedAssertion", "ConflictSet"], ["register_peer", "harvest_peer", "merge_federated_projection", "record_conflict"], ["peer_identity", "precedence_policy", "conflict_policy", "partial_failure_policy"], ["federation never invents global last-write-wins", "peer assertion keeps provenance", "partial peer failure is visible"], ["peer_unqualified", "token_invalid", "precedence_ambiguous", "partial_completion"], ["assertion_record", "discovery_projection"], effect="effect_intents_and_receipts"),
    L("metadata", "freshness_coverage", "audit_receipts", ["FreshnessObservation", "CoverageScope", "DiscoverySlo", "DiscoveryReceipt"], ["observe_freshness", "measure_coverage", "evaluate_discovery_slo", "publish_discovery_receipt"], ["freshness_clock", "coverage_denominator", "slo_policy", "unknown_posture"], ["freshness is observed not inferred from schedule", "coverage binds an explicit population", "SLO pass is not content correctness"], ["clock_unbound", "population_unknown", "observation_missing", "slo_indeterminate"], ["acquisition_port", "search_browse"]),

    # Glossary is human language governance, not ontology inference.
    L("glossary", "term_identity", "terminology_core", ["TerminologicalConceptId", "DesignationId", "LexicalForm", "LanguageTag", "BusinessScopeRef"], ["validate_designation", "plan_concept_registration", "plan_designation_addition", "resolve_designation"], ["business_scope", "concept_identity_authority", "language_script", "preferred_designation"], ["text designation concept definition and term entry are distinct", "same character sequence does not prove same concept", "concept identity survives preferred-label changes"], ["scope_missing", "concept_authority_missing", "language_invalid", "designation_collision"], effect="effect_intents_and_receipts"),
    L("glossary", "definition_scope", "terminology_core", ["DefinitionEdition", "BusinessScopeRef", "CharacteristicSet", "UsageGuidance", "Counterexample"], ["validate_definition", "compare_definitions", "plan_definition_publication", "plan_definition_supersession"], ["definition_authority", "scope_grain", "characteristic_selection", "normative_posture"], ["definition is concept-and-scope-bound", "definition usage guidance example and formal axiom are distinct", "examples never complete a definition"], ["scope_missing", "definition_circular", "authority_missing", "characteristic_conflict"], ["term_identity"], effect="effect_intents_and_receipts"),
    L("glossary", "lexical_relations", "terminology_core", ["SynonymAssertion", "HomonymGroup", "AbbreviationAssertion", "TranslationResidual"], ["evaluate_synonymy", "resolve_homonym", "expand_abbreviation", "translate_designation"], ["relation_kind", "directionality", "language_pair", "ambiguity_and_loss"], ["synonym is not identity", "homonyms require scoped resolution", "translation direction and loss are explicit"], ["relation_scope_missing", "ambiguous_homonym", "translation_unqualified", "loss_unaccepted"], ["term_identity"]),
    L("glossary", "taxonomy_binding", "taxonomy_core", ["ConceptSchemeEdition", "TaxonomyRelation", "SchemeMembership", "Notation"], ["validate_scheme", "evaluate_placement", "compare_scheme_editions", "plan_scheme_publication"], ["scheme_identity", "relation_vocabulary", "polyhierarchy", "cycle_posture"], ["taxonomy placement is not OWL subsumption", "broader-generic broader-partitive and broader-instantial remain distinct", "notation is not concept identity"], ["scheme_unbound", "relation_kind_ambiguous", "cycle_forbidden", "placement_authority_missing"], ["term_identity"], effect="effect_intents_and_receipts"),
    L("glossary", "stewardship_lifecycle", "accountability", ["GlossaryChangeProposal", "TermStewardRef", "ReviewDecision", "DeprecationNotice"], ["plan_review_assignment", "evaluate_review", "plan_glossary_publication", "plan_glossary_deprecation"], ["steward_authority", "maker_checker", "review_evidence", "deprecation_successor"], ["stewardship assignment is not semantic approval", "approval is edition-bound and authority-bearing", "deprecation preserves history and plural or absent successors"], ["steward_unassigned", "maker_checker_violated", "evidence_missing", "successor_ambiguous"], ["definition_scope", "lexical_relations", "taxonomy_binding"], effect="effect_intents_and_receipts"),

    # Ontology and knowledge model owns formal semantics, mappings and validation reports.
    L("ontology", "ontology_identity_imports", "ontology_core", ["OntologyIri", "VersionIri", "OntologyEdition", "ResolvedImportClosure"], ["validate_ontology_identity", "plan_import_resolution", "seal_import_closure", "plan_ontology_registration"], ["ontology_iri", "version_iri", "document_resolution", "import_version"], ["ontology IRI version IRI document location and registry occurrence are distinct", "imports bind exact editions", "missing import never silently disappears"], ["iri_invalid", "import_unresolved", "edition_ambiguous", "import_cycle_forbidden"], effect="effect_intents_and_receipts"),
    L("ontology", "axiom_profile", "ontology_core", ["LogicalAxiom", "EntityDeclaration", "LogicProfile", "AxiomProvenance"], ["declare_entity", "validate_axiom", "validate_profile", "derive_ontology_revision"], ["logic_profile", "entity_declaration", "annotation_posture", "unsupported_axiom"], ["annotation assertion is not logical axiom", "profile membership is not consistency", "revision preserves prior editions"], ["entity_kind_conflict", "axiom_unsupported", "profile_violation", "axiom_unattributed"], ["ontology_identity_imports"]),
    L("ontology", "reasoning_entailment", "ontology_core", ["FormalSemantics", "EntailmentRequest", "EntailmentResult", "ConsistencyResult"], ["check_consistency", "evaluate_entailment", "explain_entailment", "compare_entailment_regimes"], ["formal_semantics", "entailment_regime", "open_closed_world", "resource_bound"], ["entailed is not explicitly asserted or observed", "open-world unknown false inconsistent and timeout remain distinct", "reasoner identity cannot change the selected formal semantics"], ["regime_unsupported", "ontology_inconsistent", "resource_exhausted", "result_inconclusive"], ["axiom_profile"]),
    L("ontology", "shape_validation", "knowledge_graph", ["DataGraphCut", "ShapesGraphCut", "FocusNode", "ValidationReport"], ["validate_shapes_graph", "select_focus_nodes", "validate_data_graph", "explain_validation_result"], ["shacl_edition", "target_selection", "entailment_option", "severity_posture"], ["shape validation never mutates input graphs", "shape conformance is not ontology consistency completeness or real-world truth", "validation result binds exact data and shape graph cuts"], ["shape_invalid", "focus_scope_unknown", "recursion_unsupported", "validation_incomplete"], ["axiom_profile"]),
    L("ontology", "ontology_mapping", "ontology_core", ["OntologyMappingEdition", "MappingAssertion", "MappingDirection", "MappingEvidenceSet"], ["validate_mapping", "evaluate_mapping_evidence", "plan_mapping_approval", "plan_mapping_retraction"], ["mapping_relation", "directionality", "source_target_scope", "evidence_threshold"], ["same label is not equivalence", "close match exact match and OWL equivalence remain distinct", "mapping approval cannot edit source ontologies or imply reverse mappings"], ["source_or_target_unbound", "mapping_relation_ambiguous", "evidence_insufficient", "authority_missing"], ["ontology_identity_imports"], effect="effect_intents_and_receipts"),
    L("ontology", "knowledge_graph_release", "knowledge_graph", ["GraphReleaseEdition", "NamedGraphPartition", "GraphAssertionId", "CanonicalDataset"], ["validate_assertion_envelope", "assemble_graph_release", "canonicalize_graph_release", "plan_graph_publication"], ["dataset_identity", "assertion_identity", "partition_policy", "canonicalization_digest"], ["knowledge graph does not own ontology axioms source facts or real-world truth", "graph release is immutable and cut-bound", "canonical digest is representation identity not semantic equivalence"], ["graph_identity_missing", "assertion_provenance_missing", "partition_leak", "canonicalization_too_complex"], ["ontology_identity_imports", "ontology_mapping"], effect="effect_intents_and_receipts"),

    # Schema registry owns runtime structural editions and compatibility decisions only.
    L("schema", "subject_identity", "identity_kernel", ["SchemaSubject", "SubjectNamespace", "SubjectAlias", "SubjectStatus"], ["register_subject", "resolve_subject", "bind_alias", "retire_subject"], ["subject_naming", "namespace_authority", "alias_policy", "retirement_policy"], ["subject is not schema version or topic/table identity", "alias is not authority", "retirement preserves resolution history"], ["namespace_unbound", "subject_collision", "alias_conflict", "retirement_blocked"]),
    L("schema", "artifact_profile", "schema_contracts", ["SchemaArtifact", "SchemaFormat", "CanonicalSchema", "SchemaDigest"], ["parse_schema", "canonicalize_schema", "validate_schema", "compute_digest"], ["format_edition", "canonicalization_profile", "unknown_keyword_posture", "reference_policy"], ["parse success is not compatibility", "canonicalization never invents equivalence", "schema and business meaning are distinct"], ["format_unsupported", "schema_invalid", "canonicalization_loss", "reference_unresolved"], ["subject_identity"]),
    L("schema", "version_registry", "schema_contracts", ["SchemaVersion", "VersionOrdinal", "RegistrationRequest", "RegistrationReceipt"], ["register_version", "fetch_version", "list_versions", "deprecate_version"], ["version_identity", "deduplication_policy", "ordering_policy", "deprecation_policy"], ["version identity is immutable", "registration is not compatibility approval unless policy is applied", "duplicate digest policy is explicit"], ["subject_unknown", "version_conflict", "digest_conflict", "illegal_deprecation"], ["artifact_profile"], effect="effect_intents_and_receipts"),
    L("schema", "compatibility", "schema_contracts", ["CompatibilityMode", "ReaderWriterPair", "CompatibilityResult", "CompatibilityResidual"], ["check_backward", "check_forward", "check_full", "explain_incompatibility"], ["transitivity", "history_scope", "default_value_semantics", "unknown_feature_posture"], ["syntactic compatibility is format and policy scoped", "reader-writer compatibility is directional", "compatibility does not prove business substitutability"], ["mode_unbound", "history_incomplete", "feature_unsupported", "compatibility_indeterminate"], ["version_registry"]),
    L("schema", "reference_closure", "schema_contracts", ["SchemaReference", "ReferenceGraph", "ResolvedClosure", "ClosureDigest"], ["add_reference", "resolve_closure", "detect_cycle", "seal_closure"], ["reference_version_policy", "cycle_policy", "remote_resolution", "closure_identity"], ["schema identity includes exact reference closure", "floating reference is explicit", "missing reference blocks registration"], ["reference_missing", "reference_cycle", "remote_unavailable", "closure_changed"], ["version_registry"]),
    L("schema", "migration_lifecycle", "assurance_workflow", ["SchemaChange", "ImpactAssessment", "MigrationPlan", "SunsetNotice"], ["propose_schema_change", "assess_impact", "approve_migration", "publish_sunset"], ["change_classification", "blast_radius", "approval_authority", "sunset_policy"], ["compatible change is not zero-impact", "migration and registration are distinct", "sunset preserves in-flight consumer disposition"], ["impact_unknown", "consumer_census_incomplete", "approval_missing", "sunset_too_early"], ["compatibility", "reference_closure"], effect="effect_intents_and_receipts"),

    # Data contract registry owns negotiated promises, not observations or effects.
    L("contract", "contract_identity", "data_product_contracts", ["DataContractId", "ContractEdition", "ContractDigest", "ContractStatus"], ["draft_contract", "register_contract", "resolve_edition", "supersede_contract"], ["identity_scope", "edition_policy", "canonicalization", "supersession_policy"], ["contract document and contract edition are distinct", "published editions are immutable", "supersession never rewrites acceptance history"], ["identity_ambiguous", "edition_conflict", "digest_mismatch", "supersession_invalid"]),
    L("contract", "party_purpose_roles", "accountability", ["ProducerParty", "ConsumerParty", "Purpose", "RoleAssignment"], ["bind_producer", "bind_consumer", "bind_purpose", "delegate_role"], ["party_identity", "purpose_scope", "role_authority", "delegation_policy"], ["producer consumer owner steward and custodian are distinct", "acceptance authority is explicit", "purpose is editioned"], ["party_unresolved", "purpose_ambiguous", "role_conflict", "delegation_invalid"], ["contract_identity"]),
    L("contract", "data_schema_binding", "data_product_contracts", ["DataPortRef", "SchemaEditionRef", "DatasetIdentity", "BindingResidual"], ["bind_data_port", "bind_schema_edition", "bind_dataset_identity", "validate_binding"], ["port_identity", "schema_binding", "physical_location_posture", "residual_policy"], ["contract references rather than owns schema and dataset truth", "binding is exact-editioned", "location change does not silently change identity"], ["port_unresolved", "schema_unbound", "dataset_identity_ambiguous", "binding_residual_unaccepted"], ["contract_identity"]),
    L("contract", "quality_service_obligations", "data_product_contracts", ["QualityObligation", "ServiceObjective", "FreshnessPromise", "SupportPromise"], ["declare_quality_obligation", "declare_service_objective", "declare_freshness", "declare_support"], ["obligation_measure", "threshold_policy", "service_window", "remedy_posture"], ["declared obligation is not observed attainment", "quality promise is purpose scoped", "SLA breach and data defect are distinct"], ["measure_unbound", "threshold_ambiguous", "window_missing", "remedy_authority_missing"], ["data_schema_binding"]),
    L("contract", "compatibility_acceptance", "assurance_workflow", ["ContractCompatibility", "AcceptanceCriteria", "AcceptanceDecision", "AcceptanceEvidence"], ["compare_contract_editions", "evaluate_acceptance", "accept_contract", "reject_contract"], ["compatibility_relation", "acceptance_authority", "evidence_policy", "conditional_acceptance"], ["compatibility is not acceptance", "acceptance is party and purpose scoped", "conditional acceptance retains obligations"], ["compatibility_unknown", "criteria_incomplete", "authority_missing", "evidence_insufficient"], ["quality_service_obligations"]),
    L("contract", "change_breach_case", "assurance_workflow", ["ContractChange", "BreachFinding", "ContractCase", "RemediationPlan"], ["propose_change", "record_breach_finding", "open_contract_case", "close_case"], ["change_classification", "breach_materiality", "notice_policy", "closure_evidence"], ["change proposal is not accepted edition", "breach finding is not remedy execution", "case closure preserves residuals"], ["blast_radius_unknown", "breach_scope_ambiguous", "notice_missing", "closure_unproved"], ["compatibility_acceptance"], effect="effect_intents_and_receipts"),
    L("contract", "deprecation_exit", "data_product_contracts", ["DeprecationNotice", "ConsumerCensus", "ExitPackage", "TerminationReceipt"], ["announce_deprecation", "bind_consumer_census", "export_contract_package", "terminate_contract"], ["notice_period", "in_flight_disposition", "exit_completeness", "termination_authority"], ["deprecation is not termination", "exit includes semantic policy and evidence artifacts", "consumer obligations survive as declared"], ["consumer_census_incomplete", "notice_period_unsatisfied", "exit_package_incomplete", "termination_blocked"], ["change_breach_case"], effect="effect_intents_and_receipts"),

    # MDM keeps identity, authority, survivorship and reference data separate.
    L("master", "master_domain_identity", "master_authority", ["MasterDomain", "MasterEntityId", "AcceptedResolutionAssertionRef", "IdentityIssuingAuthorityRef"], ["evaluate_identity_issuance", "plan_identity_issuance", "apply_identity_issuance_receipt", "plan_identity_retirement"], ["domain_scope", "identity_authority", "resolution_evidence", "merge_split_retirement_policy"], ["master identity is not source record match score candidate link or resolution cluster", "resolution assertion and identity issuance are distinct", "identity authority is scope-bound", "retirement preserves aliases and history"], ["domain_unbound", "identity_collision", "resolution_assertion_unaccepted", "retirement_conflict"], effect="effect_intents_and_receipts"),
    L("master", "source_record_authority", "master_authority", ["SourceRecordRef", "AttributeAuthorityAssertion", "AuthorityValidityInterval", "EffectiveCandidateSet"], ["validate_source_reference", "evaluate_attribute_authority", "rank_candidates", "detect_authority_conflict"], ["attribute_scope", "source_record_identity", "valid_time", "conflict_precedence"], ["master data references and never registers source records", "source priority is attribute context purpose and time scoped", "latest is not automatically authoritative", "unselected candidates retain provenance"], ["source_unresolved", "authority_overlap", "precedence_incomplete", "effective_time_invalid"], ["master_domain_identity"]),
    L("master", "survivorship_projection", "master_authority", ["SurvivorshipRule", "CandidateValue", "FieldDecision", "MasterProjectionEdition"], ["compile_survivorship", "select_field_value", "assemble_master_projection", "explain_survivorship"], ["rule_precedence", "missing_value_posture", "tie_break", "manual_override"], ["golden record is reproducible cut-bound projection not universal truth", "field provenance and residual conflicts are retained", "manual override requires authority reason scope and expiry"], ["rule_conflict", "candidate_provenance_missing", "tie_unresolved", "override_unauthorized"], ["source_record_authority"]),
    L("master", "stewardship_case", "accountability", ["MasterStewardshipCase", "Conflict", "StewardDecision", "CorrectionProposal"], ["open_master_case", "assign_steward", "record_decision", "submit_correction"], ["case_severity", "steward_authority", "maker_checker", "correction_scope"], ["steward decision is not source mutation", "case closure requires evidence", "conflict history is append-only"], ["steward_unassigned", "authority_missing", "maker_checker_violated", "closure_evidence_missing"], ["survivorship_projection"], effect="effect_intents_and_receipts"),
    L("master", "reference_set", "reference_core", ["ReferenceSet", "ReferenceSetEdition", "ReferenceValue", "PublisherAuthority"], ["validate_reference_edition", "resolve_effective_value", "plan_reference_publication", "plan_value_deprecation"], ["publisher_authority", "set_and_edition_identity", "validity_model", "deprecation_replacement"], ["reference value classifies other data and is not master entity", "set identity edition value and distribution are distinct", "deprecated values preserve historical resolution"], ["publisher_unresolved", "value_collision", "validity_overlap", "replacement_ambiguous"], effect="effect_intents_and_receipts"),
    L("master", "code_set_lifecycle", "reference_core", ["CodeSetEdition", "CodeIdentity", "ConceptRef", "Designation"], ["validate_code", "plan_code_addition", "plan_designation_change", "plan_code_retirement"], ["maintenance_agency", "code_identity", "designation_language", "retirement_and_reuse"], ["code concept designation and display label are distinct", "code set edition and code validity are distinct", "retirement never deletes historical meaning", "reuse is forbidden unless exact policy permits"], ["agency_unbound", "code_collision", "language_invalid", "reuse_forbidden"], ["reference_set"], effect="effect_intents_and_receipts"),
    L("master", "crosswalk_mapping", "reference_core", ["CrosswalkEdition", "MappingAssertion", "MappingRelationship", "InformationLossProfile"], ["validate_mapping", "map_value", "compose_crosswalks", "plan_crosswalk_publication"], ["source_target_editions", "directionality", "mapping_cardinality", "loss_acceptance"], ["crosswalk is not equivalence by default", "mapping binds exact source and target editions direction context and cardinality", "forward mapping never implies reverse mapping", "composition accumulates partiality ambiguity and loss"], ["edition_unbound", "cardinality_ambiguous", "mapping_context_missing", "loss_unaccepted"], ["reference_set", "code_set_lifecycle"], effect="effect_intents_and_receipts"),

    # Data-use policy owns policy statements and decisions, not enforcement effects.
    L("policy", "policy_statement", "policy_model", ["PolicyId", "PolicyEdition", "Permission", "Prohibition", "Duty"], ["validate_policy_edition", "plan_policy_publication", "plan_policy_revocation", "reconcile_policy_effect"], ["language_profile", "issuer_authority_and_delegation", "validity_and_activation", "supersession_and_revocation"], ["policy document edition deployment and product are distinct", "syntax validity is not issuer authority approval activation or legal validity", "revocation preserves historical decisions"], ["issuer_unbound", "delegation_invalid", "policy_invalid", "lifecycle_completion_unknown"], effect="effect_intents_and_receipts"),
    L("policy", "purpose_action_resource", "classification_privacy", ["PurposeRef", "ProcessingActionRef", "ResourceRef", "DataCategoryRef", "AttributeEvidence"], ["bind_decision_request", "validate_attribute_cut", "derive_sensitive_view", "compare_request_cuts"], ["external_vocabulary_editions", "attribute_sources", "temporal_cut", "missing_conflict_and_redaction"], ["policy consumes and never owns purpose resource data-category identity consent or legal-basis truth", "classification is evidence-bound and does not grant access", "missing unknown withheld stale and conflicting remain distinct"], ["purpose_unresolved", "resource_unresolved", "attribute_issuer_unbound", "attribute_conflict"], ["policy_statement"]),
    L("policy", "rule_precedence", "policy_model", ["PolicyRule", "CompiledPolicySet", "DecisionEffect", "CombinationTrace"], ["compile_policy_set", "evaluate_applicability", "combine_rule_results", "explain_combination"], ["applicability", "effect_lattice", "combining_algorithm", "indeterminate_and_error_semantics"], ["permit deny not-applicable and indeterminate remain distinct", "precedence is declared not inferred from retrieval order", "provider identity never changes combination semantics"], ["combining_algorithm_missing", "precedence_cycle", "function_unsupported", "combination_nondeterministic"], ["policy_statement", "purpose_action_resource"]),
    L("policy", "decision_evaluation", "policy_client", ["ValidatedRequestCut", "PolicyDecision", "DecisionTrace", "DecisionExplanation"], ["evaluate_decision", "explain_decision", "derive_cache_key", "replay_decision"], ["policy_and_request_cuts", "evaluator_edition", "cache_and_replay", "reevaluation_trigger"], ["decision binds exact policy request attribute evaluator and clock cuts", "decision is not authentication entitlement approval enforcement or effect", "prior permit does not authorize unbounded future use"], ["policy_cut_unavailable", "attribute_missing", "decision_indeterminate", "reevaluation_required"], ["rule_precedence"]),
    L("policy", "obligation_lifecycle", "policy_client", ["ObligationAssignment", "ObligationDispatchIntent", "ObligationDispatchReceipt", "ObligationState"], ["plan_obligation_dispatch", "reconcile_obligation_receipt", "plan_usage_reevaluation", "plan_usage_termination"], ["obligation_versus_advice", "recipient_capability", "timing_continuity", "outcome_failure"], ["returned obligation dispatch receipt execution outcome and verified fulfillment are distinct", "policy coordinates and never executes business effects", "unknown completion reconciles before retry"], ["recipient_unresolved", "capability_unsupported", "dispatch_completion_unknown", "termination_unconfirmed"], ["decision_evaluation"], effect="effect_intents_and_receipts"),
    L("policy", "decision_receipt", "audit_receipts", ["DecisionOccurrence", "DecisionEvidenceRecord", "ProtectedDecisionRecord", "DecisionEvidenceAppendReceipt"], ["assemble_decision_evidence", "protect_sensitive_fields", "plan_evidence_append", "verify_decision_evidence"], ["occurrence_identity", "policy_input_engine_digest", "sensitive_field_protection", "retention_binding"], ["decision evidence proves evaluation occurrence not enforcement", "redaction preserves verifiability", "retention authority is external", "absence of a log is not absence of a decision without completeness evidence"], ["occurrence_unbound", "digest_incomplete", "sensitive_field_leak", "append_completion_unknown"], ["decision_evaluation", "obligation_lifecycle"], effect="effect_intents_and_receipts"),

    # Publication creates a governed product edition; marketplace only lists/offers it.
    L("publication", "product_identity", "data_product_contracts", ["DataProductId", "DataProductEditionId", "ProductKind", "ProductScope", "EditionRelation"], ["validate_product_edition", "compare_product_editions", "plan_product_registration", "plan_product_supersession"], ["identity_authority", "edition_semantics", "product_scope", "supersession_relation"], ["data product edition dataset table API offer and deployment are distinct", "identifier name registry occurrence and package digest are distinct", "supersession and compatibility are explicit directional relations"], ["identity_authority_missing", "identity_collision", "edition_conflict", "registration_completion_unknown"], effect="effect_intents_and_receipts"),
    L("publication", "port_contract_assembly", "data_product_contracts", ["ProductPortEdition", "ExternalEditionBinding", "DependencyGraph", "ClosedPortAssembly"], ["bind_product_port", "assemble_dependency_graph", "validate_port_closure", "derive_dependency_impact"], ["port_taxonomy", "binding_exactness", "compatibility_requirement", "dependency_closure"], ["port contract schema dataset distribution endpoint and credential are distinct", "all external dependencies are editioned", "closed structural graph is not runtime readiness"], ["port_identity_collision", "external_edition_unbound", "compatibility_unknown", "dependency_graph_open"], ["product_identity"]),
    L("publication", "accountability_stewardship", "accountability", ["AccountabilityBinding", "ResponsibilityScope", "AuthorityEvidenceRef", "SupportCoverage"], ["validate_accountability_binding", "plan_accountability_assignment", "plan_accountability_revocation", "derive_support_coverage"], ["role_vocabulary", "responsibility_scope", "authority_evidence", "support_model"], ["owner semantic-owner steward custodian publisher operator and support-owner are distinct", "product binds and never invents organizational authority", "delegation never transfers ultimate accountability"], ["accountable_owner_missing", "authority_evidence_missing", "segregation_violated", "support_gap"], ["product_identity"], effect="effect_intents_and_receipts"),
    L("publication", "readiness_certification", "assurance_workflow", ["ReadinessCriteriaEdition", "EvidenceCut", "RequirementSatisfaction", "ReadinessVerdict", "ExternalCertificateRef"], ["validate_readiness_criteria", "assemble_readiness_evidence", "evaluate_readiness", "explain_readiness"], ["criteria_profile", "evidence_cut_and_freshness", "assessor_independence", "residual_and_exception_posture"], ["readiness evidence verdict approval publication and external certificate are distinct", "product cannot certify itself", "quality SLO FAIR security and contract evidence remain separate dimensions"], ["criteria_incomplete", "evidence_stale", "independence_unproved", "readiness_undetermined"], ["port_contract_assembly", "accountability_stewardship"]),
    L("publication", "publication_lifecycle", "data_product_contracts", ["PublicationEdition", "PublicationManifest", "PublicationIntent", "PublicationReceipt", "VisibilityScope"], ["plan_publication", "reconcile_publication_receipt", "plan_visibility_change", "plan_unpublication"], ["publication_authority", "visibility_scope", "target_registry", "idempotency_and_reconciliation"], ["readiness approval publication intent receipt listing and consumption are distinct", "publication binds exact product assembly verdict approval and target", "publication never mutates referenced resources"], ["product_not_ready", "approval_missing", "publication_authority_missing", "publication_completion_unknown"], ["readiness_certification"], effect="effect_intents_and_receipts"),
    L("publication", "change_notification", "assurance_workflow", ["ClassifiedProductChange", "SubscriberPopulation", "ChangeNoticePlan", "NoticeDeliveryStatus", "ChangeClosureResult"], ["classify_product_change", "plan_change_notice", "reconcile_notice_delivery", "evaluate_migration_window"], ["change_classification", "subscriber_population_and_cut", "notice_window", "in_flight_disposition"], ["change diff notice delivery acknowledgement and migration are distinct", "logs never silently become a complete consumer census", "delivered notice does not prove migration"], ["change_class_unknown", "subscriber_population_unknown", "delivery_partial", "migration_incomplete"], ["publication_lifecycle"], effect="effect_intents_and_receipts"),
    L("publication", "recall_decommission_exit", "data_product_contracts", ["RecallCase", "DependencyBlastRadius", "ExitPackage", "ExitValidationResult", "DecommissionDecision"], ["open_recall_case", "plan_recall_propagation", "assemble_exit_package", "evaluate_decommission"], ["recall_authority_and_scope", "dependency_blast_radius", "exit_package_profile", "decommission_gate"], ["deprecation sunset recall revocation unpublication deletion and exit are distinct", "recall never self-attests downstream effects", "package integrity is not semantic portability", "decommission waits for dependencies obligations and exit evidence"], ["recall_scope_ambiguous", "propagation_incomplete", "exit_package_incomplete", "decommission_unsafe"], ["change_notification"], effect="effect_intents_and_receipts"),

    L("marketplace", "offer_listing", "catalog_discovery", ["MarketplaceOfferId", "OfferEditionId", "ListingEditionId", "PublishedProductEditionRef", "TermsEditionRef", "VisibilityScope"], ["validate_offer_edition", "derive_listing_projection", "plan_listing_publication", "plan_listing_withdrawal"], ["offer_identity_authority", "bound_product_edition", "terms_and_price_editions", "audience_and_visibility"], ["product publication offer listing policy agreement and subscription are distinct", "offer binds exact external editions without acquiring their authority", "an offer proposes terms and grants none", "listing receipt proves only its exact target effect"], ["offer_issuer_unbound", "product_edition_unpublished", "external_edition_unbound", "publication_completion_unknown"], effect="effect_intents_and_receipts"),
    L("marketplace", "discovery_experience", "catalog_discovery", ["MarketplaceQuery", "CatalogCut", "CandidateOfferSet", "RankingProfileRef", "RankingEvidence", "DiscoveryResult"], ["normalize_marketplace_query", "derive_candidate_offers", "rank_candidate_offers", "explain_discovery_result"], ["query_semantics", "candidate_coverage", "ranking_profile", "personalization_posture"], ["visibility discoverability relevance rank suitability recommendation eligibility and endorsement are distinct", "ranking binds exact profile feature evidence and resource cuts", "empty filtered truncated timed-out and incomplete remain distinct"], ["query_unsupported", "candidate_coverage_unknown", "ranking_profile_missing", "result_truncated"], ["offer_listing"]),
    L("marketplace", "eligibility", "policy_client", ["EligibilityCaseId", "ConsumerRef", "PurposeRef", "CredentialVerificationResultRef", "PolicyDecisionRef", "CommercialQualificationRef", "MarketplaceEligibilityStatus"], ["plan_eligibility_evidence_request", "validate_eligibility_evidence", "derive_marketplace_eligibility", "explain_marketplace_eligibility"], ["consumer_and_purpose_cut", "required_external_decisions", "combination_semantics", "indeterminate_posture"], ["marketplace consumes and never issues identity credential purpose policy or qualification evidence", "credential verification is not claim truth or eligibility", "eligibility is not approval entitlement provisioning or access"], ["consumer_unresolved", "purpose_missing", "required_decision_missing", "eligibility_expired"], ["offer_listing"]),
    L("marketplace", "subscription_request", "access_workflow", ["SubscriptionRequestId", "OfferEditionRef", "ApprovalRoute", "ExternalApprovalDecisionRef", "SubscriptionCase"], ["validate_subscription_request", "plan_approval_route", "reconcile_external_decision", "plan_request_withdrawal"], ["request_identity", "approval_route", "maker_checker_policy", "decision_reconciliation"], ["request eligibility approval agreement fulfillment and access are distinct", "marketplace owns routing but not approval authority", "approval dispatch or receipt is not approval"], ["eligibility_unsatisfied", "approver_unresolved", "maker_checker_violated", "decision_completion_unknown"], ["eligibility"], effect="effect_intents_and_receipts"),
    L("marketplace", "fulfillment_handoff", "access_workflow", ["FulfillmentCaseId", "ApprovedRequestRef", "AgreementRef", "FulfillmentIntent", "ProviderEffectReceipt", "SubscriptionBinding"], ["plan_fulfillment_handoff", "reconcile_provider_receipt", "derive_subscription_binding", "plan_subscription_termination"], ["provider_selection", "effect_protocol", "idempotency_scope", "completion_reconciliation"], ["approved request agreement fulfillment provider effect entitlement access transfer delivery and acceptance are distinct", "marketplace never self-provisions an external effect", "provider receipt proves only the named provider effect", "unknown completion reconciles before retry"], ["request_unapproved", "provider_unqualified", "provisioning_unknown", "termination_authority_missing"], ["subscription_request"], effect="effect_intents_and_receipts"),
    L("marketplace", "usage_terms_evidence", "audit_receipts", ["TermsAcknowledgement", "SignerAuthorityEvidenceRef", "UsageObservationRef", "ChargeReference", "MarketplaceReceipt"], ["validate_terms_acknowledgement", "bind_usage_and_charge_references", "plan_marketplace_evidence_append", "derive_marketplace_receipt"], ["acknowledgement_semantics", "signer_authority_evidence", "usage_reference_scope", "charge_reference_scope"], ["terms acknowledgement consent agreement permission and acceptance are distinct", "usage observation charge invoice settlement and payment are distinct", "marketplace receipt proves only included marketplace occurrences"], ["terms_edition_unbound", "signer_authority_invalid", "usage_scope_excessive", "append_completion_unknown"], ["fulfillment_handoff"], effect="effect_intents_and_receipts"),
]


# These contracts were subsequently adjudicated in exact horizontal universes.
# Structural binding closes only the exact API gap;
# implementation qualification and portability remain withheld by the central registry.
EXACT_COMPILER_LIBRARIES = {
    local_library("metadata", key): f"library.metadata_discovery.{key}"
    for key in ("acquisition_port", "assertion_record", "discovery_projection", "search_browse", "federation", "freshness_coverage")
} | {
    local_library("schema", key): f"library.schema_registry.{key}"
    for key in ("subject_identity", "artifact_profile", "version_registry", "compatibility", "reference_closure", "migration_lifecycle")
} | {
    local_library("contract", key): f"library.data_contract.{key}"
    for key in ("contract_identity", "party_purpose_roles", "data_schema_binding", "quality_service_obligations", "compatibility_acceptance", "change_breach_case", "deprecation_exit")
} | {
    local_library("master", key): target
    for key, target in {
        "master_domain_identity": "library.master_data.domain_identity",
        "source_record_authority": "library.master_data.source_authority",
        "survivorship_projection": "library.master_data.survivorship_projection",
        "stewardship_case": "library.master_data.stewardship_case",
        "reference_set": "library.reference_data.reference_set",
        "code_set_lifecycle": "library.reference_data.code_set_lifecycle",
        "crosswalk_mapping": "library.reference_data.crosswalk_mapping",
    }.items()
} | {
    local_library("glossary", key): f"library.business_glossary.{key}"
    for key in ("term_identity", "definition_scope", "lexical_relations", "taxonomy_binding", "stewardship_lifecycle")
} | {
    local_library("ontology", key): target
    for key, target in {
        "ontology_identity_imports": "library.ontology_model.identity_import_closure",
        "axiom_profile": "library.ontology_model.axiom_profile",
        "reasoning_entailment": "library.ontology_model.reasoning_entailment",
        "shape_validation": "library.ontology_model.shape_validation",
        "ontology_mapping": "library.ontology_model.ontology_mapping",
        "knowledge_graph_release": "library.ontology_model.knowledge_graph_release",
    }.items()
} | {
    local_library("policy", key): target
    for key, target in {
        "policy_statement": "library.data_use_policy.policy_edition",
        "purpose_action_resource": "library.data_use_policy.request_context",
        "rule_precedence": "library.data_use_policy.rule_combination",
        "decision_evaluation": "library.data_use_policy.decision_evaluation",
        "obligation_lifecycle": "library.data_use_policy.obligation_protocol",
        "decision_receipt": "library.data_use_policy.decision_evidence",
    }.items()
} | {
    local_library("publication", key): target
    for key, target in {
        "product_identity": "library.data_product_publication.product_edition",
        "port_contract_assembly": "library.data_product_publication.port_assembly",
        "accountability_stewardship": "library.data_product_publication.accountability_binding",
        "readiness_certification": "library.data_product_publication.readiness_evidence",
        "publication_lifecycle": "library.data_product_publication.publication_protocol",
        "change_notification": "library.data_product_publication.consumer_change",
        "recall_decommission_exit": "library.data_product_publication.recall_exit",
    }.items()
} | {
    local_library("marketplace", key): target
    for key, target in {
        "offer_listing": "library.data_marketplace.offer_listing",
        "discovery_experience": "library.data_marketplace.discovery_ranking",
        "eligibility": "library.data_marketplace.eligibility_broker",
        "subscription_request": "library.data_marketplace.subscription_case",
        "fulfillment_handoff": "library.data_marketplace.fulfillment_handoff",
        "usage_terms_evidence": "library.data_marketplace.terms_usage_evidence",
    }.items()
}


PROFILES: dict[str, dict[str, Any]] = {
    "metadata": {
        "question": "For an exact discovery population and as-of cut, what source-attributed metadata can be harvested, projected, searched and federated with freshness, coverage, conflicts and visibility explicit without becoming source truth, certification or access authority?",
        "classification": "core_horizontal_metadata_discovery_product",
        "users": ["data_consumer", "metadata_engineer", "catalog_curator", "data_steward", "source_owner", "platform_operator", "auditor"],
        "harmed": ["data_subject", "source_owner", "consumer", "steward", "operator"],
        "outcomes": ["source_attributed_metadata_assertions", "reconciled_harvest_cursors", "cut_bound_discovery_projection", "freshness_and_coverage_evidence", "conflict_preserving_federation", "typed_search_and_browse_results"],
        "negative": "Does not own described assets, source facts, glossary/ontology/schema truth, certification, access policy, data-product publication or marketplace fulfillment.",
        "states": ["draft", "sources_bound", "harvesting", "projection_building", "active", "stale", "degraded", "conflict_open", "reconciling", "retired"],
        "commands": ["open_discovery_program", "bind_source_occurrences", "start_harvest", "record_extraction", "publish_assertion_edition", "build_discovery_projection", "publish_visibility_cut", "search_or_browse", "measure_freshness_and_coverage", "reconcile_peer_conflicts", "retire_discovery_program"],
        "events": ["discovery_program_opened", "source_occurrences_bound", "harvest_started", "extraction_recorded", "assertion_edition_published", "discovery_projection_built", "visibility_cut_published", "discovery_query_executed", "freshness_and_coverage_measured", "peer_conflicts_reconciled", "discovery_program_retired"],
        "invariants": ["asset metadata assertion projection listing query result and certification are distinct", "every assertion retains source and temporal scope", "absence from a harvest or result is not proof of source absence", "freshness coverage quality and authority are independent", "federation retains peer provenance and conflicts", "rank never grants access or endorsement"],
        "refusals": ["discovery_population_unknown", "source_occurrence_unbound", "harvest_cursor_conflict", "normalization_loss_unaccepted", "projection_cut_unknown", "freshness_unsatisfied", "coverage_unknown", "policy_denied"],
        "inside": ["metadata acquisition and cursor lifecycle", "assertion identity provenance and validity", "discovery projections facets search and browse", "federation precedence and conflict", "freshness coverage and discovery receipts"],
        "outside": ["described asset and source truth", "glossary ontology schema and metric authority", "certification and access grant", "publication and marketplace fulfillment"],
        "terms": ["MetadataAssertion", "AssertionEdition", "HarvestCursor", "ExtractionReceipt", "DiscoveryProjection", "VisibilityCut", "DiscoveryQuery", "CoverageStatement", "FreshnessObservation", "FederatedConflict"],
        "values": ["DiscoveryProgramId", "SourceOccurrenceRef", "AssertionId", "ProjectionCutRef", "PeerId", "HarvestToken", "FreshnessBound", "CoverageScope"],
        "entities": ["DiscoveryProgram", "HarvestOccurrence", "MetadataAssertion", "DiscoveryProjection", "FederationPeer", "DiscoveryReceipt"],
        "roots": ["DiscoveryProgram", "HarvestOccurrence", "MetadataAssertion", "DiscoveryProjection", "FederationPeer"],
        "neighbors": [("context.source_system", "anti_corruption_layer"), ("product.business_glossary", "customer_supplier"), ("product.ontology_knowledge_model", "customer_supplier"), ("product.schema_registry", "customer_supplier"), ("product.data_product_publication", "customer_supplier"), ("product.data_use_policy", "customer_supplier")],
        "time": "Separate source event/commit, extraction, assertion validity/recording, projection build, visibility, query, freshness observation and retirement times; preserve bitemporal assertions and per-peer cuts.",
    },
    "glossary": {
        "question": "Within a bounded business scope and language, which concept and term editions, definitions, lexical relations, taxonomy placements, stewardship decisions and deprecations are authoritative?",
        "classification": "core_horizontal_business_glossary_product",
        "users": ["domain_owner", "terminologist", "business_steward", "analyst", "data_product_author", "translator", "reviewer"],
        "harmed": ["domain_community", "data_consumer", "translated_language_community", "downstream_model_owner"],
        "outcomes": ["stable_concept_and_term_identity", "scope_and_language_bound_definition", "explicit_synonym_homonym_translation_relations", "governed_taxonomy_placement", "stewardship_and_approval_receipts", "safe_deprecation_and_successor"],
        "negative": "Does not own formal ontology axioms, runtime schema, metadata assertions, data-product publication or source business decisions; a glossary definition is not a theorem.",
        "states": ["draft", "scope_bound", "review_pending", "approved", "published", "challenged", "deprecated", "superseded", "retired"],
        "commands": ["register_concept", "register_term", "draft_definition", "bind_scope_and_language", "assert_lexical_relation", "place_in_taxonomy", "submit_review", "approve_or_reject", "publish_term_edition", "deprecate_term", "supersede_definition"],
        "events": ["concept_registered", "term_registered", "definition_drafted", "scope_and_language_bound", "lexical_relation_asserted", "taxonomy_placement_recorded", "term_review_submitted", "term_approved_or_rejected", "term_edition_published", "term_deprecated", "definition_superseded"],
        "invariants": ["concept term designation label definition and scope are distinct", "same label is not same concept", "synonym homonym abbreviation translation and equivalence remain distinct", "taxonomy placement is not ontology entailment", "stewardship is not approval authority", "deprecated terms preserve history and successor"],
        "refusals": ["concept_identity_ambiguous", "scope_missing", "language_invalid", "homonym_unresolved", "relation_strength_ambiguous", "taxonomy_cycle_forbidden", "approval_authority_missing", "successor_ambiguous"],
        "inside": ["concept and term identity", "scope language definition and guidance", "synonym homonym abbreviation and translation relations", "taxonomy and hierarchy binding", "stewardship review approval publication and deprecation"],
        "outside": ["formal axioms and inference", "runtime schemas and source facts", "metadata discovery projection", "business-policy and effect authority"],
        "terms": ["Concept", "Term", "Designation", "DefinitionEdition", "BusinessScope", "LanguageTag", "Synonym", "Homonym", "Translation", "ConceptScheme", "StewardshipCase"],
        "values": ["ConceptId", "TermId", "DefinitionId", "ScopeRef", "LanguageTag", "RelationStrength", "SchemeId", "ApprovalRef"],
        "entities": ["Concept", "Term", "DefinitionEdition", "ConceptScheme", "TermReviewCase", "DeprecationNotice"],
        "roots": ["Concept", "Term", "DefinitionEdition", "ConceptScheme", "TermReviewCase"],
        "neighbors": [("product.ontology_knowledge_model", "open_host_service"), ("product.metadata_discovery", "open_host_service"), ("context.vertical_domain_authority", "customer_supplier"), ("product.data_product_publication", "customer_supplier")],
        "time": "Separate definition validity, recording, review, approval, publication, usage, deprecation and successor-effective times; retain language- and scope-specific bitemporal history.",
    },
    "ontology": {
        "question": "For exact ontology, import, logic, shape and graph editions, what axioms are asserted, which entailments or consistency results follow, which mappings are supported, and which graph constraints conform?",
        "classification": "core_horizontal_ontology_and_knowledge_model_product",
        "users": ["ontologist", "knowledge_engineer", "domain_modeler", "graph_engineer", "application_developer", "assurance_reviewer"],
        "harmed": ["domain_community", "knowledge_consumer", "data_subject", "downstream_reasoning_consumer"],
        "outcomes": ["editioned_ontology_and_import_closure", "profile_valid_axiom_set", "scoped_entailment_and_consistency_result", "cut_bound_shape_validation", "evidence_bound_mapping", "immutable_knowledge_graph_release"],
        "negative": "Does not own real-world truth, glossary approval, runtime schemas, source facts, causal claims or business decisions; consistency and conformance are scoped formal results.",
        "states": ["draft", "imports_resolving", "profile_validated", "inconsistent", "reasoning", "review_pending", "published", "mapping_pending", "graph_release_sealed", "deprecated", "retired"],
        "commands": ["register_ontology", "resolve_import_closure", "add_axiom", "validate_logic_profile", "check_consistency", "request_entailment", "compile_shapes", "validate_graph", "propose_mapping", "approve_mapping", "seal_graph_release", "supersede_ontology"],
        "events": ["ontology_registered", "import_closure_resolved", "axiom_added", "logic_profile_validated", "consistency_checked", "entailment_answered", "shapes_compiled", "graph_validated", "mapping_proposed", "mapping_approved", "graph_release_sealed", "ontology_superseded"],
        "invariants": ["asserted entailed inferred and observed remain distinct", "ontology consistency is not real-world truth", "shape conformance is not ontology consistency", "logic and entailment regimes are explicit", "imports bind exact editions", "same label is not equivalence", "knowledge graph does not own source facts or ontology axioms"],
        "refusals": ["ontology_iri_invalid", "import_unresolved", "profile_unsupported", "ontology_inconsistent", "reasoning_resource_exhausted", "shape_invalid", "validation_incomplete", "mapping_evidence_insufficient", "graph_release_unsealed"],
        "inside": ["ontology IRI edition and import closure", "entity declarations axioms and profiles", "consistency entailment and inference traces", "shape graph validation", "ontology mappings", "knowledge graph assertion partitions and releases"],
        "outside": ["real-world and source truth", "glossary and taxonomy approval", "runtime schema compatibility", "causality and decision authority"],
        "terms": ["Ontology", "OntologyEdition", "ImportClosure", "Axiom", "LogicProfile", "Entailment", "ConsistencyResult", "ShapeGraph", "ValidationReport", "MappingAssertion", "GraphRelease"],
        "values": ["OntologyIri", "VersionIri", "ImportDigest", "AxiomId", "EntailmentRegime", "ShapeEdition", "NamedGraphId", "MappingStrength"],
        "entities": ["Ontology", "OntologyEdition", "ImportClosure", "ReasoningOccurrence", "ShapeValidationOccurrence", "OntologyMapping", "GraphRelease"],
        "roots": ["Ontology", "OntologyEdition", "ReasoningOccurrence", "ShapeValidationOccurrence", "OntologyMapping", "GraphRelease"],
        "neighbors": [("product.business_glossary", "anti_corruption_layer"), ("product.schema_registry", "separate_ways"), ("context.source_knowledge", "anti_corruption_layer"), ("product.lineage_provenance", "published_language"), ("product.data_use_policy", "customer_supplier")],
        "time": "Separate ontology and import validity, axiom recording, reasoning cut, shape/data graph cuts, mapping approval, graph release and deprecation times; reasoning never silently crosses editions.",
    },
    "schema": {
        "question": "For a schema subject and exact format/profile, which immutable versions and reference closures exist, and what directional reader-writer compatibility and migration evidence applies?",
        "classification": "core_horizontal_runtime_schema_registry_product",
        "users": ["schema_author", "event_or_api_owner", "application_developer", "data_engineer", "registry_operator", "compatibility_reviewer"],
        "harmed": ["producer", "consumer", "source_owner", "operator", "downstream_contract_owner"],
        "outcomes": ["stable_schema_subject", "canonical_schema_artifact", "immutable_version_registry", "directional_compatibility_result", "closed_reference_graph", "impact_bound_migration_and_sunset"],
        "negative": "Does not own business meaning, data contracts, source records, semantic metrics or generated-code behavior; syntax compatibility is not business substitutability.",
        "states": ["subject_draft", "active", "version_pending", "registered", "compatibility_failed", "deprecated", "sunset_announced", "retired"],
        "commands": ["register_schema_subject", "parse_and_canonicalize_schema", "register_schema_version", "resolve_reference_closure", "check_compatibility", "publish_compatibility_result", "propose_schema_change", "assess_consumer_impact", "approve_migration", "deprecate_version", "retire_subject"],
        "events": ["schema_subject_registered", "schema_canonicalized", "schema_version_registered", "reference_closure_resolved", "schema_compatibility_checked", "compatibility_result_published", "schema_change_proposed", "consumer_impact_assessed", "schema_migration_approved", "schema_version_deprecated", "schema_subject_retired"],
        "invariants": ["subject schema artifact version reference closure and generated binding are distinct", "registered versions are immutable", "compatibility is directional and profile scoped", "parse validity is not compatibility", "compatible change is not zero impact", "schema is not business meaning or data contract"],
        "refusals": ["subject_collision", "format_unsupported", "schema_invalid", "version_conflict", "reference_unresolved", "compatibility_mode_unbound", "history_incomplete", "impact_unknown", "migration_authority_missing", "retirement_blocked"],
        "inside": ["subject namespace and identity", "schema artifacts formats and canonicalization", "immutable version registry", "directional compatibility", "reference closure", "migration deprecation and sunset lifecycle"],
        "outside": ["business glossary and ontology", "data contract acceptance", "instance data quality", "generated code/runtime behavior", "source and product truth"],
        "terms": ["SchemaSubject", "SchemaArtifact", "SchemaVersion", "SchemaFormat", "ReferenceClosure", "CompatibilityMode", "ReaderWriterPair", "CompatibilityResult", "MigrationPlan", "SunsetNotice"],
        "values": ["SubjectId", "Namespace", "SchemaDigest", "VersionOrdinal", "FormatEdition", "ClosureDigest", "CompatibilityPolicyEdition"],
        "entities": ["SchemaSubject", "SchemaVersion", "ReferenceClosure", "CompatibilityAssessment", "MigrationCase"],
        "roots": ["SchemaSubject", "SchemaVersion", "ReferenceClosure", "CompatibilityAssessment", "MigrationCase"],
        "neighbors": [("product.data_contract_registry", "open_host_service"), ("context.source_interface", "customer_supplier"), ("product.data_quality_operations", "published_language"), ("product.lineage_provenance", "published_language")],
        "time": "Separate subject/version validity, registration, compatibility assessment, consumer observation, migration effective, deprecation and sunset times; retain historical policy editions.",
    },
    "contract": {
        "question": "Between identified producers and consumers for a declared purpose, which immutable data-contract edition, exact bindings, obligations, acceptance decisions, breaches, changes and exit duties govern exchange?",
        "classification": "core_horizontal_data_contract_registry_product",
        "users": ["data_producer", "data_consumer", "contract_owner", "data_product_owner", "quality_owner", "service_owner", "reviewer"],
        "harmed": ["consumer", "producer", "data_subject", "dependent_application", "support_operator"],
        "outcomes": ["immutable_contract_edition", "identified_parties_purpose_and_roles", "exact_data_port_and_schema_bindings", "quality_and_service_obligations", "scoped_acceptance_decision", "breach_and_change_case_evidence", "safe_deprecation_and_exit"],
        "negative": "Does not own schemas, source facts, observed quality/SLO attainment, party identity, enforcement, publication or marketplace fulfillment; declared promises are not observations.",
        "states": ["draft", "negotiating", "review_pending", "accepted", "rejected", "active", "breach_open", "change_pending", "deprecated", "exit_pending", "terminated", "superseded"],
        "commands": ["draft_contract", "bind_parties_purpose_and_roles", "bind_data_ports_and_schemas", "declare_quality_and_service_obligations", "compare_contract_editions", "evaluate_acceptance", "accept_or_reject_contract", "record_breach_finding", "open_change_case", "announce_deprecation", "export_exit_package", "terminate_contract"],
        "events": ["contract_drafted", "parties_purpose_and_roles_bound", "data_ports_and_schemas_bound", "quality_and_service_obligations_declared", "contract_editions_compared", "contract_acceptance_evaluated", "contract_accepted_or_rejected", "breach_finding_recorded", "contract_change_case_opened", "contract_deprecation_announced", "contract_exit_package_exported", "contract_terminated"],
        "invariants": ["contract document edition acceptance observation breach and enforcement are distinct", "producer consumer owner steward and custodian remain distinct", "schema binding is exact and externally owned", "declared quality/SLA is not observed attainment", "compatibility is not acceptance", "deprecation termination and exit remain distinct"],
        "refusals": ["contract_identity_ambiguous", "party_unresolved", "purpose_missing", "schema_unbound", "obligation_measure_ambiguous", "acceptance_authority_missing", "evidence_insufficient", "breach_scope_unknown", "consumer_census_incomplete", "exit_package_incomplete"],
        "inside": ["contract identity and immutable editions", "party purpose and role binding", "data port schema and dataset references", "quality service freshness and support obligations", "compatibility and acceptance", "change breach deprecation termination and exit lifecycle"],
        "outside": ["schema and source truth", "party identity authority", "quality/SLO observations", "enforcement and effects", "product publication and marketplace"],
        "terms": ["DataContract", "ContractEdition", "Producer", "Consumer", "Purpose", "DataPort", "SchemaBinding", "QualityObligation", "ServiceObjective", "AcceptanceDecision", "BreachFinding", "ExitPackage"],
        "values": ["ContractId", "ContractDigest", "PartyRef", "PurposeRef", "PortRef", "SchemaEditionRef", "ObligationId", "AcceptanceRef"],
        "entities": ["DataContract", "ContractEdition", "PartyBinding", "ObligationSet", "AcceptanceCase", "ContractChangeCase", "ExitProcess"],
        "roots": ["DataContract", "ContractEdition", "ObligationSet", "AcceptanceCase", "ContractChangeCase", "ExitProcess"],
        "neighbors": [("product.schema_registry", "customer_supplier"), ("context.party_identity", "anti_corruption_layer"), ("product.data_quality_operations", "open_host_service"), ("product.data_product_publication", "open_host_service"), ("product.lineage_provenance", "published_language")],
        "time": "Separate contract validity, recording, acceptance, obligation window, observation, breach, notice, deprecation, termination and post-termination duty times; preserve party-specific acceptance history.",
    },
    "master": {
        "question": "Within an authority scope and effective time, what stable master identities, authoritative field values, reproducible golden projections, reference-set editions, codes and crosswalks may be published?",
        "classification": "core_horizontal_master_and_reference_data_product",
        "users": ["master_data_owner", "reference_data_manager", "data_steward", "source_owner", "application_consumer", "control_reviewer"],
        "harmed": ["represented_entity", "source_owner", "consumer", "counterparty", "operator"],
        "outcomes": ["authority_scoped_master_identity", "attribute_level_source_authority", "reproducible_survivorship_and_golden_record", "governed_stewardship_case", "editioned_reference_and_code_sets", "loss_declared_crosswalk"],
        "negative": "Does not own probabilistic entity-resolution decisions, source-record mutation, universal real-world truth, business glossary, taxonomy or downstream transaction effects.",
        "states": ["domain_draft", "active", "conflict_open", "steward_review", "effective", "superseded", "deprecated", "held", "retired"],
        "commands": ["register_master_domain", "issue_master_identity", "register_source_record", "assign_attribute_authority", "compile_survivorship", "publish_golden_record", "open_stewardship_case", "record_steward_decision", "publish_reference_set", "maintain_code_set", "publish_crosswalk", "retire_master_identity"],
        "events": ["master_domain_registered", "master_identity_issued", "source_record_registered", "attribute_authority_assigned", "survivorship_compiled", "golden_record_published", "stewardship_case_opened", "steward_decision_recorded", "reference_set_published", "code_set_maintained", "crosswalk_published", "master_identity_retired"],
        "invariants": ["entity identity source record master record golden projection reference value and code remain distinct", "latest is not authoritative by default", "survivorship is reproducible and field-provenanced", "master identity is not match score", "reference data is not master entity", "crosswalk is not equivalence by default"],
        "refusals": ["master_domain_unbound", "identity_collision", "attribute_authority_overlap", "priority_ambiguous", "survivorship_rule_conflict", "steward_authority_missing", "reference_publisher_unresolved", "code_collision", "crosswalk_loss_unaccepted", "retirement_blocked"],
        "inside": ["master-domain and identity authority", "source record and attribute authority", "survivorship and golden projections", "stewardship cases", "reference sets and code sets", "crosswalk mappings"],
        "outside": ["entity-resolution candidate/match decisions", "source mutation", "business glossary and ontology", "transaction/effect execution", "universal truth"],
        "terms": ["MasterDomain", "MasterEntityId", "SourceRecord", "AttributeAuthority", "SourcePriority", "SurvivorshipRule", "GoldenRecord", "StewardshipCase", "ReferenceSet", "CodeSet", "Crosswalk"],
        "values": ["MasterDomainId", "MasterEntityId", "SourceRecordRef", "AuthorityScope", "EffectiveInterval", "GoldenEdition", "ReferenceSetId", "Code", "MappingKind"],
        "entities": ["MasterDomain", "MasterEntity", "SourceRecordBinding", "GoldenRecordEdition", "StewardshipCase", "ReferenceSet", "CodeSet", "Crosswalk"],
        "roots": ["MasterDomain", "MasterEntity", "GoldenRecordEdition", "StewardshipCase", "ReferenceSet", "CodeSet", "Crosswalk"],
        "neighbors": [("product.entity_resolution", "anti_corruption_layer"), ("context.source_system", "customer_supplier"), ("product.business_glossary", "customer_supplier"), ("product.data_quality_operations", "open_host_service"), ("product.lineage_provenance", "published_language")],
        "time": "Separate source event/recording, identity validity, attribute authority, effective master version, survivorship run, stewardship decision, reference value validity, code retirement and crosswalk edition times.",
    },
    "policy": {
        "question": "For an identified subject, purpose, action, resource and context, what editioned data-use policy decision and obligations apply, with precedence, indeterminacy and evidence explicit?",
        "classification": "core_horizontal_data_use_policy_decision_product",
        "users": ["policy_author", "data_owner", "privacy_owner", "application_developer", "decision_service_operator", "auditor", "affected_party"],
        "harmed": ["data_subject", "resource_owner", "requesting_principal", "rights_holder", "operator"],
        "outcomes": ["authority_bound_policy_edition", "externally_owned_request_context_cut", "deterministic_combination_result", "explainable_policy_decision", "receipt_bound_obligation_handoff", "integrity_bound_decision_evidence"],
        "negative": "Does not own legal truth, identity, purpose or classification taxonomies, resource truth, consent validity, entitlement issuance, enforcement, rights fulfillment or source facts; a policy decision is not an effect.",
        "states": ["draft", "review_pending", "published", "active", "decisioning", "conflict", "revoked", "expired", "superseded"],
        "commands": ["validate_policy_edition", "publish_policy_edition", "revoke_policy_edition", "bind_request_context", "compile_policy_set", "evaluate_policy", "explain_decision", "dispatch_obligations", "record_obligation_receipt", "record_decision_evidence", "request_usage_reevaluation", "request_usage_termination"],
        "events": ["policy_edition_validated", "policy_edition_published", "policy_edition_revoked", "request_context_bound", "policy_set_compiled", "policy_evaluated", "policy_decision_explained", "obligations_dispatched", "obligation_receipt_recorded", "decision_evidence_recorded", "usage_reevaluation_requested", "usage_termination_requested"],
        "invariants": ["policy edition deployment decision obligation enforcement and effect are distinct", "purpose resource classification consent and legal basis remain externally owned references", "permit deny not-applicable and indeterminate remain distinct", "combination semantics are editioned", "decision binds policy request attribute evaluator and clock cuts", "obligation dispatch is not fulfillment", "decision evidence is not effect completion"],
        "refusals": ["issuer_unbound", "delegation_invalid", "purpose_unresolved", "resource_unresolved", "attribute_issuer_unbound", "precedence_cycle", "function_unsupported", "decision_indeterminate", "obligation_capability_unsupported", "dispatch_completion_unknown", "evidence_integrity_failed", "effect_authority_requested"],
        "inside": ["policy identity immutable editions issuer authority and lifecycle", "request-context reference and attribute-evidence binding", "rule compilation combination and deterministic decisions", "obligation and reevaluation effect protocols", "decision explanation and evidence"],
        "outside": ["legal interpretation", "identity purpose classification resource consent and legal-basis truth", "entitlement and business approval", "effect enforcement", "rights workflows and source facts"],
        "terms": ["Policy", "PolicyEdition", "Issuer", "Permission", "Prohibition", "Duty", "Advice", "RequestContext", "PolicyCut", "PolicyDecision", "Obligation", "DecisionEvidence"],
        "values": ["PolicyId", "PolicyEditionId", "IssuerRef", "PurposeRef", "ActionRef", "ResourceRef", "AttributeCutId", "DecisionOccurrenceId", "ObligationId"],
        "entities": ["Policy", "PolicyEdition", "CompiledPolicySet", "PolicyDecisionOccurrence", "ObligationAssignment", "DecisionEvidenceRecord"],
        "roots": ["Policy", "PolicyEdition", "CompiledPolicySet", "PolicyDecisionOccurrence", "ObligationAssignment", "DecisionEvidenceRecord"],
        "neighbors": [("context.identity_and_entitlement", "anti_corruption_layer"), ("product.privacy_rights_retention", "customer_supplier"), ("context.effect_runtime", "effect_port"), ("product.data_product_publication", "open_host_service"), ("product.lineage_provenance", "published_language")],
        "time": "Separate policy validity/recording, attribute validity, decision request/effective time, obligation due/fulfillment, enforcement and effect times; retain replayable historical policy cuts.",
    },
    "publication": {
        "question": "For an independently owned data-product edition, when are its ports, contracts, distributions, accountability, readiness evidence and lifecycle sufficient to publish, change, recall, export or decommission it?",
        "classification": "core_horizontal_data_product_publication_product",
        "users": ["data_product_owner", "data_product_developer", "steward", "publisher", "consumer", "support_operator", "assurance_reviewer"],
        "harmed": ["consumer", "data_subject", "source_owner", "support_operator", "dependent_product"],
        "outcomes": ["stable_product_identity_and_edition", "closed_port_contract_distribution_graph", "explicit_accountability_and_support", "scoped_readiness_evidence", "editioned_publication_receipt", "consumer_change_notice", "recall_and_portable_exit"],
        "negative": "Does not own underlying source facts, schema or contract semantics, marketplace listing, access approval, fulfillment, independent assurance or consumer outcome truth.",
        "states": ["draft", "assembling", "readiness_pending", "approved", "published", "change_pending", "deprecated", "recalled", "exit_pending", "decommissioned", "superseded"],
        "commands": ["validate_product_edition", "plan_product_registration", "bind_product_port", "assemble_dependency_graph", "validate_port_closure", "validate_accountability_binding", "plan_accountability_assignment", "assemble_readiness_evidence", "evaluate_readiness", "plan_publication", "reconcile_publication_receipt", "classify_product_change", "plan_change_notice", "reconcile_notice_delivery", "open_recall_case", "plan_recall_propagation", "assemble_exit_package", "evaluate_decommission"],
        "events": ["product_edition_validated", "product_registration_planned", "product_port_bound", "dependency_graph_assembled", "port_closure_validated", "accountability_binding_validated", "accountability_assignment_planned", "readiness_evidence_assembled", "readiness_evaluated", "publication_planned", "publication_receipt_reconciled", "product_change_classified", "change_notice_planned", "notice_delivery_reconciled", "recall_case_opened", "recall_propagation_planned", "exit_package_assembled", "decommission_evaluated"],
        "invariants": ["product series product edition dataset table API model report application offer and deployment are distinct", "identifier name registry occurrence catalog record and package digest are distinct", "product port contract schema dataset distribution service endpoint credential and location are distinct", "a product binds externally owned editions without acquiring their semantic authority", "product owner semantic owner data owner steward custodian publisher operator and support owner are distinct", "readiness evidence verdict approval publication receipt listing access and consumption are distinct", "a product cannot manufacture independent appraisal or certify itself", "notice delivery consumer acknowledgement migration evidence and migration completion are distinct", "deprecation sunset recall access revocation unpublication retirement decommission deletion and exit are distinct", "package integrity does not prove semantic completeness portability or substitutability"],
        "refusals": ["product_identity_collision", "port_or_contract_unbound", "dependency_graph_open", "accountability_missing", "readiness_evidence_stale", "publication_authority_missing", "visibility_invalid", "subscriber_census_incomplete", "recall_scope_ambiguous", "exit_package_incomplete", "live_dependency_remaining"],
        "inside": ["data product identity and immutable editions", "port contract distribution and dependency assembly", "accountability stewardship and support", "readiness criteria and evidence", "publication visibility and receipts", "change notice recall exit and decommission"],
        "outside": ["source schema and contract semantic ownership", "marketplace listing and ranking", "access approval and fulfillment", "independent assurance", "consumer outcomes"],
        "terms": ["DataProduct", "DataProductEdition", "ProductPort", "AccountabilityBinding", "ReadinessVerdict", "PublicationEdition", "ProductChange", "ChangeNotice", "RecallCase", "ExitPackage", "DecommissionDecision"],
        "values": ["DataProductId", "ProductEditionId", "PortId", "ContractEditionRef", "DistributionRef", "OwnerRef", "PublicationRef", "RecallRef"],
        "entities": ["DataProduct", "DataProductEdition", "PortAssembly", "AccountabilityBinding", "ReadinessCase", "Publication", "RecallCase", "ExitProcess"],
        "roots": ["DataProduct", "DataProductEdition", "PortAssembly", "AccountabilityBinding", "ReadinessCase", "Publication", "RecallCase", "ExitProcess"],
        "neighbors": [("product.data_contract_registry", "customer_supplier"), ("product.schema_registry", "customer_supplier"), ("product.data_marketplace", "open_host_service"), ("product.independent_assurance", "customer_supplier"), ("product.data_use_policy", "customer_supplier"), ("product.lineage_provenance", "published_language")],
        "time": "Separate product-edition validity, readiness evidence, publication approval/effective, consumer notice, recall, exit cut and decommission times; preserve historical dependency and visibility editions.",
    },
    "marketplace": {
        "question": "For a published data-product edition and prospective consumer, which marketplace offer is discoverable, eligible and requestable, and what approval and fulfillment handoffs occurred without transferring product or policy authority?",
        "classification": "supporting_horizontal_data_marketplace_product",
        "users": ["data_consumer", "marketplace_curator", "product_owner", "approver", "commercial_owner", "fulfillment_operator", "auditor"],
        "harmed": ["consumer", "data_subject", "product_owner", "rights_holder", "operator", "budget_owner"],
        "outcomes": ["editioned_offer_and_listing", "cut_bound_discovery_and_ranking_evidence", "externally_evidenced_marketplace_eligibility", "authority_preserving_subscription_case", "receipt_bound_fulfillment_handoff", "scoped_terms_usage_and_charge_evidence"],
        "negative": "Does not own data-product truth or publication; identity, credential, purpose, policy, approval or agreement authority; entitlement, provisioning, access, transfer or delivery effects; billing truth; or consumer fitness and acceptance.",
        "states": ["offer_draft", "listing_pending", "listed", "hidden", "eligibility_pending", "request_pending", "external_decision_pending", "approved", "fulfillment_pending", "subscription_active", "termination_pending", "terminated", "expired", "withdrawn"],
        "commands": ["validate_offer_edition", "plan_listing_publication", "normalize_marketplace_query", "rank_candidate_offers", "plan_eligibility_evidence_request", "derive_marketplace_eligibility", "validate_subscription_request", "plan_approval_route", "reconcile_external_decision", "plan_fulfillment_handoff", "reconcile_provider_receipt", "derive_subscription_binding", "validate_terms_acknowledgement", "bind_usage_and_charge_references", "plan_subscription_termination"],
        "events": ["offer_edition_validated", "listing_publication_planned", "marketplace_query_normalized", "candidate_offers_ranked", "eligibility_evidence_request_planned", "marketplace_eligibility_derived", "subscription_request_validated", "approval_route_planned", "external_decision_reconciled", "fulfillment_handoff_planned", "provider_receipt_reconciled", "subscription_binding_derived", "terms_acknowledgement_validated", "usage_and_charge_references_bound", "subscription_termination_planned"],
        "invariants": ["published product offer listing policy agreement subscription and deployment are distinct", "visibility relevance rank recommendation suitability eligibility and endorsement are distinct", "credential verification is not claim truth or eligibility", "eligibility approval agreement entitlement provisioning access transfer delivery consumption and acceptance are distinct", "approval dispatch or receipt is not approval", "provider receipt proves only its exact contracted effect", "terms acknowledgement consent agreement policy permission and acceptance are distinct", "usage observation normalized billing record charge invoice settlement and payment are distinct", "unknown effect completion reconciles before retry"],
        "refusals": ["offer_issuer_unbound", "product_edition_unpublished", "external_edition_unbound", "visibility_invalid", "candidate_coverage_unknown", "ranking_profile_missing", "consumer_unresolved", "purpose_missing", "required_decision_missing", "eligibility_indeterminate", "approver_unresolved", "maker_checker_violated", "external_decision_invalid", "fulfillment_provider_unqualified", "provisioning_unknown", "signer_authority_invalid", "usage_scope_excessive", "termination_authority_missing"],
        "inside": ["offer and listing editions", "cut-bound discovery ranking and coverage evidence", "external eligibility-evidence brokerage", "subscription request case and approval routing", "fulfillment and termination handoffs", "terms acknowledgement usage and charge references"],
        "outside": ["data-product publication and truth", "identity credential purpose policy approval and agreement authority", "entitlement provisioning access transfer and delivery effects", "usage metering invoice settlement and accounting truth", "consumer fitness and acceptance"],
        "terms": ["MarketplaceOffer", "OfferEdition", "ListingEdition", "DiscoveryResult", "MarketplaceEligibilityStatus", "SubscriptionCase", "ExternalApprovalDecision", "FulfillmentIntent", "ProviderEffectReceipt", "SubscriptionBinding", "MarketplaceReceipt"],
        "values": ["MarketplaceOfferId", "OfferEditionId", "ListingEditionId", "PublishedProductEditionRef", "ConsumerRef", "PurposeRef", "SubscriptionRequestId", "FulfillmentCaseId", "SubscriptionBindingId"],
        "entities": ["MarketplaceOffer", "OfferEdition", "ListingEdition", "EligibilityCase", "SubscriptionCase", "FulfillmentCase", "SubscriptionBinding", "MarketplaceEvidenceRecord"],
        "roots": ["MarketplaceOffer", "OfferEdition", "ListingEdition", "EligibilityCase", "SubscriptionCase", "FulfillmentCase", "SubscriptionBinding", "MarketplaceEvidenceRecord"],
        "neighbors": [("product.data_product_publication", "customer_supplier"), ("product.data_use_policy", "customer_supplier"), ("context.identity_entitlement", "anti_corruption_layer"), ("context.fulfillment_runtime", "effect_port"), ("context.commercial_billing", "published_language")],
        "time": "Separate product publication, listing validity, search, eligibility-policy cut, request, approval, provisioning, access, usage, billing and termination times; uncertain fulfillment completion reconciles before retry.",
    },
}


def relevant_sources(upstream: str) -> list[str]:
    refs: set[str] = set()
    if upstream in GMO_LIBRARIES:
        context_refs = GMO_LIBRARIES[upstream]["owns_contexts"]
    else:
        # Retiring a coarse library removes its compiler identity, not the
        # evidence that motivated the narrower product seams.  Recover that
        # evidence through the explicit replacement record's covered contexts.
        context_refs = GMO_REPLACEMENTS[upstream]["covered_context_refs"]
    for context_ref in context_refs:
        refs.update(GMO_CONTEXTS[context_ref]["evidence_refs"])
    return [f"gmo.source.{ref.lower()}" for ref in sorted(refs)]


def converted_sources() -> list[dict[str, Any]]:
    return [{
        "source_id": f"gmo.source.{source_id.lower()}",
        "source_class": "primary_research" if row["source_kind"] == "research_article" else "official_specification_or_documentation",
        "title": row["title"], "publisher": row["issuer"], "uri": row["url"],
        "retrieved_at": row["retrieved_at"],
        "claim": "Supports " + ", ".join(row["supports"]) + ".",
        "scope_limit": "; ".join(row["does_not_establish"]),
    } for source_id, row in sorted(GMO_SOURCES.items())]


def product_libraries(product_key: str) -> list[dict[str, Any]]:
    return [row for row in LIBRARY_SPECS if row["product"] == product_key]


def truth(product_key: str, profile: dict[str, Any]) -> dict[str, Any]:
    specs = product_libraries(product_key)
    jobs = [f"Govern {row['key'].replace('_', ' ')} with exact identity, decisions, evidence, refusals and lifecycle." for row in specs]
    return {
        "sovereign_question": profile["question"], "users": profile["users"], "harmed_parties": profile["harmed"],
        "jobs": jobs, "outcomes": profile["outcomes"], "negative_mission": profile["negative"],
        "lifecycle_states": profile["states"], "commands": profile["commands"], "events": profile["events"],
        "invariants": profile["invariants"], "refusals": profile["refusals"], "automation_modality": AUTOMATION,
    }


def dossier(product_key: str, profile: dict[str, Any]) -> dict[str, Any]:
    product = PRODUCTS[product_key]
    t = truth(product_key, profile)
    roots = profile["roots"]
    services = [pascal(row["key"]) + "Service" for row in product_libraries(product_key)]
    ddd = {
        "domain_vision_statement": "Own " + profile["question"].rstrip("?").removeprefix("For ").removeprefix("Within "),
        "subdomain_classification": profile["classification"],
        "bounded_context_boundary": {"inside": profile["inside"], "outside": profile["outside"]},
        "ubiquitous_language_policy": {"canonical_terms": profile["terms"], "law": "One scoped editioned meaning per term; homonyms, aliases, mappings, compatibility and authority relations are explicit and never inferred from labels."},
        "context_map": [{"neighbor_ref": ref, "relationship": rel, "translation": "Translate exact editions and preserve the neighbor's identity, truth, policy, evidence and effect authority."} for ref, rel in profile["neighbors"]],
        "anti_corruption_layers": [f"acl.{product_key}.{ref.split('.')[-1]}" for ref, _ in profile["neighbors"]],
        "published_language": profile["terms"] + ["TypedRefusal", "EvidenceRef", "EditionRef", "AuthorityRef"],
        "value_objects": profile["values"], "entities": profile["entities"],
        "aggregates": [{"root": root, "consistency": f"{root} changes only through version-checked named commands; evidence, authority and refusals remain explicit."} for root in roots],
        "aggregate_roots": roots, "aggregate_invariants": profile["invariants"],
        "commands": profile["commands"], "domain_events": profile["events"],
        "refusal_failure_catalog": profile["refusals"], "domain_services": services,
        "application_services": [pascal(command) + "UseCase" for command in profile["commands"]],
        "repositories": [root + "Repository" for root in roots],
        "factories": [root + "Factory" for root in roots],
        "specifications": [pascal(row["key"]) + "Specification" for row in product_libraries(product_key)] + ["EvidenceValiditySpecification", "AuthorityScopeSpecification", "ExitCompletenessSpecification"],
        "state_machine": {"states": profile["states"], "transition_law": "Only named commands with expected version, exact editions, satisfied invariants, current evidence and scoped authority emit the corresponding past-tense event; unknown and revoked fail closed."},
        "policies_and_reactions": ["on upstream edition change open an impact case", "on evidence expiry refuse stronger claims", "on authority revocation propagate invalidation", "on unknown provider completion reconcile before retry", "on optional automation failure use deterministic fallback or typed refusal"],
        "sagas_and_process_managers": [pascal(product_key) + "LifecycleProcess", "ChangeImpactProcess", "RevocationPropagationProcess", "ProviderQualificationProcess", "ExitAndPortabilityProcess"],
        "read_models_and_projections": [root + "StatusProjection" for root in roots] + ["OpenRefusalsProjection", "EvidenceAuthorityProjection", "DependencyImpactProjection"],
        "integration_event_policy": "Only immutable editioned published-language facts cross the boundary. Drafts, provider callbacks, inferred proposals and tentative findings remain internal; neighboring truth, authority, effect and outcome claims require owning-context receipts.",
        "concurrency_and_idempotency": "Use immutable occurrence IDs, aggregate versions, command idempotency keys and append-only decisions/receipts. Retries preserve attempts; concurrent semantic edits conflict rather than silently merge; uncertain effects reconcile before repetition.",
        "time_model": profile["time"],
        "event_storming_swimlanes": {"actors": profile["users"], "commands": profile["commands"], "events": profile["events"], "hotspots": ["identity versus label", "validity versus recording time", "proposal versus accepted edition", "evidence versus authority", "decision versus effect", "revocation propagation"]},
        "nonfunctional_laws": profile["invariants"] + ["finite query inference validation and workflow budgets are declared", "provider identity never changes semantics", "one implementation never proves portability", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "dossier_id": f"ddd.governance.{product_key}", "product_ref": product,
        "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": t["sovereign_question"], "users": t["users"], "harmed_parties": t["harmed_parties"], "jobs": t["jobs"], "measurable_outcomes": t["outcomes"], "negative_mission": t["negative_mission"]},
        "strategic_and_tactical_ddd": ddd,
    }


def library_row(spec: dict[str, Any]) -> dict[str, Any]:
    product_key, key = spec["product"], spec["key"]
    evidence_refs = relevant_sources(spec["upstream"])
    return {
        "library_id": local_library(product_key, key), "class": "semantic_effect_port" if spec["effect"] != "pure_no_io" else "semantic_pure",
        "owner_ref": local_semantic(product_key, key), "provides": [local_capability(product_key, key)],
        "types": spec["types"], "operations": spec["operations"], "decisions": spec["decisions"],
        "invariants": spec["laws"] + ["provider identity does not change meaning", "model or agent output is never semantic or effect authority"],
        "refusals": spec["refusals"] + ["provider_unqualified", "unsupported_capability"],
        "dependencies": [local_library(product_key, dep) for dep in spec["deps"]],
        "effect_boundary": spec["effect"], "evidence_refs": evidence_refs,
        "product_refs": [PRODUCTS[product_key]],
    }


def enrich_governance_products(source: dict[str, Any]) -> dict[str, Any]:
    product_refs = set(PRODUCTS.values())
    old_libraries = {row["library_id"] for row in source["libraries"] if not row.get("product_refs")}
    old_capabilities = {ref for row in source["libraries"] if row["library_id"] in old_libraries for ref in row["provides"]}
    new_source_ids = {row["source_id"] for row in converted_sources()}
    new_library_ids = {local_library(row["product"], row["key"]) for row in LIBRARY_SPECS}
    new_capability_ids = {local_capability(row["product"], row["key"]) for row in LIBRARY_SPECS}
    new_semantic_ids = {local_semantic(row["product"], row["key"]) for row in LIBRARY_SPECS}
    new_map_ids = {f"binding.governance_{row['product']}.{row['key']}" for row in LIBRARY_SPECS}
    new_gap_ids = {f"gap.governance_{row['product']}.{row['key']}.exact_contract" for row in LIBRARY_SPECS}

    source["sources"] = [row for row in source["sources"] if row["source_id"] not in new_source_ids] + converted_sources()
    source["libraries"] = [row for row in source["libraries"] if row["library_id"] not in old_libraries | new_library_ids]
    source["requirements"] = [row for row in source["requirements"] if row["consumer_ref"] not in product_refs and row["capability_ref"] not in new_capability_ids]
    source["relations"] = [row for row in source["relations"] if row["from_ref"] not in product_refs or row["to_ref"] not in old_capabilities | new_capability_ids]
    source["binding_maps"] = [row for row in source["binding_maps"] if row["binding_map_id"] not in new_map_ids]
    source["binding_gaps"] = [row for row in source["binding_gaps"] if row["gap_id"] not in new_gap_ids]
    source["ddd_dossiers"] = [row for row in source["ddd_dossiers"] if row["product_ref"] not in product_refs]
    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in new_capability_ids | new_semantic_ids]
    governance_laws = {
        "metadata assertion != asset != source fact != discovery projection != listing != certification",
        "concept != term != label != definition != taxonomy placement != ontology axiom",
        "ontology consistency != shape conformance != real-world truth",
        "schema validity != compatibility != contract acceptance != business substitutability",
        "contract declaration != observed attainment != breach decision != remedy effect",
        "source record != master identity != golden projection != reference value != code",
        "policy statement != decision != obligation fulfillment != enforcement != effect",
        "data-product readiness != publication != marketplace listing != eligibility != access != consumption",
    }
    source["non_collapse_laws"] = [law for law in source["non_collapse_laws"] if law not in governance_laws]

    for product_key, profile in PROFILES.items():
        next(row for row in source["artifacts"] if row["artifact_id"] == PRODUCTS[product_key]).update(truth(product_key, profile))
        source["ddd_dossiers"].append(dossier(product_key, profile))

    for spec in LIBRARY_SPECS:
        product_key, key = spec["product"], spec["key"]
        product = PRODUCTS[product_key]
        evidence_refs = relevant_sources(spec["upstream"])
        semantic = local_semantic(product_key, key)
        capability = local_capability(product_key, key)
        library = local_library(product_key, key)
        gap = f"gap.governance_{product_key}.{key}.exact_contract"
        source["artifacts"].extend([
            {"artifact_id": semantic, "kind": "semantic_contract", "name": key.replace("_", " ").title() + " semantics", "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False, "operated": False, "definition": "Owns the exact product-scoped identity, decisions, lifecycle, laws and refusals for " + key.replace("_", " ") + ".", "evidence_refs": evidence_refs},
            {"artifact_id": capability, "kind": "capability", "name": key.replace("_", " ").title(), "status": "specified_candidate", "semantic_owner_ref": semantic, "adoption_unit": False, "operated": False, "definition": "Expose provider-neutral " + key.replace("_", " ") + " behavior with all semantic, temporal, authority, evidence and failure decisions explicit.", "evidence_refs": evidence_refs},
        ])
        source["libraries"].append(library_row(spec))
        source["requirements"].append({
            "requirement_id": f"requirement.governance_{product_key}.{key}", "consumer_ref": product,
            "capability_ref": capability, "binding_phase": "runtime" if spec["effect"] != "pure_no_io" else "compile_time",
            "minimum_qualified_offers": 1, "status": "unbound", "refusal": f"no_qualified_{key}_implementation",
        })
        source["relations"].append({
            "relation_id": f"relation.governance_{product_key}.offers_{key}", "from_ref": product,
            "predicate": "offers", "to_ref": capability, "binding_phase": "compile_time",
            "authority_effect": "product owns the exact semantic contract; providers and candidate upstream projections gain no semantic authority",
        })
        exact_ref = EXACT_COMPILER_LIBRARIES.get(library)
        if exact_ref:
            stem = exact_ref.removeprefix("library.")
            source["binding_maps"].append({
                "binding_map_id": f"binding.governance_{product_key}.{key}", "product_refs": [product],
                "abstract_library_ref": library, "concrete_library_refs": [exact_ref],
                "required_requirement_refs": [f"requirement.{stem}.implementation"],
                "portable_offer_refs": [f"offer.{stem}.portable"],
                "candidate_projection_refs": [] if spec["upstream"] in RETIRED_GMO_UPSTREAMS else [f"library.gmo.{spec['upstream'].removeprefix('gmo.library.') }"],
                "compiler_disposition": "structurally_projected_unqualified", "gap_ref": None, "portable_offer": False,
            })
        else:
            source["binding_maps"].append({
                "binding_map_id": f"binding.governance_{product_key}.{key}", "product_refs": [product],
                "abstract_library_ref": library, "concrete_library_refs": [], "required_requirement_refs": [],
                "portable_offer_refs": [], "candidate_projection_refs": [] if spec["upstream"] in RETIRED_GMO_UPSTREAMS else [f"library.gmo.{spec['upstream'].removeprefix('gmo.library.') }"],
                "compiler_disposition": "blocked_typed_gap", "gap_ref": gap, "portable_offer": False,
            })
            source["binding_gaps"].append({
                "gap_id": gap, "product_refs": [product], "abstract_library_ref": library,
                "abstract_library_refs": [library], "candidate_projection_refs": [] if spec["upstream"] in RETIRED_GMO_UPSTREAMS else [f"library.gmo.{spec['upstream'].removeprefix('gmo.library.') }"],
                "reason": "The researched GMO boundary supports this split, but its compiler projection explicitly lacks an adjudicated exact API/effect contract and independently qualified implementations; broad upstream ownership may also require a narrower owner split.",
                "resolution": "Publish the exact versioned public types, operations, decisions, laws, refusal precedence, effect intents/receipts, finite bounds, conformance fixtures and at least two independent qualified implementations for this product-scoped seam.",
            })

    negatives = [
        ("metadata.asset_assertion", "Metadata assertion is the described asset or source fact", "preserve source attribution and authority"),
        ("metadata.empty_absence", "Empty discovery result proves source absence", "report coverage and freshness"),
        ("glossary.label_identity", "Same label proves same concept", "require scoped concept identity"),
        ("glossary.taxonomy_ontology", "Taxonomy placement is ontology entailment", "retain formal mapping boundary"),
        ("ontology.consistency_truth", "Ontology consistency proves real-world truth", "publish scoped formal result only"),
        ("ontology.shape_truth", "SHACL conformance proves ontology consistency or truth", "retain validation scope"),
        ("schema.parse_compatible", "Schema parses therefore it is compatible", "run exact directional policy"),
        ("schema.compatible_substitutable", "Wire compatibility proves business substitutability", "require contract acceptance"),
        ("contract.declared_observed", "Declared contract obligation is observed attainment", "bind observation evidence separately"),
        ("contract.compatible_accepted", "Compatible contract edition is accepted", "require party authority and evidence"),
        ("master.latest_authoritative", "Latest source value is authoritative", "apply scoped field authority"),
        ("master.golden_truth", "Golden record is universal truth", "retain projection provenance and scope"),
        ("master.crosswalk_equivalence", "Crosswalk mapping proves equivalence", "preserve mapping kind and loss"),
        ("policy.decision_effect", "Policy decision is enforcement or effect", "require external effect receipt"),
        ("policy.permit_duty", "Permit with duty proves duty fulfilled", "track obligation lifecycle"),
        ("publication.ready_published", "Readiness verdict is publication", "require publication authority and receipt"),
        ("publication.listing_consumption", "Publication is listing or consumption", "retain marketplace and consumer occurrences"),
        ("marketplace.visible_eligible", "Visible listing proves eligibility", "evaluate exact policy cut"),
        ("marketplace.approved_provisioned", "Approved request proves access provisioned", "require provider receipt and reconciliation"),
        ("governance.agent_authority", "A model or agent may define, approve, publish, match, decide or fulfill governance truth", "retain proposal taint and deterministic authority"),
    ]
    existing = {row["test_id"] for row in source["negative_tests"]}
    source["negative_tests"].extend({"test_id": f"negative.{key}", "input_claim": claim, "expected_refusal": expected} for key, claim, expected in negatives if f"negative.{key}" not in existing)
    source["non_collapse_laws"].extend(sorted(governance_laws))
    for row in source["crosswalks"]:
        if row["legacy_ref"] == "legacy.ai_governance_feature":
            row["canonical_refs"] = ["library.governance_metadata.acquisition_port"]
            row["disposition"] = "replace_with_deterministic_contract_optional_assistance_external"
    return source
