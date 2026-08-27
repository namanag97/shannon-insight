#!/usr/bin/env python3
"""Build exact Master Data and Reference Data governance contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for row in rows)


def S(ident: str, title: str, publisher: str, url: str, scope: str, limit: str, kind: str = "official_specification") -> dict:
    return {"source_id": f"source.master-reference.{ident}", "title": title, "publisher": publisher, "url": url, "source_kind": kind, "claim_scope": scope, "scope_limit": limit}


SOURCES = [
    S("w3c.prov-o", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", "source attribution, derivation, specialization, alternates, agents and activities", "PROV describes provenance relations; it does not establish master identity, authority or truth."),
    S("w3c.prov-constraints", "Constraints of the PROV Data Model", "W3C", "https://www.w3.org/TR/prov-constraints/", "generation, usage, derivation and temporal constraints", "PROV validity does not prove source accuracy or survivorship correctness."),
    S("w3c.skos", "SKOS Simple Knowledge Organization System Reference", "W3C", "https://www.w3.org/TR/skos-reference/", "concept schemes, notations, labels and mapping relations", "SKOS mapping properties do not make mappings universally substitutable."),
    S("oasis.genericode.1", "Code List Representation (genericode) Version 1.0", "OASIS Open", "https://docs.oasis-open.org/codelist/genericode/v1.0/genericode-v1.0.html", "code-list identity, version identity, columns, keys and list sets", "A genericode document is a representation contract, not publisher authority or lifecycle policy."),
    S("hl7.fhir.r5.codesystem", "FHIR R5 CodeSystem", "HL7 International", "https://hl7.org/fhir/R5/codesystem.html", "code-system identity, versions, concepts, designations and properties", "FHIR terminology semantics are evidence for boundaries, not universal enterprise terminology policy."),
    S("hl7.fhir.r5.valueset", "FHIR R5 ValueSet", "HL7 International", "https://hl7.org/fhir/R5/valueset.html", "intensional and extensional value-set definitions and expansions", "A value-set expansion is cut- and parameter-bound, not an eternal reference set."),
    S("hl7.fhir.r5.conceptmap", "FHIR R5 ConceptMap", "HL7 International", "https://hl7.org/fhir/R5/conceptmap.html", "directional, contextual, one-to-many terminology mappings", "FHIR ConceptMap is trial-use and a mapping assertion never proves reverse or business equivalence."),
    S("iso.11179-1.2023", "ISO/IEC 11179-1:2023 Metadata Registries Framework", "ISO", "https://www.iso.org/standard/78914.html", "metadata registry conceptual framework", "The public abstract does not expose paywalled clause-level requirements."),
    S("iso.11179-6", "ISO/IEC 11179-6 Registration", "ISO", "https://www.iso.org/standard/35348.html", "registration authority, administered-item identification and status", "The public abstract supports only catalog-level registration claims."),
    S("iso.8000-110.2021", "ISO 8000-110:2021 Master Data Exchange", "ISO", "https://www.iso.org/standard/78501.html", "machine-checkable syntax and semantic encoding for characteristic master data exchange", "Exchange conformance does not confer identity authority or source correctness."),
    S("iso.8000-115.2024", "ISO 8000-115:2024 Quality Identifiers", "ISO", "https://www.iso.org/standard/88847.html", "identifier owner, use restrictions and resolution characteristics", "Quality-identifier conformance is not universal master-entity identity."),
    S("gleif.lei-cdf.3.1", "LEI Common Data File 3.1 Documentation", "Global Legal Entity Identifier Foundation", "https://www.gleif.org/content/4_lei-data/1_access-and-use-lei-data/2_level-1-data-lei-cdf-3-1-format/lei-cdf_version_3.1-documentation.html", "exclusive LEI assignment, registration status, validation authority and effective dates", "LEI rules apply to legal entities in the GLEIS and do not generalize to every master domain."),
    S("gs1.id-keys", "GS1 Identification Keys", "GS1", "https://www.gs1.org/standards/id-keys", "authority-scoped identifiers for products, parties, locations, documents and assets", "GS1 keys cover specified supply-chain identities, not arbitrary enterprise identity."),
    S("gs1.general-specifications", "GS1 General Specifications", "GS1", "https://ref.gs1.org/standards/genspecs/", "identifier allocation, namespace interpretation, lifecycle and non-reuse rules", "GS1 allocation rules cannot be silently applied outside the exact key type and edition."),
    S("unece.unlocode", "UN/LOCODE", "UNECE", "https://unlocode.unece.org/", "maintenance requests, authority review, status assignment and releases", "UN/LOCODE is one maintained reference-data system, not a generic MDM implementation."),
    S("sdmx.information-model", "SDMX Information Model", "SDMX", "https://docs.sdmx.org/en/latest/pages/information-model.html", "agency, maintainable artefact, version and codelist semantics", "SDMX concepts apply to statistical exchange structures and require explicit cross-domain adaptation."),
]


def context(slug: str, name: str, question: str, outside: list[str]) -> dict:
    return {"context_id": f"context.{slug}", "name": name, "sovereign_question": question, "inside": ["exact semantic identities", "editioned policy", "typed operations", "laws", "refusals"], "outside": outside + ["provider qualification", "ambient persistence", "unauthorized external effects"], "owner": f"authority.{slug}", "status": "specified_candidate"}


CONTEXTS = [
    context("master_data.domain_identity", "Master domain identity", "Under an exact domain and issuing authority, which durable master identity denotes which accepted domain subject across its lifecycle?", ["source-record identity", "probabilistic entity resolution", "survivorship projection"]),
    context("master_data.source_authority", "Source attribute authority", "For which attribute, context and valid-time interval may which independently identified source record supply an authoritative candidate value?", ["source record registration", "source-system truth", "master identity issuance"]),
    context("master_data.survivorship_projection", "Survivorship projection", "Given exact source candidates, authority assertions and rules, what reproducible field-level master projection and explanation result?", ["source mutation", "identity issuance", "manual decision authority"]),
    context("master_data.stewardship_case", "Master-data stewardship case", "How are unresolved identity, authority and survivorship conflicts assigned, decided, corrected and closed with maker-checker evidence?", ["automatic source mutation", "business approval outside explicit delegation"]),
    context("reference_data.reference_set", "Reference set", "Which exact publisher-scoped set edition contains which reference values, validity intervals and replacement relations?", ["master-entity identity", "concept ontology", "physical distribution"]),
    context("reference_data.code_set_lifecycle", "Code-set lifecycle", "Under which maintenance agency and edition do stable codes, concepts, designations, statuses and changes exist?", ["reference-set selection for a use case", "cross-system mapping"]),
    context("reference_data.crosswalk_mapping", "Crosswalk mapping", "Under exact source and target editions, direction, context and cardinality, what mapping results and information loss are justified?", ["concept identity", "reverse mapping by assumption", "business acceptance"]),
]


DECISIONS: dict[str, list[str]] = {
    "master_data.domain_identity": ["domain_scope", "issuing_authority", "identity_evidence", "alias_merge_split_policy", "retirement_and_reuse"],
    "master_data.source_authority": ["attribute_scope", "source_record_identity", "authority_basis", "valid_time_model", "conflict_precedence"],
    "master_data.survivorship_projection": ["rule_precedence", "missing_value_posture", "tie_break", "manual_override", "projection_cut"],
    "master_data.stewardship_case": ["case_classification", "assignment_authority", "maker_checker", "correction_scope", "closure_evidence"],
    "reference_data.reference_set": ["publisher_authority", "set_and_edition_identity", "value_identity", "validity_model", "deprecation_replacement"],
    "reference_data.code_set_lifecycle": ["maintenance_agency", "code_identity", "designation_language", "change_classification", "retirement_and_reuse"],
    "reference_data.crosswalk_mapping": ["source_target_editions", "directionality", "cardinality", "context_and_dependency", "loss_acceptance"],
}


DECISION_ROWS = [{"decision_id": f"decision.{ctx}.{decision}", "owner_context": f"context.{ctx}", "question": f"What exact {decision.replace('_', ' ')} applies?", "default": None, "default_law": "forbidden", "status": "declared"} for ctx, values in DECISIONS.items() for decision in values]


def O(ctx: str, name: str, inputs: list[str], output: str, purity: str = "pure", intent: str | None = None, receipt: str | None = None) -> dict:
    row = {"operation_ref": f"operation.{ctx}.{name}", "input_types": inputs, "output_type": f"Result<{output},{ctx.split('.')[-1].title().replace('_', '')}Refusal>", "purity": purity}
    if intent:
        row["effect_intent_type"] = intent
    if receipt:
        row["receipt_type"] = receipt
    return row


SPECS = [
    {"id":"library.master_data.domain_identity","ctx":"master_data.domain_identity","name":"Master Domain Identity","kind":"effect_port","types":["MasterDomainId","MasterDomainEdition","DomainSubjectRef","MasterEntityId","IdentityIssuingAuthorityRef","AcceptedResolutionAssertionRef","IdentityEvidenceSet","MasterAlias","IdentityRelation","IdentityStatus","IdentityIssuanceIntent","IdentityIssuanceReceipt","IdentityRetirementIntent","DomainIdentityRefusal"],"ops":[O("master_data.domain_identity","evaluate_issuance",["DomainSubjectRef","AcceptedResolutionAssertionRef","IdentityEvidenceSet","IdentityPolicy"],"IdentityEligibility"),O("master_data.domain_identity","plan_issuance",["IdentityEligibility","IdentityIssuingAuthorityRef","IdentitySnapshot"],"IdentityIssuanceIntent"),O("master_data.domain_identity","apply_issuance_receipt",["IdentityIssuanceIntent","IdentityIssuanceReceipt","IdentitySnapshot"],"IdentitySnapshot"),O("master_data.domain_identity","plan_retirement",["MasterEntityId","IdentitySnapshot","RetirementPolicy"],"IdentityRetirementIntent")],"laws":["Master entity identity is not a source-record identifier, match score, candidate link, entity-resolution cluster or survivorship projection.","A match score or cluster cannot become identity without a separately accepted resolution assertion and issuing authority.","Identity, alias, equivalence assertion, merge, split, successor and retirement are distinct relations or events.","Retirement preserves historical resolution; reuse and alias inheritance require explicit domain policy."],"errors":["DomainScopeUnbound","IssuingAuthorityMissing","ResolutionAssertionUnaccepted","IdentityCollision","MergeSplitAmbiguous","RetirementBlocked"],"deps":[],"evidence":["source.master-reference.gleif.lei-cdf.3.1","source.master-reference.gs1.id-keys","source.master-reference.iso.8000-115.2024"]},
    {"id":"library.master_data.source_authority","ctx":"master_data.source_authority","name":"Source Attribute Authority","kind":"policy_pure","types":["SourceRecordRef","SourceOccurrenceRef","AttributePath","AuthorityContext","AuthorityBasisRef","AttributeAuthorityAssertion","AuthorityValidityInterval","CandidateValue","CandidateProvenance","AuthorityRank","AuthorityConflict","AuthorityEvaluation","EffectiveCandidateSet","SourceAuthorityRefusal"],"ops":[O("master_data.source_authority","validate_source_reference",["SourceRecordRef","SourceOccurrenceCatalogCut"],"ValidatedSourceRecordRef"),O("master_data.source_authority","evaluate_attribute_authority",["AttributeAuthorityAssertionSet","AttributePath","AuthorityContext","ValidTime"],"AuthorityEvaluation"),O("master_data.source_authority","rank_candidates",["CandidateValueSet","AuthorityEvaluation","PrecedencePolicy"],"EffectiveCandidateSet"),O("master_data.source_authority","detect_authority_conflict",["AttributeAuthorityAssertionSet","AuthorityConflictPolicy"],"AuthorityConflictSet")],"laws":["Master Data references source records owned and identified by source occurrences; it never registers or rewrites them.","Authority is attribute-, context-, purpose- and valid-time-scoped; source-wide priority is not implied.","Latest, most complete, most frequent and most authoritative are independent orderings.","Every candidate value retains exact source-record and extraction provenance even when it is not selected."],"errors":["SourceRecordUnresolved","AttributeScopeAmbiguous","AuthorityBasisMissing","ValidityOverlap","PrecedenceIncomplete","AuthorityConflictUnresolved"],"deps":["library.master_data.domain_identity"],"evidence":["source.master-reference.w3c.prov-o","source.master-reference.w3c.prov-constraints","source.master-reference.gleif.lei-cdf.3.1"]},
    {"id":"library.master_data.survivorship_projection","ctx":"master_data.survivorship_projection","name":"Survivorship Projection","kind":"algorithm_pure","types":["SurvivorshipPolicy","CompiledSurvivorshipRule","CandidateValue","CandidateSet","ProjectionCut","FieldDecision","DecisionExplanation","ProjectionField","MasterProjectionEdition","ProjectionDigest","ProjectionResidual","ManualOverrideRef","SurvivorshipTrace","SurvivorshipRefusal"],"ops":[O("master_data.survivorship_projection","compile_rules",["SurvivorshipPolicy","SourceAuthorityPolicy"],"CompiledSurvivorshipRuleSet"),O("master_data.survivorship_projection","select_field",["CandidateSet","CompiledSurvivorshipRuleSet","ProjectionCut"],"FieldDecision"),O("master_data.survivorship_projection","assemble_projection",["MasterEntityId","FieldDecisionSet","ProjectionPolicy"],"MasterProjectionEdition"),O("master_data.survivorship_projection","explain_projection",["MasterProjectionEdition","SurvivorshipTrace"],"DecisionExplanationSet")],"laws":["A master or golden record is a reproducible, cut-bound projection and not universal truth or master identity.","Field-level selection preserves candidates, provenance, authority evaluation, rule edition and residual conflict.","Manual override is an authority-, reason-, scope- and expiry-bound input; it is not an invisible higher priority.","Unknown, missing, explicit null, inapplicable, conflicting and withheld values remain distinct."],"errors":["RulePrecedenceInvalid","CandidateProvenanceMissing","ProjectionCutIncomplete","TieUnresolved","OverrideUnauthorized","ResidualConflictUnaccepted"],"deps":["library.master_data.domain_identity","library.master_data.source_authority"],"evidence":["source.master-reference.w3c.prov-o","source.master-reference.iso.8000-110.2021","source.master-reference.gleif.lei-cdf.3.1"]},
    {"id":"library.master_data.stewardship_case","ctx":"master_data.stewardship_case","name":"Master Data Stewardship Case","kind":"effect_port","types":["MasterStewardshipCaseId","MasterConflictRef","CaseClassification","StewardAuthorityRef","CaseAssignmentIntent","CaseAssignmentReceipt","StewardDecision","DecisionEvidenceSet","CorrectionProposal","CorrectionEffectIntent","CaseClosureEligibility","CaseClosureIntent","CaseClosureReceipt","StewardshipRefusal"],"ops":[O("master_data.stewardship_case","plan_case_opening",["MasterConflictRef","CasePolicy"],"CaseOpeningIntent"),O("master_data.stewardship_case","plan_assignment",["MasterStewardshipCaseId","StewardAuthorityRef","AssignmentPolicy"],"CaseAssignmentIntent"),O("master_data.stewardship_case","evaluate_decision",["StewardDecision","DecisionEvidenceSet","MakerCheckerPolicy"],"DecisionEligibility"),O("master_data.stewardship_case","plan_closure",["MasterStewardshipCaseId","DecisionEligibility","ClosureEvidenceSet"],"CaseClosureIntent")],"laws":["A stewardship decision is not a source mutation, identity issuance, correction effect or case closure.","Maker, checker, steward, source owner, identity issuer and correction executor are distinct roles unless explicitly delegated.","Correction is an effect intent addressed to the owning source or projection port and requires a receipt.","Case closure preserves conflict history, rationale, dissent, appeals and unresolved residuals."],"errors":["ConflictUnbound","StewardAuthorityMissing","MakerCheckerViolated","DecisionEvidenceInsufficient","CorrectionScopeInvalid","ClosureUnproved"],"deps":["library.master_data.survivorship_projection"],"evidence":["source.master-reference.iso.11179-6","source.master-reference.unece.unlocode","source.master-reference.gleif.lei-cdf.3.1"]},
    {"id":"library.reference_data.reference_set","ctx":"reference_data.reference_set","name":"Reference Set","kind":"effect_port","types":["ReferenceSetId","ReferenceSetEdition","PublisherAuthorityRef","ReferenceValueId","ReferenceValue","ReferenceValueStatus","ValidityInterval","ReplacementRelation","ReferenceSetPublicationIntent","ReferenceSetPublicationReceipt","ReferenceResolutionQuery","ReferenceResolution","ReferenceSetDiff","ReferenceSetRefusal"],"ops":[O("reference_data.reference_set","validate_edition",["ReferenceSetEdition","ReferenceSetPolicy"],"ReferenceSetValidation"),O("reference_data.reference_set","resolve_effective_value",["ReferenceResolutionQuery","ReferenceSetEdition","ValidTime"],"ReferenceResolution"),O("reference_data.reference_set","plan_publication",["ReferenceSetEdition","PublisherAuthorityRef","PublicationPolicy"],"ReferenceSetPublicationIntent"),O("reference_data.reference_set","plan_deprecation",["ReferenceValueId","ReplacementRelationSet","DeprecationPolicy"],"ReferenceValueDeprecationIntent")],"laws":["A reference value classifies or constrains other data; it is not thereby a mastered business entity.","Stable set identity, immutable edition, value identity, label and physical distribution are distinct.","Validity time, recording time, publication time, deprecation time and replacement-effective time remain distinct.","Deprecated or withdrawn values retain historical resolution and do not imply an unambiguous replacement."],"errors":["PublisherAuthorityMissing","SetEditionConflict","ValueIdentityCollision","ValidityOverlap","ReplacementAmbiguous","PublicationCompletionUnknown"],"deps":[],"evidence":["source.master-reference.oasis.genericode.1","source.master-reference.iso.11179-1.2023","source.master-reference.unece.unlocode"]},
    {"id":"library.reference_data.code_set_lifecycle","ctx":"reference_data.code_set_lifecycle","name":"Code Set Lifecycle","kind":"effect_port","types":["CodeSetId","CodeSetEdition","MaintenanceAgencyRef","ConceptRef","Code","CodeIdentity","Designation","LanguageTag","CodeStatus","CodeChange","CodeAdditionIntent","DesignationChangeIntent","CodeRetirementIntent","CodeSetReceipt","CodeSetRefusal"],"ops":[O("reference_data.code_set_lifecycle","validate_code",["Code","CodeIdentityPolicy","CodeSetEdition"],"CodeValidation"),O("reference_data.code_set_lifecycle","plan_addition",["Code","ConceptRef","DesignationSet","MaintenanceAgencyRef"],"CodeAdditionIntent"),O("reference_data.code_set_lifecycle","plan_designation_change",["CodeIdentity","DesignationSet","DesignationPolicy"],"DesignationChangeIntent"),O("reference_data.code_set_lifecycle","plan_retirement",["CodeIdentity","CodeSetEdition","RetirementPolicy"],"CodeRetirementIntent")],"laws":["Code, code identity, concept, notation, designation, definition and display label are distinct.","A code-set edition and each code's validity interval evolve independently and must both be bound.","Code addition, designation change, semantic change, retirement, withdrawal, replacement and reuse are distinct.","Retired codes preserve historical meaning; code reuse is forbidden unless the exact maintenance policy proves otherwise."],"errors":["MaintenanceAgencyMissing","CodeCollision","ConceptUnbound","LanguageTagInvalid","SemanticChangeMisclassified","CodeReuseForbidden"],"deps":["library.reference_data.reference_set"],"evidence":["source.master-reference.w3c.skos","source.master-reference.oasis.genericode.1","source.master-reference.hl7.fhir.r5.codesystem","source.master-reference.sdmx.information-model"]},
    {"id":"library.reference_data.crosswalk_mapping","ctx":"reference_data.crosswalk_mapping","name":"Crosswalk Mapping","kind":"effect_port","types":["CrosswalkId","CrosswalkEdition","SourceSetEditionRef","TargetSetEditionRef","MappingDirection","MappingCardinality","MappingRelationship","MappingContext","MappingDependency","MappingAssertion","MappingResult","MappingResidual","InformationLossProfile","CrosswalkPublicationIntent","CrosswalkRefusal"],"ops":[O("reference_data.crosswalk_mapping","validate_mapping",["MappingAssertion","CrosswalkPolicy"],"MappingValidation"),O("reference_data.crosswalk_mapping","map_value",["ReferenceValueId","CrosswalkEdition","MappingContext"],"MappingResult"),O("reference_data.crosswalk_mapping","compose_crosswalks",["CrosswalkEditionList","CompositionPolicy"],"ComposedCrosswalk"),O("reference_data.crosswalk_mapping","plan_publication",["CrosswalkEdition","MappingEvidenceSet","PublisherAuthorityRef"],"CrosswalkPublicationIntent")],"laws":["Crosswalk relation is not equivalence by default; related, exact, close, broader, narrower and not-related remain distinct.","Every mapping binds exact source and target set editions, direction, cardinality, context and dependencies.","A mapping in one direction does not imply a reverse mapping, invertibility or round-trip preservation.","Composition accumulates ambiguity, partiality and information loss monotonically and may refuse rather than fabricate a result."],"errors":["SourceEditionUnbound","TargetEditionUnbound","DirectionAmbiguous","CardinalityAmbiguous","MappingContextMissing","InformationLossUnaccepted"],"deps":["library.reference_data.reference_set","library.reference_data.code_set_lifecycle"],"evidence":["source.master-reference.w3c.skos","source.master-reference.hl7.fhir.r5.conceptmap","source.master-reference.hl7.fhir.r5.valueset"]},
]


def materialize(spec: dict) -> dict:
    ctx = spec["ctx"]
    effect = "pure_effect_intents" if spec["kind"] == "effect_port" else "pure_no_io"
    return {"library_id": spec["id"], "name": spec["name"], "library_kind": spec["kind"], "semantic_owner_context": f"context.{ctx}", "status": "specified", "candidate_responsibility": spec["name"].lower(), "effect_boundary": effect, "public_types": spec["types"], "public_traits": [spec["name"].replace(" ", "") + "Algebra"], "operation_refs": [op["operation_ref"] for op in spec["ops"]], "operations": spec["ops"], "decision_refs": [f"decision.{ctx}.{d}" for d in DECISIONS[ctx]], "configuration_contracts": [spec["name"].replace(" ", "") + "Policy"], "laws": spec["laws"], "invariants": ["published editions and accepted receipts are immutable", "all identity, authority, evidence, validity and mappings are exact-scope, edition and time bound", "unknown, absent, refused, failed, indeterminate and completion-unknown remain distinct"], "error_contracts": spec["errors"] + ["UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"], "dependencies": spec["deps"], "evidence_refs": spec["evidence"], "oracles": ["canonical positive fixtures", "negative twins", "property laws", "state-machine model tests", "malformed and boundary corpus", "edition migration corpus", "two independent differential implementations"], "gaps": ["No implementation is qualified; two independent implementations and executed conformance remain required."], "must_not_own": ["source-system records or facts", "entity-resolution scores or clusters", "provider qualification", "legal interpretation", "unauthorized external effects"], "qualification_required": False}


LIBRARIES = [materialize(spec) for spec in SPECS]


NEGATIVES = [
    ("score_identity", "A high match score or entity-resolution cluster is a master identity.", "Require an accepted resolution assertion and explicit identity-issuing authority."),
    ("master_registers_source", "The MDM service registers or rewrites source-record identity.", "Reference the source occurrence's immutable record identity and issue only master-domain assertions."),
    ("latest_authoritative", "The latest source value is automatically authoritative.", "Evaluate attribute-, context-, purpose- and valid-time-scoped authority."),
    ("golden_truth", "The golden record is universal source truth.", "Treat it as a reproducible projection with candidates, provenance and residual conflicts."),
    ("override_priority", "Manual override is an invisible highest-priority source.", "Bind override authority, reason, scope, validity and expiry explicitly."),
    ("steward_mutates", "A steward decision automatically mutates a source system.", "Emit a correction intent to the owning port and reconcile its receipt."),
    ("reference_master", "Every reference value is a mastered business entity.", "Keep classification values and domain entities in separate identity contexts."),
    ("code_label", "A displayed label is the stable code or concept identity.", "Bind code, concept, designation, language and edition separately."),
    ("retire_delete", "Retiring a code deletes its historical meaning.", "Preserve historical resolution, status and replacement relations."),
    ("code_reuse", "A retired code may be silently reused.", "Refuse unless the exact maintenance policy and scope explicitly permit reuse."),
    ("map_equivalence", "A crosswalk row proves semantic equivalence.", "Retain the exact mapping relationship, evidence, context and loss profile."),
    ("reverse_mapping", "A forward mapping implies a valid reverse mapping.", "Require an independently governed reverse assertion or refuse."),
    ("agent_authority", "A model or agent may issue identity, waive conflict, approve a code or ratify a mapping.", "Require the named human or institutional authority and an external receipt."),
]


NEGATIVE_ROWS = [{"negative_id": f"negative.master-reference.{slug}", "unsafe_inference": unsafe, "required_behavior": behavior, "status": "active"} for slug, unsafe, behavior in NEGATIVES]


COMPILER_ROWS = []
for lib in LIBRARIES:
    stem = lib["library_id"].removeprefix("library.")
    COMPILER_ROWS += [
        {"record_kind": "capability_requirement", "requirement_id": f"requirement.{stem}.implementation", "subject_ref": lib["library_id"], "required_operations": lib["operation_refs"], "required_decisions": lib["decision_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": f"offer.{stem}.reference", "subject_ref": lib["library_id"], "claimed_operations": lib["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": f"requirement.{stem}.implementation", "offer_ref": f"offer.{stem}.reference", "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable implementation.", "selectable": False, "status": "declared"},
    ]


FILES = {"sources.jsonl": SOURCES, "bounded-contexts.jsonl": CONTEXTS, "decision-points.jsonl": DECISION_ROWS, "library-contracts.jsonl": LIBRARIES, "compiler-contracts.jsonl": COMPILER_ROWS, "negative-twins.jsonl": NEGATIVE_ROWS}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id": "master_reference_data_governance_v0_1_0", "as_of": AS_OF, "edition": EDITION, "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False, "qualified_implementation_count": 0}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS master/reference data governance: {len(SOURCES)} sources, {len(CONTEXTS)} contexts, {len(DECISION_ROWS)} decisions, {len(LIBRARIES)} exact libraries, {len(COMPILER_ROWS)} compiler contracts")


if __name__ == "__main__":
    main()
