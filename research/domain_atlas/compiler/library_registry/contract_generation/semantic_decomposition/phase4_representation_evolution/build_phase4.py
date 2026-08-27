#!/usr/bin/env python3
"""Build the Phase-4 representation/compatibility/evolution constitution candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
AS_OF = "2026-08-26"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build() -> dict[str, Any]:
    sources = [
        {"source_id":"source.semantic-phase4.json-schema.core","publisher":"JSON Schema project","source_kind":"specification","title":"JSON Schema Core 2020-12","url":"https://json-schema.org/draft/2020-12/json-schema-core","claim_scope":"schema resources, dialects, vocabularies, references, annotations and assertion processing","authority_limit":"Describes JSON instances under declared vocabularies; schema validity is not domain validity, referent truth, behavioral compatibility or preservation under conversion."},
        {"source_id":"source.semantic-phase4.arrow.columnar","publisher":"Apache Arrow","source_kind":"specification","title":"Arrow Columnar Format","url":"https://arrow.apache.org/docs/format/Columnar.html","claim_scope":"application-facing data types, physical layouts, buffers, IPC metadata and extension types","authority_limit":"Defines an in-memory/interchange representation for supported shapes; it does not own business semantics, persistence policy, mutation coordination or every implementation behavior."},
        {"source_id":"source.semantic-phase4.protobuf.proto3","publisher":"Google / Protocol Buffers project","source_kind":"official_guide","title":"Protocol Buffers proto3 Language Guide","url":"https://protobuf.dev/programming-guides/proto3/","claim_scope":"message definition, field presence and binary/JSON/text evolution rules","authority_limit":"Wire-safe parsing does not prove application behavior, validation, semantic preservation, source compatibility or historical correctness."},
        {"source_id":"source.semantic-phase4.avro.spec","publisher":"Apache Avro","source_kind":"specification","title":"Apache Avro Specification","url":"https://avro.apache.org/docs/current/specification/","claim_scope":"writer/reader schema resolution, aliases, defaults, encodings and object-container representation","authority_limit":"Resolution specifies how Avro data is decoded; it does not establish domain equivalence, losslessness outside Avro or acceptance by consumers."},
        {"source_id":"source.semantic-phase4.iceberg.spec","publisher":"Apache Iceberg","source_kind":"specification","title":"Apache Iceberg Table Specification","url":"https://iceberg.apache.org/spec/","claim_scope":"stable field IDs, schema/spec evolution, snapshots and valid promotions","authority_limit":"Table metadata rules do not establish upstream meaning, row uniqueness, application compatibility or arbitrary migration reversibility."},
        {"source_id":"source.semantic-phase4.semver","publisher":"Semantic Versioning project","source_kind":"specification","title":"Semantic Versioning 2.0.0","url":"https://semver.org/spec/v2.0.0.html","claim_scope":"version precedence and change signaling relative to a declared public API","authority_limit":"Version numbers are publisher claims about a declared API; SemVer does not prove behavioral, data, ABI, operational or provider compatibility."},
        {"source_id":"source.semantic-phase4.cargo.semver","publisher":"Rust project","source_kind":"official_reference","title":"Cargo SemVer Compatibility","url":"https://doc.rust-lang.org/stable/cargo/reference/semver.html","claim_scope":"Rust/Cargo source-level compatibility hazards and conventional change categories","authority_limit":"Guidelines focus mainly on whether dependent Rust code builds; runtime behavior, unsafe contracts, data compatibility and downstream policy remain separately governed."},
        {"source_id":"source.semantic-phase4.wasm.wit","publisher":"WebAssembly Component Model project","source_kind":"design_specification","title":"WebAssembly Interface Types (WIT)","url":"https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md","claim_scope":"typed component interfaces, package/interface versions, imports/exports and canonical component types","authority_limit":"WIT and canonical ABI adaptation define interface representation; they do not prove domain meaning, effect behavior, resource guarantees or provider qualification."},
        {"source_id":"source.semantic-phase4.openapi","publisher":"OpenAPI Initiative","source_kind":"specification","title":"OpenAPI Specification 3.2.0","url":"https://spec.openapis.org/oas/v3.2.0.html","claim_scope":"language-neutral HTTP interface descriptions, operations, messages, schemas, dialects and version/deprecation metadata","authority_limit":"An interface description does not prove server conformance, authorization, domain semantics, behavioral compatibility or operational fitness."},
    ]
    constitution = {
        "record_kind":"semantic_axis_phase_constitution_candidate",
        "constitution_id":"constitution.semantic-axis.phase4.representation-evolution.v1",
        "edition":1,"as_of":AS_OF,"status":"EVIDENCE_BACKED_CANDIDATE_PENDING_OWNER_RATIFICATION","completion_claim":False,
        "sovereign_question":"Which exact meaning is represented by which profile, schema, carrier, layout, codec, wire contract and implementation edition, and under which directional compatibility and migration relation may it change without hidden loss?",
        "negative_mission":"Do not infer semantic equivalence from matching fields, domain validity from schema success, compatibility from decodability or version numbers, preservation from round-trip bytes, or reversibility from the existence of a migration script.",
        "modules":[
            {
                "module_id":"module.semantic-axis.representation.v1","axis":"representation",
                "representation_layers":[
                    "owned domain meaning and invariants","published language or semantic profile","logical schema and constraints","representation binding","carrier and physical layout","container/framing and metadata","codec and canonicalization profile","wire/DTO/API contract","language/ABI binding","provider/legacy adapter",
                ],
                "binding_coordinates":[
                    "source meaning edition","target representation edition","direction","supported shape/profile subset","identity and equality preservation","grain/cardinality preservation","state/time/order preservation","partiality/uncertainty preservation","authority/privacy/security/safety preservation","units/reference systems/collation","defaulting/coercion/normalization","unknown-field and extension behavior","loss/residual channel","resource and size limits","determinism/canonical bytes","round-trip and conformance evidence","accepting owner",
                ],
                "required_outcomes":["exactly_preserved","preserved_under_declared_profile","projected_with_residual","lossy_with_explicit_acceptance","opaque_passthrough","unsupported","ambiguous","indeterminate","refused"],
                "non_collapse_laws":[
                    "domain meaning is not a schema a DTO a field name or a storage type","published language is not provider wire format","logical schema is not physical layout","carrier equality is not value or domain equivalence","schema syntax validity is not instance validity and instance validity is not aggregate validity","successful decoding is not semantic preservation","round-trip bytes are not round-trip meaning unless the preservation profile proves it","canonicalization is scoped to a representation profile and does not create domain identity","defaulting coercion truncation normalization and imputation are transformations not neutral parsing","unknown-field preservation is distinct from understanding or enforcing the field","extension passthrough does not confer extension semantics","column order field order event order and causal order are separate","zero-copy is a physical property not a semantic guarantee","a generated binding or FFI adapter is never the owner of meaning","every lossy conversion emits a typed residual or is refused","format and provider adapters remain replaceable at the boundary",
                ],
            },
            {
                "module_id":"module.semantic-axis.compatibility-evolution.v1","axis":"compatibility_and_evolution",
                "compatibility_dimensions":[
                    "semantic meaning/invariant","source API/type-checking","behavioral/refusal","logical schema/validation","reader-from-writer data","writer-for-reader data","wire/protocol","serialization/canonical bytes","ABI/calling convention","state/history/replay","operational/SLO/resource","security/privacy/safety","provider capability","build target/MSRV/feature/dependency","evidence/conformance",
                ],
                "directional_relations":["new_consumer_reads_old","old_consumer_reads_new","new_producer_serves_old","old_producer_serves_new","mixed_version_coexists","historical_replay_under_new","rollback_reads_new_writes","round_trip_preserves_profile"],
                "change_lifecycle":[
                    "immutable edition identity","typed semantic diff","compatibility vector and affected profiles","blast-radius/dependency cut","upcast/downcast or translation plan","data migration/backfill/reconciliation","in-flight work disposition","dual-read/write or shadow/parallel run","provider and consumer qualification","canary/rollout gates","rollback and roll-forward plans","historical replay evidence","deprecation and replacement edges","decommission and tombstone","evidence invalidation and renewed acceptance",
                ],
                "required_outcomes":["compatible_for_declared_profile","compatible_with_adapter","conditionally_compatible","migration_required","parallel_run_required","incompatible","unknown","evidence_stale","refused"],
                "non_collapse_laws":[
                    "compatibility is a directional relation over a declared profile not a boolean property of one artifact","source compatibility is not behavioral wire data ABI operational or semantic compatibility","backward and forward compatibility are not synonyms","wire-safe evolution is not semantic-safe evolution","reader/writer schema resolution is not bidirectional round-trip preservation","version precedence is not compatibility proof","a major version does not identify the broken dimension and a minor version does not prove unchanged behavior","an upcaster constructs a current interpretation and does not rewrite historical truth","migration backfill replay and reprocessing are distinct effects","rollback of code is not reversal of schema data authority or external effects","dual-write does not guarantee atomicity agreement or cutover safety","aliases are resolution hints not identity continuity","rename by stable field identity is different from delete-and-add by name","deprecation without replacement deadline consumer census and exit evidence is incomplete","provider compatibility claims require exact capability edition and independent qualification","feature/MSRV/target/dependency changes are separate compatibility coordinates","evidence is edition-bound and may become stale when any relied-upon coordinate changes","no compatibility alias may silently preserve an obsolete meaning",
                ],
            },
        ],
        "cross_module_laws":[
            "Every compatibility claim names source and target editions, direction, profile, representation bindings, consumers, evidence and expiry.",
            "Semantic diff precedes schema/wire diff; identical schemas can hide changed meaning and different schemas can preserve meaning through a proved adapter.",
            "The compiler chooses a binding only after preservation obligations from Phases 1-3 are discharged; otherwise it emits a residual or refusal.",
            "Generated adapters are versioned artifacts with explicit total outcomes, resource limits, evidence and removal seams.",
            "Migration is an authorized effect and re-enters time, partiality, authority, privacy, security, safety and unknown-completion analysis.",
        ],
        "imported_foundation_refs":[
            "library.dsh.contract.logical-schema","library.dsh.contract.schema-diff","library.dsh.contract.compatibility-policy","library.dsh.contract.canonical-schema-serialization","library.dsh.contract.content-addressed-schema-id","library.dsh.contract.schema-ref-resolution","library.dsh.contract.validation","library.dsh.contract.schema-registry-port","library.dsh.contract.lineage-impact-hook","library.representation.codec.contract-model","library.representation.codec.canonicalization","library.representation.codec.roundtrip-conformance","library.csp.change.compatibility-relation","library.csp.change.semantic-diff","library.csp.change.migration-plan","library.csp.change.upcast-downcast","library.csp.change.backfill","library.csp.change.rollout-plan","library.csp.change.rollback-plan","library.csp.change.decommission","library.csp.change.historical-replay",
        ],
        "prohibited_new_facades":["universal_schema","universal_record","universal_codec","universal_adapter","universal_compatibility_boolean","universal_version","universal_migration","universal_upcaster"],
        "ratification_gate":"Named semantic, contract, representation, runtime, migration, security and affected-family owners accept layers, dimensions, directional relations, loss channels and lifecycle gates; every family matrix records applicability and exceptions.",
    }
    claims = [
        {"claim_id":"claim.phase4.json-schema-dialects","source_ref":"source.semantic-phase4.json-schema.core","bounded_claim":"JSON Schema separates schema resources, dialects and vocabularies, and distinguishes assertion behavior from annotations and unknown vocabulary handling.","supports_module_refs":["module.semantic-axis.representation.v1"],"authority_limit":sources[0]["authority_limit"]},
        {"claim_id":"claim.phase4.arrow-types-layouts","source_ref":"source.semantic-phase4.arrow.columnar","bounded_claim":"Arrow separates application-facing data types from physical layouts and permits extension semantics over storage types while specifying interoperable buffers and IPC metadata.","supports_module_refs":["module.semantic-axis.representation.v1"],"authority_limit":sources[1]["authority_limit"]},
        {"claim_id":"claim.phase4.protobuf-wire-safety","source_ref":"source.semantic-phase4.protobuf.proto3","bounded_claim":"Protocol Buffers classifies message changes by wire safety and notes that binary, JSON and text representations have different safe-change rules.","supports_module_refs":["module.semantic-axis.representation.v1","module.semantic-axis.compatibility-evolution.v1"],"authority_limit":sources[2]["authority_limit"]},
        {"claim_id":"claim.phase4.avro-directional-resolution","source_ref":"source.semantic-phase4.avro.spec","bounded_claim":"Avro resolution is directional between the writer schema stored with data and the reader schema expected by an application.","supports_module_refs":["module.semantic-axis.compatibility-evolution.v1"],"authority_limit":sources[3]["authority_limit"]},
        {"claim_id":"claim.phase4.iceberg-stable-field-identity","source_ref":"source.semantic-phase4.iceberg.spec","bounded_claim":"Iceberg evolves schemas using never-reused field IDs, new schema identities and a constrained set of promotions rather than relying on field position or name alone.","supports_module_refs":["module.semantic-axis.representation.v1","module.semantic-axis.compatibility-evolution.v1"],"authority_limit":sources[4]["authority_limit"]},
        {"claim_id":"claim.phase4.semver-public-api","source_ref":"source.semantic-phase4.semver","bounded_claim":"SemVer signals change relative to an explicitly declared public API and requires released version contents to remain immutable.","supports_module_refs":["module.semantic-axis.compatibility-evolution.v1"],"authority_limit":sources[5]["authority_limit"]},
        {"claim_id":"claim.phase4.cargo-source-compatibility","source_ref":"source.semantic-phase4.cargo.semver","bounded_claim":"Cargo documents Rust-specific source compatibility categories while warning that runtime behavior often remains a maintainer judgment.","supports_module_refs":["module.semantic-axis.compatibility-evolution.v1"],"authority_limit":sources[6]["authority_limit"]},
        {"claim_id":"claim.phase4.wit-interface-binding","source_ref":"source.semantic-phase4.wasm.wit","bounded_claim":"WIT defines typed component imports and exports that resolve to canonical component types and applies version gates to interface items.","supports_module_refs":["module.semantic-axis.representation.v1","module.semantic-axis.compatibility-evolution.v1"],"authority_limit":sources[7]["authority_limit"]},
        {"claim_id":"claim.phase4.openapi-description-bound","source_ref":"source.semantic-phase4.openapi","bounded_claim":"OpenAPI describes HTTP interface operations and message data through an editioned, language-neutral contract whose schemas may use declared JSON Schema dialects.","supports_module_refs":["module.semantic-axis.representation.v1"],"authority_limit":sources[8]["authority_limit"]},
    ]
    projection = {
        "record_kind":"semantic_axis_compiler_projection_candidate","projection_id":"projection.compiler.semantic-axis.phase4.v1","edition":1,"status":"STRUCTURAL_PROJECTION_NOT_IR_AUTHORITY",
        "required_ir_roles":["MeaningRef","PublishedLanguageRef","LogicalSchemaRef","SchemaDialectRef","RepresentationProfileRef","CarrierTypeRef","PhysicalLayoutRef","ContainerRef","CodecRef","CanonicalizationProfileRef","WireContractRef","LanguageBindingRef","ProviderAdapterRef","PreservationObligationSet","LossChannel","SourceEditionRef","TargetEditionRef","CompatibilityProfileRef","CompatibilityVector","SemanticDiffRef","MigrationPlanRef","UpcasterRef","DowncasterRef","BackfillPlanRef","RolloutPlanRef","RollbackPlanRef","HistoricalReplayPlanRef","DecommissionPlanRef","EvidenceInvalidationSet","Residual"],
        "binding_sequence":["bind owned meaning and Phase 1-3 semantic obligations","select published language and exact logical schema dialect","select representation profile carrier layout container and codec","prove each preservation coordinate and expose loss","bind exact wire/language/provider adapter editions","compute directional compatibility vector for named consumers","derive semantic diff blast radius migration and in-flight disposition","qualify adapters/providers and execute canary or parallel run","validate replay rollback roll-forward and decommission evidence","emit residuals and invalidate stale evidence"],
        "required_adapter_proofs":["meaning/profile identity","identity equality and grain preservation","state/time/order/partiality preservation","authority/privacy/security/safety preservation","default/coercion/unknown-field behavior","loss and residual completeness","determinism/canonicalization scope","directional reader/writer compatibility","resource bounds and total outcomes","historical replay and rollback behavior","independent conformance"],
        "refusal_roles":["meaning_unbound","dialect_unknown","vocabulary_unsupported","schema_invalid","domain_invariant_unproved","representation_profile_missing","carrier_unsupported","loss_unreported","coercion_ambiguous","unknown_field_policy_missing","canonicalization_unproved","wire_contract_mismatch","adapter_unqualified","compatibility_direction_missing","compatibility_profile_missing","semantic_diff_missing","consumer_census_incomplete","migration_plan_missing","in_flight_disposition_missing","rollback_unproved","historical_replay_unproved","evidence_stale","decommission_incomplete"],
        "generation_prohibition":"Do not generate schemas, codecs, adapters, compatibility declarations, upcasters, migrations, rollouts, rollback or decommission actions from matching names, parse success, round trips, version ranges or provider claims alone.",
    }
    summary = {"program_id":"program.semantic-axis.phase4.representation-evolution.v1","edition":1,"as_of":AS_OF,"status":"ACTIVE_PENDING_OWNER_RATIFICATION","completion_claim":False,"modules":2,"primary_sources":len(sources),"bounded_primary_evidence_claims":len(claims),"representation_layers":10,"binding_coordinates":17,"compatibility_dimensions":15,"directional_relations":8,"change_lifecycle_stages":15,"canonical_exact_gaps_closed":0,"remaining_gate":constitution["ratification_gate"]}
    return {"sources":sources,"constitution":constitution,"claims":claims,"projection":projection,"summary":summary}


def outputs() -> dict[str, str]:
    bundle = build()
    files = {
        "sources.jsonl":"".join(canonical(x)+"\n" for x in bundle["sources"]),
        "constitution.json":json.dumps(bundle["constitution"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        "evidence-claims.jsonl":"".join(canonical(x)+"\n" for x in bundle["claims"]),
        "compiler-projection.json":json.dumps(bundle["projection"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        "summary.json":json.dumps(bundle["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
    }
    manifest = {name:{"sha256":hashlib.sha256(text.encode()).hexdigest(),"bytes":len(text.encode())} for name,text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id":"manifest.semantic-axis.phase4.v1","as_of":AS_OF,"files":manifest},sort_keys=True,indent=2)+"\n"
    return files


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--check",action="store_true"); args=parser.parse_args(); stale=[]
    for name,text in outputs().items():
        path=HERE/name
        if args.check:
            if not path.is_file() or path.read_text()!=text: stale.append(name)
        else: path.write_text(text)
    if stale: print("STALE "+", ".join(stale)); return 1
    summary=build()["summary"]
    print(f"{'CHECK' if args.check else 'BUILD'} PASS Phase 4 semantic constitution: {summary['modules']} modules, {summary['primary_sources']} sources, {summary['bounded_primary_evidence_claims']} claims, zero canonical gaps closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
