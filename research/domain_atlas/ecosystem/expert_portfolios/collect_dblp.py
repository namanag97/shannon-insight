#!/usr/bin/env python3
"""Collect a pinned DBLP bibliography snapshot for the curated expert seeds.

This is a research-time collector.  The deterministic corpus builder consumes the
checked-in normalized snapshot and never performs network I/O.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

from expert_seeds import rows

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "bibliography-snapshot.jsonl"
FAILED = ROOT / "collection-failures.jsonl"

EXCLUDED_TITLE_TERMS = {
    "artificial intelligence", "large language model", "language model", "generative",
    "chatgpt", "foundation model", "deep learning", "neural network", "transformer",
    "diffusion model", "machine learning", "reinforcement learning",
}

DOMAIN_TERMS = {
    "process_case_mining": ["process", "event log", "conformance", "workflow", "petri", "object-centric", "ocel", "bpmn", "case"],
    "databases_query": ["database", "query", "transaction", "join", "index", "sql", "column", "cardinality", "optimizer"],
    "streaming_distributed": ["stream", "distributed", "consensus", "replication", "checkpoint", "event time", "dataflow", "log", "mapreduce", "spark", "flink", "kafka", "crdt", "mesos", "sparrow", "blazeit"],
    "storage_lakehouse": ["storage", "database", "transaction", "table", "catalog", "file", "cloud", "warehouse", "lake", "delta", "spark sql", "gamma", "parquet"],
    "quality_lineage_cleaning": ["quality", "clean", "lineage", "provenance", "dependency", "repair", "integration", "duplicate", "explanation"],
    "semantics_ontology": ["ontology", "semantic", "knowledge", "concept", "reason", "linked data", "identity", "description logic"],
    "causal_experimental_statistics": ["causal", "treatment", "counterfactual", "experiment", "confound", "instrument", "estimand", "intervention", "markov equivalence", "directed mixed graph"],
    "forecasting_time_series": ["forecast", "time series", "state space", "prediction interval", "exponential smoothing", "reconciliation"],
    "operations_research": ["optimization", "integer", "linear programming", "routing", "scheduling", "constraint", "stochastic", "robust"],
    "simulation_decision_analysis": ["simulation", "monte carlo", "decision", "multi-criteria", "ranking", "selection", "discrete event", "health care system"],
    "visualization_hci": ["visual", "interaction", "graphical", "chart", "human", "perception", "uncertainty", "interface"],
    "spatial_scientific_media": ["spatial", "geographic", "raster", "trajectory", "array", "scientific", "multimedia", "image", "similarity", "visualization", "rendering"],
    "compression_encoding": ["compress", "encoding", "succinct", "bitmap", "entropy", "serialization", "string", "index", "huffman", "parquet", "protobuf", "protocol buffer", "avro", "coding"],
    "privacy_security_trust": ["privacy", "security", "access control", "cryptograph", "information flow", "identity", "differential", "policy"],
    "compiler_runtime_reliability": ["compiler", "runtime", "program", "parallel", "failure", "testing", "verification", "performance", "reliability", "llvm", "dataflow", "consistency"],
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def author_rows(info: dict) -> list[dict]:
    value = info.get("authors", {}).get("author", [])
    if isinstance(value, dict):
        value = [value]
    return [item if isinstance(item, dict) else {"text": str(item)} for item in value]


def exactish_author_match(seed_name: str, authors: list[dict]) -> tuple[bool, list[str]]:
    seed = norm(seed_name).split()
    first, last = seed[0], seed[-1]
    matches = []
    for author in authors:
        candidate = norm(author.get("text", "")).split()
        if candidate and last in candidate and candidate[0][:1] == first[:1]:
            matches.append(author.get("@pid", ""))
    return bool(matches), matches


def normalize_hit(seed: dict, hit: dict) -> dict | None:
    info = hit.get("info", {})
    title = re.sub(r"<[^>]+>", "", info.get("title", "")).strip()
    if not title or any(term in norm(title) for term in EXCLUDED_TITLE_TERMS):
        return None
    try:
        year = int(info.get("year", 0))
    except (TypeError, ValueError):
        year = 0
    if year and year > 2026:
        return None
    authors = author_rows(info)
    matched, pids = exactish_author_match(seed["name"], authors)
    if not matched:
        return None
    ee = info.get("ee")
    if isinstance(ee, list):
        ee = ee[0] if ee else None
    if isinstance(ee, dict):
        ee = ee.get("text")
    direct_url = ee or info.get("url")
    title_n = norm(title)
    matches = sorted({term for term in DOMAIN_TERMS[seed["domain"]] if norm(term) in title_n})
    return {
        "query_name": seed["name"],
        "seed_domain": seed["domain"],
        "seed_family": seed["family"],
        "dblp_key": info.get("key"),
        "title": title,
        "authors": [{"name": a.get("text"), "dblp_pid": a.get("@pid")} for a in authors],
        "matched_dblp_pids": pids,
        "year": year or None,
        "venue": info.get("venue"),
        "artifact_type": info.get("type"),
        "doi": info.get("doi"),
        "direct_url": direct_url,
        "dblp_url": info.get("url"),
        "open_access_marker": info.get("access"),
        "title_topic_matches": matches,
        "topic_assignment_state": "title_term_supported" if matches else "seed_routed_needs_content_review",
        "bibliographic_evidence_scope": ["title", "authors", "year", "venue", "persistent locator"],
        "bibliographic_evidence_limitations": [
            "DBLP verifies bibliographic metadata, not invention, contribution magnitude, artifact correctness, or expertise.",
            "Topic classification is title-level only until a reviewer reads the primary artifact.",
        ],
    }


def fetch(seed: dict, hits: int) -> list[dict]:
    query = f'author:{seed["name"]}:'
    url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode({
        "q": query, "h": hits, "format": "json"
    })
    request = urllib.request.Request(url, headers={"User-Agent": "SAN-domain-atlas-research/0.1 (bibliography snapshot)"})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.load(response)
    raw_hits = payload.get("result", {}).get("hits", {}).get("hit", [])
    if isinstance(raw_hits, dict):
        raw_hits = [raw_hits]
    candidates = [normalize_hit(seed, hit) for hit in raw_hits]
    candidates = [row for row in candidates if row]
    candidates.sort(key=lambda row: (
        0 if row["title_topic_matches"] else 1,
        -(row["year"] or 0),
        row["title"],
    ))
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query-hits", type=int, default=25)
    parser.add_argument("--select", type=int, default=6)
    parser.add_argument("--delay", type=float, default=0.08)
    args = parser.parse_args()
    selected, failures = [], []
    for index, seed in enumerate(rows(), start=1):
        try:
            candidates = fetch(seed, args.query_hits)
            chosen = candidates[: args.select]
            selected.extend(chosen)
            if len(chosen) < args.select:
                failures.append({
                    "query_name": seed["name"], "failure_kind": "insufficient_matching_records",
                    "selected": len(chosen), "required": args.select,
                    "action": "Add verified primary artifacts manually or adjudicate an alternate identity locator.",
                })
        except Exception as exc:  # Research collector records failure; it never fabricates.
            failures.append({
                "query_name": seed["name"], "failure_kind": "collector_exception",
                "detail": f"{type(exc).__name__}: {exc}",
                "action": "Retry or add a manually verified primary source.",
            })
        print(f"[{index:03d}/180] {seed['name']}: {len(selected)} selected", flush=True)
        time.sleep(args.delay)
    SNAPSHOT.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in selected), encoding="utf-8")
    FAILED.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in failures), encoding="utf-8")
    print(f"wrote {len(selected)} bibliography records and {len(failures)} failures")


if __name__ == "__main__":
    main()
