#!/usr/bin/env python3
"""Query Luna's website catalogue and emit a topic-specific research watchlist."""

from __future__ import annotations

import argparse
import json
import math
import re
import urllib.parse
from pathlib import Path
from typing import Any, Optional


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9+#.]+", value.lower()))


def resolve_terms(
    topic: str, contexts: dict[str, Any]
) -> tuple[str, list[str], list[str], Optional[str]]:
    wanted = normalized(topic)
    for context in contexts["contexts"]:
        labels = [context["id"], context["name"], *context.get("aliases", [])]
        if wanted in {normalized(label) for label in labels}:
            terms = [context["name"], *context.get("aliases", [])]
            facets: list[str] = []
            profile_id = context.get("profile")
            if profile_id:
                profile = next(
                    item for item in contexts["topic_profiles"] if item["id"] == profile_id
                )
                terms.extend([profile["name"], *profile.get("aliases", []), *profile.get("query_terms", [])])
                facets = list(profile.get("required_facets", []))
            return f"{context['id']} — {context['name']}", terms, facets, profile_id
    for profile in contexts["topic_profiles"]:
        labels = [profile["id"], profile["name"], *profile.get("aliases", [])]
        if wanted in {normalized(label) for label in labels}:
            return (
                profile["name"],
                [profile["name"], *profile.get("aliases", []), *profile.get("query_terms", [])],
                list(profile.get("required_facets", [])),
                profile["id"],
            )
    return topic, [topic], [], None


def source_score(source: dict[str, Any], terms: list[str]) -> float:
    haystack = normalized(
        " ".join(
            [
                source["domain"],
                source["name"],
                *source["topics"],
                *source.get("facets", []),
                *source["sample_titles"],
                *source["sample_urls"],
            ]
        )
    )
    score = 0.0
    matched = False
    for term in terms:
        term_normalized = normalized(term)
        tokens = [token for token in term_normalized.split() if len(token) > 1]
        if term_normalized and term_normalized in haystack:
            score += 12
            matched = True
        token_hits = sum(token in haystack for token in tokens)
        if tokens and token_hits == len(tokens):
            score += 5 + token_hits
            matched = True
        elif token_hits:
            score += token_hits * 0.5
    if not matched:
        return 0.0
    score += {"curated": 8, "repeatedly-discovered": 4}.get(source["review_status"], 0)
    score += max(0, 5 - int(source["evidence_tier"]))
    score += min(6, math.log2(1 + int(source["discovery_count"])))
    return round(score, 2)


def discovery_links(topic: str, families: dict[str, Any]) -> list[dict[str, str]]:
    query = urllib.parse.quote_plus(topic)
    return [
        {
            "name": endpoint["id"],
            "family": endpoint["family"],
            "url": endpoint["url_template"].format(query=query),
        }
        for endpoint in families["discovery_endpoints"]
    ]


def render_markdown(
    label: str,
    topic: str,
    sources: list[tuple[float, dict[str, Any]]],
    facets: list[str],
    curated_endpoints: list[dict[str, Any]],
    discovery: list[dict[str, str]],
) -> str:
    lines = [
        f"# Source watchlist: {label}",
        "",
        f"Query: `{topic}` · matched sources: **{len(sources)}**",
        "",
    ]
    if facets:
        lines.extend(["## Required coverage facets", "", *[f"- {facet}" for facet in facets], ""])
    if curated_endpoints:
        lines.extend(["## Curated topic endpoints", ""])
        for source in curated_endpoints:
            lines.append(
                f"- [{source['name']}]({source['url']}) — tier {source['tier']}, {source['family']}, {source['access']}"
            )
        lines.append("")
    lines.extend(["## Ranked sources", ""])
    for score, source in sources:
        lines.extend(
            [
                f"### {score:.2f} — [{source['name']}]({source['homepage']})",
                "",
                f"`{source['domain']}` · tier {source['evidence_tier']} · {source['review_status']} · seen {source['discovery_count']} times",
                "",
                f"Topics: {', '.join(source['topics'])}",
                "",
            ]
        )
    lines.extend(["## Expansion searches", ""])
    lines.extend(f"- [{item['name']}]({item['url']}) — {item['family']}" for item in discovery)
    lines.extend(
        [
            "",
            "A catalogue match is a lead, not evidence. Open the current primary documentation or artifact before using a claim.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic")
    parser.add_argument("--catalog", type=Path, default=here / "source_catalog.json")
    parser.add_argument("--contexts", type=Path, default=here / "contexts.json")
    parser.add_argument("--families", type=Path, default=here / "source_families.json")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-tier", type=int, default=4)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    contexts = json.loads(args.contexts.read_text(encoding="utf-8"))
    families = json.loads(args.families.read_text(encoding="utf-8"))
    label, terms, facets, profile_id = resolve_terms(args.topic, contexts)
    curated_endpoints: list[dict[str, Any]] = []
    if profile_id:
        profile_path = here / "topic_sources" / f"{profile_id}.json"
        if profile_path.exists():
            curated_endpoints = json.loads(profile_path.read_text(encoding="utf-8"))["sources"]
    ranked = sorted(
        (
            (score, source)
            for source in catalog["sources"]
            if int(source["evidence_tier"]) <= args.max_tier
            if (score := source_score(source, terms)) > 0
        ),
        key=lambda item: (-item[0], item[1]["domain"]),
    )[: max(1, args.limit)]
    discovery = discovery_links(args.topic, families)

    if args.json:
        rendered = json.dumps(
            {
                "topic": args.topic,
                "label": label,
                "required_facets": facets,
                "curated_topic_endpoints": curated_endpoints,
                "sources": [{"score": score, **source} for score, source in ranked],
                "expansion_searches": discovery,
            },
            indent=2,
            ensure_ascii=False,
        )
    else:
        rendered = render_markdown(
            label, args.topic, ranked, facets, curated_endpoints, discovery
        )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
