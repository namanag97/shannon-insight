# Frontier accounting — lossless disposition of the gap-convergence starting frontier

Scope: the complete P01–P07 frontier as of the frozen snapshot (`frozen_inputs/manifest.json`
binds 20 upstream artifacts by SHA-256): **686 gap clusters representing 16,717 atoms**
(the externally circulated "16,687" predates an upstream regeneration; see reconciliations).

## What is here

| Artifact | Rows | Content |
|---|---|---|
| `frontier-ledger.jsonl` | 686 | one exit-port per cluster; authority role + required receipt kind |
| `atom-chains.jsonl` | 16,732 | atom→cluster→upstream-record chains, Σweight = 16,717 (15 zero-weight rows carry the documented live-file drift) |
| `reconciliations.jsonl` | 5 | stale-number corrections; 982-vs-674 denominators; derived 1008 obligations; 873-vs-888 vacancy drift; wave-4 gate |
| `p01-authority-packets.jsonl` | 23 | source-authority decision packets: 22 with internet-verified candidate authorities (39 citations), 1 honest vacancy (`consumption_bi_visualization`) |
| `p02-symbol-dispositions.jsonl` | 210 | per-docket recommendations: 92 ENDORSE_*; 118 RESEARCH_ACTIONS (exactly the challenge-package-blocked set); every row links docket+collision+decision-unit+wave |
| `p03-axis-evidence-packs.jsonl` | 103 | family×axis evidence packs instantiated from six researched axis templates (35 verified primary sources across identity/equality, composition algebra, grain/cardinality, order/topology, partiality/uncertainty, state/change), all unverified sources excluded into typed vacancies |
| `p04-ratification-workplan.jsonl` | 368 | join to review dockets: 258 → LIBRARY_OWNER ratification gates, 103 → blocked-with-P03-dependency, 7 → modal research |
| `frontier-summary.json` | — | dashboards + completion_claim=false |

Research provenance: 10 background agents produced the Wave-1 axis templates and Wave-2
authority discoveries over the live web (2026-08-27); their raw transcripts stay out of
canonical space, merged fragments live under `axis_templates/` and `family_authorities.json`.

## What this does NOT claim

Every port above is a **typed gate** naming its owner role and receipt kind. Research cannot
ratify owners, publish contracts for other lanes, implement, or qualify — so completion_claim
stays false. Nothing canonical was modified anywhere.

## Validate

    python3 build_frontier.py && python3 validate_frontier.py
Laws: ledger partition + port legality, Σchain weights == Σsnapshot atoms == 16,717,
per-cluster equality, drift flags mandatory on zero weights, frozen-copy digest integrity,
artifact count checks (23/210/103/368), sorted deterministic output, no CLOSED ports.
Exit path taken by this run: FRONTIER VALIDATOR PASSED.

## C-wave addendum (2026-08-27): symbol-conflict appraisal research

All six researcher slices merged (`waves/conflict_appraisals/slice0..5.jsonl`):
**85 unique owner conflicts appraised** across the 210 dockets. Outcomes: 47
INTERNAL_SEMANTICS_NO_EXTERNAL_AUTHORITY, 21 STANDOFF_CONFIRMED, **17
DECISIVE_EVIDENCE_FOUND** (incl. Cockburn hexagonal-architecture adjudicating seven
port-vs-adapter collisions; Process Mining Manifesto; Vega-Lite/Prometheus/nbformat/
Jupyter splits; MathML meaning-before-lineage). Dispositions: QUALIFY_LOCAL 33 ·
FAMILY_SHARED 21 · CANONICAL_SHARED 16 · UNRESOLVED_WITH_REASON 12 · HOMONYM_RENAME 3.
52 conflicts carry live-verified citations; 45 carry typed vacancies naming exactly what
an owner session must supply. **21 verdict disagreements between researcher batches are
preserved verbatim in `waves/DISSENTS.md`** — owner sessions adjudicate, this lane never
resolves dissent by overwrite. Notable standing dispute: AppraisalPolicy
(shared-import-with-profile per lane dossier v2 vs qualified-homonym per slice-0 law read).
