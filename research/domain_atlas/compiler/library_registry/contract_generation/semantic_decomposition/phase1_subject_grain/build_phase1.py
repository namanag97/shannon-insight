#!/usr/bin/env python3
"""Build the evidence-backed Phase-1 subject, identity and grain constitution candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
AS_OF = "2026-08-26"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build() -> dict[str, Any]:
    constitution = {
        "record_kind": "semantic_axis_phase_constitution_candidate",
        "constitution_id": "constitution.semantic-axis.phase1.subject-identity-grain.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "EVIDENCE_BACKED_CANDIDATE_PENDING_OWNER_RATIFICATION",
        "completion_claim": False,
        "sovereign_question": "What exact subject is being discussed, under which identity/equality relation and at which grain/cardinality?",
        "negative_mission": "Do not create a universal Object, Id, Record or Collection type and do not infer subject identity, equality or analytical grain from names, schemas, storage rows or provider occurrences.",
        "modules": [
            {
                "module_id": "module.semantic-axis.semantic-object.v1",
                "axis": "semantic_object",
                "status": "CANDIDATE_PENDING_RATIFICATION",
                "facet_refs": [
                    "value", "entity_or_occurrence", "event_or_fact", "state_or_snapshot",
                    "relation_or_graph", "rule_or_policy", "plan_or_intent",
                    "claim_or_evidence", "resource_or_capability", "representation_artifact",
                ],
                "required_decisions": [
                    "referent domain and semantic owner", "subject kind and edition",
                    "role versus intrinsic kind", "identity-bearing versus identity-less",
                    "lifecycle-bearing versus immutable", "asserted observed requested derived or represented",
                    "classification overlap and precedence", "unknown or disputed classification",
                ],
                "non_collapse_laws": [
                    "referent is not identifier",
                    "referent is not representation occurrence",
                    "entity is not record and record is not row",
                    "event fact observation assertion and command are distinct",
                    "state is not the event history or snapshot that represents it",
                    "claim is not evidence and evidence is not proof of truth",
                    "plan intent attempt effect and accepted outcome are distinct",
                    "resource capability entitlement allocation and usage are distinct",
                    "one subject may occupy multiple explicitly scoped roles; facet labels are not globally disjoint ontological truth",
                ],
                "required_outcomes": ["classified", "multi_role", "inapplicable", "indeterminate", "disputed", "refused"],
            },
            {
                "module_id": "module.semantic-axis.identity-equality.v1",
                "axis": "identity_and_equality",
                "status": "CANDIDATE_PENDING_RATIFICATION",
                "equality_stack": [
                    "lexical equality", "representation equality", "canonical representation equality",
                    "value equality", "domain equivalence claim", "resolved co-reference",
                    "version continuity", "occurrence identity", "historical continuity",
                ],
                "required_coordinates": [
                    "identity domain", "scheme and namespace", "assignment or naming authority",
                    "semantic edition", "temporal validity", "comparison purpose",
                    "equality or equivalence relation", "canonicalization profile",
                    "resolution evidence and defeaters", "version occurrence and continuity model",
                ],
                "non_collapse_laws": [
                    "same spelling is not same scoped identifier",
                    "same identifier is not same referent",
                    "proof of control is not subject identity",
                    "byte or digest equality is not semantic equality",
                    "canonicalization is scoped to one declared equivalence relation",
                    "merge is an authorized lifecycle action and not proof of historical equivalence",
                    "mutable reference immutable version logical subject and physical occurrence have separate identities",
                    "comparison failure is not inequality",
                ],
                "required_outcomes": ["equal", "not_equal", "equivalent_under_profile", "not_equivalent_under_profile", "incomparable", "indeterminate", "refused"],
            },
            {
                "module_id": "module.semantic-axis.grain-cardinality.v1",
                "axis": "grain_and_cardinality",
                "status": "CANDIDATE_PENDING_RATIFICATION",
                "grain_coordinates": [
                    "unit of observation", "unit of identity", "unit of analysis",
                    "unit of update", "unit of authority", "unit of storage",
                    "unit of partition", "unit of ordering", "unit of completeness",
                ],
                "cardinality_coordinates": [
                    "minimum", "maximum including unbounded", "known versus unknown",
                    "set bag sequence map graph or stream semantics", "boundedness",
                    "partition census", "page or continuation scope", "window or cut",
                ],
                "non_collapse_laws": [
                    "observation grain is not entity identity grain",
                    "analysis grain is not storage row grain",
                    "update atomicity grain is not transaction authority scope",
                    "scalar record collection partition page stream and graph are distinct",
                    "set bag and sequence multiplicity or ordering cannot be exchanged silently",
                    "partition-local order uniqueness or completeness is not global",
                    "pagination is a delivery mechanism and not semantic result grain",
                    "bounded and unbounded collections have different completion laws",
                    "aggregation disaggregation explode deduplicate and join are grain-changing transformations with preservation and residual contracts",
                    "zero one many unknown and unbounded are distinct cardinality states",
                ],
                "required_outcomes": ["compatible", "requires_lossless_regrain", "requires_authorized_loss", "incompatible", "indeterminate", "refused"],
            },
        ],
        "cross_module_laws": [
            "A subject classification is interpreted only inside an exact bounded context and edition.",
            "Identity/equality is parameterized by subject kind and purpose; no universal equality relation exists.",
            "Grain changes cannot manufacture or discard identity, multiplicity, order or completeness without an explicit preservation/loss contract.",
            "A representation schema may constrain carrier structure but cannot choose the domain subject, identity relation or analysis grain.",
            "Unknown and disputed decisions remain typed; the compiler does not default them.",
        ],
        "imported_foundation_refs": [
            "library.csp.identity.scoped-identifier", "library.csp.identity.namespace-registry",
            "library.csp.identity.version-identity", "library.csp.identity.canonicalization",
            "library.san_content_identity", "library.san_canonical", "library.san_integrity",
        ],
        "prohibited_new_facades": ["universal_object", "universal_id", "universal_record", "universal_collection", "universal_equality", "universal_grain"],
        "ratification_gate": "Named foundation owners accept vocabulary, coordinate sets, non-collapse laws, outcomes and imports; all 23 family matrices record applicability and exceptions.",
    }
    evidence_claims = [
        {
            "claim_id": "claim.phase1.rdf-term-and-graph-equality",
            "source_ref": "DSS-011",
            "source_registry_path": "research/domain_atlas/universes/data_shapes/sources.jsonl",
            "url": "https://www.w3.org/TR/rdf12-concepts/",
            "bounded_claim": "RDF 1.2 defines kind-sensitive term equality, componentwise triple equality and graph isomorphism; an IRI and a literal remain different terms even when based on the same string.",
            "supports_module_refs": ["module.semantic-axis.semantic-object.v1", "module.semantic-axis.identity-equality.v1"],
            "authority_limit": "RDF term and graph equality do not define enterprise entity identity, property-graph identity, domain equivalence or historical continuity.",
        },
        {
            "claim_id": "claim.phase1.uri-comparison-purpose",
            "source_ref": "source.csp.ietf-rfc3986",
            "source_registry_path": "research/domain_atlas/universes/core_semantic_primitives/sources.jsonl",
            "url": "https://www.rfc-editor.org/rfc/rfc3986.html",
            "bounded_claim": "URI comparison is purpose- and scheme-sensitive and uses a comparison ladder that trades processing cost against false negatives.",
            "supports_module_refs": ["module.semantic-axis.identity-equality.v1"],
            "authority_limit": "URI equivalence cannot prove that different URIs denote different resources or establish subject identity.",
        },
        {
            "claim_id": "claim.phase1.shacl-cardinality-is-profile-scoped",
            "source_ref": "DSS-013",
            "source_registry_path": "research/domain_atlas/universes/data_shapes/sources.jsonl",
            "url": "https://www.w3.org/TR/shacl/",
            "bounded_claim": "SHACL cardinality constraints count value nodes reached through an exact property shape and path, producing profile-scoped conformance results.",
            "supports_module_refs": ["module.semantic-axis.grain-cardinality.v1"],
            "authority_limit": "A SHACL count does not establish real-world completeness, analytical grain, entity identity or data-source truth.",
        },
        {
            "claim_id": "claim.phase1.beam-boundedness-changes-execution",
            "source_ref": "src.beam.basics",
            "source_registry_path": "research/domain_atlas/universes/pipeline_dataflow/sources.jsonl",
            "url": "https://beam.apache.org/documentation/basics/",
            "bounded_claim": "Apache Beam makes bounded and unbounded PCollections distinct model states and requires runners lacking the required capability to reject rather than silently execute weakened semantics.",
            "supports_module_refs": ["module.semantic-axis.grain-cardinality.v1"],
            "authority_limit": "Beam defines its portable dataflow model, not universal business collection grain, source completeness or analytical acceptance.",
        },
        {
            "claim_id": "claim.phase1.otel-metric-stream-identity-and-grain",
            "source_ref": "source.telemetry.otel.metrics",
            "source_registry_path": "research/domain_atlas/universes/telemetry_signals/sources.jsonl",
            "url": "https://opentelemetry.io/docs/specs/otel/metrics/data-model/",
            "bounded_claim": "OpenTelemetry metric streams have explicit identity coordinates, attribute-defined stream partitions, point kinds, timestamps and delta/cumulative temporality; some properties identify a stream while others do not.",
            "supports_module_refs": ["module.semantic-axis.identity-equality.v1", "module.semantic-axis.grain-cardinality.v1"],
            "authority_limit": "Telemetry stream identity and natural merge do not define business measures, master identity, global completeness or arbitrary analytical reaggregation.",
        },
        {
            "claim_id": "claim.phase1.arrow-array-length-and-layout",
            "source_ref": "source.schema-mapping.arrow.columnar.1.5",
            "source_registry_path": "research/domain_atlas/universes/schema_mapping_translation/sources.jsonl",
            "url": "https://arrow.apache.org/docs/format/Columnar.html",
            "bounded_claim": "Arrow arrays are typed sequences with explicit length, null count, buffers, children and physical layouts, and nested type equality depends on child types.",
            "supports_module_refs": ["module.semantic-axis.semantic-object.v1", "module.semantic-axis.grain-cardinality.v1"],
            "authority_limit": "Array length and physical layout do not define entity, observation or analytical grain and do not prove application semantic equality.",
        },
    ]
    compiler_projection = {
        "record_kind": "semantic_axis_compiler_projection_candidate",
        "projection_id": "projection.compiler.semantic-axis.phase1.v1",
        "edition": 1,
        "status": "STRUCTURAL_PROJECTION_NOT_IR_AUTHORITY",
        "required_ir_roles": [
            "SemanticSubjectRef", "SubjectKindRef", "SubjectClassificationRef",
            "IdentityDomainRef", "EqualityRelationRef", "CanonicalizationProfileRef",
            "GrainContractRef", "CardinalityContractRef", "Boundedness",
            "CollectionSemantics", "ComparisonOutcome", "RegrainPlan", "PreservationSet", "Residual",
        ],
        "binding_sequence": [
            "resolve bounded context and semantic owner",
            "bind subject classification edition",
            "bind identity domain and comparison purpose",
            "bind equality and canonicalization profiles",
            "bind all nine grain coordinates and cardinality states",
            "compare producer and consumer contracts",
            "insert only proved lossless adapters or explicitly authorized lossy regrain plans",
            "emit residual ownership and refusal when any coordinate remains unresolved",
        ],
        "required_adapter_proofs": [
            "subject-kind preservation", "identity preservation", "multiplicity preservation",
            "ordering preservation", "boundedness/completion preservation", "partition/global semantics",
            "aggregation or disaggregation law", "loss and residual evidence",
        ],
        "refusal_roles": [
            "subject_unresolved", "classification_disputed", "identity_domain_unbound",
            "equality_relation_unbound", "comparison_incomparable", "grain_unbound",
            "cardinality_incompatible", "boundedness_incompatible", "multiplicity_loss_unaccepted",
            "ordering_loss_unaccepted", "completeness_unproved", "adapter_proof_missing",
        ],
        "generation_prohibition": "Do not generate Rust types, IR nodes or adapters from labels alone; exact owner-ratified modules and family applicability are prerequisites.",
    }
    summary = {
        "program_id": "program.semantic-axis.phase1.subject-identity-grain.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "ACTIVE_PENDING_OWNER_RATIFICATION",
        "completion_claim": False,
        "modules": 3,
        "bounded_primary_evidence_claims": len(evidence_claims),
        "grain_coordinates": 9,
        "imported_foundations": len(constitution["imported_foundation_refs"]),
        "canonical_exact_gaps_closed": 0,
        "remaining_gate": constitution["ratification_gate"],
    }
    return {"constitution": constitution, "evidence_claims": evidence_claims, "compiler_projection": compiler_projection, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "constitution.json": json.dumps(built["constitution"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "evidence-claims.jsonl": "".join(canonical(row) + "\n" for row in built["evidence_claims"]),
        "compiler-projection.json": json.dumps(built["compiler_projection"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.semantic-axis.phase1.v1", "as_of": AS_OF, "files": claims}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = build()["summary"]
    print(f"{'CHECK' if args.check else 'BUILD'} PASS Phase 1 semantic constitution: {summary['modules']} modules, {summary['bounded_primary_evidence_claims']} bounded claims, {summary['grain_coordinates']} grain coordinates, zero canonical gaps closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
