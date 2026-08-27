#!/usr/bin/env python3
"""Build the deterministic adjudication of the 30 multi-owner library candidates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REGISTRY = ROOT / "research/domain_atlas/compiler/library_registry/registry.jsonl"
AS_OF = "2026-08-26"


SOURCES = [
    {"source_id": "source.shared-owner.parnas", "title": "On the Criteria To Be Used in Decomposing Systems into Modules", "authority": "D. L. Parnas", "url": "https://dl.acm.org/doi/10.1145/361598.361623", "supports": "information-hiding boundaries and independently changeable design decisions"},
    {"source_id": "source.shared-owner.iso42010", "title": "ISO/IEC/IEEE 42010 Architecture Description", "authority": "ISO/IEC/IEEE", "url": "https://www.iso.org/standard/74393.html", "supports": "stakeholders, concerns, viewpoints, correspondences and architecture decisions"},
    {"source_id": "source.shared-owner.skos", "title": "SKOS Simple Knowledge Organization System Reference", "authority": "W3C", "url": "https://www.w3.org/TR/skos-reference/", "supports": "concept schemes, labels, semantic relations, mappings and the separation of informal KOS from formal ontology"},
    {"source_id": "source.shared-owner.prov", "title": "PROV-O: The PROV Ontology", "authority": "W3C", "url": "https://www.w3.org/TR/prov-o/", "supports": "provenance entities, activities, agents and qualified relations"},
    {"source_id": "source.shared-owner.focus", "title": "FOCUS Specification 1.2", "authority": "FinOps Open Cost and Usage Specification", "url": "https://focus.finops.org/docs/specification/v1-2/", "supports": "normalized billing data and allocation-related cost semantics"},
    {"source_id": "source.shared-owner.openslo", "title": "OpenSLO Specification", "authority": "OpenSLO", "url": "https://openslo.com/", "supports": "service-level indicator and objective declarations"},
    {"source_id": "source.shared-owner.jsonschema", "title": "JSON Schema Core 2020-12", "authority": "JSON Schema", "url": "https://json-schema.org/draft/2020-12/json-schema-core.html", "supports": "schema resource identity, dialect and reference semantics"},
    {"source_id": "source.shared-owner.cargo-resolver", "title": "Cargo Dependency Resolution", "authority": "Rust Project", "url": "https://doc.rust-lang.org/cargo/reference/resolver.html", "supports": "constraint, feature, target and resolved-graph distinctions"},
]


# subject, disposition, unique owner, existing replacements, proposed replacements, rationale
SPECS = [
    ("library.gmo.accountability", "retain_unique_owner", "gmo.context.ownership_accountability", [], [], "Accountability owns decision responsibility; stewardship and custody are separately identified contributor roles."),
    ("library.gmo.assurance_workflow", "replaced_and_retired", "gmo.context.certification", ["library.gmo.certification_lifecycle", "library.gmo.assurance_appraisal_plan", "library.gmo.governance_issue_workflow", "library.gmo.change_review_policy"], [], "Appraisal planning, certification, issue remediation and change governance have different aggregates, authorities, terminal states and evidence."),
    ("library.gmo.catalog_discovery", "replaced_and_retired", "gmo.context.search_discovery", ["library.gmo.catalog_listing_contract", "library.gmo.discovery_query"], [], "A catalog assertion/listing is governed content; ranking, retrieval and discovery are query algorithms over that content."),
    ("library.gmo.classification_privacy", "replaced_and_retired", "gmo.context.classification", ["library.gmo.classification_assignment", "library.gmo.privacy_purpose_binding", "library.spt.privacy_vocabulary"], [], "Classification and privacy purpose differ in issuer, validity, authority and downstream policy consequence."),
    ("library.gmo.data_product_contracts", "replaced_and_retired", "gmo.context.data_product", ["library.data_contract.contract_identity", "library.data_contract.data_schema_binding", "library.data_product_publication.product_edition", "library.data_product_publication.accountability_binding"], [], "A data product packages but does not own producer-consumer contract, schema binding, publication edition or accountability semantics."),
    ("library.gmo.entity_resolution", "replaced_and_retired", "gmo.context.entity_resolution", ["library.csp.identity.entity-resolution", "library.csp.identity.merge-split-ledger", "library.master_data.survivorship_projection", "library.gmo.match_policy"], [], "Entity identity, candidate matching, match policy, merge/split history and survivorship projection are independent decisions."),
    ("library.gmo.identity_kernel", "replaced_and_retired", "gmo.context.asset_identity", ["library.csp.identity.scoped-identifier", "library.csp.identity.namespace-registry", "library.csp.identity.version-identity", "library.san_content_identity"], [], "Asset identity must compose the sovereign identifier, namespace, version and content-identity contracts instead of redefining them."),
    ("library.gmo.lineage_core", "replaced_and_retired", "gmo.context.lineage", ["library.lpe.lineage-core", "library.lpe.prov-statement-algebra","library.lpe.provenance-assertion", "library.lpe.provenance-bundle", "library.lpe.field-lineage", "library.lpe.formula-provenance"], [], "Lineage topology and provenance assertions are related but non-identical contracts already owned by the lineage/provenance universe."),
    ("library.gmo.master_authority", "replaced_and_retired", "gmo.context.master_authority", ["library.master_data.domain_identity", "library.master_data.source_authority", "library.master_data.survivorship_projection", "library.gmo.golden_record_edition"], [], "Source authority is a decision right; a golden record is a reproducible projection with its own edition and lineage."),
    ("library.gmo.ontology_core", "replaced_and_retired", "gmo.context.ontology", ["library.ontology_model.axiom_profile", "library.ontology_model.ontology_mapping", "library.ontology_model.reasoning_entailment", "library.ontology_model.identity_import_closure"], [], "Ontology axioms, mappings, import closure and entailment profiles already have separate change and conformance boundaries."),
    ("library.gmo.policy_client", "retain_unique_owner", "gmo.context.policy_enforcement", [], [], "The client is an enforcement-side effect port; entitlements are supplied inputs and never become its semantic owner."),
    ("library.gmo.records_governance", "retain_unique_owner", "gmo.context.retention_disposition", ["library.lpe.retention-policy"], [], "Disposition owns the decision; legal hold contributes a precedence constraint and external authority, not joint ownership."),
    ("library.gmo.reference_core", "replaced_and_retired", "gmo.context.reference_data", ["library.reference_data.reference_set", "library.reference_data.code_set_lifecycle", "library.reference_data.crosswalk_mapping"], [], "Reference sets, code-set lifecycle and crosswalk mappings have different identity, compatibility and loss laws."),
    ("library.gmo.schema_contracts", "replaced_and_retired", "gmo.context.technical_schema", ["library.san_wire_schema", "library.schema_registry.subject_identity", "library.schema_registry.version_registry", "library.schema_registry.compatibility", "library.schema_registry.reference_closure"], [], "Technical schema meaning is not registry subject/version lifecycle, compatibility policy or reference closure."),
    ("library.gmo.semantic_query", "replaced_and_retired", "gmo.context.semantic_model", ["library.cbv.semantic_query_types", "library.smf.semantic_query_canonicalizer", "library.smf.semantic_query_gateway"], [], "Semantic query types, canonicalization and effectful query dispatch must remain independently substitutable."),
    ("library.gmo.taxonomy_core", "retain_unique_owner", "gmo.context.taxonomy", [], [], "The taxonomy owns the concept scheme; hierarchy is one qualified relation structure and formal ontology entailment remains excluded."),
    ("library.gmo.terminology_core", "retain_unique_owner", "gmo.context.terminology", ["library.business_glossary.term_identity"], [], "Terminology owns concept/designation semantics; a business glossary curates and publishes scoped terminology."),
    ("library.platform-commercial-support.allocation-core", "retain_unique_owner", "context.platform-commercial-support.cost-allocation", [], [], "Cost allocation owns allocation rules and traces; chargeback/showback are downstream presentations or postings."),
    ("library.platform-commercial-support.commercial-credit-preauthorization", "retain_unique_owner_after_rename", "context.platform-commercial-support.budget-control", [], [], "Commercial money/credit preauthorization is distinct from runtime resource-budget precharge; the completed rename prevents false substitution."),
    ("library.platform-commercial-support.commercial-identities", "replaced_and_retired", "context.platform-commercial-support.account-registry", ["library.platform-commercial-support.account_identity", "library.platform-commercial-support.customer_party_identity", "library.platform-commercial-support.billing_account_identity", "library.platform-commercial-support.legal_entity_binding"], [], "Platform account, commercial customer, billing account and external legal entity have different issuers and lifecycles."),
    ("library.platform-commercial-support.effective-interval", "replaced_and_retired", "context.platform-commercial-support.contract-amendment", ["library.csp.time.interval-algebra"], [], "Half-open interval algebra is a shared temporal primitive; amendment, cycle and renewal retain their domain-specific policies."),
    ("library.platform-commercial-support.entitlement-algebra", "replaced_and_retired", "context.platform-commercial-support.entitlement-policy", ["library.csp.authority.entitlement", "library.csp.authority.policy-algebra", "library.platform-commercial-support.feature_definition", "library.platform-commercial-support.entitlement_decision_policy", "library.platform-commercial-support.entitlement_grant", "library.platform-commercial-support.license_seat"], [], "Feature definition, grant occurrence, license-seat allocation and entitlement decision policy are not one aggregate."),
    ("library.platform-commercial-support.exit-manifest", "retain_unique_owner", "context.platform-commercial-support.portability-export", [], [], "The export authority owns the manifest; supplier exit, decommission and residual obligations consume it but require separate completion evidence."),
    ("library.platform-commercial-support.invoice-arithmetic", "retain_unique_owner", "context.platform-commercial-support.invoice", ["library.csp.quantity.money-core"], [], "Invoice arithmetic owns line/total/rounding and linked adjustment laws; credit notes are correction occurrences under invoice authority."),
    ("library.platform-commercial-support.lifecycle-reducer", "replaced_and_retired", "context.platform-commercial-support.subscription", ["library.platform-commercial-support.subscription_lifecycle", "library.platform-commercial-support.product_order_lifecycle", "library.platform-commercial-support.service_order_lifecycle", "library.platform-commercial-support.support_case_lifecycle", "library.platform-commercial-support.incident_lifecycle"], [], "These five lifecycles have incompatible commands, transitions, authorities, terminal facts and compensation rules."),
    ("library.platform-commercial-support.meter-algebra", "replaced_and_retired", "context.platform-commercial-support.meter-definition", ["library.platform-commercial-support.meter_definition", "library.platform-commercial-support.usage_event", "library.platform-commercial-support.usage_aggregation"], [], "Meter definition, immutable usage occurrence and derived aggregate have different identities and correction/replay laws."),
    ("library.platform-commercial-support.money", "replaced_and_retired", "context.platform-commercial-support.price-book", ["library.csp.quantity.money-core"], [], "Money is a shared exact amount/currency primitive; price, balance, charge and invoice remain domain values using it."),
    ("library.platform-commercial-support.rating-core", "retain_unique_owner", "context.platform-commercial-support.rating", ["library.csp.quantity.money-core"], [], "Rating owns the deterministic usage-plus-price-to-rated-charge derivation; the price book is an immutable input edition."),
    ("library.platform-commercial-support.service-level-evaluator", "replaced_and_retired", "context.platform-commercial-support.service-objective", ["library.platform-commercial-support.slo_evaluator", "library.platform-commercial-support.sla_eligibility", "library.platform-commercial-support.service_credit_decision"], [], "SLO evaluation, contractual SLA eligibility and credit award are separate evidence and authority transitions."),
    ("library.platform-commercial-support.tenant-identity", "retain_unique_owner", "context.platform-commercial-support.tenant-registry", [], [], "The registry owns TenantId issuance/lifecycle; hierarchy contributes scoped relations without co-owning identity."),
]


LAWS = [
    "Exactly one bounded context or explicit shared-contract authority owns a library's meaning.",
    "A contributor, consumer, referenced aggregate or provider is not a co-owner.",
    "A convenience facade spanning independently changing decisions is not admitted as a semantic library.",
    "Replacement by composition is complete only when every operation, law, refusal and migration edge is covered or explicitly retired.",
    "A rejected or split-pending candidate is never selectable by the compiler.",
    "Representation reuse, shared vocabulary or common arithmetic does not collapse domain authority.",
]

RENAMES = [{
    "record_kind": "library_identity_crosswalk",
    "crosswalk_id": "crosswalk.shared-owner.commercial-credit-preauthorization",
    "legacy_ref": "library.platform-commercial-support.budget-precharge",
    "canonical_ref": "library.platform-commercial-support.commercial-credit-preauthorization",
    "relation": "renamed_to_remove_semantic_collision",
    "compatibility_alias_permitted": False,
    "reason": "Commercial credit/money reservation and runtime resource-budget reservation have different units, authorities, effects and reconciliation laws.",
}]


def load_library_ids() -> set[str]:
    ids = set()
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("record_kind") == "library_contribution":
            ids.add(row["library_id"])
    return ids


def build() -> dict[str, list[dict]]:
    known = load_library_ids()
    verdicts = []
    edges = []
    gaps = []
    crosswalks = list(RENAMES)
    for subject, disposition, owner, replacements, proposed, rationale in SPECS:
        verdict_id = f"verdict.shared-owner.{subject.removeprefix('library.').replace('.', '-')}"
        verdicts.append({
            "record_kind": "library_boundary_verdict", "verdict_id": verdict_id,
            "subject_ref": subject, "disposition": disposition, "unique_owner_context_ref": owner,
            "existing_replacement_refs": replacements, "proposed_replacement_refs": proposed,
            "rationale": rationale, "laws": LAWS,
            "compiler_selectable_after_verdict": disposition in {"retain_unique_owner", "retain_unique_owner_after_rename"},
            "status": "adjudicated_candidate_not_ratified",
            "evidence_refs": [row["source_id"] for row in SOURCES],
        })
        for replacement in replacements:
            edges.append({
                "record_kind": "replacement_edge", "edge_id": f"edge.{subject.removeprefix('library.').replace('.', '-')}.{replacement.removeprefix('library.').replace('.', '-')}",
                "from_ref": subject, "to_ref": replacement, "to_ref_exists": replacement in known,
                "coverage_status": "candidate_requires_operation_law_refusal_crosswalk",
                "non_equivalence_law": "Reuse is admitted only for the exact owned contract; surrounding domain semantics remain outside the replacement.",
            })
        if disposition == "replaced_and_retired":
            crosswalks.append({
                "record_kind": "library_composition_crosswalk",
                "crosswalk_id": f"crosswalk.shared-owner.{subject.removeprefix('library.').replace('.', '-')}",
                "legacy_ref": subject,
                "canonical_refs": replacements,
                "relation": "retired_and_replaced_by_composition",
                "compatibility_alias_permitted": False,
                "reason": rationale,
            })
        if disposition not in {"retain_unique_owner", "retain_unique_owner_after_rename", "replaced_and_retired"}:
            gaps.append({
                "record_kind": "boundary_closure_gap", "gap_id": f"gap.shared-owner.{subject.removeprefix('library.').replace('.', '-')}",
                "subject_ref": subject, "disposition": disposition, "blocking": True,
                "required_existing_refs": replacements, "required_proposed_refs": proposed,
                "resolution_condition": "Publish exact replacement APIs and a total operation/law/refusal/migration crosswalk; remove or explicitly retire the coarse candidate; rerun product and dependency closure.",
                "prohibited_fallbacks": ["pick the first listed context", "retain a utility bag facade", "treat shared DTOs as shared meaning", "mark resolved from names alone"],
                "status": "open",
            })
    negatives = [
        {"negative_id": "negative.shared-owner.first-context", "unsafe_inference": "The first context in a list owns the meaning.", "required_behavior": "Require an explicit verdict and owner authority."},
        {"negative_id": "negative.shared-owner.consumers-own", "unsafe_inference": "Every consuming context co-owns a shared library.", "required_behavior": "Model consumers as contributor/import relations."},
        {"negative_id": "negative.shared-owner.generic-reducer", "unsafe_inference": "Identical state-machine mechanics imply identical lifecycle semantics.", "required_behavior": "Keep domain commands, guards, refusals and terminal facts separate."},
        {"negative_id": "negative.shared-owner-carrier", "unsafe_inference": "Use of the same carrier or primitive collapses the domain libraries using it.", "required_behavior": "Reuse the primitive while preserving domain value and authority boundaries."},
        {"negative_id": "negative.shared-owner-replacement", "unsafe_inference": "Naming replacement libraries proves semantic coverage.", "required_behavior": "Require total operation, law, refusal and migration crosswalk evidence."},
        {"negative_id": "negative.shared-owner-agent", "unsafe_inference": "An agent may resolve an ownership collision from names or popularity.", "required_behavior": "Agents may propose; only governed evidence-backed adjudication changes the registry."},
    ]
    return {"sources.jsonl": SOURCES, "verdicts.jsonl": verdicts, "replacement-edges.jsonl": edges, "closure-gaps.jsonl": gaps, "identity-crosswalks.jsonl": crosswalks, "negative-twins.jsonl": negatives}


def render(rows: list[dict]) -> str:
    return "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows) + "\n"


def main() -> None:
    files = build()
    inventory = {}
    for name, rows in files.items():
        data = render(rows)
        (HERE / name).write_text(data, encoding="utf-8")
        inventory[name] = {"records": len(rows), "sha256": hashlib.sha256(data.encode()).hexdigest()}
    counts = {"verdicts": len(files["verdicts.jsonl"]), "replacement_edges": len(files["replacement-edges.jsonl"]), "closure_gaps": len(files["closure-gaps.jsonl"])}
    manifest = {"manifest_id": "shared_owner_boundary_adjudication_v0_1_0", "as_of": AS_OF, "completion_claim": False, "counts": counts, "files": inventory, "status": "candidate_adjudication_requires_source_projection"}
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    dispositions = {}
    for row in files["verdicts.jsonl"]:
        dispositions[row["disposition"]] = dispositions.get(row["disposition"], 0) + 1
    print(f"BUILD PASS shared-owner: 30 verdicts; dispositions={dict(sorted(dispositions.items()))}; {len(files['closure-gaps.jsonl'])} blocking closure gaps")


if __name__ == "__main__":
    main()
