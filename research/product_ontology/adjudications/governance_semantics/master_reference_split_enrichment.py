#!/usr/bin/env python3
"""Split the overloaded master/reference product into two governed product boundaries."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from governance_product_enrichment import AUTOMATION, DDD_FIELDS, PRODUCT_FIELDS


OLD_PRODUCT = "product.master_reference_data"
OLD_OWNER = "semantic.master_reference_data"
MASTER_PRODUCT = "product.master_data_governance"
REFERENCE_PRODUCT = "product.reference_data_governance"
MASTER_OWNER = "semantic.master_data_governance"
REFERENCE_OWNER = "semantic.reference_data_governance"

MASTER_KEYS = {
    "master_domain_identity", "source_record_authority", "survivorship_projection",
    "stewardship_case",
}
REFERENCE_KEYS = {"reference_set", "code_set_lifecycle", "crosswalk_mapping"}
ALL_KEYS = MASTER_KEYS | REFERENCE_KEYS


def _axis_test(evidence_refs: list[str]) -> dict[str, dict[str, Any]]:
    scores = {
        "user": 2, "job": 2, "adoption": 2, "semantics": 2, "authority": 2,
        "lifecycle": 2, "operation": 2, "economics": 1, "interface": 2,
        "market_evidence": 1,
    }
    return {axis: {"score": score, "evidence_refs": evidence_refs} for axis, score in scores.items()}


MASTER_TRUTH = {
    "sovereign_question": "Within one governed master domain, which stable entity identities, source-attribute authorities, survivorship decisions and master projections may be issued, changed, challenged, published or retired?",
    "users": ["master_data_owner", "domain_steward", "source_owner", "entity_resolution_owner", "application_consumer", "control_reviewer"],
    "harmed_parties": ["represented_entity", "source_owner", "consumer", "counterparty", "decision_subject", "operator"],
    "jobs": ["govern master-domain and entity identity", "bind source records and attribute-level authority", "compile reproducible survivorship projections", "adjudicate conflicts and publish or retire master editions"],
    "outcomes": ["authority_scoped_master_identity", "attribute_level_source_authority", "field_provenanced_master_projection", "challengeable_stewardship_decision", "impact_bound_master_change"],
    "negative_mission": "Does not own source records, probabilistic entity-resolution decisions, reference/code systems, universal truth, business terminology, downstream transactions or correction effects.",
    "lifecycle_states": ["domain_draft", "active", "identity_pending", "conflict_open", "steward_review", "effective", "superseded", "held", "retired"],
    "commands": ["register_master_domain", "issue_master_identity", "bind_source_record", "assign_attribute_authority", "compile_survivorship", "publish_master_projection", "open_stewardship_case", "record_steward_decision", "supersede_master_projection", "retire_master_identity"],
    "events": ["master_domain_registered", "master_identity_issued", "source_record_bound", "attribute_authority_assigned", "survivorship_compiled", "master_projection_published", "stewardship_case_opened", "steward_decision_recorded", "master_projection_superseded", "master_identity_retired"],
    "invariants": ["source occurrence resolution assertion master identity and master projection are distinct", "identity issuance requires scoped external authority", "latest is not authoritative by default", "survivorship is editioned reproducible and field-provenanced", "unselected candidates and residual conflicts remain visible", "steward decision is not source mutation"],
    "refusals": ["master_domain_unbound", "identity_authority_missing", "identity_collision", "source_occurrence_unresolved", "attribute_authority_overlap", "survivorship_rule_conflict", "tie_unresolved", "steward_authority_missing", "impact_scope_unknown", "retirement_blocked"],
    "automation_modality": AUTOMATION,
}

REFERENCE_TRUTH = {
    "sovereign_question": "Under one maintenance authority, which reference schemes, sets, codes, designations, validity editions and directional mappings may be published, replaced, recalled or retired?",
    "users": ["reference_data_manager", "code_system_maintainer", "terminology_steward", "application_owner", "integration_owner", "control_reviewer"],
    "harmed_parties": ["classified_subject", "data_producer", "data_consumer", "integration_consumer", "reporting_subject", "operator"],
    "jobs": ["govern reference-scheme and set identity", "publish effective-dated code and designation editions", "govern deprecation replacement and reuse", "publish directional crosswalks with cardinality ambiguity and loss"],
    "outcomes": ["authority_bound_reference_set", "immutable_code_system_edition", "historically_resolvable_deprecation", "directional_loss_declared_crosswalk", "consumer_pinned_reference_release"],
    "negative_mission": "Does not own master entities, source records, entity resolution, business glossary definitions, ontology entailment, universal equivalence, transaction facts or consumer migration effects.",
    "lifecycle_states": ["scheme_draft", "review", "published", "effective", "change_pending", "deprecated", "replacement_pending", "recalled", "retired"],
    "commands": ["register_reference_scheme", "publish_reference_set", "add_code", "publish_designation", "deprecate_code", "declare_replacement", "publish_crosswalk", "supersede_crosswalk", "recall_reference_release", "retire_reference_scheme"],
    "events": ["reference_scheme_registered", "reference_set_published", "code_added", "designation_published", "code_deprecated", "replacement_declared", "crosswalk_published", "crosswalk_superseded", "reference_release_recalled", "reference_scheme_retired"],
    "invariants": ["concept code notation designation display and definition are distinct", "reference value classifies other data and is not a master entity", "set identity edition member and distribution are distinct", "retirement preserves historical resolution", "reuse is forbidden unless exact policy permits", "crosswalk direction cardinality context and information loss are explicit", "forward mapping never implies reverse mapping or equivalence"],
    "refusals": ["maintenance_authority_unbound", "scheme_identity_collision", "code_collision", "designation_language_invalid", "validity_overlap", "reuse_forbidden", "replacement_ambiguous", "mapping_edition_unbound", "mapping_cardinality_ambiguous", "mapping_loss_unaccepted"],
    "automation_modality": AUTOMATION,
}


def _product(product_ref: str, owner_ref: str, name: str, definition: str, evidence_refs: list[str], truth: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": product_ref, "kind": "product", "name": name,
        "status": "strong_product_candidate", "semantic_owner_ref": owner_ref,
        "adoption_unit": True, "operated": True, "definition": definition,
        "evidence_refs": evidence_refs, **deepcopy(truth),
    }


def _semantic(owner_ref: str, name: str, definition: str, evidence_refs: list[str]) -> dict[str, Any]:
    return {
        "artifact_id": owner_ref, "kind": "semantic_contract", "name": name,
        "status": "candidate", "semantic_owner_ref": None, "adoption_unit": False,
        "operated": False, "definition": definition, "evidence_refs": evidence_refs,
    }


def _dossier(product_ref: str, owner_ref: str, truth: dict[str, Any], kind: str) -> dict[str, Any]:
    master = kind == "master_data"
    roots = (["MasterDomain", "MasterEntity", "MasterProjectionEdition", "StewardshipCase"] if master
             else ["ReferenceScheme", "ReferenceSetEdition", "CodeLifecycle", "CrosswalkEdition"])
    values = (["MasterDomainId", "MasterEntityId", "SourceOccurrenceRef", "AuthorityScope", "EffectiveInterval", "SurvivorshipPolicyEdition", "MasterProjectionId", "EvidenceRef"] if master
              else ["ReferenceSchemeId", "ReferenceSetId", "ReferenceEditionId", "ConceptId", "Code", "LanguageTag", "MappingKind", "ValidityInterval", "EvidenceRef"])
    inside = (["master domain and entity identity authority", "source occurrence and attribute authority", "survivorship and field-provenanced master projections", "stewardship conflict and retirement lifecycle"] if master
              else ["reference schemes sets and code-system editions", "codes designations validity deprecation replacement and reuse", "directional crosswalks cardinality ambiguity and loss", "publication recall subscription and retirement lifecycle"])
    outside = (["source mutation", "entity-resolution scoring and clustering", "reference and code-system governance", "business glossary and ontology", "transaction effects and universal truth"] if master
               else ["master entity identity and survivorship", "entity resolution", "business-definition and ontology authority", "transaction facts", "consumer migration effects and universal equivalence"])
    neighbors = ([REFERENCE_PRODUCT, "product.entity_resolution", "product.business_glossary", "product.data_quality_operations", "product.lineage_provenance"] if master
                 else [MASTER_PRODUCT, "product.business_glossary", "product.ontology_knowledge_model", "product.schema_registry", "product.lineage_provenance"])
    services = (["MasterIdentityService", "SourceAuthorityService", "SurvivorshipService", "StewardshipService"] if master
                else ["ReferenceSchemeService", "CodeLifecycleService", "CrosswalkService", "ReferencePublicationService"])
    commands = truth["commands"]
    events = truth["events"]
    ddd = {
        "domain_vision_statement": truth["sovereign_question"],
        "subdomain_classification": f"core_horizontal_{kind}_governance_product",
        "bounded_context_boundary": {"inside": inside, "outside": outside},
        "ubiquitous_language_policy": {"canonical_terms": values + roots, "law": "One scoped editioned meaning per term; homonyms mappings aliases authority and compatibility are explicit and never inferred from labels."},
        "context_map": [{"neighbor_ref": ref, "relationship": "anti_corruption_layer" if ref in {REFERENCE_PRODUCT, MASTER_PRODUCT, "product.entity_resolution"} else "customer_supplier", "translation": "Bind exact editions and preserve the neighbor's semantic truth policy evidence and effect authority."} for ref in neighbors],
        "anti_corruption_layers": [f"acl.{kind}.{ref.rsplit('.', 1)[-1]}" for ref in neighbors],
        "published_language": values + roots + ["TypedRefusal", "AuthorityRef", "EvidenceReceipt"],
        "value_objects": values,
        "entities": roots + (["SourceRecordBinding", "FieldDecision"] if master else ["ReferenceCode", "Designation", "MappingAssertion"]),
        "aggregates": [{"root": root, "consistency": "Changes only through version-checked named commands with exact editions scoped authority retained evidence and typed refusals."} for root in roots],
        "aggregate_roots": roots,
        "aggregate_invariants": truth["invariants"],
        "commands": commands,
        "domain_events": events,
        "refusal_failure_catalog": truth["refusals"],
        "domain_services": services,
        "application_services": ["".join(part.title() for part in command.split("_")) + "UseCase" for command in commands],
        "repositories": [root + "Repository" for root in roots],
        "factories": [root + "Factory" for root in roots],
        "specifications": [service.removesuffix("Service") + "Specification" for service in services] + ["AuthorityScopeSpecification", "EvidenceValiditySpecification", "ExitCompletenessSpecification"],
        "state_machine": {"states": truth["lifecycle_states"], "transition_law": "Only named commands with expected edition current evidence and scoped authority emit past-tense events; unknown revoked and conflicting states fail closed."},
        "policies_and_reactions": ["on source or authority change open exact impact review", "on evidence expiry refuse stronger publication claims", "on revocation propagate invalidation", "on unknown provider completion reconcile before retry", "on optional automation failure use deterministic fallback or typed refusal"],
        "sagas_and_process_managers": [root + "LifecycleProcess" for root in roots] + ["RevocationPropagationProcess", "ExitAndPortabilityProcess"],
        "read_models_and_projections": [root + "StatusProjection" for root in roots] + ["OpenRefusalsProjection", "EvidenceAuthorityProjection", "DependencyImpactProjection"],
        "integration_event_policy": "Only immutable editioned published-language facts cross the boundary; proposals provider callbacks and unaccepted findings remain internal, and effects require owning-authority receipts.",
        "concurrency_and_idempotency": "Use immutable occurrence identities aggregate editions command idempotency keys and append-only decisions attempts and receipts; conflicts refuse and unknown effects reconcile before retry.",
        "time_model": ("Separate source occurrence, recording, identity validity, attribute authority, survivorship cut, stewardship decision, publication, supersession and retirement times." if master else "Separate scheme, set and code validity, recording, publication, consumer pinning, deprecation, replacement, mapping, recall and retirement times."),
        "event_storming_swimlanes": {"actors": truth["users"], "commands": commands, "events": events, "hotspots": ["identity versus label", "validity versus recording time", "proposal versus accepted edition", "evidence versus authority", "decision versus effect", "revocation propagation"]},
        "nonfunctional_laws": truth["invariants"] + ["finite query validation publication and workflow budgets are declared", "provider identity never changes semantics", "one implementation never proves portability", AUTOMATION["removal_law"]],
    }
    assert set(ddd) == DDD_FIELDS
    return {
        "record_kind": "product_ddd_dossier",
        "dossier_id": f"ddd.governance.{kind}", "product_ref": product_ref,
        "status": "candidate_not_ratified",
        "product_truth": {"sovereign_question": truth["sovereign_question"], "users": truth["users"], "harmed_parties": truth["harmed_parties"], "jobs": truth["jobs"], "measurable_outcomes": truth["outcomes"], "negative_mission": truth["negative_mission"]},
        "strategic_and_tactical_ddd": ddd,
    }


def _key_from_id(value: str) -> str | None:
    for key in ALL_KEYS:
        if value.endswith("." + key):
            return key
    return None


def _product_for_key(key: str) -> str:
    return MASTER_PRODUCT if key in MASTER_KEYS else REFERENCE_PRODUCT


def _prefix_for_key(key: str) -> str:
    return "governance_master_data" if key in MASTER_KEYS else "governance_reference_data"


def _rewrite_exact_id(value: str) -> str:
    key = _key_from_id(value)
    if key is None:
        return value
    for old in ("governance_master",):
        value = value.replace(old, _prefix_for_key(key))
    return value


def _rewrite_for_key(value: str, key: str) -> str:
    return value.replace("governance_master", _prefix_for_key(key))


def _restore_combined_namespace(value: str) -> str:
    return value.replace("governance_master_data", "governance_master").replace(
        "governance_reference_data", "governance_master"
    )


def prepare_master_reference_regeneration(source: dict[str, Any]) -> dict[str, Any]:
    """Restore the private pre-split shape so the upstream generator remains idempotent.

    The returned combined boundary is only an intermediate generator input.  The public source
    emitted by the complete pipeline is always split again by ``enrich_master_reference_split``.
    """
    source["artifacts"] = [
        row for row in source["artifacts"]
        if row["artifact_id"] not in {MASTER_PRODUCT, REFERENCE_PRODUCT, MASTER_OWNER, REFERENCE_OWNER}
    ]
    for artifact in source["artifacts"]:
        artifact["artifact_id"] = _restore_combined_namespace(artifact["artifact_id"])
        if artifact.get("semantic_owner_ref") in {MASTER_OWNER, REFERENCE_OWNER}:
            artifact["semantic_owner_ref"] = OLD_OWNER
        elif artifact.get("semantic_owner_ref"):
            artifact["semantic_owner_ref"] = _restore_combined_namespace(artifact["semantic_owner_ref"])
    source["artifacts"].extend([
        {
            "artifact_id": OLD_PRODUCT, "kind": "product", "name": "Master and Reference Data",
            "status": "strong_product_candidate", "semantic_owner_ref": OLD_OWNER,
            "adoption_unit": True, "operated": True,
            "definition": "Govern mastered identities, survivorship projections, reference sets, code lifecycles and mappings.",
            "evidence_refs": ["evidence.iso8000", "evidence.gleif.level2", "evidence.gs1.gdsn"],
        },
        {
            "artifact_id": OLD_OWNER, "kind": "semantic_contract",
            "name": "Master and reference data semantics", "status": "candidate",
            "semantic_owner_ref": None, "adoption_unit": False, "operated": False,
            "definition": "Private regeneration boundary replaced by independently governed master-data and reference-data products in the emitted corpus.",
            "evidence_refs": ["evidence.iso8000", "evidence.gleif.level2", "evidence.gs1.gdsn"],
        },
    ])

    for library in source.get("libraries", []):
        key = _key_from_id(library["library_id"])
        if key:
            library["library_id"] = _restore_combined_namespace(library["library_id"])
            library["owner_ref"] = _restore_combined_namespace(library["owner_ref"])
            library["provides"] = [_restore_combined_namespace(ref) for ref in library["provides"]]
            library["dependencies"] = [_restore_combined_namespace(ref) for ref in library["dependencies"]]
            library["product_refs"] = [OLD_PRODUCT]

    for requirement in source.get("requirements", []):
        key = _key_from_id(requirement.get("capability_ref", ""))
        if key:
            requirement["requirement_id"] = _restore_combined_namespace(requirement["requirement_id"])
            requirement["capability_ref"] = _restore_combined_namespace(requirement["capability_ref"])
            requirement["consumer_ref"] = OLD_PRODUCT

    source["relations"] = [
        row for row in source.get("relations", [])
        if row["relation_id"] not in {"relation.suite.packages.master_data", "relation.suite.packages.reference_data"}
    ]
    source["relations"].append({
        "relation_id": "relation.suite.packages.master", "from_ref": "suite.data_governance",
        "predicate": "packages", "to_ref": OLD_PRODUCT, "binding_phase": "authoring",
    })
    for relation in source["relations"]:
        key = _key_from_id(relation.get("to_ref", ""))
        if key:
            relation["relation_id"] = _restore_combined_namespace(relation["relation_id"])
            relation["from_ref"] = OLD_PRODUCT
            relation["to_ref"] = _restore_combined_namespace(relation["to_ref"])

    for binding in source.get("binding_maps", []):
        key = _key_from_id(binding.get("abstract_library_ref", ""))
        if key:
            binding["binding_map_id"] = _restore_combined_namespace(binding["binding_map_id"])
            binding["abstract_library_ref"] = _restore_combined_namespace(binding["abstract_library_ref"])
            binding["product_refs"] = [OLD_PRODUCT]

    source["boundary_decisions"] = [
        row for row in source["boundary_decisions"]
        if row["decision_id"] not in {
            "decision.governance.master_data", "decision.governance.reference_data",
            "decision.governance.master_reference_split",
        }
    ]
    for meaning in source["ownership"]:
        if meaning.get("owner_ref") in {MASTER_OWNER, REFERENCE_OWNER}:
            meaning["owner_ref"] = OLD_OWNER
        collapsed = [OLD_OWNER if ref in {MASTER_OWNER, REFERENCE_OWNER} else ref for ref in meaning["must_not_be_owned_by"]]
        meaning["must_not_be_owned_by"] = [
            ref for ref in dict.fromkeys(collapsed) if ref != meaning.get("owner_ref")
        ]

    source["ddd_dossiers"] = [
        row for row in source.get("ddd_dossiers", [])
        if row.get("product_ref") not in {MASTER_PRODUCT, REFERENCE_PRODUCT}
    ]
    source["crosswalks"] = [
        row for row in source["crosswalks"]
        if row["legacy_ref"] != "candidate.product.master_reference_data"
    ]
    source["negative_tests"] = [
        row for row in source["negative_tests"]
        if not row["test_id"].startswith("negative.master_reference.")
    ]
    split_laws = {
        "master data governance != reference data governance",
        "master entity != reference value != code != designation",
        "resolution assertion != master identity issuance != master projection",
        "reference mapping != equivalence and forward mapping != reverse mapping",
    }
    source["non_collapse_laws"] = [
        law for law in source.get("non_collapse_laws", []) if law not in split_laws
    ]
    return source


def enrich_master_reference_split(source: dict[str, Any]) -> dict[str, Any]:
    evidence_master = ["evidence.iso8000", "evidence.gleif.level2", "gmo.source.e024", "gmo.source.e037"]
    evidence_reference = ["evidence.gs1.gdsn", "gmo.source.e004", "gmo.source.e022", "gmo.source.e025"]

    source["artifacts"] = [row for row in source["artifacts"] if row["artifact_id"] not in {OLD_PRODUCT, OLD_OWNER}]
    source["artifacts"].extend([
        _product(MASTER_PRODUCT, MASTER_OWNER, "Master Data Governance", "Govern authority-scoped master identities source authority survivorship projections and stewardship lifecycles.", evidence_master, MASTER_TRUTH),
        _semantic(MASTER_OWNER, "Master data governance semantics", "Owns master-domain identity source authority survivorship stewardship and master-edition lifecycle without owning source truth or entity resolution.", evidence_master),
        _product(REFERENCE_PRODUCT, REFERENCE_OWNER, "Reference Data Governance", "Govern reference schemes sets code editions designations replacements and directional crosswalk lifecycles.", evidence_reference, REFERENCE_TRUTH),
        _semantic(REFERENCE_OWNER, "Reference data governance semantics", "Owns reference-scheme code designation mapping publication and retirement lifecycle without owning master entities terminology or ontology truth.", evidence_reference),
    ])
    for artifact in source["artifacts"]:
        key = _key_from_id(artifact["artifact_id"])
        if key:
            artifact["artifact_id"] = _rewrite_exact_id(artifact["artifact_id"])
            owner = artifact.get("semantic_owner_ref")
            if owner:
                artifact["semantic_owner_ref"] = _rewrite_exact_id(owner)
    for artifact in source["artifacts"]:
        if artifact["artifact_id"] == "capability.adjudicate_master_record":
            artifact["semantic_owner_ref"] = MASTER_OWNER
        elif artifact["artifact_id"] == "capability.publish_reference_codes":
            artifact["semantic_owner_ref"] = REFERENCE_OWNER

    for library in source["libraries"]:
        key = _key_from_id(library["library_id"])
        if not key:
            continue
        library["library_id"] = _rewrite_exact_id(library["library_id"])
        library["owner_ref"] = _rewrite_exact_id(library["owner_ref"])
        library["provides"] = [_rewrite_exact_id(ref) for ref in library["provides"]]
        library["dependencies"] = [_rewrite_exact_id(ref) for ref in library["dependencies"]]
        library["product_refs"] = [_product_for_key(key)]

    for requirement in source["requirements"]:
        key = _key_from_id(requirement["capability_ref"])
        if key:
            requirement["requirement_id"] = _rewrite_exact_id(requirement["requirement_id"])
            requirement["capability_ref"] = _rewrite_exact_id(requirement["capability_ref"])
            requirement["consumer_ref"] = _product_for_key(key)

    rewritten_relations = []
    for relation in source["relations"]:
        if relation["relation_id"] == "relation.suite.packages.master":
            for product, suffix in ((MASTER_PRODUCT, "master_data"), (REFERENCE_PRODUCT, "reference_data")):
                rewritten_relations.append({**relation, "relation_id": f"relation.suite.packages.{suffix}", "to_ref": product, "authority_effect": "Packaging transfers no semantic identity publication or effect authority."})
            continue
        key = _key_from_id(relation["to_ref"])
        if key and relation["from_ref"] == OLD_PRODUCT:
            relation["relation_id"] = _rewrite_for_key(relation["relation_id"], key)
            relation["from_ref"] = _product_for_key(key)
            relation["to_ref"] = _rewrite_exact_id(relation["to_ref"])
        rewritten_relations.append(relation)
    source["relations"] = rewritten_relations

    for binding in source["binding_maps"]:
        key = _key_from_id(binding["abstract_library_ref"])
        if key:
            binding["binding_map_id"] = _rewrite_exact_id(binding["binding_map_id"])
            binding["abstract_library_ref"] = _rewrite_exact_id(binding["abstract_library_ref"])
            binding["product_refs"] = [_product_for_key(key)]

    source["boundary_decisions"] = [row for row in source["boundary_decisions"] if row["decision_id"] != "decision.governance.master_reference"]
    source["boundary_decisions"].extend([
        {"decision_id": "decision.governance.master_data", "subject_ref": MASTER_PRODUCT, "disposition": "strong_product_candidate", "rationale": "Master-domain identity issuance source authority survivorship master projection and stewardship form an independently operated authority and lifecycle that does not require reference-code governance.", "split_test": _axis_test(evidence_master), "supersedes": ["candidate.product.master_reference_data"], "evidence_refs": evidence_master},
        {"decision_id": "decision.governance.reference_data", "subject_ref": REFERENCE_PRODUCT, "disposition": "strong_product_candidate", "rationale": "Reference schemes code editions designations deprecation replacement crosswalk and publication form an independently adopted maintenance-authority lifecycle that does not require mastered entities.", "split_test": _axis_test(evidence_reference), "supersedes": ["candidate.product.master_reference_data"], "evidence_refs": evidence_reference},
        {"decision_id": "decision.governance.master_reference_split", "subject_ref": "suite.data_governance", "disposition": "split_overloaded_product", "rationale": "Master entities and reference/code systems have different sovereign questions authorities users states outputs and adoption paths; either product can be adopted without the other.", "evidence_refs": sorted(set(evidence_master + evidence_reference))},
    ])

    for meaning in source["ownership"]:
        if meaning["meaning_id"] == "meaning.master_identity":
            meaning["owner_ref"] = MASTER_OWNER
        elif meaning["meaning_id"] == "meaning.reference_code_edition":
            meaning["owner_ref"] = REFERENCE_OWNER
        excluded: list[str] = []
        for ref in meaning["must_not_be_owned_by"]:
            if ref == OLD_OWNER:
                excluded.extend([MASTER_OWNER, REFERENCE_OWNER])
            else:
                excluded.append(ref)
        meaning["must_not_be_owned_by"] = list(dict.fromkeys(excluded))

    source["ddd_dossiers"] = [row for row in source["ddd_dossiers"] if row["product_ref"] != OLD_PRODUCT]
    source["ddd_dossiers"].extend([
        _dossier(MASTER_PRODUCT, MASTER_OWNER, MASTER_TRUTH, "master_data"),
        _dossier(REFERENCE_PRODUCT, REFERENCE_OWNER, REFERENCE_TRUTH, "reference_data"),
    ])

    for row in source["crosswalks"]:
        row["canonical_refs"] = [MASTER_PRODUCT if ref == OLD_PRODUCT else ref for ref in row["canonical_refs"]]
    source["crosswalks"] = [row for row in source["crosswalks"] if row["legacy_ref"] != "candidate.product.master_reference_data"]
    source["crosswalks"].append({"legacy_ref": "candidate.product.master_reference_data", "disposition": "split_without_compatibility_alias", "canonical_refs": [MASTER_PRODUCT, REFERENCE_PRODUCT], "loss_or_warning": "Intent must select master governance reference governance or both; the overloaded combined identity is removed and no compatibility alias is emitted."})

    source["negative_tests"].extend([
        {"test_id": "negative.master_reference.combined_lifecycle", "input_claim": "Master entities and reference-code systems necessarily share one product lifecycle and authority.", "expected_refusal": "select the independently owned master and reference products required by intent"},
        {"test_id": "negative.master_reference.resolution_identity", "input_claim": "An entity-resolution cluster may issue or mutate a master identity.", "expected_refusal": "require master-domain issuing authority and an accepted resolution assertion"},
        {"test_id": "negative.master_reference.golden_truth", "input_claim": "A survivorship projection is universal source truth.", "expected_refusal": "return the scoped projection edition field provenance and residual conflicts"},
        {"test_id": "negative.master_reference.code_concept", "input_claim": "A code label or notation is the referenced concept.", "expected_refusal": "preserve concept code designation language and edition identities"},
        {"test_id": "negative.master_reference.crosswalk_equivalence", "input_claim": "A forward crosswalk proves reverse semantic equivalence.", "expected_refusal": "preserve direction relation cardinality ambiguity and information loss"},
    ])
    source["non_collapse_laws"].extend([
        "master data governance != reference data governance",
        "master entity != reference value != code != designation",
        "resolution assertion != master identity issuance != master projection",
        "reference mapping != equivalence and forward mapping != reverse mapping",
    ])
    assert set(MASTER_TRUTH) == PRODUCT_FIELDS and set(REFERENCE_TRUTH) == PRODUCT_FIELDS
    return source
