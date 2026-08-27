#!/usr/bin/env python3
"""Laws for the frontier-accounting artifacts. Failures are reported, never silenced."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "frozen_inputs"
EXPECTED_PROGRAM_ATOMS = {"P01": 23, "P02": 210, "P03": 2805, "P04": 10784,
                          "P05": 674, "P06": 674, "P07": 1547}
LEGAL_PORTS = {
    "GATE_FAMILY_OWNER_ADJUDICATION", "GATE_SEMANTIC_OWNER_ADJUDICATION",
    "GATE_LIBRARY_OWNER_RATIFICATION", "GATE_VIA_P03_EVIDENCE_PACKAGE",
    "GATE_MODAL_RESEARCH_REQUIRED", "GATE_IMPLEMENTER_OFFERS",
    "GATE_INDEPENDENT_APPRAISER", "GATE_PRODUCT_ACCEPTANCE",
}


def rows(name):
    p = HERE / name
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n"), f"{name}: missing terminal newline"
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        r = json.loads(line)
        assert isinstance(r, dict)
        out.append(r)
    return out


def sorted_by(rs, key):
    ks = [str(r.get(key)) for r in rs]
    return ks == sorted(ks)


def main() -> int:
    f: list[str] = []
    snap = [json.loads(l) for l in (FROZEN / "gap-clusters.jsonl").read_text().splitlines()]
    total_atoms = sum(c["atom_count"] for c in snap)

    led = rows("frontier-ledger.jsonl")
    if len(led) != len(snap):
        f.append(f"ledger rows {len(led)} != clusters {len(snap)}")
    ids = [r["ledger_id"] for r in led]
    if len(ids) != len(set(ids)) or not sorted_by(led, "ledger_id"):
        f.append("ledger ids duplicated/unsorted")
    prog_atoms = Counter()
    for r in led:
        if r["exit_port"] not in LEGAL_PORTS:
            f.append(f"{r['ledger_id']}: illegal exit_port")
        if not r.get("required_receipt_kind") or not r.get("required_authority_role"):
            f.append(f"{r['ledger_id']}: missing authority/receipt wiring")
        if "CLOSED" in str(r["exit_port"]):
            f.append(f"{r['ledger_id']}: research lane may never emit CLOSED ports")
        prog_atoms[r["program_ref"]] += r["atom_count_snapshot"]
    for pg, n in EXPECTED_PROGRAM_ATOMS.items():
        if prog_atoms[pg] != n:
            f.append(f"program {pg} atoms {prog_atoms[pg]} != {n}")

    chs = rows("atom-chains.jsonl")
    cids = [r["chain_id"] for r in chs]
    if len(cids) != len(set(cids)):
        f.append("duplicate chain_id")
    weighted = sum(r["weight"] for r in chs)
    if weighted != total_atoms:
        f.append(f"Σ chain weights {weighted} != snapshot atoms {total_atoms}")
    cluster_ids = {r["cluster_id"] for r in led}
    per_cluster = Counter()
    for r in chs:
        if r["cluster_id"] not in cluster_ids:
            f.append(f"{r['chain_id']}: orphan cluster ref")
        if r["weight"] not in (0, 1):
            f.append(f"{r['chain_id']}: bad weight")
        if r["weight"] == 0 and not r.get("drift_flag"):
            f.append(f"{r['chain_id']}: zero-weight without drift flag")
        per_cluster[r["cluster_id"]] += r["weight"]
    by_cid = {c["cluster_id"]: c["atom_count"] for c in snap}
    for cid, n in per_cluster.items():
        if n != by_cid[cid]:
            f.append(f"{cid}: chained {n} != atoms {by_cid[cid]}")

    # frozen-input integrity
    man = json.loads((FROZEN / "manifest.json").read_text())
    for m in man["files"]:
        d = hashlib.sha256((FROZEN / m["frozen_name"]).read_bytes()).hexdigest()
        if d != m["sha256"]:
            f.append(f"frozen copy drifted: {m['frozen_name']}")

    p1 = rows("p01-authority-packets.jsonl")
    if len(p1) != 23:
        f.append(f"P01 packets {len(p1)} != 23")
    for r in p1:
        if not r.get("owner_decision_required") or r.get("gate") != "GATE_FAMILY_OWNER_ADJUDICATION":
            f.append(f"{r['packet_id']}: broken gate")
        for cand in r.get("candidate_authorities") or []:
            if cand.get("origin") == "INTERNET_VERIFIED_CANDIDATE" and not cand.get("uri"):
                f.append(f"{r['packet_id']}: internet candidate lacks uri")

    p2 = rows("p02-symbol-dispositions.jsonl")
    if len(p2) != 210:
        f.append(f"P02 recos {len(p2)} != 210")
    for r in p2:
        if r.get("recommendation", "").startswith("ENDORSE_"):
            if not r.get("collision_id") or not r.get("proposal_ref"):
                f.append(f"{r['reco_id']}: endorsement without proposal/collision link")

    p3 = rows("p03-axis-evidence-packs.jsonl")
    if len(p3) != 103:
        f.append(f"P03 packs {len(p3)} != 103")
    for r in p3:
        if not r["evidence_source_refs"] and not r["evidence_vacancies"]:
            f.append(f"{r['pack_id']}: neither evidence nor explicit vacancy")

    p4 = rows("p04-ratification-workplan.jsonl")
    if len(p4) != 368:
        f.append(f"P04 workplan {len(p4)} != 368")
    cnt = Counter(r["exit_port"] for r in p4)
    if cnt["GATE_LIBRARY_OWNER_RATIFICATION"] < 250:
        f.append("P04 ready-ratification ports suspiciously low")

    # dossier completeness law (Wave M1)
    fam_slugs = set()
    fd = HERE / "family_dossiers.json"
    if fd.exists():
        for e in json.loads(fd.read_text()):
            fam_slugs.add(e["family_slug"])
    wx = HERE / "waves" / "family_dossiers_extra.jsonl"
    if wx.exists():
        for line in wx.read_text().splitlines():
            if line.strip():
                fam_slugs.add(json.loads(line)["family_slug"])
    if len(fam_slugs) not in (0, 23):
        f.append(f"family dossier coverage {len(fam_slugs)}/23 — partial states forbidden")

    p3s = Counter(r["research_status"] for r in p3)
    scaffold_only = p3s.get("PACK_ASSEMBLED_FROM_VERIFIED_AXIS_TEMPLATE", 0) + \
                    p3s.get("TEMPLATE_SCAFFOLD_WITH_EXPLICIT_UNVERIFIED_SOURCE_VACANCIES", 0)
    if wx.exists() and scaffold_only:
        f.append(f"{scaffold_only} packs still template-only despite full dossier wave present")

    summ = json.loads((HERE / "frontier-summary.json").read_text())
    if summ["completion_claim"] is not False:
        f.append("frontier-summary must keep completion_claim=false")
    if summ["chain_weighted_atoms"] != weighted or summ["cluster_rows"] != len(led):
        f.append("frontier-summary inconsistent with artifacts")

    if f:
        print("FRONTIER VALIDATION FAILED")
        for x in f:
            print("-", x)
        return 1
    print("FRONTIER VALIDATOR PASSED")
    print(f"clusters={len(led)} programs={len(EXPECTED_PROGRAM_ATOMS)} "
          f"chains={len(chs)} weighted_atoms={weighted} (drift_zero_weight={sum(1 for r in chs if r['weight']==0)})")
    print(f"ports={dict(sorted(cnt_r for cnt_r in Counter(r['exit_port'] for r in led).items()))}")
    print("completion_claim=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
