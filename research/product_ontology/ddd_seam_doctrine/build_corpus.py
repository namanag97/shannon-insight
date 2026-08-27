#!/usr/bin/env python3
"""Build the evidence-backed DDD/product/library seam doctrine."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"


def encode(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


SOURCES = [
    {"source_id":"source.ddd.evans.reference","title":"Domain-Driven Design Reference: Definitions and Pattern Summaries","author":"Eric Evans","uri":"https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf","claim_scope":"bounded context, ubiquitous language, model-driven design, aggregates, modules, conceptual contours, context mapping, generic subdomains and core-domain distillation","scope_limit":"DDD defines modeling boundaries and relationships; it does not define SAN product, commercial packaging or library qualification criteria."},
    {"source_id":"source.ddd.fowler.ddd","title":"Domain Driven Design","author":"Martin Fowler","uri":"https://martinfowler.com/bliki/DomainDrivenDesign.html","claim_scope":"DDD as evolutionary software modeling of complex domain processes and rules","scope_limit":"A concise synthesis, not a replacement for the canonical pattern definitions."},
    {"source_id":"source.ddd.fowler.bounded-context","title":"Bounded Context","author":"Martin Fowler","uri":"https://martinfowler.com/bliki/BoundedContext.html","claim_scope":"multiple internally unified models, linguistic boundaries and explicit context relationships","scope_limit":"A bounded context is not automatically a deployment, team, product or commercial boundary."},
    {"source_id":"source.ddd.eventstorming","title":"EventStorming","author":"Alberto Brandolini","uri":"https://www.eventstorming.com/","claim_scope":"collaborative exploration of business flows, competing perspectives, services and candidate software boundaries","scope_limit":"Workshop artifacts are discovery evidence, not automatically ratified contexts, aggregates or products."},
    {"source_id":"source.boundary.team-topologies","title":"Modern Software Delivery / Organization Dynamics with Team Topologies","author":"Matthew Skelton and Manuel Pais","uri":"https://teamtopologies.com/s/Organization-Dynamics-with-Team-Topologies-Mini-book-MB80.pdf","claim_scope":"stream-aligned ownership, cognitive load, service interaction and thinnest viable platform boundaries","scope_limit":"Team topology informs operability and flow; Conway alignment cannot override semantic ownership."},
    {"source_id":"source.product.data-product-design","title":"Designing Data Products","author":"Kiran Prakash","uri":"https://martinfowler.com/articles/designing-data-products.html","claim_scope":"work backward from use cases, overlay unrelated use cases, assign one domain owner, define SLOs and preserve independent value","scope_limit":"Data-product guidance applies to analytical data adoption units, not every SAN platform or semantic product kind."},
    {"source_id":"source.product.svpg","title":"Product Management: An Introduction","author":"Silicon Valley Product Group","uri":"https://www.svpg.com/product-management-an-introduction/","claim_scope":"durable product teams solve customer and business problems for outcomes rather than merely shipping features","scope_limit":"Product operating-model guidance does not establish a DDD model or technical consistency boundary."},
]


KINDS = [
    ("domain", "Area of knowledge or activity to which the software is applied.", "Research scope; not itself a boundary or adoption unit."),
    ("subdomain", "Cohesive problem area classified as core, supporting or generic relative to a strategy.", "Problem-space division; not automatically a bounded context, team, service or product."),
    ("bounded_context", "Explicit boundary within which one model and ubiquitous language are defined, internally consistent and applicable.", "Semantic applicability and translation boundary; may contain many aggregates and libraries and may support multiple products."),
    ("aggregate", "Cluster with a root that enforces synchronous invariants and transactional consistency.", "Consistency boundary inside a bounded context; not an integration, deployment or product boundary."),
    ("domain_service", "Named domain operation that belongs to no natural entity or value object.", "Behavior in a bounded context; not automatically independently adoptable."),
    ("capability", "Typed selectable behavior needed or offered by a composition.", "Composition axis; can cross product and implementation graphs without owning all involved meanings."),
    ("library", "Versioned reusable semantic or implementation contract with explicit operations, laws, dependencies and decisions.", "Build/reuse unit; may implement part of one context or serve several contexts through published contracts."),
    ("provider", "Concrete implementation or operated resource offer that can satisfy a typed requirement after qualification.", "Implementation/operation axis; does not inherit semantic authority from use."),
    ("product", "Governed, independently consumable promise of outcomes to defined users with owned adoption, service, lifecycle, evidence and exit.", "Adoption and outcome boundary; may compose several bounded contexts, capabilities, libraries and providers."),
    ("suite", "Commercial or internal package of independently governed products.", "Packaging only; it does not merge semantic owners or lifecycle identities."),
    ("solution_pack", "Vertical composition of reusable products, capabilities and domain vocabulary for a class of enterprise needs.", "Configuration/composition boundary; it must not fork horizontal semantics merely by industry name."),
]

ARTIFACT_KINDS = [
    {"record_id":f"kind.{kind}","record_kind":"boundary_kind","kind":kind,"definition":definition,"non_claim":non_claim}
    for kind, definition, non_claim in KINDS
]


FORCES = [
    ("language_discontinuity", "Do the same terms require incompatible meanings or does a distinct vocabulary become coherent?", ["bounded_context"], "Strong semantic split evidence."),
    ("model_consistency", "Can all rules coexist in one internally consistent model without conditionals that encode another worldview?", ["bounded_context"], "Strong semantic split evidence."),
    ("authority", "Who may define meaning, decide transitions, grant approval or authorize effects?", ["bounded_context","product","aggregate"], "Split when decision rights or trust boundaries are independently governed."),
    ("invariant_atomicity", "Which facts must become valid together and which may converge asynchronously?", ["aggregate"], "Defines consistency, not product or service granularity."),
    ("identity_lifecycle", "Which identities are created, versioned, corrected, revoked, retired and restored together?", ["aggregate","bounded_context","product"], "Different identity and lifecycle laws are split evidence."),
    ("time_model", "Do valid, recording, event, observation, processing and publication times have different owners or precedence?", ["bounded_context","library"], "Temporal homonyms and precedence can expose a model seam."),
    ("change_stability", "Which concepts change together, for the same reasons and at the same rate?", ["library","bounded_context","product"], "Use observed shearing forces; repository layout alone is weak evidence."),
    ("translation", "Does contact require an ACL, published language or loss-bearing mapping?", ["bounded_context"], "Need for explicit translation strongly supports distinct contexts."),
    ("user_job_outcome", "Is there a coherent user population hiring the candidate for an independently valuable outcome?", ["product"], "Necessary product evidence; irrelevant to aggregate boundaries."),
    ("adoption_exit", "Can the promise be adopted, replaced, migrated and removed independently?", ["product"], "Necessary product evidence; a reusable library alone is insufficient."),
    ("operation_failure_slo", "Does it have a distinct service level, capacity, failure, recovery and on-call boundary?", ["product","provider"], "Operational split evidence; it cannot manufacture a semantic split."),
    ("economics", "Are usage, cost, value and support governed independently?", ["product","provider"], "Product/provider evidence, not semantic ownership."),
    ("cognitive_flow", "Can one durable team understand, change and operate the slice without blocking handoffs?", ["product","bounded_context"], "Useful feasibility evidence; team structure must follow or explicitly translate model boundaries."),
    ("replaceable_algorithm", "Can an implementation or method vary while the semantic contract remains stable?", ["library","provider","capability"], "Prefer a library/provider seam, not a new bounded context or product."),
    ("physical_locality", "Must state or compute be colocated for latency, throughput or data gravity?", ["provider"], "Physical planning evidence; never sufficient for semantic or product identity."),
]

SEAM_FORCES = [
    {"record_id":f"force.{ident}","record_kind":"seam_force","question":question,"supports_boundary_kinds":kinds,"interpretation":interpretation}
    for ident, question, kinds, interpretation in FORCES
]


STAGES = [
    (1,"observe_domain","Collect actors, jobs, harmed parties, workflows, commands, events, policies, documents, source occurrences, decisions, failures, time and authority from real cases.","domain_observation_graph"),
    (2,"build_language","Define terms in examples and counterexamples; record homonyms, synonyms, competing definitions and unresolved language.","scoped_language_candidates"),
    (3,"discover_models","Cluster rules that form internally coherent models; identify contradictions that cannot coexist without translation.","model_candidates"),
    (4,"draw_contexts","Name each model applicability boundary and its owner; state inside, outside, negative mission and boundary falsifiers.","bounded_context_candidates"),
    (5,"map_contexts","Record every contact, influence direction, translation, ACL, published language, shared kernel or explicit separation.","context_map"),
    (6,"model_tactically","Within each context derive entities, values, aggregates, invariants, services, commands, events, refusals, state, time and concurrency.","tactical_domain_model"),
    (7,"derive_library_seams","Use conceptual contours, closure of operations, change axes, algorithm replaceability and effect boundaries to define reusable contracts.","library_candidates"),
    (8,"derive_products_independently","Starting from users and outcomes, test adoption, lifecycle, operation, economics, interface, evidence and exit without assuming one product per context.","product_candidates"),
    (9,"map_products_to_models","Connect products to owned and imported contexts, capabilities and libraries; preserve every semantic and authority owner.","product_context_hypergraph"),
    (10,"falsify","Run split/merge, negative twins, unrelated verticals, provider substitution, failure scenarios and semantic-diff tests.","bounded_adjudication"),
    (11,"implement_and_qualify","Encode types and laws, build at least two independent implementations, execute conformance and qualify exact provider editions.","qualified_offers"),
    (12,"anneal","Use production change, incidents, domain-expert correction and new evidence to split, merge, rehome or retire boundaries.","next_edition"),
]

PROCEDURE = [
    {"record_id":f"stage.ddd-seam.{number:02d}","record_kind":"seam_discovery_stage","ordinal":number,"name":name,"required_work":work,"output":output,"default_law":"no_stage_output_is_self_ratifying"}
    for number, name, work, output in STAGES
]


NEGATIVES = [
    ("one_noun_one_context","Every important noun should have one enterprise-wide meaning.","Permit different local models and require explicit translation at contacts."),
    ("one_library_one_context","Every reusable library deserves its own bounded context.","Split contexts only for model applicability; place several cohesive libraries in one context when language and ownership remain unified."),
    ("one_product_one_context","Every product is exactly one bounded context.","Model product adoption and outcomes independently, then map it to one or more owned/imported contexts."),
    ("one_context_one_product","Every bounded context must be sold or operated as a product.","Retain supporting contexts that have no independent user promise or exit boundary."),
    ("aggregate_service","Every aggregate is a service or deployment.","Use aggregate boundaries only for synchronous invariants and transactional consistency."),
    ("repository_boundary","Repository, crate, microservice or team boundaries prove the domain seam.","Require language, rules, authority and change evidence; record implementation layout separately."),
    ("vendor_sku","A vendor SKU or open-source project proves one product and one model.","Decompose packaging into independently owned promises, models, capabilities and providers."),
    ("shared_data_model","Contexts sharing source data must share one canonical model.","Translate source occurrences into each context's model without transferring source authority."),
    ("reuse_split","Potential reuse requires the smallest possible libraries and contexts.","Preserve whole concepts and conceptual contours; expose stable operations rather than fragments clients must reconstruct."),
    ("score_semantics","A product split score may override duplicate semantic ownership.","Merge, narrow or translate any candidates that claim the same meaning regardless of numeric score."),
    ("workshop_truth","An EventStorming cluster is a ratified bounded context or aggregate.","Treat it as discovery evidence and test it against language, invariants, authority and real scenarios."),
    ("final_upfront_model","DDD produces a complete upfront ontology that should stop changing.","Version the bounded verdict and continuously refactor toward deeper insight from implementation and domain evidence."),
]

NEGATIVE_TESTS = [
    {"record_id":f"negative.ddd-seam.{ident}","record_kind":"negative_seam_test","unsafe_claim":claim,"required_behavior":behavior}
    for ident, claim, behavior in NEGATIVES
]


METADATA_AUDIT = [
    {"record_id":"audit.metadata-discovery.product","record_kind":"seam_adjudication","subject_ref":"product.metadata_discovery","adjudicated_kind":"product","verdict":"retain","rationale":"One independently adopted and operated promise serves catalog consumers and curators through acquisition, source-attributed description, projection, discovery, federation and service evidence; its exit and SLO are cohesive even though it composes several contexts.","semantic_owner_ref":None},
    {"record_id":"audit.metadata-discovery.acquisition","record_kind":"seam_adjudication","subject_ref":"library.metadata_discovery.acquisition_port","adjudicated_kind":"bounded_context_and_library","verdict":"retain_separate_context","rationale":"Source protocol records, attempts, cursors, checkpoints, deletion signals and receipts form an integration language and effect lifecycle distinct from catalog assertion publication.","semantic_owner_ref":"context.metadata_discovery.acquisition"},
    {"record_id":"audit.metadata-discovery.assertion","record_kind":"seam_adjudication","subject_ref":"library.metadata_discovery.assertion_record","adjudicated_kind":"aggregate_and_library","verdict":"merge_context_into_catalog","rationale":"Assertion identity and lifecycle are the authoritative write model of the catalog context; the library and aggregate seam remain exact without inventing a separate language boundary.","semantic_owner_ref":"context.metadata_discovery.catalog"},
    {"record_id":"audit.metadata-discovery.projection","record_kind":"seam_adjudication","subject_ref":"library.metadata_discovery.discovery_projection","adjudicated_kind":"read_model_library","verdict":"merge_context_into_catalog","rationale":"Discovery documents, facets and browse graphs are derived read models of catalog assertions under the same local vocabulary and ownership.","semantic_owner_ref":"context.metadata_discovery.catalog"},
    {"record_id":"audit.metadata-discovery.search","record_kind":"seam_adjudication","subject_ref":"library.metadata_discovery.search_browse","adjudicated_kind":"application_domain_service_and_effect_port","verdict":"merge_context_into_catalog","rationale":"Discovery query semantics belong to the catalog language while physical search/index execution is an imported provider/product; rank does not create a new catalog semantic owner.","semantic_owner_ref":"context.metadata_discovery.catalog"},
    {"record_id":"audit.metadata-discovery.federation","record_kind":"seam_adjudication","subject_ref":"library.metadata_discovery.federation","adjudicated_kind":"supporting_bounded_context_and_library","verdict":"retain_separate_context","rationale":"Peer identity, harvest edition, alignment, precedence, conflict and partial completion form a distinct inter-catalog model with explicit translation to local assertions.","semantic_owner_ref":"context.metadata_discovery.federation"},
    {"record_id":"audit.metadata-discovery.freshness","record_kind":"seam_adjudication","subject_ref":"library.metadata_discovery.freshness_coverage","adjudicated_kind":"domain_service_and_algorithm_library","verdict":"merge_context_into_catalog","rationale":"Freshness and coverage specialize generic measurement over catalog populations and cuts; they do not have an independent lifecycle, language community or adoption promise.","semantic_owner_ref":"context.metadata_discovery.catalog"},
]


FILES = {
    "sources.jsonl": SOURCES,
    "boundary-kinds.jsonl": ARTIFACT_KINDS,
    "seam-forces.jsonl": SEAM_FORCES,
    "seam-discovery-procedure.jsonl": PROCEDURE,
    "negative-tests.jsonl": NEGATIVE_TESTS,
    "metadata-discovery-seam-audit.jsonl": METADATA_AUDIT,
}


def main() -> None:
    files = {}
    for name, rows in FILES.items():
        payload = encode(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        files[name] = {"records":len(rows),"sha256":hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id":"ddd_product_seam_doctrine_v0_1_0","as_of":AS_OF,"edition":1,"status":"researched_candidate","completion_claim":False,"files":files}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS DDD seam doctrine: {len(SOURCES)} sources, {len(ARTIFACT_KINDS)} kinds, {len(SEAM_FORCES)} forces, {len(PROCEDURE)} stages, {len(METADATA_AUDIT)} metadata rulings")


if __name__ == "__main__":
    main()
