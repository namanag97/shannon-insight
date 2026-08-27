#!/usr/bin/env python3
"""Build a source corpus from the Scaling Postgres episode archive.

The public episode pages contain a curated ``Content Discussed`` list.  Those
links are more reliable for source discovery than attempting to infer URLs from
YouTube captions.  This script uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import concurrent.futures
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
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

SITEMAP_URL = "https://www.scalingpostgres.com/sitemap.xml"
USER_AGENT = "LunaResearch/1.0 (+source-corpus-builder)"


@dataclass(frozen=True)
class DiscussedLink:
    title: str
    url: str
    domain: str


@dataclass(frozen=True)
class Episode:
    number: int
    title: str
    description: str
    page_url: str
    youtube_id: Optional[str]
    links: list[DiscussedLink]


class EpisodeParser(HTMLParser):
    """Extract the title, summary, YouTube ID, and discussed links."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.youtube_id: Optional[str] = None
        self.links: list[DiscussedLink] = []
        self._capture_h1 = False
        self._capture_lead = False
        self._capture_h2 = False
        self._h2_text: list[str] = []
        self._in_discussed = False
        self._link_url: Optional[str] = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "h1" and not self.title:
            self._capture_h1 = True
        elif tag == "p" and "lead" in classes and not self.description:
            self._capture_lead = True
        elif tag == "h2":
            self._capture_h2 = True
            self._h2_text = []
        elif tag == "a" and self._in_discussed and values.get("href"):
            self._link_url = values["href"]
            self._link_text = []
        elif tag == "iframe":
            match = re.search(r"youtube\.com/embed/([\w-]+)", values.get("src") or "")
            if match:
                self.youtube_id = match.group(1)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self._capture_h1 = False
        elif tag == "p":
            self._capture_lead = False
        elif tag == "h2" and self._capture_h2:
            heading = " ".join("".join(self._h2_text).split()).lower()
            self._in_discussed = heading == "content discussed"
            self._capture_h2 = False
        elif tag == "a" and self._link_url:
            title = " ".join("".join(self._link_text).split())
            parsed = urllib.parse.urlparse(self._link_url)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                domain = parsed.netloc.lower().removeprefix("www.")
                self.links.append(DiscussedLink(title, self._link_url, domain))
            self._link_url = None
            self._link_text = []

    def handle_data(self, data: str) -> None:
        if self._capture_h1:
            self.title += data
        if self._capture_lead:
            self.description += data
        if self._capture_h2:
            self._h2_text.append(data)
        if self._link_url:
            self._link_text.append(data)


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


def episode_urls(sitemap: bytes) -> list[str]:
    root = ET.fromstring(sitemap)
    urls = [element.text or "" for element in root.findall("{*}url/{*}loc")]
    return sorted(
        (url for url in urls if "/episodes/" in url and re.search(r"/episodes/\d+-", url)),
        key=episode_number,
    )


def episode_number(url: str) -> int:
    match = re.search(r"/episodes/(\d+)-", url)
    return int(match.group(1)) if match else 0


def parse_episode(url: str) -> Episode:
    parser = EpisodeParser()
    parser.feed(fetch(url).decode("utf-8", errors="replace"))
    return Episode(
        number=episode_number(url),
        title=" ".join(parser.title.split()),
        description=" ".join(parser.description.split()),
        page_url=url,
        youtube_id=parser.youtube_id,
        links=parser.links,
    )


def build_corpus(urls: Iterable[str], workers: int) -> list[Episode]:
    episodes: list[Episode] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_urls = {executor.submit(parse_episode, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_urls):
            url = future_urls[future]
            try:
                episodes.append(future.result())
            except Exception as exc:  # continue so one stale page does not lose the corpus
                print(f"warning: {url}: {exc}", file=sys.stderr)
    return sorted(episodes, key=lambda item: item.number)


def summary(episodes: list[Episode]) -> dict[str, object]:
    domains = Counter(link.domain for episode in episodes for link in episode.links)
    return {
        "episodes": len(episodes),
        "discussed_links": sum(len(episode.links) for episode in episodes),
        "unique_domains": len(domains),
        "top_domains": [{"domain": domain, "links": count} for domain, count in domains.most_common(75)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="JSON output path")
    parser.add_argument("--workers", type=int, default=8, help="concurrent requests (default: 8)")
    parser.add_argument("--limit", type=int, default=0, help="only fetch the newest N episodes")
    args = parser.parse_args()

    urls = episode_urls(fetch(SITEMAP_URL))
    if args.limit:
        urls = urls[-args.limit :]
    episodes = build_corpus(urls, max(1, args.workers))
    payload = {
        "reference": {
            "channel": "Scaling Postgres",
            "channel_id": "UCnfO7IhkmJu_azn0WbIcV9A",
            "youtube_url": "https://www.youtube.com/@ScalingPostgres/videos",
            "sitemap_url": SITEMAP_URL,
        },
        "summary": summary(episodes),
        "episodes": [asdict(episode) for episode in episodes],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
