# Industry taxonomy and evidence foundation

This folder is the classification substrate for the vertical analytical-needs atlas. It gives every
industry pack stable, edition-qualified scope identifiers and makes classification loss visible. It
does **not** claim that an economic-activity code is a product, a bounded context, an analytical
case, or a complete description of an industry.

## Result

The global activity spine is the complete official ISIC Revision 5 structure pinned to SHA-256
`fc408f57bd3a4f33c35a4f384ec0010283dd72774892c8d48ae1330a8caeb57f`:

| Level | Nodes |
| --- | ---: |
| Section | 22 |
| Division | 87 |
| Group | 258 |
| Class | 463 |
| **Total** | **830** |

The research foundation also registers 27 scheme editions or analytical overlays and 44 verified
authoritative sources from 23 publishers. These include jurisdictional activity views for North
America, the EU, Australia/New Zealand, the UK, Singapore and India, plus specialist views for
health, education, tourism, agriculture, energy, environment, digital activity, government,
nonprofits, critical infrastructure, the marine economy and insurance regulation.

ISIC Revision 5 is used as a **reference spine**, not a universal ontology. UNSD states that its
structure is endorsed and available while the formal publication is forthcoming. Likewise, this
corpus distinguishes final classification state from operational adoption: UK SIC 2026 is final but
ONS adoption is phased, and the SIEC Version 2 structure was endorsed in March 2026 while its
explanatory notes and correspondences are still being finalized.

## Identity contract

An industry identity freezes one semantic boundary in one classification edition:

```text
industry.isic5.section.l       Financial and insurance activities
industry.isic5.division.c64   Financial service activities, except insurance and pension funding
industry.isic5.group.c641      Monetary intermediation
industry.isic5.class.c6419     Other monetary intermediation
```

The leading `c` makes numeric codes valid dotted atlas identifiers; the official code remains in
`scheme_code`. IDs are never silently carried across editions. A later edition either retains the
boundary through an evidence-bearing mapping or receives a new edition-qualified identity.

Vertical packs should use a registered node for `industry_id` and `subindustry_ids`. A local
extension is lawful only when the pack declares its parent, semantic boundary, jurisdiction,
edition, evidence and unresolved mapping back to the reference spine. Free-text labels alone are
not scope.

## Orthogonal classification graphs

The foundation prevents common category errors:

```text
economic activity  ISIC / NACE / NAICS / national SICs
product            CPC / HS / SIEC / crop classifications
provider           SHA ICHA-HP
function/purpose   COFOG / SHA health functions
programme/field    ISCED / ISCED-F
regulatory line    NAIC market-conduct lines of business
criticality        CISA critical-infrastructure sectors
analytical overlay tourism / digital / environment / marine economy / nonprofit
```

These graphs can be crosswalked but are not parent-child substitutes. A hospital provider type is
not identical to a hospital economic activity; an energy product is not an energy producer; a
tourism industry is partly defined by visitor demand; and a critical-infrastructure sector can span
many ordinary industries.

## Crosswalk semantics

`crosswalks.jsonl` encodes mapping assertions as reviewable objects. Every assertion includes:

- source and target scheme editions and member extents;
- equivalence, subset, superset, overlap, disjoint or unresolved relation;
- one-to-one, one-to-many, many-to-one or many-to-many cardinality;
- single, union, intersection or allocation semantics;
- concept, statistical-unit, geography, time and inclusion/exclusion compatibility;
- semantic losses, allocation rules, evidence and two-role review posture; and
- a transitivity decision, which defaults to forbidden.

An official correspondence table is not automatically a record recode or a time-series bridge.
Partial codes require an extent qualifier. Allocation weights must be official or empirically tied
to a stated population and period; otherwise compilation refuses the mapping.

The seed assertions intentionally include:

- exact named unions for OECD ICT manufacturing and trade overlays;
- partial-code extents for tourism accommodation;
- an unresolved country-specific tourism retail category; and
- a refused equivalence between SHA hospital-provider type and ISIC hospital activity.

## Evidence and completion rules

`evidence-policy.json` defines authority tiers, claim/source obligations, freshness, mapping
evidence and refusal conditions. `claims.jsonl` separates direct support from inference and records
defeaters. The source registry conforms to the shared industry `source_evidence` record shape.

`completeness-policy.json` has 12 coverage dimensions and nine gates. The crucial boundary is:

```text
complete ISIC hierarchy
!= complete national detail
!= complete specialist ontology
!= complete crosswalk coverage
!= complete analytical-needs coverage
```

Each vertical family still needs its own 25+ authoritative sources and must account for every
in-scope leaf or justified aggregation with analytical cases, source-system needs, data shapes or a
typed gap. Foundation sources count only when directly relevant and explicitly cited. A KPI name
never closes an analytical case: the shared record still requires the question, actors, decision or
action, grain, time, systems, shapes, methods, operations, evidence, uncertainty and failure modes.

## Review

`review-policy.json` defines classification, jurisdiction, domain, evidence and vertical-pack
stewards. Lossy, cross-axis, partial, allocation-bearing or jurisdiction-changing mappings require
independent classification and domain/jurisdiction review. A source or mapping review applies only
to the exact artifact edition reviewed.

Re-review is mandatory on a new edition, corrigendum, adoption change, changed correspondence,
new national extension, conflicting evidence, digest failure or a vertical boundary that cannot be
expressed by registered nodes.

## Files

- `isic-rev5.nodes.jsonl` — all 830 edition-frozen global activity nodes.
- `classification-schemes.json` — 27 cross-industry, jurisdictional and specialist scheme records.
- `sources.jsonl` — 44 authoritative evidence records.
- `claims.jsonl` — evidence-bearing foundation claims and limitations.
- `crosswalks.jsonl` — typed seed mappings and explicit refusals.
- `evidence-policy.json` — evidence authority, provenance, freshness and refusal rules.
- `completeness-policy.json` — coverage dimensions, gates and anti-completion claims.
- `review-policy.json` — roles, state transitions, review checks and re-review triggers.
- `schema/` — JSON Schemas for scheme, node, crosswalk and claim records.
- `build_isic_rev5.py` — deterministic, digest-pinned import from the official UNSD CSV.
- `validate_foundation.py` — referential, hierarchy, digest, policy and optional JSON Schema checks.
- `manifest.json` — pinned counts, digests and completion posture.

## Rebuild and verify

Download the official [UNSD ISIC Revision 5 structure CSV](https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/ISIC_Rev_5_english_structure.csv), then run:

```bash
python3 build_isic_rev5.py /path/to/ISIC_Rev_5_english_structure.csv
python3 validate_foundation.py
uv run --with jsonschema python validate_foundation.py --schemas
```

The builder refuses a source whose digest differs. A legitimate upstream correction therefore
requires a new import edition, updated digest, review and migration record rather than an in-place
overwrite.

## Primary methodological anchors

- [UNSD ISIC Revision 5](https://unstats.un.org/unsd/classifications/Econ/isic/4)
- [UN classification best practices](https://unstats.un.org/unsd/classifications/Meetings/UNCEISC2022/UNCEISC_2022_meeting_Session_1_Bk3_Best_Practice.pdf)
- [UNECE GSIM classification model](https://statswiki.unece.org/spaces/gsim/pages/97356506/1_Introduction)
- [W3C SKOS mapping semantics](https://www.w3.org/TR/skos-reference/)
- [W3C PROV-O](https://www.w3.org/TR/prov-o/)
- [Eurostat NACE correspondence guidance](https://ec.europa.eu/eurostat/web/nace/correspondence-tables)
- [OECD health-account classifications](https://www.oecd.org/en/publications/best-practice-in-institutionalising-health-accounts_cf997130-en/full-report/key-classifications-of-the-system-of-health-accounts-2011_a2857acf.html)
- [UN Tourism IRTS 2008](https://unstats.un.org/unsd/publication/seriesm/seriesm_83rev1e.pdf)
- [UN Statistical Commission Decision 57/121](https://unstats.un.org/UNSDWebsite/statcom/session_57/documents/2026-35-FinalReport-EE.pdf)

All 44 sources and their limitations are in `sources.jsonl`.
