# Platform, commercial, and customer-support universe

This is a **sourced research candidate**, not an adjudicated domain model and not a completeness
claim. It defines the horizontal product/service semantics needed to make generated enterprise
data and analytics solutions adoptable, billable, supportable, operable, portable, and removable.
It does not define an LLM/generative core, interpret full legal agreements, calculate jurisdictional
tax without a qualified provider, own security/privacy policy, or own physical runtime resources.

The current generated edition contains 63 bounded-context candidates and 428
capability/operation/decision/lifecycle/contract records. Its source registry contains 102 official
standards, specifications, frameworks, open-source documents, authority pages, and specialist
product APIs. Every claim is narrow: source authority is evidence for vocabulary or demonstrated
implementation behavior, not proof that this candidate context map is complete or correct.

## Decomposition

```text
PARTIES AND SCOPES
  TenantId ------------------------ isolation and platform ownership scope
      +-- tenant hierarchy -------- delegation/aggregation relation
      +-- AccountId --------------- product-facing grouping
      +-- OrganizationId ---------- customer-visible organizational unit
      +-- WorkspaceId ------------- collaboration/resource namespace
  CustomerId ---------------------- commercial relationship
  BillingAccountId ---------------- payer-facing invoice responsibility
  LegalEntityRef ------------------ externally verified counterparty reference
  PartyRef + Role ----------------- time-bounded participation

      none of these identifiers aliases another

COMMERCIAL DEFINITION                 CUSTOMER-SPECIFIC REALIZATION
  FeatureKey                          EntitlementGrant
  ProductOffering + edition    --->   Contract projection + amendment
  ServiceSpecification               Subscription + phase/items
  PlanVersion                         Trial / renewal
  PriceBook + RateCard                Suspension / termination
  Quote                               (no implicit deletion)

  catalog offer != signed contract != subscription != provisioned service

USAGE AND MONEY LINEAGE
  UsageEvent
      -> admission receipt
      -> tenant/customer/billing/workspace attribution
      -> MeterDefinition + windowed UsageAggregate
      -> RateCard/contract edition -> RatedUsage
      -> immutable ChargeEntry
      -> tax determination
      -> InvoiceLine -> finalized Invoice
      -> PaymentIntent / settlement / refund / credit note

  event != aggregate != rated usage != charge != invoice line != payment

FOUR INDEPENDENT ADMISSION QUESTIONS
  1. entitlement: may this customer use the commercial feature?
  2. authorization: may this principal perform this action on this data now?
  3. quota: is the technical consumption limit available?
  4. budget/credit: is finite spend or prepaid authority available?
  5. capacity: can the runtime actually place and execute the work?

  The fifth is deliberately shown: commercial control never proves physical feasibility.

ORDER TO OPERABLE SERVICE
  ProductOrder -> ServiceOrder -> ProvisioningPlan -> ServiceInstance receipt
                                  |
                                  +-> onboarding readiness
                                  +-> adoption/success evidence
                                  +-> catalog/inventory projection

SERVICE OPERATIONS
  alert/telemetry ---> Incident -----------------> mitigation/restoration
                          |                              |
  SupportCase -------- correlation                  Problem / known error
      |                   (not identity)                 |
      +-> severity -> escalation/on-call           corrective Change

  MaintenanceWindow -> approved Change -> observed impact
       planned facts      execution facts        outage/incident facts

  SLI -> internal SLO evaluation
                   != contractual SLA evaluation
                   != eligible/approved ServiceCredit

CUSTOMER COMMUNICATION AND EVIDENCE
  Incident/maintenance/support/usage/SLA facts
      -> audience-scoped StatusNotice
      -> integrity-bound CustomerEvidencePackage

EXIT
  termination
      -> ExitPlan
      -> export scope + schemas + lineage + manifest + checksums
      -> independent transfer/import verification
      -> dependencies/integrations/credentials disposition
      -> cutover and acceptance
      -> decommission/destruction or declared retention
      -> residual-obligation schedule and discharge evidence

  data export alone != product/supplier exit
```

## Context families

| Family | Candidate owners |
|---|---|
| Identity, hierarchy, isolation | tenant registry/hierarchy, account, organization, workspace, legal-entity binding, customer, party role, delegated administration, tenant isolation |
| Product definition and agreement | feature, entitlement policy/grant, licenses/seats, product/service catalogs, plans, price books, quotes, contract/amendment |
| Metering and money | meter, event intake, attribution, aggregation, rating, charge ledger, credits, billing account/cycle, invoice, tax, payment, refund/credit note |
| FinOps and limits | cost allocation, budget control, chargeback/showback, quota policy |
| Customer lifecycle and fulfillment | subscription, trial, renewal, suspension/termination, product/service order, provisioning, onboarding, adoption/success |
| Service and support | support case, severity, escalation, maintenance/change, status communication, incident, problem, SLO, SLA, service credit |
| Evidence and exit | customer evidence, portability export, supplier exit, decommission, residual obligation |

## Authority and tenant-isolation laws

Every command first resolves a tenant-scoped identity and validates an explicit authority reference.
Persistent keys, cache keys, idempotency scopes, stream partitions, logs/traces, support attachments,
exports, and provider bindings include `TenantId`. Unknown and unauthorized identifiers use the
same non-enumerating refusal. Cross-tenant aggregation requires separate purpose, authority,
minimization, and evidence; billing consolidation does not grant access to tenant data.

Commercial entitlement is input to product access, never a security authorization. Security,
privacy, hold, and disclosure prohibitions dominate commercial allowance. A provider adapter
rechecks tenant scope before an effect and returns a receipt that retains authority and exact
editions.

## Failure and refusal precedence

The compiler and generated services use this deterministic order. A later failure never masks an
earlier, higher-authority refusal:

```text
1 malformed input / unsupported schema or semantic edition
2 tenant-scope mismatch / non-enumeration
3 missing authority / security / privacy / hold prohibition
4 illegal lifecycle transition / stale aggregate edition
5 missing or exhausted commercial entitlement
6 technical quota exhaustion
7 hard budget reservation failure / prepaid credit depletion
8 physical resource infeasibility
9 provider refusal, timeout, or unknown outcome
10 post-commit reconciliation failure
```

A committed authoritative terminal fact outranks a caller timeout or cancellation observation. An
unknown provider outcome is reconciled through idempotency and receipts; it is not guessed to be a
failure. Maintenance does not outrank observed impact, an SLO breach does not produce a credit by
itself, and termination never outranks a retention/hold decision to trigger deletion.

## Compiler and library boundary

```text
product truth / enterprise intent
        |
        v
identity IR -> authority/privacy IR -> catalog/contract/subscription IR
        -> entitlement IR -> lifecycle IR
        -> quota + budget/credit IR -> runtime demand/feasibility IR
        -> qualified provider binding -> explicit effect intents
        -> receipts/lineage -> release + upgrade/rollback/exit proof

pure semantic/policy/algorithm libraries
        | emit values, decisions, refusals, effect intents
        v
effect ports
        | typed calls and receipts; no provider DTO leakage
        v
provider adapters
        | OpenMeter / Stripe / Peppol / TM Forum / PagerDuty / Statuspage / Zendesk
        v
provider occurrences and observations
```

Bindings in `requirements-offers-bindings.jsonl` are `candidate_not_proven`. A provider page or
passing schema check does not establish semantic equivalence. Release requires target probes,
tenant-isolation tests, replay/race/fault tests, version migration fixtures, and two independent
implementations for reusable library claims.

## Cross-universe ownership

- Security/privacy owns authorization, purpose, disclosure, retention/hold, and policy enforcement;
  this universe owns commercial feature scope and tenant-aware product operations.
- Runtime/resource owns demand, admission, capacity, allocation, attempts, and usage receipts; this
  universe owns commercial entitlement, technical product quota, budgets, rating, and invoices.
- Provider-target registry owns provider offers and occurrences; provider adapters here translate
  through anti-corruption ports.
- Product-boundary work owns the final product composition; `product-truth-mappings.jsonl` supplies
  candidate truth-to-owner mappings.
- Evidence/lineage owns general evidence semantics; this universe specifies which customer-facing
  commercial, support, service, and exit claims require evidence.
- Compiler/release owns final binding and refusal; this universe supplies requirements, offers,
  mappings, proof obligations, invalidators, and exit gates.

All six mappings remain explicitly `requires_adjudication`.

## Vertical examples

`vertical-examples.jsonl` traces two deliberately different deployments:

1. A regulated financial-risk analytics workspace with separate tenant, risk organization,
   workspace, group customer, local billing account, and verified legal entity; contract-fixed
   rating, distinct SLO/SLA/service-credit handling, and independently verified exit.
2. A multi-brand retail analytics platform with a parent tenant, brand organization/workspace,
   consolidated external billing, internal showback, workspace quotas and budgets, many-to-one case
   and incident correlation, and brand exit without deleting the group tenant.

They are illustrations, not reference architectures or compliance claims.

## Machine-readable artifacts

| Artifact | Purpose |
|---|---|
| `bounded-context-candidates.jsonl` | 63 positive/negative ownership hypotheses |
| `capabilities.jsonl`, `operations.jsonl`, `decisions.jsonl` | Platform behavior and compiler-visible choices |
| `state-machines.jsonl` | 45 reachable, total command/state lifecycle candidates |
| `contracts.jsonl` | Tenant-, authority-, time-, money-, and event-safe carrier contracts |
| `invariants-refusals.jsonl` | Authority, isolation, semantic distinction, refusal, and precedence laws |
| `library-boundaries.jsonl` | 43 live pure libraries, effect ports, and provider adapters |
| `retired-compositions.jsonl` | Seven coarse boundaries retired in favor of exact identity, money, interval, metering, service-level, entitlement and lifecycle compositions; no compatibility aliases |
| `requirements-offers-bindings.jsonl` | 43 requirements, 43 offers, and 43 deliberately unproven bindings |
| `compiler-mappings.jsonl`, `compiler-contract.json` | IR stages, gates, invalidation, and release behavior |
| `product-truth-mappings.jsonl` | 22 candidate product truths with unique owners and prohibited derivations |
| `cross-domain-mappings.jsonl` | Security, runtime, provider, product, evidence, and compiler boundaries |
| `sources.jsonl`, `evidence.jsonl` | 102 narrow official source and evidence claims |
| `innovations-2021-2026.jsonl` | 24 non-LLM developments and compiler implications |
| `gaps.jsonl` | 20 exact gaps; 18 currently block release/ratification |
| `vertical-examples.jsonl` | Two end-to-end compiler traces |
| `schemas/` | 17 JSON Schemas for the principal record families |
| `manifest.json`, `validation-report.json` | Gates, exact counts, status, and validation result |

All nineteen contracts introduced by the coarse-boundary splits publish exact public types, traits,
operation signatures, typed refusals, laws and conformance-oracle classes: four commercial
identities, three metering contracts, three service-level/credit decisions, four entitlement
contracts and five independent lifecycles. The validator rejects any regeneration that replaces
those contracts with registry-generated API placeholders.

## Regenerate and validate

```bash
python3 research/domain_atlas/universes/platform_commercial_support/build_corpus.py
python3 research/domain_atlas/universes/platform_commercial_support/validate_corpus.py
```

The validator checks deterministic regeneration, JSON/schema-required fields, unique identities,
reference closure, manifest reconciliation, lifecycle reachability and total command/state dispatch,
source and innovation gates, distinction invariants, binding closure, and the honest candidate flag.

## Honest standing

The passing validator proves internal corpus consistency, not domain correctness. The largest
remaining blockers are cross-universe ownership adjudication, legal/tax/payment qualification,
meter correction and tiered-rating oracles, adversarial tenant-isolation evidence, SLA exclusion and
service-credit reconciliation, provider drift detection, a successful independent import for export
fidelity, two full vertical exit exercises, the repository-wide product-truth crosswalk, and two
independent implementations of every reusable contract. `completion_claim` is therefore `false`.
