#!/usr/bin/env python3
"""Collect and rank fresh feed items for Luna's daily data-news research."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import email.utils
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

USER_AGENT = "LunaResearch/1.0 (+daily-data-news)"
TECHNICAL_TERMS = re.compile(
    r"\b(release|benchmark|architecture|query|engine|database|warehouse|lakehouse|"
    r"stream|kafka|flink|cdc|orchestrat|pipeline|transform|semantic|lineage|catalog|"
    r"observability|governance|postgres|spark|iceberg|duckdb|clickhouse|trino|dbt|"
    r"latency|throughput|storage|compute|vector|sql|connector|schema)\b",
    re.IGNORECASE,
)
LOW_SIGNAL_TERMS = re.compile(
    r"\b(webinar|conference|summit|keynote|hiring|funding|series [a-z]|customer story|"
    r"partner|certification|award|pricing|register now)\b",
    re.IGNORECASE,
)
NIGHTLY_TERMS = re.compile(r"(?:nightly|\.dev\d*)", re.IGNORECASE)
PRE_RELEASE_TERMS = re.compile(r"(?:^|[.\d-])(?:rc|alpha)\d*", re.IGNORECASE)
BETA_TERMS = re.compile(r"(?:^|[.\d-])beta\d*", re.IGNORECASE)
PACKAGE_RELEASE_TERMS = re.compile(r"^(?:providers-|constraints-)", re.IGNORECASE)


@dataclass(frozen=True)
class Candidate:
    score: int
    title: str
    url: str
    published: Optional[str]
    source_id: str
    source_name: str
    tier: int
    beats: list[str]
    summary: str


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(element: ET.Element, names: tuple[str, ...]) -> str:
    for child in element:
        if local_name(child.tag) in names:
            return "".join(child.itertext()).strip()
    return ""


def entry_url(element: ET.Element) -> str:
    for child in element:
        if local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        relation = child.attrib.get("rel", "alternate")
        if href and relation == "alternate":
            return href
        if child.text and child.text.strip():
            return child.text.strip()
    return ""


def parse_date(value: str) -> Optional[dt.datetime]:
    if not value:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def clean_text(value: str, limit: int = 500) -> str:
    value = re.sub(r"<[^>]+>", " ", html.unescape(value))
    return " ".join(value.split())[:limit]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def score_item(title: str, summary: str, tier: int, published: Optional[dt.datetime], now: dt.datetime) -> int:
    text = f"{title} {summary}"
    score = {1: 6, 2: 4, 3: 2}.get(tier, 1)
    score += min(4, len(TECHNICAL_TERMS.findall(text)))
    if LOW_SIGNAL_TERMS.search(text):
        score -= 5
    if NIGHTLY_TERMS.search(text):
        score -= 8
    elif PRE_RELEASE_TERMS.search(title):
        score -= 4
    elif BETA_TERMS.search(title):
        score -= 2
    if PACKAGE_RELEASE_TERMS.search(title):
        score -= 3
    if published:
        age_hours = max(0.0, (now - published).total_seconds() / 3600)
        score += 4 if age_hours <= 24 else 2 if age_hours <= 48 else 0
    return score


def parse_feed(source: dict[str, Any], now: dt.datetime, cutoff: dt.datetime, include_undated: bool) -> list[Candidate]:
    root = ET.fromstring(fetch(source["url"]))
    entries = [element for element in root.iter() if local_name(element.tag) in {"item", "entry"}]
    results: list[Candidate] = []
    for entry in entries:
        title = clean_text(child_text(entry, ("title",)), 220)
        url = entry_url(entry)
        date_text = child_text(entry, ("published", "updated", "pubDate", "date"))
        published = parse_date(date_text)
        summary = clean_text(child_text(entry, ("description", "summary", "content")))
        if not title or not url or (published is None and not include_undated):
            continue
        if published and published < cutoff:
            continue
        results.append(
            Candidate(
                score=score_item(title, summary, int(source["tier"]), published, now),
                title=title,
                url=url,
                published=published.isoformat() if published else None,
                source_id=source["id"],
                source_name=source["name"],
                tier=int(source["tier"]),
                beats=list(source["beats"]),
                summary=summary,
            )
        )
    return results


def canonical_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = [(key, value) for key, value in query if not key.lower().startswith("utm_")]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), urllib.parse.urlencode(query), ""))


def collect(config: dict[str, Any], now: dt.datetime, lookback_hours: int, workers: int, include_undated: bool) -> tuple[list[Candidate], list[str]]:
    cutoff = now - dt.timedelta(hours=lookback_hours)
    sources = [source for source in config["sources"] if source["kind"] in {"rss", "atom"}]
    items: list[Candidate] = []
    failures: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(parse_feed, source, now, cutoff, include_undated): source
            for source in sources
        }
        for future in concurrent.futures.as_completed(futures):
            source = futures[future]
            try:
                items.extend(future.result())
            except (ET.ParseError, urllib.error.URLError, TimeoutError, ValueError) as exc:
                failures.append(f"{source['id']}: {exc}")

    deduped: dict[str, Candidate] = {}
    for item in items:
        key = canonical_url(item.url) or re.sub(r"\W+", " ", item.title.lower()).strip()
        previous = deduped.get(key)
        if previous is None or item.score > previous.score:
            deduped[key] = item
    return sorted(deduped.values(), key=lambda item: (-item.score, item.published or "", item.title)), sorted(failures)


def render_markdown(items: list[Candidate], failures: list[str], generated_at: dt.datetime) -> str:
    lines = [
        "# Luna daily data-news candidates",
        "",
        f"Generated: {generated_at.isoformat()}",
        "",
        "These are discovery candidates, not publish-ready stories. Apply `luna_prompt.md` before selection.",
        "",
    ]
    for item in items:
        date = item.published[:10] if item.published else "undated"
        lines.extend(
            [
                f"## {item.score} — [{item.title}]({item.url})",
                "",
                f"Source: {item.source_name} (tier {item.tier}) · {date} · {', '.join(item.beats)}",
                "",
                item.summary or "No feed summary.",
                "",
            ]
        )
    if failures:
        lines.extend(["## Feed failures", "", *[f"- {failure}" for failure in failures], ""])
    return "\n".join(lines)


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=here / "sources.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--lookback-hours", type=int)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--include-undated", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc)
    lookback = args.lookback_hours or int(config["default_lookback_hours"])
    items, failures = collect(config, now, lookback, args.workers, args.include_undated)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(items, failures, now), encoding="utf-8")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(
                {"generated_at": now.isoformat(), "candidates": [asdict(item) for item in items], "failures": failures},
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"{len(items)} candidates; {len(failures)} feed failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
