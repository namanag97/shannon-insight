#!/usr/bin/env python3
"""Build the deterministic expert-to-artifact contribution graph.

Network collectors are intentionally separate.  This builder consumes pinned JSONL
snapshots and emits stable, sorted records without network access.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from expert_seeds import FAMILY_GROUPS, rows as seed_rows
from collect_dblp import DOMAIN_TERMS, norm as bibliographic_norm

ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-25"


DOMAIN_CONTRACTS = {
    "process_case_mining": {
        "inputs": ["typed events", "object/case correlation", "lifecycle and ordering policy", "reference or learned process model"],
        "outputs": ["model or alignment", "deviation/performance evidence", "case/object explanation", "method receipt"],
        "decisions": ["correlation semantics", "event classifier", "model formalism", "conformance cost", "soundness/fitness/precision thresholds"],
        "laws": ["event != activity instance", "case projection != object-centric truth", "discovery != conformance", "deviation != root cause", "prediction != intervention authority"],
        "libraries": ["event-and-object model", "process formalism", "discovery/conformance method", "explanation and evidence"],
    },
    "databases_query": {
        "inputs": ["logical query", "schema and constraints", "statistics", "target capabilities and resource envelope"],
        "outputs": ["equivalent physical plan", "execution receipt", "result with ordering/null/error semantics"],
        "decisions": ["equivalence rule set", "cost model", "join/access strategy", "materialization and adaptation", "transaction isolation"],
        "laws": ["logical operator != physical kernel", "estimated cost != observed cost", "row order is absent unless declared", "plan equivalence is semantics-relative"],
        "libraries": ["relational algebra and types", "optimizer rules and costs", "physical operators", "transaction and result contracts"],
    },
    "streaming_distributed": {
        "inputs": ["stream/log contract", "time and ordering model", "state transition", "failure and side-effect policy"],
        "outputs": ["state snapshots", "emissions", "checkpoints", "recovery and delivery receipts"],
        "decisions": ["event/processing time", "watermark", "partitioning", "checkpoint/barrier", "replay and deduplication", "consistency model"],
        "laws": ["exactly-once processing != exactly-once external effect", "event time != arrival time", "replication != consensus", "checkpoint != durable recovery proof"],
        "libraries": ["stream-time semantics", "partitioned state", "checkpoint/recovery", "log/replication protocol"],
    },
    "storage_lakehouse": {
        "inputs": ["typed records/objects", "schema evolution policy", "transaction intent", "storage/catalog target"],
        "outputs": ["versioned persisted state", "snapshot/manifest", "commit receipt", "maintenance plan"],
        "decisions": ["layout and file format", "table protocol", "catalog protocol", "commit isolation", "partition/clustering", "compaction and retention"],
        "laws": ["file format != table protocol", "catalog != storage", "snapshot != branch", "product != protocol implementation", "vacuum != logical deletion"],
        "libraries": ["storage carriers", "table transaction protocol", "catalog adapter", "maintenance and qualification"],
    },
    "quality_lineage_cleaning": {
        "inputs": ["declared contract", "observed data", "lineage/provenance context", "authority and fitness purpose"],
        "outputs": ["observations", "violations", "adjudications", "corrections/reconciliation", "certificates"],
        "decisions": ["constraint/check semantics", "sampling", "identity/matching", "threshold", "adjudication authority", "repair and reconciliation policy"],
        "laws": ["validity != quality != fitness", "detection != adjudication", "repair != reconciliation", "lineage != causality", "explanation != evidence"],
        "libraries": ["quality predicates", "identity/integration", "lineage/provenance graph", "repair/reconciliation and evidence"],
    },
    "semantics_ontology": {
        "inputs": ["terms and definitions", "identity criteria", "axioms/constraints", "mappings and governance context"],
        "outputs": ["versioned semantic model", "inferences", "conflicts", "mapping and proof receipts"],
        "decisions": ["logic profile", "open/closed world", "unique-name posture", "identity and alignment", "inconsistency handling", "version policy"],
        "laws": ["term label != concept identity", "ontology != catalog", "inference != asserted fact", "sameAs != approximate match", "semantic compatibility != schema compatibility"],
        "libraries": ["semantic identifiers and vocabulary", "axiom/constraint model", "reasoner interface", "alignment and versioning"],
    },
    "causal_experimental_statistics": {
        "inputs": ["population", "treatment/intervention", "comparison", "outcome", "time", "assumptions and observed data"],
        "outputs": ["identified estimand or refusal", "estimate", "uncertainty", "diagnostics and sensitivity receipt"],
        "decisions": ["causal graph/design", "estimand", "identification strategy", "estimator", "nuisance model", "overlap and sensitivity"],
        "laws": ["association != causation", "prediction != intervention", "estimand != estimator", "identification != estimation", "statistical significance != decision value"],
        "libraries": ["study and estimand model", "identification rules", "estimators", "diagnostics/sensitivity/evaluation"],
    },
    "forecasting_time_series": {
        "inputs": ["time-indexed observations", "information availability", "horizon and hierarchy", "loss and update policy"],
        "outputs": ["point/distribution/quantile forecast", "coherence receipt", "backtest and calibration evidence"],
        "decisions": ["frequency and aggregation", "transformation", "model class", "hierarchy reconciliation", "evaluation window", "combination/update"],
        "laws": ["forecast != target observation", "interval != confidence interval", "in-sample fit != forecast accuracy", "base forecast != reconciled forecast"],
        "libraries": ["temporal carrier and calendar", "forecast models", "reconciliation", "backtest/scoring/calibration"],
    },
    "operations_research": {
        "inputs": ["decision variables", "objective(s)", "constraints", "uncertainty/information structure", "resource budget"],
        "outputs": ["solution/incumbent", "status", "bound/gap/certificate", "diagnostic and execution receipt"],
        "decisions": ["formulation", "exact/approximate posture", "relaxation/decomposition", "algorithm/solver", "tolerance", "search and termination budget"],
        "laws": ["feasible != optimal", "incumbent != proof", "heuristic != approximation guarantee", "model infeasible != business impossible", "solver status is typed"],
        "libraries": ["optimization model IR", "solver capability interface", "algorithm/search policy", "solution verification"],
    },
    "simulation_decision_analysis": {
        "inputs": ["system boundary and state", "transition/event model", "stochastic inputs", "alternatives and preferences"],
        "outputs": ["replicated outcomes", "uncertainty estimate", "ranking/choice evidence", "sensitivity receipt"],
        "decisions": ["simulation paradigm", "random stream", "warm-up/run length", "replication", "output estimator", "utility/criteria aggregation"],
        "laws": ["simulation model != real system", "single run != estimate", "random seed != uncertainty model", "score != preference truth", "ranking != authority to act"],
        "libraries": ["simulation state/event model", "randomness and experiment design", "output analysis", "preference/decision analysis"],
    },
    "visualization_hci": {
        "inputs": ["semantic query result", "task and audience", "uncertainty", "interaction/accessibility constraints"],
        "outputs": ["presentation specification", "interaction state", "accessible rendering", "evaluation evidence"],
        "decisions": ["encoding/channel", "scale/layout", "aggregation", "interaction grammar", "uncertainty display", "accessibility and narrative"],
        "laws": ["data value != visual mark", "chart != analytical case", "explanation != evidence", "color distinction != accessibility", "interaction state != source state"],
        "libraries": ["visual grammar", "scale/layout", "interaction state machine", "accessibility/uncertainty/evaluation"],
    },
    "spatial_scientific_media": {
        "inputs": ["typed spatial/array/media carrier", "reference system and support", "resolution/uncertainty", "operation semantics"],
        "outputs": ["derived geometry/coverage/array/media feature", "error/loss bounds", "provenance and target receipt"],
        "decisions": ["CRS/support", "topology/interpolation", "resolution/chunking", "index", "similarity/feature", "loss and precision"],
        "laws": ["coordinates without CRS are incomplete", "raster != vector", "array shape != semantic dimensions", "similarity != identity", "codec loss != measurement uncertainty"],
        "libraries": ["spatial/reference types", "coverage/array algebra", "index and kernels", "media representation/similarity"],
    },
    "compression_encoding": {
        "inputs": ["semantic carrier", "logical value stream", "distribution/access workload", "compatibility and loss policy"],
        "outputs": ["encoded bytes", "framing/index metadata", "decoder contract", "size/speed/loss receipt"],
        "decisions": ["code/codec", "framing", "block/page size", "dictionary/state", "random access", "schema evolution and checksum"],
        "laws": ["semantic type != encoding", "encoding != container", "compression ratio != end-to-end utility", "lossless bytes != semantic round-trip", "decoder availability is mandatory"],
        "libraries": ["carrier/encoding contracts", "codec", "framing/index", "compatibility and benchmark qualification"],
    },
    "privacy_security_trust": {
        "inputs": ["principal and authority", "asset and purpose", "policy/consent", "threat and privacy budget"],
        "outputs": ["decision/enforcement", "protected data/result", "privacy/security accounting", "audit/attestation evidence"],
        "decisions": ["identity/authentication", "authorization and delegation", "privacy mechanism/accounting", "cryptographic purpose", "retention/disclosure", "audit and incident response"],
        "laws": ["authentication != authorization", "approval != issuance != enforcement", "encryption != permission", "pseudonymization != anonymization", "audit log != proof of compliance"],
        "libraries": ["principal/authority model", "policy decision/enforcement", "privacy accounting", "cryptographic and evidence interfaces"],
    },
    "compiler_runtime_reliability": {
        "inputs": ["typed intent/IR", "semantic laws", "target capability offer", "resource/failure budget"],
        "outputs": ["lowered artifact", "proof/qualification receipt", "runtime outcome", "diagnostic and provenance"],
        "decisions": ["IR representation", "rewrite/pass", "target lowering", "scheduling/resource", "cancellation/failure", "testing and reproducibility"],
        "laws": ["rewrite != equivalence proof", "compile success != target qualification", "retry != idempotency", "benchmark != production guarantee", "failure observation != root cause"],
        "libraries": ["typed IR and passes", "target capability/binder", "runtime resource/failure", "verification/testing/diagnosis"],
    },
}


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def stable(prefix: str, value: str) -> str:
    return f"{prefix}.{slug(value)[:80]}_{hashlib.sha256(value.encode()).hexdigest()[:10]}"


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(name: str, rows: list[dict], key: str) -> None:
    ordered = sorted(rows, key=lambda row: row[key])
    (ROOT / name).write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in ordered), encoding="utf-8")


def artifact_kind(value: str | None) -> str:
    return {
        "journal-article": "journal_article", "proceedings-article": "conference_article",
        "book": "book", "book-chapter": "book_chapter", "posted-content": "technical_report",
        "report": "technical_report", "dataset": "dataset", "dissertation": "thesis",
    }.get(value or "", "other")


def main() -> None:
    seeds = seed_rows()
    seed_by_name = {row["name"]: row for row in seeds}
    identities = {row["query_name"]: row for row in load_jsonl(ROOT / "bibliographic-identities.jsonl")}
    # Crossref common-name matches are admitted only when the artifact title contains a
    # routed domain term.  Ambiguous zero-match portfolios are recovered through explicit
    # name+topic DBLP queries, still as bibliography-only candidates.
    snapshot = [row for row in load_jsonl(ROOT / "bibliography-snapshot.jsonl") if row["query_name"] in seed_by_name]
    for row in snapshot:
        title_n = bibliographic_norm(row["title"])
        row["title_topic_matches"] = sorted({term for term in DOMAIN_TERMS[row["seed_domain"]] if bibliographic_norm(term) in title_n})
        row["topic_assignment_state"] = "title_term_supported" if row["title_topic_matches"] else "seed_routed_needs_content_review"
        row["semantic_route_admissible"] = bool(row["title_topic_matches"])
    for row in load_jsonl(ROOT / "bibliography-dblp-targeted.jsonl"):
        if row["query_name"] in seed_by_name:
            row["semantic_route_admissible"] = True
            snapshot.append(row)
    manual_rows = [row for row in load_jsonl(ROOT / "manual-primary-artifacts.jsonl") if row["query_name"] in seed_by_name]
    for row in manual_rows:
        row["semantic_route_admissible"] = True
    snapshot.extend(manual_rows)
    manual_names = {row["query_name"] for row in manual_rows}

    # Deduplicate artifacts but retain every query route; DOI is the canonical key when present.
    artifact_by_key: dict[str, dict] = {}
    selections: list[tuple[str, str, dict]] = []
    for row in snapshot:
        key = (row.get("doi") or row.get("direct_url") or row["title"]).lower()
        aid = stable("artifact", key)
        selections.append((row["query_name"], aid, row))
        if key not in artifact_by_key:
            artifact_by_key[key] = {
                "artifact_id": aid,
                "work_id": stable("work", key),
                "edition_id": stable("edition", f"{key}|{row.get('publication_date') or row.get('year') or 'undated'}"),
                "edition_identity_state": "doi_registered_manifestation_not_content_pinned",
                "content_digest": None,
                "title": row["title"],
                "artifact_kind": artifact_kind(row.get("artifact_type")),
                "year": row.get("year"),
                "publication_date": row.get("publication_date"),
                "venue": row.get("venue"),
                "doi": row.get("doi"),
                "direct_url": row.get("direct_url"),
                "authors": row.get("authors", []),
                "query_routes": [],
                "family_refs": [],
                "selection_buckets": [],
                "title_topic_matches": [],
                "content_claims": [],
                "explicit_roles": [],
                "semantic_route_admissible": False,
                "claim_state": "bibliographic_verified",
                "evidence_scope": row["bibliographic_evidence_scope"],
                "limitations": row["bibliographic_evidence_limitations"],
            }
        target = artifact_by_key[key]
        target["query_routes"].append(row["query_name"])
        target["family_refs"].append(f"family.{row['seed_family']}")
        target["selection_buckets"].append(row.get("selection_bucket"))
        target["title_topic_matches"].extend(row.get("title_topic_matches", []))
        if row.get("content_claim"):
            target["content_claims"].append(row["content_claim"])
        target["explicit_roles"].extend(row.get("explicit_roles", []))
        target["semantic_route_admissible"] = target["semantic_route_admissible"] or row.get("semantic_route_admissible", False)
    artifacts = list(artifact_by_key.values())
    for artifact in artifacts:
        for field in ["query_routes", "family_refs", "selection_buckets", "title_topic_matches", "content_claims", "explicit_roles"]:
            artifact[field] = sorted({value for value in artifact[field] if value})

    artifact_refs_by_expert = defaultdict(list)
    quarantined_refs_by_expert = defaultdict(list)
    for name, aid, source_row in selections:
        if source_row.get("semantic_route_admissible"):
            artifact_refs_by_expert[name].append(aid)
        else:
            quarantined_refs_by_expert[name].append(aid)

    existing_names = set()
    specialist_path = ROOT.parent / "specialists" / "experts.jsonl"
    for row in load_jsonl(specialist_path):
        existing_names.add(row.get("name"))

    experts = []
    for seed in seeds:
        identity = identities.get(seed["name"])
        refs = sorted(set(artifact_refs_by_expert[seed["name"]]))
        if seed["name"] in existing_names:
            portfolio_state = "artifact_evidenced_seed"
        elif refs:
            portfolio_state = "bibliographic_candidate"
        else:
            portfolio_state = "identity_review_required"
        experts.append({
            "expert_id": f"expert.{slug(seed['name'])}",
            "name": seed["name"],
            "domain": seed["domain"],
            "family_refs": [f"family.{seed['family']}"] + [f"family.{x}" for x in seed["secondary_families"]],
            "identity_state": identity.get("identity_state") if identity else ("manual_primary_artifact_identity_candidate" if seed["name"] in manual_names else "collector_or_identity_review_required"),
            "candidate_orcids": identity.get("candidate_orcids", []) if identity else [],
            "portfolio_state": portfolio_state,
            "artifact_refs": refs,
            "quarantined_artifact_refs": sorted(set(quarantined_refs_by_expert[seed["name"]])),
            "compiler_learning": seed["compiler_lesson"],
            "evidence_scope": ["curated research routing seed", "Crossref bibliographic authorship metadata"] + (["existing specialist corpus artifact evidence"] if seed["name"] in existing_names else []),
            "limitations": [
                "This corpus is not a ranking, endorsement, complete bibliography, or claim that the person solely invented the linked concepts.",
                "Family assignment routes review; expertise and contribution roles beyond authorship require primary-artifact and authoritative-profile review.",
                "Affiliation, citation counts, coauthorship, and fame are not used as proof of expertise or contribution magnitude.",
            ],
            "current_as_of": AS_OF,
        })

    families = []
    mappings = []
    for domain, group in FAMILY_GROUPS.items():
        contract = DOMAIN_CONTRACTS[domain]
        for family in group["families"]:
            fid = f"family.{family}"
            families.append({
                "family_id": fid, "name": family.replace("_", " "), "domain": domain,
                "coverage_state": "seeded_with_bibliographic_portfolios",
                "expert_refs": sorted(e["expert_id"] for e in experts if fid in e["family_refs"]),
                "constitutional_laws": contract["laws"],
                "limitations": ["Family boundaries are research candidates pending bounded-context adjudication.", "The finite person sample is not a completeness claim."],
            })
            mappings.append({
                "mapping_id": f"mapping.{family}", "family_id": fid,
                "mapping_state": "candidate_requires_artifact_content_review",
                "domain_inputs": contract["inputs"], "domain_outputs": contract["outputs"],
                "decision_points": contract["decisions"], "invariants": contract["laws"],
                "compiler_targets": ["domain_vocabulary", "semantic_ir", "decision_point", "proof_obligation", "library_boundary", "qualification_receipt", "test_oracle"],
                "library_boundaries": contract["libraries"] + [f"candidate family module: san-{family.replace('_', '-')}"] ,
                "qualification_requirements": [
                    "Read and scope the primary artifact; title-level routing is insufficient.",
                    "Identify executable laws, invalid inputs, refusal states, result semantics, and reproducible fixtures.",
                    "Verify at least one implementation or independent reproduction before provider binding.",
                    "Run exact-boundary, negative, property, compatibility, and target qualification tests.",
                ],
                "limitations": ["This mapping is a conversion hypothesis, not evidence that the cited authors endorse SAN or that an implementation is production-qualified."],
            })

    edges = []
    edge_seen = set()
    for name, aid, source_row in selections:
        eid = f"expert.{slug(name)}"
        roles = source_row.get("explicit_roles") or ["authored"]
        edge_key = f"{eid}|authored|{aid}"
        if "authored" in roles and edge_key not in edge_seen:
            edges.append({
                "edge_id": stable("edge", edge_key), "from_id": eid, "to_id": aid,
                "relation": "authored", "claim_state": "bibliographic_verified" if source_row.get("semantic_route_admissible") else "identity_review_required",
                "evidence_refs": [aid], "evidence_scope": ["registered bibliographic authorship"],
                "author_position": next((a.get("sequence") for a in source_row.get("authors", []) if a.get("name") and slug(name).split("_")[-1] in slug(a["name"])), None),
                "limitations": ["Authorship does not establish invention, equal contribution, expertise, maintenance, advocacy, or implementation."],
            })
            edge_seen.add(edge_key)
        relation_map = {"implemented_software": "implemented", "developed_methodology": "developed_methodology", "performed_formal_analysis": "performed_formal_analysis", "validated": "validated", "maintains": "maintains", "advocated": "advocated"}
        for role in roles:
            relation = relation_map.get(role)
            if not relation:
                continue
            role_key = f"{eid}|{relation}|{aid}"
            if role_key in edge_seen:
                continue
            edges.append({
                "edge_id": stable("edge", role_key), "from_id": eid, "to_id": aid,
                "relation": relation, "claim_state": source_row.get("topic_assignment_state", "artifact_content_verified"),
                "evidence_refs": [aid], "evidence_scope": source_row.get("bibliographic_evidence_scope", []),
                "limitations": source_row.get("bibliographic_evidence_limitations", ["Contribution scope requires review."]),
            })
            edge_seen.add(role_key)
        family_id = f"family.{source_row['seed_family']}"
        if source_row.get("semantic_route_admissible"):
            route_key = f"{eid}|portfolio_routed_to|{family_id}|{aid}"
            edges.append({
                "edge_id": stable("edge", route_key), "from_id": eid, "to_id": family_id,
                "relation": "portfolio_routed_to",
                "claim_state": source_row.get("topic_assignment_state", "seed_routed_needs_content_review"),
                "evidence_refs": [aid],
                "evidence_scope": source_row.get("bibliographic_evidence_scope", ["title terms and curated review route"]),
                "title_topic_matches": source_row.get("title_topic_matches", []),
                "limitations": ["This is not an admitted expertise or invention claim; full artifact content and identity review are required."],
            })

    concepts = []
    concept_edges = []
    concept_seen = {}
    for artifact in artifacts:
        if not artifact["semantic_route_admissible"]:
            continue
        for term in artifact["title_topic_matches"]:
            cid = stable("concept", term)
            if cid not in concept_seen:
                concept_seen[cid] = True
                concepts.append({
                    "concept_id": cid, "label": term,
                    "admission_state": "title_term_candidate",
                    "limitations": ["A matching title term is not yet a canonical concept definition or evidence of method semantics."],
                })
            key = f"{artifact['artifact_id']}|content_supports|{cid}"
            concept_edges.append({
                "edge_id": stable("edge", key), "from_id": artifact["artifact_id"], "to_id": cid,
                "relation": "content_supports", "claim_state": "title_term_supported",
                "evidence_refs": [artifact["artifact_id"]], "evidence_scope": ["artifact title only"],
                "limitations": ["The relation must be upgraded, narrowed, or rejected after content review."],
            })
    edges.extend(concept_edges)

    implementation_candidates = []
    implementation_terms = ["system", "software", "engine", "framework", "tool", "library", "platform", "language", "database", "solver"]
    for artifact in artifacts:
        if not artifact["semantic_route_admissible"]:
            continue
        matched = [term for term in implementation_terms if term in artifact["title"].lower()]
        if matched:
            implementation_candidates.append({
                "implementation_candidate_id": stable("implementation_candidate", artifact["artifact_id"]),
                "artifact_ref": artifact["artifact_id"], "matched_title_terms": matched,
                "evidence_state": "paper_title_suggests_implementation_needs_repository_or_release_verification",
                "required_evidence": ["versioned repository/release", "documented capability surface", "license and maintenance state", "independent executable qualification"],
                "limitations": ["A system/tool word in a paper title is not evidence of maintained or production-ready software."],
            })

    innovation_candidates = []
    for artifact in artifacts:
        if artifact.get("year") and 2021 <= artifact["year"] <= 2026:
            innovation_candidates.append({
                "innovation_candidate_id": stable("innovation_candidate", artifact["artifact_id"]),
                "artifact_ref": artifact["artifact_id"], "year": artifact["year"],
                "family_refs": artifact["family_refs"],
                "admission_state": "not_admitted_bibliographic_candidate",
                "required_review": ["read primary artifact", "isolate non-LLM delta", "compare predecessor/base state", "find implementation evidence", "seek independent replication or limitation"],
                "limitations": ["Publication date and title do not prove novelty, validity, state-of-the-art status, implementation, or production value."],
            })

    implementation_by_artifact = {row["artifact_ref"]: row["implementation_candidate_id"] for row in implementation_candidates}
    mapping_by_family = {row["family_id"]: row for row in mappings}
    conversion_candidates = []
    for name, aid, source_row in selections:
        family_id = f"family.{source_row['seed_family']}"
        mapping = mapping_by_family[family_id]
        artifact = next(item for item in artifacts if item["artifact_id"] == aid)
        admissible = source_row.get("semantic_route_admissible", False)
        conversion_candidates.append({
            "conversion_id": stable("conversion", f"{name}|{aid}|{family_id}"),
            "expert_ref": f"expert.{slug(name)}", "artifact_ref": aid,
            "work_ref": artifact["work_id"], "edition_ref": artifact["edition_id"],
            "family_ref": family_id,
            "admitted_roles": source_row.get("explicit_roles") or (["authored"] if admissible else []),
            "candidate_claim": (
                f"The registered artifact title contains {source_row.get('title_topic_matches')}; content review may narrow, upgrade, or reject its relation to {family_id}."
                if source_row.get("title_topic_matches")
                else f"The artifact was retrieved through the {family_id} research route; no topical claim is admitted from the title."
            ),
            "candidate_concepts": source_row.get("title_topic_matches", []) if admissible else [],
            "candidate_method_ref": family_id if admissible else None,
            "candidate_representation_inputs": mapping["domain_inputs"] if admissible else [],
            "candidate_result_outputs": mapping["domain_outputs"] if admissible else [],
            "candidate_decision_points": mapping["decision_points"] if admissible else [],
            "candidate_invariants": mapping["invariants"] if admissible else [],
            "candidate_compiler_targets": mapping["compiler_targets"] if admissible else [],
            "candidate_library_boundaries": mapping["library_boundaries"] if admissible else [],
            "implementation_candidate_ref": implementation_by_artifact.get(aid) if admissible else None,
            "conversion_state": "artifact_content_candidate_not_compiler_eligible" if source_row.get("topic_assignment_state") in {"artifact_content_verified", "implementation_verified"} else ("bibliographic_only_not_compiler_eligible" if admissible else "quarantined_identity_or_topic_ambiguous"),
            "conversion_blockers": [
                "authoritative identity receipt", "primary artifact content review", "explicit contribution-role evidence",
                "work-versus-edition/version adjudication", "claim scope and limitation extraction",
                "method/algorithm/implementation separation", "independent replication or counterevidence",
                "executable laws, fixtures, refusals, and result semantics", "library boundary and target qualification",
            ],
            "limitations": ["This row proves conversion structure exists; it does not make the title-derived candidate compiler-selectable."],
        })

    reviews = []
    for expert in experts:
        reasons = []
        if expert["identity_state"] in {"name_only_identity_review_required", "collector_or_identity_review_required"}:
            reasons.append("identity_not_authoritatively_disambiguated")
        if len(expert["candidate_orcids"]) != 1:
            reasons.append("missing_or_multiple_orcid_candidates")
        if len(expert["artifact_refs"]) < 6:
            reasons.append("artifact_portfolio_below_six")
        reasons.extend(["family_assignment_not_content_verified", "contribution_roles_beyond_authorship_unknown", "independent_replication_not_linked"])
        reviews.append({
            "review_id": f"review.{expert['expert_id'].split('.',1)[1]}", "subject_ref": expert["expert_id"],
            "priority": "high" if len(reasons) > 4 else "normal", "reasons": reasons,
            "required_actions": ["verify authoritative identity profile and persistent identifiers", "read exact primary artifacts", "record explicit contribution roles", "link software/spec/standard history where applicable", "find limitations, critics, and independent replications", "adjudicate compiler/library mappings"],
            "blocking": ["inventor claims", "expertise admission", "automatic compiler binding", "provider qualification"],
        })

    sources = [
        {"source_id": "source.w3c_prov_o", "title": "PROV-O", "url": "https://www.w3.org/TR/prov-o/", "authority_scope": ["qualified provenance relations and roles"], "limitations": ["Does not define scholarly contribution magnitude."]},
        {"source_id": "source.niso_credit", "title": "CRediT", "url": "https://credit.niso.org/", "authority_scope": ["research contributor role vocabulary"], "limitations": ["Roles must be explicitly evidenced; authorship alone cannot populate them."]},
        {"source_id": "source.datacite_46", "title": "DataCite Metadata Schema", "url": "https://datacite-metadata-schema.readthedocs.io/", "authority_scope": ["persistent identifiers and contributor/resource metadata"], "limitations": ["Registration metadata is not appraisal."]},
        {"source_id": "source.crossref_api_snapshot", "title": "Crossref REST API", "url": "https://api.crossref.org/", "authority_scope": ["DOI registration metadata discovery"], "limitations": ["Name matching is not identity proof; metadata is publisher-deposited and may be incomplete."]},
        {"source_id": "source.dblp", "title": "DBLP", "url": "https://dblp.org/", "authority_scope": ["computer-science bibliographic discovery"], "limitations": ["Bibliography is not expertise, invention, or validity evidence."]},
        {"source_id": "source.openalex", "title": "OpenAlex", "url": "https://docs.openalex.org/", "authority_scope": ["cross-domain bibliographic and identity discovery"], "limitations": ["Automated entities and concepts require disambiguation and primary-source review."]},
    ]

    counterevidence = [{
        "counterevidence_id": f"counterevidence.{family['family_id'].split('.',1)[1]}",
        "family_ref": family["family_id"],
        "invalid_inferences": ["many papers imply correctness", "many citations imply authority", "one artifact implies complete domain expertise", "coauthor order implies exact contribution", "recent implies state of the art", "paper implies maintained software"],
        "required_counterevidence_search": ["negative results and known failure modes", "independent replications and benchmarks", "scope conditions and counterexamples", "competing formalisms and implementations", "superseded or retracted artifacts"],
        "status": "open",
    } for family in families]

    write_jsonl("experts.jsonl", experts, "expert_id")
    write_jsonl("artifacts.jsonl", artifacts, "artifact_id")
    write_jsonl("families.jsonl", families, "family_id")
    write_jsonl("contribution-edges.jsonl", edges, "edge_id")
    write_jsonl("concept-candidates.jsonl", concepts, "concept_id")
    write_jsonl("compiler-library-mappings.jsonl", mappings, "mapping_id")
    write_jsonl("implementation-tool-evidence.jsonl", implementation_candidates, "implementation_candidate_id")
    write_jsonl("innovations-2021-2026.jsonl", innovation_candidates, "innovation_candidate_id")
    write_jsonl("artifact-conversion-candidates.jsonl", conversion_candidates, "conversion_id")
    write_jsonl("review-queue.jsonl", reviews, "review_id")
    write_jsonl("counterevidence-queue.jsonl", counterevidence, "counterevidence_id")
    write_jsonl("sources.jsonl", sources, "source_id")

    family_counts = Counter()
    for expert in experts:
        for family in expert["family_refs"]:
            family_counts[family] += 1
    coverage = {
        "edition": "0.1.0-candidate", "current_as_of": AS_OF,
        "counts": {
            "domains": len(FAMILY_GROUPS), "families": len(families), "experts": len(experts),
            "experts_with_bibliographic_artifacts": sum(bool(e["artifact_refs"]) for e in experts),
            "unique_artifacts": len(artifacts), "expert_artifact_selections": len(selections),
            "contribution_edges": len(edges), "concept_candidates": len(concepts),
            "recent_2021_2026_candidates": len(innovation_candidates),
            "implementation_candidates": len(implementation_candidates), "compiler_mappings": len(mappings),
            "artifact_conversion_candidates": len(conversion_candidates),
            "semantically_routed_conversion_candidates": sum(row["conversion_state"] != "quarantined_identity_or_topic_ambiguous" for row in conversion_candidates),
            "quarantined_conversion_candidates": sum(row["conversion_state"] == "quarantined_identity_or_topic_ambiguous" for row in conversion_candidates),
            "open_expert_reviews": len(reviews), "open_counterevidence_reviews": len(counterevidence),
        },
        "family_expert_counts": dict(sorted(family_counts.items())),
        "coverage_laws": ["zero uncovered seeded families is not zero uncovered real-world families", "candidate records do not satisfy admitted/qualified coverage"],
        "explicitly_uncovered": [
            "authoritative identity profiles for every person", "complete artifact bibliographies", "explicit CRediT roles for most artifacts",
            "patents and standards contribution histories at global completeness", "software commit/release maintenance histories",
            "independent replications and negative results at family depth", "practitioner experts without indexed scholarly outputs",
            "regional/language/institutional equity audit", "citation and selection bias audit", "production qualification evidence",
        ],
        "sibling_deep_pilots": [{
            "path": "../process_mining_expert_pilot/", "scope": "artifact-level process-mining and Dirk Fahland adjudication",
            "reported_counts": {"sources": 71, "experts": 25, "contributions": 112, "compiler_mappings": 506, "library_boundaries": 262},
            "integration_law": "Merge by stable person/work/edition/contribution/concept identity and preserve evidence history; do not duplicate or overwrite deep-pilot records."
        }],
    }
    (ROOT / "coverage-matrix.json").write_text(json.dumps(coverage, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "edition": "0.1.0-candidate", "generated_at": AS_OF,
        "files": {name: sum(1 for _ in (ROOT / name).open(encoding="utf-8")) for name in [
            "experts.jsonl", "artifacts.jsonl", "families.jsonl", "contribution-edges.jsonl",
            "concept-candidates.jsonl", "compiler-library-mappings.jsonl", "implementation-tool-evidence.jsonl",
            "innovations-2021-2026.jsonl", "review-queue.jsonl", "counterevidence-queue.jsonl", "sources.jsonl",
            "artifact-conversion-candidates.jsonl",
        ]},
        "determinism": "All generated JSONL is sorted; builder reads only checked-in snapshots and local seed files.",
        "claim": "Broad candidate evidence graph, not a complete expert census or admitted compiler knowledge base.",
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(coverage["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
