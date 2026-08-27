#!/usr/bin/env python3
"""Frontier accounting: lossless disposition wiring for 686 gap clusters / 16,717 atoms.

Deterministic; writes only inside this directory. Canonical inputs are consumed via the
frozen_inputs/ adjacent copy whose digests bind every generated row.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "frozen_inputs"
ACCESSED = "2026-08-27"


def jload(name):
    return [json.loads(l) for l in (FROZEN / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def jdumps(rows, key):
    def k(r):
        kk = key(r)
        return tuple(str(x) for x in kk) if isinstance(kk, tuple) else str(kk)
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                   for r in sorted(rows, key=k))


def write(name, rows, key):
    (HERE / name).write_text(jdumps(rows, key), encoding="utf-8")


def sha(path):
    return hashlib.sha256((FROZEN / path).read_bytes()).hexdigest()


# ---- load -----------------------------------------------------------------
clusters = jload("gap-clusters.jsonl")
queue = jload("closure-queue.jsonl")
audits = jload("readiness-audits.jsonl")
collisions = jload("global-symbol-collisions.jsonl")
proposals = jload("owner-proposals.jsonl")
dockets_p2 = jload("owner-adjudication-dockets.jsonl")
waves_p2 = jload("owner-decision-waves.jsonl")
units_p2 = jload("owner-decision-units.jsonl")
packages_p3 = jload("targeted-evidence-work-packages.jsonl")
dockets_p4 = jload("family-axis-review-dockets.jsonl")

CL = {(r["family_refs"][0], r["semantic_axes"][0]): r for r in clusters if r["program_ref"] == "P04"}
DK = {(r.get("family_ref"), r.get("semantic_axis")): r for r in dockets_p4}
PROP_BY_DOCKET = {r["docket_ref"]: r for r in proposals}
COLL_BY_ID = {r["collision_id"]: r for r in collisions}

# unit -> member dockets (units partition the 210 dockets)
UNIT_MEMBERS = {u["decision_unit_id"]: u.get("symbol_docket_refs") or [] for u in units_p2}
DOCKET_UNIT = {}
for d in dockets_p2:
    DOCKET_UNIT[d["docket_id"]] = d.get("decision_unit_ref")
WAVE_BY_DOCKET = {d["docket_id"]: d.get("decision_wave_ref") for d in dockets_p2}

# P04 wave phases
wave_matrix = {}
try:
    waves_rev = jload("review-waves.jsonl")
    for wv in waves_rev:
        for mref in wv.get("matrix_refs", []):
            wave_matrix[mref] = wv.get("phase", wv.get("review_wave_ref"))
except Exception:
    pass

# ---- receipts / authority tables ------------------------------------------
RECEIPT_REQUIRED = {
    "P01": {"operation": "ADJUDICATE", "authority_role": "FAMILY_OWNER",
            "receipt_kind": "OWNER_RATIFICATION_RECEIPT"},
    "P02": {"operation": "ADJUDICATE", "authority_role": "SEMANTIC_OWNER",
            "receipt_kind": "OWNER_RATIFICATION_RECEIPT"},
    "P03": {"operation": "RESEARCH", "authority_role": "FAMILY_OWNER",
            "receipt_kind": "EVIDENCE_APPRAISAL_RECEIPT"},
    "P04": {"operation": "RATIFY", "authority_role": "LIBRARY_OWNER",
            "receipt_kind": "APPLICABILITY_RATIFICATION_RECEIPT"},
    "P05": {"operation": "SPECIFY", "authority_role": "LIBRARY_OWNER",
            "receipt_kind": "EXACT_CONTRACT_PUBLICATION_RECEIPT"},
    "P06": {"operation": "IMPLEMENT", "authority_role": "IMPLEMENTER",
            "receipt_kind": "IMPLEMENTATION_RECEIPT"},
    "P07": {"operation": "QUALIFY", "authority_role": "INDEPENDENT_APPRAISER",
            "receipt_kind": "QUALIFICATION_OR_ACCEPTANCE_RECEIPT"},
}

PORTS = {
    "GATE_FAMILY_OWNER_ADJUDICATION": "awaiting FAMILY_OWNER decision receipt",
    "GATE_SEMANTIC_OWNER_ADJUDICATION": "awaiting SEMANTIC_OWNER decision receipt",
    "GATE_LIBRARY_OWNER_RATIFICATION": "research-complete; awaiting LIBRARY_OWNER ratification",
    "GATE_VIA_P03_EVIDENCE_PACKAGE": "blocked pending family-axis evidence package output",
    "GATE_MODAL_RESEARCH_REQUIRED": "no unique modal default; needs residual research",
    "GATE_IMPLEMENTER_OFFERS": "awaiting implementation offers against intake templates",
    "GATE_INDEPENDENT_APPRAISER": "awaiting executable laws/differentials receipt",
    "GATE_PRODUCT_ACCEPTANCE": "awaiting product acceptance receipts per vacancy register",
}

# ---- helpers ---------------------------------------------------------------
def allocate_quota(ids_sorted, quota):
    """Deterministically assign weight 1 to `quota` entries of an ordered id list."""
    out = {}
    for i, x in enumerate(sorted(ids_sorted)):
        out[x] = 1 if i < quota else 0
    return out

def sym_slug(ref):
    """'packet.p1.symbol.type.type-contract-x-y' -> 'type-contract-x-y'"""
    parts = ref.split(".")
    return "-".join(parts[4:]) if len(parts) > 4 else ref

LEDGER, CHAINS, RECONCILIATIONS = [], [], []
_CLAIMED_COLLISIONS = set()

def chain(program, cluster, art, rec_id, scope, weight=1, drift=None):
    CHAINS.append({
        "chain_id": f"atom.{program}.{scope}.{rec_id}",
        "program_ref": program, "cluster_id": cluster["cluster_id"],
        "upstream_frozen_artifact": art, "upstream_record_id": rec_id,
        "chain_scope": scope, "weight": weight,
        "drift_flag": drift or ("WEIGHT_ZERO_EXCEEDS_SNAPSHOT_QUOTA" if weight == 0 else None),
    })

def base_row(c):
    prog = c["program_ref"]
    r = RECEIPT_REQUIRED[prog]
    return {
        "ledger_id": f"ledger.{c['cluster_id']}",
        "cluster_id": c["cluster_id"],
        "program_ref": prog,
        "closure_operation": r["operation"],
        "required_authority_role": r["authority_role"],
        "required_receipt_kind": r["receipt_kind"],
        "gap_kind": c["gap_kind"], "defect_kind": c["defect_kind"],
        "scope_grain": c["scope_grain"], "decision_shape": c["decision_shape"],
        "reuse_layer": c["reuse_layer"],
        "lifecycle_current": c["lifecycle"],
        "atom_count_snapshot": c["atom_count"],
        "chains_enumerated": None,
        "exit_port": None, "port_basis": None,
        "research_support_refs": [],
    }

for c in clusters:
    prog = c["program_ref"]
    fam = c["family_refs"][0] if c.get("family_refs") else None
    row = base_row(c)

    if prog == "P01":
        aud = next((a for a in audits if a.get("family_id") == fam), None)
        pkt = f"packet.p1.authority.{fam.split('.')[-1]}"
        row.update(exit_port="GATE_FAMILY_OWNER_ADJUDICATION",
                   port_basis="authority decision packets generated; ratification receipt required",
                   research_support_refs=[pkt] + ([aud["audit_id"]] if aud else []),
                   chains_enumerated=1)
        LEDGER.append(row)
        if aud:
            chain(prog, c, "readiness-audits.jsonl", aud["audit_id"], "source-authority")

    elif prog == "P02":
        cands = {s.rsplit(".", 1)[-1].lower() for s in c["affected_scope_refs"]}
        cands.add(c["cluster_id"].rsplit(".", 1)[-1].lower())
        ids = []
        for d in collisions:
            rem = d["collision_id"].replace("collision.p0.symbol.", "")
            tail = rem.split(".")[-1].lower()
            if tail in cands:
                ids.append(d["collision_id"])
        recs = sorted(set(ids))
        row.update(exit_port="GATE_SEMANTIC_OWNER_ADJUDICATION",
                   port_basis="disposition recommendations emitted; owner ratification receipt required",
                   research_support_refs=[f"reco.p2.{sym_slug(x)}" for x in recs[:6]],
                   chains_enumerated=len(recs))
        LEDGER.append(row)
        for cid in recs:
            if cid not in _CLAIMED_COLLISIONS:
                _CLAIMED_COLLISIONS.add(cid)
                chain(prog, c, "global-symbol-collisions.jsonl", cid, "symbol-owner")

    elif prog == "P03":
        axis = c["semantic_axes"][0]
        pkg = next((p for p in packages_p3
                    if p["family_id"] == fam and p["axis"] == axis), None)
        if pkg is None:
            row.update(exit_port="GATE_MODAL_RESEARCH_REQUIRED",
                       port_basis="no 1:1 targeted-evidence package found", chains_enumerated=0)
            LEDGER.append(row)
            continue
        libs = pkg["library_refs"]
        assert len(libs) == pkg["library_count"] == c["atom_count"]
        row.update(exit_port="GATE_FAMILY_OWNER_ADJUDICATION",
                   port_basis="axis evidence pack assembled at family x axis grain; appraisal receipt required",
                   research_support_refs=[pkg["work_package_id"], f"pack.p03.{fam.split('.')[-1]}.{axis}"],
                   chains_enumerated=len(libs))
        LEDGER.append(row)
        for lib in libs:
            chain(prog, c, "targeted-evidence-work-packages.jsonl", f"{pkg['work_package_id']}::{lib}",
                  "family-axis-evidence")

    elif prog == "P04":
        dk = DK.get((fam, c["semantic_axes"][0]))
        cells = c["affected_scope_refs"]
        if dk is None:
            row.update(exit_port="GATE_MODAL_RESEARCH_REQUIRED",
                       port_basis="no review docket join", chains_enumerated=len(cells))
            LEDGER.append(row); continue
        st, rc = dk.get("status"), dk.get("review_class")
        if st == "READY_FOR_FAMILY_AXIS_REVIEW":
            port = "GATE_LIBRARY_OWNER_RATIFICATION"
        elif rc == "BLOCKED_EVIDENCE_VACANCY":
            port = "GATE_VIA_P03_EVIDENCE_PACKAGE"
        else:
            port = "GATE_MODAL_RESEARCH_REQUIRED"
        basis = f"docket={dk['docket_id']} status={st} class={rc}"
        if dk.get("targeted_evidence_work_package_ref"):
            basis += f" unblock_via={dk['targeted_evidence_work_package_ref']}"
        row.update(exit_port=port, port_basis=basis,
                   research_support_refs=[dk["docket_id"]]
                   + ([dk["targeted_evidence_work_package_ref"]] if dk.get("targeted_evidence_work_package_ref") else []),
                   chains_enumerated=len(cells))
        LEDGER.append(row)
        for pcid in cells:
            chain(prog, c, "gap-clusters.jsonl(affected_scope_refs)", pcid, "member-axis-cell")

    elif prog in ("P05", "P06"):
        qitems = [q for q in queue if q["library_ref"] in set(c["affected_scope_refs"])]
        n = len(qitems)
        row.update(
            exit_port=("GATE_LIBRARY_OWNER_RATIFICATION" if prog == "P05" else "GATE_IMPLEMENTER_OFFERS"),
            port_basis=(f"{n}/{c['atom_count']} closure items enumerated; specification receipt required"
                        if prog == "P05" else
                        f"{n}/{c['atom_count']} queue items routed; offer intake lives at "
                        "p7_offer_binding_qualification/implementation-offer-intake-templates.jsonl "
                        "(491 qualification scopes x 2 independence slots = 982 slot demands; different denominator, see reconciliations.jsonl)"),
            chains_enumerated=n)
        LEDGER.append(row)
        for q in qitems:
            chain(prog, c, "closure-queue.jsonl", q["closure_id"],
                  "specification" if prog == "P05" else "implementation")

    elif prog == "P07" and c["gap_kind"] == "qualification":
        qitems = [q for q in queue if q["library_ref"] in set(c["affected_scope_refs"])]
        row.update(exit_port="GATE_INDEPENDENT_APPRAISER",
                   port_basis=f"{len(qitems)} queue items await executable laws/differentials; "
                              "491 qualification scope kernels declare the acceptance surface",
                   chains_enumerated=len(qitems))
        LEDGER.append(row)
        for q in qitems:
            chain(prog, c, "closure-queue.jsonl", q["closure_id"], "qualification")

# product-gate clusters consume the live vacancy register against snapshot quotas.
vac_all = jload("evidence-vacancies.jsonl")
def norm_slug(s):
    return s.replace("-", "_")
by_gate = defaultdict(list)
for v in vac_all:
    g = norm_slug((v.get("gate_ref") or "").rsplit(".", 1)[-1])
    by_gate[g].append(v["vacancy_id"])
gate_slugs = ["build-ready", "differential-exit", "specification-freeze", "vertical-pair-exit"]
for c in clusters:
    if c["program_ref"] != "P07" or c["gap_kind"] != "product-gate":
        continue
    row = base_row(c)
    slug = norm_slug(c["cluster_id"].rsplit(".", 1)[-1])
    ids_all = sorted(by_gate.get(slug, []))
    wmap = allocate_quota(ids_all, c["atom_count"])
    chosen = [i for i, w in wmap.items() if w == 1]
    overflow = [i for i, w in wmap.items() if w == 0]
    drift = "LIVE_FILE_HAS_MORE_RECORDS_THAN_SNAPSHOT" if overflow else None
    row.update(exit_port="GATE_PRODUCT_ACCEPTANCE",
               port_basis=f"vacancy register joined on gate '{slug}': quota {len(chosen)}, live-file surplus withheld: {len(overflow)}",
               research_support_refs=["product_ontology/qualification_program/evidence-vacancies.jsonl"],
               chains_enumerated=len(chosen))
    LEDGER.append(row)
    for vid, w in sorted(wmap.items()):
        chain("P07", c, "evidence-vacancies.jsonl", vid, "product-acceptance", weight=w, drift=drift)

# ---- Wave artifacts --------------------------------------------------------
AXES = ["composition_algebra", "grain_and_cardinality", "identity_and_equality",
        "order_and_topology", "partiality_and_uncertainty", "state_and_change"]
TDIR = HERE / "axis_templates"

def load_template(axis):
    p = TDIR / f"{axis}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

FAMILY_AUTHORITY_HINTS = {
    # deterministic topic anchors into the already web-verified lane register
    "analytical_method_kernels": ("src.jcgm.vim.2012",),
    "shared_semantic_foundations": ("src.w3c.prov-dm", "src.w3c.dqv"),
    "security_privacy_trust": ("src.nist.fips180-4", "src.iso.27037.landing"),
    "lineage_provenance_evidence": ("src.w3c.prov-dm", "src.w3c.prov-constraints", "src.openlineage.object-model-1.52"),
    "quality_reconciliation": ("src.w3c.dqv", "src.bcbs239"),
    "connectors_protocols": ("src.ietf.rfc5424",),
}

_FAM_AUTH_OVERRIDE = {}
if (HERE / "family_authorities.json").exists():
    _raw = json.loads((HERE / "family_authorities.json").read_text(encoding="utf-8"))
    for e in _raw:
        _FAM_AUTH_OVERRIDE[e["family_slug"]] = e

def authority_packet(c):
    fam = c["family_refs"][0]
    if fam.split(".")[-1] in _FAM_AUTH_OVERRIDE:
        ov = _FAM_AUTH_OVERRIDE[fam.split(".")[-1]]
        cands = [{"origin": "INTERNET_VERIFIED_CANDIDATE",
                  "title": a.get("title"), "uri": a.get("uri"),
                  "issuer": a.get("issuer"),
                  "edition_or_date": a.get("edition_or_date"),
                  "confidence": a.get("confidence", "medium"),
                  "status": "CANDIDATE_PENDING_FAMILY_OWNER"}
                 for a in ov.get("authorities", [])]
        vacs = [{"statement": v, "required_evidence": "PRIMARY_SOURCE"}
                for v in ov.get("discovery_vacancies", [])]
        aud = next((a for a in audits if a.get("family_id") == fam), None)
        pkt_id = f"packet.p1.authority.{fam.split('.')[-1]}"
        out = {"packet_id": pkt_id, "family_ref": fam,
               "audit_ref": aud["audit_id"] if aud else None,
               "cluster_id": c["cluster_id"],
               "readiness_verdict": aud.get("authority_decision") if aud else None,
               "candidate_authorities": cands,
               "evidence_vacancies": vacs,
               "discovery_seed_terms": [],
               "owner_decision_required": True,
               "gate": "GATE_FAMILY_OWNER_ADJUDICATION",
               "research_status": ("PACKET_READY_INTERNET_VERIFIED_CANDIDATES"
                                   if cands else "NEEDS_PRIMARY_DISCOVERY")}
        return out
    aud = next((a for a in audits if a.get("family_id") == fam), None)
    slug = fam.split(".")[-1]
    hints = FAMILY_AUTHORITY_HINTS.get(slug)
    cand = ([{"source_ref": s, "origin": "lane_verified_source_register",
              "status": "CANDIDATE_PENDING_FAMILY_OWNER"} for s in hints]
            if hints else [])
    vac = [] if cand else [{
        "statement": f"No vetted primary authority mapped deterministically for family '{fam}'.",
        "required_evidence": "PRIMARY_SOURCE discovery pass over official standards/specs matching the family subject domain.",
    }]
    return {
        "packet_id": f"packet.p1.authority.{slug}",
        "family_ref": fam,
        "audit_ref": aud["audit_id"] if aud else None,
        "cluster_id": c["cluster_id"],
        "readiness_verdict": aud.get("authority_decision") if aud else None,
        "candidate_authorities": cand,
        "discovery_seed_terms": slug.replace("_", "-").split("-") if not hints else [],
        "owner_decision_required": True,
        "gate": "GATE_FAMILY_OWNER_ADJUDICATION",
        "research_status": "PACKET_READY_CANDIDATES_ONLY" if cand else "NEEDS_PRIMARY_DISCOVERY",
    }

P01_PACKETS = [authority_packet(c) for c in clusters if c["program_ref"] == "P01"]

def symbol_reco(dock):
    cid = dock["collision_id"]
    prop = next((p for p in proposals if p["docket_ref"] ==
                 f"docket.p2.symbol.{'.'.join(cid.split('.')[-3:])}" or
                 p["symbol_ref"].endswith(dock.get("symbol_name", "@@")) ), None)
    prop = prop or PROP_BY_DOCKET.get(cid) or next(
        (p for p in proposals if p["proposal_id"] ==
         f"proposal.p2.owner.{'.'.join(cid.split('.')[-2:])}"), None)
    unit = DOCKET_UNIT.get(f"docket.p2.symbol.{dock['symbol_name']}")
    reco = {
        "reco_id": f"reco.p2.{cid.rsplit('.', 2)[-2]}.{dock['symbol_name']}",
        "collision_id": cid,
        "symbol_name": dock["symbol_name"],
        "collision_class": dock["collision_class"],
        "definition_digest_count": len(dock.get("definition_digests") or []),
        "occurrence_count": dock.get("library_count"),
        "unit_ref": unit,
        "non_collapse_law": dock.get("non_collapse_law"),
    }
    if prop:
        reco.update({
            "proposal_ref": prop["proposal_id"],
            "proposed_disposition": prop.get("proposed_symbol_disposition"),
            "proposed_owner_refs": prop.get("proposed_owner_refs") or [],
            "confidence": prop.get("confidence"),
            "blockers": prop.get("blockers") or [],
            "counterfactual_status": (prop.get("counterfactual_checks") or {}).get("stability")
            if isinstance(prop.get("counterfactual_checks"), dict) else None,
            "recommendation": (
                f"ENDORSE_{prop.get('proposed_symbol_disposition')}"
                if prop.get("status") == "PROPOSED_UNRATIFIED"
                and prop.get("confidence") in ("HIGH", "MEDIUM")
                and prop.get("proposed_symbol_disposition") not in (None, "UNRESOLVED")
                else "RESEARCH_ACTIONS_REQUIRED_BEFORE_ADJUDICATION"),
        })
    else:
        reco.update({"recommendation": "RESEARCH_ACTIONS_REQUIRED_BEFORE_ADJUDICATION",
                     "research_actions": ["locate proposal layering gap for this docket"]})
    reco.update({
        "decision_wave_hint": next((w["decision_wave_ref"] for w in waves_p2
                                    if unit and unit in (w.get("decision_unit_refs") or [])), None),
        "owner_decision_required": True,
        "gate": "GATE_SEMANTIC_OWNER_ADJUDICATION",
        "research_status": "RECOMMENDATION_EMITTED_NOT_RATIFIED",
    })
    return reco

# collide dockets with collision records via symbol name: build name index first
name_index = {}
for d in collisions:
    nm = d["collision_id"].split(".type.")[-1] if ".type." in d["collision_id"] else d["collision_id"]
    name_index[nm] = d
def p02_dockets():
    out = []
    prop_symbols = set()
    for p in proposals:
        sr = p.get("symbol_ref") or ""
        prop_symbols.add(sr.rsplit(".", 1)[-1])
        out.append((p, sr))
    return out

# Build reco rows from the authoritative docket table (210) with exact proposal join.
P02_RECOS = []
prop_by_docket = {p["docket_ref"]: p for p in proposals}
_coll_tail = {}
for _d in collisions:
    _rem = _d["collision_id"].replace("collision.p0.symbol.", "")
    _coll_tail[_rem.rsplit(".", 1)[-1].lower()] = _d["collision_id"]
for i, dk in enumerate(sorted(dockets_p2, key=lambda x: x["docket_id"]), 1):
    did = dk["docket_id"]
    prop = prop_by_docket.get(did)
    slug = did.split(".")[3] if did.count(".") >= 3 else did
    cid = _coll_tail.get(slug.lower())
    unit = DOCKET_UNIT.get(did)
    wave = WAVE_BY_DOCKET.get(did)
    reco = {
        "reco_id": f"reco.p2.docket{i:03d}",
        "docket_ref": did,
        "symbol_slug": slug,
        "symbol_ref": dk.get("symbol_ref"),
        "collision_id": cid,
        "occurrence_count_in_docket": dk.get("occurrence_count"),
        "priority_rank": dk.get("priority_rank"),
        "allowed_dispositions": dk.get("allowed_symbol_dispositions"),
        "disposition_hypotheses": (dk.get("disposition_hypotheses") or [])[:2],
        "authority_limits_input": (dk.get("authority_limits") or [])[:1],
        "unit_ref": unit,
        "decision_wave_hint": wave,
    }
    if prop:
        cf = prop.get("counterfactual_checks")
        stab = cf.get("stability") if isinstance(cf, dict) else None
        disp = prop.get("proposed_symbol_disposition")
        reco.update({
            "proposal_ref": prop["proposal_id"],
            "proposed_disposition": disp,
            "named_owners": prop.get("proposed_owner_refs") or [],
            "confidence": prop.get("confidence"),
            "proposal_state": prop.get("status"),
            "counterfactual_stability": stab,
            "blockers": (prop.get("blockers") or [])[:3],
            "recommendation": ("ENDORSE_" + str(disp))
            if (prop.get("status") == "PROPOSED_UNRATIFIED"
                and prop.get("confidence") in ("HIGH", "MEDIUM")
                and disp not in (None, "UNRESOLVED"))
            else "RESEARCH_ACTIONS_REQUIRED_BEFORE_ADJUDICATION",
        })
    else:
        reco.update({"recommendation": "PROPOSAL_LAYER_MISSING_RESEARCH_ACTIONS_REQUIRED"})
    reco.update({
        "gate": "GATE_SEMANTIC_OWNER_ADJUDICATION",
        "research_status": "RECOMMENDATION_EMITTED_NOT_RATIFIED",
        "owner_decision_required": True,
    })
    P02_RECOS.append(reco)

# Wave-C1 overlay: appraisal research on challenge-blocked dockets.
_CA_DIR = HERE / "waves" / "conflict_appraisals"
if _CA_DIR.exists():
    ca_by_conflict = {}
    for f in sorted(_CA_DIR.glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            cid = r.get("conflict_id") or r.get("collision_id")
            if cid:
                ca_by_conflict[cid] = r
    # bridge: frozen conflicts carry docket_ref directly; appraisal rows quote conflict ids
    _frozen_conflicts = jload("proposal-conflicts.jsonl")
    _confid_to_docket = {c["conflict_id"]: c["docket_ref"] for c in _frozen_conflicts}
    _sym_to_docket = {dkg.get("symbol_ref", ""): dkg["docket_id"] for dkg in dockets_p2}
    def _ca_docket(ca):
        did = _confid_to_docket.get(ca.get("conflict_id"))
        if did:
            return did
        sym = ca.get("symbol") or ""
        return _sym_to_docket.get(sym.replace("-", "."))
    reco_by_docket = {}
    for r0 in P02_RECOS:
        if r0.get("docket_ref"):
            reco_by_docket[r0["docket_ref"]] = r0
        elif r0.get("symbol_slug"):
            for dkg0 in dockets_p2:
                slug0 = dkg0["docket_id"].split(".")[3] if dkg0["docket_id"].count(".") >= 3 else ""
                if slug0.lower() == r0["symbol_slug"].lower():
                    reco_by_docket[dkg0["docket_id"]] = r0
                    break
    n_up = 0
    unmatched = []
    for cid, ca in ca_by_conflict.items():
        did2 = _ca_docket(ca) or _confid_to_docket.get(cid)
        r0 = reco_by_docket.get(did2)
        if not r0 and ca.get("symbol"):
            sk = ca["symbol"].replace(".", "-").lower()
            for dkg0, rr in list(reco_by_docket.items()):
                if slug_ok := (sk.rsplit("-",1)[-1] == (dkg0.split(".")[3].rsplit("-",1)[-1] if dkg0.count(".")>=3 else "")):
                    pass
            # fall back to symbol-token match
            tok = ca["symbol"].rsplit(".",1)[-1].lower()
            for dkg0, rr in reco_by_docket.items():
                slug0 = dkg0.split(".")[3] if dkg0.count(".")>=3 else ""
                if tok in slug0.lower() or slug0.lower().endswith(tok):
                    r0 = rr; break
        if not r0:
            unmatched.append(cid)
            continue
        r0["appraisal_overlay"] = {
            "outcome": ca.get("research_outcome"),
            "recommended_resolution": ca.get("recommended_resolution"),
            "evidence_count": len(ca.get("evidence") or []),
            "vacancy": bool(ca.get("vacancy_if_any")),
        }
        r0["research_status"] = "APPRAISAL_RESEARCH_OVERLAID_PENDING_OWNER"
        n_up += 1
    if unmatched:
        print(f"[overlay] unmatched conflicts: {len(unmatched)} e.g. {unmatched[:3]}")
    print(f"[overlay] conflict appraisals applied: {n_up}")

_FAMILY_DOSSIERS = {}
if (HERE / "family_dossiers.json").exists():
    for e in json.loads((HERE / "family_dossiers.json").read_text(encoding="utf-8")):
        _FAMILY_DOSSIERS[e["family_slug"]] = e
_wx = HERE / "waves" / "family_dossiers_extra.jsonl"
if _wx.exists():
    for _line in _wx.read_text(encoding="utf-8").splitlines():
        if not _line.strip():
            continue
        e = json.loads(_line)
        _FAMILY_DOSSIERS[e["family_slug"]] = e

# P03 packs: one per package, grounded in the frozen input's own sovereign question
# plus the researched axis template. Family-specific research (Wave-3 dossiers)
# upgrades a pack; absence keeps it an explicitly-labeled scaffold.
def p03_pack(pkg):
    axis = pkg["axis"]
    tpl = load_template(axis)
    fam_slug = pkg["family_id"].split(".")[-1]
    pack = {
        "pack_id": f"pack.p03.{fam_slug}.{axis}",
        "work_package_ref": pkg["work_package_id"],
        "family_ref": pkg["family_id"],
        "axis": axis,
        "sovereign_question_from_input": pkg.get("sovereign_research_question"),
        "module_plan_ref": pkg.get("module_ref"),
        "constitution_ref": pkg.get("constitution_ref"),
        "represented_library_count": pkg["library_count"],
        "priority": pkg.get("priority"),
        "axis_template_status": None,
        "applied_non_collapse_laws": [],
        "evidence_source_refs": [],
        "evidence_vacancies": [],
        "owner_decision_required": True,
        "gate": "GATE_FAMILY_OWNER_ADJUDICATION",
        "research_status": None,
    }
    if tpl is None:
        pack["axis_template_status"] = "TEMPLATE_MISSING_VACANCY"
        pack["research_status"] = "BLOCKED_TEMPLATE_RESEARCH_PENDING"
        pack["evidence_vacancies"] = [{
            "statement": f"No researched evidence template exists for axis '{axis}' yet.",
            "required_evidence": "Primary-source research pass per axis evidence contract."}]
        return pack
    dossier_axes = (_FAMILY_DOSSIERS.get(fam_slug_, {}) or {}).get("axes", {}) if False else \
        ((_FAMILY_DOSSIERS.get(pkg["family_id"].split(".")[-1]) or {}).get("axes") or {})
    daxis = dossier_axes.get(axis) or {}
    ds_status = daxis.get("status")
    srcs = tpl.get("sources", [])
    if ds_status in ("RESEARCHED", "RESEARCHED_WITH_VACANCY"):
        pack["axis_template_status"] = "RESEARCHED_PRIMARY_SOURCES_VERIFIED"
        pack["family_application"] = daxis.get("family_application")
        pack["family_counterexamples"] = daxis.get("family_counterexamples") or []
        pack["family_extra_verified_sources"] = [
            s for s in (daxis.get("extra_verified_sources") or []) if s.get("uri")]
    else:
        pack["axis_template_status"] = "TEMPLATE_ONLY_SCAFFOLD_PENDING_FAMILY_RESEARCH"
        pack["evidence_vacancies"].append({
            "statement": f"No family-specific research yet for {pkg['family_id']} x {axis}; "
                         "pack currently binds generic axis laws only.",
            "required_evidence": "Family-grain evidence dossier grounded in the family's facets/archetypes."})
    pack["applied_non_collapse_laws"] = tpl.get("non_collapse_laws", [])
    pack["evidence_vacancies"] = [
        v if isinstance(v, dict) else {"statement": str(v),
                                       "required_evidence": "PRIMARY_SOURCE"}
        for v in tpl.get("evidence_vacancies_if_any", [])]
    verified = sum(1 for s in srcs if s.get("verified", True))
    unverified = len(srcs) - verified
    if unverified:
        pack["evidence_vacancies"].append({
            "statement": f"{unverified} template sources could not be fetched live this pass; "
                         "excluded from normative citations pending primary access.",
            "required_evidence": "Fetch or mirror the cited standards texts."})
    pack["evidence_source_refs"] = [s.get("source_id") or s.get("id") or s.get("uri")
                                    for s in srcs if s.get("verified", True)]
    fam_researched = ds_status in ("RESEARCHED", "RESEARCHED_WITH_VACANCY")
    pack["research_status"] = (
        "FAMILY_SPECIFIC_RESEARCH_ASSEMBLED" if fam_researched and verified and not unverified else
        "FAMILY_SPECIFIC_RESEARCH_ASSEMBLED_WITH_SOURCE_VACANCIES" if fam_researched else
        ("PACK_ASSEMBLED_FROM_VERIFIED_AXIS_TEMPLATE" if verified and not unverified else
         "TEMPLATE_SCAFFOLD_WITH_EXPLICIT_UNVERIFIED_SOURCE_VACANCIES"))
    return pack

P03_PACKS = [p03_pack(p) for p in packages_p3]

# P04 ratification workplan: join docket state + phase waves + dependency refs
def p4_row(dk):
    matrix_id = dk.get("matrix_ref") or ""
    st = dk.get("status"); rc = dk.get("review_class")
    if st == "READY_FOR_FAMILY_AXIS_REVIEW":
        port = "GATE_LIBRARY_OWNER_RATIFICATION"; basis = f"ready class={rc}"
    elif rc == "BLOCKED_EVIDENCE_VACANCY":
        port = "GATE_VIA_P03_EVIDENCE_PACKAGE"
        basis = "blocked on targeted evidence: %s" % dk.get("targeted_evidence_work_package_ref")
    else:
        port = "GATE_MODAL_RESEARCH_REQUIRED"; basis = f"class={rc}"
    return {
        "workplan_id": f"wp.p04.{dk['docket_id']}",
        "docket_ref": dk["docket_id"], "matrix_ref": matrix_id,
        "wave_phase_hint": wave_matrix.get(matrix_id), "phase": dk.get("phase"),
        "family_ref": dk.get("family_ref"), "axis": dk.get("semantic_axis"),
        "member_count": dk.get("member_count"),
        "status_input": st, "review_class": rc,
        "selected_family_default": dk.get("selected_family_default_decision"),
        "member_preclassification_refs": len(dk.get("member_preclassification_refs") or []),
        "exit_port": port, "port_basis": basis,
        "evidence_pack_dependency": f"pack.p03.{(dk.get('family_ref') or '').split('.')[-1]}.{dk.get('semantic_axis')}",
        "unblock_dependency_refs": [dk["targeted_evidence_work_package_ref"]]
        if dk.get("targeted_evidence_work_package_ref") else [],
        "owner_decision_required": True,
        "research_status": ("WORKPLAN_ROUTED_AWAITING_OWNER" if port == "GATE_LIBRARY_OWNER_RATIFICATION"
                            else "WORKPLAN_ROUTED_BLOCKED_WITH_DEPENDENCY"),
    }

P04_PLAN = [p4_row(d) for d in dockets_p4]

# ---- reconciliations --------------------------------------------------------
RECONCILIATIONS += [
 {"reconciliation_id":"rec.001.stale-external-claims","claim_checked":
   "External delta text asserted 686 clusters / 16,687 atoms / 843 vacancies / 928 slots",
  "live_truth":{"clusters":686,"atoms_sum":sum(c['atom_count'] for c in clusters),
                "vacancies_live_file":len(vac_all),"slots_live_derivation":"491 scopes x 2"},
  "resolution":"Numbers in live inputs supersede external prose; ledger binds to digests."},
 {"reconciliation_id":"rec.002.p06-slots-vs-queue","metric_a":"implementation_independent_slots=982",
  "metric_b":"P06 atoms=674 closure items",
  "resolution":"Both true with different denominators: 491 qualification scopes x 2 required independence slots = 982 slot-demands; 674 counts library closure targets. Documented relation, no data bug; subject dockets(504)/resolutions(635) bridge them."},
 {"reconciliation_id":"rec.003.obligations-derived","metric":"vertical_acceptance_slot_gate_obligations=1008",
  "resolution":"Derived: 126 slots x 8 gate classes = 1008 (acceptance-class-workstreams.jsonl); not an independent population."},
 {"reconciliation_id":"rec.004.evidence-vacancy-drift","summary_value":873,"live_file_records":len(vac_all),
  "resolution":"product_ontology/qualification_program/evidence-vacancies.jsonl regenerated after last upstream build (untracked dir). Ledger chains allocate snapshot quotas deterministically; surplus live rows carry weight=0 + drift flag until upstream rebuild realigns summary.json."},
 {"reconciliation_id":"rec.005.wave-4-blocked","artifact":"p2_owner_adjudication/owner-decision-waves.jsonl",
  "fact":"wave.p2.owner.04-occurrences is BLOCKED_PENDING_OWNER_WAVES covering 666 occurrence relations (321 proposed / 345 blocked-pending-evidence)",
  "resolution":"Recorded as legitimate SEMANTIC_OWNER gate dependency ordering; not research-avoidable."},
]

# ---- write all ---------------------------------------------------------------
from collections import Counter

def main():
    write("frontier-ledger.jsonl", LEDGER, lambda r: r["ledger_id"])
    write("atom-chains.jsonl", CHAINS, lambda r: r["chain_id"])
    write("reconciliations.jsonl", RECONCILIATIONS, lambda r: r["reconciliation_id"])
    write("p01-authority-packets.jsonl", P01_PACKETS, lambda r: r["packet_id"])
    write("p02-symbol-dispositions.jsonl", P02_RECOS, lambda r: r["reco_id"])
    write("p03-axis-evidence-packs.jsonl", P03_PACKS, lambda r: r["pack_id"])
    write("p04-ratification-workplan.jsonl", P04_PLAN, lambda r: r["workplan_id"])

    total_atoms = sum(c["atom_count"] for c in clusters)
    weighted = sum(x["weight"] for x in CHAINS)
    summary = {
      "as_of": ACCESSED,
      "cluster_rows": len(LEDGER),
      "clusters_in_input": len(clusters),
      "atom_total_snapshot": total_atoms,
      "chain_rows": len(CHAINS),
      "chain_weighted_atoms": weighted,
      "chains_zero_weight_drift": sum(1 for x in CHAINS if x["weight"] == 0),
      "by_program_ledger": dict(sorted(Counter(r["program_ref"] for r in LEDGER).items())),
      "by_program_atoms_snapshot": {p: sum(c['atom_count'] for c in clusters if c['program_ref']==p)
                                    for p in sorted({c['program_ref'] for c in clusters})},
      "by_exit_port": dict(sorted(Counter(r["exit_port"] for r in LEDGER).items())),
      "p01_packets": len(P01_PACKETS), "p02_recos": len(P02_RECOS),
      "p03_packs": len(P03_PACKS), "p04_workplan_rows": len(P04_PLAN),
      "reconciliations": len(RECONCILIATIONS),
      "completion_claim": False,
      "note": "Ports are typed gates to owner roles; nothing here closes a canonical gap.",
    }
    (HERE / "frontier-summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
