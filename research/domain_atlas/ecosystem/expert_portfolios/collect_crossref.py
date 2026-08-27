#!/usr/bin/env python3
"""Collect a deterministic normalized Crossref bibliography discovery snapshot."""

from __future__ import annotations

import concurrent.futures
import argparse
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from expert_seeds import rows
from collect_dblp import DOMAIN_TERMS, EXCLUDED_TITLE_TERMS

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "bibliography-snapshot.jsonl"
IDENTITIES = ROOT / "bibliographic-identities.jsonl"
FAILED = ROOT / "collection-failures.jsonl"
UA = "SAN-domain-atlas-research/0.1 (Crossref public metadata snapshot)"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def fetch_json(url: str, attempts: int = 4) -> dict:
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(1 + attempt * 2)
    raise AssertionError("unreachable")


def author_name(author: dict) -> str:
    return " ".join(part for part in [author.get("given"), author.get("family")] if part)


def exactish(seed_name: str, author: dict) -> bool:
    seed = norm(seed_name).split()
    candidate = norm(author_name(author)).split()
    return bool(seed and candidate and seed[-1] == candidate[-1] and seed[0][0] == candidate[0][0])


def date_of(item: dict) -> tuple[int | None, str | None]:
    for key in ["published-print", "published-online", "published", "issued", "created"]:
        parts = (item.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            year = int(parts[0][0])
            month = int(parts[0][1]) if len(parts[0]) > 1 else 1
            day = int(parts[0][2]) if len(parts[0]) > 2 else 1
            return year, f"{year:04d}-{month:02d}-{day:02d}"
    return None, None


def normalize_item(seed: dict, item: dict) -> dict | None:
    title_list = item.get("title") or []
    title = re.sub(r"<[^>]+>", "", title_list[0] if title_list else "").strip()
    title_n = norm(title)
    if not title or any(norm(term) in title_n for term in EXCLUDED_TITLE_TERMS):
        return None
    year, date = date_of(item)
    if year and year > 2026:
        return None
    authors = item.get("author") or []
    matches = [author for author in authors if exactish(seed["name"], author)]
    if not matches:
        return None
    topic = sorted({term for term in DOMAIN_TERMS[seed["domain"]] if norm(term) in title_n})
    doi = item.get("DOI")
    return {
        "query_name": seed["name"],
        "seed_domain": seed["domain"],
        "seed_family": seed["family"],
        "crossref_doi": doi,
        "title": title,
        "authors": [
            {"name": author_name(author), "orcid": author.get("ORCID"), "sequence": author.get("sequence")}
            for author in authors
        ],
        "matched_orcids": sorted({author.get("ORCID") for author in matches if author.get("ORCID")}),
        "year": year,
        "publication_date": date,
        "venue": (item.get("container-title") or [None])[0],
        "artifact_type": item.get("type"),
        "doi": doi,
        "direct_url": f"https://doi.org/{doi}" if doi else item.get("URL"),
        "crossref_url": item.get("URL"),
        "is_referenced_by_count_snapshot": item.get("is-referenced-by-count"),
        "title_topic_matches": topic,
        "topic_assignment_state": "title_term_supported" if topic else "seed_routed_needs_content_review",
        "bibliographic_evidence_scope": ["title", "authors", "date", "venue", "DOI locator"],
        "bibliographic_evidence_limitations": [
            "Crossref registration metadata supports discovery and authorship only, not invention, contribution magnitude, validity, or expertise.",
            "An exact-ish name match is not identity disambiguation; same-name and missing-ORCID cases require review.",
            "Topic classification is title-level only until the primary artifact is read.",
        ],
    }


def collect_seed(seed: dict) -> tuple[dict, list[dict]]:
    params = {
        "query.author": seed["name"],
        "rows": 30,
        "filter": "until-pub-date:2026-08-25",
        "select": "DOI,title,author,published,published-online,published-print,issued,created,container-title,type,URL,is-referenced-by-count",
    }
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    items = fetch_json(url).get("message", {}).get("items", [])
    candidates = [normalize_item(seed, item) for item in items]
    candidates = [row for row in candidates if row]
    # Four influential/relevant plus three recent; keep selection reason explicit.
    by_influence = sorted(candidates, key=lambda row: (
        0 if row["title_topic_matches"] else 1,
        -(row["is_referenced_by_count_snapshot"] or 0),
        row["title"],
    ))
    selected = []
    seen = set()
    for row in by_influence:
        key = row["doi"] or row["direct_url"] or row["title"]
        if key not in seen:
            row["selection_bucket"] = "influential_or_relevant"
            selected.append(row); seen.add(key)
        if len(selected) == 4:
            break
    recent = sorted(candidates, key=lambda row: (row["year"] or 0, row["publication_date"] or "", row["title"]), reverse=True)
    for row in recent:
        key = row["doi"] or row["direct_url"] or row["title"]
        if key not in seen:
            row["selection_bucket"] = "recent_2021_2026" if (row["year"] or 0) >= 2021 else "additional_historical"
            selected.append(row); seen.add(key)
        if len(selected) >= 7:
            break
    orcids = sorted({orcid for row in selected for orcid in row["matched_orcids"]})
    identity = {
        "query_name": seed["name"], "seed_domain": seed["domain"], "seed_family": seed["family"],
        "candidate_orcids": orcids,
        "identity_state": "orcid_candidate_needs_profile_review" if orcids else "name_only_identity_review_required",
        "selected_artifact_count": len(selected),
        "evidence_limitations": [
            "Crossref is a discovery index; an authoritative person profile must resolve identity.",
            "Multiple ORCIDs or absent ORCID remain explicit review items.",
        ],
    }
    return identity, selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--names", help="Comma-separated subset to collect and merge into the pinned snapshot")
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    selected_seeds = rows()
    if args.names:
        wanted = {name.strip() for name in args.names.split(",") if name.strip()}
        selected_seeds = [seed for seed in selected_seeds if seed["name"] in wanted]
        missing = wanted - {seed["name"] for seed in selected_seeds}
        if missing:
            raise SystemExit(f"unknown seed names: {sorted(missing)}")
    identities, artifacts, failures = [], [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {pool.submit(collect_seed, seed): seed for seed in selected_seeds}
        for index, future in enumerate(concurrent.futures.as_completed(future_map), 1):
            seed = future_map[future]
            try:
                identity, selected = future.result()
                identities.append(identity); artifacts.extend(selected)
                if len(selected) < 6:
                    failures.append({
                        "query_name": seed["name"], "failure_kind": "insufficient_artifacts",
                        "selected": len(selected), "target": 7,
                        "action": "Review a primary bibliography or software/specification history and add exact artifacts manually.",
                    })
            except Exception as exc:
                failures.append({
                    "query_name": seed["name"], "failure_kind": "collector_exception",
                    "detail": f"{type(exc).__name__}: {exc}", "action": "Retry or add authoritative primary artifacts manually.",
                })
            print(f"[{index:03d}/{len(selected_seeds)}] identities={len(identities)} artifacts={len(artifacts)}", flush=True)
    if args.names:
        old_identities = [json.loads(line) for line in IDENTITIES.read_text(encoding="utf-8").splitlines() if line.strip()] if IDENTITIES.exists() else []
        old_artifacts = [json.loads(line) for line in SNAPSHOT.read_text(encoding="utf-8").splitlines() if line.strip()] if SNAPSHOT.exists() else []
        old_failures = [json.loads(line) for line in FAILED.read_text(encoding="utf-8").splitlines() if line.strip()] if FAILED.exists() else []
        retried = {seed["name"] for seed in selected_seeds}
        identities = [row for row in old_identities if row["query_name"] not in retried] + identities
        artifacts = [row for row in old_artifacts if row["query_name"] not in retried] + artifacts
        failures = [row for row in old_failures if row["query_name"] not in retried] + failures
    identities.sort(key=lambda row: row["query_name"])
    artifacts.sort(key=lambda row: (row["query_name"], row["year"] or 0, row["title"]))
    IDENTITIES.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in identities), encoding="utf-8")
    SNAPSHOT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in artifacts), encoding="utf-8")
    FAILED.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in failures), encoding="utf-8")
    print(f"wrote {len(identities)} identities, {len(artifacts)} artifacts, {len(failures)} gaps")


if __name__ == "__main__":
    main()
