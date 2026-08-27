#!/usr/bin/env python3
"""Build bounded primary-evidence candidates for identity and equality."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
TARGETS = SEM / "structured_projection/targeted-evidence-work-packages.jsonl"
AS_OF = "2026-08-27"
sys.path.insert(0, str(SEM))

from axis_evidence_campaign import build_campaign, campaign_outputs, write_outputs  # noqa: E402


CLAIMS: dict[str, dict[str, Any]] = {
    "constitution.family.analytical_method_kernels": {
        "title": "Open Neural Network Exchange Intermediate Representation (ONNX IR) Specification",
        "publisher": "ONNX",
        "url": "https://onnx.ai/onnx/repo-docs/IR.html",
        "claim": "ONNX scopes several different identifiers: operator sets use a domain and version pair, functions use name/domain/overload in current IR versions, and node outputs obey graph-local single static assignment name uniqueness. These identifiers coexist with model semantics, under which deterministic inference is expected to produce the same output for the same input.",
        "coordinates": ["operator_set_identity", "function_identity", "graph_local_value_name", "model_state_identity", "behavioral_output_equality"],
        "limit": "ONNX specifies computation-model interchange. Its scoped names and version identifiers do not establish semantic equivalence of statistical methods, trained parameters, causal estimands, forecasts, process models or analytical findings, and equal outputs on sampled inputs do not prove model identity.",
        "negative": "matching operator names, graph names, model bytes or observed outputs makes two analytical methods, trained models and findings the same semantic object",
    },
    "constitution.family.query_compilation_execution": {
        "title": "Substrait Extensions",
        "publisher": "Substrait",
        "url": "https://substrait.io/extensions/",
        "claim": "Substrait gives each extension document an owner-qualified extension URN, references extension entities by URN plus name, and assigns non-negative anchor values inside plans. The reference therefore carries layered identity rather than treating a short function name or numeric anchor as globally sufficient.",
        "coordinates": ["extension_document_urn", "owner_namespace", "extension_entity_name", "plan_anchor", "function_signature_identity"],
        "limit": "Substrait identifies serialized extension references for relational plans. It does not prove two plans semantically equivalent, make two implementations behaviorally identical, define business entity identity, or make equal numeric anchors portable across unrelated plans.",
        "negative": "a short function name, numeric anchor, textual expression or matching output schema is a global semantic identity for a query operation or plan",
    },
    "constitution.family.runtime_resource_control": {
        "title": "Kubernetes Object Names and IDs",
        "publisher": "Kubernetes",
        "url": "https://kubernetes.io/docs/concepts/overview/working-with-objects/names/",
        "claim": "Kubernetes distinguishes a client-provided name, whose uniqueness is scoped by API group, resource type and namespace, from a system-generated UID that distinguishes historical object occurrences across the cluster lifetime. A deleted name may be reused while the replacement receives a distinct UID.",
        "coordinates": ["kind_scoped_name", "namespace_scope", "cluster_lifetime_uid", "historical_occurrence", "name_reuse_after_delete"],
        "limit": "Kubernetes defines identity for API objects in a cluster. It does not make a name, label, provider handle, process ID, lease token or resource specification interchangeable, and UID equality does not establish capability authority or desired/observed state equality.",
        "negative": "a reused resource name, equal desired specification or matching provider label identifies the same runtime occurrence and preserves its leases, receipts and authority",
    },
    "constitution.family.persistence_lakehouse": {
        "title": "Apache Iceberg Specification",
        "publisher": "Apache Iceberg",
        "url": "https://iceberg.apache.org/spec/",
        "claim": "Iceberg selects columns by stable field ID even when names and order change, permits multiple historical names to map to one field ID, and separately defines optional identifier fields whose equal values mean rows represent the same entity without requiring Iceberg itself to enforce row uniqueness.",
        "coordinates": ["stable_field_identity", "rename_independence", "name_mapping_alias", "row_identifier_value_equality", "uniqueness_enforcement_boundary"],
        "limit": "Iceberg defines table-format field identity and optional row-identifier semantics. It does not establish cross-table business identity, guarantee identifier uniqueness, equate snapshot identity with table equivalence, or make file path, row position and entity identity interchangeable.",
        "negative": "column names are column identity, equal row values guarantee one physical row, and equal schemas or file sets make snapshots and tables identical",
    },
    "constitution.family.representation_codec": {
        "title": "RFC 8785: JSON Canonicalization Scheme (JCS)",
        "publisher": "RFC Editor",
        "url": "https://www.rfc-editor.org/rfc/rfc8785.html",
        "claim": "JCS produces an invariant UTF-8 representation of I-JSON data by fixed primitive serialization and deterministic property sorting while preserving array order and string data without Unicode normalization. The canonical bytes support repeatable hashing and signing after application-level correctness checks.",
        "coordinates": ["parsed_json_value", "canonical_byte_representation", "property_order_normalization", "array_order_preservation", "application_correctness_boundary"],
        "limit": "RFC 8785 is an informational representation canonicalization scheme. It does not define domain identity or semantic equivalence, normalize Unicode meanings, preserve numbers outside its I-JSON constraints, or make a matching digest proof of truth, authority or lifecycle continuity.",
        "negative": "equal canonical JSON bytes prove equal domain objects, equal authority and equal meaning, while unequal bytes necessarily prove semantically different values",
    },
    "constitution.family.platform_commercial_support": {
        "title": "TMF622 Product Ordering Management API v5.0.0",
        "publisher": "TM Forum",
        "url": "https://github.com/tmforum-apis/TMF622_ProductOrder/blob/main/TMF622-ProductOrdering-v5.0.0.oas.yaml",
        "claim": "TMF622 addresses a ProductOrder by resource ID, models entity references with an identifier and reference URI, uses referred type for disambiguation, and keeps an agreement identifier distinct from an agreement-item identifier. Commercial references therefore require entity-kind and containment scope in addition to identifier text.",
        "coordinates": ["resource_id", "entity_reference", "reference_uri", "referred_type", "aggregate_item_identity"],
        "limit": "TMF622 defines identifiers in one telecom ordering API. It does not establish global tenant, customer, product, entitlement, invoice, support-case or provider identity, and equal external text or a shared href does not prove lifecycle or legal-party equivalence.",
        "negative": "one string ID or display name can identify every commercial object across tenants, entity kinds, aggregates, providers and lifecycle editions",
    },
    "constitution.family.operations_research": {
        "title": "CP-SAT Solver",
        "publisher": "Google OR-Tools",
        "url": "https://developers.google.com/optimization/cp/cp_solver",
        "claim": "A CP-SAT model creates distinct decision variables even when they share the same finite domain, expresses equality or inequality between those variables as explicit constraints, and returns solution statuses separately from variable assignments. Variable identity, admissible domain and assigned value are therefore separate coordinates.",
        "coordinates": ["model_scoped_variable", "variable_domain", "equality_constraint", "solution_assignment", "solve_status"],
        "limit": "The CP-SAT guide demonstrates one solver model. It does not give decision variables identity outside their model, prove two formulations equivalent, equate equal objective values with equal solutions, or turn a feasible assignment into an authorized operational decision.",
        "negative": "variables with the same name, domain or solved value are the same decision variable and solutions with equal objective values are interchangeable",
    },
}


def build() -> dict[str, Any]:
    return build_campaign(
        axis="identity_and_equality",
        campaign_key="p3i",
        program_id="program.p3i.identity-equality-evidence.v1",
        claims=CLAIMS,
        targets_path=TARGETS,
        as_of=AS_OF,
    )


def outputs() -> dict[str, str]:
    return campaign_outputs(
        built=build(),
        manifest_id="manifest.p3i.identity-equality-evidence.v1",
        as_of=AS_OF,
    )


def main() -> int:
    write_outputs(HERE, outputs())
    summary = build()["summary"]
    print(
        "BUILD PASS P3I identity/equality: "
        f"{summary['primary_evidence_candidates']} bounded candidates route "
        f"{summary['represented_library_occurrences']} library occurrences; "
        "owner decisions and gap closures remain zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
