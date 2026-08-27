#!/usr/bin/env python3
"""Collect a pinned OpenAlex identity/work snapshot with bounded concurrency.

OpenAlex is used for discovery and bibliographic metadata.  DOI/repository landing
pages remain the artifact locators; OpenAlex does not prove invention or expertise.
"""

from __future__ import annotations

import concurrent.futures
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
IDENTITIES = ROOT / "openalex-identities.jsonl"
SNAPSHOT = ROOT / "bibliography-snapshot.jsonl"
FAILED = ROOT / "collection-failures.jsonl"
USER_AGENT = "SAN-domain-atlas-research/0.1 (public bibliography snapshot)"


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def get_json(url: str, attempts: int = 4) -> dict:
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(1.5 * (2 ** attempt))
    raise AssertionError("unreachable")


def author_identity(seed: dict) -> dict:
    url = "https://api.openalex.org/authors?" + urllib.parse.urlencode({
        "search": seed["name"], "per-page": 5,
    })
    payload = get_json(url)
    candidates = payload.get("results", [])
    exact = [candidate for candidate in candidates if norm(candidate.get("display_name")) == norm(seed["name"])]
    pool = exact or candidates
    if not pool:
        raise ValueError("no OpenAlex author candidate")
    pool.sort(key=lambda row: (row.get("works_count", 0), row.get("cited_by_count", 0)), reverse=True)
    chosen = pool[0]
    return {
        "query_name": seed["name"],
        "seed_domain": seed["domain"],
        "seed_family": seed["family"],
        "openalex_id": chosen["id"],
        "display_name": chosen.get("display_name"),
        "orcid": chosen.get("orcid"),
        "works_count": chosen.get("works_count", 0),
        "cited_by_count": chosen.get("cited_by_count", 0),
        "last_known_institutions": chosen.get("last_known_institutions") or [],
        "exact_normalized_name_match": bool(exact),
        "same_name_candidates": [
            {"openalex_id": candidate.get("id"), "display_name": candidate.get("display_name"), "works_count": candidate.get("works_count")}
            for candidate in exact[1:]
        ],
        "identity_state": "bibliographic_candidate_needs_authoritative_profile_review",
        "evidence_limitations": [
            "Automated name matching and work counts do not prove personal identity or domain expertise.",
            "Affiliation is a mutable OpenAlex observation, not an authoritative employment claim.",
        ],
    }


def topic_matches(title: str, domain: str) -> list[str]:
    title_n = norm(title)
    return sorted({term for term in DOMAIN_TERMS[domain] if norm(term) in title_n})


def normalize_work(identity: dict, work: dict, selection_bucket: str) -> dict | None:
    title = work.get("title") or work.get("display_name") or ""
    if not title or any(term in norm(title) for term in EXCLUDED_TITLE_TERMS):
        return None
    year = work.get("publication_year")
    if year and year > 2026:
        return None
    authorships = []
    matched_position = None
    for authorship in work.get("authorships", []):
        author = authorship.get("author") or {}
        authorships.append({
            "name": author.get("display_name"), "openalex_id": author.get("id"),
            "position": authorship.get("author_position"), "corresponding": authorship.get("is_corresponding"),
        })
        if author.get("id") == identity["openalex_id"]:
            matched_position = authorship.get("author_position")
    if matched_position is None:
        return None
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    direct = work.get("doi") or primary.get("landing_page_url") or work.get("id")
    matches = topic_matches(title, identity["seed_domain"])
    return {
        "query_name": identity["query_name"],
        "seed_domain": identity["seed_domain"],
        "seed_family": identity["seed_family"],
        "openalex_work_id": work.get("id"),
        "title": title,
        "authors": authorships,
        "matched_author_openalex_id": identity["openalex_id"],
        "matched_author_position": matched_position,
        "year": year,
        "publication_date": work.get("publication_date"),
        "venue": source.get("display_name"),
        "artifact_type": work.get("type"),
        "doi": work.get("doi"),
        "direct_url": direct,
        "open_access": (work.get("open_access") or {}).get("is_oa"),
        "cited_by_count_snapshot": work.get("cited_by_count", 0),
        "selection_bucket": selection_bucket,
        "title_topic_matches": matches,
        "topic_assignment_state": "title_term_supported" if matches else "seed_routed_needs_content_review",
        "bibliographic_evidence_scope": ["title", "authorship position", "date", "venue", "persistent locator"],
        "bibliographic_evidence_limitations": [
            "OpenAlex verifies discovery metadata, not invention, contribution magnitude, method validity, or expertise.",
            "Author position is recorded but is not interpreted as contribution magnitude.",
            "Topic classification is title-level only until the primary artifact is read.",
        ],
    }


def fetch_works(identity: dict) -> list[dict]:
    author_id = identity["openalex_id"].rsplit("/", 1)[-1]
    common = {"filter": f"authorships.author.id:{author_id}", "per-page": 30}
    top_url = "https://api.openalex.org/works?" + urllib.parse.urlencode({**common, "sort": "cited_by_count:desc"})
    recent_url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
        **common, "filter": f"authorships.author.id:{author_id},from_publication_date:2021-01-01,to_publication_date:2026-08-25",
        "sort": "publication_date:desc",
    })
    top = [normalize_work(identity, work, "foundational_or_influential") for work in get_json(top_url).get("results", [])]
    recent = [normalize_work(identity, work, "recent_2021_2026") for work in get_json(recent_url).get("results", [])]
    top = [row for row in top if row]
    recent = [row for row in recent if row]
    # Prefer topically supported artifacts, but never fabricate relevance.
    score = lambda row: (0 if row["title_topic_matches"] else 1, -(row["cited_by_count_snapshot"] or 0), row["title"])
    top.sort(key=score)
    recent.sort(key=lambda row: (0 if row["title_topic_matches"] else 1, row["publication_date"] or "", row["title"]), reverse=False)
    selected = top[:4]
    seen = {row["openalex_work_id"] for row in selected}
    for row in sorted(recent, key=lambda x: (x["publication_date"] or "", x["title"]), reverse=True):
        if row["openalex_work_id"] not in seen:
            selected.append(row)
            seen.add(row["openalex_work_id"])
        if len(selected) >= 7:
            break
    for row in top[4:]:
        if len(selected) >= 7:
            break
        if row["openalex_work_id"] not in seen:
            selected.append(row)
            seen.add(row["openalex_work_id"])
    return selected


def main() -> None:
    seeds = rows()
    failures = []
    identities = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        future_map = {pool.submit(author_identity, seed): seed for seed in seeds}
        for number, future in enumerate(concurrent.futures.as_completed(future_map), 1):
            seed = future_map[future]
            try:
                identities.append(future.result())
            except Exception as exc:
                failures.append({"query_name": seed["name"], "stage": "identity", "detail": f"{type(exc).__name__}: {exc}"})
            print(f"identity [{number:03d}/180]", flush=True)
    identities.sort(key=lambda row: row["query_name"])
    works = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        future_map = {pool.submit(fetch_works, identity): identity for identity in identities}
        for number, future in enumerate(concurrent.futures.as_completed(future_map), 1):
            identity = future_map[future]
            try:
                selected = future.result()
                works.extend(selected)
                if len(selected) < 6:
                    failures.append({"query_name": identity["query_name"], "stage": "works", "detail": f"only {len(selected)} selected artifacts"})
            except Exception as exc:
                failures.append({"query_name": identity["query_name"], "stage": "works", "detail": f"{type(exc).__name__}: {exc}"})
            print(f"works [{number:03d}/{len(identities)}]: {len(works)}", flush=True)
    works.sort(key=lambda row: (row["query_name"], row["year"] or 0, row["title"]))
    IDENTITIES.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in identities), encoding="utf-8")
    SNAPSHOT.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in works), encoding="utf-8")
    FAILED.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in failures), encoding="utf-8")
    print(f"wrote {len(identities)} identities, {len(works)} artifacts, {len(failures)} collection gaps")


if __name__ == "__main__":
    main()
