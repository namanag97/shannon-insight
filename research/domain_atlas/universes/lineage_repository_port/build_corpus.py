#!/usr/bin/env python3
"""Build the exact provider-neutral lineage repository port contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for row in rows)


def S(ident: str, title: str, publisher: str, url: str, scope: str, limit: str, kind: str = "official_specification") -> dict:
    return {"source_id": f"source.lineage-repository.{ident}", "title": title, "publisher": publisher,
            "url": url, "source_kind": kind, "claim_scope": scope, "scope_limit": limit}


SOURCES = [
    S("w3c.prov-dm", "PROV-DM: The PROV Data Model", "W3C", "https://www.w3.org/TR/prov-dm/", "provenance entity, activity, agent, event, bundle and relation semantics", "PROV-DM defines meaning, not persistence, transaction, consistency, retention or provider qualification."),
    S("w3c.prov-o", "PROV-O: The PROV Ontology", "W3C", "https://www.w3.org/TR/prov-o/", "RDF representation of PROV entities, activities, agents and qualified relations", "PROV-O is one representation and does not mandate a graph store or prove assertion truth."),
    S("w3c.prov-constraints", "Constraints of the PROV Data Model", "W3C", "https://www.w3.org/TR/prov-constraints/", "uniqueness, event ordering, type, impossibility, validity and equivalence constraints", "PROV validity is semantic consistency, not storage acknowledgement, source truth or evidence sufficiency."),
    S("w3c.prov-aq", "PROV-AQ: Provenance Access and Query", "W3C", "https://www.w3.org/TR/prov-aq/", "provenance URI discovery, direct retrieval, query-service discovery and pingback", "PROV-AQ is a Working Group Note and leaves provider coverage, persistence and query result scope open."),
    S("w3c.prov-links", "Linking Across Provenance Bundles", "W3C", "https://www.w3.org/TR/prov-links/", "linking provenance descriptions across bundles", "Bundle links do not merge authority, identity, temporal cuts or storage transactions."),
    S("w3c.rdf11", "RDF 1.1 Concepts and Abstract Syntax", "W3C", "https://www.w3.org/TR/rdf11-concepts/", "RDF graph, dataset, named graph, triple, IRI, blank node and literal", "RDF is one graph representation; lineage also includes non-RDF profiles and externally owned semantics."),
    S("w3c.rdf-canon", "RDF Dataset Canonicalization", "W3C", "https://www.w3.org/TR/rdf-canon/", "RDFC-1.0 canonical serialization and dataset hashing", "Canonicalization and a matching digest prove algorithm-scoped representation identity, not semantic truth or repository completeness."),
    S("w3c.sparql-query", "SPARQL 1.1 Query Language", "W3C", "https://www.w3.org/TR/sparql11-query/", "RDF dataset graph-pattern evaluation and solution sequences", "SPARQL is one query profile and does not define lineage path semantics, bitemporal cuts, coverage or authorization."),
    S("w3c.ldp", "Linked Data Platform 1.0", "W3C", "https://www.w3.org/TR/ldp/", "HTTP creation, update, deletion, containment and constrained-by discovery", "LDP resource effects do not establish lineage semantic acceptance, immutable editions or retention authority."),
    S("ietf.rfc9110", "RFC 9110: HTTP Semantics", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html", "resource representations, validators, preconditions, conditional requests and status", "HTTP success and ETags are representation/effect evidence under HTTP, not semantic acceptance or durable repository proof."),
    S("ietf.rfc7089", "RFC 7089: HTTP Framework for Time-Based Access to Resource States", "IETF", "https://www.rfc-editor.org/rfc/rfc7089.html", "original resource, memento, timegate, timemap and datetime negotiation", "Datetime negotiation is not bitemporal lineage semantics, complete history or exact snapshot selection by itself."),
    S("openlineage.spec", "OpenLineage Specification", "OpenLineage", "https://openlineage.io/docs/spec/", "event-based run, job, dataset and facet interchange", "OpenLineage events are capture inputs; ingestion success does not prove semantic validity, complete lineage or repository qualification."),
    S("cncf.cloudevents", "CloudEvents Specification 1.0", "CNCF", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "portable event envelope identity, source, type, subject, time and schema reference", "An envelope does not define delivery, ordering, deduplication, business semantics or persistence completion."),
    S("ocfl.1.1", "Oxford Common File Layout Specification 1.1", "OCFL Community", "https://ocfl.io/1.1/spec/", "repository object inventory, versions, manifests, fixity and storage diversity", "OCFL is a preservation layout; it does not define lineage graph semantics, query completeness or retention decisions."),
    S("ietf.rfc8493", "RFC 8493: BagIt File Packaging Format", "IETF", "https://www.rfc-editor.org/rfc/rfc8493.html", "package completeness and manifest checksum validity", "A complete valid bag proves package structure and fixity only, not graph semantics, coverage or repository equivalence."),
    S("loc.premis3", "PREMIS Data Dictionary for Preservation Metadata 3.0", "Library of Congress", "https://www.loc.gov/standards/premis/v3/premis-3-0-final.pdf", "preservation objects, events, agents, rights and outcomes", "PREMIS preservation records do not confer retention, disclosure, erasure or evidentiary authority."),
    S("sigstore.bundle", "Sigstore Bundle Format", "Sigstore", "https://docs.sigstore.dev/about/bundle/", "versioned signature content and verification material bundle", "Cryptographic verification proves protected material under a method, not assertion truth, authority or repository completeness."),
]


CONTEXTS = [{
    "context_id": "context.lineage_repository.persistence",
    "name": "Lineage Repository Persistence Port",
    "sovereign_question": "For externally validated lineage assertions and exact graph cuts, what append, immutable-edition, read, change-scan, verification and authorized-disposition intents and receipts preserve identity, time, coverage and history across replaceable repository providers?",
    "inside": ["repository occurrence identity", "typed write/read/disposition protocols", "immutable graph-edition manifests", "cursor and consistency-cut semantics", "effect reconciliation", "laws and refusals"],
    "outside": ["lineage relation or graph-query semantics", "assertion truth or semantic acceptance", "capture completeness", "policy, retention, disclosure or erasure authority", "evidence admissibility", "physical provider implementation", "provider qualification"],
    "owner": "authority.lineage_repository.persistence", "status": "specified_candidate",
}]


DECISIONS = [
    "repository_occurrence_identity", "assertion_identity_and_uniqueness", "append_batch_atomicity", "duplicate_and_conflict_posture",
    "precondition_and_concurrency", "partition_and_locality", "commit_ordering_token", "consistency_and_read_isolation",
    "graph_edition_manifest", "snapshot_and_canonicalization_profile", "cursor_scope_and_expiry", "pagination_and_change_scan",
    "bitemporal_cut", "coverage_and_redaction_gaps", "retention_hold_and_disposition_authority", "receipt_and_verification_evidence",
]


DECISION_ROWS = [{"decision_id": f"decision.lineage_repository.port.{decision}",
                  "owner_context": "context.lineage_repository.persistence",
                  "question": f"What exact {decision.replace('_', ' ')} applies?", "default": None,
                  "default_law": "forbidden", "status": "declared"} for decision in DECISIONS]


def O(name: str, inputs: list[str], output: str) -> dict:
    return {"operation_ref": f"operation.lineage_repository.port.{name}", "input_types": inputs,
            "output_type": f"Result<{output},LineageRepositoryRefusal>", "purity": "pure"}


OPERATIONS = [
    O("assemble_assertion_append_batch", ["ValidatedLineageAssertionSet", "AssertionIdentityPolicy", "BatchPolicy", "CoverageStatement"], "AssertionAppendBatch"),
    O("plan_assertion_append", ["AssertionAppendBatch", "RepositoryOccurrenceRef", "ExpectedRepositoryCut", "AppendPolicy"], "AssertionAppendIntent"),
    O("reconcile_append_receipt", ["AssertionAppendIntent", "RepositoryAppendReceipt", "ReceiptValidationPolicy"], "AppendReconciliation"),
    O("assemble_graph_edition_manifest", ["AppendReconciliationSet", "GraphEditionId", "TemporalCut", "CoverageAndGapSet", "ManifestPolicy"], "GraphEditionManifest"),
    O("plan_graph_edition_publication", ["GraphEditionManifest", "RepositoryOccurrenceRef", "ExpectedRepositoryCut", "PublicationPolicy"], "GraphEditionPublicationIntent"),
    O("reconcile_graph_edition_receipt", ["GraphEditionPublicationIntent", "GraphEditionPublicationReceipt", "ReceiptValidationPolicy"], "PublishedGraphEditionRef"),
    O("plan_graph_cut_load", ["GraphCutReadRequest", "RepositoryOccurrenceRef", "ReadConsistencyPolicy", "ResourceBudget"], "GraphCutReadIntent"),
    O("validate_loaded_graph_cut", ["GraphCutReadIntent", "GraphCutReadReceipt", "LoadedGraphCut", "ReadValidationPolicy"], "ValidatedLoadedGraphCut"),
    O("plan_change_scan", ["ChangeScanRequest", "RepositoryCursor", "ChangeScanPolicy", "ResourceBudget"], "ChangeScanIntent"),
    O("validate_change_page", ["ChangeScanIntent", "ChangePageReceipt", "ChangePage", "CursorValidationPolicy"], "ValidatedChangePage"),
    O("verify_repository_snapshot", ["GraphSnapshot", "SnapshotManifest", "CanonicalizationProfile", "VerificationBudget"], "SnapshotVerificationResult"),
    O("plan_repository_disposition", ["RepositoryScope", "ExternalDispositionDecisionRef", "HoldEvidenceSet", "DispositionPolicy"], "RepositoryDispositionIntent"),
    O("reconcile_disposition_receipt", ["RepositoryDispositionIntent", "RepositoryDispositionReceipt", "ReceiptValidationPolicy"], "DispositionReconciliation"),
]


PUBLIC_TYPES = [
    "LineageRepositoryPortEdition", "RepositoryOccurrenceId", "RepositoryOccurrenceRef", "RepositoryProviderRef", "RepositoryProviderEditionRef",
    "AssertionId", "AssertionEditionId", "AssertionOccurrenceId", "ValidatedLineageAssertion", "ValidatedLineageAssertionSet", "AssertionAppendBatch",
    "AppendAttemptId", "AssertionAppendIntent", "RepositoryAppendReceipt", "AppendReconciliation", "DuplicateEvidence", "ConflictEvidence",
    "ExpectedRepositoryCut", "RepositoryCommitPosition", "CausalToken", "ConsistencyProfile", "ReadIsolationProfile", "PartitionKey",
    "GraphEditionId", "GraphEditionManifest", "GraphEditionDigest", "GraphEditionPublicationIntent", "GraphEditionPublicationReceipt", "PublishedGraphEditionRef",
    "GraphSnapshotId", "GraphSnapshotRef", "GraphSnapshot", "SnapshotManifest", "SnapshotDigest", "CanonicalizationProfile", "SnapshotVerificationResult",
    "GraphCutReadRequest", "GraphCutReadIntent", "GraphCutReadReceipt", "LoadedGraphCut", "ValidatedLoadedGraphCut", "TemporalCut", "ValidityInterval", "RecordingInterval",
    "CoverageStatement", "CoverageGap", "CaptureGapRef", "RedactionGapRef", "QueryPolicyDecisionRef", "PageLimit", "ResourceBudget",
    "RepositoryCursor", "CursorScope", "CursorExpiry", "ChangeScanRequest", "ChangeScanIntent", "ChangePage", "ChangePageReceipt", "ValidatedChangePage",
    "ExternalDispositionDecisionRef", "RetentionClassRef", "LegalHoldRef", "HoldEvidenceSet", "RepositoryScope", "DispositionKind", "RepositoryDispositionIntent",
    "RepositoryDispositionReceipt", "DispositionReconciliation", "LineageRepositoryRefusal",
]


LAWS = [
    "Lineage assertion identity, assertion edition, repository occurrence, commit position, graph edition, snapshot, representation and provider object are distinct.",
    "The repository persists externally validated assertions and never acquires relation semantics, semantic acceptance, source truth or causal authority.",
    "Append intent, dispatch, storage acknowledgement, committed occurrence, semantic validation, graph-edition publication and evidence acceptance are distinct.",
    "Duplicate, idempotent replay, compatible partial assertion, conflicting assertion, correction, retraction and deletion remain distinct.",
    "Every write binds exact repository occurrence, provider edition, batch, precondition, transaction scope, idempotency identity, clock and causal cut.",
    "A provider ordering token is scoped to its declared partition and consistency profile and never becomes event time, validity time or universal causal order.",
    "Graph edition is an immutable manifest over exact assertion editions, temporal cut, coverage, redaction and canonicalization profile; it is not a mutable latest graph.",
    "Recording time, commit time, event time, validity time, retrieval time, verification time and disposition time remain distinct.",
    "A read binds exact graph edition or repository cut, consistency profile, authorization decision, temporal predicate, page/cursor scope and finite budget.",
    "Not found, hidden by policy, outside the requested cut, expired cursor, incomplete coverage, unavailable snapshot and proven absence remain distinct.",
    "Cursor identity is query-, repository-, partition-, policy-, consistency- and edition-bound; it is opaque, finite-lived and not portable across providers by default.",
    "A returned path or graph cut is repository material only; path semantics, inference, impact and query completeness remain owned by lineage query libraries.",
    "Canonical digest, matching ETag, valid signature, OCFL inventory or BagIt manifest proves only its named representation, protocol or fixity claim.",
    "Repository integrity, availability, durability, semantic validity, coverage completeness, evidentiary sufficiency and provider qualification are separate verdicts.",
    "Retention, legal hold, disclosure, redaction, correction, erasure and physical deletion require externally issued scoped decisions; storage configuration is not authority.",
    "Disposition intent, provider receipt, logical tombstone, access suppression, crypto-erasure, physical erasure and verified downstream deletion are distinct.",
    "Unknown effect completion is reconciled before retry, and a receipt is accepted only against the exact intent, provider, target, attempt and precondition.",
    "Repository substitution requires exact behavioral conformance for identity, atomicity, ordering, cuts, cursors, gaps, receipts and disposition—not merely a graph API.",
]


LIBRARIES = [{
    "library_id": "library.lineage_repository.port", "name": "Lineage Repository Persistence Port",
    "library_kind": "effect_port", "semantic_owner_context": "context.lineage_repository.persistence",
    "status": "specified", "candidate_responsibility": "persist and retrieve immutable lineage assertion and graph editions through an authority-preserving provider-neutral port",
    "effect_boundary": "pure_effect_intents", "public_types": PUBLIC_TYPES,
    "public_traits": ["LineageRepositoryPortAlgebra"], "operation_refs": [op["operation_ref"] for op in OPERATIONS],
    "operations": OPERATIONS, "decision_refs": [row["decision_id"] for row in DECISION_ROWS],
    "configuration_contracts": ["LineageRepositoryPortPolicy"], "laws": LAWS,
    "invariants": ["all identities, editions, cuts, temporal axes, coverage gaps, authority decisions, attempts, preconditions and receipts are explicit",
                   "pure operations plan or reconcile effects and never perform ambient I/O",
                   "no model or agent may establish lineage truth, waive a conflict, select hidden consistency, authorize disposition, accept evidence or qualify a provider"],
    "error_contracts": ["RepositoryOccurrenceUnbound", "ProviderEditionUnbound", "AssertionIdentityConflict", "DuplicatePostureUnbound", "PreconditionFailed",
                        "AtomicityUnsupported", "ConsistencyProfileUnsupported", "OrderingScopeInvalid", "GraphEditionConflict", "SnapshotUnavailable",
                        "TemporalCutInvalid", "CoverageUnknown", "AuthorizationDecisionMissing", "CursorInvalid", "CursorExpired", "PageIncomplete",
                        "CanonicalizationUnsupported", "VerificationBudgetExceeded", "DispositionAuthorityMissing", "LegalHoldConflict", "ReceiptMismatch",
                        "EffectCompletionUnknown", "UnsupportedEdition", "InvalidConfiguration", "ResourceBudgetExceeded"],
    "dependencies": ["library.lpe.prov-statement-algebra","library.lpe.provenance-assertion", "library.lpe.provenance-bundle"],
    "evidence_refs": [row["source_id"] for row in SOURCES],
    "oracles": ["canonical append/idempotency/conflict fixtures", "atomicity and lost-update model tests", "bitemporal cut and pagination corpus",
                "cursor scope/expiry/partition negative twins", "snapshot canonicalization and fixity fixtures", "policy/hold/disposition state-machine tests",
                "effect retry and reconciliation histories", "provider substitution differential suite", "two independent implementations"],
    "gaps": ["No implementation is qualified; two independent providers and executed conformance remain required."],
    "must_not_own": ["lineage vocabulary, relation semantics or graph-query inference", "assertion truth, semantic acceptance or causal claims",
                     "capture or query completeness", "identity, policy, retention, disclosure, hold or erasure authority", "evidence admissibility or relying decisions",
                     "physical provider implementation or provider qualification"],
    "qualification_required": False,
}]


NEGATIVES = [
    ("database_semantics", "A chosen graph database defines lineage relation or query semantics.", "Keep provider storage behind the exact lineage repository port."),
    ("ack_acceptance", "A successful append acknowledgement semantically accepts the lineage assertion.", "Reconcile storage effect separately from semantic validation and acceptance."),
    ("duplicate_replay", "The same assertion identifier always means a harmless idempotent replay.", "Compare exact edition, digest, scope and conflict policy."),
    ("latest_graph", "The mutable latest graph is a stable graph edition.", "Publish an immutable cut-bound manifest with exact member editions."),
    ("commit_event_time", "Repository commit order is event, validity or causal order.", "Preserve every temporal axis and scope ordering tokens explicitly."),
    ("etag_truth", "A matching ETag or digest proves graph semantics or assertion truth.", "Report exact representation and algorithm-scoped integrity only."),
    ("valid_prov_stored", "Stored PROV is valid merely because the repository accepted it.", "Run the external PROV constraint oracle and retain its verdict."),
    ("snapshot_complete", "A verified snapshot contains all lineage that exists.", "Bind coverage population, capture gaps, redactions and temporal cut."),
    ("not_found_absence", "Not-found proves the assertion or path does not exist.", "Distinguish policy hiding, wrong cut, missing coverage, unavailability and proven absence."),
    ("cursor_portable", "A cursor can be reused across queries, policies, editions, partitions or providers.", "Bind and validate its exact scope and expiry."),
    ("page_complete", "One successful page is the complete query result.", "Require declared pagination closure and coverage evidence."),
    ("read_path_causal", "A stored path proves causation or observed business impact.", "Return repository material for external lineage/impact evaluation."),
    ("canonical_equivalent", "Equal canonical digests under unspecified algorithms prove universal semantic equivalence.", "Bind exact representation and canonicalization algorithm edition."),
    ("bag_portable", "A valid BagIt or OCFL package proves repository behavioral substitutability.", "Test identity, cuts, ordering, cursor, effect and disposition laws independently."),
    ("retention_config_authority", "A storage TTL or lifecycle rule is retention or erasure authority.", "Require an external scoped disposition decision and hold evaluation."),
    ("tombstone_erased", "A tombstone or hidden record proves physical or downstream erasure.", "Track logical suppression, provider effect, physical verification and downstream scope separately."),
    ("delete_history", "Correction, retraction or deletion may silently rewrite prior graph editions.", "Preserve immutable history and publish explicit lifecycle relations."),
    ("retry_new_attempt", "Unknown completion may be retried with a new identity.", "Reconcile first and retain the same bounded idempotency identity."),
    ("provider_qualified", "Successful reads/writes or protocol compatibility qualify the repository provider.", "Require the full substitution/conformance suite and independent evidence."),
    ("agent_authority", "A model or agent may resolve conflicts, choose hidden cuts, authorize disposition, accept evidence or qualify a provider.", "Allow attributed proposals only; deterministic contracts and named authorities retain decisions."),
]


NEGATIVE_ROWS = [{"negative_id": f"negative.lineage-repository.{slug}", "unsafe_inference": unsafe,
                  "required_behavior": required, "status": "active"} for slug, unsafe, required in NEGATIVES]


STEM = "lineage_repository.port"
COMPILER_ROWS = [
    {"record_kind": "capability_requirement", "requirement_id": f"requirement.{STEM}.implementation", "subject_ref": "library.lineage_repository.port", "required_operations": LIBRARIES[0]["operation_refs"], "required_decisions": LIBRARIES[0]["decision_refs"], "fallback_law": "refuse", "status": "declared"},
    {"record_kind": "capability_offer", "offer_id": f"offer.{STEM}.reference", "subject_ref": "library.lineage_repository.port", "claimed_operations": LIBRARIES[0]["operation_refs"], "qualified_implementation_count": 0, "portable": False, "selectable": False, "status": "specified_unimplemented"},
    {"record_kind": "binding_rule", "binding_rule_id": f"binding.{STEM}", "requirement_ref": f"requirement.{STEM}.implementation", "offer_ref": f"offer.{STEM}.reference", "structural_match": True, "selection_law": "Structural match never promotes an unqualified or non-portable implementation.", "selectable": False, "status": "declared"},
]


FILES = {"sources.jsonl": SOURCES, "bounded-contexts.jsonl": CONTEXTS, "decision-points.jsonl": DECISION_ROWS,
         "library-contracts.jsonl": LIBRARIES, "compiler-contracts.jsonl": COMPILER_ROWS, "negative-twins.jsonl": NEGATIVE_ROWS}


def main() -> None:
    digests = {}
    for name, rows in FILES.items():
        payload = lines(rows)
        (ROOT / name).write_text(payload, encoding="utf-8")
        digests[name] = {"records": len(rows), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
    manifest = {"manifest_id": "lineage_repository_port_v0_1_0", "as_of": AS_OF, "edition": EDITION,
                "status": "specified_unimplemented_open_world", "files": digests, "completion_claim": False,
                "qualified_implementation_count": 0}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUILD PASS lineage repository port: {len(SOURCES)} sources, 1 context, {len(DECISION_ROWS)} decisions, 1 exact library, {len(OPERATIONS)} operations")


if __name__ == "__main__":
    main()
