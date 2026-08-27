# Reference-channel analysis: Scaling Postgres

Analyzed on 2026-08-11 from the public [YouTube channel](https://www.youtube.com/@ScalingPostgres/videos), the [episode archive](https://www.scalingpostgres.com/episodes/), its sitemap, episode `Content Discussed` lists, and auto-caption transcripts sampled across episodes 1, 50, 100, 150, 200, 250, 300, 350, 400, and 429.

## Corpus

| Material | Coverage | Result |
|---|---:|---:|
| YouTube catalogue metadata | Entire public catalogue | 438 videos |
| Numbered episode source pages | Entire public sitemap | 429 pages |
| Curated `Content Discussed` links | Every public episode page | 7,324 links |
| Distinct linked URLs | Every public episode page | 7,238 URLs |
| Distinct linked domains | Every public episode page | 655 domains |
| Auto-caption transcript sample | Series-spanning sample | 10 episodes |

The catalogue has 429 numbered roundups plus nine early standalone/tutorial videos. The sitemap contains two pages numbered 214 and no page numbered 218, which explains why 429 pages do not map one-to-one to episode numbers 1–429.

## What makes the format work

1. **Curation is the product.** Each episode page links to a median of 14 sources (17.1 average), while the spoken episode promotes roughly four lead topics and then moves through a faster ecosystem roundup.
2. **The hook is concrete.** Titles emphasize a measurable result, an architectural tension, a failure mode, or a consequential release—not an abstract category.
3. **The host adds judgment.** Transcripts do more than summarize: they question benchmark context, point out operational trade-offs, and explain who should care.
4. **The unit is short.** Across all 438 catalogue entries, median duration is about 15.2 minutes. The ten sampled transcripts ranged from 12.2 to 19.2 minutes and averaged roughly 2,670 words.
5. **Discovery is broad but selection is narrow.** The latest 20 source pages contained 627 links from 105 domains. Repeated scanning creates coverage; editorial filtering creates value.

## Historical source shape

The most-linked domains across the full archive were:

| Domain | Links |
|---|---:|
| cybertec-postgresql.com | 503 |
| timescale.com | 250 |
| crunchydata.com | 244 |
| enterprisedb.com | 235 |
| postgresql.life | 207 |
| postgres.fm | 179 |
| depesz.com | 176 |
| pganalyze.com | 174 |
| supabase.com | 160 |
| stormatics.tech | 155 |
| percona.com | 154 |
| highgo.ca | 150 |
| postgresql.org | 123 |
| citusdata.com | 120 |
| dbi-services.com | 118 |
| tigerdata.com | 116 |
| thebuild.com | 113 |
| aws.amazon.com | 110 |
| pgedge.com | 78 |
| postgres-contrib.org | 70 |

This mix is strong for Postgres internals, operations, and performance, but it is structurally too narrow for the requested brief. Only about 8% of numbered-episode titles/descriptions explicitly center analytics or data-engineering terms, and only about 2% center AI/agent topics. Luna's source pack therefore retains the channel's strongest database sources while adding primary coverage for Spark, Iceberg, Trino, DuckDB, ClickHouse, Kafka, Flink, Debezium, Airflow, Dagster, Prefect, dbt, metadata/quality systems, and semantic/BI tooling.

## Editorial pattern to retain

- Open on one high-consequence claim or architectural change.
- Cover three to five verified stories, not everything collected.
- Explain mechanism and operational consequence.
- Link every claim to the original material.
- Add a rapid release/watchlist section only after the main stories.
- Preserve uncertainty around vendor benchmarks and early releases.

## Patterns not to copy

- Do not inherit a Postgres-only beat.
- Do not treat every source-page link as equally important.
- Do not repeat host phrasing, scripts, or personality.
- Do not use auto-captions as factual evidence when the linked primary source is available.
- Do not turn a daily brief into a 15-minute inventory; tighter daily selection should beat weekly volume.

## Reproduction

Run `scrape_scaling_postgres.py` to rebuild the link corpus. YouTube catalogue metadata and auto-captions were used for structural analysis only and are not stored in this repository.

