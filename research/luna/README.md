# Luna: daily data-engineering and analytics research

This pack turns the editorial mechanics of [Scaling Postgres](https://www.scalingpostgres.com/episodes/) into a broader daily research workflow for data engineering and technical analytics. It does not copy the channel's scripts. It borrows the useful system: scan many technical sources, choose a small number of consequential stories, trace each story to its original evidence, and explain the production impact concisely.

## What's here

- `sources.json` — 40 live RSS/Atom feeds, primary release feeds, topic beats, and a manual web watchlist.
- `source_catalog.csv` / `source_catalog.json` — more than 1,000 distinct data-and-analytics websites and blogs, with provenance, topical classification, evidence tier, and review status.
- `source_catalog_summary.md` — catalogue counts and coverage distribution.
- `build_source_catalog.py` — reproducibly rebuilds the large catalogue from curated seeds and editorial archives.
- `query_source_catalog.py` — produces a ranked source watchlist for any known or ad-hoc topic.
- `contexts.json` — all 55 DAT contexts from the supplied SSPEC audit, plus a detailed SAP-extraction profile.
- `source_families.json` — the evidence-source families and expansion endpoints used for topics not yet represented in the catalogue.
- `topic_sources/sap-extraction.json` — worked authoritative source map for SAP extraction and replication.
- `daily_research.py` — dependency-free collector, freshness filter, canonical-URL deduplication, and initial relevance ranking.
- `luna_prompt.md` — Luna's research and editorial contract.
- `reference_channel_analysis.md` — findings from the full public channel catalogue, all public episode source pages, and a transcript sample spanning the series.
- `scrape_scaling_postgres.py` — reproducible archive/source-corpus builder.

## Daily run

Run from the repository root:

```bash
python3 research/luna/daily_research.py \
  --output research/luna/runs/candidates-$(date +%F).md \
  --json-output research/luna/runs/candidates-$(date +%F).json
```

Use 96 hours on Monday to bridge the weekend:

```bash
python3 research/luna/daily_research.py \
  --lookback-hours 96 \
  --output research/luna/runs/candidates-$(date +%F).md
```

Then give the candidate file and `luna_prompt.md` to Luna. Luna must open the shortlisted articles and their primary evidence before writing; feed summaries are discovery aids only.

## Find sources for any topic

Search by a plain-language topic, a DAT coordinate, or a registered alias:

```bash
python3 research/luna/query_source_catalog.py "SAP extraction" --limit 50
python3 research/luna/query_source_catalog.py DAT-020 --limit 50
python3 research/luna/query_source_catalog.py "Snowflake cost optimization" --limit 50
```

When catalogue matches are thin, the output includes expansion links for GitHub, advisories, research indexes, Stack Overflow, Hacker News, Google News, and conference/video discovery. This allows Luna to cover thousands of topics without pretending a static list can be complete forever.

## Rebuild the 1,000+ source catalogue

First build the Scaling Postgres corpus, then merge it with all Data Engineering Weekly archive issues and the curated/profile sources:

```bash
python3 research/luna/scrape_scaling_postgres.py \
  --output research/luna/runs/scaling-postgres-corpus.json

python3 research/luna/build_source_catalog.py \
  --scaling-corpus research/luna/runs/scaling-postgres-corpus.json \
  --json-output research/luna/source_catalog.json \
  --csv-output research/luna/source_catalog.csv \
  --summary-output research/luna/source_catalog_summary.md \
  --minimum-sources 1000
```

`discovered-unreviewed` means exactly that: the site appeared in a specialist editorial archive but has not been individually endorsed. Curated and repeatedly discovered sources rank above one-off leads.

## Refresh the reference corpus

The archive scraper reads the episode sitemap and every `Content Discussed` section:

```bash
python3 research/luna/scrape_scaling_postgres.py \
  --output research/luna/runs/scaling-postgres-corpus.json
```

The resulting corpus can be large, so it is generated on demand rather than committed.

## Operating notes

- Default lookback is 72 hours. This accommodates sources that publish in different time zones without allowing week-old filler.
- Feed ranking is intentionally only a first pass. A high score is not permission to publish.
- Release-candidate, nightly, event, partnership, and funding items are heavily down-ranked.
- Vendor benchmarks require methodology review and, where possible, a second source or reproducible code.
- If a feed fails, keep the failure in the candidate report and repair or replace the source. Silent gaps are not acceptable.
