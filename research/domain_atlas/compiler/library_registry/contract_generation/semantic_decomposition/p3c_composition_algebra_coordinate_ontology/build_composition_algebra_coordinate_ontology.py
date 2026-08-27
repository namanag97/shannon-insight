#!/usr/bin/env python3
"""Build an operator-positioned composition/algebra ontology and lossless P3C rebase."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"
P3C_DOCKETS = SEM / "p3c_composition_algebra_evidence/family-evidence-dockets.jsonl"
PRECLASSIFICATIONS = SEM / "applicability_matrices/member-preclassifications.jsonl"
sys.path.insert(0, str(SEM))

from member_axis_rebase import build_member_rebase  # noqa: E402


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


PRIMARY_SOURCES = [
    {
        "source_id": "source.composition.xacml-3",
        "title": "eXtensible Access Control Markup Language (XACML) Version 3.0",
        "publisher": "OASIS",
        "url": "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html",
        "bounded_implication": "Policy and rule results compose under named, non-interchangeable combining algorithms that preserve Permit, Deny, NotApplicable and extended Indeterminate outcomes and may be order-sensitive.",
        "authority_limit": "XACML does not make policy combination a universal Boolean algebra, prove obligations were executed or authorize effects outside its policy-decision boundary.",
    },
    {
        "source_id": "source.composition.json-schema-2020-12",
        "title": "JSON Schema Core and Applicator Vocabulary, Draft 2020-12",
        "publisher": "JSON Schema",
        "url": "https://json-schema.org/draft/2020-12/json-schema-core.html",
        "bounded_implication": "Applicators apply subschemas and combine assertion and annotation results under keyword-specific rules; allOf, anyOf and oneOf are distinct and are not object or data merge operators.",
        "authority_limit": "JSON Schema constrains validation evaluation, not arbitrary data reconciliation, inheritance, mutation or semantic compatibility.",
    },
    {
        "source_id": "source.composition.substrait-relations",
        "title": "Substrait Logical Relations",
        "publisher": "Substrait",
        "url": "https://substrait.io/relations/logical_relations/",
        "bounded_implication": "Join, set, aggregate, reference and write relations have different arity, multiplicity, schema, orderedness, distribution and effect contracts.",
        "authority_limit": "A type-correct relational plan does not establish domain join meaning, business acceptance, authorization or preservation of every physical property.",
    },
    {
        "source_id": "source.composition.beam-programming-guide",
        "title": "Apache Beam Programming Guide",
        "publisher": "Apache Beam",
        "url": "https://beam.apache.org/documentation/programming-guide/",
        "bounded_implication": "Composite transforms form dataflow graphs; multi-input flattening and combination remain constrained by element types, coders, windows and triggers rather than generic concatenation.",
        "authority_limit": "Beam composition does not make transforms reorderable, external effects atomic or runner behavior universally equivalent.",
    },
    {
        "source_id": "source.composition.kubernetes-ssa",
        "title": "Kubernetes Server-Side Apply",
        "publisher": "Kubernetes",
        "url": "https://kubernetes.io/docs/reference/using-api/server-side-apply/",
        "bounded_implication": "Declarative object fragments merge according to schema-declared atomic, set, map and granular topologies while field ownership creates explicit conflict or forced-transfer outcomes.",
        "authority_limit": "Forced ownership transfer is not proof of semantic safety, downstream compatibility or successful reconciliation of external effects.",
    },
    {
        "source_id": "source.composition.rfc7386",
        "title": "RFC 7386: JSON Merge Patch",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc7386.html",
        "bounded_implication": "Merge Patch recursively overlays object members, replaces non-object targets and gives null deletion semantics; it is unsuitable for some JSON structures and explicit-null domains.",
        "authority_limit": "Merge Patch does not define a general semantic merge, conflict-free replicated datatype, authorization decision or reversible edit algebra.",
    },
    {
        "source_id": "source.composition.rfc6902",
        "title": "RFC 6902: JavaScript Object Notation (JSON) Patch",
        "publisher": "IETF / RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc6902.html",
        "bounded_implication": "JSON Patch is an ordered sequence of typed operations with path, test and failure behavior; reordering operations can change or invalidate the result.",
        "authority_limit": "Syntactic patch application does not establish domain validity, conflict resolution, compensation or authority to mutate the target.",
    },
    {
        "source_id": "source.composition.rdf11-concepts",
        "title": "RDF 1.1 Concepts and Abstract Syntax",
        "publisher": "W3C",
        "url": "https://www.w3.org/TR/rdf11-concepts/",
        "bounded_implication": "RDF graph merge is set union after standardizing blank nodes from different graphs apart; graph merge, dataset composition and concrete serialization are distinct.",
        "authority_limit": "RDF merge does not resolve contradictory claims, merge real-world identities, prove truth or transfer graph authority.",
    },
    {
        "source_id": "source.composition.iceberg-spec",
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "bounded_implication": "Table state composes through optimistic snapshot commits, manifest structures and sequence-scoped data/delete application with operation-specific conflict behavior.",
        "authority_limit": "File or snapshot composition does not create one cross-table business transaction or make every concurrent mutation commutative.",
    },
    {
        "source_id": "source.composition.onnx-ir",
        "title": "ONNX Intermediate Representation Specification",
        "publisher": "ONNX",
        "url": "https://onnx.ai/onnx/repo-docs/IR.html",
        "bounded_implication": "Computation graphs and function expansions require typed operator bindings, acyclic dependencies, namespace uniqueness and SSA output-name discipline.",
        "authority_limit": "Tensor-shape compatibility does not establish calibration, distribution, predictive validity, behavioral substitutability or effect safety.",
    },
]


OPERATOR_ARCHETYPES = [
    ("pure_unary_transform", "One semantic input is transformed without an authorized external effect."),
    ("pure_binary_operator", "Two positioned operands produce one result under an explicit operand order and law profile."),
    ("nary_fold_or_reduce", "A collection is folded under a declared operator, seed/identity and evaluation strategy."),
    ("ordered_sequence", "Child computations or edits execute in a semantically significant order."),
    ("exclusive_or_conditional_choice", "Exactly one or a bounded subset of alternatives is selected by guards or applicability."),
    ("parallel_or_concurrent_fanout", "Branches may progress concurrently with an explicit join, cancellation and effect policy."),
    ("race_or_first_completion", "One completion is selected while loser cancellation and partial effects remain explicit."),
    ("constraint_combiner", "Constraints compose by conjunction, disjunction, exclusivity or another declared satisfaction rule."),
    ("multivalued_policy_combiner", "Non-Boolean policy results combine under precedence and indeterminate-propagation rules."),
    ("set_operator", "Distinct members combine under union, intersection, difference or symmetric difference."),
    ("bag_or_multiset_operator", "Member multiplicity participates in the operation and result."),
    ("sequence_concatenation_or_merge", "Ordered sequences combine by concatenation or comparator-governed merge."),
    ("relational_join_or_set_relation", "Relations combine with explicit key, match, null, multiplicity and output-schema rules."),
    ("group_aggregate", "Occurrences partition into groups and measures combine under aggregation and empty-input laws."),
    ("graph_or_ontology_merge", "Statements or axioms combine with node-identity, namespace and consistency obligations."),
    ("schema_or_shape_applicator", "Schemas or shapes apply and combine validation plus annotation outcomes."),
    ("structural_overlay_merge", "A patch or fragment overlays a target using field topology, deletion and ownership rules."),
    ("ordered_patch_program", "A sequence of edits transforms one representation with path preconditions and failure semantics."),
    ("state_transition_composition", "Transitions compose only when post-state, pre-state and invariant boundaries align."),
    ("transactional_bundle", "Several supported effects commit or abort under a declared atomicity and isolation scope."),
    ("compensating_process", "Forward steps and compensations form a long-running process without pretending compensation is rollback."),
    ("fixed_point_or_iteration", "An operator repeats until a declared convergence, termination or budget condition."),
    ("optimization_model_assembly", "Variables, constraints and objectives assemble into one decision model under units and priority rules."),
    ("metric_or_formula_expression", "Measures compose through typed arithmetic, filters, grain, units, windows and missingness rules."),
    ("evidence_or_argument_composition", "Claims and evidence combine under an argument/appraisal rule that preserves uncertainty and defeaters."),
    ("probabilistic_or_model_combiner", "Models or distributions combine under calibration, dependence and uncertainty assumptions."),
    ("interface_or_component_linkage", "Imports, exports, names, types, capabilities and resource ownership are linked across components."),
    ("external_effect_orchestration", "Commands or tools compose across authority, idempotency, partial effect, receipt and recovery boundaries."),
]


def operator_archetype_rows() -> list[dict[str, Any]]:
    return [
        {
            "record_kind": "composition_operator_archetype",
            "archetype_id": f"archetype.composition.{name}.v1",
            "meaning": meaning,
            "required_coordinate_ref": "ontology.semantic-axis.composition-algebra-coordinate.v1#operator_coordinate",
            "applicability": "UNRESOLVED_PER_OPERATOR_AND_USE_SITE",
            "completion_claim": False,
        }
        for name, meaning in OPERATOR_ARCHETYPES
    ]


ONTOLOGY = {
    "ontology_id": "ontology.semantic-axis.composition-algebra-coordinate.v1",
    "edition": 1,
    "as_of": AS_OF,
    "axis": "composition_algebra",
    "domain_question": "At each exact use site, which positioned operands over which carrier and semantic domain compose under which operator, laws, failure/precedence, information-loss, state/effect, authority and proof contract?",
    "coordinate_key": [
        "bounded_context_ref",
        "operator_ref",
        "operator_edition_ref",
        "use_site_ref",
        "operand_position_refs",
        "result_position_ref",
    ],
    "operator_coordinate": {
        "required_fields": [
            "operator_archetype_ref",
            "carrier_and_semantic_domain_refs",
            "arity_and_operand_roles",
            "operand_type_grain_order_and_compatibility",
            "result_type_grain_and_semantic_role",
            "admissibility_closure_and_partiality",
            "identity_zero_absorber_and_inverse_profile",
            "algebraic_law_profile",
            "precedence_conflict_and_tie_policy",
            "determinism_evaluation_order_and_concurrency",
            "state_effect_authority_and_receipt_boundary",
            "information_preservation_loss_and_provenance",
            "version_migration_and_extension_policy",
            "resource_termination_and_cancellation_bounds",
            "conformance_oracle_and_negative_twins",
        ],
        "law_verdicts": ["HOLDS", "CONDITIONAL", "DOES_NOT_HOLD", "UNDEFINED", "UNRESOLVED"],
        "algebraic_laws": [
            "closure", "associativity", "commutativity", "idempotence", "identity",
            "zero_or_absorber", "inverse_or_residual", "distributivity", "monotonicity",
            "inflationary_or_deflationary", "determinism", "order_sensitivity", "confluence",
            "termination", "reversibility", "losslessness",
        ],
        "partiality_and_conflict_outcomes": [
            "success", "not_applicable", "indeterminate", "incompatible_operands",
            "precondition_failed", "conflict", "ambiguous", "infeasible", "non_convergent",
            "resource_exhausted", "cancelled", "partial_effect", "compensation_required", "refused",
        ],
        "effect_scopes": [
            "pure_value", "representation_only", "local_state", "single_transaction",
            "single_log_or_store", "multi_resource_process", "authorized_external_effect", "unknown",
        ],
    },
    "dependency_axis_refs": [
        "semantic_object", "identity_and_equality", "grain_and_cardinality", "state_and_change",
        "order_and_topology", "time", "partiality_and_uncertainty", "authority_and_policy",
        "effect_and_execution", "failure_and_recovery", "representation", "compatibility_and_evolution",
        "resources_and_bounds", "evidence_and_conformance",
    ],
    "discovery_projection_compatibility": {
        "status": "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY",
        "prohibition": "A lexical composition facet cannot select an operator, carrier, operand roles, laws, conflict precedence, effect scope, authority, applicability or exact contract.",
    },
    "non_collapse_laws": [
        "merge is not union join overlay patch or reconciliation",
        "set bag sequence relation graph and state composition are not interchangeable",
        "schema or shape conjunction is not data merge inheritance or repair",
        "policy combination is not ordinary Boolean folding",
        "parallel declaration is not commutativity confluence atomicity or effect safety",
        "type compatibility is not semantic behavioral calibration or lifecycle compatibility",
        "transactional atomicity is bounded and is not a universal distributed transaction",
        "compensation is not rollback inverse or erasure of an irreversible effect",
        "idempotent invocation is not exactly-once effect",
        "optimistic commit is not conflict-free composition",
        "constraint conjunction is not objective aggregation or preference adjudication",
        "evidence aggregation is not truth acceptance authorization or execution",
        "fixed-point notation does not prove convergence termination uniqueness or resource boundedness",
        "interface linkage does not prove behavioral substitutability or resource ownership compatibility",
        "graph merge does not resolve entity identity contradictory assertions or authority",
        "an associative law in one carrier or precondition set does not transfer to a homonymous operator",
    ],
    "primary_source_refs": [row["source_id"] for row in PRIMARY_SOURCES],
    "owner_decision": "UNRESOLVED",
    "member_applicability_decisions": 0,
    "canonical_gaps_closed": 0,
    "completion_claim": False,
}


KERNEL_DEFINITIONS = [
    ("function_compose", "pure_unary_transform", "typed output-to-input binding", "composed pure transform", "Composition is partial when types, semantics or effects do not align."),
    ("ordered_sequence", "ordered_sequence", "ordered child operations", "last result plus intermediate obligations", "Sequence is not commutative and earlier effects may survive later refusal."),
    ("exclusive_choice", "exclusive_or_conditional_choice", "guards and alternatives", "one selected branch or ambiguity/refusal", "Exclusive choice is not set union or first-applicable without a declared rule."),
    ("parallel_join_all", "parallel_or_concurrent_fanout", "independent branches", "joined outcomes under an all policy", "Concurrency does not imply independence, confluence or safe cancellation."),
    ("race_first_completion", "race_or_first_completion", "concurrent alternatives", "winner plus loser disposition", "First completion is not best result and losing effects do not vanish."),
    ("boolean_all", "constraint_combiner", "Boolean or multivalued predicates", "conjunctive satisfaction", "Short-circuit evaluation must not erase required evidence or effects."),
    ("boolean_any", "constraint_combiner", "Boolean or multivalued predicates", "disjunctive satisfaction", "Any-of is not exclusive choice and may require all annotations/evidence."),
    ("exactly_one", "constraint_combiner", "candidate outcomes", "one-of satisfaction or ambiguity", "Exactly-one differs from any-of even when one branch currently succeeds."),
    ("deny_overrides", "multivalued_policy_combiner", "policy decisions", "precedence-combined decision", "Deny, Permit, NotApplicable and Indeterminate cannot be collapsed to Boolean values."),
    ("permit_overrides", "multivalued_policy_combiner", "policy decisions", "precedence-combined decision", "Permit-overrides is not deny-overrides and obligation execution remains separate."),
    ("first_applicable", "multivalued_policy_combiner", "ordered policy decisions", "first applicable result", "Reordering policies may change the result."),
    ("only_one_applicable", "multivalued_policy_combiner", "policy applicability outcomes", "single result or indeterminate", "Multiple applicable policies are not resolved by arbitrary precedence."),
    ("set_union", "set_operator", "sets under one equality", "distinct-member union", "Set union removes multiplicity and does not preserve sequence order."),
    ("set_intersection", "set_operator", "sets under one equality", "common distinct members", "Intersection does not reconcile unequal representations or identities."),
    ("set_difference", "set_operator", "primary and subtracting sets", "directional remainder", "Difference is directional, non-commutative and equality-dependent."),
    ("bag_union_or_sum", "bag_or_multiset_operator", "bags under one equality", "multiplicity-preserving combination", "Bag union/sum is not set union or sequence concatenation."),
    ("sequence_concatenate", "sequence_concatenation_or_merge", "ordered sequences", "operand-ordered concatenation", "Concatenation is not sorted merge, event-time merge or reconciliation."),
    ("sorted_merge", "sequence_concatenation_or_merge", "sequences under one comparator", "merged ordered sequence", "Local ordering is insufficient when comparators, nulls or ties differ."),
    ("relational_join", "relational_join_or_set_relation", "left/right relations plus match predicate", "matched relation with declared multiplicity", "Join is not union and matching keys do not prove domain identity."),
    ("relational_set_operation", "relational_join_or_set_relation", "schema-compatible relations", "operator-specific relation", "Distinct/all variants have different duplicate and null behavior."),
    ("group_fold", "group_aggregate", "occurrences, grouping key and aggregate", "one result per group", "Aggregation laws depend on empty inputs, nulls, order and decomposability."),
    ("rdf_graph_merge", "graph_or_ontology_merge", "RDF graphs", "set union after blank-node separation", "Blank node labels do not create cross-graph identity."),
    ("ontology_import_closure", "graph_or_ontology_merge", "versioned ontology imports", "transitive axiom closure", "Import is not endorsement and inconsistent versions need not compose."),
    ("schema_all_of", "schema_or_shape_applicator", "subschemas", "conjunctive validation plus annotations", "allOf is not object inheritance or data merge."),
    ("schema_any_or_one_of", "schema_or_shape_applicator", "subschemas", "keyword-specific validation outcome", "anyOf and oneOf are not interchangeable and annotations complicate short circuiting."),
    ("structural_merge_patch", "structural_overlay_merge", "target and merge patch", "recursively overlaid JSON value", "Null deletion and array replacement make this unsuitable as a universal merge."),
    ("schema_directed_field_merge", "structural_overlay_merge", "owned object fragments plus schema", "merged object or ownership conflict", "Atomic, set, map and granular fields have different merge laws."),
    ("ordered_json_patch", "ordered_patch_program", "target plus ordered edit list", "transformed target or failed operation", "Patch operations are not generally reorderable, commutative or reversible."),
    ("transition_chain", "state_transition_composition", "compatible before/after states", "composite transition or refusal", "Matching carrier types do not prove invariant-compatible state composition."),
    ("atomic_transaction_bundle", "transactional_bundle", "effects inside one transaction domain", "commit or abort receipt", "Atomicity does not extend to unsupported stores or arbitrary external effects."),
    ("consume_transform_produce", "transactional_bundle", "log input offsets and output records", "atomic log transaction", "Log atomicity does not make all downstream effects exactly once."),
    ("saga_with_compensation", "compensating_process", "forward actions and compensation policy", "completed or compensated process record", "Compensation can fail and cannot undo all irreversible effects."),
    ("least_or_greatest_fixed_point", "fixed_point_or_iteration", "ordered domain and monotone operator assumptions", "fixed point or non-convergence", "Iteration alone proves neither monotonicity, uniqueness nor termination."),
    ("constraint_model_assembly", "optimization_model_assembly", "variables and constraints", "feasibility model", "Encoding conjunction does not prove world validity or feasibility."),
    ("multiobjective_composition", "optimization_model_assembly", "typed objectives and preference policy", "scalarized or partially ordered objective", "Adding scores without units and priority does not create a valid objective."),
    ("typed_metric_expression", "metric_or_formula_expression", "measures, dimensions, grain, units and filters", "derived metric", "Executable arithmetic does not prove semantic compatibility or denominator validity."),
    ("evidence_conjunction_or_argument", "evidence_or_argument_composition", "claims, evidence and defeaters", "argument/appraisal state", "More evidence does not monotonically imply truth, acceptance or authorization."),
    ("probabilistic_mixture_or_product", "probabilistic_or_model_combiner", "distributions/models plus dependence assumptions", "combined predictive object", "Matching output shapes do not establish calibration, independence or validity."),
    ("component_import_export_link", "interface_or_component_linkage", "typed imports and exports", "linked component graph or collision", "Name/type compatibility does not prove behavioral substitutability or shared resource safety."),
    ("authorized_effect_chain", "external_effect_orchestration", "commands, authorities and receipts", "process outcome with partial-effect record", "Tool chaining does not create shared authority, atomicity or safe compensation."),
    ("reconciliation_with_precedence", "structural_overlay_merge", "competing observations or records", "adjudicated result plus residuals", "Reconciliation is not last-writer-wins and must preserve conflict evidence and authority."),
]


def operator_kernel_rows() -> list[dict[str, Any]]:
    source_refs = [row["source_id"] for row in PRIMARY_SOURCES]
    return [
        {
            "record_kind": "composition_operator_kernel",
            "kernel_id": f"kernel.composition.{name}.v1",
            "operator_archetype_ref": f"archetype.composition.{archetype}.v1",
            "operand_contract": operand_contract,
            "result_contract": result_contract,
            "required_coordinate_fields": ONTOLOGY["operator_coordinate"]["required_fields"],
            "negative_twin": negative_twin,
            "bounded_primary_source_refs": source_refs,
            "applicability": "UNRESOLVED_PER_OPERATOR_AND_USE_SITE",
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        }
        for name, archetype, operand_contract, result_contract, negative_twin in KERNEL_DEFINITIONS
    ]


def route_for_facets(facets: tuple[str, ...]) -> str:
    return (
        "LEXICAL_DISCOVERY_PROJECTION_ONLY_OPERATOR_RESEARCH_REQUIRED"
        if facets
        else "NO_MEMBER_OPERATOR_EVIDENCE_VACANCY"
    )


def build() -> dict[str, Any]:
    rebase = build_member_rebase(
        axis="composition_algebra",
        dockets_path=P3C_DOCKETS,
        preclassifications_path=PRECLASSIFICATIONS,
        cluster_prefix="cluster.p3c.composition-algebra-rebase",
        cluster_route=route_for_facets,
    )
    clusters = [
        {
            "record_kind": "composition_member_research_cluster",
            **row,
            "required_next_evidence": [
                "authoritative per-use-site operator and operand inventory",
                "carrier semantic-domain arity type grain and order contracts",
                "law verdicts with preconditions and counterexamples",
                "conflict precedence partiality determinism and effect boundaries",
                "authority information-loss resource and conformance obligations",
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
            "record_kind": "composition_member_research_route",
            "route_id": f"route.p3c.composition-algebra.{row['library_ref'].removeprefix('library.').replace('.', '-').replace('_', '-')}",
            **row,
            "flat_projection_effect": "DISCOVERY_ROUTING_ONLY_NOT_APPLICABILITY",
            "required_operator_and_use_site_inventory": "NOT_YET_SUPPLIED",
            "required_operand_and_result_coordinate_profiles": "NOT_YET_SUPPLIED",
            "required_law_and_precondition_profiles": "NOT_YET_SUPPLIED",
            "required_effect_authority_and_proof_contracts": "NOT_YET_SUPPLIED",
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
                "record_kind": "composition_exact_contract_extension_candidate",
                "extension_id": f"extension.p3c.composition-algebra-coordinate.{short}.v1",
                "family_ref": family_ref,
                "family_evidence_docket_ref": docket["docket_id"],
                "represented_library_refs": docket["library_refs"],
                "represented_library_count": docket["library_count"],
                "required_record_kinds": [
                    "operator_use_site_inventory", "operand_result_coordinate",
                    "algebraic_law_profile", "conflict_precedence_contract",
                    "effect_authority_contract", "information_loss_contract", "composition_conformance_oracle",
                ],
                "owner_decision": "UNRESOLVED",
                "member_applicability_decisions": 0,
                "canonical_gaps_closed": 0,
                "status": "CANDIDATE_UNRATIFIED",
                "completion_claim": False,
            }
        )
    kernels = operator_kernel_rows()
    summary = {
        "program_id": "program.p3c.composition-algebra-coordinate-ontology-and-rebase.v1",
        "as_of": AS_OF,
        "axis": "composition_algebra",
        "primary_sources": len(PRIMARY_SOURCES),
        "operator_archetypes": len(OPERATOR_ARCHETYPES),
        "operator_kernels": len(kernels),
        "family_extension_candidates": len(extensions),
        "research_clusters": len(clusters),
        "target_member_routes": len(members),
        "routes_with_lexical_discovery_projection": rebase["lexical_member_count"],
        "routes_with_no_member_operator_evidence": rebase["vacancy_member_count"],
        "operator_use_site_inventories_supplied": 0,
        "operator_coordinate_profiles_supplied": 0,
        "member_applicability_decisions": 0,
        "owner_decisions": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {
        "ontology": ONTOLOGY,
        "sources": PRIMARY_SOURCES,
        "archetypes": operator_archetype_rows(),
        "kernels": kernels,
        "clusters": clusters,
        "members": members,
        "extensions": extensions,
        "summary": summary,
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "composition-algebra-coordinate-ontology.json": json.dumps(built["ontology"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "primary-sources.jsonl": "".join(canonical(row) + "\n" for row in built["sources"]),
        "operator-archetypes.jsonl": "".join(canonical(row) + "\n" for row in built["archetypes"]),
        "operator-kernels.jsonl": "".join(canonical(row) + "\n" for row in built["kernels"]),
        "member-research-clusters.jsonl": "".join(canonical(row) + "\n" for row in built["clusters"]),
        "member-composition-routes.jsonl": "".join(canonical(row) + "\n" for row in built["members"]),
        "extension-candidates.jsonl": "".join(canonical(row) + "\n" for row in built["extensions"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {
        name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.p3c.composition-algebra-coordinate-ontology-and-rebase.v1",
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
        "BUILD PASS P3C composition/algebra coordinate ontology: "
        f"{summary['operator_archetypes']} operator archetypes, {summary['operator_kernels']} kernels, "
        f"{summary['research_clusters']} clusters and {summary['target_member_routes']} exact routes; "
        "decisions and gap closure remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
