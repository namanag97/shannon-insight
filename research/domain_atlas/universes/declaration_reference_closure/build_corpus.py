#!/usr/bin/env python3
"""Build interface, provider-offer and package reference-closure contracts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def source(key: str, title: str, authority: str, url: str, supports: str, limit: str) -> dict:
    return {
        "source_id": f"source.drc.{key}", "title": title, "authority": authority,
        "url": url, "retrieved": AS_OF, "source_kind": "primary_or_official",
        "supports": supports, "does_not_prove": limit,
    }


SOURCES = [
    source("openapi32", "OpenAPI Specification 3.2.0", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.2.0.html", "multi-document API descriptions, dialect editions, operations, servers, security and references", "An API description does not prove deployment, reachability, authorization or behavior."),
    source("asyncapi30", "AsyncAPI Specification 3.0.0", "AsyncAPI Initiative", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "message API documents, channels, operations, bindings, schemas and Reference Objects", "A declared application contract does not prove broker topology or runtime behavior."),
    source("jsonschema202012", "JSON Schema Core Draft 2020-12", "JSON Schema", "https://json-schema.org/draft/2020-12/json-schema-core.html", "resource identity, base URI, anchors, ref and dynamicRef semantics", "A schema reference is not an instruction to fetch a network URL and schema validity is not business validity."),
    source("rfc3986", "RFC 3986 URI Generic Syntax", "IETF", "https://www.rfc-editor.org/rfc/rfc3986", "URI reference parsing and resolution", "URI equality does not establish resource identity or availability."),
    source("rfc6901", "RFC 6901 JSON Pointer", "IETF", "https://www.rfc-editor.org/rfc/rfc6901", "JSON document fragment addressing", "A pointer identifies a location under an exact document, not a semantic entity."),
    source("rfc8259", "RFC 8259 JSON", "IETF", "https://www.rfc-editor.org/rfc/rfc8259", "JSON interchange grammar", "Syntactic JSON validity does not determine interface semantics."),
    source("yaml122", "YAML 1.2.2 Specification", "YAML Language Development Team", "https://yaml.org/spec/1.2.2/", "YAML representation and JSON compatibility boundaries", "Equivalent-looking YAML and JSON carriers do not imply identical source spans or extension behavior."),
    source("dcat3", "Data Catalog Vocabulary 3", "W3C", "https://www.w3.org/TR/vocab-dcat-3/", "DataService, endpoint URL, endpoint description and conformance target distinctions", "A service description does not prove an endpoint occurrence implements it."),
    source("cargo_manifest", "Cargo Manifest Format", "Rust Project", "https://doc.rust-lang.org/cargo/reference/manifest.html", "package declarations, targets, dependencies and features", "A manifest is not a resolved graph, lockfile, build or artifact."),
    source("cargo_resolver", "Cargo Dependency Resolution", "Rust Project", "https://doc.rust-lang.org/cargo/reference/resolver.html", "version, feature and target-dependent dependency resolution", "One resolver result is not portable across profiles, targets or resolver editions."),
    source("cargo_metadata", "cargo metadata", "Rust Project", "https://doc.rust-lang.org/cargo/commands/cargo-metadata.html", "machine-readable package and resolved dependency graphs", "Metadata output is editioned and does not prove compilation or conformance."),
    source("cargo_pkgid", "Cargo Package ID Specifications", "Rust Project", "https://doc.rust-lang.org/cargo/reference/pkgid-spec.html", "fully qualified package identities inside a graph", "An abbreviated name is not identity when the graph is ambiguous."),
    source("npm_lock", "npm package-lock.json", "npm", "https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json", "exact dependency tree and lockfile semantics", "A lockfile is ecosystem-specific and does not prove installed or executed code."),
    source("spdx301", "SPDX Specification 3.0.1 Package", "SPDX", "https://spdx.github.io/spdx-spec/v3.0.1/model/Software/Classes/Package/", "package artifact identity and relationships", "An SBOM package graph need not equal a resolver, build-unit or runtime-load graph."),
    source("cyclonedx17", "CycloneDX 1.7 Dependency Graph", "OWASP CycloneDX", "https://cyclonedx.org/docs/1.7/json/", "component and service dependency graph representation", "Omitted graph nodes can mean unknown rather than dependency-free."),
    source("slsa12", "SLSA 1.2", "OpenSSF", "https://slsa.dev/spec/v1.2/", "artifact and build provenance tied to exact inputs", "Provenance is not package semantic correctness or dependency completeness."),
    source("dbt_manifest", "dbt Manifest JSON", "dbt Labs", "https://docs.getdbt.com/reference/artifacts/manifest-json", "project resources, dependencies, selectors and generated manifest artifacts", "A generated manifest does not by itself establish provider execution or result acceptance."),
]


CONTEXT_SPECS = [
    ("interface_contract", "Which exact dialect documents and references compile into a provider-neutral interface contract without claiming deployed behavior?", ["dialect and dialect edition", "entry document and base URI", "reference/resource closure", "operations, messages, schemas, security requirements and declared limits", "unsupported and implementation-defined behavior"], ["network retrieval", "deployed endpoint occurrence", "provider qualification", "business authorization", "request execution"]),
    ("provider_offer_closure", "Which exact descriptions, capability assertions and evidence references form one provider-offer closure without promoting declarations to observations?", ["offer identity and edition", "interface-description bindings", "capability/reference graph", "declaration/observation/evidence posture", "validity and residual gaps"], ["provider selection", "deployment probing", "qualification verdict", "credentials", "effect authorization"]),
    ("package_closure", "Which manifest, constraints, resolver policy, lock state and target selection form an exact package closure without claiming a build?", ["package and source identity", "manifest declarations", "constraints and feature/profile policy", "resolver and lock editions", "resolved target-specific graph and unknowns"], ["source download", "build-unit execution", "artifact production", "license/security acceptance", "runtime load graph"]),
]

CONTEXTS = [{
    "context_id": f"context.drc.{key}", "name": key.replace("_", " ").title(),
    "sovereign_question": question, "inside": inside, "outside": outside,
    "owner": f"authority.drc.{key}", "invariants": [
        "declaration, resolution, observation, qualification and effect are separate verdicts",
        "every input, dialect, resolver, policy and target edition is explicit",
        "unknown, cyclic, ambiguous, unsupported and unreachable references remain typed",
        "pure closure construction performs no ambient network, filesystem, clock or environment access",
    ], "status": "specified_candidate",
} for key, question, inside, outside in CONTEXT_SPECS]

LIBRARY_SPECS = [
    ("library.api.contract_parser", "interface_contract", "semantic_pure", "compile an exact interface-description carrier and dialect profile into typed provider-neutral interface IR", ["library.schema_registry.reference_closure"]),
    ("library.provider_offer.reference_closure", "provider_offer_closure", "policy_pure", "close exact provider-offer, interface, capability, evidence and validity references without qualifying the provider", ["library.api.contract_parser", "library.schema_registry.reference_closure"]),
    ("library.package.reference_closure", "package_closure", "algorithm_pure", "form an exact ecosystem/profile/target-qualified package dependency closure from declared and resolved graph evidence", []),
]

COMMON_DECISIONS = ["identity", "edition", "input_cut", "reference_profile", "base_identity", "cycle_policy", "unknown_policy", "extension_policy", "loss_policy", "finite_budget", "canonicalization", "digest"]
SPECIFIC_DECISIONS = {
    "interface_contract": ["carrier_format", "dialect", "dialect_edition", "entry_document", "root_object", "implicit_connection_policy", "schema_dialect", "security_requirement_semantics", "operation_identity", "implementation_defined_behavior"],
    "provider_offer_closure": ["offer_identity", "offer_issuer", "interface_binding", "capability_assertion_posture", "observation_binding", "evidence_scope", "validity", "conflict_precedence", "residual_gap", "qualification_separation"],
    "package_closure": ["ecosystem", "manifest_profile", "package_source_identity", "constraint_semantics", "resolver_edition", "lock_state", "feature_profile", "dependency_scope", "target_profile", "unknown_dependency_posture", "resolved_graph_identity", "build_graph_separation"],
}

DECISIONS = []
for key, *_ in CONTEXT_SPECS:
    for name in COMMON_DECISIONS + SPECIFIC_DECISIONS[key]:
        DECISIONS.append({
            "decision_id": f"decision.drc.{key}.{name}", "owner_context": f"context.drc.{key}",
            "question": f"What exact {name.replace('_', ' ')} applies?", "default": None,
            "default_law": "forbidden", "binding_phase": "intent_or_semantic_closure", "status": "declared",
        })

OPERATION_SPECS = {
    "interface_contract": ["validate_carrier", "select_dialect", "parse_entry_document", "resolve_interface_references", "normalize_interface_contract", "classify_unsupported_behavior", "canonicalize_interface_contract"],
    "provider_offer_closure": ["validate_offer_declaration", "bind_interface_description", "resolve_capability_references", "bind_observation_and_evidence", "classify_conflicts_and_residuals", "form_provider_offer_closure", "canonicalize_provider_offer_closure"],
    "package_closure": ["validate_package_manifest", "bind_ecosystem_and_resolver_profile", "resolve_declared_constraints", "validate_lock_or_resolver_snapshot", "select_features_scopes_and_target", "form_package_reference_closure", "classify_unknown_dependencies", "canonicalize_package_closure"],
}

OPERATIONS = []
for context, names in OPERATION_SPECS.items():
    stem = "".join(word.title() for word in context.split("_"))
    for name in names:
        OPERATIONS.append({
            "operation_ref": f"operation.drc.{context}.{name}", "owner_context": f"context.drc.{context}",
            "input_types": [f"{stem}Input", f"{stem}Policy"],
            "output_type": f"Result<{''.join(word.title() for word in name.split('_'))}Outcome,DeclarationClosureRefusal>",
            "purity": "pure", "refusals": ["DialectUnsupported", "ReferenceAmbiguous", "ReferenceCycleRejected", "ReferenceUnavailableInCut", "BudgetExceeded", "CanonicalizationFailed"],
        })

LIBRARIES = []
for library_id, context, kind, responsibility, dependencies in LIBRARY_SPECS:
    stem = "".join(word.title() for word in library_id.split(".")[-2:])
    LIBRARIES.append({
        "library_id": library_id, "semantic_owner_context": f"context.drc.{context}",
        "name": library_id.removeprefix("library.").replace(".", " ").title(),
        "library_kind": kind, "effect_boundary": "pure_no_io", "status": "specified",
        "candidate_responsibility": responsibility, "dependencies": dependencies,
        "public_types": [f"{stem}Declaration", f"{stem}Profile", f"{stem}Closure", f"{stem}Digest", "DeclarationClosureRefusal"],
        "public_traits": [f"{stem}Algebra"],
        "operations": [row for row in OPERATIONS if row["owner_context"] == f"context.drc.{context}"],
        "operation_refs": [row["operation_ref"] for row in OPERATIONS if row["owner_context"] == f"context.drc.{context}"],
        "decision_refs": [row["decision_id"] for row in DECISIONS if row["owner_context"] == f"context.drc.{context}"],
        "laws": CONTEXTS[[row[0] for row in CONTEXT_SPECS].index(context)]["invariants"],
        "must_not_own": CONTEXTS[[row[0] for row in CONTEXT_SPECS].index(context)]["outside"],
        "oracles": ["reference-cycle and ambiguity fixtures", "base-identity and edition mutation tests", "canonical digest properties", "declaration-versus-observation negative twins", "two independent implementation differentials"],
        "qualification_required": False,
        "evidence_refs": [row["source_id"] for row in SOURCES],
    })

COMPILER = []
for library in LIBRARIES:
    stem = library["library_id"].removeprefix("library.")
    COMPILER.extend([
        {"record_kind": "capability_requirement", "requirement_id": f"requirement.{stem}.implementation", "subject_ref": library["library_id"], "required_operations": library["operation_refs"], "fallback_law": "refuse", "status": "declared"},
        {"record_kind": "capability_offer", "offer_id": f"offer.{stem}.reference", "subject_ref": library["library_id"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
        {"record_kind": "binding_rule", "binding_rule_id": f"binding.{stem}", "requirement_ref": f"requirement.{stem}.implementation", "offer_ref": f"offer.{stem}.reference", "structural_match": True, "selectable": False, "selection_law": "A structural contract match never promotes an unqualified implementation.", "status": "declared"},
    ])

NEGATIVE_ROWS = [
    ("syntax_behavior", "A valid interface document proves deployed behavior.", "Retain declaration-only posture until occurrence evidence is qualified."),
    ("api_version", "Interface spec edition, document edition and deployed API edition are interchangeable.", "Bind all three identities separately."),
    ("implicit_fetch", "A URL-shaped reference authorizes network retrieval.", "Resolve only from an explicit supplied resource cut or effect request."),
    ("pointer_identity", "A JSON Pointer is semantic entity identity.", "Scope it to the exact document resource and edition."),
    ("dynamic_static", "dynamicRef can always be closed statically.", "Retain runtime/dynamic-scope obligation where the dialect requires it."),
    ("schema_api", "Schema closure equals interface contract closure.", "Preserve operations, bindings, security and implicit connections."),
    ("offer_behavior", "A provider offer declaration is an observed capability.", "Require separate occurrence observation evidence."),
    ("offer_qualification", "A closed offer graph is a qualified provider.", "Execute the exact qualification profile separately."),
    ("endpoint_authority", "An endpoint description grants access or authorization.", "Require external authority and credential references."),
    ("latest_offer", "Unversioned latest offer references are safe defaults.", "Refuse or bind an authorized immutable edition."),
    ("manifest_lock", "A package manifest is a lockfile.", "Separate declared constraints from selected versions."),
    ("lock_resolve", "A lockfile is a universal resolver result.", "Bind ecosystem, resolver, feature, profile and target editions."),
    ("resolve_build", "A resolved package graph is the build-unit graph.", "Retain target/build-tool generated-unit evidence separately."),
    ("build_runtime", "A build dependency graph is the runtime-load graph.", "Model runtime loading as a separate occurrence graph."),
    ("name_identity", "A package name uniquely identifies a package.", "Require source, namespace and edition-qualified identity."),
    ("omitted_empty", "An omitted dependency node means dependency-free.", "Retain unknown/opaque graph posture."),
    ("feature_default", "Default features are semantic defaults.", "Bind feature selection as build/package policy only."),
    ("target_independent", "One resolved closure applies to every target.", "Bind target and platform predicates."),
    ("sbom_resolver", "An SBOM dependency graph is the resolver graph.", "Preserve assertion issuer, scope and graph kind."),
    ("provenance_conformance", "Build provenance proves library semantic conformance.", "Keep provenance and conformance verdicts separate."),
    ("cycle_flatten", "Reference cycles may be silently flattened.", "Apply the dialect/profile cycle law and retain recursion explicitly."),
    ("extension_ignore", "Unknown extensions can always be ignored.", "Apply explicit extension and loss policy."),
    ("partial_closure", "Partial closure may be labeled complete.", "Emit residual references and completeness posture."),
    ("agent_fill", "A model or agent may invent a missing reference target.", "Retain proposal taint and refuse deterministic closure."),
    ("one_impl", "One parser or resolver proves portability.", "Require two independent qualified implementations."),
]
NEGATIVES = [{"negative_id": f"negative.drc.{key}", "unsafe_inference": unsafe, "required_behavior": required, "status": "active"} for key, unsafe, required in NEGATIVE_ROWS]

LENS_NAMES = ["value", "semantic", "behavior", "authority", "consistency", "variability", "software", "operation", "economics", "empirical", "analytical", "system"]
LENSES = [{"lens_id": f"lens.drc.{name}", "lens": name, "finding": "Interface, offer and package closures have different owners, reference laws, evidence and downstream effects.", "boundary_consequence": "Retain three libraries and compose existing query syntax plus query binding rather than minting a query-compiler monolith.", "status": "applied"} for name in LENS_NAMES]

VERDICTS = [
    {"verdict_id": "verdict.drc.interface_offer", "subject_refs": ["library.api.contract_parser", "library.provider_offer.reference_closure"], "disposition": "retain_separate", "rationale": "Interface grammar/semantics and provider capability/evidence closure have different identities and qualification posture.", "status": "candidate_boundary_adjudicated_not_ratified"},
    {"verdict_id": "verdict.drc.package", "subject_refs": ["library.package.reference_closure", "library.schema_registry.reference_closure"], "disposition": "retain_separate", "rationale": "Package resolution owns constraints, features, scopes, lock state and target selection; schema closure owns schema-resource reference semantics.", "status": "candidate_boundary_adjudicated_not_ratified"},
    {"verdict_id": "verdict.drc.query", "subject_refs": ["library.qck.query-syntax", "library.qck.query-binding"], "disposition": "compose_existing", "rationale": "Parsing and semantic binding already expose the required query compilation seams; a new monolith would duplicate them.", "status": "candidate_boundary_adjudicated_not_ratified"},
]

PROFILES = [{
    "record_kind": "qualification_profile", "receipt_id": f"profile.{row['library_id'].removeprefix('library.')}",
    "subject_ref": row["library_id"], "edition": EDITION, "claim": "Exact implementation preserves declared closure laws and refusals.",
    "scope": ["exact implementation/build", "exact dialect/resolver/profile editions", "exact operation set"],
    "fixtures": row["oracles"], "oracles": row["oracles"], "configuration": {}, "environment": {}, "results": [],
    "limitations": ["Unexecuted profile proves no capability.", "Passing one scope does not prove another dialect, ecosystem or target."],
    "status": "template_not_executed",
} for row in LIBRARIES]

FILES = {
    "sources.jsonl": SOURCES, "bounded-contexts.jsonl": CONTEXTS, "decision-points.jsonl": DECISIONS,
    "operations.jsonl": OPERATIONS, "library-contracts.jsonl": LIBRARIES, "compiler-contracts.jsonl": COMPILER,
    "negative-twins.jsonl": NEGATIVES, "boundary-lenses.jsonl": LENSES, "boundary-verdicts.jsonl": VERDICTS,
    "qualification-profiles.jsonl": PROFILES,
}


def render(rows: list[dict]) -> str:
    return "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for row in rows) + "\n"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    inventory = {}
    for name, rows in FILES.items():
        text = render(rows)
        (HERE / name).write_text(text, encoding="utf-8")
        inventory[name] = {"records": len(rows), "sha256": hashlib.sha256(text.encode()).hexdigest()}
    manifest = {"manifest_id": "declaration_reference_closure_v0_1_0", "edition": EDITION, "as_of": AS_OF, "completion_claim": False, "qualified_implementation_count": 0, "files": inventory, "status": "specified_unimplemented_open_world"}
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS drc: {len(SOURCES)} sources, {len(CONTEXTS)} contexts, {len(DECISIONS)} decisions, {len(LIBRARIES)} libraries, {len(OPERATIONS)} operations, {len(NEGATIVES)} negative twins")


if __name__ == "__main__":
    main()
