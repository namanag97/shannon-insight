# Boundary maps

## Orthogonal ownership graphs

```text
SEMANTIC GRAPH                    PRODUCT GRAPH

vertical context ──ACL────┐      user/job/outcome
source context ────ACL────┼──►   product promise ──contained-in──► suite
metric context ────API────┤             │
authority context ─grant──┘             ├──requires──► capability contract
                                        ├──composes──► other product promise
No product gains ownership              └──packaged-by► solution/industry pack
from composition.                             (no semantic re-ownership)

IMPLEMENTATION GRAPH

capability requirement
        │ exact satisfaction + evidence
        ▼
provider offer ──implemented-by──► library ──realized-by──► module/runtime
        │                                                   │
        └──────── substitution + exit contract ◄────────────┘

Repository dependency != semantic authority.
Provider selection     != product identity.
Suite entitlement      != product boundary.
```

## Boundary decision

```text
candidate promise
      │
      ├─ distinct user and job? ────────────── no ──► capability/module
      │ yes
      ├─ independently adoptable? ──────────── no ──► merge/defer
      │ yes
      ├─ operable + supportable? ───────────── no ──► shared implementation
      │ yes
      ├─ billable/allocatable? ─────────────── no ──► gather economic evidence
      │ yes
      ├─ independent exit + substitution? ──── no ──► refuse/defer
      │ yes
      ├─ unique semantics and authority? ───── no ──► narrow/ACL/refuse
      │ yes
      └─ lifecycle + interface + evidence? ─── yes ─► product candidate
                                                       (ratification withheld)
```

## Service blueprint

```text
consumer:  discover ─ evaluate ─ adopt ─ configure ─ use ─ support ─ exit
               │          │         │         │        │       │        │
frontstage: promise    evidence   declaration status  outcome case   export
               │          │         │         │        │       │        │
backstage: registry ─ qualification ─ binding ─ operate ─ meter ─ recover
               │          │         │         │        │       │        │
receipts:   source     decision   adoption  config   runtime incident exit

Every handoff can refuse. "Unknown" is not silently lowered to a default.
```

## Horizontal products and industry packs

```text
          HORIZONTAL PRODUCTS + METHOD CONTRACTS (meanings unchanged)

          forecast  process-mining  geospatial  policy  quality  BI  publish
              ▲           ▲             ▲          ▲       ▲     ▲      ▲
              │ typed requirement/offer + ACL + authority + evidence     │
 ┌────────────┼───────────┼─────────────┼──────────┼───────┼─────┼──────┼──┐
 │ HEALTH PACK│           │             │          │       │     │      │  │
 │ terms/case/population/grain/rules/source mappings/clinical authority  │
 └────────────┼───────────┼─────────────┼──────────┼───────┼─────┼──────┼──┘
 ┌────────────┼───────────┼─────────────┼──────────┼───────┼─────┼──────┼──┐
 │ ENERGY PACK│           │             │          │       │     │      │  │
 │ terms/case/population/grain/rules/source mappings/asset authority     │
 └────────────┼───────────┼─────────────┼──────────┼───────┼─────┼──────┼──┘
 ┌────────────┼───────────┼─────────────┼──────────┼───────┼─────┼──────┼──┐
 │ PUBLIC PACK│           │             │          │       │     │      │  │
 │ terms/case/population/grain/rules/source mappings/statutory authority │
 └────────────────────────────────────────────────────────────────────────┘

Industry pack = vertical composition, not horizontal product.
Vertical authority never flows upward into a generic engine.
```

## Analytical method and product refusal

```text
vertical business question + population + decision authority
                              |
                              v
                  analytical practice / study design
                              |
                              v
          formal method / estimand / model / assumptions
                              |
                              v
              algorithm -> kernel -> reusable library
                              |
                              v
             governed execution environment / workbench
                              |
                              v
          independently adopted product, only if proven
                              |
                              v
              reviewed decision handoff -> effect product

Retained product candidates:

  experimentation platform      assignment/exposure/metric-cut/conclusion lifecycle
  forecasting workbench         origin/horizon/backtest/distribution/override lifecycle
  optimization solver           exact model/tolerance/status/solution/certificate
  process-mining workbench      projection/project/discovery/conformance/finding lifecycle
  geospatial workbench          project/layer/CRS/workflow/history/result lifecycle
  simulation environment        model/scenario/experiment/seed/replication lifecycle

Reclassified method/library families:

  statistics  causal inference  anomaly/change  graph  text/document  media/signal

estimate != fact != forecast != causal effect != authorized decision
solver solution != business command
anomaly finding != incident or root cause
graph path != causal path
simulation distribution != prediction
```

```text
automation posture at each use site

  PROHIBITED | OPTIONAL | REQUIRED_BY_INTENT | UNDETERMINED
                      |
                      v
human / deterministic / OR-statistics / predictive model /
generative model / tool-using agent / declared hybrid
                      |
                      v
typed request -> allowed tools -> attributed proposal -> deterministic checks -> review
                      |
                      v
             separate authority/effect boundary

Default = deterministic core. Removing optional model/LLM/agent support leaves a
conformant core path or an explicit capability-unavailable compiler gap.
```

## Lakehouse refusal

```text
Lakehouse suite / experience
       │
       ├── table-state semantic contract
       │      ├── Iceberg / Delta / Hudi exact standards
       │      ├── typed capabilities
       │      └── pure libraries + unqualified implementations
       ├── catalog + commit product ─── namespace/authority/export exit
       ├── analytical query product ── plan/result/cancellation exit
       ├── ingestion product ───────── source-cut/delivery exit
       ├── managed maintenance product  destructive-authority/budget exit
       ├── data-sharing product ─────── disclosure/revocation exit
       ├── data-use policy neighbor ─── policy/grant/revocation exit
       └── managed experience product ─ declaration/status/support exit

One SKU may contain all branches. A table standard/library is not a product, and one suite may not
become the semantic owner of all branches.
```

## Data movement refusal

```text
Data integration suite
       |
       +-- connectivity product ------ connection declaration/binding/revocation
       +-- CDC product --------------- source snapshot/log cursor/stitching
       +-- ingestion product --------- source-to-target delivery cursor/receipt
       +-- orchestration product ----- schedule/run/task-attempt/retry/backfill
       +-- dataflow product ---------- event time/state/checkpoint/recovery
       +-- transform-build product --- manifest/selection/materialization/receipt
       +-- event-streaming product --- channel/partition/offset/retention/replay
       +-- activation product -------- destination mapping/authority/effect receipt

source cursor != broker offset != delivery cursor != workflow logical date
              != operator checkpoint != build receipt != destination receipt

Airflow task success        != data correctness or sink commit
Flink operator checkpoint   != end-to-end exactly-once effect
CloudEvents/Kafka transport != source payload meaning
analytical result           != authority to mutate an operational application
```

ETL, ELT, CDC and reverse ETL remain topology/processing patterns. A connector brand or plugin is
a provider offer. Independent adoption, operation, support, economics, exit and semantic authority
are required before any movement boundary is called a product.

## Catalog and governance refusal

```text
"catalog" / governance suite
        |
        +-- table catalog + commit authority ---- neighboring lakehouse product
        +-- metadata discovery ----------------- source-attributed projection/search
        +-- business glossary ------------------ human term/label/homonym approval
        +-- ontology + knowledge model --------- axiom/inference/shape editions
        +-- schema registry --------------------- subject/version/syntax compatibility
        +-- data-contract registry -------------- parties/promise/acceptance/SLA
        +-- master/reference data --------------- identity/survivorship/code authority
        +-- lineage/provenance ------------------ derivation assertions/evidence
        +-- quality/reconciliation -------------- scoped fitness/discrepancy/correction
        +-- data-use policy --------------------- decision/obligation (not enforcement)
        +-- data-product publication ------------ edition/contract/lifecycle/recall
        +-- marketplace ------------------------- listing/eligibility/fulfillment handoff

term != ontology class != schema field != master identity
schema compatibility  != data-contract acceptance
derivation            != causation
policy permit         != enforced effect or discharged obligation
publication           != listing != disclosure

optional model/agent proposal
        |
        v
typed schema -> deterministic owner validation -> scoped authority -> effect intent/receipt

No model or agent may skip the middle of this chain.
```

## Lifecycle and exit

```text
hypothesis → researched → specified → validated → adoptable → operating
                                                                │
                    retirement attestation ← retired ← exiting ← deprecated
                                                  ▲        │
                                                  │        ├─ export identities/state/data
                                                  │        ├─ disposition in-flight work
                                                  │        ├─ substitute conformance + replay
                                                  │        ├─ revoke routes/credentials/grants
                                                  │        └─ deletion/retention evidence
                                                  └────────────── exit receipt

Every arrow requires evidence; a version label alone is not a lifecycle transition.
```

## Ratification dependency

```text
adjudicated contexts + global context map
                  │
qualified libraries + provider occurrences + two implementations
                  │
typed compiler + semantic diff + operation totality
                  │
cross-provider SLO/security/commercial/exit drills
                  │
two-release vertical + unrelated-industry generality
                  │
independent appraisal
                  ▼
          bounded ratification verdict

Any unresolved blocking input yields cannot_ratify_until, never a guessed green check.
```
