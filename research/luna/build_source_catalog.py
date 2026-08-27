#!/usr/bin/env python3
"""Build a 1,000+ website/blog catalogue for data and analytics research.

The catalogue is evidence-aware: curated seeds are preserved, while domains
discovered in editorial archives retain their provenance and sample links.  A
domain appearing in a newsletter is a discovery lead, not automatic authority.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Optional

USER_AGENT = "LunaResearch/1.0 (+data-source-catalog)"
DEW_SITEMAP = "https://www.dataengineeringweekly.com/sitemap.xml"
EXCLUDED_DOMAINS = {
    "apple.com",
    "doubleclick.net",
    "enable-javascript.com",
    "facebook.com",
    "fonts.googleapis.com",
    "google.com",
    "googletagmanager.com",
    "instagram.com",
    "linkedin.com",
    "mailchi.mp",
    "substack.com",
    "t.co",
    "twitter.com",
    "x.com",
}
EXCLUDED_SUFFIXES = (
    ".cloudfront.net",
    ".doubleclick.net",
    ".googleusercontent.com",
)
DOMAIN_DISPLAY_NAMES = {
    "api.sap.com": "SAP Business Accelerator Hub",
    "docs.aws.amazon.com": "AWS Documentation",
    "github.com": "GitHub",
    "help.sap.com": "SAP Help Portal",
    "learn.microsoft.com": "Microsoft Learn",
    "me.sap.com": "SAP for Me",
    "support.sap.com": "SAP Support",
}

TOPIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "databases-query-engines": re.compile(
        r"\b(database|postgres|mysql|mariadb|sqlite|duckdb|clickhouse|trino|presto|query engine|"
        r"sql|nosql|mongodb|cassandra|redis|dynamodb|spanner|cockroach|tidb|yugabyte)\b",
        re.I,
    ),
    "warehouses-lakehouses-formats": re.compile(
        r"\b(warehouse|lakehouse|data lake|iceberg|delta lake|hudi|parquet|orc|snowflake|"
        r"bigquery|redshift|databricks|object storage|table format)\b",
        re.I,
    ),
    "streaming-messaging-cdc": re.compile(
        r"\b(stream|kafka|flink|pulsar|redpanda|debezium|change data capture|cdc|event[- ]driven|"
        r"message queue|kinesis|pubsub|event time|watermark)\b",
        re.I,
    ),
    "orchestration-ingestion-transformation": re.compile(
        r"\b(airflow|dagster|prefect|kestra|orchestrat|pipeline|etl|elt|ingest|connector|airbyte|"
        r"fivetran|dbt|dataform|sqlmesh|transformation)\b",
        re.I,
    ),
    "analytics-bi-semantic-metrics": re.compile(
        r"\b(analytics|business intelligence|\bbi\b|semantic layer|metrics layer|dashboard|"
        r"looker|tableau|power bi|superset|metabase|cube|dimensional|olap)\b",
        re.I,
    ),
    "quality-observability-reliability": re.compile(
        r"\b(data quality|observability|lineage|reliability|testing|great expectations|soda|"
        r"monte carlo|incident|freshness|schema change|data contract)\b",
        re.I,
    ),
    "governance-catalog-security": re.compile(
        r"\b(governance|catalog|metadata|privacy|security|authorization|access control|lineage|"
        r"openmetadata|datahub|collibra|atlan|gdpr|residency|retention)\b",
        re.I,
    ),
    "ml-ai-data-infrastructure": re.compile(
        r"\b(machine learning|\bml\b|artificial intelligence|\bai\b|llm|rag|vector|embedding|"
        r"feature store|model serving|training data|mlops)\b",
        re.I,
    ),
    "enterprise-systems-connectors": re.compile(
        r"\b(sap|salesforce|oracle ebs|workday|netsuite|dynamics|erp|crm|mainframe|extractor|"
        r"odata|jdbc|odbc|bapi|abap)\b",
        re.I,
    ),
    "cloud-infrastructure-cost": re.compile(
        r"\b(aws|azure|google cloud|kubernetes|terraform|cloud|serverless|storage|compute|cost|"
        r"finops|network|capacity|performance|benchmark)\b",
        re.I,
    ),
    "research-standards-theory": re.compile(
        r"\b(research|paper|proceedings|standard|specification|theorem|algorithm|vldb|sigmod|"
        r"cidr|arxiv|acm|ieee|w3c|ietf)\b",
        re.I,
    ),
}
BEAT_TOPIC_MAP: dict[str, list[str]] = {
    "query-engines-and-databases": ["databases-query-engines"],
    "warehouses-and-lakehouses": ["warehouses-lakehouses-formats"],
    "streaming-and-cdc": ["streaming-messaging-cdc"],
    "orchestration-and-transformation": ["orchestration-ingestion-transformation"],
    "quality-observability-and-governance": [
        "quality-observability-reliability",
        "governance-catalog-security",
    ],
    "analytics-bi-and-semantic-layers": ["analytics-bi-semantic-metrics"],
    "performance-reliability-and-cost": [
        "quality-observability-reliability",
        "cloud-infrastructure-cost",
    ],
    "open-source-releases": ["open-source-projects-releases"],
    "ai-data-infrastructure": ["ml-ai-data-infrastructure"],
}


@dataclass
class SourceRecord:
    domain: str
    name: str
    homepage: str
    topics: list[str] = field(default_factory=list)
    facets: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    discovery_count: int = 0
    latest_reference: Optional[int] = None
    sample_urls: list[str] = field(default_factory=list)
    sample_titles: list[str] = field(default_factory=list)
    evidence_tier: int = 4
    review_status: str = "discovered-unreviewed"
    feed_url: Optional[str] = None


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: Optional[str] = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            title = " ".join("".join(self._text).split())
            self.links.append((self._href, title))
            self._href = None
            self._text = []


def fetch(url: str, attempts: int = 3) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt + 1 == attempts:
                raise
            time.sleep(0.5 * (2**attempt))
    raise RuntimeError("unreachable")


def normalized_domain(url: str) -> Optional[str]:
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    domain = parsed.hostname.lower().removeprefix("www.")
    if domain in EXCLUDED_DOMAINS or domain.endswith(EXCLUDED_SUFFIXES):
        return None
    if domain.endswith("dataengineeringweekly.com") or domain.endswith("scalingpostgres.com"):
        return None
    return domain


def clean_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in {"ref", "source", "campaign", "mc_cid", "mc_eid"}
    ]
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), "")
    )


def display_name(domain: str) -> str:
    if domain in DOMAIN_DISPLAY_NAMES:
        return DOMAIN_DISPLAY_NAMES[domain]
    stem = domain.split(".")[-2] if "." in domain else domain
    return " ".join(part.capitalize() for part in re.split(r"[-_]", stem))


def add_link(
    records: dict[str, SourceRecord],
    url: str,
    title: str,
    provenance: str,
    latest_reference: Optional[int] = None,
) -> None:
    domain = normalized_domain(url)
    if not domain:
        return
    record = records.setdefault(
        domain,
        SourceRecord(domain=domain, name=display_name(domain), homepage=f"https://{domain}/"),
    )
    record.discovery_count += 1
    if provenance not in record.provenance:
        record.provenance.append(provenance)
    if latest_reference is not None:
        record.latest_reference = max(record.latest_reference or 0, latest_reference)
    cleaned = clean_url(url)
    if cleaned not in record.sample_urls and len(record.sample_urls) < 3:
        record.sample_urls.append(cleaned)
    if title and title not in record.sample_titles and len(record.sample_titles) < 3:
        record.sample_titles.append(title[:240])


def data_engineering_weekly_urls() -> list[str]:
    root = ET.fromstring(fetch(DEW_SITEMAP))
    urls = [element.text or "" for element in root.findall("{*}url/{*}loc")]
    return sorted(
        (url for url in urls if re.search(r"/p/data-engineering-weekly-\d+$", url)),
        key=lambda value: int(value.rsplit("-", 1)[-1]),
    )


def scrape_page(url: str) -> tuple[str, list[tuple[str, str]]]:
    parser = LinkParser()
    parser.feed(fetch(url).decode("utf-8", errors="replace"))
    return url, parser.links


def collect_dew(records: dict[str, SourceRecord], workers: int) -> list[str]:
    urls = data_engineering_weekly_urls()
    failures: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(scrape_page, url): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                _, links = future.result()
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                failures.append(f"{url}: {exc}")
                continue
            issue = int(url.rsplit("-", 1)[-1])
            for href, title in links:
                add_link(records, href, title, "data-engineering-weekly", issue)
    return sorted(failures)


def collect_scaling_postgres(records: dict[str, SourceRecord], corpus_path: Path) -> None:
    payload = json.loads(corpus_path.read_text(encoding="utf-8"))
    for episode in payload["episodes"]:
        for link in episode["links"]:
            add_link(
                records,
                link["url"],
                link["title"],
                "scaling-postgres",
                int(episode["number"]),
            )


def collect_curated(records: dict[str, SourceRecord], root: Path) -> None:
    feeds = json.loads((root / "sources.json").read_text(encoding="utf-8"))["sources"]
    for source in feeds:
        add_link(records, source["url"], source["name"], "luna-curated-feed")
        domain = normalized_domain(source["url"])
        if domain and domain in records:
            record = records[domain]
            if domain not in DOMAIN_DISPLAY_NAMES:
                record.name = source["name"]
            curated_url = clean_url(source["url"])
            record.sample_urls = [curated_url, *[url for url in record.sample_urls if url != curated_url]][:3]
            record.sample_titles = [source["name"], *[title for title in record.sample_titles if title != source["name"]]][:3]
            record.feed_url = source["url"]
            record.evidence_tier = min(record.evidence_tier, int(source["tier"]))
            record.review_status = "curated"
            mapped_topics = {
                mapped
                for beat in source["beats"]
                for mapped in BEAT_TOPIC_MAP.get(beat, [beat])
            }
            record.topics = sorted(set(record.topics) | mapped_topics)

    topic_dir = root / "topic_sources"
    for path in sorted(topic_dir.glob("*.json")):
        for source in json.loads(path.read_text(encoding="utf-8"))["sources"]:
            add_link(records, source["url"], source["name"], f"topic-profile:{path.stem}")
            domain = normalized_domain(source["url"])
            if domain and domain in records:
                record = records[domain]
                if domain not in DOMAIN_DISPLAY_NAMES:
                    record.name = source["name"]
                curated_url = clean_url(source["url"])
                record.sample_urls = [curated_url, *[url for url in record.sample_urls if url != curated_url]][:3]
                record.sample_titles = [source["name"], *[title for title in record.sample_titles if title != source["name"]]][:3]
                record.evidence_tier = min(record.evidence_tier, int(source["tier"]))
                record.review_status = "curated"
                record.facets = sorted(set(record.facets) | set(source["covers"]))


def classify(records: Iterable[SourceRecord]) -> None:
    for record in records:
        text = " ".join([record.domain, *record.sample_titles, *record.topics, *record.facets])
        scores = Counter(
            {
                topic: len(pattern.findall(text))
                for topic, pattern in TOPIC_PATTERNS.items()
                if pattern.search(text)
            }
        )
        inferred = [topic for topic, _ in scores.most_common(3)]
        record.topics = sorted(set(record.topics) | set(inferred))
        if not record.topics:
            record.topics = ["general-data-engineering"]
        if record.review_status != "curated":
            if len(record.provenance) > 1 or record.discovery_count >= 5:
                record.review_status = "repeatedly-discovered"
                record.evidence_tier = 3
            else:
                record.evidence_tier = 4


def write_csv(path: Path, records: list[SourceRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "domain",
                "name",
                "homepage",
                "topics",
                "facets",
                "provenance",
                "discovery_count",
                "latest_reference",
                "evidence_tier",
                "review_status",
                "feed_url",
                "sample_url",
                "sample_title",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "domain": record.domain,
                    "name": record.name,
                    "homepage": record.homepage,
                    "topics": "|".join(record.topics),
                    "facets": "|".join(record.facets),
                    "provenance": "|".join(record.provenance),
                    "discovery_count": record.discovery_count,
                    "latest_reference": record.latest_reference or "",
                    "evidence_tier": record.evidence_tier,
                    "review_status": record.review_status,
                    "feed_url": record.feed_url or "",
                    "sample_url": record.sample_urls[0] if record.sample_urls else "",
                    "sample_title": record.sample_titles[0] if record.sample_titles else "",
                }
            )


def summary(records: list[SourceRecord], failures: list[str]) -> dict[str, Any]:
    topic_counts = Counter(topic for record in records for topic in record.topics)
    status_counts = Counter(record.review_status for record in records)
    provenance_counts = Counter(source for record in records for source in record.provenance)
    return {
        "unique_websites": len(records),
        "topic_counts": dict(topic_counts.most_common()),
        "review_status_counts": dict(status_counts.most_common()),
        "provenance_counts": dict(provenance_counts.most_common()),
        "collection_failures": failures,
    }


def write_summary(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# Luna source-catalog summary",
        "",
        f"Unique websites/blogs: **{data['unique_websites']:,}**",
        "",
        "## Review status",
        "",
        *[f"- {key}: {value:,}" for key, value in data["review_status_counts"].items()],
        "",
        "## Topic coverage",
        "",
        *[f"- {key}: {value:,}" for key, value in data["topic_counts"].items()],
        "",
        "## Provenance",
        "",
        *[f"- {key}: {value:,}" for key, value in data["provenance_counts"].items()],
        "",
        "Discovery is not endorsement. Tier-4 and unreviewed records must be opened, dated, and checked against primary evidence before use.",
        "",
    ]
    if data["collection_failures"]:
        lines.extend(["## Collection failures", "", *[f"- {item}" for item in data["collection_failures"]], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaling-corpus", type=Path, help="JSON made by scrape_scaling_postgres.py")
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--csv-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--minimum-sources", type=int, default=1000)
    args = parser.parse_args()

    records: dict[str, SourceRecord] = {}
    failures = collect_dew(records, max(1, args.workers))
    if args.scaling_corpus:
        collect_scaling_postgres(records, args.scaling_corpus)
    collect_curated(records, here)
    classify(records.values())
    ordered = sorted(
        records.values(),
        key=lambda item: (item.evidence_tier, -item.discovery_count, item.domain),
    )
    if len(ordered) < args.minimum_sources:
        print(
            f"catalogue has {len(ordered)} sources; minimum is {args.minimum_sources}",
            file=sys.stderr,
        )
        return 2

    data = summary(ordered, failures)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(
            {"version": 1, "summary": data, "sources": [asdict(record) for record in ordered]},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_csv(args.csv_output, ordered)
    write_summary(args.summary_output, data)
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
