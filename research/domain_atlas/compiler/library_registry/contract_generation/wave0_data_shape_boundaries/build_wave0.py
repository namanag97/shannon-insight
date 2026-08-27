#!/usr/bin/env python3
"""Build evidence-backed Wave-0 boundary adjudications for candidate data shapes."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[5]
UNIVERSE = WORKSPACE / "research/domain_atlas/universes/data_shapes_gap_closure"
GENERATION = HERE.parent
AS_OF = "2026-08-26"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


DOMAIN_MODELS = {
    "bim_facility_model", "biological_sequence", "boundary_representation", "cad_product_model",
    "calendar_object", "caption_track", "catalog_record", "city_model", "deep_image",
    "feature_table", "frequency_spectrum", "genomic_report", "genotype_haplotype", "order_book",
    "scene_graph", "sequence_alignment", "sequence_read_set", "variant_set",
}
PUBLISHED_LANGUAGE_MODELS = {
    "dicom_study_graph", "fhir_resource_graph", "financial_business_message", "genomic_report",
    "internet_message_graph", "phenopacket", "protected_content_envelope", "stac_catalog",
}
PROTOCOL_STATE_MODELS = {"fix_message_stream", "smtp_envelope"}
REPRESENTATION_NATIVE_MODELS = {
    "fits_hdu_list", "gltf_asset", "hdf5_group_graph", "mailbox_archive",
    "musical_event_sequence", "netcdf_dataset",
}


def model_kind(shape_short: str) -> str:
    memberships = []
    for kind, values in [
        ("domain_semantic_model", DOMAIN_MODELS),
        ("published_language_model", PUBLISHED_LANGUAGE_MODELS),
        ("protocol_state_model", PROTOCOL_STATE_MODELS),
        ("representation_native_logical_model", REPRESENTATION_NATIVE_MODELS),
    ]:
        if shape_short in values:
            memberships.append(kind)
    # Genomic report intentionally has both domain and published-language aspects; that is a split
    # signal rather than an ambiguous classifier result.
    if len(memberships) == 2 and shape_short == "genomic_report":
        return "domain_model_plus_published_language_profile"
    assert len(memberships) == 1, (shape_short, memberships)
    return memberships[0]


def build() -> tuple[dict, list[dict], list[dict], list[dict], list[dict], dict]:
    contexts = {row["context_id"]: row for row in rows(UNIVERSE / "context-candidates.jsonl")}
    libraries = rows(UNIVERSE / "library-boundaries.jsonl")
    canonical_adjudications = {
        row["candidate_id"]: row for row in rows(UNIVERSE / "canonical-adjudications.jsonl")
    }
    crosswalks = rows(UNIVERSE / "representation-crosswalks.jsonl")
    source_ids = {row["source_id"] for row in rows(UNIVERSE / "sources.jsonl")}
    crosswalks_by_shape: dict[str, list[dict]] = defaultdict(list)
    for crosswalk in crosswalks:
        crosswalks_by_shape[crosswalk["target_construct_id"]].append(crosswalk)

    constitution = {
        "record_kind": "data_shape_layer_constitution_candidate",
        "constitution_id": "constitution.wave0.data-shape-layers.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "EVIDENCE_ADJUDICATED_CANDIDATE_PENDING_CANONICAL_RATIFICATION",
        "layers": [
            {"layer": "domain_or_observation_semantics", "owns": ["grain", "identity", "time", "order", "topology", "change", "uncertainty", "domain-valid operations"], "does_not_own": ["wire syntax", "container bytes", "provider I/O"]},
            {"layer": "published_language_or_standard_logical_model", "owns": ["standard-defined types", "profile edition", "extensions", "standard conformance"], "does_not_own": ["local business truth", "local authority", "transport execution"]},
            {"layer": "representation_binding", "owns": ["semantic-to-profile mapping", "preservation set", "loss and residual", "profile compatibility"], "does_not_own": ["semantic source truth", "codec execution"]},
            {"layer": "codec_container_layout", "owns": ["syntax", "bytes", "framing", "compression", "physical layout", "malformed-input handling"], "does_not_own": ["domain identity", "fitness", "authority"]},
            {"layer": "provider_runtime_adapter", "owns": ["I/O", "capability negotiation", "provider errors", "attempt observations"], "does_not_own": ["canonical semantics", "business acceptance"]},
        ],
        "non_collapse_laws": [
            "format or filename is not a semantic type",
            "parse success is not schema profile or domain validity",
            "schema or profile conformance is not business clinical scientific or legal truth",
            "logical equality representation equality byte equality and occurrence identity are distinct",
            "conversion proves an exact preservation set emits residual loss or refuses",
            "provider support is not implementation qualification",
            "a representation-native logical model can be useful without becoming universal domain meaning",
            "one library may not own both domain semantics and every representation/provider effect used to carry it",
        ],
        "dependency_direction": [
            "domain semantics may name requirements on published languages and representation bindings",
            "published-language profiles import domain concepts through explicit mappings and anti-corruption layers",
            "representation bindings depend on both source semantic and target profile editions",
            "codecs depend on representation profiles but cannot depend on product or business authority",
            "provider adapters depend on codec and effect-port contracts and return observations inward",
        ],
        "admission_tests": [
            "distinct sovereign question and semantic owner",
            "identity grain time order topology and change laws not representable by an existing shape",
            "at least one domain-valid operation or invalid operation unique to the shape",
            "independent removal from every codec and provider",
            "explicit relation to broader existing canonical shapes",
            "unrelated-vertical reuse or a justified standard published-language boundary",
        ],
        "generation_law": "This constitution governs adjudication only; it creates no exact API, canonical identifier, implementation offer or qualification.",
    }

    decisions = []
    profile_bindings = []
    for library in sorted(libraries, key=lambda row: row["library_id"]):
        context = contexts[library["semantic_owner_context"]]
        short = library["semantic_owner_context"].removeprefix("candidate.bc.")
        shape_ref = f"candidate.shape.{short}"
        canonical = canonical_adjudications[shape_ref]
        bound_profiles = sorted(crosswalks_by_shape.get(shape_ref, []), key=lambda row: row["crosswalk_id"])
        is_profile_only = short == "gltf_asset"
        semantic_ref = "library.shape.scene_graph.semantics" if is_profile_only else f"library.shape.{short}.semantics"
        replacement_contracts = [] if is_profile_only else [{
            "contract_ref": semantic_ref,
            "contract_role": "domain_or_standard_logical_shape_semantics",
            "required_archetype": "archetype.contract.semantic_algebra",
        }]
        if bound_profiles or context["owns"][-1].endswith("representation_profile"):
            replacement_contracts.append({
                "contract_ref": f"library.shape.{short}.representation-binding",
                "contract_role": "pure_preservation_loss_and_profile_binding",
                "required_archetype": "archetype.contract.semantic_algebra",
            })
        for profile in bound_profiles:
            profile_short = profile["crosswalk_id"].removeprefix("candidate.crosswalk.").replace("_", "-")
            replacement_contracts.append({
                "contract_ref": f"library.representation.{profile_short}.profile",
                "contract_role": "editioned_representation_or_published_language_profile",
                "required_archetype": "archetype.contract.conformance_oracle",
            })
            profile_bindings.append({
                "record_kind": "wave0_representation_binding_adjudication",
                "binding_id": "binding.wave0." + profile["crosswalk_id"].removeprefix("candidate.crosswalk."),
                "edition": 1,
                "status": "RETAIN_AS_SEPARATE_UNQUALIFIED_PROFILE_BINDING",
                "source_representation": profile["source_representation"],
                "semantic_shape_ref": semantic_ref,
                "binding_layer": profile["binding_layer"],
                "round_trip": profile["round_trip"],
                "preserved": profile["preserved"],
                "not_preserved_or_not_proven": profile["not_preserved_or_not_proven"],
                "evidence_refs": profile["evidence_refs"],
                "compiler_action": profile["compiler_action"],
                "qualification_status": "NO_IMPLEMENTATION_OR_PROVIDER_QUALIFIED",
            })
        decisions.append({
            "record_kind": "wave0_data_shape_boundary_adjudication",
            "decision_id": "decision.wave0." + library["library_id"].removeprefix("candidate.lib."),
            "edition": 1,
            "status": "EVIDENCE_ADJUDICATED_CANDIDATE_PENDING_CANONICAL_RATIFICATION",
            "source_library_ref": "library." + library["library_id"],
            "source_context_ref": context["context_id"],
            "source_shape_ref": shape_ref,
            "model_kind": model_kind(short),
            "shape_relation": canonical["proposed_relation"],
            "broader_shape_ref": canonical["canonical_target_id"],
            "shape_disposition": "REPRESENTATION_BINDING_ONLY_NOT_A_NEW_SHAPE" if is_profile_only else "ADMIT_LOGICAL_SHAPE_CANDIDATE_WITH_EXACT_BROADER_RELATION",
            "library_disposition": "REPLACE_WITH_PROFILE_CONFORMANCE_CONTRACT" if is_profile_only else "SPLIT_AND_RENAME_WITHOUT_COMPATIBILITY_ALIAS",
            "boundary_failure": "The source boundary owns a logical shape and its representation profile together, while its operations also mix semantic validation, parsing, conversion or profile conformance.",
            "replacement_contracts": replacement_contracts,
            "semantic_owner_question": context["sovereign_question"],
            "retained_invariants": context["invariants"],
            "forbidden_ownership": sorted(set(library["does_not_own"] + ["codec bytes unless separately contracted", "provider qualification", "business or clinical truth"])),
            "evidence_refs": sorted(set(library["evidence_refs"] + canonical["evidence_refs"] + [ref for profile in bound_profiles for ref in profile["evidence_refs"]])),
            "no_compatibility_alias": True,
            "canonical_mutation_performed": False,
            "exact_api_gap_closed": False,
            "ratification_gate": "Canonical shape owner confirms broader relation; affected family owners accept replacement identities; each replacement receives its own exact contract and dependency tests.",
        })

    evidence_claims = [
        {
            "claim_id": "claim.wave0.fhir-platform-profile-separation",
            "source_ref": "A-SRC-114",
            "bounded_claim": "FHIR is a platform specification adapted through implementation guides, profiles, capability statements, terminology bindings and local mappings; base/profile conformance cannot stand in for local clinical meaning or authority.",
            "supports_decision_refs": ["decision.wave0.fhir-resource-graph", "decision.wave0.genomic-report"],
            "source_authority_limit": "FHIR defines its own platform and conformance artifacts, not enterprise clinical truth or local authorization.",
        },
        {
            "claim_id": "claim.wave0.gltf-delivery-format-separation",
            "source_ref": "A-SRC-102",
            "bounded_claim": "glTF defines an editioned runtime asset representation and extension model; it does not establish CAD, BIM, product-configuration or manufacturability semantics.",
            "supports_decision_refs": ["decision.wave0.gltf-profile", "decision.wave0.scene-graph"],
            "source_authority_limit": "Khronos specifies glTF representation conformance, not upstream engineering truth.",
        },
        {
            "claim_id": "claim.wave0.hdf5-abstract-model-separation",
            "source_ref": "A-DSS-014",
            "bounded_claim": "HDF5 defines a generic abstract/file data model of groups, links, datasets, dataspaces, datatypes and attributes onto which applications map domain meaning.",
            "supports_decision_refs": ["decision.wave0.hdf5-graph"],
            "source_authority_limit": "The HDF5 model cannot define application axes, units, validity or scientific interpretation by itself.",
        },
        {
            "claim_id": "claim.wave0.stac-catalog-asset-separation",
            "source_ref": "A-SRC-099",
            "bounded_claim": "STAC defines catalog, collection, item, asset, link and extension contracts; catalog metadata does not prove referenced asset availability, quality, fitness or access authority.",
            "supports_decision_refs": ["decision.wave0.stac-catalog"],
            "source_authority_limit": "STAC governs its catalog model, not the truth or accessibility of every referenced asset.",
        },
    ]
    decisions_by_kind: dict[str, list[dict]] = defaultdict(list)
    for decision in decisions:
        decisions_by_kind[decision["model_kind"]].append(decision)
    ratification_packages = []
    for ordinal, (kind, members) in enumerate(sorted(decisions_by_kind.items()), start=1):
        ratification_packages.append({
            "record_kind": "wave0_ratification_work_package",
            "work_package_id": f"work.wave0.shape-ratification.{ordinal:02d}.{kind.replace('_', '-')}",
            "edition": 1,
            "status": "READY_FOR_OWNER_RATIFICATION_NOT_CANONICAL",
            "model_kind": kind,
            "decision_refs": [row["decision_id"] for row in members],
            "candidate_count": len(members),
            "shared_questions": [
                "Does the candidate own a distinct logical or domain meaning rather than a file format or provider surface?",
                "What exact identity grain time order topology change uncertainty and equality laws distinguish it from its broader shape?",
                "Which published-language profiles representation bindings codecs and provider adapters must remain separate?",
                "Which conversions are total partial or lossy and what residual evidence is mandatory?",
                "Can an unrelated vertical reuse the semantic contract without importing format vendor or product authority?",
            ],
            "allowed_dispositions": ["RATIFY", "NARROW", "SPLIT", "MERGE", "REPLACE_WITH_PROFILE", "RETIRE"],
            "exit_evidence": [
                "owner-signed disposition for every decision reference",
                "exact broader/equivalent/disjoint relation for every retained shape",
                "accepted replacement contract identities with no compatibility aliases",
                "bounded primary-source claims and counterexamples",
                "negative-twin and unrelated-vertical tests",
            ],
            "completion_effect": "Makes decisions eligible for source-contract publication; does not itself close an exact-API gap.",
        })
    assert all(ref in source_ids for decision in decisions for ref in decision["evidence_refs"])
    assert all(claim["source_ref"] in source_ids for claim in evidence_claims)

    summary = {
        "program_id": "program.wave0.data-shape-boundary-adjudication.v1",
        "edition": 1,
        "as_of": AS_OF,
        "status": "ACTIVE_PENDING_CANONICAL_RATIFICATION",
        "completion_claim": False,
        "source_boundaries": len(libraries),
        "split_and_rename": sum(row["library_disposition"].startswith("SPLIT") for row in decisions),
        "profile_only_replacements": sum(row["library_disposition"].startswith("REPLACE") for row in decisions),
        "representation_bindings": len(profile_bindings),
        "bounded_evidence_claims": len(evidence_claims),
        "ratification_work_packages": len(ratification_packages),
        "canonical_mutations": 0,
        "canonical_exact_gaps_closed": 0,
        "remaining_gate": "Ratify logical-shape relations and replacement ownership, then publish exact contracts for each retained layer.",
    }
    return constitution, decisions, profile_bindings, evidence_claims, ratification_packages, summary


def outputs() -> dict[str, str]:
    constitution, decisions, bindings, claims, ratification_packages, summary = build()
    files = {
        "layer-constitution.json": json.dumps(constitution, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        "boundary-adjudications.jsonl": "".join(canonical(row) + "\n" for row in decisions),
        "representation-bindings.jsonl": "".join(canonical(row) + "\n" for row in bindings),
        "evidence-claims.jsonl": "".join(canonical(row) + "\n" for row in claims),
        "ratification-work-packages.jsonl": "".join(canonical(row) + "\n" for row in ratification_packages),
        "summary.json": json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest_claims = {name: {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.wave0.data-shape-boundaries.v1", "as_of": AS_OF, "files": manifest_claims}, sort_keys=True, indent=2) + "\n"
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
    _, decisions, bindings, _, packages, summary = build()
    print(f"{'CHECK' if args.check else 'BUILD'} PASS Wave 0 data-shape boundaries: {len(decisions)} adjudications in {len(packages)} reusable ratification packages, {len(bindings)} separate profile bindings, {summary['split_and_rename']} split/rename, {summary['profile_only_replacements']} profile-only replacement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
