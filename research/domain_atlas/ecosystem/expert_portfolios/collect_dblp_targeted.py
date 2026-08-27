#!/usr/bin/env python3
"""Targeted DBLP recovery for ambiguous/common-name Crossref portfolios.

Each query includes the routed domain term.  Results still admit only bibliographic
authorship; query relevance is not artifact-content verification.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from collect_dblp import exactish_author_match, normalize_hit
from expert_seeds import rows

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "bibliography-dblp-targeted.jsonl"

QUERIES = {
    "Jeffrey Dean": "Jeffrey Dean MapReduce",
    "Matei Zaharia": "Matei Zaharia Spark",
    "Martin Kleppmann": "Martin Kleppmann CRDT",
    "Neha Narkhede": "Neha Narkhede Kafka streaming",
    "Jay Kreps": "Jay Kreps Kafka log streaming",
    "David DeWitt": "David DeWitt database",
    "Michael Armbrust": "Michael Armbrust Spark",
    "Jignesh Patel": "Jignesh Patel database",
    "Thomas Richardson": "Thomas Richardson causal graph",
    "James Taylor": "James W. Taylor forecasting time series",
    "John Swisher": "John Swisher simulation",
    "Erik Hoel": "Erik Hoel spatial",
    "David Maier": "David Maier database",
    "Claudio Silva": "Claudio Silva visualization",
    "David Huffman": "David Huffman coding",
    "Julien Le Dem": "Julien Le Dem Parquet",
    "Doug Cutting": "Doug Cutting Hadoop",
    "Kenton Varda": "Kenton Varda Protobuf",
    "Adam Smith": "Adam Smith differential privacy",
    "Peter Bailis": "Peter Bailis database",
    "Rodrigo Fonseca": "Rodrigo Fonseca distributed",
    "Arvind": "Arvind dataflow",
}


def main() -> None:
    seed_by_name = {row["name"]: row for row in rows()}
    selected = []
    for index, (name, query) in enumerate(QUERIES.items(), 1):
        url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode({"q": query, "h": 30, "format": "json"})
        request = urllib.request.Request(url, headers={"User-Agent": "SAN-domain-atlas-research/0.1"})
        payload = None
        for attempt in range(6):
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    payload = json.load(response)
                break
            except urllib.error.HTTPError as exc:
                if exc.code != 429 or attempt == 5:
                    raise
                time.sleep(4 + attempt * 3)
        assert payload is not None
        hits = payload.get("result", {}).get("hits", {}).get("hit", [])
        if isinstance(hits, dict):
            hits = [hits]
        candidates = []
        for hit in hits:
            row = normalize_hit(seed_by_name[name], hit)
            if row:
                row["collector"] = "dblp_targeted_query"
                row["targeted_query"] = query
                row["selection_bucket"] = "targeted_identity_topic_recovery"
                row["topic_assignment_state"] = "targeted_query_needs_content_review"
                row["bibliographic_evidence_limitations"].append(
                    "Targeted query terms improve discovery precision but do not establish artifact-content relevance."
                )
                candidates.append(row)
        candidates.sort(key=lambda row: (-(row.get("year") or 0), row["title"]))
        chosen = candidates[:7]
        selected.extend(chosen)
        print(f"[{index:02d}/{len(QUERIES)}] {name}: {len(chosen)}", flush=True)
        time.sleep(2.2)
    selected.sort(key=lambda row: (row["query_name"], row.get("year") or 0, row["title"]))
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in selected), encoding="utf-8")
    print(f"wrote {len(selected)} targeted DBLP records")


if __name__ == "__main__":
    main()
