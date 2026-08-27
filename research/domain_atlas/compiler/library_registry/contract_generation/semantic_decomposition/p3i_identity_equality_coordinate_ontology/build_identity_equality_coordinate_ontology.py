#!/usr/bin/env python3
"""Build a subject/relation-positioned identity/equality ontology and lossless P3I rebase."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
P3I_DOCKETS = SEM / "p3i_identity_equality_evidence/family-evidence-dockets.jsonl"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))

from member_axis_rebase import build_member_rebase  # noqa: E402


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {
        "source_id": "source.identity.rfc8141-urn",
        "title": "RFC 8141: Uniform Resource Names (URNs)",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc8141.html",
        "bounded_implication": "A persistent identifier is qualified by a managed namespace whose definition, assignment process, uniqueness and reassignment rules are part of the identifier contract; resolution is optional and separate.",
        "authority_limit": "URN syntax and namespace management do not prove the identified resource exists, is authentic, is authorized or has one universal notion of sameness.",
    },
    {
        "source_id": "source.identity.rfc9562-uuid",
        "title": "RFC 9562: Universally Unique IDentifiers (UUIDs)",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc9562.html",
        "bounded_implication": "UUID variants and versions have different generation, ordering, namespace and privacy properties; name-based UUID identity includes a namespace identifier and name bytes.",
        "authority_limit": "UUID format does not define the domain subject, allocation authority, lifecycle continuity, referential integrity or semantic equality of identified objects.",
    },
    {
        "source_id": "source.identity.rdf11-concepts",
        "title": "RDF 1.1 Concepts and Abstract Syntax",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/rdf11-concepts/",
        "bounded_implication": "IRI, literal and blank-node identity have different rules; literal term equality can differ from value equality, blank-node labels are locally scoped and graph equality is isomorphism rather than serialization equality.",
        "authority_limit": "RDF term or graph equality does not establish real-world entity identity, truth, source authority or application-domain merge permission.",
    },
    {
        "source_id": "source.identity.owl2-direct-semantics",
        "title": "OWL 2 Web Ontology Language Direct Semantics",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/owl2-direct-semantics/",
        "bounded_implication": "SameIndividual, DifferentIndividuals and HasKey are distinct semantic constructs interpreted within an ontology and datatype semantics rather than inferred from spelling alone.",
        "authority_limit": "OWL identity assertions and keys do not by themselves resolve operational records, authorize merges or prove closed-world uniqueness.",
    },
    {
        "source_id": "source.identity.unicode-uax15",
        "title": "Unicode Standard Annex #15: Unicode Normalization Forms",
        "publisher": "Unicode Consortium",
        "url": "https://unicode.org/reports/tr15/",
        "bounded_implication": "Canonical and compatibility equivalence are different; NFC/NFD and NFKC/NFKD provide versioned, idempotent normalized forms for their respective equivalence relations.",
        "authority_limit": "Unicode normalization does not establish linguistic, locale, identifier, security-confusable or domain-object equality.",
    },
    {
        "source_id": "source.identity.rfc8785-jcs",
        "title": "RFC 8785: JSON Canonicalization Scheme",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc8785.html",
        "bounded_implication": "JCS fixes a canonical JSON representation suitable for repeatable hashing/signing under I-JSON and deterministic serialization constraints.",
        "authority_limit": "Equal canonical JSON bytes do not establish equal domain meaning, lifecycle identity, authority or correctness; unequal bytes need not imply semantic difference.",
    },
    {
        "source_id": "source.identity.kubernetes-names-uids",
        "title": "Kubernetes Object Names and IDs",
        "publisher": "Kubernetes",
        "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/names/",
        "bounded_implication": "A resource name is unique within kind and namespace at one time and may be reused after deletion, while a UID distinguishes historical object occurrences across cluster lifetime.",
        "authority_limit": "Kubernetes name/UID rules do not define application-domain identity, semantic equivalence, provider identity or continuity after migration to another authority domain.",
    },
    {
        "source_id": "source.identity.iceberg-spec",
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "bounded_implication": "Stable field IDs preserve schema-member identity through rename/reorder, name mapping can retain historical aliases and identifier fields do not themselves guarantee row uniqueness.",
        "authority_limit": "Iceberg field and row identifier rules do not establish business entity identity, cross-table referential integrity or source authority.",
    },
    {
        "source_id": "source.identity.onnx-ir",
        "title": "ONNX Intermediate Representation Specification",
        "publisher": "ONNX",
        "url": "https://onnx.ai/onnx/repo-docs/IR.html",
        "bounded_implication": "Operator-set, function, graph-local value and model-state identifiers have different scopes and uniqueness rules; deterministic output expectations remain distinct from artifact identity.",
        "authority_limit": "Equal names, graph bytes or outputs do not establish model identity, training lineage, calibration or behavioral equivalence over all admissible inputs.",
    },
]


IDENTITY_BEARER_ARCHETYPES = [
    ("identifier_namespace", "Managed domain in which identifier syntax, allocation and uniqueness are defined."),
    ("identifier_scheme_or_edition", "Versioned identifier grammar and interpretation rules."),
    ("opaque_surrogate_identifier", "Identifier whose internal text carries no domain meaning beyond scoped reference."),
    ("natural_or_business_key", "Domain attributes used as a key under explicit validity and mutability rules."),
    ("composite_key", "Ordered or named tuple of key components with null and normalization policy."),
    ("scoped_name", "Human- or client-provided name unique only within kind, namespace, tenant or time scope."),
    ("lifecycle_occurrence_identifier", "Identifier for one historical occurrence, distinct from a reusable name or logical type."),
    ("version_or_edition_identifier", "Identity for a definition or artifact edition and its succession relation."),
    ("schema_member_or_field_identifier", "Stable identity of a schema member independent of mutable label or order."),
    ("graph_node_or_iri", "Graph node identity under an IRI or graph-specific node model."),
    ("blank_or_local_node", "Locally scoped existential node whose carrier label is not global identity."),
    ("symbol_variable_or_anchor", "Identity scoped to a model, graph, plan, module or symbol table."),
    ("reference_or_locator", "Carrier that names or locates another subject through a resolver contract."),
    ("handle_token_or_capability", "Opaque runtime reference whose identity, authority and lifetime require separate treatment."),
    ("alias_or_historical_name", "Alternate designation linked to a subject without being the subject's occurrence identity."),
    ("canonical_representation", "Chosen normal form for one declared representation-equivalence relation."),
    ("content_digest_or_fingerprint", "Algorithm- and domain-separated digest used to identify or verify bytes/content."),
    ("value_semantic_identity", "Typed value identity and equality under an explicit datatype, unit, normalization or comparison profile."),
    ("domain_entity_or_aggregate", "Identity-bearing domain subject with lifecycle and merge/split rules."),
    ("event_observation_or_claim", "Identity of an occurrence, observation or assertion distinct from its subject and content."),
    ("model_plan_or_artifact", "Identity of a definition, trained state, executable plan or packaged artifact."),
    ("solution_or_assignment", "Identity of an optimization/simulation result distinct from objective value or status."),
    ("entity_resolution_cluster", "Provisional or adjudicated grouping of records with confidence, authority and reversibility."),
    ("external_resource_occurrence", "Provider-scoped runtime resource occurrence with name, UID and migration boundaries."),
]


def identity_bearer_rows() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "identity_bearer_archetype",
            "archetype_id": f"archetype.identity.{name}.v1",
            "meaning": meaning,
            "required_coordinate_ref": "ontology.semantic-axis.identity-equality-coordinate.v1#identity_coordinate",
            "applicability": "UNRESOLVED_PER_SUBJECT_RELATION_AND_USE_SITE",
            "completion_claim": False,
        }
        for name, meaning in IDENTITY_BEARER_ARCHETYPES
    ]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.identity-equality-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "identity_and_equality",
    "domain_question": "Which subject occurrence is designated under which namespace, allocation and lifecycle contract, and under which explicitly named relation may two subjects, values, terms, representations or observations be considered equal or equivalent?",
    "coordinate_key": [
        "bounded_context_ref", "subject_kind_ref", "subject_ref", "identity_relation_ref",
        "relation_edition_ref", "lifecycle_scope_ref", "use_site_ref",
    ],
    "identity_coordinate": {
        "required_fields": [
            "identity_bearer_archetype_ref",
            "identifier_carrier_syntax_and_scheme",
            "namespace_issuer_and_allocation_authority",
            "uniqueness_scope_and_collision_model",
            "allocation_reassignment_and_reuse_policy",
            "lifecycle_persistence_and_tombstone_policy",
            "reference_resolution_and_dereference_contract",
            "equality_or_equivalence_relation_ref",
            "comparison_normalization_and_locale_profile",
            "relation_law_profile",
            "null_missing_unknown_and_invalid_policy",
            "version_specialization_alias_and_successor_relations",
            "merge_split_rekey_and_conflict_policy",
            "canonicalization_digest_and_domain_separation",
            "provenance_authority_privacy_and_disclosure",
            "conformance_oracle_and_negative_twins",
        ],
        "identity_relation_kinds": [
            "same_lifecycle_occurrence", "same_scoped_identifier", "same_reference_target",
            "term_equality", "literal_or_typed_value_equality", "structural_equality",
            "canonical_representation_equality", "digest_equality", "comparator_equivalence",
            "semantic_equivalence", "observational_or_behavioral_equivalence", "graph_isomorphism",
            "approximate_or_tolerance_relation", "domain_match_candidate", "adjudicated_same_entity",
            "alias_or_resolution_relation", "version_successor", "specialization_or_alternate",
            "explicit_difference", "indeterminate_or_unresolved",
        ],
        "law_verdicts": ["HOLDS", "CONDITIONAL", "DOES_NOT_HOLD", "UNDEFINED", "UNRESOLVED"],
        "relation_laws": [
            "reflexivity", "symmetry", "transitivity", "substitutivity", "congruence",
            "stability_across_time", "stability_across_representation", "decidability",
            "totality", "collision_resistance_assumption", "information_preservation",
        ],
        "outcomes": [
            "equal", "not_equal", "equivalent_not_identical", "possible_match", "same_as_adjudicated",
            "different_as_adjudicated", "ambiguous", "unresolved", "invalid_identifier",
            "unknown_namespace", "resolution_failed", "collision_detected", "refused",
        ],
    },
    "dependency_axis_refs": [
        "semantic_object", "grain_and_cardinality", "state_and_change", "time",
        "order_and_topology", "partiality_and_uncertainty", "authority_and_trust",
        "representation", "composition_algebra", "compatibility_and_evolution",
        "privacy_security_safety", "evidence_and_conformance",
    ],
    "discovery_projection_compatibility": {
        "existing_facets": ["opaque_identity", "occurrence_identity", "value_equality", "canonical_equivalence", "content_addressed", "versioned_identity"],
        "status": "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY",
        "prohibition": "A facet or identifier-like suffix cannot select a subject, namespace, lifecycle, equality relation, law profile, authority, applicability or exact contract.",
    },
    "non_collapse_laws": [
        "identifier carrier is not the identified subject or proof that the subject exists",
        "name is not lifecycle occurrence identity and may be reused",
        "same value is not same occurrence and same occurrence can change value",
        "term equality is not typed value equality semantic equivalence or real-world identity",
        "canonical representation equality is not semantic identity authority or correctness",
        "digest equality is algorithm domain and collision-assumption scoped",
        "different bytes do not necessarily imply different semantic values",
        "key uniqueness is not completeness existence authenticity or global identity",
        "alias resolution is not equality and can be directional time-bounded or ambiguous",
        "version succession is not equality substitutability or backward compatibility",
        "field identity is not field name position or value equality",
        "blank-node labels are not portable cross-graph identifiers",
        "graph isomorphism is not identity of described real-world subjects",
        "equal model outputs on sampled inputs do not prove model or behavioral identity",
        "equal objective values do not identify the same solution assignment",
        "entity-resolution similarity is not an identity decision or authority to merge",
        "merge and split are governed identity events not ordinary set operations",
        "approximate equality need not be transitive and cannot serve as an identity key by default",
        "normalization relation and version must be explicit; compatibility normalization may lose distinctions",
        "a handle or token can carry authority without being the subject's semantic identity",
    ],
    "primary_source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decision": "UNRESOLVED",
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


KERNEL_DEFINITIONS = [
    ("mint_scoped_identifier", "identifier_namespace", "namespace and allocation request", "new identifier or collision/refusal", "Uniqueness depends on namespace, allocator and reuse policy."),
    ("parse_and_validate_identifier", "identifier_scheme_or_edition", "identifier carrier", "typed identifier or syntax refusal", "Syntactic validity does not prove allocation, existence or authority."),
    ("qualify_identifier", "identifier_namespace", "short name and scope", "qualified identifier", "Qualification changes reference scope and does not prove target existence."),
    ("resolve_reference", "reference_or_locator", "reference and resolver context", "target candidate or resolution failure", "Resolution is time, authority and resolver scoped and is not equality."),
    ("dereference_handle", "handle_token_or_capability", "runtime handle and authority context", "resource access or refusal", "A usable handle does not establish stable semantic identity or transferable authority."),
    ("allocate_occurrence_uid", "lifecycle_occurrence_identifier", "creation event and authority", "historical occurrence identity", "A reusable name and a new occurrence UID must not be conflated."),
    ("reuse_scoped_name", "scoped_name", "tombstoned name and new creation", "new occurrence under old name", "Name continuity does not preserve occurrence, leases, receipts or authority."),
    ("rename_preserving_subject", "alias_or_historical_name", "subject plus old/new name", "renamed subject and alias history", "Rename preservation requires a stable subject identity; equal names alone do not supply it."),
    ("add_or_resolve_alias", "alias_or_historical_name", "alias relation", "resolved subject(s) or ambiguity", "Aliases can be many-to-one, time-bounded or conflicting and are not symmetric equality."),
    ("rekey_subject", "natural_or_business_key", "subject and old/new key", "rekey event plus mappings", "Key change need not create a new subject but requires collision and history rules."),
    ("compose_key", "composite_key", "positioned key components", "composite key or invalidity", "Component order, nulls, normalization and delimiter/encoding must be unambiguous."),
    ("enforce_key_uniqueness", "natural_or_business_key", "key observations in declared scope", "accepted uniqueness or conflict", "Observed uniqueness does not prove population completeness or global uniqueness."),
    ("version_successor", "version_or_edition_identifier", "prior and next editions", "successor relation", "Succession is directional and does not imply semantic equality or substitutability."),
    ("specialize_or_alternate", "domain_entity_or_aggregate", "two contextual views", "qualified specialization/alternate relation", "Contextual specialization is not same bytes, exact equality or unrestricted substitution."),
    ("field_rename_preserve_id", "schema_member_or_field_identifier", "schema member and new label", "same field ID with renamed label", "Stable field identity does not make old/new values or schemas fully compatible."),
    ("rdf_term_equal", "graph_node_or_iri", "two RDF terms", "term equality verdict", "Term equality differs from value equality, entailment and real-world identity."),
    ("typed_value_equal", "value_semantic_identity", "two typed values", "value equality or invalid/unknown", "Equal values can have different lexical forms and equality depends on datatype semantics."),
    ("structural_equal", "canonical_representation", "two structured values", "structural equality verdict", "Field order, omitted/default values, aliases and semantic equivalence require explicit treatment."),
    ("unicode_normalize", "canonical_representation", "Unicode string plus normalization form/version", "normalized string", "NFC and NFKC preserve different distinctions and neither establishes domain equality."),
    ("json_canonicalize", "canonical_representation", "JCS-admissible JSON", "canonical bytes or refusal", "Canonical bytes are representation evidence, not domain identity."),
    ("compute_domain_separated_digest", "content_digest_or_fingerprint", "bytes, algorithm and domain tag", "digest", "Digest meaning is scoped to exact bytes, algorithm, canonicalization and domain separation."),
    ("verify_digest", "content_digest_or_fingerprint", "claimed digest and bytes", "match/mismatch/unsupported", "Digest verification proves byte agreement under assumptions, not authorship, safety or semantic truth."),
    ("content_address", "content_digest_or_fingerprint", "canonical or raw content", "content address", "A content address identifies content under a scheme, not a mutable subject or authority."),
    ("graph_isomorphism", "blank_or_local_node", "two RDF graphs", "isomorphic/not-isomorphic", "Graph isomorphism abstracts blank-node labels but not real-world identity or entailment equivalence."),
    ("assert_same_individual", "domain_entity_or_aggregate", "two individual designations plus authority", "same-individual assertion", "An assertion is not automatically accepted truth or operational merge authority."),
    ("assert_different_individuals", "domain_entity_or_aggregate", "two individual designations plus authority", "difference assertion", "Difference is context/evidence scoped and must not be inferred from unequal identifiers alone."),
    ("compare_by_collation", "value_semantic_identity", "strings plus locale/collation/strength", "comparison equivalence class", "Collation equivalence is profile-specific and need not be suitable for identity."),
    ("approximate_compare", "value_semantic_identity", "values plus metric/tolerance", "within/outside/indeterminate", "Tolerance relations may be non-transitive and cannot silently define keys or deduplication."),
    ("semantic_equivalence_check", "domain_entity_or_aggregate", "two meanings and proof profile", "equivalent/non-equivalent/unresolved", "Semantic equivalence is bounded by theory, context and observables and is not occurrence identity."),
    ("behavioral_equivalence_test", "model_plan_or_artifact", "artifacts, input domain and observations", "bounded behavioral verdict", "Sampled equal outputs do not prove universal equivalence or shared lineage."),
    ("join_key_match", "natural_or_business_key", "left/right keys and comparison profile", "match/nonmatch/unknown", "A key match is a join predicate result, not necessarily entity identity."),
    ("deduplicate_by_relation", "entity_resolution_cluster", "occurrences and equality/match relation", "representatives plus residual mapping", "Deduplication depends on an explicit relation and can lose occurrence evidence."),
    ("propose_entity_match", "entity_resolution_cluster", "records, features and model/rules", "candidate with confidence and evidence", "A candidate or score is not an identity decision."),
    ("adjudicate_entity_identity", "entity_resolution_cluster", "candidates, evidence and authority", "accepted/rejected/unresolved identity decision", "Acceptance is authority and evidence scoped and must preserve dissent and reversibility."),
    ("merge_entity_identities", "domain_entity_or_aggregate", "two subjects and merge authority", "survivor, retired identities and merge receipt", "Merge is a lifecycle event; it is not set union and may require later split."),
    ("split_entity_identity", "domain_entity_or_aggregate", "merged subject, evidence and split authority", "new/rehabilitated identities plus redistribution receipt", "Split must allocate facts, history and references without pretending the prior merge never occurred."),
    ("pseudonymize_identifier", "external_resource_occurrence", "identifier, secret/context and policy", "pseudonymized carrier", "Pseudonymization changes disclosure/linkability, not necessarily underlying subject identity."),
    ("redact_identity_carrier", "event_observation_or_claim", "record and disclosure policy", "redacted representation", "Removing an identifier does not necessarily remove re-identification risk or subject linkage."),
    ("migrate_identity_mapping", "identifier_namespace", "source/target namespaces and mapping evidence", "directional mapping plus residuals", "Migration mapping can be partial, non-injective or time-bounded and is not universal equality."),
    ("compare_solution_assignment", "solution_or_assignment", "two variable assignments and model edition", "assignment equality/equivalence", "Equal objective values or status do not make assignments identical."),
    ("compare_model_identity", "model_plan_or_artifact", "definitions, learned state, lineage and edition", "identity/equivalence verdict", "Same architecture, bytes, name or outputs each answer different questions."),
    ("map_symbol_anchor", "symbol_variable_or_anchor", "local symbol and enclosing scope", "qualified symbol reference", "Numeric anchors and short names are local and cannot be promoted to global identity."),
]


def identity_kernel_rows() -> list[dict[str, Any]]:
    source_refs = [row["source_id"] for row in PRIMARY_SOURCES]
    return [
        {
            "record_kind": "identity_equality_kernel",
            "kernel_id": f"kernel.identity-equality.{name}.v1",
            "identity_bearer_archetype_ref": f"archetype.identity.{archetype}.v1",
            "input_contract": input_contract,
            "output_contract": output_contract,
            "required_coordinate_fields": ONTOLOGY["identity_coordinate"]["required_fields"],
            "negative_twin": negative_twin,
            "bounded_primary_source_refs": source_refs,
            "applicability": "UNRESOLVED_PER_SUBJECT_RELATION_AND_USE_SITE",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for name, archetype, input_contract, output_contract, negative_twin in KERNEL_DEFINITIONS
    ]


def route_for_facets(facets: tuple[str, ...]) -> str:
    return (
        "LEXICAL_DISCOVERY_PROJECTION_ONLY_IDENTITY_RELATION_RESEARCH_REQUIRED"
        if facets
        else "NO_MEMBER_IDENTITY_RELATION_EVIDENCE_VACANCY"
    )


def build() -> dict[str, Any]:
    rebase = build_member_rebase(
        axis="identity_and_equality",
        dockets_path=P3I_DOCKETS,
        preclassifications_path=PRECLASSIFICATIONS,
        cluster_prefix="cluster.p3i.identity-equality-rebase",
        cluster_route=route_for_facets,
    )
    clusters = [
        {
            "record_kind": "identity_equality_member_research_cluster",
            **row,
            "required_next_evidence": [
                "authoritative subject kind namespace scheme and allocation inventory",
                "lifecycle occurrence version alias and resolution contracts",
                "named equality/equivalence relations and per-relation law profiles",
                "canonicalization digest merge split and migration boundaries",
                "authority privacy provenance counterexamples and conformance oracles",
            ],
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for row in rebase["clusters"]
    ]
    members = [
        {
            "record_kind": "identity_equality_member_research_route",
            "route_id": f"route.p3i.identity-equality.{row['library_ref'].removeprefix('library.').replace('.', '-').replace('_', '-')}",
            **row,
            "flat_projection_effect": "DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY",
            "required_subject_and_identifier_inventory": "NOT_YET_SUPPLIED",
            "required_identity_and_equality_relation_profiles": "NOT_YET_SUPPLIED",
            "required_lifecycle_merge_split_and_alias_contracts": "NOT_YET_SUPPLIED",
            "required_authority_privacy_and_conformance_contracts": "NOT_YET_SUPPLIED",
            "member_applicability": "UNRESOLVED",
            "owner_decision": "UNRESOLVED",
            "canonical_gaps_closed": 0,
            "status": "LOSSLESSLY_ROUTED_RESEARCH_OPEN",
            "completion_claim": False,
        }
        for row in rebase["members"]
    ]
    extensions = []
    for family_ref, docket in sorted(rebase["docket_by_family"].items()):
        short = family_ref.removeprefix("constitution.family.")
        extensions.append(
            {
                "record_kind": "identity_equality_exact_contract_extension_candidate",
                "extension_id": f"extension.p3i.identity-equality-coordinate.{short}.v1",
                "family_ref": family_ref,
                "family_evidence_docket_ref": docket["docket_id"],
                "represented_library_refs": docket["library_refs"],
                "represented_library_count": docket["library_count"],
                "required_record_kinds": [
                    "subject_identity_inventory", "identifier_namespace_contract",
                    "identity_equality_relation_profile", "alias_merge_split_history_contract",
                    "canonicalization_digest_contract", "identity_conformance_oracle",
                ],
                "owner_decision": "UNRESOLVED",
                "member_applicability_decisions": 0,
                "canonical_gaps_closed": 0,
                "status": "CANDIDATE_UNRATIFIED",
                "completion_claim": False,
            }
        )
    kernels = identity_kernel_rows()
    summary = {
        "program_id": "program.p3i.identity-equality-coordinate-ontology-and-rebase.v1",
        "as_of": AS_OF,
        "axis": "identity_and_equality",
        "primary_sources": len(PRIMARY_SOURCES),
        "identity_bearer_archetypes": len(IDENTITY_BEARER_ARCHETYPES),
        "identity_equality_kernels": len(kernels),
        "family_extension_candidates": len(extensions),
        "research_clusters": len(clusters),
        "target_member_routes": len(members),
        "routes_with_lexical_discovery_projection": rebase["lexical_member_count"],
        "routes_with_no_member_identity_relation_evidence": rebase["vacancy_member_count"],
        "subject_identity_inventories_supplied": 0,
        "identity_equality_relation_profiles_supplied": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "archetypes": identity_bearer_rows(),
        "kernels": kernels,
        "clusters": clusters,
        "members": members,
        "extensions": extensions,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "identity-equality-coordinate-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "identity-bearer-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["archetypes"]),
        "identity-equality-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["kernels"]),
        "member-research-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "member-identity-routes.jsonl": "".join(canonical(row) + "\n" for row in built["members"]),
        "extension-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["extensions"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.p3i.identity-equality-coordinate-ontology-and-rebase.v1",
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
        "BUILD PASS P3I identity/equality coordinate ontology: "
        f"{summary['identity_bearer_archetypes']} bearer archetypes, "
        f"{summary['identity_equality_kernels']} kernels, {summary['research_clusters']} clusters "
        f"and {summary['target_member_routes']} exact routes; decisions and gap closure remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
