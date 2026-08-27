#!/usr/bin/env python3
"""One-shot B04 source materializer; deleted by the generated commit."""
from __future__ import annotations
import base64, hashlib, io, json, shutil, tarfile
from pathlib import Path

EXPECTED = json.loads('[{"path":"research/analytics_landscape/product_families/README.md","sha256":"08e620a462c935b8819652d381702ada30dc1279e3ff7e426aa999d5b0fea48e","size":4030},{"path":"research/analytics_landscape/product_families/build_evidence_governance.py","sha256":"6007563619214835832dd148171102fafb1ac7fd46ddd30fb5229c54d67539a4","size":23544},{"path":"research/analytics_landscape/product_families/build_evidence_upgrade_campaigns.py","sha256":"197ee7ad5bd419cae1a32fc8f515801af460f4dc2038f38e67c7e6be586c4a96","size":7675},{"path":"research/analytics_landscape/product_families/consolidation-hardening-audit.jsonl","sha256":"efb179f77226c69d3c3106c21bd228f652f7ce8a855f9a649802990109b63cad","size":6066},{"path":"research/analytics_landscape/product_families/evidence-governance-policy.json","sha256":"e2c038cc1646ba78399aff8a3d8ba27666debcebccc67febbebc6ce13df50543","size":11772},{"path":"research/analytics_landscape/product_families/evidence-governance.schema.json","sha256":"b03dce52ba7e4cb8f93da5aba46e5226f2e7250c7b7d181acb522ab3b1ee2d92","size":10720},{"path":"research/analytics_landscape/product_families/manifest.json","sha256":"8072593611d814b827768ecb480be7b9cf3c069f901f6bc221891f78768b50ad","size":3698},{"path":"research/analytics_landscape/product_families/validate_evidence_governance.py","sha256":"8bd264909d2be56fdbb7729330b1756153dff7fcd23bbde5ac1b2430cf6cb370","size":15605},{"path":"research/analytics_landscape/product_families/validate_evidence_upgrade_campaigns.py","sha256":"4e8fe2341aead5ac6eb6aa52877d4c76008357ac2e8fe1afdf1864f473431e66","size":4022}]')
ROOT = Path.cwd().resolve()
PARTS = ROOT / ".github" / "b04-hardening-payload"
payload = "".join(path.read_text(encoding="utf-8") for path in sorted(PARTS.glob("part-*.txt")))
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(payload)), mode="r:gz") as archive:
    for member in archive.getmembers():
        target = (ROOT / member.name).resolve()
        if ROOT not in target.parents:
            raise SystemExit("unsafe archive member: " + member.name)
    archive.extractall(ROOT)
for row in EXPECTED:
    path = ROOT / row["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
        raise SystemExit("payload digest mismatch: " + row["path"])
for obsolete in (
    ROOT / ".github" / "b04-payload",
    ROOT / ".github" / "bootstrap-horizontal-evidence-governance.py",
    ROOT / "research" / "analytics_landscape" / "product_families" / "b04-hardening-run-request.json",
):
    if obsolete.is_dir():
        shutil.rmtree(obsolete)
    elif obsolete.exists():
        obsolete.unlink()
shutil.rmtree(PARTS)
Path(__file__).unlink()
print("PASS materialized 9 B04 source files and removed bootstrap debris")
