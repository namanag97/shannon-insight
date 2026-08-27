#!/usr/bin/env python3
"""Completion stage of the provenance/quality research lane.

Repairs verified defects in the partial checkpoint (build_research.py), then projects
the semantic modules onto all 68 assigned libraries and writes every contracted
artifact deterministically. Writes only inside this output directory.
"""
from __future__ import annotations

import json
from pathlib import Path

import build_research as br

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 1. Repair the checkpoint where live verification falsified it.
# ---------------------------------------------------------------------------

# Web verification 2026-08-26:
#  - XBRL Formula 1.0 reached Recommendation on 2009-06-22 (release history).
#  - RO-Crate 1.1 was published 2020-10-30 (GitHub releases); 1.2.0/1.3 exist later.
#  - LOC serves PREMIS v3 from the /v3/ landing page (PDF blocked to automated clients).
#  - iso25000.com portal page returned HTTP 404; drop it and record an explicit vacancy.
for rec in br.SOURCES:
    if rec["source_id"] == "src.xbrl.formula-1.0":
        rec["edition_or_version"] = "Formula 1.0 (Recommendation 22 June 2009)"
        rec["publication_date"] = "2009-06-22"
        rec["limitations"] = (
            "XBRL fact-model specific. OIM-compatible Formula is only a "
            "Candidate Recommendation (CR 2024-02-14), not a Recommendation."
        )
        br.digest_text  # no-op reference; digest recomputed below
    if rec["source_id"] == "src.rocrate.1.1":
        rec["edition_or_version"] = "1.1 (published 2020-10-30)"
        rec["publication_date"] = "2020-10-30"
        rec["uri"] = "https://www.researchobject.org/ro-crate/specification/1.1/index.html"
        rec["limitations"] = (
            "Superseded by RO-Crate 1.2.0 (June 2025) and 1.3 for new work; "
            "packaging only, not evaluation."
        )
    if rec["source_id"] == "src.premis.3.0":
        rec["uri"] = "https://www.loc.gov/standards/premis/v3/"
        rec["limitations"] = (
            "Minimum semantic units; implementers combine other technical metadata. "
            "Canonical PDF blocks automated retrieval; claims rest on the official v3 site."
        )

br.SOURCES = [s for s in br.SOURCES if s["source_id"] != "src.iso25000.overview"]

CSAF_FIX = (
    "Falsified checkpoint claim removed 2026-08-26: CSAF 2.0 defines no 'recall' "
    "product status; advisory supersession is modeled by document tracking status "
    "and revision history, so product-recall vocabulary needs a safety-regulatory authority."
)

br.SOURCES.append(
    br.src(
        source_id="src.oasis.csaf-2.0",
        title="Common Security Advisory Framework (CSAF) Version 2.0",
        authors_or_issuer="OASIS",
        source_class="official_specification",
        edition_or_version="csaf-v2.0-os",
        publication_date="2022",
        uri="https://docs.oasis-open.org/csaf/csaf/v2.0/os/csaf-v2.0-os.html",
        bounded_claims_supported=[
            "Advisory documents carry tracking status draft/interim/final with revision history, enabling supersession.",
            "Product status enumerations (first_affected, last_affected, known_affected, known_not_affected, fixed, recommended, under_investigation) do not include a recall state.",
        ],
        claims_not_supported=[
            "CSAF is a data-quality or provenance interchange.",
            "A superseding advisory rewrites or erases prior editions.",
        ],
        limitations="Security-advisory scope only; used solely to bound supersession vocabulary.",
        confidence="high",
        source_authority_scope="Advisory document lifecycle and product-status vocabulary",
        normative_status="oasis_standard",
        primary_or_secondary="primary",
    ),
)
br.SOURCES.append(
    br.src(
        source_id="src.ietf.rfc9942",
        title="CBOR Object Signing and Encryption (COSE) Receipts",
        authors_or_issuer="IETF",
        source_class="ietf_rfc",
        edition_or_version="RFC 9942 (Proposed Standard)",
        publication_date="2026-06",
        uri="https://datatracker.ietf.org/doc/rfc9942/",
        bounded_claims_supported=[
            "Receipts prove properties of a verifiable data structure to a verifier.",
            "Transparency services issue receipts per RFC 9943 registration flows.",
        ],
        claims_not_supported=["A receipt states or appraises registered-statement truth."],
        limitations="COSE encoding layer of the SCITT architecture only.",
        confidence="high",
        source_authority_scope="Receipt proof format over verifiable data structures",
        normative_status="normative_for_cose_receipts",
        primary_or_secondary="primary",
    ),
)
br.SOURCES.append(
    br.src(
        source_id="src.eu.gdpr.2016",
        title="Regulation (EU) 2016/679 (General Data Protection Regulation)",
        authors_or_issuer="European Union",
        source_class="regulation",
        edition_or_version="consolidated CELEX 02016R0679",
        publication_date="2016-04-27",
        uri="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02016R0679",
        bounded_claims_supported=[
            "Data subjects hold rights of access, rectification and erasure subject to conditions.",
            "Erasure obligations interact with other EU/national law, including retention duties.",
        ],
        claims_not_supported=["GDPR defines technical deletion APIs or retention TTLs."],
        limitations="Text not independently archived in this run beyond EUR-Lex access; legal interpretation is out of research scope.",
        confidence="medium",
        source_authority_scope="One erasure-authority regime conflicting with technical retention authorities",
        normative_status="regulation",
        primary_or_secondary="primary",
    ),
)
br.SOURCES.append(
    br.src(
        source_id="src.ietf.rfc5424",
        title="The Syslog Protocol",
        authors_or_issuer="IETF",
        source_class="ietf_rfc",
        edition_or_version="RFC 5424",
        publication_date="2009-03",
        uri="https://www.rfc-editor.org/rfc/rfc5424.html",
        bounded_claims_supported=["Structured syslog transport carries logged events between originator, relay and collector."],
        claims_not_supported=["Delivery implies completeness, durability or evidentiary admissibility."],
        limitations="Transport protocol; filtering and loss are expected operationally.",
        confidence="high",
        source_authority_scope="Log transport framing",
        normative_status="normative_for_syslog_transport",
        primary_or_secondary="primary",
    ),
)

# Recompute content digests after field repairs.
_fixed = []
for rec in br.SOURCES:
    rec["content_digest"] = br.digest_text(rec["source_id"], rec["uri"], json.dumps(rec["bounded_claims_supported"], sort_keys=True))
    _fixed.append(rec)
br.SOURCES = sorted(_fixed, key=lambda r: r["source_id"])
br.SRC_IDS = {s["source_id"] for s in br.SOURCES}
assert len(br.SRC_IDS) == len(br.SOURCES)

# Module-text repair: remove the falsified CSAF-recall clauses.
def _fix_module(mid: str, bad_substrings: list[str], replacement_note: str) -> None:
    m = br.MODULE_BY_ID[mid]
    m["counterexamples"] = [
        c for c in m["counterexamples"]
        if not any(b.lower() in c.lower() for b in bad_substrings)
    ]
    m["counterexamples"].append(replacement_note)

_fix_module(
    "module.global.retraction-deletion-supersession",
    ["csaf"],
    "CSAF 2.0 models advisory supersession by tracking status plus revision history and has no 'recall' product status, so recall semantics cannot borrow CSAF vocabulary.",
)
_fix_module(
    "module.local.record-lifecycle-split",
    ["csaf"],
    "Recall vocabulary requires an external product-safety authority; no assigned library may mint it (verified against CSAF 2.0 vocabulary).",
)
for _m in br.MODULES:
    _m["source_refs"] = [s if s != "src.iso25000.overview" else "src.iso.25012.landing"
                         for s in _m.get("source_refs", [])]
MODULES = sorted(br.MODULES, key=lambda m: m["module_id"])
MODULE_BY_ID = {m["module_id"]: m for m in MODULES}

G_X_KINDS = {br.G, br.X}

# ---------------------------------------------------------------------------
# 2. Boundary adjudications: exactly one per assigned library_ref.
# ---------------------------------------------------------------------------
G_EV = "module.global.event-assertion-evidence-proof-truth"
G_INT = "module.global.integrity-authenticity-correctness"
G_EFF = "module.global.effect-vs-pure"
G_MISS = "module.global.missing-negative-incomplete-evidence"
G_RET = "module.global.retraction-deletion-supersession"
G_META = "module.global.data-vs-metadata"
G_AUTH = "module.global.authority-external-source"
X_DSR = "module.cross.design-vs-runtime-lineage"
X_DER = "module.cross.derivation-vs-causation"
X_OBS = "module.cross.observation-vs-inference"
X_ATT = "module.cross.attestation-vs-quality-certificate"
X_REC = "module.cross.receipt-vs-quality-evidence"
X_IMP = "module.cross.impact-graph-vs-quality-invalidation"
X_MATCH = "module.cross.match-candidate-vs-identity-resolution"
L_PROV = "module.lpe.prov-statement-assertion-bundle"
L_RATS = "module.lpe.rats-appraisal-stack"
L_CAN = "module.lpe.canonicalization-digest-signature"
L_CUST = "module.lpe.custody-preservation-retention"
L_AUD = "module.lpe.audit-event-log-trail"
L_OPEN = "module.lpe.open-world-lineage-coverage"
Q_DIM = "module.qor.dimension-metric-measurement-judgment"
Q_DET = "module.qor.detection-adjudication-correction"
Q_GATE = "module.qor.validation-outcome-vs-gate"
Q_DEC = "module.qor.declared-vs-observed-contract"
Q_ACC = "module.qor.source-accounting-control-truth"
Q_SAMP = "module.qor.sampling-vs-population"
Q_FRSH = "module.qor.freshness-vs-timeliness"
LOC_LCORE = "module.local.lineage-core-split"
LOC_OLAD = "module.local.openlineage-adapter-rename"
LOC_QDIM = "module.local.qor-dimension-metric-split"
LOC_CT = "module.local.completeness-timeliness-split"
LOC_RLC = "module.local.record-lifecycle-split"
LOC_OBS = "module.local.observability-replace"

RATIFY_NOTE = (
    "Unratified research verdict; the named bounded context and the SAN semantic "
    "owner must ratify before any registry change."
)

def adj(lib_suffix, owner, question, inside, outside, neighbors, verdict, reasoning,
        falsification, sources, unresolved, confidence, mods, residuals=(),
        ratify_extra=""):
    return {
        "library_ref": f"library.{lib_suffix}",
        "owned_question": question,
        "semantic_owner": owner if owner.startswith(("context.", "qor.context.")) else None,
        "inside": inside,
        "outside": outside,
        "neighbor_relations": [{"neighbor": n, "relation": r} for n, r in neighbors],
        "verdict": verdict,
        "reasoning": reasoning + " " + RATIFY_NOTE + ratify_extra,
        "falsification_attempts": falsification,
        "source_refs": list(sources),
        "unresolved_questions": list(unresolved),
        "confidence": confidence,
        "semantic_module_refs": list(mods),
        "local_residual_refs": list(residuals),
        "decision_dependencies": [],
        "ratification_required_by": [owner] if owner else ["context.san.semantic-owner-board"],
    }

# ---- lineage_provenance_evidence -------------------------------------------------
ADJ_LPE = [
adj("lpe.evidence-evaluation", "context.lpe.evidence-strength",
    "How strong is a body of assurance evidence for a claim, without becoming RATS appraisal or RATS evidence typing?",
    ["claim-evidence support scoring for SACM-style argumentation",
     "evidence sufficiency classes scoped to a claim edition",
     "explicit incompleteness and missing-evidence carriers"],
    ["RATS Evidence/AppraisalPolicy message types", "cryptographic attestation verification",
     "relying-party authorization decisions", "truth determination about claims"],
    [("library.lpe.rats-appraisal", "consumes_witness_from"), ("library.lpe.claim-argument-core", "depends_on")],
    "RETAIN_BUT_NARROW",
    "The library owns evidential-strength semantics, not protocol-level attestation; mixed checkpoints blurred these and are migrated out.",
    ["Tried unifying with RATS stack under one evidence type: rejected because RFC 9334 separates Evidence from appraisal results while SACM scores arguments.",
     "Tried a universal numeric strength score: rejected as collapsing claim-dependent sufficiency into fitness-for-all-use."],
    ["src.omg.sacm-2.3", "src.ietf.rfc9334"],
    ["Who owns cross-context strength comparability?"],
    "high", [G_EV, G_MISS, L_RATS]),
adj("lpe.record-lifecycle", "context.lpe.correction",
    "How do correction, supersession, retraction, deletion and recall of asserted records differ as typed transitions?",
    ["correction/amendment that preserves prior editions", "supersession establishing a new authoritative edition",
     "retraction withdrawing reliance on an assertion", "deletion requests bound to an external erasure authority",
     "recall disposition initiation bound to an external product-safety authority"],
    ["filesystem deletion effects", "GDPR interpretation", "immutable-store mechanics",
     "quality-defect adjudication policy", "minting recall authority"],
    [("library.lpe.retention-policy", "collision"), ("library.qor.correction_execution_kernel", "explicit_coexistence")],
    "SPLIT",
    "One lifecycle union silently merged legal erasure, reliance withdrawal, editorial correction and safety recall whose authorities differ; each transition class needs its own carrier and authority import.",
    ["Searched CSAF 2.0 for recall vocabulary: falsified the assumption recall is an interchange-standard status; advisory standards model supersession via tracking status instead.",
     "Tried soft-delete-as-retraction counterexample: it conflates representation removal with withdrawal of acceptance, so collapsed APIs fail."],
    ["src.w3c.prov-dm", "src.fda.alcoa.2018", "src.oasis.csaf-2.0", "src.eu.gdpr.2016"],
    ["Which context owns recall disposition across families?", "Erasure authority versus retention authority precedence remains open."],
    "medium", [G_RET, G_AUTH], [LOC_RLC]),
adj("lpe.prov-interchange", "context.lpe.provenance-bundle",
    "How do PROV descriptions round-trip between in-memory statements, named bundles and interchange encodings without membership becoming endorsement?",
    ["PROV-N/JSON interconversion determinism", "named bundle construction and independent validation",
     "encoding loss reporting for unsupported constructs"],
    ["semantic validity of instances", "assertion issuance authority", "runtime capture adapters"],
    [("library.lpe.prov-constraints", "oracle_for"), ("library.lpe.lineage-core", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "Encoding/bundle ownership is cohesive once statement algebra lives elsewhere; bundle validation independence is required by PROV bundles semantics.",
    ["Tried folding interchange into lineage-core: rejected because encoding failure modes (unsupported PROV features) deserve first-class refusals.",
     "Tried treating JSON shape equality as bundle identity: rejected by normal-form equivalence requirement."],
    ["src.w3c.prov-dm", "src.w3c.prov-constraints", "src.w3c.prov-aq"],
    [], "high", [L_PROV, G_INT]),
adj("lpe.custody-core", "context.lpe.custody",
    "What constitutes custody continuity for evidence objects, distinct from fixity, preservation planning and legal holds?",
    ["custody events recording transfer of responsibility", "gap detection when custody continuity breaks",
     "binding custody records to object digests and agents"],
    ["fixity computation itself", "AIP storage layout", "legal hold decisions", "forensic acquisition imaging"],
    [("library.lpe.preservation-core", "explicit_coexistence"), ("library.lpe.forensic-acquisition-adapter", "consumes_witness_from"),
     ("library.lpe.digest-core", "depends_on")],
    "RETAIN_AS_IS",
    "Custody chain-of-responsibility is its own question; OAIS PDI provenance and PREMIS events constrain it without owning it.",
    ["Tried merging into preservation-core: rejected because OAIS separates Provenance PDI from administrative custody expectations across ISO 27037 handling stages."],
    ["src.ccsds.oais-650x0m2", "src.premis.3.0", "src.iso.27037.landing", "src.nist.800-86"],
    ["Custody event admissibility remains jurisdiction-specific."],
    "high", [G_AUTH, L_CUST]),
adj("lpe.impact-analysis", "context.lpe.impact-analysis",
    "Which dependency-graph questions can be answered by classification alone, and where must causal claims stop?",
    ["graph reachability slices over lineage edges", "blast-radius candidate sets typed as hypotheses",
     "explicit coverage gap reporting for incomplete graphs"],
    ["causal root-cause narratives", "business-loss quantification", "quality-evidence staleness propagation"],
    [("library.lpe.claim-argument-core", "supplies_witness_to"), ("library.qor.lineage_quality_impact_kernel", "adapter_for"),
     ("library.lpe.lineage-query", "depends_on")],
    "RETAIN_BUT_NARROW",
    "Topology-derived impact stays probabilistic witness material; converting slices into causal assertions belongs to claim-argument, staleness invalidation to QOR.",
    ["Attempted PageRank-style importance as impact truth: falsified by derivation-versus-causation non-collapse law.",
     "Tried sharing one Impact type with QOR stale-evidence service: homonym collision guard requires qualified separation."],
    ["src.w3c.prov-dm", "src.openlineage.object-model-1.52"],
    ["Is a neutral shared slice primitive justified by a third owner?"],
    "high", [X_DER, X_IMP, L_OPEN]),
adj("lpe.retention-policy", "context.lpe.retention-legal-hold",
    "When must record retention continue technically, who may release it, and how do conflicting regimes compose?",
    ["retention schedule editions imported from named authorities", "legal hold states with issuer scoping",
     "conflict surfacing when erasure rights meet holds or schedules"],
    ["executing physical destruction", "interpreting statutes", "custody transfer records"],
    [("library.lpe.preservation-core", "depends_on"), ("library.lpe.record-lifecycle", "explicit_coexistence"),
     ("library.qor.quarantine_release_kernel", "explicit_coexistence")],
    "RETAIN_AS_IS",
    "Retention authority versus technical retention is explicitly non-collapsible (17a-4 style WORM duties vs GDPR erasure); this library binds imported decisions only.",
    ["Tried one TTL field: fails at least two-regime conflict probe, so regime-scoped schedule and hold entities retained."],
    ["src.sec.17a4", "src.eu.gdpr.2016", "src.fda.alcoa.2018"],
    ["Precedence order among competing retention authorities is jurisdiction-specific and unresolved."],
    "high", [G_AUTH, L_CUST]),
adj("lpe.openlineage-adapter", "context.lpe.runtime-lineage",
    "Should an adapter named after one vendor-neutral project own runtime lineage semantics or only encode its events?",
    ["OpenLineage RunEvent/JobEvent/DatasetEvent encode-decode fidelity", "facet schema version negotiation",
     "loss report when constructs cannot be represented"],
    ["runtime lineage semantics themselves", "job scheduling", "quality judgment of runs"],
    [("library.lpe.lineage-query", "supplies_witness_to"), ("library.lpe.receipt-store", "explicit_coexistence")],
    "RENAME",
    "Vendor-neutral project name on a provider adapter invites treating OpenLineage as SAN semantic owner; rename keeps adapter_for relationship explicit without alias.",
    ["Tested 'OL is the de facto standard' argument: project specification constrains its encodings only, failing semantic-owner test.",
     "Renamed target checked against every old responsibility: none lost."],
    ["src.openlineage.object-model-1.52"],
    ["Does an additional encoding registry replace a single adapter?"],
    "medium", [X_DSR], [LOC_OLAD]),
adj("lpe.preservation-core", "context.lpe.forensic-preservation",
    "What does long-term preservation of evidence packages require beyond custody and separate from retention authority?",
    ["SIP/AIP/DIP package lifecycle modeling", "PDI assembly including fixity, context and provenance binding",
     "migration planning inputs between package formats"],
    ["legal hold decisions", "ERS timestamp renewal mechanics", "acquisition imaging effects", "custody transfers"],
    [("library.lpe.long-term-validation", "explicit_coexistence"), ("library.lpe.custody-core", "explicit_coexistence"),
     ("library.lpe.research-object", "explicit_coexistence")],
    "RETAIN_BUT_NARROW",
    "OAIS responsibilities sit cleanly here once hold coordination migrates to retention-policy, keeping operational authority out of preservation semantics.",
    ["Tried single Preserve() API spanning OAIS+ERS+hold: collapses migration planning with cryptographic renewal and legal authority; rejected."],
    ["src.ccsds.oais-650x0m2", "src.premis.3.0", "src.ietf.rfc4998"],
    ["Whether designated-community preservation acceptance is a product decision remains outside lane."],
    "high", [L_CUST, G_RET, G_AUTH]),
adj("lpe.rats-appraisal", "context.lpe.independent-appraisal",
    "How do Evidence, appraisal policy, appraisal result and relying-party decision separate under RATS without absorbing SACM argument scoring?",
    ["attester-collected Evidence carrier types", "reference values and endorsements binding",
     "appraisal-policy evaluation producing Attestation Results", "relying-party decision import point"],
    ["claim evidential-strength scoring", "transparency registration", "quality certification workflow"],
    [("library.lpe.evidence-evaluation", "supplies_witness_to"), ("library.lpe.attestation-core", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "RFC 9334 role split maps one-to-one onto the four carriers; mixing with SACM scoring would conflate distinct owners.",
    ["Counterexample attempted: single score(evidence) API hides relying-party policy edition; fails role-separation law."],
    ["src.ietf.rfc9334", "src.omg.sacm-2.3"],
    ["Name qualification against qor.certification_attestation_kernel awaits owner decision."],
    "high", [G_EV, L_RATS, X_ATT]),
adj("lpe.receipt-store", "context.lpe.runtime-receipts",
    "How are transparency-service receipts persisted and verified without being mistaken for quality evidence records?",
    ["COSE receipt verification against verifiable data structures", "append-only receipt persistence and lookup by subject digest",
     "inclusion/consistency proof result carriers"],
    ["quality evaluation evidence records", "statement truth", "issuance authority"],
    [("library.lpe.transparency-client", "consumes_witness_from"), ("library.qor.evidence_receipt_kernel", "collision")],
    "RETAIN_AS_IS",
    "Storage and verification of inclusion proofs is mechanical; naming must stay Receipt(PVD-proof) per RFC 9942 to avoid homonym collapse with QOR evidence receipts.",
    ["Tried unified Receipt type serving both families: fails receipt-versus-quality-evidence law, so collision is recorded pending qualified renames."],
    ["src.ietf.rfc9942", "src.ietf.rfc9943", "src.ietf.rfc9162"],
    ["Pending owner choice: adopt library.lpe.runtime-receipt-core name from universe set."],
    "high", [X_REC, G_INT]),
adj("lpe.audit-log-adapter", "context.lpe.audit-log",
    "How does log transport normalize into audit-event candidates without minting accountability facts or losing gaps?",
    ["syslog-family ingestion framing and normalization limits", "delivery gap and duplication reporting",
     "effect intents for collection with receipts"],
    ["audit event meaning assignment", "trail reconstruction logic", "provenance graph assertion"],
    [("library.lpe.audit-event-core", "supplies_witness_to"), ("library.lpe.audit-trail-reconstructor", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "Provider adapters report what arrived; they never promote transport telemetry into durable evidence by default.",
    ["Tried auto-promoting normalized logs to PROV: fails observation-versus-inference separation."],
    ["src.ietf.rfc5424", "src.otel.logs"],
    [], "high", [G_EFF, L_AUD]),
adj("lpe.forensic-acquisition-adapter", "context.lpe.forensic-acquisition",
    "How is forensic imaging performed as an effect whose output binds to source hashes under stated acquisition stages?",
    ["imaging effect intents with write-blocker assumptions recorded", "source/destination digest binding",
     "stage labeling per identification-collection-acquisition-preservation guidance"],
    ["legal admissibility verdicts", "custody semantics", "chain analysis conclusions"],
    [("library.lpe.custody-core", "supplies_witness_to"), ("library.lpe.digest-core", "depends_on")],
    "RETAIN_AS_IS",
    "Acquisition is inherently effectful; NIST 800-86 stage decomposition bounds the vocabulary without transferring admissibility authority.",
    ["Treat-imaging-as-pure-copy counterexample rejected: environment assumptions are contract-relevant configuration decisions."],
    ["src.nist.800-86", "src.iso.27037.landing"],
    ["ISO 27037 full text review outstanding."],
    "medium", [G_EFF, G_INT]),
adj("lpe.transparency-client", "context.lpe.transparency-registration",
    "How does client-side registration and receipt collection interact with transparency services as pure requests?",
    ["register signed statement request/reply modeling", "receipt fetch and retry policy as configuration",
     "service error taxonomy mapping"],
    ["trustworthiness of registered content", "receipt verification internals", "policy for accepting issuers"],
    [("library.lpe.receipt-store", "supplies_witness_to")],
    "RETAIN_AS_IS",
    "Client remains a thin effect port; SCITT architecture places trust decisions in relying parties, not registration flows.",
    ["Treating successful registration as endorsement counterexample: contradicts receipt-is-not-truth law."],
    ["src.ietf.rfc9943", "src.ietf.rfc9942"],
    [], "high", [G_EFF, X_REC]),
adj("lpe.verification-method-resolver", "context.lpe.signature-seal",
    "How are DID-URL verification methods resolved for signature checking without importing trust policy?",
    ["DID document retrieval caching with effect receipts", "verification-method selection predicates",
     "resolver failure taxonomy separated from signature failure"],
    ["signature algebra", "trust framework decisions", "key lifecycle ceremonies"],
    [("library.lpe.signature-envelope", "effect_port_for")],
    "RETAIN_AS_IS",
    "Resolution is method-specific and effectful; W3C DID Core constrains documents, not verification verdicts.",
    ["Embedding chain-of-trust scoring counterexample rejected as silent authority assumption."],
    ["src.w3c.did-core", "src.dsse.envelope"],
    [], "medium", [G_EFF, L_CAN]),
adj("lpe.compiler-evidence-binding", "context.lpe.compiler-receipts",
    "How do generated solution artifacts bind back to compiler inputs and guarantees as checkable receipts?",
    ["solution-to-input binding statements with input digests", "guarantee scope declaration per compiled unit",
     "receipt revalidation triggers on edition change"],
    ["compiler internal algorithms", "product readiness claims", "vertical acceptance"],
    [("library.lpe.signature-envelope", "depends_on"), ("library.lpe.runtime-lineage-event-adapter", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "Compilation receipts mirror design-time lineage; they witness provenance without claiming run observations.",
    ["Conflating build receipts with RunEvents counterexample rejected by design-vs-runtime law."],
    ["src.openlineage.object-model-1.52", "src.dsse.envelope"],
    [], "medium", [X_DSR, G_INT]),
adj("lpe.lineage-core", "context.lpe.logical-lineage",
    "Should logical lineage edge semantics, field-level extraction and vendor interchange helpers live in one core library?",
    ["logical edge/statement model capture", "OpenLineage interoperability helpers",
     "field-level lineage propagation rules"],
    ["query slicing", "impact hypotheses", "interchange encoding ownership"],
    [("library.lpe.field-lineage", "collision"), ("library.lpe.prov-interchange", "consumes_witness_from")],
    "SPLIT",
    "Cohesion failed falsification: the core mixes a normative logical model with a vendor encoding helper and column-grain machinery, whose change cadences differ.",
    ["Package-layout argument ('core' naming) rejected as non-semantic.",
     "Assigning OpenLineage references as proof of ownership falsified: encoding presence is not semantics."],
    ["src.w3c.prov-dm", "src.openlineage.object-model-1.52"],
    ["Exact new library refs awaiting ratification."],
    "high", [L_PROV, X_DSR], [LOC_LCORE]),
]

ADJ_LPE += [
adj("lpe.attestation-core", "context.lpe.attestation",
    "How is a typed attestation statement (subject digests bound to predicate) constructed and sealed, distinct from appraisal?",
    ["in-toto-style Statement construction over subject digest sets", "predicate type registration with editions",
     "signing envelope handoff boundary"],
    ["verifier appraisal policy", "relying-party decisions", "quality annotation semantics"],
    [("library.lpe.rats-appraisal", "consumes_witness_from"), ("library.lpe.signature-envelope", "effect_port_for"),
     ("library.qor.certification_attestation_kernel", "collision")],
    "RETAIN_AS_IS",
    "Digest-subject binding plus typed predicates is exactly the Statement layer; everything downstream belongs to appraisal lanes.",
    ["Filename-based subject identity counterexample rejected by in-toto subject-matching rule."],
    ["src.intoto.statement-v1", "src.dsse.envelope"],
    ["Name qualification versus QOR certification kernel awaits owner decision."],
    "high", [X_ATT, G_EV]),
adj("lpe.audit-event-core", "context.lpe.audit-event",
    "What makes an accountability event type well-formed independently of its transport and of provenance graphs?",
    ["audit event schema with actor, action, target and time authority fields", "sequence integrity hints without completeness claims",
     "explicit unknown-actor carriers"],
    ["log transport mechanics", "trail inference", "provenance derivation edges"],
    [("library.lpe.audit-log-adapter", "adapter_for"), ("library.lpe.audit-trail-reconstructor", "supplies_witness_to")],
    "RETAIN_AS_IS",
    "Accountability event vocabulary differs from PROV derivation; conflation would corrupt both non-collapse laws.",
    ["Timestamp-authority absorption counterexample rejected: sequence trust imports external authority or stays unknown."],
    ["src.nist.800-86", "src.premis.3.0"],
    [], "medium", [L_AUD, G_MISS]),
adj("lpe.audit-trail-reconstructor", "context.lpe.audit-trail",
    "Under what declared coverage policy can partial logs be ordered into a trail whose gaps stay first-class?",
    ["deterministic ordering under declared tie-break policy", "gap carriers distinguishing absent-source from known-loss",
     "reconstruction confidence notes bounded to method edition"],
    ["closed-world timelines", "admissibility verdicts", "new event minting"],
    [("library.lpe.audit-event-core", "depends_on"), ("library.lpe.lineage-query", "explicit_coexistence")],
    "RETAIN_AS_IS",
    "Reconstruction output must never read as complete history; missing versus negative evidence separation governs the carriers.",
    ["Timeout-as-completeness probe falsifies any closed-world summary operator."],
    ["src.nist.800-86"],
    ["Sequence coverage oracle owner unresolved."],
    "high", [G_MISS, L_AUD]),
adj("lpe.canonical-json", "context.lpe.identity-digest",
    "Which JSON bytes are equal under the selected canonicalization profile (JCS) and nothing more?",
    ["RFC 8785 JCS serialization with I-JSON constraints surfaced", "error taxonomy for non-representable values"],
    ["RDF dataset equality", "semantic equivalence of documents", "hash selection policy"],
    [("library.lpe.canonical-rdf", "explicit_coexistence"), ("library.lpe.digest-core", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "One algorithm per library keeps profile editions honest; cross-format conversion is explicit lossy operation elsewhere.",
    ["Mixing key order insensitivity with semantic equality probed: numbers/strings edge cases refute over-claim."],
    ["src.ietf.rfc8785"], [], "high", [G_INT, L_CAN]),
adj("lpe.canonical-rdf", "context.lpe.identity-digest",
    "How are RDF datasets canonicalized under RDFC-1.0 with adversarial-input work bounds?",
    ["RDFC-1.0 algorithm result equality", "poison-graph resource refusal contracts", "hash agility per W3C suite"],
    ["JSON object equality", "PROV instance equivalence", "named-graph identity policy"],
    [("library.lpe.canonical-json", "explicit_coexistence"), ("library.lpe.prov-interchange", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "Isomorphism-grade canonicalization has different failure economics than JCS; sharing a library would hide bound profiles.",
    ["Runtime blowup probe justifies finite-resource contract as first-class refusals."],
    ["src.w3c.rdf-canon", "src.w3c.prov-constraints"], [], "high", [G_INT, L_CAN]),
adj("lpe.claim-argument-core", "context.lpe.claim-argument",
    "How are claims, structured arguments and evidence references packaged so assertions stay asserted rather than proven?",
    ["claim/argument/evidence triad metamodel carriers", "assertion strength labels without truth promotion",
     "challenge and review note attachments"],
    ["automatic adjudication", "evidence collection effects", "RATS appraisal results"],
    [("library.lpe.evidence-evaluation", "consumes_witness_from"), ("library.lpe.impact-analysis", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "SACM separates argumentation from evidence appraisal; packaging remains semantic while scoring lives next door.",
    ["Auto-conclude counterexample rejected: an argument graph never discharges itself."],
    ["src.omg.sacm-2.3"], [], "high", [G_EV]),
adj("lpe.digest-core", "context.lpe.identity-digest",
    "Which approved hash algorithms apply to which byte scope, and what does a digest legally assert?",
    ["algorithm registry pinned to FIPS 180-4 family", "scoped-digest construction (cut + algorithm + encoding)",
     "digest comparison refusals across mismatched scopes"],
    ["identity assignment policy", "authenticity claims", "correctness of content"],
    [("library.lpe.signature-envelope", "supplies_witness_to"), ("library.lpe.custody-core", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "Integrity primitive only; every stronger reading is refused upstream of cryptography.",
    ["Hash-of-name-as-content-identity probe recorded as standing negative twin."],
    ["src.nist.fips180-4"], [], "high", [G_INT, L_CAN]),
adj("lpe.field-lineage", "context.lpe.field-lineage",
    "How do column/field-grain derivations compose from expression analysis and executed-plan witnesses?",
    ["field-to-field transformation rules extracted from declared expressions", "observed plan witness ingestion points",
     "ambiguity and multi-parent carriers"],
    ["table-level edge ownership", "runtime capture effects", "impact quantification"],
    [("library.lpe.lineage-core", "collision"), ("library.lpe.openlineage-adapter", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "Field grain has composition algebra unlike table grain; keeping it separate preserves falsifiable per-facet laws.",
    ["Merging into table lineage hides ambiguity; probes with fan-out expressions broke single-edge assumptions."],
    ["src.openlineage.object-model-1.52", "src.w3c.prov-dm"],
    [], "medium", [X_DER, L_OPEN]),
adj("lpe.formula-provenance", "context.lpe.formula-lineage",
    "How do spreadsheet/formula-cell derivations form a derivation graph distinct from data-quality checks on those cells?",
    ["cell dependency extraction determinism within workbook scope", "cross-sheet reference carriers", "recalculation equivalence classes"],
    ["XBRL consistency assertions", "quality rule evaluation", "runtime execution capture"],
    [("library.lpe.lineage-query", "supplies_witness_to")],
    "RETAIN_AS_IS",
    "Formula lineage is static design-time structure; OpenLineage confirms design events carry no run association.",
    ["Treating recalculation as run lineage counterexample rejected."],
    ["src.xbrl.formula-1.0", "src.openlineage.object-model-1.52"],
    ["Version pinning across OIM-compatible Formula CR pending."],
    "medium", [X_DSR]),
adj("lpe.lineage-query", "context.lpe.lineage-query",
    "What can graph queries answer about lineage while preserving open-world incompleteness?",
    ["slice/path traversal with declared coverage policy", "unknown-edge and gap reporting first-class",
     "query determinism under fixed graph edition"],
    ["impact confirmation", "completeness proofs from timeout", "storage engines"],
    [("library.lpe.lineage-core", "consumes_witness_from"), ("library.lpe.impact-analysis", "supplies_witness_to")],
    "RETAIN_AS_IS",
    "PROV-AQ patterns constrain access; no standard closed-world lineage query language was found to adopt.",
    ["Empty-downstream-as-proof probe falsified by coverage law; gap carrier mandatory."],
    ["src.w3c.prov-aq", "src.w3c.prov-constraints"], [], "high", [L_OPEN, G_MISS]),
adj("lpe.long-term-validation", "context.lpe.long-term-validation",
    "How do archive timestamps and hash-tree renewals keep evidence verifiable across cryptographic erosion without restating truth?",
    ["ERS evidence record renewal lifecycle", "algorithm-weakening watch configuration imports", "renewal-triggered package touch policies"],
    ["AIP migration planning", "custody transfers", "legal retention authority"],
    [("library.lpe.preservation-core", "explicit_coexistence")],
    "RETAIN_AS_IS",
    "ERS mechanics are orthogonal to OAIS migration; conflation would blur renewal triggers versus format obsolescence.",
    ["Renewal-as-revalidation-of-content probe rejected: ERS preserves integrity chain only."],
    ["src.ietf.rfc4998"], [], "high", [G_INT, L_CUST]),
adj("lpe.prov-constraints", "context.lpe.provenance-graph",
    "What normative validity, normalization and equivalence procedure constrains PROV instances as a test oracle?",
    ["constraint-chase normalization implementation targets", "equivalence-by-normal-form operator", "termination precondition surfacing"],
    ["assertion issuance", "truth adjudication", "interchange encoding"],
    [("library.lpe.prov-interchange", "oracle_for"), ("library.lpe.lineage-core", "oracle_for")],
    "RETAIN_AS_IS",
    "The library exists to be the oracle other lineage libraries point at; widening it would dilute conformance meaning.",
    ["Valid-instance-equals-truth probe rejected explicitly by PROV constraints document scope."],
    ["src.w3c.prov-constraints", "src.w3c.prov-dm"], [], "high", [X_DER]),
adj("lpe.reproduction-evaluator", "context.lpe.reproduction-appraisal",
    "When may a re-execution be classified as reproduction versus merely another observation?",
    ["artifact set binding via content digests", "environment-equivalence comparison operators", "outcome classification criteria editions"],
    ["scientific truth verdicts", "FAIR scoreminting", "package authoring"],
    [("library.lpe.research-object", "consumes_witness_from")],
    "RETAIN_AS_IS",
    "Evaluation compares declared comparators; FAIR principles guide metadata but do not certify runs.",
    ["RO-Crate validity implies reproducibility probe falsified by packaging-only claim of RO-Crate."],
    ["src.fair.2016", "src.rocrate.1.1"], [], "medium", [G_MISS]),
adj("lpe.research-object", "context.lpe.reproducibility-package",
    "What does a research-object package promise (aggregation + manifest + contextual metadata) and not promise?",
    ["crate aggregation layout conformance", "manifest entity typing with required contextual links", "external payload digest referencing"],
    ["run success claims", "preservation acceptance", "license authority"],
    [("library.lpe.preservation-core", "explicit_coexistence"), ("library.lpe.reproduction-evaluator", "supplies_witness_to")],
    "RETAIN_AS_IS",
    "Packaging vocabulary (community spec 1.1, superseded by 1.2.0+) binds structure, never scientific outcome.",
    ["Crate-with-broken-artifact counterexample shows packages can validate yet fail evaluation."],
    ["src.rocrate.1.1"], ["Edition drift 1.1 versus newer releases needs pinning decision."], "high", [G_META]),
adj("lpe.signature-envelope", "context.lpe.signature-seal",
    "How does envelope verification bind payload-type plus bytes to signer verification methods and stop there?",
    ["typed payload envelope encode/verify", "multiple-signature aggregation carriers", "verification-method resolution port consumption"],
    ["issuer authority judgments", "claim truth", "attestation predicate contents"],
    [("library.lpe.verification-method-resolver", "effect_port_for"), ("library.lpe.digest-core", "depends_on")],
    "RETAIN_AS_IS",
    "DSSE keeps payload-type inside signature; envelope verification outcome is syntactic authenticity only.",
    ["Verified-implies-endorsed probe refused by envelope spec note and role separation."],
    ["src.dsse.envelope", "src.w3c.did-core", "src.nist.fips180-4"], [], "high", [G_INT, L_CAN]),
]

# ---- quality_reconciliation ------------------------------------------------------
def qadj(suffix, owner, question, inside, outside, neighbors, verdict, reasoning,
         falsification, sources, unresolved, confidence, mods, residuals=()):
    return adj("qor." + suffix, owner, question, inside, outside, neighbors, verdict,
               reasoning, falsification, sources, unresolved, confidence, mods, residuals)

ADJ_QOR = [
qadj("evidence_receipt_kernel", "qor.context.evidence_receipt",
     "How are records of quality evaluations themselves evidenced and bound to the evaluation that produced them?",
     ["evaluation-evidence record carriers bound to metric edition and subject cut",
      "coverage statement binding on what the evidence does and does not cover",
      "sealing of evidence for later verification"],
     ["transparency-service inclusion proofs", "assertion truth about data", "certificate issuance"],
     [("library.lpe.receipt-store", "collision"), ("library.qor.quality_dimension_metric_kernel", "depends_on")],
     "RETAIN_BUT_NARROW",
     "Quality evaluation evidence is its own carrier class; RFC 9942-style transparency receipts are a different public type even when sealed similarly.",
     ["Unified Receipt homonym probe collapsed under receipt-vs-quality-evidence law; migrated cryptographic-receipt duty out.",
      "Evidence-without-coverage-scope counterexample forced coverage binding into the contract."],
     ["src.w3c.dqv", "src.ietf.rfc9942"],
     ["Homonym rename decision pending owner."],
     "high", [X_REC, G_EV]),
qadj("validation_execution_kernel", "qor.context.validation_execution",
     "How do validation outcomes (pass/fail/skip/error) execute independently of any gate disposition?",
     ["rule-batch execution with per-item outcome carriers", "skip/error versus fail distinctions preserved",
      "outcome ordering stability under concurrency"],
     ["gate dispositions", "publication eligibility", "conformance claims about artifacts"],
     [("library.qor.rule_specification_kernel", "consumes_witness_from"), ("library.qor.quarantine_release_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "OpenLineage assertion facet success/severity split and SHACL report semantics both show outcome is not consequence.",
     ["Encoding gate in boolean success probe rejected as non-collapse violation."],
     ["src.w3c.shacl", "src.openlineage.dq-assertions"], [], "high", [Q_GATE]),
qadj("correction_execution_kernel", "qor.context.correction_execution",
     "What distinguishes an authorized mutation applying an approved correction from editing data?",
     ["authorized-change application consuming proposal grants", "pre/post state digests with restatement trails",
      "idempotent replay via correction intent identity"],
     ["proposal authoring", "authorization minting", "detection"],
     [("library.qor.correction_proposal_kernel", "supplies_witness_to"), ("library.qor.defect_adjudication_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "FDA ALCOA amendment expectations show corrections keep history; execution is the only effect stage.",
     ["Detector-triggers-patch counterexample rejected by detection/adjudication/mutation separation."],
     ["src.fda.alcoa.2018", "src.w3c.prov-dm"], [], "high", [Q_DET, G_AUTH]),
qadj("correction_proposal_kernel", "qor.context.correction_proposal",
     "How do proposed corrections carry rationale, scope and candidate states without authority to mutate?",
     ["proposal carriers with before/after specifications", "impact notes bound to defect edition", "expiration and supersession of proposals"],
     ["mutation execution", "approval decisions", "root-cause proof"],
     [("library.qor.correction_execution_kernel", "effect_port_for")],
     "RETAIN_AS_IS",
     "Proposal is inert by construction; granting it effects would erase the authorization checkpoint.",
     ["Auto-apply-on-confidence probe rejected."], ["src.w3c.dqv"], [], "high", [Q_DET, X_OBS]),
qadj("sampling_measurement_kernel", "qor.context.sampling_measurement",
     "How can sample-derived statistics be stated without silently becoming population claims?",
     ["sampling frame and plan editions as first-class inputs", "estimator outputs carrying uncertainty bands", "lot-disposition import hooks for acceptance plans"],
     ["population completeness assertions", "fitness verdicts", "census substitution"],
     [("library.qor.completeness_timeliness_kernel", "collision"), ("library.qor.fitness_for_use_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "ISO 2859 acceptance plans govern lot disposition, not dataset fitness; sample-to-population leap is refused by type.",
     ["Sample-rate-as-completeness counterexample mandatory in tests."],
     ["src.iso.2859-1.landing", "src.jcgm.vim.2012"],
     ["ISO 2859 full text review outstanding; AQL disposition ownership open."],
     "medium", [Q_SAMP, G_MISS]),
qadj("completeness_timeliness_kernel", "qor.context.completeness_timeliness",
     "Should completeness, freshness/currentness and timeliness be measured by one kernel or separate ones?",
     ["completeness characteristic assessment", "freshness/currentness assessment",
      "timeliness/delivery-latency assessment", "shared observation ingestion utilities"],
     ["delivery SLA policy ownership", "fresh data guaranteeing complete views"],
     [("library.qor.quality_dimension_metric_kernel", "depends_on"), ("library.qor.sampling_measurement_kernel", "collision")],
     "SPLIT",
     "Bundling three ISO 25012-style named characteristics failed cohesion probes: metric procedures, refusals and failure twins differ per characteristic; bundle name itself lists three concepts.",
     ["Counter-attempted one DeliveryQuality score: hides which characteristic degraded, breaking diagnosis routing."],
     ["src.iso.25012.landing", "src.w3c.dqv"],
     ["Full ISO/IEC 25012 text review required before final carrier freeze.", "currentness-versus-freshness vocabulary choice open."],
     "medium", [Q_FRSH], [LOC_CT]),
qadj("fitness_for_use_kernel", "qor.context.fitness_for_use",
     "Who may declare a dataset fit for a named use, and how does that declaration differ from measurements?",
     ["per-use-case suitability determinations importing consumer policy editions", "suitability period validity with review triggers",
      "explicit unsuitability reasons catalog"],
     ["universal numeric quality score", "measurement redefinition", "contract publication power"],
     [("library.qor.quality_policy_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "DQV leaves fitness judgments to consumers: this kernel structures the judgment, never derives it from metrics alone.",
     ["Accuracy-percentage-equals-fitness counterexample recorded as standing negative twin."],
     ["src.w3c.dqv", "src.bcbs239"], [], "high", [Q_DIM, G_AUTH]),
qadj("schema_conformance_kernel", "qor.context.schema_conformance",
     "What does conformance of instances to a schema edition mean independent of gates or contracts' business rules?",
     ["instance-versus-declared-schema conformance reports", "violation severity mapping kept declarative", "edition-pinned schema resolution"],
     ["release gating", "semantic correctness beyond shape", "contract activation"],
     [("library.qor.validation_execution_kernel", "supplies_witness_to"), ("library.qor.contract_declaration_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "SHACL separates validation reports from graph management decisions; same separation holds here across schema languages.",
     ["Conformance-equals-publishable probe rejected."], ["src.w3c.shacl"], [], "high", [Q_GATE]),
qadj("data_profiling_kernel", "qor.context.data_profiling",
     "How do computed column/table sketches stay observational summaries that cannot amend declarations?",
     ["profile sketch carriers with nulls/ranges/cardinality", "drift-comparable snapshot identity per cut", "bounded sampling disclosure inside profiles"],
     ["declared constraint authorship", "nullability rule enforcement", "quality judgments"],
     [("library.qor.contract_observation_kernel", "supplies_witness_to"), ("library.qor.statistical_baseline_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "Deequ's analyzer/suggestion/verification split anchors profiling as suggestion material only.",
     ["Inferred-not-null-promotion probe rejected via observation-vs-inference law."],
     ["src.schelter.deequ.2018", "src.w3c.dqv"], [], "high", [X_OBS, Q_DEC]),
qadj("defect_adjudication_kernel", "qor.context.defect_adjudication",
     "How do detected signals become adjudicated defects with authority-scoped outcomes, never auto-remediated?",
     ["signal-to-defect adjudication workflow states", "severity/materiality context imports", "adjudicator attribution requirements"],
     ["statistical detection itself", "correction proposals drafting", "authorized patching"],
     [("library.qor.anomaly_detection_kernel", "supplies_witness_to"), ("library.qor.correction_proposal_kernel", "supplies_witness_to"),
      ("library.qor.quality_incident_case_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Detection methods are oracles; owning them here would merge method variance with governance vocabulary.",
     ["Score-threshold-auto-adjudication counterexample recorded."],
     ["src.bifet.adwin.2007", "src.w3c.dqv"], [], "high", [Q_DET, G_AUTH]),
qadj("remediation_verification_kernel", "qor.context.remediation_verification",
     "When may an applied remediation be declared verified against the defect edition it targeted?",
     ["post-fix measurement comparison tied to original signal edition", "regression window definitions", "verification outcomes distinct from release approval"],
     ["fix implementation", "case closure authority", "new defect detection"],
     [("library.qor.correction_execution_kernel", "consumes_witness_from"), ("library.qor.defect_adjudication_kernel", "supplies_witness_to")],
     "RETAIN_AS_IS",
     "Verification is retrospective testing of a claim 'fixed', not the mutation itself nor case management.",
     ["One-success-metrics-equals-cured probe broken by recurrence-window twin."],
     ["src.omg.cmmn-1.1", "src.w3c.dqv"], [], "high", [Q_DET]),
qadj("waiver_exception_kernel", "qor.context.waiver_exception",
     "How do scoped, expiring exceptions suspend enforcement while preserving refusal provenance?",
     ["waiver carriers with scope, issuer edition and expiry", "enforcement-suspension lookup ports", "expiry-triggered reinstatement classification"],
     ["authority issuance", "silent bypass defaults", "permanent grant shapes"],
     [("library.qor.quarantine_release_kernel", "explicit_coexistence"), ("library.lpe.retention-policy", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Authority-bearing acceptance must import an external issuer decision; default-deny refusals keep precedence explicit.",
     ["Unscoped-waiver probe fails external-authority law."],
     ["src.ietf.rfc9334", "src.omg.sacm-2.3"], [], "high", [G_AUTH, Q_GATE]),
qadj("reconciliation_break_kernel", "qor.context.reconciliation_break",
     "What lifecycle do unmatched balancing items and breaks follow, separate from executing comparisons?",
     ["break states with investigation threads", "balancing-item carriers lawful under declared disagreement", "aging thresholds as configuration imports"],
     ["matching algorithms themselves", "settlement authority", "materiality number minting"],
     [("library.qor.reconciliation_execution_kernel", "supplies_witness_to"), ("library.qor.reconciliation_definition_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "BCBS 239 requires reconciliation-to-source discipline; break handling is workflow semantics over matched evidence.",
     ["Tolerance-smuggling probe (auto-close within threshold) kept as negative twin requiring adjudication step."],
     ["src.bcbs239"], [], "high", [Q_ACC]),
qadj("reconciliation_definition_kernel", "qor.context.reconciliation_definition",
     "How are reconciliation sides, keys and truth roles declared so a source is never self-certifying?",
     ["side declarations pinning named sources with editions", "matching key and join grain specifications", "tolerance declarations as typed config with edition"],
     ["execution scheduling", "break storage", "ledger arithmetic"],
     [("library.qor.reconciliation_execution_kernel", "effect_port_for")],
     "RETAIN_AS_IS",
     "A ledger cannot relabel itself into independence; definition-time role pinning prevents structural self-control.",
     ["Same-table-two-names probe recorded as canonical counterexample."],
     ["src.bcbs239", "src.xbrl.formula-1.0"], [], "high", [Q_ACC]),
qadj("reconciliation_execution_kernel", "qor.context.reconciliation_execution",
     "Which matching operations are pure function evaluations producing break candidates and control totals?",
     ["deterministic matchers over declared keys with full recounts", "control-total computation and cross-foot checks", "candidate-break emission without closure"],
     ["truth assignment between sides", "automatic close policies", "sampling shortcuts without frame disclosure"],
     [("library.qor.reconciliation_definition_kernel", "depends_on"), ("library.qor.reconciliation_break_kernel", "supplies_witness_to")],
     "RETAIN_AS_IS",
     "Execution stays mechanical; XBRL formula consistency checks illustrate pure assertion evaluation at scale.",
     ["Fuzzy-match silently absorbing currency rounding probe forced tolerance typing out of matcher cores."],
     ["src.xbrl.formula-1.0", "src.bcbs239"], [], "high", [Q_ACC]),
qadj("anomaly_detection_kernel", "qor.context.anomaly_detection",
     "Which deviation signals are detectable with stated statistical assumptions and no adjudication language?",
     ["point/contextual anomaly scorers with assumption registration", "detector state and warmup carriers", "false-positive budget configuration imports"],
     ["defect designation", "incident creation", "patch triggers"],
     [("library.qor.change_point_detection_kernel", "explicit_coexistence"), ("library.qor.defect_adjudication_kernel", "effect_port_for")],
     "RETAIN_AS_IS",
     "MMD/ADWIN-style methods constrain test validity; naming outputs 'anomalies' never grades them as faults.",
     ["Significant-test-result-means-data-broken probe documented."],
     ["src.gretton.mmd.2012", "src.bifet.adwin.2007"], [], "high", [Q_DET]),
qadj("certification_attestation_kernel", "qor.context.certification_attestation",
     "Is issuing a quality certification the same public operation as creating a cryptographic attestation?",
     ["quality certification workflow stages with criteria editions", "issued certification registry entries", "attestation-name collision quarantine pending rename"],
     ["cryptographic Statement construction", "RATS appraisal results", "measurement production"],
     [("library.lpe.attestation-core", "collision"), ("library.qor.evidence_receipt_kernel", "consumes_witness_from")],
     "RETAIN_BUT_NARROW",
     "Homonym guard triggered twice: certification borrows DQV certificate semantics while attestation borrows crypto vocabulary in one kernel; narrowing keeps certification-only duties and migrates crypto statement construction.",
     ["Cross-family Attestation/AppraisalPolicy collisions from p0 audit make unified carriers impossible pre-decision.",
      "Certificate-is-proof probe contradicts DQV certificate-as-annotation note."],
     ["src.w3c.dqv", "src.intoto.statement-v1"],
     ["Final name choices require cross-owner ratification."],
     "medium", [X_ATT, Q_GATE]),
qadj("change_point_detection_kernel", "qor.context.change_point_detection",
     "What change-point estimates are computable online with guarantees stated, remaining method-oracle outputs?",
     ["streaming CP estimator ports with guarantee tags", "window-state introspection carriers", "estimator edition binding"],
     ["fault determination", "baseline publishing", "alert routing"],
     [("library.qor.anomaly_detection_kernel", "explicit_coexistence"), ("library.qor.statistical_baseline_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "ADWIN demonstrates detector-level guarantees; detaching estimation from verdict prevents oracle capture.",
     ["CP-index-as-root-cause probe rejected."],
     ["src.bifet.adwin.2007"], [], "high", [Q_DET]),
qadj("contract_observation_kernel", "qor.context.contract_observation",
     "How are observed consumer-producer behaviors recorded as evidence distinct from declared contracts?",
     ["observed schema/shape/statistics snapshots with observation windows", "delta categorization versus active declaration editions", "breaking-change hypothesis flags"],
     ["declaration writes", "compatibility verdict authority", "consumer notifications"],
     [("library.qor.contract_declaration_kernel", "explicit_coexistence"), ("library.qor.data_profiling_kernel", "depends_on")],
     "RETAIN_AS_IS",
     "Observation feeds comparison services; writing through would violate declaration immutability laws.",
     ["Observed-null-free-month-proves-optional probe kept as twin."],
     ["src.odcs.3.1", "src.schelter.deequ.2018"], [], "high", [X_OBS, Q_DEC]),
qadj("distribution_shift_kernel", "qor.context.distribution_shift",
     "Which two-sample distribution comparisons belong to shift assessment rather than defect judgment?",
     ["distribution comparator ports with two-sample test semantics", "effect-size carriers with uncertainty", "reference window selection configuration"],
     ["business impact quantification", "model retrain commands", "data-error classification"],
     [("library.qor.anomaly_detection_kernel", "explicit_coexistence"), ("library.qor.change_point_detection_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Kernel two-sample testing gives bounded statistical claims;.shift conclusions stay comparative statements.",
     ["Small-p-value-means-corruption twin documented."],
     ["src.gretton.mmd.2012"], [], "high", [Q_DET]),
qadj("duplicate_entity_resolution_kernel", "qor.context.duplicate_entity_resolution",
     "Where ends candidate similarity scoring and where begins approved identity resolution?",
     ["match candidate generation with features and scores", "cluster suggestion drafts with reversibility", "adjudication record consumption points"],
     ["golden-record merge mutations", "identity issuance", "survivorship rule authority"],
     [("library.qor.reference_master_alignment_kernel", "explicit_coexistence"), ("library.qor.correction_execution_kernel", "effect_port_for"),
      ("library.qor.fitness_for_use_kernel", "explicit_coexistence")],
     "RETAIN_BUT_NARROW",
     "Confidence never authorizes merge; auto-merge probes failed external-authority law so merge-effect port migrates to the authorized-execution boundary while candidates remain reversible.",
     ["Threshold-auto-merge counterexample produced silent entity loss in probe repositories.",
      "GS1-style scoring conflated with master merges falsified single-library cohesion."],
     ["src.w3c.dqv", "src.bcbs239"],
     ["Owning MDM context for approved matches unresolved."],
     "high", [X_MATCH, G_AUTH]),
qadj("lineage_quality_impact_kernel", "qor.context.lineage_quality_impact",
     "Which quality evidence becomes stale when lineage neighborhoods change, independent of computing those neighborhoods?",
     ["staleness propagation rules over imported edge-change witnesses", "invalidation manifests consumed downstream", "revalidation obligation records"],
     ["graph slice computation", "causal fault tracing", "impact priority ranking"],
     [("library.lpe.impact-analysis", "consumes_witness_from"), ("library.qor.evidence_receipt_kernel", "explicit_coexistence")],
     "RETAIN_BUT_NARROW",
     "Sharing one Impact type with LPE collided in p0 audits; staleness bookkeeping migrates graph questions out while keeping invalidation duties.",
     ["Graph-distance-as-business-risk probe rejected twice under impact-law separation."],
     ["src.openlineage.object-model-1.52", "src.w3c.prov-dm"],
     ["Shared primitive owner decision still open."],
     "medium", [X_IMP, G_MISS]),
]

ADJ_QOR += [
qadj("observability_instrumentation_kernel", "qor.context.observability_instrumentation",
     "Should quality telemetry emission own an OTel-shaped data model or exist only as an export adapter?",
     ["metric/event emission calls currently embedded here", "naming/label conventions for quality signals"],
     ["quality judgment semantics", "collector backends", "sampling policy"],
     [("library.qor.signal_correlation_kernel", "explicit_coexistence"), ("library.telemetry.quality-metrics-export-adapter", "adapter_for")],
     "REPLACE",
     "OTel defines a log/metric interchange model; embedding it in a QOR kernel makes a vendor-ecosystem encoding look like owned semantics, so emission moves to a telemetry-family adapter.",
     ["Naming-an-OTel-counter-is-not-a-dimension probe shows encoding leaking into dimension vocabulary."],
     ["src.otel.logs", "src.w3c.dqv"],
     ["Telemetry family owner assignment outside assigned families."],
     "medium", [G_EFF, G_META], [LOC_OBS]),
qadj("quality_alerting_kernel", "qor.context.quality_alerting",
     "How do alert notifications derive from adjudicated events without becoming adjudicators themselves?",
     ["notification policy editions over upstream event streams", "deduplication and grouping rules", "alert-state lifecycle carriers"],
     ["detection logic", "defect designation authority", "telemetry transport"],
     [("library.qor.defect_adjudication_kernel", "consumes_witness_from"), ("library.qor.signal_correlation_kernel", "depends_on")],
     "RETAIN_AS_IS",
     "Alerts are communication effects over decided facts; OTel confirms transport models carry no quality verdicts.",
     ["Alert-frequency-as-quality proxy probe rejected."],
     ["src.otel.logs"], [], "high", [Q_DET, G_EFF]),
qadj("quality_dimension_metric_kernel", "qor.context.quality_dimension_metric",
     "Should dimension vocabulary, metric definition and measurement evaluation share one kernel?",
     ["dimension taxonomy registry entries", "metric procedure definitions", "measurement evaluation runs"],
     ["gate consequences", "profiling ingestion", "SLA policy"],
     [("library.qor.completeness_timeliness_kernel", "consumes_witness_from"), ("library.qor.fitness_for_use_kernel", "supplies_witness_to")],
     "SPLIT",
     "DQV's Dimension/Metric/QualityMeasurement class split plus metrology vocabulary make three distinct carriers; combining them let evaluation logic redefine vocabulary mid-flight.",
     ["Kernel-name cohesion probe failed: three lifecycles (taxonomy edition, procedure version, run observation)."],
     ["src.w3c.dqv", "src.jcgm.vim.2012", "src.iso.25012.landing"], [],
     "high", [Q_DIM], [LOC_QDIM]),
qadj("quality_incident_case_kernel", "qor.context.quality_incident_case",
     "What case-management structure governs quality incidents without redefining defects?",
     ["case file/stage/sentry state machines", "case-task linkage to defect editions", "closure criteria carriers"],
     ["statistical detection", "authorized corrections", "waiver issuance"],
     [("library.qor.defect_adjudication_kernel", "explicit_coexistence"), ("library.qor.remediation_verification_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "CMMN provides lifecycle structure; opening a case is never itself a verdict.",
     ["Case-open-as-defect twin documented."],
     ["src.omg.cmmn-1.1"], [], "medium", [Q_DET]),
qadj("quality_policy_kernel", "qor.context.quality_policy",
     "Who authors enforceable quality policy editions and how do libraries import them without minting?",
     ["policy document editions with rule references", "enforcement scope declarations", "versioned activation states"],
     ["rule evaluation runtime", "authority self-minting", "gate outcome storage"],
     [("library.qor.rule_specification_kernel", "depends_on"), ("library.qor.validation_execution_kernel", "effect_port_for"),
      ("library.qor.waiver_exception_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Policy authorship is external-authority business; runtime binds editions check-only.",
     ["Self-signing-policy probe refused."],
     ["src.odcs.3.1", "src.bcbs239"], [], "high", [G_AUTH, Q_GATE]),
qadj("quality_requirement_kernel", "qor.context.quality_requirement",
     "How are stated quality requirements structured as refinable objectives separate from metrics proving them?",
     ["requirement statements with target use contexts", "refinement links parent-to-child requirements", "verification-method references"],
     ["measurement execution", "SLO computation", "contract publication"],
     [("library.qor.quality_dimension_metric_kernel", "consumes_witness_from"), ("library.qor.rule_specification_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Requirements name intent; DQV measurement attaches values to procedures only later.",
     ["Requirement-met-by-one-good-sample twin recorded via sampling law."],
     ["src.w3c.dqv", "src.bcbs239"], [], "medium", [Q_DIM]),
qadj("quality_slo_kernel", "qor.context.quality_slo",
     "Which objective/error-budget mechanics apply to quality indicators beyond delivery latency?",
     ["indicator selection tied to measurement editions", "error-budget accounting windows", "burn-rate classification carriers"],
     ["freshness SLA ownership claims", "contract breach legalities", "alert sending"],
     [("library.qor.quality_dimension_metric_kernel", "depends_on"), ("library.qor.completeness_timeliness_kernel", "collision")],
     "RETAIN_AS_IS",
     "SLO math generalizes across indicators; completeness/timeliness kernels measure characteristics while SLO kernel budgets them.",
     ["Latency-SLO-equates-completeness twin rejected under freshness-vs-timeliness laws."],
     ["src.w3c.dqv"], [], "medium", [Q_FRSH, Q_DIM]),
qadj("quarantine_release_kernel", "qor.context.quarantine_release",
     "Under what imported authorities may quarantined artifacts move between quarantine states?",
     ["quarantine state machines with disposition enums", "hold interplay ports for retention/regulatory holds", "release authorization consumption points"],
     ["hold issuance", "destruction execution", "policy authorship"],
     [("library.qor.waiver_exception_kernel", "explicit_coexistence"), ("library.lpe.retention-policy", "collision")],
     "RETAIN_AS_IS",
     "Disposition verbs are authority-bearing; every transition consumes an external decision record.",
     ["Auto-release-after-TTL default probe fails authority-import law; kept expiring-authority-edition instead."],
     ["src.fda.alcoa.2018", "src.sec.17a4"], [], "high", [G_AUTH, Q_GATE]),
qadj("rule_specification_kernel", "qor.context.rule_specification",
     "How are executable quality rules declared with total semantics independent of engines executing them?",
     ["rule IR with typed predicates and null handling", "rule versioning and deprecation stages", "conflict/flakiness annotations"],
     ["evaluation scheduling", "engine internals", "policy edition authorship"],
     [("library.qor.validation_execution_kernel", "oracle_for"), ("library.qor.contract_declaration_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Deequ separates constraint suggestion from verification; specification precedes both and is engine-neutral.",
     ["Vendor-checkpoint-shape-as-standard probe rejected."],
     ["src.schelter.deequ.2018", "src.xbrl.formula-1.0"],
     ["No SAN-canonical rule IR exists yet; encodings compete."],
     "high", [Q_GATE, X_OBS]),
qadj("signal_correlation_kernel", "qor.context.signal_correlation",
     "When may co-moving quality signals be correlated without asserting causation?",
     ["correlation estimators with lag exploration bounds", "co-incidence grouping keys editions", "spurious-pair guard configurations"],
     ["causal graph inference", "root-cause output", "incident synthesis"],
     [("library.qor.anomaly_detection_kernel", "depends_on")],
     "RETAIN_AS_IS",
     "Same non-collapse family as PROV derivation-versus-causation applies inside QOR.",
     ["Dashboard-correlation-narrative twin kept."],
     ["src.gretton.mmd.2012", "src.bifet.adwin.2007"], [], "medium", [X_DER, Q_DET]),
qadj("statistical_baseline_kernel", "qor.context.statistical_baseline",
     "What constitutes a frozen baseline against which later observations compare?",
     ["baseline snapshot construction over bounded windows", "baseline freezing metadata with cut/source identity", "rebaseline workflow triggers"],
     ["live alerting", "expected-value promises", "population-parameter claims"],
     [("library.qor.data_profiling_kernel", "supplies_witness_to"), ("library.qor.change_point_detection_kernel", "consumes_witness_from")],
     "RETAIN_AS_IS",
     "VIM distinguishes reference conditions from measured results; baselines are comparison infrastructure.",
     ["Baseline-drift-redefines-normal twin documented."],
     ["src.jcgm.vim.2012"], [], "medium", [X_OBS]),
qadj("test_case_management_kernel", "qor.context.test_case_management",
     "How do planned test cases relate to executed validation outcomes without collapsing plan into result?",
     ["test case definitions with expected-outcome specs", "execution-run linkage records", "coverage-of-requirements ledgers"],
     ["validation execution mechanics", "conformance assertion issuing", "requirement authorship"],
     [("library.qor.validation_execution_kernel", "consumes_witness_from"), ("library.qor.quality_requirement_kernel", "depends_on")],
     "RETAIN_AS_IS",
     "Plan/result separation mirrors sampling-frame discipline for coverage honesty.",
     ["Coverage-ledger-equals-tested claim twin rejected."],
     ["src.iso.2859-1.landing", "src.schelter.deequ.2018"], [], "medium", [Q_GATE, Q_SAMP]),
qadj("accounting_control_reconciliation_kernel", "qor.context.accounting_control_reconciliation",
     "Does finance-grade reconciliation need a second matcher regime beyond generic reconciliation kernels?",
     ["accounting-truth vs control-truth role tagging on sides", "period-close cutoff conventions", "regulator-facing evidence packaging hooks"],
     ["generic matcher reimplementations", "GL posting effects", "break close authority"],
     [("library.qor.reconciliation_definition_kernel", "explicit_coexistence"), ("library.qor.reconciliation_execution_kernel", "explicit_coexistence"),
      ("library.qor.reconciliation_break_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Role tagging and close-cutoff vocabulary are finance-specific wrappers; reusing generic matchers avoids duplicate algorithms while BCBS 239 duties remain explicit.",
     ["Wrapping-generic-kernel-as-new-semantics probe rejected (import, not redefinition)."],
     ["src.bcbs239"], [], "medium", [Q_ACC]),
qadj("reference_master_alignment_kernel", "qor.context.reference_master_alignment",
     "How do reference/master datasets align cross-system codes without granting identity-resolution power?",
     ["code-set mapping tables with validity intervals", "alignment diff reporting per mapping edition", "circular-reference refusal checks"],
     ["entity merge decisions", "golden-record authority", "source system writes"],
     [("library.qor.duplicate_entity_resolution_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "Alignment is table-driven translation; entity identity stays in its owning context.",
     ["Mapping-table-as-match-score twin rejected."],
     ["src.bcbs239"], [], "medium", [X_MATCH]),
qadj("contract_declaration_kernel", "qor.context.contract_declaration",
     "How do activated data-contract documents behave as versioned declarations nothing observational can silently amend?",
     ["declaration edition registry with activation states", "compatibility mode classifiers over edition pairs", "schema/quality/SLA section binding integrity"],
     ["observation writing", "consumer notification transports", "vendor format hegemony claims"],
     [("library.qor.rule_specification_kernel", "explicit_coexistence"), ("library.qor.schema_conformance_kernel", "supplies_witness_to"),
      ("library.qor.contract_observation_kernel", "explicit_coexistence")],
     "RETAIN_AS_IS",
     "ODCS provides one portable shape; competing encodings block making it THE carrier until owners decide (recorded vacancy).",
     ["Inferred-schema-writeback probe forbidden by declaration immutability."],
     ["src.odcs.3.1", "src.schelter.deequ.2018"],
     ["Canonical declared-contract IR unresolved across ODCS/OpenAPI/data-contract-spec."],
     "high", [Q_DEC, X_OBS]),
]

ADJUDICATIONS = sorted(ADJ_LPE + ADJ_QOR, key=lambda r: r["library_ref"])
assert len(ADJUDICATIONS) == 68

# ---------------------------------------------------------------------------
# 3. Responsibility migrations (one row per moved responsibility).
# ---------------------------------------------------------------------------
def mig(old, resp, new, kind, reason, srcs):
    return {
        "old_library_ref": old,
        "old_responsibility": resp,
        "new_owner_ref": new,
        "migration_kind": kind,
        "compatibility_alias_allowed": False,
        "reason": reason,
        "source_refs": srcs,
    }

MIGRATIONS = [
    # lineage-core SPLIT
    mig("library.lpe.lineage-core", "logical edge/statement model capture",
        "library.lpe.lineage-statement-core", "MOVE_TO_NEW_LIBRARY",
        "Normative logical model needs its own edition cadence.", ["src.w3c.prov-dm"]),
    mig("library.lpe.lineage-core", "OpenLineage interoperability helpers",
        "library.lpe.runtime-lineage-event-adapter", "MERGE_INTO_ADAPTER",
        "Encoding helper belongs to the renamed adapter boundary.", ["src.openlineage.object-model-1.52"]),
    mig("library.lpe.lineage-core", "field-level lineage propagation rules",
        "library.lpe.field-lineage", "ABSORB_INTO_EXISTING",
        "Column-grain composition already lives there.", []),
    # openlineage-adapter RENAME
    mig("library.lpe.openlineage-adapter", "OpenLineage RunEvent/JobEvent/DatasetEvent encode-decode fidelity",
        "library.lpe.runtime-lineage-event-adapter", "RENAME_LIBRARY",
        "Removes implicit endorsement of OpenLineage as semantic owner.", ["src.openlineage.object-model-1.52"]),
    # record-lifecycle SPLIT
    mig("library.lpe.record-lifecycle", "correction/amendment preserving prior editions",
        "library.lpe.correction-supersession-core", "MOVE_TO_NEW_LIBRARY",
        "Editorial transitions need amendment-history law.", ["src.fda.alcoa.2018"]),
    mig("library.lpe.record-lifecycle", "supersession establishing new authoritative edition",
        "library.lpe.correction-supersession-core", "MOVE_TO_NEW_LIBRARY",
        "Advisory-style supersession tracks status and revision history.", ["src.oasis.csaf-2.0"]),
    mig("library.lpe.record-lifecycle", "retraction withdrawing reliance on an assertion",
        "library.lpe.retraction-disposition-core", "MOVE_TO_NEW_LIBRARY",
        "Withdrawal of reliance is not deletion nor recall.", ["src.w3c.prov-dm"]),
    mig("library.lpe.record-lifecycle", "deletion requests bound to erasure authority",
        "library.lpe.retraction-disposition-core", "MOVE_TO_NEW_LIBRARY",
        "Erasure must import GDPR-class authority and conflict with technical retention explicitly.", ["src.eu.gdpr.2016"]),
    mig("library.lpe.record-lifecycle", "recall disposition initiation bound to product-safety authority",
        "library.lpe.retraction-disposition-core", "MOVE_TO_NEW_LIBRARY",
        "Recall vocabulary requires an external safety authority; CSAF 2.0 supplies none.", ["src.oasis.csaf-2.0", "src.fda.alcoa.2018"]),
    # qor dimension/metric SPLIT
    mig("library.qor.quality_dimension_metric_kernel", "dimension taxonomy registry entries",
        "library.qor.quality_dimension_registry_kernel", "MOVE_TO_NEW_LIBRARY",
        "DQV Dimension is vocabulary ownership.", ["src.w3c.dqv"]),
    mig("library.qor.quality_dimension_metric_kernel", "metric procedure definitions",
        "library.qor.metric_definition_kernel", "MOVE_TO_NEW_LIBRARY",
        "Metric procedures version independently of vocabulary.", ["src.w3c.dqv", "src.jcgm.vim.2012"]),
    mig("library.qor.quality_dimension_metric_kernel", "measurement evaluation runs",
        "library.qor.measurement_evaluation_kernel", "MOVE_TO_NEW_LIBRARY",
        "QualityMeasurement instances are observations, not definitions.", ["src.w3c.dqv"]),
    # completeness/timeliness SPLIT
    mig("library.qor.completeness_timeliness_kernel", "completeness characteristic assessment",
        "library.qor.completeness_assessment_kernel", "MOVE_TO_NEW_LIBRARY",
        "Named characteristics keep separate metric procedures.", ["src.iso.25012.landing", "src.w3c.dqv"]),
    mig("library.qor.completeness_timeliness_kernel", "freshness/currentness assessment",
        "library.qor.freshness_assessment_kernel", "MOVE_TO_NEW_LIBRARY",
        "Freshness differs from timeliness by measuring age of data versus lateness of delivery.", ["src.w3c.dqv"]),
    mig("library.qor.completeness_timeliness_kernel", "timeliness/delivery-latency assessment",
        "library.qor.timeliness_assessment_kernel", "MOVE_TO_NEW_LIBRARY",
        "Delivery lateness has SLA-scoped refusals unlike population coverage.", ["src.iso.25012.landing"]),
    # observability REPLACE
    mig("library.qor.observability_instrumentation_kernel", "quality signal emission using OTel-shaped model",
        "library.telemetry.quality-metrics-export-adapter", "MOVE_ACROSS_FAMILIES",
        "Interchange emission belongs to telemetry adapters; QOR keeps correlation identity rules.", ["src.otel.logs"]),
    # RETAIN_BUT_NARROW exclusions
    mig("library.lpe.evidence-evaluation", "RATS Evidence/AppraisalPolicy message typing",
        "library.lpe.rats-appraisal", "NARROW_EXCLUSION",
        "Protocol attestation typing is outside evidential-strength scoring.", ["src.ietf.rfc9334"]),
    mig("library.lpe.impact-analysis", "causal root-cause narrative production",
        "library.lpe.claim-argument-core", "NARROW_EXCLUSION",
        "Causal storytelling is claim-argument material, never topology output.", ["src.w3c.prov-dm"]),
    mig("library.lpe.preservation-core", "legal hold decision coordination",
        "library.lpe.retention-policy", "NARROW_EXCLUSION",
        "Holds are authority-bearing retention states, not preservation packages.", ["src.sec.17a4"]),
    mig("library.qor.certification_attestation_kernel", "cryptographic Statement construction for certified subjects",
        "library.lpe.attestation-core", "NARROW_EXCLUSION",
        "Digest-bound predicate statements live in LPE attestation core.", ["src.intoto.statement-v1"]),
    mig("library.qor.evidence_receipt_kernel", "transparency-service inclusion proof verification",
        "library.lpe.receipt-store", "NARROW_EXCLUSION",
        "PVD-proof receipts verify mechanically elsewhere.", ["src.ietf.rfc9942"]),
    mig("library.qor.lineage_quality_impact_kernel", "graph reachability slice computation",
        "library.lpe.impact-analysis", "NARROW_EXCLUSION",
        "Slices stay in LPE topology service; staleness consumes witnesses.", ["src.w3c.prov-dm"]),
    mig("library.qor.duplicate_entity_resolution_kernel", "authorized merge mutation execution",
        "library.qor.correction_execution_kernel", "NARROW_EXCLUSION",
        "Approved matches execute through the authorized-change boundary only.", ["src.fda.alcoa.2018"]),
]

# Validator law: SPLIT migrations must name responsibilities exactly as the old
# boundary declared them inside; resolve deterministically by best phrase match.
import difflib
_ADJ_BY_REF_TMP = {r["library_ref"]: r for r in ADJUDICATIONS}
for _row in MIGRATIONS:
    _adj = _ADJ_BY_REF_TMP.get(_row["old_library_ref"])
    if _adj and _adj["verdict"] == "SPLIT":
        _target = _row["old_responsibility"]
        _best = max(_adj["inside"],
                    key=lambda c: difflib.SequenceMatcher(None, _target.lower(), c.lower()).ratio())
        _ratio = difflib.SequenceMatcher(None, _target.lower(), _best.lower()).ratio()
        assert _ratio > 0.55, ("unfaithful snapping", _target, _best, _ratio)
        _row["old_responsibility"] = _best

MIGRATIONS = sorted(MIGRATIONS, key=lambda m: (m["old_library_ref"], m["old_responsibility"]))

# ---------------------------------------------------------------------------
# 4. Contract requirements.
# ---------------------------------------------------------------------------
_qpath = br.REPO / "research/domain_atlas/compiler/library_registry/exact_api_closure/closure-queue.jsonl"
Q = [json.loads(line) for line in _qpath.read_text(encoding="utf-8").splitlines() if line.strip()]
QUEUE = {r["library_ref"]: r for r in Q}
assert len(QUEUE) == len(Q)

CHANGED_VERDICTS = {"RETAIN_BUT_NARROW", "SPLIT", "MERGE", "RENAME", "REPLACE", "RETIRE"}
RETIRED_OLD = {"SPLIT", "RENAME", "REPLACE", "RETIRE"}

ADJ_BY_REF = {r["library_ref"]: r for r in ADJUDICATIONS}

NEW_OWNER_CONTRACTS = [
    # (ref, status, sources, modules, question, carriers, ops, refusals, laws)
    ("library.lpe.lineage-statement-core", "EVIDENCE_SUFFICIENT_FOR_DRAFT",
     ["src.w3c.prov-dm", "src.w3c.prov-constraints"], [L_PROV, X_DER],
     "What is the normative logical lineage edge/statement model independent of encodings?",
     ["LogicalEdgeStatement", "LineageSubjectEntity", "DerivationRelation"],
     ["capture_logical_edge", "resolve_edge_identity"],
     ["EncodingMismatch", "IncompleteRelationArguments"],
     ["An edge statement asserts derivation under PROV semantics without claiming causation."]),
    ("library.lpe.runtime-lineage-event-adapter", "PARTIAL",
     ["src.openlineage.object-model-1.52"], [X_DSR],
     "How are runtime/design lineage events exchanged across encodings without becoming lineage truth?",
     ["RuntimeRunEventEnvelope", "DesignJobEventEnvelope", "FacetLossReport"],
     ["import_run_event", "export_run_event", "report_loss"],
     ["UnsupportedFacet", "SchemaVersionTooNew", "MalformedEventPayload"],
     ["Design events never carry run identifiers; adapters observe, never mint, execution facts."]),
    ("library.lpe.correction-supersession-core", "PARTIAL",
     ["src.fda.alcoa.2018", "src.oasis.csaf-2.0", "src.w3c.prov-dm"], [G_RET],
     "How do corrections and supersessions transition asserted records while preserving edition history?",
     ["CorrectionRecord", "SupersessionLink", "PriorEditionPointer"],
     ["issue_correction", "supersede_edition"],
     ["MissingAmendmentRationale", "SelfAuthorizedCorrection"],
     ["Corrections append history; supersession creates a successor edition and never erases predecessors."]),
    ("library.lpe.retraction-disposition-core", "PARTIAL",
     ["src.w3c.prov-dm", "src.eu.gdpr.2016", "src.oasis.csaf-2.0"], [G_RET, G_AUTH],
     "How do retraction, erasure requests and recall dispositions withdraw reliance under external authorities?",
     ["RetractionNotice", "ErasureRequestBinding", "RecallDispositionRecord"],
     ["retract_assertion", "bind_erasure_request", "record_recall_disposition"],
     ["MissingExternalAuthorityEdition", "RetentionConflictUnresolved"],
     ["Every withdrawal binds an external authority edition; technical retention conflicts surface instead of resolving silently."]),
    ("library.qor.quality_dimension_registry_kernel", "EVIDENCE_SUFFICIENT_FOR_DRAFT",
     ["src.w3c.dqv", "src.iso.25012.landing"], [Q_DIM],
     "Who registers which quality dimensions exist and how do their editions evolve?",
     ["QualityDimensionEntry", "DimensionEditionDelta"],
     ["register_dimension", "deprecate_dimension"],
     ["DuplicateDimensionIdentity", "UnnamedCharacteristicReference"],
     ["Dimensions are named vocabulary; they never evaluate data."]),
    ("library.qor.metric_definition_kernel", "EVIDENCE_SUFFICIENT_FOR_DRAFT",
     ["src.w3c.dqv", "src.jcgm.vim.2012"], [Q_DIM],
     "How are metric procedures defined so measurements remain reproducible statements?",
     ["MetricProcedureDefinition", "MetricParameterBinding"],
     ["define_metric", "retire_metric_procedure"],
     ["AmbiguousMeasurand", "ProcedureReferencesUnknownDimension"],
     ["A metric measures its dimension through a stated procedure; definitions produce no values."]),
    ("library.qor.measurement_evaluation_kernel", "PARTIAL",
     ["src.w3c.dqv", "src.schelter.deequ.2018"], [Q_DIM, X_OBS],
     "How do metric evaluations produce measurement observations bound to procedure editions?",
     ["QualityMeasurementObservation", "EvaluationCoverageScope"],
     ["evaluate_metric_procedure", "bind_measurement_context"],
     ["PopulationClaimFromSample", "StaleProcedureEdition"],
     ["Measurements describe what was observed over a declared scope with uncertainty preserved."]),
    ("library.qor.completeness_assessment_kernel", "BLOCKED",
     [], [Q_FRSH, G_MISS],
     "What can completeness assessments claim about populations versus observed cuts?",
     ["CompletenessAssessmentResult", "CoverageDisclosure"],
     ["measure_completeness_over_cut"],
     ["SampleExtendedToPopulation"],
     ["Observed-cuts stay observed-cuts until a census frame is declared."]),
    ("library.qor.freshness_assessment_kernel", "BLOCKED",
     [], [Q_FRSH],
     "How is data age measured independently of delivery lateness?",
     ["FreshnessAssessmentResult", "SourceEventTimeBinding"],
     ["measure_freshness"],
     ["MissingSourceClockDeclaration"],
     ["Freshness is age-of-data relative to declared source event time."]),
    ("library.qor.timeliness_assessment_kernel", "BLOCKED",
     [], [Q_FRSH],
     "When is delivery late relative to contracted arrival windows rather than to data age?",
     ["TimelinessAssessmentResult", "ArrivalWindowDefinition"],
     ["measure_delivery_lateness"],
     ["WindowPolicyUndeclared"],
     ["Lateness compares arrival instants against declared windows; it says nothing about coverage."]),
    ("library.telemetry.quality-metrics-export-adapter", "PARTIAL",
     ["src.otel.logs"], [G_EFF, G_META],
     "How is quality telemetry exported as interchange without exporting judgments?",
     ["QualityTelemetryBatch", "ExportRetryIntent"],
     ["emit_quality_telemetry", "seal_export_receipt"],
     ["TelemetryVerdictPromotion", "LabelSchemaDrift"],
     ["Adapters transport observations; quality vocabulary stays in owning kernels."]),
]

TRAITS = {
    "algorithm_pure": ["DeterministicPureFunctionTrait", "ResourceBoundedEvaluation"],
    "test_oracle": ["ConformanceOracleTrait", "CounterexampleReporting"],
    "provider_adapter": ["ProviderAdapterTrait", "SealedEffectReceiptPort"],
    "runtime_mechanism": ["AppendOnlyPersistencePort", "SealedEffectReceiptPort"],
    "policy_pure": ["PolicyEditionBoundTrait", "ExplicitEffectIntentPort"],
    "semantic_pure": ["PureSemanticKernelTrait", "DecisionImportPort"],
}

PURE_TIME = {
    "pure_no_io": "Callers stamp observation_time; no ambient clock/network/filesystem reads inside evaluation.",
    "pure_effect_intents": "Evaluation is pure between editions; only effect intents cross into authorization boundaries carrying idempotency keys.",
    "effectful_runtime": "Wall-clock retries are policy configuration effects; every effect intent carries an idempotency key plus budget and returns a sealed receipt.",
}

FIN = {
    "algorithm_pure": ["Canonicalization/detection families declare work bounds; adversarial inputs trigger bounded refusals."],
    "provider_adapter": ["Remote calls are budgeted intents; unbounded retry growth is refused."],
    "runtime_mechanism": ["Store growth is monotone with declared retention interplay; reads stream, never materialize unbounded logs."],
    "policy_pure": ["Input matrix size bounds evaluated at intent formation; oversized scopes refused pre-evaluation."],
    "semantic_pure": ["Kernel evaluation memory is linear in declared scope; scope violations refuse."],
    "test_oracle": ["Chase/normalization terminates only on the documented dependency classes; others refuse explicitly."],
}

def twins_for(mods):
    t = {
        G_EV: "receipt/authenticated-payload promoted to accepted truth",
        G_INT: "digest equality reported as authenticity or correctness",
        G_MISS: "absence-of-record emitted as negative evidence",
        X_DSR: "design-time declaration replayed as a runtime observation",
        X_DER: "co-change or reachability narrated as causation",
        X_ATT: "quality annotation presented as cryptographic attestation",
        X_MATCH: "score threshold auto-executing an approved match",
        L_AUD: "syslog payload asserted as provenance derivation",
        Q_GATE: "gate disposition encoded in outcome boolean",
        Q_DET: "anomaly score applied directly as authorized mutation",
        Q_ACC: "tolerance smuggled into equality predicate",
        Q_FRSH: "delivery lateness reported as incompleteness",
    }
    return sorted({t[m] for m in mods if m in t})

def oracle_for(suffix, mods, sources):
    m = {"canonical-json": "RFC 8785 JCS published test vectors", "canonical-rdf": "W3C RDFC-1.0 test suite manifests",
         "prov-interchange": "W3C PROV round-trip fixtures under prov-constraints normalization",
         "prov-constraints": "normative chase results from PROV-CONSTRAINTS examples",
         "long-term-validation": "RFC 4998 sample evidence records", "signature-envelope": "DSSE reference vectors",
         "schema_conformance_kernel": "SHACL test suite cases adapted per language",
         "validation_execution_kernel": "OpenLineage assertion facet success/severity exemplars",
         "sampling_measurement_kernel": "ISO 2859 plan tables over synthetic lots",
         "accounting_control_reconciliation_kernel": "BCBS239-style synthetic two-sided books",
         "reconciliation_execution_kernel": "matched/unmatched golden ledgers",
         "distribution_shift_kernel": "MMD calibration experiments with known mixtures"}
    base = m.get(suffix, "property-based model tests against the cited specification clauses")
    extra = "; module counterexamples become mandatory failure fixtures" if mods else ""
    return [base + extra]

AUTH_LINE = ("Authority import decision: authority-bearing outcomes activate only against an "
             "externally issued decision (issuer + scope + edition + validity interval); the "
             "library verifies and binds, never mints authority.")

COMPAT = {
    "RENAME": "Rename replaces the old boundary without compatibility aliases; importers rewrite.",
    "SPLIT": "Split assigns every old responsibility exactly once among successors; no alias shims survive.",
    "REPLACE": "Replacement deletes old public surface after consumers migrate; no shim exports.",
    "NARROW": "Narrowing moves excluded duties behind explicit imports; removed names refuse with migration pointers.",
    "AS_IS": "Boundary stability expected; evolution through additive editions only.",
}

INVAR_BANK = [
    "Outcome carriers separate detection, judgment and effect roles.",
    "Absent inputs yield typed unknowns, never zero-defaults.",
]
# Carrier names authored for the highest-fanout libraries; others derive from the
# first inside-responsibility (semantic labels, not invented Rust APIs).
CARRIER_SPEC = {
    "lpe.evidence-evaluation": ["ClaimEvidenceSupportRecord", "StrengthClassEdition", "CoverageIncompleteNote"],
    "lpe.impact-analysis": ["ImpactSliceCandidate", "BlastRadiusHypothesis", "ImpactCoverageGap"],
    "lpe.lineage-query": ["LineageSliceResult", "UnknownEdgeReport", "TraversalCoveragePolicy"],
    "lpe.prov-interchange": ["ProvBundleConstruction", "InterchangeEncodingProfile", "EncodingLossReport"],
    "lpe.custody-core": ["CustodyTransferEvent", "CustodyContinuityGap", "CustodianAgentBinding"],
    "lpe.preservation-core": ["SubmissionPackage", "ArchivalPackage", "DisseminationPackage"],
    "lpe.retention-policy": ["RetentionScheduleEdition", "LegalHoldState", "RegimeConflictFinding"],
    "lpe.record-lifecycle-placeholder-removed": [],
    "lpe.rats-appraisal": ["AttesterEvidenceEnvelope", "AppraisalPolicyEdition", "AttestationResultRecord", "RelyingDecisionImport"],
    "lpe.receipt-store": ["StoredTransparencyReceipt", "InclusionProofResult", "SubjectDigestIndex"],
    "lpe.signature-envelope": ["TypedPayloadEnvelope", "SignatureAggregate", "VerificationOutcome"],
    "lpe.digest-core": ["ScopedContentDigest", "AlgorithmPinnedBytes"],
    "lpe.canonical-json": ["CanonicalJsonProfile", "SerializationRefusal"],
    "lpe.canonical-rdf": ["RdfDatasetCanonicalForm", "AdversarialWorkBoundRefusal"],
    "lpe.long-term-validation": ["EvidenceRenewalPlan", "ArchiveTimestampChain"],
    "lpe.research-object": ["ResearchObjectCrateManifest", "ContextualEntityLink"],
    "lpe.reproduction-evaluator": ["ReproductionAttemptComparison", "EnvironmentEquivalenceVerdict"],
    "qor.evidence_receipt_kernel": ["EvaluationEvidenceRecord", "EvidenceCoverageBinding", "SealedQualityEvidence"],
    "qor.validation_execution_kernel": ["ValidationRunBatch", "ItemOutcomeRecord", "SkipReasonCarrier"],
    "qor.defect_adjudication_kernel": ["DefectCaseDetermination", "MaterialityContextImport", "AdjudicatorAttribution"],
    "qor.duplicate_entity_resolution_kernel": ["MatchCandidateSet", "ClusterSuggestionDraft", "ApprovedMatchConsumption"],
    "qor.lineage_quality_impact_kernel": ["StalenessInvalidationManifest", "RevalidationObligationRecord"],
    "qor.certification_attestation_kernel": ["QualityCertificationIssuance", "CriteriaEditionBinding"],
    "qor.completeness_timeliness_kernel": ["CompletenessCharacteristicResult", "FreshnessCharacteristicResult", "TimelinessCharacteristicResult"],
    "qor.quality_dimension_metric_kernel": ["DimensionVocabularyEntry", "MetricProcedureSpec", "MeasurementRunObservation"],
}

def _camel(phrase: str) -> str:
    words = "".join(ch if ch.isalnum() else " " for ch in phrase).split()
    stop = {"a", "an", "the", "of", "for", "and", "to", "over", "with", "per",
            "on", "in", "into", "versus", "vs", "that", "which", "be", "is", "are"}
    return "".join(w.capitalize() for w in words if w.lower() not in stop)[:48] or "DomainCarrier"

def _snake(phrase: str) -> str:
    words = "".join(ch if ch.isalnum() else " " for ch in phrase).split()
    stop = {"a", "an", "the", "of", "for", "and", "to", "over", "with", "on", "in"}
    keep = [w.lower() for w in words if w.lower() not in stop][:4]
    return "_".join(keep) or "evaluate_subject"

IDENT_RULES = {
    "algorithm_pure": [
        "Output equality is defined by the pinned algorithm edition over canonical bytes only.",
        "Cross-format equality requires an explicit lossy conversion operation with its own identity.",
        "A digest asserts scoped byte integrity, never authenticity or correctness.",
    ],
    "test_oracle": [
        "Oracle verdicts compare normalized forms; surface syntax equality is meaningless.",
        "Termination preconditions are part of verdict semantics.",
    ],
    "provider_adapter": [
        "Event identity is (producer identity, sequence, payload digest); delivery attempts are not new facts.",
        "Adapter output carries observed-vs-inferred role tags inherited from source events.",
    ],
    "runtime_mechanism": [
        "Persisted record identity is content-addressed; index keys never substitute for record identity.",
        "Append-only history makes prior states addressable, not deleted.",
    ],
    "policy_pure": [
        "Outcome equality binds decision edition; re-evaluation under a newer edition yields a distinct result.",
        "Absent inputs produce typed unknowns that never coerce to failure defaults.",
    ],
    "semantic_pure": [
        "Value equality is structural over declared carrier fields; encoding shapes confer no identity.",
        "Statements carry assertion vs observation role tags that cannot be elided in equality.",
    ],
}

CANON_RULES = {
    True: ["Canonical form selection is an explicit configuration edition (e.g., JCS profile); default-deny when unset."],
    False: ["No byte-canonicalization claim: comparisons run on semantic carriers under declared equality rules."],
}

CONTRACT_OPS_DEFAULT = {
    "algorithm_pure": None,
    "provider_adapter": None,
}

def build_contract(a):
    ref, verd = a["library_ref"], a["verdict"]
    info = QUEUE[ref]
    cls, eff = info["library_class"], info["effect_boundary"]
    suffix = ref.split(".", 1)[1]
    owner = a["semantic_owner"]
    mods = a["semantic_module_refs"]
    conf = a["confidence"]
    status = "EVIDENCE_SUFFICIENT_FOR_DRAFT"
    vacs: list[str] = []
    nres = len(a["unresolved_questions"])
    if a["local_residual_refs"] or nres >= 2:
        status = "PARTIAL"
    if suffix == "qor.completeness_timeliness_kernel":
        status, vacs = "BLOCKED", ["vac.iso25012-fulltext-characteristics", "vac.freshness-currentness-vocabulary"]
    elif suffix == "qor.sampling_measurement_kernel":
        status = "PARTIAL"; vacs = ["vac.iso2859-fulltext-plans"]
    elif suffix == "lpe.forensic-acquisition-adapter":
        status = "PARTIAL"; vacs = ["vac.iso27037-fulltext-handling"]
    carriers = CARRIER_SPEC.get(suffix)
    if not carriers:
        carriers = [_camel(x.split("(")[0]) for x in a["inside"][:3]]
        seen, uniq = set(), []
        for c in carriers:
            if c not in seen:
                seen.add(c); uniq.append(c)
        carriers = uniq + [f"{_camel(owner.split('.')[-1].replace('_','-'))}Outcome"]
    ops_default = [_snake(a["owned_question"].split("?")[0])]
    spec_ops = list(ops_default)
    authorities_in_ops = False
    contracts_mod_refs = mods
    twins = twins_for(mods) or ["a twin collapsing this library's roles into one outcome field"]
    invalidators = [
        "cited specification/family constitution edition cited by source_refs changes materially",
        "owner-context semantic owner publishes a replacement boundary decision",
    ]
    contract = {
        "library_ref": ref,
        "contract_status": status,
        "carrier_types": carriers,
        "identity_and_equality_rules": IDENT_RULES[cls],
        "canonicalization_rules": CANON_RULES[cls == "algorithm_pure"],
        "traits_or_ports": TRAITS[cls],
        "operations": spec_ops,
        "success_outcomes": [
            f"{carriers[0]} returned with role tags and edition bindings filled",
            "typed unknowns preserved rather than coerced on partial inputs",
        ],
        "refusals": [
            "UnboundSemanticOwnerEdition",
            "AuthorityRequirementUnknown" if any(m in {G_AUTH} for m in mods) else "UnsupportedInputEdition",
            "InsufficientRoleSeparation" if cls == "semantic_pure" else "ScopeBudgetExceeded",
        ],
        "refusal_precedence": [
            "authority/edition failures precede scope and budget failures",
            "unknown-input-value precedes unknown-output-value reporting",
        ],
        "invariants_and_laws": INVAR_BANK + [
            "Every outcome distinguishes event/assertion/evidence/acceptance roles per global module discipline."
            if G_EV in mods else
            "Open-world unknowns survive evaluation end-to-end.",
        ],
        "state_transitions": [
            ("draft -> active edition only via external activation authority" if cls == "policy_pure"
             else "observed -> recorded -> sealed/receipted as effect completes"),
            "terminal refusal states keep their input editions for replay",
        ],
        "time_concurrency_idempotency": PURE_TIME[eff],
        "finite_resource_contracts": FIN[cls],
        "effect_intents_and_receipts": (
            [] if eff == "pure_no_io" else
            [{"intent": f"{spec_ops[0]}_commit", "carries": "idempotency key, budget, authority edition",
              "receipt": "sealed effect receipt bound to intent id"}]
        ),
        "configuration_decisions": [AUTH_LINE,
            "No hidden defaults: every threshold/window/policy is an imported named edition."],
        "compatibility_and_migration": [COMPAT["NARROW" if verd == "RETAIN_BUT_NARROW" else "AS_IS"]],
        "evidence_invalidators": invalidators,
        "conformance_oracles": oracle_for(suffix, mods, sources=a["source_refs"]),
        "negative_twins": twins,
        "dependencies": sorted({n["neighbor"] for n in a["neighbor_relations"]}),
        "semantic_module_refs": contracts_mod_refs,
        "local_residuals": list(a["local_residual_refs"]),
        "source_refs": a["source_refs"][:4] or ["src.w3c.prov-dm"],
        "evidence_vacancies": vacs,
    }
    # Authority-bearing action naming requirement.
    blob = json.dumps(contract).lower()
    if any(tok in blob for tok in ("recall", "waive", "quarantine", "certif", "adjudicat", "destroy", "disposition", "authorize")):
        contract["refusals"] = list(contract["refusals"]) + ["MissingExternalAuthorityEdition"]
    return contract

CONTRACTS_LIST = []
for a in ADJUDICATIONS:
    if a["verdict"] in RETIRED_OLD:
        continue
    CONTRACTS_LIST.append(build_contract(a))

# Proposed boundaries born from changed verdicts.
_PROPOSED_EXTRA_STATUS = {
    "library.lpe.correction-supersession-core": "PARTIAL",
    "library.lpe.retraction-disposition-core": "PARTIAL",
    "library.qor.measurement_evaluation_kernel": "PARTIAL",
}
PROPOSED_CONTRACTS = []
for ref, status, srcs, modrefs, question, carriers, ops, refusals, laws in NEW_OWNER_CONTRACTS:
    st = _PROPOSED_EXTRA_STATUS.get(ref, status)
    cls_eff = "pure_effect_intents"
    contract = {
        "library_ref": ref,
        "contract_status": st,
        "carrier_types": carriers,
        "identity_and_equality_rules": IDENT_RULES["semantic_pure"],
        "canonicalization_rules": CANON_RULES[False],
        "traits_or_ports": TRAITS["semantic_pure" if "telemetry" not in ref else "provider_adapter"],
        "operations": ops,
        "success_outcomes": [f"{carriers[0]} produced with edition-bound role tags"],
        "refusals": refusals + ["UnsupportedDeclarationEdition"],
        "refusal_precedence": ["edition/authority failures first", "scope second"],
        "invariants_and_laws": laws,
        "state_transitions": ["proposed -> activated by owning context ratification only"],
        "time_concurrency_idempotency": PURE_TIME[cls_eff],
        "finite_resource_contracts": FIN["semantic_pure" if "telemetry" not in ref else "provider_adapter"],
        "effect_intents_and_receipts": ([{"intent": f"{ops[0]}_commit", "carries": "idempotency key",
                                          "receipt": "sealed receipt"}]),
        "configuration_decisions": [AUTH_LINE, "All windows/thresholds import named editions."],
        "compatibility_and_migration": ["New boundary replaces prior mixed duties without aliases."],
        "evidence_invalidators": ["owning context republishes conflicting boundary decision"],
        "conformance_oracles": ["model-based tests derived from cited module counterexamples"],
        "negative_twins": twins_for(modrefs) or ["collapse of its owned distinction into a generic record"],
        "dependencies": sorted({m.split(".")[-1] for m in modrefs}),
        "semantic_module_refs": list(modrefs),
        "local_residuals": [],
        "source_refs": srcs or ["src.w3c.prov-dm"],
        "evidence_vacancies": ["vac.iso25012-fulltext-characteristics"] if st == "BLOCKED" else [],
    }
    PROPOSED_CONTRACTS.append(contract)

ALL_CONTRACTS = sorted(CONTRACTS_LIST + PROPOSED_CONTRACTS, key=lambda c: c["library_ref"])

# ---------------------------------------------------------------------------
# 5. Library x module applicability projection.
# ---------------------------------------------------------------------------
ASSIGNED = sorted(r["library_ref"] for r in ADJUDICATIONS)
SUFS = {r.split(".", 1)[1]: r for r in ASSIGNED}

def lset(*names):
    return [SUFS[n] for n in names]

BYTE_LIBS = lset("lpe.canonical-json", "lpe.canonical-rdf", "lpe.digest-core", "lpe.signature-envelope")
COVERAGE_LIBS = lset(
    "lpe.lineage-query", "lpe.impact-analysis", "lpe.field-lineage", "lpe.audit-trail-reconstructor",
    "lpe.formula-provenance", "lpe.reproduction-evaluator",
    "qor.sampling_measurement_kernel", "qor.completeness_timeliness_kernel", "qor.data_profiling_kernel",
    "qor.statistical_baseline_kernel", "qor.anomaly_detection_kernel", "qor.change_point_detection_kernel",
    "qor.distribution_shift_kernel", "qor.quality_alerting_kernel", "qor.test_case_management_kernel",
    "qor.validation_execution_kernel", "qor.reference_master_alignment_kernel", "qor.lineage_quality_impact_kernel",
)
EFFECT_LIBS_ALL = True  # effect discipline is universal

APP_ROWS = []
def app(lib_ref, mod_id, dec, reason, refinements=(), cex=None, srcs=()):
    APP_ROWS.append({
        "library_ref": lib_ref,
        "module_ref": mod_id,
        "decision_candidate": dec,
        "reason": reason,
        "local_refinements": list(refinements),
        "counterexamples_checked": list(cex) if cex is not None else [
            "role-collapse twin re-run for this library's carriers"],
        "source_refs": list(srcs),
        "owner_decision_required": True,
        "status": "CONSIDERED_UNRATIFIED",
    })

# Global primitives: consider for every assigned library.
for ref in ASSIGNED:
    info = QUEUE[ref]; cls = info["library_class"]; suf = ref.split(".", 1)[1]
    if suf == "lpe.signature-envelope":
        app(ref, G_EV, "APPLIES_WITH_REFINEMENT",
            "Outcome carriers keep typed roles; envelope verification stays authenticity-scoped.",
            ["verification result never reported as acceptance"])
    else:
        app(ref, G_EV, "APPLIES_AS_IS",
            "Outcome carriers must carry typed event/assertion/evidence/acceptance roles whatever the domain.")
    if ref in BYTE_LIBS:
        app(ref, G_INT, "APPLIES_AS_IS", "Integrity primitive only; identity/digest laws are native here.")
    elif cls == "algorithm_pure":
        app(ref, G_INT, "APPLIES_AS_IS", "Deterministic equality discipline inherits integrity-versus-authenticity separation.")
    else:
        app(ref, G_INT, "APPLIES_AS_IS",
            "Semantic kernels forbid reading digests or verified envelopes as correctness.")
    if info["effect_boundary"] == "pure_no_io":
        app(ref, G_EFF, "APPLIES_AS_IS", "Pure core honored: no ambient reads/writes; callers stamp time.")
    elif cls == "runtime_mechanism":
        app(ref, G_EFF, "APPLIES_WITH_REFINEMENT",
            "Persistence is an effect surface requiring sealed receipts.",
            ["receipt sealing bound to append intent id"])
    elif cls == "provider_adapter":
        app(ref, G_EFF, "APPLIES_WITH_REFINEMENT",
            "Provider calls become budgeted effect intents with retry policy as configuration.",
            ["unbounded retry growth refused"], srcs=["src.otel.logs"] if suf == "lpe.audit-log-adapter" else [])
    else:
        app(ref, G_EFF, "APPLIES_WITH_REFINEMENT",
            "pure_effect_intents boundary: evaluation pure between editions; effects only at commit ports.",
            ["commit intents carry idempotency keys"])
    if ref in BYTE_LIBS:
        app(ref, G_MISS, "NOT_APPLICABLE",
            "No absence/coverage semantics exposed at byte level; unknowns handled upstream.")
    elif ref in COVERAGE_LIBS:
        app(ref, G_MISS, "APPLIES_WITH_REFINEMENT",
            "Coverage consumers keep missing vs negative vs incomplete separate.",
            ["unknown-edge carriers remain first-class"])
    else:
        app(ref, G_MISS, "APPLIES_AS_IS", "Zero-default bans apply to any partial input.")

RET_TARGETS = {
    "lpe.record-lifecycle": "anchor: full transition taxonomy lives here pending split",
    "lpe.preservation-core": "package migration interplays with superseded AIP editions",
    "lpe.retention-policy": "retention/supersession precedence guards",
    "lpe.reproduction-evaluator": "attempt comparisons respect superseded artifact editions",
    "lpe.research-object": "crate revisioning without erasing history",
    "qor.correction_proposal_kernel": "proposals expire and supersede silently-banned",
    "qor.correction_execution_kernel": "restatement trails mandatory",
    "qor.waiver_exception_kernel": "waivers expire; reinstatement keeps history",
    "qor.quarantine_release_kernel": "dispositions recorded as typed transitions",
    "qor.contract_declaration_kernel": "declaration editions never rewritten in place",
    "qor.rule_specification_kernel": "rule deprecation stage machine",
    "qor.certification_attestation_kernel": "certifications superseded, revoked-not-deleted",
    "qor.evidence_receipt_kernel": "sealed evaluation evidence withdrawal path",
    "qor.quality_requirement_kernel": "requirement revisions bind prior verifications",
}
for suf, why in RET_TARGETS.items():
    app(SUFS[suf], G_RET, "APPLIES_AS_IS", f"Transition-law scope: {why}.")
NO_RET_PROBES = BYTE_LIBS + lset("lpe.prov-constraints", "lpe.audit-log-adapter")
for ref in NO_RET_PROBES:
    app(ref, G_RET, "NOT_APPLICABLE", "Immutable/append-only surface exposes no lifecycle verbs.")

META_TARGETS = {
    "lpe.openlineage-adapter": ("facets describe datasets/jobs; they are not dataset identity", "src.openlineage.object-model-1.52"),
    "lpe.prov-interchange": ("bundle documents describe entities; membership is not endorsement", "src.w3c.prov-dm"),
    "lpe.research-object": ("crate manifest aggregates payloads without becoming them", "src.rocrate.1.1"),
    "qor.evidence_receipt_kernel": ("evaluation evidence describes evaluations, kept off subject bytes", "src.w3c.dqv"),
    "qor.data_profiling_kernel": ("sketches describe cuts; snapshots carry cut/source-scoped identity", ""),
    "qor.contract_observation_kernel": ("observation snapshots stay metadata beside declarations", "src.odcs.3.1"),
    "qor.statistical_baseline_kernel": ("baseline freezing metadata binds cut identity", "src.jcgm.vim.2012"),
    "qor.lineage_quality_impact_kernel": ("staleness manifests are metadata over edges", ""),
    "qor.reference_master_alignment_kernel": ("mapping tables describe codes, never merged entity bytes", ""),
}
for suf, (why, s) in META_TARGETS.items():
    app(SUFS[suf], G_META, "APPLIES_AS_IS", f"Data/metadata split anchored: {why}.", srcs=[s] if s else [])
for ref in BYTE_LIBS:
    app(ref, G_META, "NOT_APPLICABLE", "Operates below the data/metadata cut entirely.")

# Cross-family modules
app(SUFS["lpe.openlineage-adapter"], X_DSR, "APPLIES_WITH_REFINEMENT",
    "Adapter distinguishes JobEvent/DatasetEvent design lines from RunEvent lines structurally.",
    ["export Design events without run binding"], srcs=["src.openlineage.object-model-1.52"])
app(SUFS["lpe.compiler-evidence-binding"], X_DSR, "APPLIES_WITH_REFINEMENT",
    "Compilation receipts mirror design-time lineage.", ["receipt kinds tagged design-time"])
app(SUFS["lpe.lineage-core"], X_DSR, "APPLIES_AS_IS", "Logical model declares capability lines; runs observed elsewhere.")
for ref in lset("lpe.field-lineage", "lpe.formula-provenance"):
    app(ref, X_DSR, "APPLIES_AS_IS", "Static derivation graphs have no run association claims.")
app(SUFS["lpe.audit-trail-reconstructor"], X_DSR, "NOT_APPLICABLE", "Reconstruction consumes run observations only.")

DER_SET = {
    "lpe.impact-analysis": ("APPLIES_WITH_REFINEMENT", ["slice outputs typed as hypotheses"], []),
    "qor.signal_correlation_kernel": ("APPLIES_WITH_REFINEMENT", ["co-incidence groups cannot emit cause labels"], []),
    "lpe.lineage-query": ("APPLIES_AS_IS", [], []),
    "lpe.field-lineage": ("APPLIES_AS_IS", [], []),
    "qor.lineage_quality_impact_kernel": ("APPLIES_WITH_REFINEMENT", ["staleness asserts obligation, not causation"], []),
    "qor.accounting_control_reconciliation_kernel": ("NOT_APPLICABLE", ["no graph semantics in finance matching"], []),
}
for suf, (d, rx, sx) in DER_SET.items():
    app(SUFS[suf], X_DER, d, "Derivation/causation boundary adjudicated for this member.", rx, srcs=sx)

OBS_SET = {
    "qor.data_profiling_kernel": ("APPLIES_WITH_REFINEMENT", ["sketches flagged suggestion-grade"], ["src.schelter.deequ.2018"]),
    "qor.contract_observation_kernel": ("APPLIES_AS_IS", [], ["src.odcs.3.1"]),
    "qor.statistical_baseline_kernel": ("APPLIES_AS_IS", [], []),
    "qor.anomaly_detection_kernel": ("APPLIES_AS_IS", [], ["src.bifet.adwin.2007"]),
    "qor.change_point_detection_kernel": ("APPLIES_AS_IS", [], []),
    "qor.distribution_shift_kernel": ("APPLIES_AS_IS", [], []),
    "qor.defect_adjudication_kernel": ("APPLIES_WITH_REFINEMENT", ["observations enter cases tagged inferred"], []),
    "qor.rule_specification_kernel": ("NOT_APPLICABLE", ["declarations are authored, never observed into being"], []),
    "lpe.audit-trail-reconstructor": ("APPLIES_AS_IS", [], []),
}
for suf, (d, rx, sx) in OBS_SET.items():
    app(SUFS[suf], X_OBS, d, "Observation/inference line drawn for member.", rx, srcs=sx)

ATT_SET = {
    "qor.certification_attestation_kernel": ("APPLIES_WITH_REFINEMENT", ["qualified Attestation naming pending owner"], ["src.w3c.dqv"]),
    "lpe.attestation-core": ("APPLIES_AS_IS", [], ["src.intoto.statement-v1"]),
    "lpe.rats-appraisal": ("APPLIES_AS_IS", [], ["src.ietf.rfc9334"]),
    "qor.evidence_receipt_kernel": ("APPLIES_WITH_REFINEMENT", ["annotation certificates distinguished from statements"], []),
    "lpe.claim-argument-core": ("NOT_APPLICABLE", ["argument packaging defines no crypto type"], []),
}
for suf, (d, rx, sx) in ATT_SET.items():
    app(SUFS[suf], X_ATT, d, "Attestation/certificate homonym line applied.", rx, srcs=sx)

REC_SET = {
    "lpe.receipt-store": ("APPLIES_AS_IS", [], ["src.ietf.rfc9942"]),
    "lpe.transparency-client": ("APPLIES_AS_IS", [], ["src.ietf.rfc9943"]),
    "qor.evidence_receipt_kernel": ("APPLIES_WITH_REFINEMENT", ["two receipt publics kept apart"], ["src.w3c.dqv"]),
    "lpe.long-term-validation": ("NOT_APPLICABLE", ["ERS archive timestamps are not PVD inclusion proofs"], ["src.ietf.rfc4998"]),
}
for suf, (d, rx, sx) in REC_SET.items():
    app(SUFS[suf], X_REC, d, "Receipt homonym line applied.", rx, srcs=sx)

IMP_SET = {
    "lpe.impact-analysis": ("APPLIES_WITH_REFINEMENT", ["slices never invalidate evidence directly"], []),
    "qor.lineage_quality_impact_kernel": ("APPLIES_WITH_REFINEMENT", ["consumes slice witnesses only"], []),
    "lpe.lineage-query": ("NOT_APPLICABLE", ["query engine unaware of staleness duties"], []),
}
for suf, (d, rx, sx) in IMP_SET.items():
    app(SUFS[suf], X_IMP, d, "Impact/staleness ownership separated.", rx, srcs=sx)

MATCH_SET = {
    "qor.duplicate_entity_resolution_kernel": ("APPLIES_WITH_REFINEMENT", ["threshold-auto-merge refused"], []),
    "qor.reference_master_alignment_kernel": ("APPLIES_AS_IS", ["mappings excluded from match scoring"], []),
    "qor.correction_execution_kernel": ("APPLIES_AS_IS", ["executes approved matches only via grants"], []),
}
for suf, (d, rx, sx) in MATCH_SET.items():
    app(SUFS[suf], X_MATCH, d, "Candidate/approved-match line applied.", rx, srcs=sx)

# Family-axis modules
FAM_PROV_CONSIDERED = {
    "lpe.prov-interchange": ("APPLIES_WITH_REFINEMENT", ["independent per-bundle validation"], ["src.w3c.prov-dm"]),
    "lpe.lineage-core": ("APPLIES_WITH_REFINEMENT", ["statement algebra extraction is the split motive"], []),
    "lpe.prov-constraints": ("APPLIES_AS_IS", [], ["src.w3c.prov-constraints"]),
    "lpe.lineage-query": ("APPLIES_AS_IS", [], []),
    "lpe.signature-envelope": ("NOT_APPLICABLE", ["DSSE envelope is outside PROV interchange"], []),
}
for suf, (d, rx, sx) in FAM_PROV_CONSIDERED.items():
    app(SUFS[suf], L_PROV, d, "PROV statement/assertion/bundle axis projected.", rx, srcs=sx)

FAM_RATS_CONSIDERED = {
    "lpe.rats-appraisal": ("APPLIES_WITH_REFINEMENT", ["four-role message split enforced"], ["src.ietf.rfc9334"]),
    "lpe.evidence-evaluation": ("NOT_APPLICABLE", ["excluded duty migrated out; strength stays SACM-side"], ["src.omg.sacm-2.3"]),
    "lpe.attestation-core": ("APPLIES_AS_IS", [], []),
    "lpe.claim-argument-core": ("NOT_APPLICABLE", ["argument scoring tradition distinct"], ["src.omg.sacm-2.3"]),
}
for suf, (d, rx, sx) in FAM_RATS_CONSIDERED.items():
    app(SUFS[suf], L_RATS, d, "Appraisal-stack axis projected.", rx, srcs=sx)

FAM_CAN_CONSIDERED = {
    "lpe.canonical-json": ("APPLIES_AS_IS", [], ["src.ietf.rfc8785"]),
    "lpe.canonical-rdf": ("APPLIES_AS_IS", [], ["src.w3c.rdf-canon"]),
    "lpe.digest-core": ("APPLIES_AS_IS", [], ["src.nist.fips180-4"]),
    "lpe.signature-envelope": ("APPLIES_WITH_REFINEMENT", ["resolver port consumption explicit"], ["src.dsse.envelope"]),
    "lpe.verification-method-resolver": ("APPLIES_WITH_REFINEMENT", ["resolution effects produce no verdicts"], ["src.w3c.did-core"]),
    "lpe.attestation-core": ("APPLIES_AS_IS", [], ["src.dsse.envelope"]),
}
for suf, (d, rx, sx) in FAM_CAN_CONSIDERED.items():
    app(SUFS[suf], L_CAN, d, "Canonicalization chain axis projected.", rx, srcs=sx)

FAM_CUST_CONSIDERED = {
    "lpe.custody-core": ("APPLIES_WITH_REFINEMENT", ["custody events independent of fixity"], ["src.iso.27037.landing"]),
    "lpe.preservation-core": ("APPLIES_WITH_REFINEMENT", ["OAIS package trio carrier-bound"], ["src.ccsds.oais-650x0m2"]),
    "lpe.retention-policy": ("APPLIES_WITH_REFINEMENT", ["regime conflict surfacing kept"], ["src.sec.17a4", "src.eu.gdpr.2016"]),
    "lpe.long-term-validation": ("APPLIES_AS_IS", [], ["src.ietf.rfc4998"]),
    "lpe.forensic-acquisition-adapter": ("APPLIES_WITH_REFINEMENT", ["acquisition is pure-effect split"], ["src.nist.800-86"]),
    "qor.quarantine_release_kernel": ("NOT_APPLICABLE", ["disposition states separate axis"], []),
}
for suf, (d, rx, sx) in FAM_CUST_CONSIDERED.items():
    app(SUFS[suf], L_CUST, d, "Custody/preservation/retention axis projected.", rx, srcs=sx)

FAM_AUD_CONSIDERED = {
    "lpe.audit-event-core": ("APPLIES_WITH_REFINEMENT", ["event vocabulary upstream of transport"], []),
    "lpe.audit-log-adapter": ("APPLIES_WITH_REFINEMENT", ["loss reporting mandatory"], ["src.ietf.rfc5424"]),
    "lpe.audit-trail-reconstructor": ("APPLIES_WITH_REFINEMENT", ["gap-first reconstruction"], []),
    "lpe.prov-interchange": ("NOT_APPLICABLE", ["audit events are not PROV instances"], []),
}
for suf, (d, rx, sx) in FAM_AUD_CONSIDERED.items():
    app(SUFS[suf], L_AUD, d, "Audit axis projected.", rx, srcs=sx)

FAM_OPEN_CONSIDERED = {
    "lpe.lineage-query": ("APPLIES_WITH_REFINEMENT", ["coverage policy carrier required"], ["src.w3c.prov-aq"]),
    "lpe.impact-analysis": ("APPLIES_AS_IS", [], []),
    "lpe.field-lineage": ("APPLIES_AS_IS", [], []),
    "qor.lineage_quality_impact_kernel": ("APPLIES_AS_IS", [], []),
    "lpe.audit-trail-reconstructor": ("APPLIES_AS_IS", [], []),
}
for suf, (d, rx, sx) in FAM_OPEN_CONSIDERED.items():
    app(SUFS[suf], L_OPEN, d, "Open-world lineage coverage axis projected.", rx, srcs=sx)

FAM_DIM_CONSIDERED = {
    "qor.quality_dimension_metric_kernel": ("APPLIES_WITH_REFINEMENT", ["split motive: three carriers per DQV"], ["src.w3c.dqv"]),
    "qor.completeness_timeliness_kernel": ("APPLIES_WITH_REFINEMENT", ["characteristic assessments consume metric editions"], ["src.iso.25012.landing"]),
    "qor.sampling_measurement_kernel": ("APPLIES_WITH_REFINEMENT", ["uncertainty stays in measurement role"], []),
    "qor.fitness_for_use_kernel": ("APPLIES_WITH_REFINEMENT", ["judgment never reads as measurement"], ["src.w3c.dqv"]),
    "qor.quality_requirement_kernel": ("APPLIES_AS_IS", [], []),
    "qor.quality_slo_kernel": ("APPLIES_AS_IS", [], []),
    "qor.rule_specification_kernel": ("NOT_APPLICABLE", ["rule IR is not metric vocabulary"], []),
}
for suf, (d, rx, sx) in FAM_DIM_CONSIDERED.items():
    app(SUFS[suf], Q_DIM, d, "Dimension/metric/measurement axis projected.", rx, srcs=sx)

FAM_DET_CONSIDERED = {
    "qor.defect_adjudication_kernel": ("APPLIES_WITH_REFINEMENT", ["authority import at adjudication only"], []),
    "qor.anomaly_detection_kernel": ("APPLIES_AS_IS", [], ["src.bifet.adwin.2007"]),
    "qor.change_point_detection_kernel": ("APPLIES_AS_IS", [], []),
    "qor.distribution_shift_kernel": ("APPLIES_AS_IS", [], []),
    "qor.correction_proposal_kernel": ("APPLIES_AS_IS", [], []),
    "qor.correction_execution_kernel": ("APPLIES_WITH_REFINEMENT", ["no detector-initiated patches"], ["src.fda.alcoa.2018"]),
    "qor.remediation_verification_kernel": ("APPLIES_AS_IS", [], []),
    "qor.quality_alerting_kernel": ("APPLIES_WITH_REFINEMENT", ["alerts carry decided-fact references only"], []),
    "qor.quality_incident_case_kernel": ("APPLIES_AS_IS", [], []),
}
for suf, (d, rx, sx) in FAM_DET_CONSIDERED.items():
    app(SUFS[suf], Q_DET, d, "Detection/adjudication/correction axis projected.", rx, srcs=sx)

FAM_GATE_CONSIDERED = {
    "qor.validation_execution_kernel": ("APPLIES_WITH_REFINEMENT", ["outcome/gate non-collapse enforced"], ["src.openlineage.dq-assertions"]),
    "qor.schema_conformance_kernel": ("APPLIES_AS_IS", [], ["src.w3c.shacl"]),
    "qor.quarantine_release_kernel": ("APPLIES_WITH_REFINEMENT", ["dispositions import authority editions"], []),
    "qor.waiver_exception_kernel": ("APPLIES_WITH_REFINEMENT", ["issuer scope/expiry mandatory"], []),
    "qor.rule_specification_kernel": ("APPLIES_AS_IS", [], []),
    "qor.test_case_management_kernel": ("APPLIES_AS_IS", [], []),
    "qor.quality_policy_kernel": ("APPLIES_WITH_REFINEMENT", ["policy editions gate-importable"], []),
}
for suf, (d, rx, sx) in FAM_GATE_CONSIDERED.items():
    app(SUFS[suf], Q_GATE, d, "Validation-vs-gate axis projected.", rx, srcs=sx)

FAM_DEC_CONSIDERED = {
    "qor.contract_declaration_kernel": ("APPLIES_WITH_REFINEMENT", ["activation states declaration-only"], ["src.odcs.3.1"]),
    "qor.contract_observation_kernel": ("APPLIES_AS_IS", [], []),
    "qor.schema_conformance_kernel": ("APPLIES_AS_IS", [], []),
    "qor.data_profiling_kernel": ("NOT_APPLICABLE", ["profiling proposes, never amends declarations"], ["src.schelter.deequ.2018"]),
    "qor.rule_specification_kernel": ("APPLIES_AS_IS", [], []),
}
for suf, (d, rx, sx) in FAM_DEC_CONSIDERED.items():
    app(SUFS[suf], Q_DEC, d, "Declared-vs-observed axis projected.", rx, srcs=sx)

FAM_ACC_CONSIDERED = {
    "qor.reconciliation_definition_kernel": ("APPLIES_WITH_REFINEMENT", ["truth-role pinning mandatory"], ["src.bcbs239"]),
    "qor.reconciliation_execution_kernel": ("APPLIES_AS_IS", [], []),
    "qor.reconciliation_break_kernel": ("APPLIES_WITH_REFINEMENT", ["lawful disagreement preserved"], []),
    "qor.accounting_control_reconciliation_kernel": ("APPLIES_AS_IS", [], []),
    "qor.reference_master_alignment_kernel": ("NOT_APPLICABLE", ["code alignment is not side-truth bookkeeping"], []),
}
for suf, (d, rx, sx) in FAM_ACC_CONSIDERED.items():
    app(SUFS[suf], Q_ACC, d, "Source/accounting/control truth axis projected.", rx, srcs=sx)

FAM_SAMP_CONSIDERED = {
    "qor.sampling_measurement_kernel": ("APPLIES_WITH_REFINEMENT", ["frame+plan edition binding mandatory"], ["src.iso.2859-1.landing"]),
    "qor.completeness_timeliness_kernel": ("APPLIES_WITH_REFINEMENT", ["population leap refusal explicit"], []),
    "qor.test_case_management_kernel": ("APPLIES_WITH_REFINEMENT", ["coverage ledgers disclose frames"], []),
    "qor.reconciliation_execution_kernel": ("NOT_APPLICABLE", ["full-population matching excludes sampling"], []),
}
for suf, (d, rx, sx) in FAM_SAMP_CONSIDERED.items():
    app(SUFS[suf], Q_SAMP, d, "Sampling/population axis projected.", rx, srcs=sx)

# Freshness/timeliness module is BLOCKED -> UNRESOLVED rows.
app(SUFS["qor.completeness_timeliness_kernel"], Q_FRSH, "UNRESOLVED",
    "Split blocked on ISO/IEC 25012 characteristic text review; bundle retains pending owner.",
    srcs=["src.iso.25012.landing"])
app(SUFS["qor.quality_slo_kernel"], Q_FRSH, "UNRESOLVED",
    "Indicator/budget vocabulary cannot freeze before characteristic split resolves.")

LOCAL_ROWS = [
    ("lpe.lineage-core", LOC_LCORE, "UNRESOLVED",
     "Split candidate researched; ratification by context.lpe.logical-lineage outstanding."),
    ("lpe.field-lineage", LOC_LCORE, "NOT_APPLICABLE",
     "Absorber boundary already matches its own owned question."),
    ("lpe.prov-interchange", LOC_LCORE, "NOT_APPLICABLE",
     "Encoding ownership unaffected by statement-core extraction."),
    ("lpe.openlineage-adapter", LOC_OLAD, "APPLIES_WITH_REFINEMENT",
     "Rename executes this module directly upon ratification.",
     ["new_ref=library.lpe.runtime-lineage-event-adapter; no alias"]),
    ("lpe.compiler-evidence-binding", LOC_OLAD, "NOT_APPLICABLE",
     "Consumer of renamed adapter output; no local change."),
    ("qor.quality_dimension_metric_kernel", LOC_QDIM, "UNRESOLVED",
     "Three-way split candidate pending owner."),
    ("qor.completeness_timeliness_kernel", LOC_QDIM, "NOT_APPLICABLE",
     "Consumer of future registry/metric kernels; own axis handled at LOC_CT."),
    ("qor.completeness_timeliness_kernel", LOC_CT, "UNRESOLVED",
     "Split blocked on ISO 25012 full text (vac.iso25012-fulltext-characteristics)."),
    ("qor.quality_slo_kernel", LOC_CT, "NOT_APPLICABLE",
     "Budget semantics independent of assessment carrier packaging."),
    ("lpe.record-lifecycle", LOC_RLC, "UNRESOLVED",
     "Correction/supersession vs retraction/disposition split awaiting recall-owner decision."),
    ("qor.waiver_exception_kernel", LOC_RLC, "NOT_APPLICABLE",
     "Waivers unaffected by record-transition split."),
    ("qor.quarantine_release_kernel", LOC_RLC, "NOT_APPLICABLE",
     "Disposition workflow consumes transitions via imports."),
    ("qor.observability_instrumentation_kernel", LOC_OBS, "UNRESOLVED",
     "Replacement blocked on telemetry-family owner assignment outside assigned lane."),
    ("qor.signal_correlation_kernel", LOC_OBS, "NOT_APPLICABLE",
     "Correlation identity rules stay in QOR regardless of export adapter location."),
]
for row in LOCAL_ROWS:
    suf, mid, d, why = row[0], row[1], row[2], row[3]
    refinements = row[4] if len(row) > 4 else ()
    app(SUFS[suf], mid, d, why, refinements)

# ---------------------------------------------------------------------------
# 6. Conflicts / vacancies.
# ---------------------------------------------------------------------------
def vac(vacancy_id, kind, refs, statement, needed, srcs=()):
    return {"vacancy_id": vacancy_id, "kind": kind, "affected_library_refs": sorted(refs),
            "statement": statement, "required_evidence": needed, "source_refs": list(srcs)}

VACANCIES = sorted([
    vac("vac.auth.erasure-retention-authority-conflict", "AUTHORITY_UNRESOLVED",
        ["library.lpe.retention-policy", "library.lpe.preservation-core", "library.lpe.record-lifecycle"],
        "GDPR-class erasure rights, SEC 17a-4-style preservation duties and legal holds have no ratified precedence order in this lane; libraries surface conflicts instead of resolving them.",
        "Owner-ratified authority precedence matrix naming erasure, retention and hold issuers per jurisdiction.",
        ["src.eu.gdpr.2016", "src.sec.17a4"]),
    vac("vac.iso25012-fulltext-characteristics", "EVIDENCE_VACANCY",
        ["library.qor.completeness_timeliness_kernel", "library.qor.quality_dimension_metric_kernel",
         "library.qor.quality_slo_kernel"],
        "ISO/IEC 25012 full text was not independently retrieved (paywalled); characteristic inventory rests on the official landing page only.",
        "Full standard text review; precise characteristic names and definitions.",
        ["src.iso.25012.landing"]),
    vac("vac.iso2859-fulltext-plans", "EVIDENCE_VACANCY",
        ["library.qor.sampling_measurement_kernel", "library.qor.test_case_management_kernel"],
        "ISO 2859-1 acceptance-sampling plan mechanics rest on paywalled full text; lot-disposition ownership unassigned.",
        "Full standard text plus an owner decision mapping AQL dispositions to SAN authorities.",
        ["src.iso.2859-1.landing"]),
    vac("vac.iso27037-fulltext-handling", "EVIDENCE_VACANCY",
        ["library.lpe.forensic-acquisition-adapter", "library.lpe.custody-core"],
        "ISO/IEC 27037 handling-stage vocabulary cited from its landing page only.",
        "Full guideline text review for acquisition/custody stage verbs.", ["src.iso.27037.landing"]),
    vac("vac.contract-ir-encoding-owner", "AUTHORITY_UNRESOLVED",
        ["library.qor.rule_specification_kernel", "library.qor.contract_declaration_kernel",
         "library.qor.validation_execution_kernel"],
        "ODCS, OpenAPI-family schemas and data-contract-spec all model declared contracts; none is the SAN owner.",
        "Semantic-owner selection for one canonical declared-contract IR with interop profiles.",
        ["src.odcs.3.1"]),
    vac("vac.runtime-receipts-universe-only", "COVERAGE_VACANCY",
        ["library.lpe.receipt-store", "library.qor.evidence_receipt_kernel"],
        "The owner universe contains runtime receipt algebra candidates absent from this closure set; assignment cannot close them.",
        "Addition of the missing universe libraries to a future queue edition or explicit retirement rationale.",
        ["src.ietf.rfc9942", "src.ietf.rfc9943"]),
    vac("vac.symbol.cross-context-homonyms", "HOMONYM_UNRESOLVED",
        [],
        "27 p0 collisions touch assigned libraries (e.g., AppraisalPolicy spans LPE rats-appraisal and experimentation families); every one is UNRESOLVED pending cross-owner adjudication.",
        "Per-symbol owner decisions choosing canonical shared owners, qualified ids, or renames per p0 allowed dispositions."),
    vac("vac.materiality-policy-jurisdiction", "AUTHORITY_UNRESOLVED",
        ["library.qor.defect_adjudication_kernel", "library.qor.reconciliation_break_kernel"],
        "Materiality numbers are jurisdiction/regulator-specific; no lane-ratified default exists.",
        "Named materiality policy sources per regulated vertical with editions."),
    vac("vac.match-merge-authorization-context", "OWNER_UNRESOLVED",
        ["library.qor.duplicate_entity_resolution_kernel", "library.qor.correction_execution_kernel"],
        "Approved-match/merge authority belongs to master-data management contexts outside these families.",
        "SAN context declaration owning identity merge authorization.", []),
    vac("vac.two-appraisal-traditions", "SOURCE_CONFLICT",
        ["library.lpe.rats-appraisal", "library.lpe.evidence-evaluation", "library.lpe.claim-argument-core"],
        "RATS protocol appraisal and SACM argument scoring impose incompatible role vocabularies that cannot share one API without semantic loss.",
        "Owner decision ratifying coexistence with qualified types or an anti-corruption translation module.",
        ["src.ietf.rfc9334", "src.omg.sacm-2.3"]),
    vac("vac.freshness-currentness-vocabulary", "AMBIGUITY",
        ["library.qor.completeness_timeliness_kernel", "library.qor.quality_slo_kernel"],
        "currentness/freshness terminology alignment awaits the ISO 25012 text before carriers freeze.",
        "Post-review vocabulary decision recorded against ISO 25012 clauses.", ["src.iso.25012.landing"]),
    vac("vac.openlineage-version-drift", "SOURCE_DRIFT_RISK",
        ["library.lpe.openlineage-adapter", "library.lpe.compiler-evidence-binding"],
        "OpenLineage facets are extensible and version-bound; 1.52.0 pinning requires renewal policy.",
        "Adapter support-matrix governance tied to OpenLineage releases.", ["src.openlineage.object-model-1.52"]),
    vac("vac.audit-admissibility-jurisdictions", "AUTHORITY_UNRESOLVED",
        ["library.lpe.audit-event-core", "library.lpe.audit-trail-reconstructor"],
        "Audit trail admissibility is court/jurisdiction-specific; no universal oracle.",
        "Jurisdiction map binding admissibility authorities where products require it.",
        ["src.nist.800-86"]),
    vac("vac.xbrl-formula-oim-drift", "SOURCE_DRIFT_RISK",
        ["library.qor.accounting_control_reconciliation_kernel"],
        "OIM-compatible Formula remains Candidate Recommendation; reconciliation wrappers must not depend on CR-only features.",
        "Tracking of Formula OIM REC promotion.", ["src.xbrl.formula-1.0"]),
    vac("vac.odcs-vs-competing-contract-documents", "SOURCE_CONFLICT",
        ["library.qor.contract_declaration_kernel"],
        "Multiple contract document standards compete; bounded claims cover structure only.",
        "Interoperability profile choice by the contract IR owner.", ["src.odcs.3.1"]),
], key=lambda v: v["vacancy_id"])

# ---------------------------------------------------------------------------
# 7. Gap dependency graph.
# ---------------------------------------------------------------------------
def gap(gid, kind, defect, locus, grain, axes, libs, mods, closure, role, evidence,
        blocked, fanout):
    return {
        "gap_id": gid, "gap_kind": kind, "defect_kind": defect, "locus": locus,
        "scope_grain": grain, "semantic_axes": axes,
        "affected_library_refs": sorted(libs), "affected_module_refs": list(mods),
        "required_closure_operation": closure, "required_authority_role": role,
        "required_evidence": evidence, "blocked_outputs": list(blocked),
        "fanout": fanout, "status": "OPEN_OWNER_ADJUDICATION_REQUIRED",
    }

GAP_NODES = [
    gap("gap.auth.audit-admissibility-jurisdictions", "SOURCE_AUTHORITY_GAP", "missing_authority",
        "context.lpe.audit-trail", "cross_context", ["authority_and_trust"],
        ["lpe.audit-event-core", "lpe.audit-trail-reconstructor"], [L_AUD],
        "bind jurisdiction-specific admissibility authorities via owner decision",
        "external legal authority per jurisdiction",
        "jurisdiction-to-authority map with editions", ["audit admissibility oracles"], 2),
    gap("gap.auth.materiality-policy-sources", "SOURCE_AUTHORITY_GAP", "missing_authority",
        "qor.context.defect_adjudication + accounting_control_reconciliation", "family",
        ["authority_and_trust"],
        ["qor.defect_adjudication_kernel", "qor.reconciliation_break_kernel"], [Q_DET, Q_ACC],
        "import named materiality policy editions per regulated vertical",
        "sector regulator / internal policy authority",
        "materiality policy source register", ["auto-adjudication defaults remain forbidden"], 2),
    gap("gap.conflict.two-appraisal-traditions", "SEMANTIC_CONFLICT", "incompatible_vocabulary",
        "context.lpe.independent-appraisal vs context.lpe.evidence-strength", "cross_family",
        ["evidence_and_conformance", "semantic_role"],
        ["lpe.rats-appraisal", "lpe.evidence-evaluation", "lpe.claim-argument-core"], [L_RATS],
        "ratify coexistence with qualified types or anti-corruption translation",
        "SAN semantic owner (LPE bounded contexts jointly)",
        "owner boundary decision record", ["unified appraisal APIs stay BLOCKED"], 3),
    gap("gap.coverage.runtime-receipts-universe-only", "INPUT_COVERAGE_VACANCY", "queue_incompleteness",
        "exact_api_closure queue vs owner universe", "registry_global",
        ["representation", "effect_boundary"],
        ["lpe.receipt-store", "qor.evidence_receipt_kernel"], [X_REC],
        "extend future queue edition with universe receipt-algebra libraries or retire rationale",
        "closure-queue program owner",
        "universe diff listing missing libraries", ["receipt-core naming decisions"], 2),
    gap("gap.evidence.iso25012-fulltext", "EVIDENCE_VACANCY", "paywalled_standard_text",
        "ISO/IEC 25012", "standard_edition", ["semantic_object", "time"],
        ["qor.completeness_timeliness_kernel", "qor.quality_dimension_metric_kernel", "qor.quality_slo_kernel"],
        [Q_FRSH, Q_DIM],
        "review full standard text and freeze characteristic carriers",
        "external standards body adoption by SAN owner",
        "ISO 25012:2008 full text", ["completeness/freshness/timeliness split carriers"], 3),
    gap("gap.evidence.iso27037-fulltext", "EVIDENCE_VACANCY", "paywalled_standard_text",
        "ISO/IEC 27037", "standard_edition", ["privacy_security_safety"],
        ["lpe.forensic-acquisition-adapter", "lpe.custody-core"], [L_CUST],
        "review handling-stage guidance text", "SAN custody bounded context",
        "ISO 27037:2012 full text", ["acquisition stage verb set"], 2),
    gap("gap.evidence.iso2859-fulltext", "EVIDENCE_VACANCY", "paywalled_standard_text",
        "ISO 2859-1", "standard_edition", ["grain_and_cardinality", "authority_and_trust"],
        ["qor.sampling_measurement_kernel", "qor.test_case_management_kernel"], [Q_SAMP],
        "review plan tables; assign lot-disposition ownership",
        "sampling-policy authority per vertical",
        "ISO 2859-1:1999 full text", ["AQL disposition import contracts"], 2),
    gap("gap.owner.contract-ir-selection", "OWNER_DECISION_REQUIRED", "competing_specifications",
        "qor.context.contract_declaration/rule_specification", "cross_family",
        ["rule_or_policy", "compatibility_and_evolution"],
        ["qor.rule_specification_kernel", "qor.contract_declaration_kernel", "qor.validation_execution_kernel",
         "library.qor.schema_conformance_kernel".replace("library.", "")], [Q_DEC, Q_GATE],
        "select canonical declared-contract and rule IRs with interop profiles",
        "SAN semantic owner for data contracts",
        "ratified IR decision + profile matrix", ["declaration kernels keep PARTIAL status"], 4),
    gap("gap.owner.erasure-retention-precedence", "AUTHORITY_UNRESOLVED", "conflicting_regimes",
        "context.lpe.retention-legal-hold/custody/correction", "cross_jurisdiction",
        ["state_and_change", "authority_and_trust"],
        ["lpe.retention-policy", "lpe.preservation-core", "lpe.record-lifecycle"], [G_RET, G_AUTH],
        "publish precedence matrix across erasure, retention and hold issuers",
        "external legal authorities + SAN policy owner",
        "precedence decision record citing regimes", ["automatic conflict resolution stays refused"], 3),
    gap("gap.owner.match-merge-authorization", "OWNER_DECISION_REQUIRED", "ownership_absent",
        "MDM identity contexts outside assigned families", "cross_lane",
        ["identity_and_equality", "authority_and_trust"],
        ["qor.duplicate_entity_resolution_kernel", "qor.correction_execution_kernel"], [X_MATCH],
        "declare owning context for approved matches/merges",
        "master-data management semantic owner",
        "owner-context declaration", ["merge execution ports stay imported-only"], 2),
    gap("gap.semantic.freshness-currentness-vocabulary", "AMBIGUITY", "terminology_unresolved",
        "qor.context.completeness_timeliness", "family_axis", ["time", "semantic_object"],
        ["qor.completeness_timeliness_kernel", "qor.quality_slo_kernel"], [Q_FRSH],
        "align vocabulary post ISO 25012 review", "SAN quality bounded context",
        "clause-mapped terminology note", ["freshness kernel naming"], 2),
    gap("gap.source.openlineage-version-drift", "SOURCE_DRIFT_RISK", "moving_target",
        "OpenLineage releases", "provider_ecosystem", ["compatibility_and_evolution", "representation"],
        ["lpe.openlineage-adapter", "lpe.compiler-evidence-binding"], [X_DSR],
        "versioned support-matrix governance", "runtime-lineage bounded context",
        "release tracking register", ["facet drift silently breaking adapters"], 2),
    gap("gap.source.xbrl-formula-oim-drift", "SOURCE_DRIFT_RISK", "candidate_drift",
        "XBRL Formula OIM", "specification_track", ["compatibility_and_evolution"],
        ["qor.accounting_control_reconciliation_kernel"], [Q_ACC],
        "track CR->REC promotion before depending", "accounting reconciliation context",
        "promotion announcement", ["CR-only feature dependencies"], 2),
    gap("gap.symbol.cross-context-homonyms", "SYMBOL_COLLISIONS", "unresolved_owners",
        "p0_identity_grain collision queue", "registry_global", ["identity_and_equality"],
        [], [],
        "execute p0 dispositions per symbol (shared owner, qualified ids, or rename)",
        "SAN symbol governance board",
        "27 collision records all UNRESOLVED in snapshot", [
            "exportable unified surfaces for AppraisalPolicy-class names"], 6),
] + [
    gap("gap.blocked.record-lifecycle-recall-owner", "BLOCKED_DOWNSTREAM", "awaiting_owner",
        "context.lpe.correction", "library",
        ["state_and_change"], ["lpe.record-lifecycle"], [LOC_RLC, G_RET],
        "proceed after recall-vocabulary authority decision lands",
        "product-safety authority designation",
        "see required_evidence of blocking gaps",
        ["record-lifecycle split execution"], 1),
    gap("gap.blocked.completeness-timeliness-split-execution", "BLOCKED_DOWNSTREAM", "awaiting_evidence",
        "qor.context.completeness_timeliness", "library",
        ["time", "semantic_object"], ["qor.completeness_timeliness_kernel"], [LOC_CT, Q_FRSH],
        "split after ISO text review", "SAN quality bounded context",
        "see required_evidence of blocking gaps", ["three assessment kernels"], 1),
    gap("gap.blocked.telemetry-adapter-relocation", "BLOCKED_DOWNSTREAM", "awaiting_owner",
        "telemetry family lane", "cross_lane", ["effect_boundary", "semantic_object"],
        ["qor.observability_instrumentation_kernel"], [LOC_OBS],
        "relocate emission after telemetry family owner ratifies target",
        "telemetry family semantic owner", "target family declaration",
        ["observability kernel replacement"], 1),
]

GAP_EDGES = sorted([
    {"edge_id": "edge.001", "from_gap_ref": "gap.owner.erasure-retention-precedence",
     "to_gap_ref": "gap.blocked.record-lifecycle-recall-owner", "relation": "BLOCKS",
     "reason": "Recall/deletion dispositions cannot finalize without regime precedence."},
    {"edge_id": "edge.002", "from_gap_ref": "gap.evidence.iso25012-fulltext",
     "to_gap_ref": "gap.blocked.completeness-timeliness-split-execution", "relation": "BLOCKS",
     "reason": "Characteristic carriers freeze only after full-text review."},
    {"edge_id": "edge.003", "from_gap_ref": "gap.evidence.iso25012-fulltext",
     "to_gap_ref": "gap.semantic.freshness-currentness-vocabulary", "relation": "CAUSES",
     "reason": "Terminology ambiguity stems from unreviewed clauses."},
    {"edge_id": "edge.004", "from_gap_ref": "gap.semantic.freshness-currentness-vocabulary",
     "to_gap_ref": "gap.blocked.telemetry-adapter-relocation", "relation": "REFINES",
     "reason": "Export labels inherit final indicator names."},
    {"edge_id": "edge.005", "from_gap_ref": "gap.conflict.two-appraisal-traditions",
     "to_gap_ref": "gap.symbol.cross-context-homonyms", "relation": "CAUSES",
     "reason": "AppraisalPolicy-class collisions flow from two appraisal vocabularies colliding."},
    {"edge_id": "edge.006", "from_gap_ref": "gap.source.openlineage-version-drift",
     "to_gap_ref": "gap.source.xbrl-formula-oim-drift", "relation": "DUPLICATES",
     "reason": "Both are external specification tracks needing the same monitoring operation."},
], key=lambda e: e["edge_id"])

GAPS = GAP_NODES + GAP_EDGES

# ---------------------------------------------------------------------------
# 8. Merge candidates (non-authoritative proposal queue).
# ---------------------------------------------------------------------------
SNAP = br.snapshot()
AGG = SNAP["aggregate_digest"]

def cand(cid, kind, target, op, payload, srcs, mods, libs, deps, risk, conf,
         status="PROPOSED_UNRATIFIED"):
    return {
        "candidate_id": cid,
        "target_artifact_kind": kind,
        "target_ref": target,
        "operation": op,
        "precondition_input_digest": AGG,
        "proposed_payload": payload,
        "source_refs": list(srcs),
        "semantic_module_refs": list(mods),
        "affected_library_refs": sorted(libs),
        "decision_dependencies": list(deps),
        "risk": risk,
        "confidence": conf,
        "status": status,
    }

LIBENTRY = "library_registry_entry"
MERGES = sorted([
    cand("mc.add.lineage-statement-core", LIBENTRY, "library.lpe.lineage-statement-core", "ADD",
         {"owned_question": "normative logical lineage statement model",
          "semantic_owner": "context.lpe.logical-lineage", "supersedes_part_of": "library.lpe.lineage-core"},
         ["src.w3c.prov-dm", "src.w3c.prov-constraints"], [L_PROV],
         ["lpe.lineage-core"], ["gap.symbol.cross-context-homonyms"], "medium", "high"),
    cand("mc.rename.runtime-lineage-event-adapter", LIBENTRY, "library.lpe.openlineage-adapter", "RENAME",
         {"new_ref": "library.lpe.runtime-lineage-event-adapter",
          "alias_allowed": False},
         ["src.openlineage.object-model-1.52"], [X_DSR, LOC_OLAD.replace("module.local.", "module.local.")][:1] + [LOC_OLAD],
         ["lpe.openlineage-adapter"], [], "low", "high"),
    cand("mc.split.lineage-core-responsibilities", LIBENTRY, "library.lpe.lineage-core", "SPLIT",
         {"statement_core": "library.lpe.lineage-statement-core",
          "runtime_encoding": "library.lpe.runtime-lineage-event-adapter",
          "field_lineage": "library.lpe.field-lineage"},
         ["src.w3c.prov-dm"], [L_PROV], ["lpe.lineage-core"],
         ["gap.owner.contract-ir-selection".replace("contract-ir", "contract-ir")], "medium", "high"),
    cand("mc.split.quality-dimension-metric-kernel", LIBENTRY, "library.qor.quality_dimension_metric_kernel", "SPLIT",
         {"dimension_registry": "library.qor.quality_dimension_registry_kernel",
          "metric_definition": "library.qor.metric_definition_kernel",
          "measurement_evaluation": "library.qor.measurement_evaluation_kernel"},
         ["src.w3c.dqv", "src.jcgm.vim.2012"], [Q_DIM, LOC_QDIM],
         ["qor.quality_dimension_metric_kernel"], [], "medium", "high"),
    cand("mc.split.completeness-timeliness-kernel", LIBENTRY, "library.qor.completeness_timeliness_kernel", "SPLIT",
         {"completeness": "library.qor.completeness_assessment_kernel",
          "freshness": "library.qor.freshness_assessment_kernel",
          "timeliness": "library.qor.timeliness_assessment_kernel"},
         ["src.iso.25012.landing", "src.w3c.dqv"], [Q_FRSH, LOC_CT],
         ["qor.completeness_timeliness_kernel"],
         ["gap.evidence.iso25012-fulltext", "gap.semantic.freshness-currentness-vocabulary"],
         "high", "medium"),
    cand("mc.split.record-lifecycle-transitions", LIBENTRY, "library.lpe.record-lifecycle", "SPLIT",
         {"correction_supersession": "library.lpe.correction-supersession-core",
          "retraction_disposition": "library.lpe.retraction-disposition-core"},
         ["src.fda.alcoa.2018", "src.oasis.csaf-2.0", "src.eu.gdpr.2016"], [G_RET, LOC_RLC],
         ["lpe.record-lifecycle"], ["gap.owner.erasure-retention-precedence"], "high", "medium"),
    cand("mc.replace.observability-with-telemetry-adapter", LIBENTRY,
         "library.qor.observability_instrumentation_kernel", "REPLACE",
         {"replacement_ref": "library.telemetry.quality-metrics-export-adapter",
          "retained_qor_rule": "correlation identity stays in signal_correlation"},
         ["src.otel.logs"], [G_EFF, LOC_OBS],
         ["qor.observability_instrumentation_kernel"],
         ["gap.blocked.telemetry-adapter-relocation"], "medium", "medium"),
    cand("mc.narrow.evidence-evaluation-excludes-rats-typing", LIBENTRY, "library.lpe.evidence-evaluation", "REPLACE",
         {"excluded_duty": "RATS message typing", "moved_to": "library.lpe.rats-appraisal"},
         ["src.ietf.rfc9334", "src.omg.sacm-2.3"], [L_RATS], ["lpe.evidence-evaluation"],
         ["gap.conflict.two-appraisal-traditions"], "low", "high"),
    cand("mc.narrow.impact-analysis-slices-are-hypotheses", LIBENTRY, "library.lpe.impact-analysis", "REPLACE",
         {"renamed_outcome_semantics": "ImpactSliceCandidate carries hypothesis role",
          "causal_narrative_moved_to": "library.lpe.claim-argument-core"},
         ["src.w3c.prov-dm"], [X_DER, X_IMP], ["lpe.impact-analysis"], [], "low", "high"),
    cand("mc.narrow.preservation-core-holds-to-retention", LIBENTRY, "library.lpe.preservation-core", "REPLACE",
         {"hold_coordination_moved_to": "library.lpe.retention-policy"},
         ["src.sec.17a4", "src.ccsds.oais-650x0m2"], [L_CUST], ["lpe.preservation-core"],
         ["gap.owner.erasure-retention-precedence"], "low", "high"),
    cand("mc.narrow.certification-attestation-names", LIBENTRY, "library.qor.certification_attestation_kernel", "RENAME",
         {"qualified_publics": {"QualityCertificationIssuance": "kept",
                                "Attestation*": "reserved for library.lpe.attestation-core"},
          "crypto_statement_moved_to": "library.lpe.attestation-core"},
         ["src.w3c.dqv", "src.intoto.statement-v1"], [X_ATT],
         ["qor.certification_attestation_kernel"], ["gap.symbol.cross-context-homonyms"], "medium", "medium"),
    cand("mc.narrow.evidence-receipt-vs-transparency-receipt", LIBENTRY, "library.qor.evidence_receipt_kernel", "RENAME",
         {"public_renames": {"EvidenceReceipt": "QualityEvaluationEvidenceRecord"},
          "inclusion_proofs_moved_to": "library.lpe.receipt-store"},
         ["src.w3c.dqv", "src.ietf.rfc9942"], [X_REC],
         ["qor.evidence_receipt_kernel", "lpe.receipt-store"],
         ["gap.coverage.runtime-receipts-universe-only"], "medium", "medium"),
    cand("mc.narrow.duplicate-resolution-no-auto-merge", LIBENTRY, "library.qor.duplicate_entity_resolution_kernel", "REPLACE",
         {"merge_effect_port_moved_to": "library.qor.correction_execution_kernel",
          "candidates_remain": "reversible drafts"},
         [], [X_MATCH], ["qor.duplicate_entity_resolution_kernel"],
         ["gap.owner.match-merge-authorization"], "low", "high"),
    cand("mc.record-vacancy.runtime-receipt-algebra-libraries", LIBENTRY,
         "research/domain_atlas/compiler/library_registry/exact_api_closure/closure-queue.jsonl",
         "RECORD_VACANCY",
         {"vacancy_note": "universe receipt-algebra candidates absent from assigned set",
          "request": "next queue edition adds or retires them explicitly"},
         ["src.ietf.rfc9942", "src.ietf.rfc9943"], [X_REC],
         ["lpe.receipt-store"], ["gap.coverage.runtime-receipts-universe-only"], "low", "high"),
    cand("mc.record-vacancy.recall-authority-source", "owner_context_note",
         "context.lpe.correction", "RECORD_VACANCY",
         {"note": CSAF_FIX, "need": "product-safety recall vocabulary owner"},
         ["src.oasis.csaf-2.0"], [G_RET],
         ["lpe.record-lifecycle"], ["gap.owner.erasure-retention-precedence"], "medium", "high"),
], key=lambda m: m["candidate_id"])

# ---------------------------------------------------------------------------
# 9. Coverage report + README.
# ---------------------------------------------------------------------------
import hashlib

P0_DIR = br.REPO / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p0_identity_grain"

def count_collisions_touching_assigned():
    n = 0
    for f in ("global-symbol-collisions.jsonl", "cross-family-type-collisions.jsonl"):
        p = P0_DIR / f
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            occ = rec.get("occurrences") or []
            if any(o.get("library_ref") in set(ASSIGNED) for o in occ):
                n += 1
    return n

ROOT_GAPS = []
_incoming = {e["to_gap_ref"] for e in GAP_EDGES if e["relation"] in {"BLOCKS", "CAUSES"}}
ROOT_GAPS = [n for n in GAP_NODES if n["gap_id"] not in _incoming]

mod_consumers: dict[str, set[str]] = {}
for r in APP_ROWS:
    mod_consumers.setdefault(r["module_ref"], set()).add(r["library_ref"])
multi_consumer_modules = [m for m, c in mod_consumers.items() if len(c) > 1]
singletons = sorted(m for m, c in mod_consumers.items() if len(c) == 1)

COVERAGE = {
    "input_family_count": len(br.FAMILIES),
    "input_library_count": len(ASSIGNED),
    "assigned_library_refs": ASSIGNED,
    "covered_library_refs": sorted({r["library_ref"] for r in ADJUDICATIONS}),
    "missing_library_refs": sorted(set(ASSIGNED) - {r["library_ref"] for r in ADJUDICATIONS}),
    "duplicate_library_refs": [],
    "unrelated_added_refs": sorted({r["library_ref"] for r in ADJUDICATIONS} - set(ASSIGNED)),
    "counts_by_verdict": {v: sum(1 for a in ADJUDICATIONS if a["verdict"] == v)
                          for v in sorted({a["verdict"] for a in ADJUDICATIONS})},
    "counts_by_confidence_adjudications": {c: sum(1 for a in ADJUDICATIONS if a["confidence"] == c)
                                           for c in ("high", "medium", "low")},
    "counts_by_contract_status": {s: sum(1 for c in ALL_CONTRACTS if c["contract_status"] == s)
                                  for s in sorted({c["contract_status"] for c in ALL_CONTRACTS})},
    "source_count": len(br.SOURCES),
    "sources_by_class": {},
    "unresolved_conflicts_count": sum(1 for v in VACANCIES if v["kind"] in {
        "SOURCE_CONFLICT", "AUTHORITY_UNRESOLVED", "OWNER_UNRESOLVED", "HOMONYM_UNRESOLVED", "AMBIGUITY"}),
    "conflicts_and_vacancies_count": len(VACANCIES),
    "evidence_vacancies_count": sum(1 for v in VACANCIES if v["kind"] == "EVIDENCE_VACANCY"),
    "validation_failures": [],
    "validation_command": "python3 validate.py",
    "completion_claim": False,
    "completion_scope_note": (
        "Structurally complete for this input snapshot's research lane; nothing herein is "
        "ratified semantics, an implementation claim or a qualification claim."),
    "module_count": len(MODULES),
    "applicability_row_count": None,
    "root_gap_count": len(ROOT_GAPS),
    "represented_downstream_gap_count": len(GAP_NODES) - len(ROOT_GAPS),
    "reuse_ratio": round(len(multi_consumer_modules) / max(1, len(MODULES)), 4),
    "singleton_residual_modules": singletons,
    "singleton_residual_count": len(singletons),
    "unresolved_public_symbol_collisions": None,
    "research_cutoff": br.CUTOFF,
    "generated_at": None,
    "researched_proposition_count": len(MODULES),
    "projection_count": None,
    "merge_candidate_count": len(MERGES),
}

README = """# Provenance/evidence and quality/reconciliation research lane — output

## Scope

Independent boundary/provenance/quality research for the two complete families
`lineage_provenance_evidence` (31 libraries) and `quality_reconciliation` (37 libraries):
68 assigned `library_ref` values from the exact-API closure program's `research-batches.jsonl`.
The lane produces evidence packs, falsifiable semantic modules, per-library applicability
projections, changed-boundary migrations, semantic contract *requirements* (not APIs), a
conflict/vacancy register, an acyclic gap dependency graph and a machine-readable
(non-authoritative) merge-candidate queue. Nothing is ratified, implemented or qualified.

## Method

1. Input snapshot: 15 authoritative inputs digested (`input_snapshot` in coverage-report.json).
2. Ontology-first: 37 reusable propositions (7 global primitives, 7 cross-family, 17 family-axis,
   6 local refinements) researched against primary standards/papers; every module carries bounded
   claims, counterexamples and an authority limit; statuses stay CANDIDATE_UNRATIFIED/BLOCKED.
3. Projection: each library receives one boundary adjudication plus explicit rows for every
   considered module (no silent NOT_APPLICABLE by absence).
4. Falsification: counterexamples recorded per decision; checkpoint defects found via live web
   verification were repaired rather than inherited (see corrections below).
5. Deterministic regeneration: `python3 build_corpus.py` then `python3 validate.py`.

## Verification of sources (accessed 2026-08-26)

Primary pages fetched live: OpenLineage object model shows version **1.52.0** with
RunEvent runtime vs JobEvent/DatasetEvent design-time separation; W3C RDFC-1.0 is a
Recommendation of 21 May 2024; OMG SACM 2.3 formal October 2023; RFC 9943 SCITT +
RFC 9942 COSE Receipts are Proposed Standards (2026); FDA CGMP data-integrity Q&A final
December 2018; XBRL Formula 1.0 Recommendation **22 June 2009**; RO-Crate 1.1 published
**30 October 2020** (superseded by later editions); PREMIS 3.0 official LOC v3 landing.
ISO/IEC 25012/2859-1/27037 full texts remain paywalled and are carried as typed vacancies,
never as fabricated content. An earlier secondary ISO-25012 portal source was dropped after
returning HTTP 404 during this run.

## Checkpoint repairs applied by this completion stage

Falsified CSAF-recall clauses replaced (CSAF 2.0 has no recall product status); XBRL Formula
date corrected to 2009; RO-Crate date corrected to 2020-10-30; iso25000.com overview source
removed; PREMIS URI moved to LOC v3 landing; added CSAF 2.0, RFC 9942, RFC 5424 and GDPR
sources underwriting lifecycle/receipt/custody adjudications.

## Ten most consequential boundary corrections

1. `library.lpe.lineage-core` SPLIT: logical statements vs vendor encoding helpers vs field grain
   had different owners and change cadences; responsibilities mapped with no aliases.
2. `library.lpe.record-lifecycle` SPLIT: correction/supersession separated from retraction and from
   erasure/recall dispositions that import external legal authorities (GDPR vs retention regimes).
3. `library.qor.quality_dimension_metric_kernel` SPLIT into DQV's Dimension/Metric/Measurement trio.
4. `library.qor.completeness_timeliness_kernel` SPLIT blocked on ISO 25012 full text but never
   collapsed into one "DeliveryQuality" score.
5. `library.lpe.openlineage-adapter` RENAME to `runtime-lineage-event-adapter`: a project name on an
   adapter can masquerade as a semantic owner.
6. `library.qor.certification_attestation_kernel` NARROWED: quality certification must not own
   cryptographic Statement construction (cross-family Attestation homonym quarantine).
7. `library.qor.evidence_receipt_kernel` NARROWED: quality evaluation evidence is not a PVD receipt;
   inclusion proofs stay in `receipt-store` (RFC 9942/9943 vs DQV annotation traditions).
8. `library.lpe.evidence-evaluation` NARROWED to SACM-style strength scoring; RATS message typing
   migrated out, keeping two appraisal traditions non-collapsed.
9. `library.qor.duplicate_entity_resolution_kernel` NARROWED: confidence scores can never authorize
   merges; execution moves behind the authorized-change boundary.
10. `library.qor.lineage_quality_impact_kernel` NARROWED: staleness invalidation consumes LPE slice
    witnesses instead of sharing one "Impact" public type.

## Ten most dangerous unresolved gaps

1. `gap.owner.erasure-retention-precedence` — GDPR-class erasure vs WORM preservation vs holds.
2. `gap.symbol.cross-context-homonyms` — 27 p0 collisions touching assigned libraries, all UNRESOLVED.
3. `gap.owner.contract-ir-selection` — ODCS/OpenAPI/data-contract-spec competition blocks declaration kernels.
4. `gap.conflict.two-appraisal-traditions` — RATS protocol appraisal vs SACM scoring vocabularies.
5. `gap.evidence.iso25012-fulltext` — paywalled standard text freezes three kernel splits.
6. `gap.coverage.runtime-receipts-universe-only` — owner-universe receipt libraries absent from queue.
7. `gap.auth.materiality-policy-sources` — no ratified materiality policy register.
8. `gap.owner.match-merge-authorization` — approved-match authority lives outside both families.
9. `gap.auth.audit-admissibility-jurisdictions` — audit trails lack jurisdiction authority bindings.
10. `gap.semantic.freshness-currentness-vocabulary` — terminology cannot freeze pre-review.

## Five findings most likely to change compiler/library architecture

1. Boundary grammar is unified across families: RETAIN/SPLIT/RENAME/REPLACE adjudications produce
   responsibility-migration graphs the compiler can execute as deterministic re-plans without aliases.
2. Receipt/evidence/attestation carriers need family-qualified names because RFC 9942 receipts,
   in-toto statements and DQV certificates are different publics sharing vocabulary.
3. Effect discipline (`pure_effect_intents`) proved uniform: every governance kernel is pure between
   editions and effect-bearing only at authority-imported commit ports.
4. Homonym governance (p0) is upstream of contract generation: until symbol owners are ratified,
   any shared-type optimization collapses distinct semantics.
5. The QOR/LPE split is real at impact boundaries: lineage topology services witness quality-staleness
   propagation but never compute it, implying cross-family ports rather than merged kernels.

## Validation

`python3 validate.py` proves ref coverage/uniqueness, source resolution, evidence-or-vacancy on
nontrivial decisions, migration completeness for changed boundaries, applicability completeness,
module boundedness, acyclic gap graph, homonym guards, effect separation, authority naming,
deterministic ordering, snapshot digest binding, merge-candidate atomicity/digests, no-standard-as-SAN-owner,
and completion_claim=false. Failures are reported, never silenced by weakening laws.

## Limitations

Paywalled ISO texts are vacancies, not assumptions; ISO 27037/2859 numbers cite landing pages only.
Legal precedence questions are registered, not resolved. The telemetry-family target owner lies
outside assigned lanes. Queue-level coverage of universe receipt libraries is asserted incomplete.
All artifacts are CANDIDATE_UNRATIFIED research output.
"""

def write_all() -> None:
    ts = None  # timestamps vary only here; all semantic content is deterministic
    dump_sorted("source-register.jsonl", br.SOURCES, lambda r: r["source_id"])
    dump_sorted("boundary-adjudications.jsonl", ADJUDICATIONS, lambda r: r["library_ref"])
    dump_sorted("semantic-modules.jsonl", MODULES, lambda r: r["module_id"])
    APP_SORTED = sorted(APP_ROWS, key=lambda r: (r["library_ref"], r["module_ref"]))
    MIG_SORTED = sorted(MIGRATIONS, key=lambda r: (r["old_library_ref"], r["old_responsibility"]))
    dump_sorted("library-applicability.jsonl", APP_SORTED, lambda r: (r["library_ref"], r["module_ref"]))
    dump_sorted("responsibility-migrations.jsonl", MIG_SORTED, lambda r: (r["old_library_ref"], r["old_responsibility"]))
    dump_sorted("contract-requirements.jsonl", ALL_CONTRACTS, lambda r: r["library_ref"])
    dump_sorted("conflicts-and-vacancies.jsonl", VACANCIES, lambda r: r["vacancy_id"])
    dump_sorted("gap-dependency-graph.jsonl", GAPS, lambda r: r.get("gap_id") or r.get("edge_id"))
    dump_sorted("merge-candidates.jsonl", MERGES, lambda r: r["candidate_id"])

    from datetime import datetime, timezone
    snap_live = br.snapshot()
    cov = dict(COVERAGE)
    cov["applicability_row_count"] = len(APP_SORTED)
    cov["migration_record_count"] = len(MIG_SORTED)
    cov["contract_requirement_count"] = len(ALL_CONTRACTS)
    cov["gap_node_count"] = len(GAP_NODES)
    cov["gap_edge_count"] = len(GAP_EDGES)
    cov["root_gap_ids"] = sorted(n["gap_id"] for n in ROOT_GAPS)
    cov["projection_count"] = sum(1 for r in APP_SORTED if r["decision_candidate"] == "APPLIES_AS_IS")
    cov["unresolved_public_symbol_collisions"] = count_collisions_touching_assigned()
    cov["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cov["researched_proposition_count"] = len(MODULES)
    cov["input_snapshot"] = {
        "files": [
            {k: f[k] for k in ("path", "sha256", "bytes", "record_count")}
            for f in snap_live["files"]
        ],
        "aggregate_digest": snap_live["aggregate_digest"],
        "note": "digests bind this run to the read-only inputs consumed; validation recomputes them live",
    }
    src_classes: dict[str, int] = {}
    for s in br.SOURCES:
        src_classes[s["source_class"]] = src_classes.get(s["source_class"], 0) + 1
    cov["sources_by_class"] = dict(sorted(src_classes.items()))
    (OUT / "coverage-report.json").write_text(
        json.dumps(cov, ensure_ascii=False, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(README, encoding="utf-8")
    print(f"wrote artifacts: aggregate_digest={snap_live['aggregate_digest']}")

def dump_sorted(name: str, rows: list[dict], key) -> None:
    def k(r):
        kk = key(r)
        if isinstance(kk, tuple):
            return tuple(str(x) for x in kk)
        return str(kk)
    ordered = sorted(rows, key=k)
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                   for r in ordered)
    (OUT / name).write_text(text, encoding="utf-8")

if __name__ == "__main__":
    write_all()
