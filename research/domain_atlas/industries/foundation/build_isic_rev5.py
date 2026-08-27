#!/usr/bin/env python3
"""Build the edition-frozen ISIC Rev. 5 industry spine from UNSD's official CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


SOURCE_URL = (
    "https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/"
    "ISIC_Rev_5_english_structure.csv"
)
EXPECTED_SHA256 = "fc408f57bd3a4f33c35a4f384ec0010283dd72774892c8d48ae1330a8caeb57f"
EXPECTED_COUNTS = {"section": 22, "division": 87, "group": 258, "class": 463}
LEVEL_BY_WIDTH = {1: "section", 2: "division", 3: "group", 4: "class"}


def stable_id(level: str, code: str) -> str:
    # Shared atlas IDs require every dotted segment to start with a letter.
    id_code = code.lower() if code.isalpha() else f"c{code}"
    return f"industry.isic5.{level}.{id_code}"


def read_rows(source: Path) -> tuple[list[dict[str, str]], str]:
    payload = source.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"refusing unexpected ISIC source: sha256={digest}; expected={EXPECTED_SHA256}"
        )
    # The current official CSV contains Windows-1252 punctuation/non-breaking spaces.
    rows = list(csv.DictReader(payload.decode("cp1252").splitlines()))
    normalized = []
    for row in rows:
        code = row["ISIC Rev 5 Code"].strip()
        title = " ".join(row["ISIC Rev 5 Title"].replace("\xa0", " ").split())
        if len(code) not in LEVEL_BY_WIDTH:
            raise SystemExit(f"unsupported ISIC code width: {code!r}")
        normalized.append({"code": code, "title": title})
    return normalized, digest


def build(rows: list[dict[str, str]], digest: str) -> list[dict[str, object]]:
    nodes: list[dict[str, object]] = []
    current_section: str | None = None
    seen: set[str] = set()
    for row in rows:
        code = row["code"]
        level = LEVEL_BY_WIDTH[len(code)]
        node_id = stable_id(level, code)
        if node_id in seen:
            raise SystemExit(f"duplicate node id: {node_id}")
        seen.add(node_id)

        if level == "section":
            current_section = code
            parent_id = None
            ancestors: list[str] = []
        elif level == "division":
            if current_section is None:
                raise SystemExit(f"division {code} precedes a section")
            parent_id = stable_id("section", current_section)
            ancestors = [parent_id]
        elif level == "group":
            section_id = stable_id("section", current_section or "")
            division_id = stable_id("division", code[:2])
            parent_id = division_id
            ancestors = [section_id, division_id]
        else:
            section_id = stable_id("section", current_section or "")
            division_id = stable_id("division", code[:2])
            group_id = stable_id("group", code[:3])
            parent_id = group_id
            ancestors = [section_id, division_id, group_id]

        nodes.append(
            {
                "record_id": node_id,
                "record_kind": "industry_taxonomy_node",
                "edition": 1,
                "status": "official_import",
                "scheme_id": "scheme.un.isic",
                "scheme_edition_id": "scheme.un.isic.rev5",
                "scheme_code": code,
                "level": level,
                "level_ordinal": len(code),
                "title": row["title"],
                "parent_id": parent_id,
                "ancestor_ids": ancestors,
                "concept_kind": "economic_activity",
                "taxonomy_role": "global_activity_reference_spine",
                "semantic_identity_policy": "edition_frozen_boundary",
                "assignment_basis": "principal_economic_activity_under_scheme_rules",
                "source_refs": ["source.un.isic.rev5.structure"],
                "source_locator": f"ISIC Rev. 5 code {code}",
                "source_sha256": digest,
            }
        )

    child_counts = Counter(node["parent_id"] for node in nodes if node["parent_id"])
    for node in nodes:
        node["child_count"] = child_counts[node["record_id"]]
        node["is_leaf"] = node["child_count"] == 0
    return nodes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="downloaded official ISIC Rev. 5 structure CSV")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("isic-rev5.nodes.jsonl"),
    )
    args = parser.parse_args()
    rows, digest = read_rows(args.source)
    nodes = build(rows, digest)
    counts = Counter(node["level"] for node in nodes)
    if dict(counts) != EXPECTED_COUNTS:
        raise SystemExit(f"unexpected level counts: {dict(counts)}")
    args.output.write_text(
        "".join(json.dumps(node, ensure_ascii=False, sort_keys=True) + "\n" for node in nodes),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "source_url": SOURCE_URL,
                "source_sha256": digest,
                "nodes": len(nodes),
                "counts": dict(counts),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
