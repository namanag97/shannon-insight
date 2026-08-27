#!/usr/bin/env python3
"""One-shot branch bootstrap; removed by the generated commit."""
from __future__ import annotations
import base64, hashlib, io, json, shutil, tarfile
from pathlib import Path

EXPECTED = json.loads('[{"path":".github/workflows/horizontal-evidence-governance.yml","sha256":"6e4a798a3d39e8a593a6297bfed3196ac92fde9662b5ff8d4cc2222b1a9008d0","size":1831},{"path":"research/analytics_landscape/product_families/README.md","sha256":"5949e980a456a40d00539c1adbe26a7c4a56bd5b504fe112afbbdd48b7c102a4","size":2449},{"path":"research/analytics_landscape/product_families/consolidation-hardening-audit.jsonl","sha256":"81f118ea9f1b6dd0be72b26671eedb1cf8e00602938940c7a40e88c247a83a63","size":5539},{"path":"research/analytics_landscape/product_families/evidence_governance/README.md","sha256":"b541b4fcdafc8195429ad23a8200e698d4ac51ba3f69f826ed3a9399ff396080","size":3082},{"path":"research/analytics_landscape/product_families/evidence_governance/build.py","sha256":"c3920671324c97a96f4ff6df65dc9fa666267b15f705cffc48fe392c84d84ad4","size":16266},{"path":"research/analytics_landscape/product_families/evidence_governance/entity-identity-taxonomy.json","sha256":"a47ef9d5b7039c50f0f9f4edffaea815c37ebc1c67f8ae8bfd2e543e8b735238","size":4686},{"path":"research/analytics_landscape/product_families/evidence_governance/evidence-governance.schema.json","sha256":"c37c7a5b09c58516b506dd92d25e5b81f1a93dec8486d0df63dd568f631c8635","size":6527},{"path":"research/analytics_landscape/product_families/evidence_governance/evidence-role-taxonomy.json","sha256":"70d5b1cfea2def50c7aab29b05514503a063f12a8b6007f63c45790a0ba647d2","size":4247},{"path":"research/analytics_landscape/product_families/evidence_governance/manifest.json","sha256":"f4f76a72232ba58331c08a07aa211ac785d13b9ca21800a87cb61e84b24acd39","size":1209},{"path":"research/analytics_landscape/product_families/evidence_governance/policy.json","sha256":"c7da5ba5118d32e0fce7283fe624a857eebb7d29bffdc53711563bc3181596b7","size":3794},{"path":"research/analytics_landscape/product_families/evidence_governance/source_model.py","sha256":"edb80353fd5a093830ba3a1a87681effe77d16545daf0c461d6ba238ab298378","size":2843},{"path":"research/analytics_landscape/product_families/evidence_governance/sources/datacite-metadata-schema-4-7.json","sha256":"dab69bb294106dc9aac36b3e95e796bd460fe6823b91daa3a14e80bc55471bf2","size":759},{"path":"research/analytics_landscape/product_families/evidence_governance/sources/gleif-level-1.json","sha256":"256baf99f210192ca2ffa9c6955c4f44d882f4620cf4d266137a729eb1ffbb78","size":750},{"path":"research/analytics_landscape/product_families/evidence_governance/sources/gleif-level-2.json","sha256":"f59bd3a0b62635873652d9373a404e5a3d1bb528193d338ec02d8023424b79ff","size":818},{"path":"research/analytics_landscape/product_families/evidence_governance/sources/w3c-prov-o.json","sha256":"b65f8cc5ca822d2c89977e585a97c82105c6c83f6a7aaab2ae683deebde86a14","size":684},{"path":"research/analytics_landscape/product_families/evidence_governance/sources/w3c-web-annotation.json","sha256":"ea0a80c76832b66daa7e9db912c8db6857be0abf62b289631f2eff6b784ca393","size":662},{"path":"research/analytics_landscape/product_families/evidence_governance/validate.py","sha256":"d57f467363688043ea6151747ee50414fddec48d0b6ac0982043cc58b88b3411","size":9611},{"path":"research/analytics_landscape/product_families/manifest.json","sha256":"1fa86d696e07c2039822bffaba0e88309ac15e63b9845302febf045743875f56","size":3068}]')
ROOT = Path.cwd().resolve()
PARTS = ROOT / ".github" / "b04-payload"
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
shutil.rmtree(PARTS)
Path(__file__).unlink()
print("PASS bootstrapped 18 governed repository files")
