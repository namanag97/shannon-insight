#!/usr/bin/env python3
"""Build the platform/commercial/support candidate universe deterministically.

The generated corpus is an architectural research artifact, not legal, tax, accounting,
payment-security, or service-management advice.  Official specifications and product APIs
provide scoped implementation evidence; they do not prove that a candidate boundary is final.
"""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCHEMAS = HERE / "schemas"
EDITION = "0.1.0"
AS_OF = "2026-08-25"
STATUS = "sourced_candidate"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def cid(slug: str) -> str:
    return f"context.platform-commercial-support.{slug}"


def sid(slug: str) -> str:
    return f"source.platform-commercial-support.{slug}"


# slug, name, sovereign question, owned terms, terms that must stay outside this owner.
CONTEXT_SPECS = [
    ("tenant-registry", "Tenant registry", "Which durable tenant identity exists and which lifecycle edition names it?", ["TenantId", "tenant lifecycle", "tenant alias history"], ["billing account", "legal entity", "authentication realm"]),
    ("tenant-hierarchy", "Tenant hierarchy", "Which parent-child tenant relations are valid for delegation and aggregation at an effective time?", ["tenant edge", "hierarchy edition", "delegation boundary"], ["legal ownership", "workspace membership", "invoice roll-up"]),
    ("account-registry", "Account registry", "Which product-facing account groups users and assets without implying who pays?", ["AccountId", "account profile", "account status"], ["billing account", "tenant identity", "legal entity"]),
    ("organization-registry", "Organization registry", "Which customer-visible organizational units exist and how are they related?", ["OrganizationId", "organization edge", "organization role"], ["tenant isolation", "legal incorporation", "payment responsibility"]),
    ("workspace-registry", "Workspace registry", "Which collaboration workspace exists inside a tenant and what resource namespace does it bind?", ["WorkspaceId", "workspace membership projection", "workspace lifecycle"], ["tenant identity", "authorization grant", "billing account"]),
    ("legal-entity-binding", "Legal-entity binding", "Which externally established legal entity is referenced for contracting, tax, invoicing, or payment?", ["LegalEntityRef", "verified attributes", "effective binding"], ["legal adjudication", "tenant identity", "billing account"]),
    ("commercial-customer", "Commercial customer", "Which commercial relationship is the subject of offers, subscriptions, support, and success activity?", ["CustomerId", "customer relationship status", "party bindings"], ["tenant identity", "payer", "end user"]),
    ("party-role", "Party and role", "Which person or organization participates in which commercial or service role at an effective time?", ["PartyRef", "party role", "role validity"], ["authentication principal", "authorization decision", "employment truth"]),
    ("delegated-administration", "Delegated administration", "Who may administer which product scope on behalf of a tenant, and under what delegation?", ["administration delegation", "delegation scope", "delegation revocation"], ["end-user authorization", "commercial entitlement", "legal authority beyond evidence"]),
    ("tenant-isolation", "Tenant isolation policy", "Which storage, compute, cache, event, support, and evidence boundaries must isolate tenants?", ["isolation policy", "isolation class", "cross-tenant exception evidence"], ["authentication", "commercial entitlement", "physical capacity"]),
    ("feature-definition", "Feature definition", "What stable product capability key may be entitled, metered, packaged, and retired?", ["FeatureKey", "feature edition", "compatibility relation"], ["authorization permission", "implementation flag state", "plan"]),
    ("entitlement-policy", "Entitlement policy", "What commercial conditions make a feature available to a subject and scope?", ["entitlement rule", "entitlement evaluation", "commercial availability"], ["authorization", "quota", "physical feasibility"]),
    ("entitlement-grant", "Entitlement grant", "Which issued feature allowance exists, for whom, during what interval, with what consumption law?", ["EntitlementGrantId", "grant balance", "grant validity"], ["prepaid monetary balance", "quota", "role permission"]),
    ("license-seat", "License and seat allocation", "How many named or concurrent seats may be allocated and reclaimed without double assignment?", ["license pool", "seat assignment", "concurrency observation"], ["user identity", "workspace membership", "invoice quantity"]),
    ("product-catalog", "Product catalog", "Which versioned commercial product offerings can be discovered and configured?", ["ProductOfferingId", "offer edition", "offer eligibility"], ["signed contract", "service instance", "price realization"]),
    ("service-catalog", "Service catalog", "Which operable services and requestable service actions are published?", ["ServiceSpecificationId", "service offer", "request schema"], ["product plan", "deployed service instance", "support case"]),
    ("plan-version", "Plan version", "Which feature, price, limit, and lifecycle templates comprise a versioned plan?", ["PlanVersionId", "plan phase", "template composition"], ["customer subscription", "signed contract", "catalog product identity"]),
    ("price-book", "Price book and rate card", "Which versioned prices and rating parameters may be offered for a market and currency?", ["PriceBookId", "rate card", "price validity"], ["rated usage", "invoice line", "tax result"]),
    ("quote-configuration", "Quote and configuration", "Which eligible configuration and commercial proposal may be presented before acceptance?", ["QuoteId", "configured offer", "quote validity"], ["signed contract", "product order", "service activation"]),
    ("commercial-contract", "Commercial contract projection", "Which signed commercial terms have machine-enforceable product semantics?", ["ContractId", "effective terms projection", "counterparty bindings"], ["full legal text interpretation", "catalog offer", "subscription"]),
    ("contract-amendment", "Contract amendment", "How do approved term changes create a new effective contract edition without rewriting history?", ["AmendmentId", "term delta", "effective-date precedence"], ["plan mutation", "invoice correction", "unilateral runtime override"]),
    ("meter-definition", "Meter definition", "Which event facts, dimensions, window, and aggregation define a billable or observable measure?", ["MeterId", "meter edition", "aggregation law"], ["raw usage event", "rated usage", "invoice line"]),
    ("usage-event", "Usage event intake", "Which immutable occurrence is accepted as potential usage and how is replay deduplicated?", ["UsageEventId", "event payload", "ingestion receipt"], ["aggregate usage", "price", "invoice"]),
    ("usage-attribution", "Usage attribution", "Which tenant, customer, billing account, product, workspace, and cost object receive an accepted event?", ["attribution edition", "subject mapping", "unattributed queue"], ["event authenticity", "rating", "chargeback policy"]),
    ("usage-aggregation", "Usage aggregation", "How are accepted attributed events reduced into windowed quantities under a meter edition?", ["UsageAggregateId", "window", "late-correction lineage"], ["raw event", "rated usage", "invoice quantity"]),
    ("rating", "Rating", "How does an aggregate quantity become a priced charge candidate under an effective rate card?", ["RatedUsageId", "pricing tier application", "rating receipt"], ["invoice issuance", "tax determination", "payment"]),
    ("charge-ledger", "Charge ledger", "Which immutable debit, credit, adjustment, and reversal entries explain customer charges?", ["ChargeEntryId", "charge lineage", "ledger balance"], ["general ledger", "invoice document", "usage event"]),
    ("prepaid-credit", "Prepaid and promotional credit", "Which finite monetary or unit credit balance may be consumed, expire, roll over, or be restored?", ["CreditGrantId", "credit bucket", "burn priority"], ["quota", "budget", "service credit claim"]),
    ("billing-account", "Billing account", "Which payer-facing account owns invoice preferences, currency, terms, and payment responsibility?", ["BillingAccountId", "bill-to profile", "collection settings"], ["tenant", "legal entity", "commercial customer"]),
    ("billing-cycle", "Billing cycle", "Which calendar, cutoff, finalization, and reopening rules partition charges?", ["BillingCycleId", "cycle window", "close edition"], ["usage window", "contract term", "SLO window"]),
    ("invoice", "Invoice", "Which finalized payable document and lines state amounts, provenance, and settlement status?", ["InvoiceId", "invoice line", "invoice lifecycle"], ["charge ledger", "meter event", "payment transaction"]),
    ("tax-determination", "Tax determination", "Which qualified external result supplies tax category, jurisdiction, amount, and evidence?", ["TaxDeterminationId", "tax evidence reference", "rounding result"], ["legal advice", "tax policy invention", "invoice payment"]),
    ("payment-collection", "Payment collection", "Which payment intent, authorization, capture, settlement, failure, and dispute facts apply?", ["PaymentIntentRef", "collection attempt", "settlement reference"], ["invoice issuance", "payment-network internals", "entitlement policy"]),
    ("refund-credit-note", "Refund and credit note", "How are approved monetary reversals linked to charge, invoice, tax, and payment history?", ["RefundId", "CreditNoteId", "reversal allocation"], ["history deletion", "service credit eligibility", "subscription cancellation"]),
    ("cost-allocation", "Cost allocation", "How are shared and direct costs allocated to accountable cost objects with disclosed method?", ["allocation rule", "cost object", "allocation receipt"], ["billing invoice", "budget authority", "resource quota"]),
    ("cost-normalization", "Cost normalization", "How is one identified provider cost-and-usage occurrence mapped to an exact FOCUS edition while retaining source identity, unmapped information, validation findings and semantic loss?", ["cost occurrence", "normalization profile", "normalized FOCUS record", "normalization residual"], ["cost allocation", "provider invoice authority", "general-ledger posting", "business-value judgment"]),
    ("budget-control", "Budget control", "Which spend threshold, forecast, alert, approval, or hard stop applies to a governed scope?", ["BudgetId", "budget period", "threshold action"], ["prepaid credit", "quota", "physical capacity"]),
    ("chargeback-showback", "Chargeback and showback", "Which internal consumer is informed or debited for allocated cost, under what policy?", ["chargeback statement", "showback view", "allocation policy edition"], ["external invoice", "legal liability", "meter definition"]),
    ("quota-policy", "Product quota policy", "Which technical admission limit applies independently of commercial access, money, and capacity?", ["QuotaId", "quota window", "quota consumption"], ["entitlement", "budget", "physical capacity"]),
    ("subscription", "Subscription", "Which customer-specific plan or negotiated configuration is active over time?", ["SubscriptionId", "subscription item", "phase schedule"], ["catalog plan", "signed contract", "tenant"]),
    ("trial", "Trial", "Which time- or usage-bounded evaluation access exists and what conversion or expiry rules apply?", ["TrialId", "trial allowance", "conversion outcome"], ["free plan", "promotional credit", "contract renewal"]),
    ("renewal", "Renewal", "Which continuation proposal, notice, acceptance, and new term edition governs renewal?", ["RenewalCaseId", "renewal proposal", "renewal outcome"], ["automatic invoice", "silent contract mutation", "plan publication"]),
    ("suspension-termination", "Suspension and termination", "When is service use temporarily blocked or permanently ended without equating either to deletion?", ["suspension order", "termination order", "service access consequence"], ["entitlement revocation", "data deletion", "tenant erasure"]),
    ("product-order", "Product order", "Which accepted commercial configuration is requested, decomposed, amended, or cancelled?", ["ProductOrderId", "order item", "commercial fulfillment status"], ["service order", "provisioning task", "signed contract"]),
    ("service-order", "Service order", "Which service actions fulfill a product order or catalog request, with dependencies and fallout?", ["ServiceOrderId", "service order item", "fallout reason"], ["product pricing", "resource allocation", "support case"]),
    ("provisioning", "Provisioning orchestration", "Which declared service instances must be created, configured, verified, rolled back, or decommissioned?", ["ProvisioningPlanId", "provisioning step", "activation receipt"], ["service semantics", "provider resource ownership", "commercial acceptance"]),
    ("onboarding", "Customer onboarding", "Which prerequisites, migrations, training, acceptance, and go-live gates establish readiness?", ["OnboardingPlanId", "onboarding milestone", "go-live acceptance"], ["product order", "data migration semantics", "customer success outcome"]),
    ("adoption-success", "Adoption and customer success", "Which declared outcomes and product-use signals evidence adoption without redefining customer intent?", ["SuccessPlanId", "adoption milestone", "risk signal"], ["usage invoice", "support resolution", "business outcome truth"]),
    ("support-case", "Support case", "Which customer-reported question, request, or impairment is tracked to response and closure?", ["SupportCaseId", "case conversation", "case resolution"], ["incident", "problem", "service order"]),
    ("severity-policy", "Severity and priority", "How are impact, urgency, scope, and customer contract translated into severity and priority?", ["SeverityPolicyId", "impact assessment", "priority decision"], ["incident identity", "support entitlement", "escalation route"]),
    ("escalation-routing", "Escalation and on-call routing", "Which responder or management path receives an unresolved or high-severity item at each deadline?", ["EscalationPolicyId", "routing step", "acknowledgement deadline"], ["incident diagnosis", "case ownership", "status communication"]),
    ("maintenance-change", "Maintenance and change window", "Which approved change may occur during what window, with what notice, risk, validation, and rollback?", ["ChangeId", "maintenance window", "change outcome"], ["unplanned outage", "incident", "contract amendment"]),
    ("status-communication", "Status communication", "Which audience receives which verified operational message, through which channel and edition?", ["StatusNoticeId", "audience scope", "publication/retraction history"], ["incident record", "support conversation", "marketing message"]),
    ("incident", "Service incident", "Which unplanned service degradation or interruption is coordinated to mitigation and restoration?", ["IncidentId", "impact interval", "mitigation/restoration facts"], ["support case", "problem", "planned maintenance"]),
    ("problem", "Problem and known error", "Which underlying cause hypothesis and corrective work explain one or more incidents?", ["ProblemId", "cause hypothesis", "known-error/workaround"], ["incident response", "support request", "change approval"]),
    ("service-objective", "Service objective", "Which indicator, target, window, exclusions, and error-budget method define an internal SLO?", ["SLOId", "SLI binding", "objective evaluation"], ["contractual SLA", "service credit", "incident severity"]),
    ("service-agreement", "Service-level agreement", "Which customer contract projection binds defined service commitments and measurement rules?", ["SLAId", "commitment term", "claim procedure"], ["internal SLO", "support plan", "service credit award"]),
    ("service-credit", "Service credit", "Which verified SLA breach creates an eligible claim and approved commercial credit?", ["ServiceCreditClaimId", "eligibility result", "credit award"], ["SLO breach alone", "prepaid balance", "refund"]),
    ("customer-evidence", "Customer evidence package", "Which receipts may be disclosed to a customer to substantiate usage, service, support, and exit claims?", ["EvidencePackageId", "disclosure scope", "integrity manifest"], ["internal telemetry dump", "legal discovery", "system-of-record ownership"]),
    ("portability-export", "Data portability and export", "Which scoped data, metadata, formats, checksums, and completeness proofs constitute a portable export?", ["ExportPlanId", "export manifest", "transfer receipt"], ["supplier exit completion", "deletion proof", "semantic interoperability guarantee"]),
    ("supplier-exit", "Supplier and product exit", "Which coordinated transition plan moves service, data, dependencies, credentials, and responsibilities to an exit state?", ["ExitPlanId", "exit milestone", "exit acceptance"], ["data export alone", "tenant deletion", "contract interpretation"]),
    ("decommission", "Decommission", "Which service instances and dependencies may be disabled, drained, destroyed, or retained after exit?", ["DecommissionPlanId", "dependency disposition", "destruction receipt"], ["subscription termination", "data export", "legal hold decision"]),
    ("residual-obligation", "Residual obligation", "Which surviving retention, access, evidence, support, payment, and deletion duties remain after termination?", ["ResidualObligationId", "obligation schedule", "discharge evidence"], ["full legal obligation model", "active entitlement", "silent indefinite retention"]),
]


# Primary and official implementation evidence.  Each claim is deliberately narrow.
# slug, title, publisher, URL, evidence family, supported claim, kind, publication/material year.
SOURCE_SPECS = [
    ("tmf620", "TMF620 Product Catalog Management API", "TM Forum", "https://github.com/tmforum-apis/TMF620_ProductCatalog", "catalog", "Product offerings and specifications are versioned catalog resources.", "official_open_api", 2025),
    ("tmf622", "TMF622 Product Ordering Management API", "TM Forum", "https://github.com/tmforum-apis/TMF622_ProductOrder", "ordering", "Product orders and order items have explicit lifecycle fields.", "official_open_api", 2025),
    ("tmf637", "TMF637 Product Inventory Management API", "TM Forum", "https://github.com/tmforum-apis/TMF637_ProductInventory", "subscription", "Realized customer products are distinct from catalog offerings.", "official_open_api", 2025),
    ("tmf629", "TMF629 Customer Management API", "TM Forum", "https://github.com/tmforum-apis/TMF629_CustomerManagement", "customer", "Customer resources are distinct from party and account resources.", "official_open_api", 2025),
    ("tmf632", "TMF632 Party Management API", "TM Forum", "https://github.com/tmforum-apis/TMF632_PartyManagement", "identity", "Individuals and organizations can participate as parties without becoming tenants.", "official_open_api", 2025),
    ("tmf666", "TMF666 Account Management API", "TM Forum", "https://github.com/tmforum-apis/TMF666_AccountManagement", "account", "Account resources carry distinct bill, settlement, and relationship roles.", "official_open_api", 2025),
    ("tmf633", "TMF633 Service Catalog Management API", "TM Forum", "https://github.com/tmforum-apis/TMF633_ServiceCatalog", "catalog", "Service specifications and candidates are catalog concepts distinct from instances.", "official_open_api", 2025),
    ("tmf641", "TMF641 Service Ordering Management API", "TM Forum", "https://github.com/tmforum-apis/TMF641_ServiceOrder", "ordering", "Service order fulfillment has lifecycle and item decomposition.", "official_open_api", 2025),
    ("tmf638", "TMF638 Service Inventory Management API", "TM Forum", "https://github.com/tmforum-apis/TMF638_ServiceInventory", "provisioning", "Service inventory represents realized services separately from orders.", "official_open_api", 2025),
    ("tmf645", "TMF645 Service Qualification Management API", "TM Forum", "https://github.com/tmforum-apis/TMF645_ServiceQualification", "qualification", "Eligibility and technical qualification can precede an order.", "official_open_api", 2025),
    ("tmf648", "TMF648 Quote Management API", "TM Forum", "https://github.com/tmforum-apis/TMF648_QuoteManagement", "quote", "A quote is a time-bounded proposal distinct from an accepted order.", "official_open_api", 2025),
    ("tmf651", "TMF651 Agreement Management API", "TM Forum", "https://github.com/tmforum-apis/TMF651_AgreementManagement", "contract", "Agreement resources carry terms, parties, validity, and related documents.", "official_open_api", 2025),
    ("tmf635", "TMF635 Usage Management API", "TM Forum", "https://github.com/tmforum-apis/TMF635_UsageManagement", "usage", "Usage records and usage specifications are explicit API resources.", "official_open_api", 2025),
    ("tmf677", "TMF677 Usage Consumption Management API", "TM Forum", "https://github.com/tmforum-apis/TMF677_UsageConsumption", "usage", "Consumption summaries expose bucket and counter semantics separately from invoices.", "official_open_api", 2025),
    ("tmf678", "TMF678 Customer Bill Management API", "TM Forum", "https://github.com/tmforum-apis/TMF678_CustomerBill", "billing", "Customer bills and bill items have their own lifecycle.", "official_open_api", 2025),
    ("tmf676", "TMF676 Payment Management API", "TM Forum", "https://github.com/tmforum-apis/TMF676_PaymentManagement", "payment", "Payments are separately identified and related to amounts and accounts.", "official_open_api", 2025),
    ("tmf654", "TMF654 Prepay Balance Management API", "TM Forum", "https://github.com/tmforum-apis/TMF654_PrepayBalanceManagement", "credit", "Prepaid balances and bucket adjustments are distinct from quota.", "official_open_api", 2025),
    ("tmf679", "TMF679 Product Offering Qualification API", "TM Forum", "https://github.com/tmforum-apis/TMF679_ProductOfferingQualification", "qualification", "Offer qualification is an explicit pre-order decision.", "official_open_api", 2025),
    ("tmf621", "TMF621 Trouble Ticket Management API", "TM Forum", "https://github.com/tmforum-apis/TMF621_TroubleTicket", "support", "Trouble tickets have severity, status, related parties, and notes.", "official_open_api", 2025),
    ("tmf656", "TMF656 Service Problem Management API", "TM Forum", "https://github.com/tmforum-apis/TMF656_ServiceProblemManagement", "problem", "Service problems are modeled separately from trouble tickets.", "official_open_api", 2025),
    ("tmf642", "TMF642 Alarm Management API", "TM Forum", "https://github.com/tmforum-apis/TMF642_AlarmManagement", "incident", "Alarms are observations and not themselves customer cases or incidents.", "official_open_api", 2025),
    ("tmf688", "TMF688 Event Management API", "TM Forum", "https://github.com/tmforum-apis/TMF688_Event", "event", "Operational events use an envelope distinct from domain semantics.", "official_open_api", 2025),
    ("tmf657", "TMF657 Service Quality Management API", "TM Forum", "https://github.com/tmforum-apis/TMF657_ServiceQualityManagement", "service-level", "Service quality measurements and objectives are explicit resources.", "official_open_api", 2025),
    ("tmf623", "TM Forum SLA Management API Swagger", "TM Forum", "https://github.com/tmforum/TMFAPISWAGGER/tree/master/slaManagement/v2", "service-level", "SLA resources carry commitments and violations separately from internal SLOs.", "official_open_api", 2025),
    ("tmf640", "TMF640 Service Activation and Configuration API", "TM Forum", "https://github.com/tmforum-apis/TMF640_ActivationConfiguration", "provisioning", "Activation/configuration is a fulfillment mechanism rather than product truth.", "official_open_api", 2025),
    ("tmf639", "TMF639 Resource Inventory Management API", "TM Forum", "https://github.com/tmforum-apis/TMF639_ResourceInventory", "resource", "Provider resources remain distinct from products and services.", "official_open_api", 2025),
    ("tmf669", "TMF669 Party Role Management API", "TM Forum", "https://github.com/tmforum-apis/TMF669_PartyRole", "identity", "A party role is effective-dated participation, not identity itself.", "official_open_api", 2025),
    ("tmf701", "TMF701 Process Flow Management API", "TM Forum", "https://github.com/tmforum-apis/TMF701_ProcessFlow", "orchestration", "Process-flow state can coordinate but does not own commercial semantics.", "official_open_api", 2025),
    ("it4it3", "IT4IT Standard Version 3 overview", "The Open Group", "https://www.opengroup.org/it4it", "service-management", "Digital-product management spans portfolio, development, delivery, and operation value streams.", "official_standard_overview", 2022),
    ("it4it-cert", "IT4IT Version 3 conformance program", "The Open Group", "https://www.opengroup.org/certifications/it4it", "service-management", "IT4IT 3 supplies standardized terminology and conformance requirements.", "official_conformance", 2023),
    ("iso20000-1", "ISO/IEC 20000-1:2018 service management system requirements", "ISO", "https://www.iso.org/standard/70636.html", "service-management", "A service management system covers planning, operation, performance evaluation, and improvement.", "official_standard", 2018),
    ("iso20000-5", "ISO/IEC TS 20000-5:2022 implementation guidance", "ISO", "https://www.iso.org/standard/81164.html", "service-management", "Service-management requirements require an implementation plan and controlled evidence.", "official_standard", 2022),
    ("iso22301", "ISO 22301 business continuity management systems", "ISO", "https://www.iso.org/standard/75106.html", "continuity", "Continuity planning is separate from routine incident and maintenance handling.", "official_standard", 2019),
    ("iso19941", "ISO/IEC 19941 cloud interoperability and portability", "ISO", "https://www.iso.org/standard/66639.html", "portability", "Cloud interoperability and portability require explicit interfaces and responsibilities.", "official_standard", 2017),
    ("iso19944", "ISO/IEC 19944-1:2020 cloud data flow and data categories", "ISO", "https://www.iso.org/standard/79573.html", "portability", "Cloud data flows and data categories support scoped portability analysis.", "official_standard", 2020),
    ("iso4217", "ISO 4217 currency code maintenance", "SIX Group", "https://www.six-group.com/en/products-services/financial-information/data-standards.html", "billing", "Currency codes and minor units are external controlled data.", "official_registration_authority", 2026),
    ("rfc3339", "RFC 3339 date and time on the Internet", "IETF", "https://www.rfc-editor.org/rfc/rfc3339", "time", "Internet timestamps require explicit offsets and a constrained profile.", "official_standard", 2002),
    ("cloudevents", "CloudEvents Specification 1.0.2", "CNCF", "https://github.com/cloudevents/spec/tree/ce@v1.0.2", "event", "Event envelope metadata is interoperable while event meaning remains application-owned.", "official_open_spec", 2022),
    ("cloudevents-sql", "CloudEvents SQL v1.0", "CNCF", "https://github.com/cloudevents/spec/blob/cesql@v1.0.0/cesql/spec.md", "event", "A portable expression language can select event envelope and data attributes.", "official_open_spec", 2024),
    ("openslo", "OpenSLO Specification", "OpenSLO", "https://github.com/OpenSLO/OpenSLO", "service-level", "SLOs bind indicators, objectives, windows, and budgeting methods independently of provider implementation.", "official_open_spec", 2024),
    ("opentelemetry", "OpenTelemetry Specification", "CNCF", "https://opentelemetry.io/docs/specs/otel/", "evidence", "Traces, metrics, logs, baggage, and resources are separate telemetry signals.", "official_open_spec", 2026),
    ("otel-semconv", "OpenTelemetry semantic conventions", "CNCF", "https://opentelemetry.io/docs/specs/semconv/", "evidence", "Semantic conventions version observed service and event attributes.", "official_open_spec", 2026),
    ("openmeter-events", "OpenMeter usage event overview", "OpenMeter", "https://openmeter.io/docs/metering/events/overview", "usage", "Usage ingestion accepts CloudEvents before aggregation and billing.", "official_oss_docs", 2026),
    ("openmeter-subjects", "OpenMeter subjects", "OpenMeter", "https://openmeter.io/docs/metering/subjects", "usage", "A meter subject is not the same managed entity as a billing customer.", "official_oss_docs", 2026),
    ("openmeter-meters", "OpenMeter meters", "OpenMeter", "https://openmeter.io/docs/metering/meters", "usage", "Meters define aggregation and grouping separately from events.", "official_oss_docs", 2026),
    ("openmeter-entitlements", "OpenMeter entitlements", "OpenMeter", "https://openmeter.io/docs/billing/entitlements/quickstart", "entitlement", "Boolean, static, and metered entitlements can gate feature access.", "official_oss_docs", 2026),
    ("openmeter-grants", "OpenMeter grants", "OpenMeter", "https://openmeter.io/docs/billing/entitlements/grant", "credit", "Usage grants have priority, validity, recurrence, and rollover semantics.", "official_oss_docs", 2026),
    ("openmeter-subscriptions", "OpenMeter subscriptions", "OpenMeter", "https://openmeter.io/docs/billing/subscription/overview", "subscription", "Subscriptions concretize plan phases, rate cards, prices, and entitlements.", "official_oss_docs", 2026),
    ("openmeter-invoices", "OpenMeter invoicing", "OpenMeter", "https://openmeter.io/docs/billing/invoicing", "billing", "Invoice lifecycle is downstream of rated line construction.", "official_oss_docs", 2026),
    ("openmeter-notifications", "OpenMeter notification rules", "OpenMeter", "https://openmeter.io/docs/integrations/notifications/rule", "event", "Threshold, reset, and invoice notifications are selected domain events.", "official_oss_docs", 2026),
    ("focus12", "FOCUS Specification 1.2", "FinOps Foundation", "https://focus.finops.org/focus-specification/v1-2/", "finops", "Normalized billing data separates billed, effective, list, and contracted costs and allocation fields.", "official_open_spec", 2025),
    ("focus11", "FOCUS Specification 1.1", "FinOps Foundation", "https://focus.finops.org/focus-specification/v1-1/", "finops", "Cost and usage records include charge classes and commitment-discount semantics.", "official_open_spec", 2024),
    ("finops-framework", "FinOps Framework", "FinOps Foundation", "https://www.finops.org/framework/", "finops", "Allocation, budgeting, forecasting, chargeback, and unit economics are distinct capabilities.", "official_framework", 2025),
    ("opencost", "OpenCost Specification", "OpenCost / CNCF", "https://www.opencost.io/docs/specification", "finops", "Kubernetes cost allocation uses explicit workload, asset, and shared-cost fields.", "official_open_spec", 2026),
    ("k8s-resource-quota", "Kubernetes ResourceQuota", "Kubernetes / CNCF", "https://kubernetes.io/docs/concepts/policy/resource-quotas/", "quota", "Quota restricts aggregate namespace consumption but does not prove cluster capacity.", "official_oss_docs", 2026),
    ("k8s-limit-range", "Kubernetes LimitRange", "Kubernetes / CNCF", "https://kubernetes.io/docs/concepts/policy/limit-range/", "quota", "Per-object resource constraints differ from namespace aggregate quota.", "official_oss_docs", 2026),
    ("k8s-multitenancy", "Kubernetes multi-tenancy", "Kubernetes / CNCF", "https://kubernetes.io/docs/concepts/security/multi-tenancy/", "tenant-isolation", "Multi-tenancy requires control-plane and data-plane isolation appropriate to trust level.", "official_oss_docs", 2026),
    ("openfeature", "OpenFeature Specification", "CNCF", "https://openfeature.dev/specification/", "feature", "A vendor-neutral feature-flag evaluation API separates evaluation from provider implementation.", "official_open_spec", 2026),
    ("backstage-catalog", "Backstage system model", "CNCF", "https://backstage.io/docs/features/software-catalog/system-model/", "catalog", "Components, systems, APIs, resources, and domains form a service catalog projection.", "official_oss_docs", 2026),
    ("ubl21", "Universal Business Language 2.1", "OASIS", "https://docs.oasis-open.org/ubl/os-UBL-2.1/UBL-2.1.html", "invoice", "UBL supplies interoperable invoice, credit note, order, and related document structures.", "official_standard", 2013),
    ("peppol-billing", "Peppol BIS Billing 3.0", "OpenPeppol", "https://docs.peppol.eu/poacc/billing/3.0/bis/", "invoice", "Invoice and credit-note semantics and validation rules implement EN 16931 profiles.", "official_spec", 2026),
    ("peppol-ordering", "Peppol BIS Ordering 3", "OpenPeppol", "https://docs.peppol.eu/poacc/upgrade-3/2025-Q4/bis/", "ordering", "Interoperable order and response choreography is distinct from invoicing.", "official_spec", 2025),
    ("peppol-pint", "Peppol International Invoice Model", "OpenPeppol", "https://docs.peppol.eu/poac/pint/", "invoice", "PINT supplies jurisdiction-extensible international invoice semantics.", "official_spec", 2026),
    ("uncefact-cii", "UN/CEFACT Cross Industry Invoice", "UNECE", "https://unece.org/trade/uncefact/xml-schemas", "invoice", "CII is a maintained structured invoice syntax family.", "official_standard", 2024),
    ("eu-vat-invoice", "EU VAT invoicing rules", "European Commission", "https://taxation-customs.ec.europa.eu/taxation/vat/vat-businesses/invoicing_en", "tax", "Invoice content and VAT handling depend on jurisdictional rules supplied outside the compiler.", "official_authority", 2026),
    ("eu-data-act", "Regulation (EU) 2023/2854 Data Act", "EUR-Lex", "https://eur-lex.europa.eu/eli/reg/2023/2854/oj", "exit", "Cloud switching requires more than a file download and includes transition and interoperability concerns.", "official_law", 2023),
    ("swipo-exit", "SWIPO IaaS Code of Conduct", "SWIPO", "https://swipo.eu/iaas-code-of-conduct/", "exit", "Cloud exit planning includes data, configurations, processes, timeframes, and assistance.", "official_code", 2020),
    ("nist-sp800-146", "NIST SP 800-146 Cloud Computing Synopsis and Recommendations", "NIST", "https://csrc.nist.gov/pubs/sp/800/146/final", "portability", "Cloud portability requires attention to data, application, and platform dependencies.", "official_guidance", 2012),
    ("stripe-meter-events", "Stripe billing meter events API", "Stripe", "https://docs.stripe.com/api/billing/meter-event", "usage", "Meter events carry customer, event, timestamp, and payload before invoice generation.", "official_product_api", 2026),
    ("stripe-meters", "Stripe usage-based billing", "Stripe", "https://docs.stripe.com/billing/subscriptions/usage-based", "rating", "Meters, prices, usage recording, and invoice calculation are separate steps.", "official_product_docs", 2026),
    ("stripe-entitlements", "Stripe Entitlements", "Stripe", "https://docs.stripe.com/billing/entitlements", "entitlement", "Product feature access can be driven by active subscription entitlements.", "official_product_docs", 2026),
    ("stripe-subscriptions", "Stripe subscriptions API", "Stripe", "https://docs.stripe.com/api/subscriptions", "subscription", "Subscription lifecycle includes trial, active, paused, past-due, canceled, and incomplete states.", "official_product_api", 2026),
    ("stripe-invoices", "Stripe invoices API", "Stripe", "https://docs.stripe.com/api/invoices", "invoice", "Invoices have draft, open, paid, uncollectible, and void states.", "official_product_api", 2026),
    ("stripe-credit-notes", "Stripe credit notes API", "Stripe", "https://docs.stripe.com/api/credit_notes", "invoice", "Credit notes adjust invoice balances without rewriting issued invoice history.", "official_product_api", 2026),
    ("stripe-payment-intents", "Stripe Payment Intents API", "Stripe", "https://docs.stripe.com/api/payment_intents", "payment", "Payment intent, confirmation, authentication, capture, cancellation, and failure are distinct states.", "official_product_api", 2026),
    ("stripe-tax", "Stripe Tax calculation API", "Stripe", "https://docs.stripe.com/api/tax/calculations", "tax", "Tax calculation is a separately identified result with line-level amounts.", "official_product_api", 2026),
    ("zuora-subscriptions", "Zuora subscriptions API", "Zuora", "https://developer.zuora.com/v1-api-reference/api/tag/Subscriptions/", "subscription", "Enterprise subscription APIs model terms, renewals, amendments, and charges.", "official_product_api", 2026),
    ("zuora-orders", "Zuora Orders API", "Zuora", "https://developer.zuora.com/v1-api-reference/api/tag/Orders/", "ordering", "Orders can create and amend subscriptions through ordered actions.", "official_product_api", 2026),
    ("chargebee-subscriptions", "Chargebee subscriptions API", "Chargebee", "https://apidocs.chargebee.com/docs/api/subscriptions", "subscription", "Subscription APIs expose pause, resume, cancel, reactivate, and term changes.", "official_product_api", 2026),
    ("paddle-subscriptions", "Paddle subscriptions API", "Paddle", "https://developer.paddle.com/api-reference/subscriptions/overview", "subscription", "Subscription state and scheduled changes are explicit API resources.", "official_product_api", 2026),
    ("lago-api", "Lago API reference", "Lago", "https://getlago.com/docs/api-reference/intro", "billing", "An open-source billing API separates billable metrics, plans, subscriptions, fees, and invoices.", "official_oss_docs", 2026),
    ("killbill-subscription", "Kill Bill subscription user guide", "Kill Bill", "https://docs.killbill.io/latest/userguide_subscription", "subscription", "Catalog, entitlement, billing, and payment timelines are separable in an OSS billing platform.", "official_oss_docs", 2026),
    ("killbill-usage", "Kill Bill usage billing", "Kill Bill", "https://docs.killbill.io/latest/userguide_subscription.html#components-usage", "usage", "Usage billing uses recorded usage and catalog rating rules.", "official_oss_docs", 2026),
    ("pci-dss", "PCI Data Security Standard", "PCI Security Standards Council", "https://www.pcisecuritystandards.org/standards/pci-dss/", "payment", "Payment-account data handling is a separate qualified security boundary.", "official_standard", 2024),
    ("iso20022", "ISO 20022 financial messaging", "ISO 20022 Registration Authority", "https://www.iso20022.org/", "payment", "Payment messages use maintained business models and message definitions.", "official_standard", 2026),
    ("pagerduty-incidents", "PagerDuty incidents API", "PagerDuty", "https://developer.pagerduty.com/api-reference/9d0b4b12e36f9-list-incidents", "incident", "Incident APIs expose acknowledgement, resolution, urgency, escalation, and assignment.", "official_product_api", 2026),
    ("pagerduty-escalation", "PagerDuty escalation policies API", "PagerDuty", "https://developer.pagerduty.com/api-reference/612e4e7a57a64-list-escalation-policies", "escalation", "Escalation policies route through ordered rules and targets.", "official_product_api", 2026),
    ("statuspage-incidents", "Atlassian Statuspage incidents API", "Atlassian", "https://developer.statuspage.io/#tag/incidents", "status", "Public incident communication has independent incident-update lifecycle.", "official_product_api", 2026),
    ("statuspage-maintenance", "Atlassian Statuspage scheduled maintenances API", "Atlassian", "https://developer.statuspage.io/#tag/scheduled-maintenances", "maintenance", "Scheduled maintenance is communicated separately from an unplanned incident.", "official_product_api", 2026),
    ("jsm-requests", "Jira Service Management requests API", "Atlassian", "https://developer.atlassian.com/cloud/jira/service-desk/rest/api-group-request/", "support", "Customer requests carry request types, participants, status, and comments.", "official_product_api", 2026),
    ("jsm-incidents", "Jira Service Management incidents", "Atlassian", "https://support.atlassian.com/jira-service-management-cloud/docs/what-is-incident-management/", "incident", "Incident management coordinates restoration separately from request fulfillment.", "official_product_docs", 2026),
    ("zendesk-tickets", "Zendesk Tickets API", "Zendesk", "https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/", "support", "Support tickets expose status, priority, requester, assignee, and audit history.", "official_product_api", 2026),
    ("zendesk-sla", "Zendesk SLA policies API", "Zendesk", "https://developer.zendesk.com/api-reference/ticketing/business-rules/sla_policies/", "service-level", "Support SLA policies apply target metrics by conditions and priority.", "official_product_api", 2026),
    ("salesforce-case", "Salesforce Case object reference", "Salesforce", "https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_case.htm", "support", "A customer case is a CRM service object rather than an operational incident.", "official_product_api", 2026),
    ("intercom-tickets", "Intercom Tickets API", "Intercom", "https://developers.intercom.com/docs/references/rest-api/api.intercom.io/tickets", "support", "Ticket types and attributes support structured customer support workflows.", "official_product_api", 2026),
    ("github-service-catalog", "GitHub service catalog and custom properties", "GitHub", "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-custom-properties", "catalog", "Custom properties can project governed service ownership metadata.", "official_product_docs", 2026),
    ("cncf-tag-app-delivery", "CNCF Cloud Native Operational Excellence whitepaper", "CNCF", "https://tag-app-delivery.cncf.io/whitepapers/cloud-native-operational-excellence/", "service-management", "Operational excellence spans service maturity, reliability, observability, and lifecycle practices.", "official_guidance", 2024),
    ("w3c-prov", "PROV-O", "W3C", "https://www.w3.org/TR/prov-o/", "evidence", "Entities, activities, agents, and derivations form a portable provenance vocabulary.", "official_standard", 2013),
    ("in-toto", "in-toto Attestation Framework", "in-toto / CNCF", "https://github.com/in-toto/attestation/tree/main/spec", "evidence", "Typed attestations bind subjects to evidence predicates.", "official_open_spec", 2026),
    ("oci-distribution", "OCI Distribution Specification", "Open Container Initiative", "https://github.com/opencontainers/distribution-spec", "portability", "Content-addressed artifacts can be transferred through a standard distribution interface.", "official_open_spec", 2026),
    ("openapi31", "OpenAPI Specification 3.1", "OpenAPI Initiative", "https://spec.openapis.org/oas/v3.1.1.html", "portability", "Provider APIs can expose machine-readable operations and schemas without owning domain meaning.", "official_open_spec", 2024),
    ("asyncapi3", "AsyncAPI Specification 3.0", "AsyncAPI Initiative", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "event", "Asynchronous channels, operations, messages, and bindings can be separately described.", "official_open_spec", 2024),
]


GROUP_SOURCES = {
    "identity": ["tmf632", "tmf669", "k8s-multitenancy"],
    "tenant": ["k8s-multitenancy", "tmf629", "openmeter-subjects"],
    "account": ["tmf666", "openmeter-subjects"],
    "customer": ["tmf629", "tmf632"],
    "catalog": ["tmf620", "tmf633", "backstage-catalog"],
    "feature": ["openfeature", "openmeter-entitlements", "stripe-entitlements"],
    "entitlement": ["openmeter-entitlements", "openmeter-grants", "stripe-entitlements"],
    "contract": ["tmf651", "it4it3"],
    "quote": ["tmf648", "tmf679"],
    "usage": ["tmf635", "openmeter-events", "openmeter-meters", "cloudevents"],
    "rating": ["stripe-meters", "openmeter-meters", "lago-api"],
    "credit": ["tmf654", "openmeter-grants", "stripe-credit-notes"],
    "billing": ["tmf678", "focus12", "openmeter-invoices"],
    "invoice": ["ubl21", "peppol-billing", "peppol-pint"],
    "tax": ["eu-vat-invoice", "stripe-tax", "peppol-billing"],
    "payment": ["tmf676", "stripe-payment-intents", "pci-dss", "iso20022"],
    "finops": ["focus12", "finops-framework", "opencost"],
    "quota": ["k8s-resource-quota", "k8s-limit-range", "openmeter-entitlements"],
    "subscription": ["openmeter-subscriptions", "stripe-subscriptions", "killbill-subscription"],
    "ordering": ["tmf622", "tmf641", "peppol-ordering"],
    "provisioning": ["tmf638", "tmf640", "tmf701"],
    "support": ["tmf621", "zendesk-tickets", "jsm-requests", "salesforce-case"],
    "escalation": ["pagerduty-escalation", "pagerduty-incidents"],
    "maintenance": ["statuspage-maintenance", "iso20000-1"],
    "status": ["statuspage-incidents", "cloudevents"],
    "incident": ["pagerduty-incidents", "jsm-incidents", "tmf642"],
    "problem": ["tmf656", "iso20000-1"],
    "service-level": ["openslo", "tmf623", "tmf657", "zendesk-sla"],
    "evidence": ["opentelemetry", "otel-semconv", "w3c-prov", "in-toto"],
    "portability": ["iso19941", "iso19944", "oci-distribution", "openapi31"],
    "exit": ["eu-data-act", "swipo-exit", "nist-sp800-146", "iso19941"],
    "service-management": ["it4it3", "iso20000-1", "cncf-tag-app-delivery"],
}


def source_family_for_context(slug: str) -> str:
    exact = {
        "tenant-registry": "tenant", "tenant-hierarchy": "tenant", "account-registry": "account",
        "organization-registry": "identity", "workspace-registry": "tenant", "legal-entity-binding": "identity",
        "commercial-customer": "customer", "party-role": "identity", "delegated-administration": "tenant",
        "tenant-isolation": "tenant", "feature-definition": "feature", "entitlement-policy": "entitlement",
        "entitlement-grant": "entitlement", "license-seat": "entitlement", "product-catalog": "catalog",
        "service-catalog": "catalog", "plan-version": "catalog", "price-book": "rating",
        "quote-configuration": "quote", "commercial-contract": "contract", "contract-amendment": "contract",
        "meter-definition": "usage", "usage-event": "usage", "usage-attribution": "usage",
        "usage-aggregation": "usage", "rating": "rating", "charge-ledger": "billing",
        "prepaid-credit": "credit", "billing-account": "account", "billing-cycle": "billing",
        "invoice": "invoice", "tax-determination": "tax", "payment-collection": "payment",
        "refund-credit-note": "invoice", "cost-allocation": "finops", "cost-normalization": "finops", "budget-control": "finops",
        "chargeback-showback": "finops", "quota-policy": "quota", "subscription": "subscription",
        "trial": "subscription", "renewal": "subscription", "suspension-termination": "subscription",
        "product-order": "ordering", "service-order": "ordering", "provisioning": "provisioning",
        "onboarding": "service-management", "adoption-success": "customer", "support-case": "support",
        "severity-policy": "support", "escalation-routing": "escalation", "maintenance-change": "maintenance",
        "status-communication": "status", "incident": "incident", "problem": "problem",
        "service-objective": "service-level", "service-agreement": "service-level", "service-credit": "service-level",
        "customer-evidence": "evidence", "portability-export": "portability", "supplier-exit": "exit",
        "decommission": "exit", "residual-obligation": "exit",
    }
    return exact[slug]


EXTERNAL_NEIGHBORS = {
    "security": "context.security-privacy-trust.tenant-boundary",
    "runtime": "context.runtime-resource.quota-budget",
    "provider": "context.provider-target.target-occurrence",
    "product": "context.product-boundary.product-truth",
    "lineage": "context.lineage-evidence.evidence-bundle",
    "compiler": "context.compiler.release",
}


def build_sources() -> list[dict]:
    return [
        {
            "record_kind": "source",
            "source_id": sid(slug),
            "edition": EDITION,
            "status": STATUS,
            "title": title,
            "publisher": publisher,
            "url": url,
            "evidence_family": family,
            "source_kind": kind,
            "publication_or_material_year": year,
            "primary_or_official": True,
            "claim_supported": claim,
            "scope_limitation": "Supports only the stated vocabulary or implementation behavior; it does not establish legal applicability, semantic completeness, or provider-neutral conformance.",
            "accessed_at": AS_OF,
        }
        for slug, title, publisher, url, family, claim, kind, year in SOURCE_SPECS
    ]


def source_refs_for(slug: str) -> list[str]:
    return [sid(ref) for ref in GROUP_SOURCES[source_family_for_context(slug)]]


def build_contexts() -> list[dict]:
    rows = []
    for slug, name, question, owns, excludes in CONTEXT_SPECS:
        isolation_invariant = "Every command carries TenantId and authoritative scope; a mismatched or absent scope is refused before existence disclosure."
        rows.append({
            "record_kind": "bounded_context",
            "context_id": cid(slug),
            "edition": EDITION,
            "status": "research_candidate",
            "name": name,
            "sovereign_question": question,
            "subdomain_classification": "core" if slug in {"tenant-registry", "entitlement-policy", "commercial-contract", "usage-event", "rating", "invoice", "subscription", "support-case", "incident", "supplier-exit"} else "supporting",
            "owns": owns,
            "explicitly_excludes": excludes,
            "published_language": f"contract.platform-commercial-support.{slug}.v1",
            "authority_invariants": [isolation_invariant, "Mutation requires an authority reference whose subject, action, scope, and validity cover the command."],
            "tenant_isolation_invariants": ["Persistent keys, idempotency keys, caches, streams, traces, exports, and support attachments are tenant-scoped.", "Cross-tenant aggregation requires a separately evidenced disclosure authority and produces no tenant-addressable raw output."],
            "neighbor_context_refs": list(EXTERNAL_NEIGHBORS.values()),
            "source_refs": source_refs_for(slug),
            "candidate_limitations": ["Aggregate ownership and terminology require cross-universe adjudication.", "Official API evidence demonstrates implementability, not a complete or preferred implementation."],
        })
    return rows


def build_capabilities(contexts: list[dict]) -> list[dict]:
    rows = []
    for context in contexts:
        slug = context["context_id"].rsplit(".", 1)[1]
        owner = context["context_id"]
        owns = context["owns"]
        for suffix, verb, index, capability_class in [
            ("govern", "Govern", 0, "command"),
            ("evaluate", "Evaluate", 1, "decision"),
        ]:
            rows.append({
                "record_kind": "capability",
                "capability_id": f"capability.platform-commercial-support.{slug}.{suffix}",
                "edition": EDITION,
                "status": STATUS,
                "owner_context_ref": owner,
                "name": f"{verb} {owns[index]}",
                "capability_class": capability_class,
                "purpose": f"{verb.lower()} {owns[index]} without assuming any of {', '.join(context['explicitly_excludes'])}.",
                "required_authority": "tenant-scoped explicit authority or an immutable system delegation",
                "tenant_scope": "required",
                "preconditions": ["referenced editions exist", "effective-time interval is explicit", "idempotency scope is bounded"],
                "postconditions": ["append-only receipt is attributable", "no cross-tenant fact is disclosed", "downstream effects refer to exact input editions"],
                "refusals": ["tenant_scope_mismatch", "authority_missing_or_expired", "unknown_or_stale_edition", "ambiguous_effective_time"],
                "source_refs": context["source_refs"],
            })
    return rows


def build_operations(contexts: list[dict]) -> list[dict]:
    rows = []
    for context in contexts:
        slug = context["context_id"].rsplit(".", 1)[1]
        for suffix, mode, cap_suffix in [("record", "effectful_command", "govern"), ("inspect", "pure_query", "evaluate")]:
            rows.append({
                "record_kind": "operation",
                "operation_id": f"operation.platform-commercial-support.{slug}.{suffix}",
                "edition": EDITION,
                "status": STATUS,
                "owner_context_ref": context["context_id"],
                "capability_ref": f"capability.platform-commercial-support.{slug}.{cap_suffix}",
                "mode": mode,
                "input_contract_ref": f"contract.platform-commercial-support.{slug}",
                "output": "typed receipt" if mode == "effectful_command" else "tenant-filtered projection",
                "effects": ["append domain fact", "publish outbox after commit"] if mode == "effectful_command" else [],
                "idempotency": "TenantId + operation_id + caller idempotency key + payload digest",
                "consistency": "single-owner aggregate atomicity; cross-context work is a receipt-driven saga",
                "refusal_precedence": ["malformed", "unsupported_edition", "tenant_scope", "authority", "privacy_or_hold", "lifecycle", "commercial_entitlement", "quota_or_budget", "physical_feasibility", "provider_failure"],
                "source_refs": context["source_refs"],
            })
    for suffix in ["parse-source-occurrence", "normalize-record", "validate-focus-record", "explain-residuals", "project-loss-report"]:
        rows.append({
            "record_kind": "operation",
            "operation_id": f"operation.platform-commercial-support.cost-normalization.{suffix}",
            "edition": EDITION,
            "status": STATUS,
            "owner_context_ref": cid("cost-normalization"),
            "capability_ref": "capability.platform-commercial-support.cost-normalization.evaluate",
            "mode": "pure_query",
            "input_contract_ref": "contract.platform-commercial-support.cost-normalization",
            "output": "typed total normalization outcome, refusal, residual or trace projection",
            "effects": [],
            "idempotency": "canonical input occurrence, source edition, profile edition and FOCUS edition digest",
            "consistency": "pure deterministic evaluation over frozen input and policy editions",
            "refusal_precedence": ["malformed", "unsupported_focus_edition", "source_identity", "source_edition", "mandatory_semantics", "currency_unit_time", "mapping_ambiguity", "unauthorized_loss", "validation", "resource_budget"],
            "source_refs": source_refs_for("cost-normalization"),
        })
    return rows


DECISION_SPECIALS = {
    "tenant-isolation": ("Which isolation class is required?", ["shared_control_separate_data", "separate_namespace", "separate_cluster", "separate_account", "dedicated_stack"]),
    "entitlement-policy": ("How may absence of an entitlement be interpreted?", ["deny", "allow_only_explicit_free_feature", "not_applicable"]),
    "usage-event": ("Which duplicate law applies to usage events?", ["reject_same_id_different_payload", "idempotent_same_id_same_digest"]),
    "usage-aggregation": ("How are late accepted events handled after window finalization?", ["new_correction_edition", "next_window_with_lineage", "reject_by_declared_cutoff"]),
    "rating": ("Which rate-card edition prices an aggregate?", ["event_time_effective", "window_end_effective", "contract_fixed_edition"]),
    "invoice": ("May a finalized invoice be mutated?", ["never_issue_credit_or_debit_note", "jurisdiction_qualified_correction_document"]),
    "budget-control": ("What happens when a hard budget cannot be atomically reserved?", ["refuse", "hold_for_approval"]),
    "cost-normalization": ("How must a provider field that has no lossless mapping to the selected FOCUS edition be handled?", ["retain_typed_residual_and_continue_if_profile_allows", "refuse_record", "retain_source_occurrence_as_unmapped_without_normalized_claim"]),
    "quota-policy": ("Can quota availability imply capacity availability?", ["never"]),
    "suspension-termination": ("What data consequence follows suspension or termination?", ["retain_per_residual_obligations", "schedule_separate_deletion_workflow"]),
    "service-credit": ("Does an SLO breach automatically award a service credit?", ["never_require_sla_eligibility_and_claim", "only_if_contract_explicitly_automatic"]),
    "supplier-exit": ("When is product exit complete?", ["accepted_transition_and_obligation_schedule", "provider_attested_with_customer_dispute_window"]),
}


def build_decisions(contexts: list[dict]) -> list[dict]:
    rows = []
    for context in contexts:
        slug = context["context_id"].rsplit(".", 1)[1]
        question, allowed = DECISION_SPECIALS.get(slug, (f"Which explicit policy edition governs {context['owns'][0]}?", ["explicit_tenant_policy", "explicit_contract_policy", "explicit_platform_policy", "not_applicable"]))
        rows.append({
            "record_kind": "decision",
            "decision_id": f"decision.platform-commercial-support.{slug}.policy",
            "edition": EDITION,
            "status": STATUS,
            "owner_context_ref": context["context_id"],
            "question": question,
            "allowed_values": allowed,
            "binding_phase": "commercial_and_operational_ir",
            "authority_ref": "authority.product-owner-or-delegated-tenant-admin",
            "default_law": "forbidden",
            "default_value": None,
            "constraints": ["must be tenant-scoped", "must cite effective policy or contract edition"],
            "conflicts": ["security and privacy prohibitions dominate commercial allowance", "runtime infeasibility cannot be overridden by entitlement"],
            "invalidation": ["policy edition changes", "contract edition changes", "tenant binding changes", "source evidence expires"],
            "source_refs": context["source_refs"],
        })
    return rows


LIFECYCLE_SPECS = [
    ("tenant-registry", "tenant", ["proposed", "active", "suspended", "terminated", "rejected"]),
    ("workspace-registry", "workspace", ["pending", "active", "archived", "deleted", "rejected"]),
    ("delegated-administration", "delegation", ["draft", "active", "revoked", "expired", "rejected"]),
    ("entitlement-grant", "entitlement-grant", ["draft", "active", "exhausted", "expired", "revoked"]),
    ("license-seat", "seat-assignment", ["requested", "assigned", "released", "expired", "rejected"]),
    ("product-catalog", "product-offer-edition", ["draft", "published", "withdrawn", "retired", "rejected"]),
    ("service-catalog", "service-offer-edition", ["draft", "published", "withdrawn", "retired", "rejected"]),
    ("plan-version", "plan-version", ["draft", "published", "grandfathered", "retired", "rejected"]),
    ("quote-configuration", "quote", ["draft", "presented", "accepted", "expired", "rejected"]),
    ("commercial-contract", "contract", ["draft", "approved", "active", "expired", "terminated"]),
    ("usage-event", "usage-event", ["received", "validated", "accepted", "rejected", "superseded"]),
    ("usage-aggregation", "usage-aggregate", ["open", "provisional", "final", "corrected", "rejected"]),
    ("rating", "rated-usage", ["pending", "rated", "posted", "reversed", "rejected"]),
    ("charge-ledger", "charge-entry", ["pending", "posted", "allocated", "reversed", "rejected"]),
    ("prepaid-credit", "credit-grant", ["issued", "active", "depleted", "expired", "revoked"]),
    ("billing-account", "billing-account", ["pending", "active", "delinquent", "closed", "rejected"]),
    ("billing-cycle", "billing-cycle", ["scheduled", "open", "closing", "closed", "abandoned"]),
    ("invoice", "invoice", ["draft", "open", "paid", "void", "uncollectible"]),
    ("payment-collection", "payment-intent", ["requires_method", "requires_confirmation", "processing", "succeeded", "canceled"]),
    ("refund-credit-note", "refund", ["requested", "approved", "processing", "succeeded", "rejected"]),
    ("budget-control", "budget", ["draft", "active", "alerted", "closed", "exhausted"]),
    ("quota-policy", "quota", ["draft", "active", "exhausted", "retired", "rejected"]),
    ("subscription", "subscription", ["pending", "trialing", "active", "canceled", "expired"]),
    ("trial", "trial", ["proposed", "active", "converted", "expired", "canceled"]),
    ("renewal", "renewal-case", ["not_due", "evaluating", "offered", "accepted", "declined"]),
    ("suspension-termination", "service-access", ["active", "suspended", "termination_pending", "terminated", "rejected"]),
    ("product-order", "product-order", ["acknowledged", "in_progress", "completed", "cancelled", "failed"]),
    ("service-order", "service-order", ["acknowledged", "in_progress", "completed", "cancelled", "failed"]),
    ("provisioning", "provisioning-plan", ["planned", "executing", "verifying", "active", "failed"]),
    ("onboarding", "onboarding-plan", ["planned", "in_progress", "ready", "accepted", "cancelled"]),
    ("adoption-success", "success-plan", ["draft", "active", "at_risk", "achieved", "retired"]),
    ("support-case", "support-case", ["new", "open", "pending", "solved", "closed"]),
    ("escalation-routing", "escalation", ["pending", "routed", "acknowledged", "completed", "timed_out"]),
    ("maintenance-change", "change", ["proposed", "scheduled", "in_progress", "completed", "rolled_back"]),
    ("status-communication", "status-notice", ["draft", "published", "superseded", "retracted", "archived"]),
    ("incident", "incident", ["detected", "triaged", "mitigated", "resolved", "false_positive"]),
    ("problem", "problem", ["logged", "investigating", "known_error", "resolved", "closed"]),
    ("service-objective", "slo", ["draft", "active", "breached", "retired", "rejected"]),
    ("service-agreement", "sla", ["draft", "agreed", "active", "expired", "terminated"]),
    ("service-credit", "service-credit-claim", ["submitted", "validating", "approved", "applied", "rejected"]),
    ("customer-evidence", "evidence-package", ["requested", "assembling", "sealed", "delivered", "revoked"]),
    ("portability-export", "export", ["requested", "generating", "validating", "transferred", "failed"]),
    ("supplier-exit", "exit-plan", ["proposed", "planned", "executing", "complete", "aborted"]),
    ("decommission", "decommission-plan", ["proposed", "approved", "draining", "complete", "failed"]),
    ("residual-obligation", "residual-obligation", ["identified", "active", "due", "discharged", "breached"]),
]


def build_state_machines() -> list[dict]:
    rows = []
    for context_slug, subject, states in LIFECYCLE_SPECS:
        transitions = []
        commands = []
        for left, right in zip(states[:3], states[1:4]):
            command = f"advance_to_{right}"
            commands.append(command)
            transitions.append({"from": left, "command": command, "to": right, "guard": "authority, scope, edition, and stated preconditions pass"})
        terminal_command = f"terminate_as_{states[4]}"
        commands.append(terminal_command)
        for state in states[:3]:
            transitions.append({"from": state, "command": terminal_command, "to": states[4], "guard": "terminal outcome evidence is authoritative"})
        transition_pairs = {(item["from"], item["command"]) for item in transitions}
        refusals = [
            {"state": state, "command": command, "refusal": "illegal_or_already_terminal_transition"}
            for state in states
            for command in commands
            if (state, command) not in transition_pairs
        ]
        rows.append({
            "record_kind": "state_machine",
            "state_machine_id": f"state-machine.platform-commercial-support.{subject}",
            "edition": EDITION,
            "status": STATUS,
            "owner_context_ref": cid(context_slug),
            "subject": subject,
            "states": states,
            "initial_state": states[0],
            "terminal_states": states[3:],
            "commands": commands,
            "transitions": transitions,
            "refusal_matrix": refusals,
            "totality_law": "For every declared state and command pair, exactly one transition or typed refusal is defined.",
            "concurrency": "Optimistic edition compare-and-swap; a losing command is refused and may be retried against the new edition.",
            "idempotency": "Same tenant, subject, command id, and payload digest returns the original receipt.",
            "outcome_precedence": ["authoritative terminal fact", "accepted transition commit", "timeout observation", "caller cancellation"],
            "source_refs": source_refs_for(context_slug),
        })
    return rows


def build_contracts(contexts: list[dict]) -> list[dict]:
    rows = []
    for context in contexts:
        slug = context["context_id"].rsplit(".", 1)[1]
        fields = ["tenant_id", f"{slug.replace('-', '_')}_id", "edition", "effective_from", "effective_until", "authority_ref", "source_refs"]
        rows.append({
            "record_kind": "contract",
            "contract_id": f"contract.platform-commercial-support.{slug}",
            "edition": EDITION,
            "status": STATUS,
            "owner_context_ref": context["context_id"],
            "contract_kind": "semantic_aggregate_envelope",
            "fields": fields,
            "required_fields": fields[:6],
            "identity_law": f"tenant_id plus {fields[1]} identifies an aggregate occurrence; edition identifies immutable state.",
            "time_law": "Intervals are half-open [effective_from, effective_until); absent end means unbounded only when the owner explicitly permits it.",
            "money_law": "Any monetary field is integer minor units or exact decimal plus ISO 4217 currency and rounding edition; binary float is forbidden.",
            "authority_law": "authority_ref is evaluated before mutation and retained in the receipt.",
            "tenant_law": "All foreign references are checked for the same tenant or an explicit cross-tenant disclosure authority.",
            "event_law": "Events are past-tense immutable facts and use an outbox; command acceptance is not downstream completion.",
            "must_not_be_confused_with": context["explicitly_excludes"],
            "source_refs": context["source_refs"],
        })
    return rows


INVARIANT_SPECS = [
    ("tenant-before-lookup", "authority_invariant", "Resolve and validate TenantId before any tenant-addressable lookup; unknown and unauthorized identifiers share a non-enumerating refusal."),
    ("tenant-keying", "tenant_isolation_invariant", "Every durable key, cache key, idempotency key, event partition, trace projection, attachment, export, and provider binding includes tenant scope."),
    ("cross-tenant-explicit", "tenant_isolation_invariant", "Cross-tenant aggregation requires an explicit purpose, authority, minimization rule, and evidence receipt; raw tenant-identifiable output is forbidden by default."),
    ("identity-separation", "semantic_invariant", "Tenant identity, product account, organization, workspace, commercial customer, billing account, payer, and legal entity remain separately identified and explicitly related."),
    ("entitlement-not-authorization", "semantic_invariant", "Commercial entitlement may satisfy a product-access prerequisite but never grants a security permission or bypasses policy enforcement."),
    ("four-limits", "semantic_invariant", "Commercial entitlement, technical quota, finite budget/prepaid balance, and physical capacity are evaluated and reported separately."),
    ("usage-layering", "semantic_invariant", "Meter event, accepted usage, attributed usage, aggregate usage, rated usage, charge entry, and invoice line have different identities and immutable lineage."),
    ("catalog-contract", "semantic_invariant", "A plan or catalog offer is reusable proposal material; only an effective signed contract projection and subscription bind customer-specific terms."),
    ("slo-sla-credit", "semantic_invariant", "An internal SLO evaluation is not a contractual SLA breach, and an SLA breach is not an awarded service credit without eligibility and claim rules."),
    ("support-incident-problem", "semantic_invariant", "Customer support case, operational incident, alert, and problem/known error are linked but never share identity or lifecycle."),
    ("maintenance-outage", "semantic_invariant", "Approved maintenance remains planned change; observed customer impact is recorded separately and may still constitute an incident or SLA event."),
    ("suspend-revoke-delete", "semantic_invariant", "Suspension, entitlement revocation, contract termination, tenant deletion, and data destruction are separate commands with separate authority and evidence."),
    ("exit-not-export", "semantic_invariant", "Product or supplier exit is incomplete when only data export is complete; dependencies, credentials, service transition, decommission, evidence, and residual obligations remain."),
    ("money-exact", "semantic_invariant", "Money uses exact amount, currency, scale/rounding policy, and effective price/tax edition; binary floating point is forbidden."),
    ("append-only-financial", "semantic_invariant", "Accepted usage, posted charge, finalized invoice, payment, and credit facts are corrected by linked adjustment or reversal, never destructive mutation."),
    ("effective-time", "semantic_invariant", "Catalog, plan, price, contract, entitlement, quota, tax, SLA, and policy evaluation binds exact effective-time editions."),
    ("authority-evidence", "authority_invariant", "Every mutating receipt retains actor, delegation/authority, tenant scope, command digest, decision edition, and event/recorded time."),
    ("provider-not-owner", "boundary_invariant", "Provider APIs and adapters implement ports; provider object names never become provider-neutral semantic owners."),
    ("refuse-unknown-edition", "refusal", "Unknown schema, policy, catalog, meter, price, contract, or adapter edition is refused before effects rather than coerced to latest."),
    ("refuse-missing-scope", "refusal", "Missing or ambiguous tenant, billing, contract, time, currency, or measurement scope is a typed refusal, not a platform default."),
    ("refuse-unauthorized-before-entitlement", "refusal", "Security/privacy prohibition is evaluated before commercial entitlement to prevent feature purchases from widening authority."),
    ("refuse-no-entitlement", "refusal", "A feature requiring commercial entitlement is refused when no active grant covers subject, feature, scope, and effective time."),
    ("refuse-quota-separately", "refusal", "Quota exhaustion is reported separately from entitlement denial, budget exhaustion, credit depletion, rate limit, and physical infeasibility."),
    ("refuse-budget-before-effect", "refusal", "Hard finite budget or prepaid consumption is atomically reserved before an irreversible billable effect; failure refuses or holds work."),
    ("refuse-stale-rating", "refusal", "Rating is refused when meter aggregate lineage, price edition, contract override, currency, or rounding policy is unresolved."),
    ("refuse-invoice-without-lineage", "refusal", "An invoice cannot finalize while any line lacks charge-entry, rating, adjustment, tax, and billing-account lineage."),
    ("refuse-maintenance-masquerade", "refusal", "An observed outage cannot be reclassified away merely because a maintenance window exists."),
    ("refuse-credit-from-slo", "refusal", "An SLO breach alone cannot create a service-credit award."),
    ("refuse-delete-on-terminate", "refusal", "Termination cannot invoke deletion or destruction without a separate disposition plan, hold/retention decision, and authority."),
    ("refuse-exit-without-verification", "refusal", "Exit completion is refused until export manifests, transfer verification, dependency disposition, credential revocation, decommission state, and residual obligations are accounted."),
    ("precedence-malformed", "failure_precedence", "Malformed or unsupported-edition input dominates all domain evaluation because no trustworthy command exists."),
    ("precedence-tenant-authority", "failure_precedence", "Tenant-scope mismatch and authority/privacy prohibition dominate lifecycle, entitlement, quota, budget, capacity, and provider errors."),
    ("precedence-lifecycle-commercial", "failure_precedence", "Illegal lifecycle state dominates entitlement, quota, budget, capacity, and downstream provider execution."),
    ("precedence-entitlement-limits", "failure_precedence", "Entitlement denial precedes quota, budget, physical capacity, and provider availability; each retains its distinct code."),
    ("precedence-commit-timeout", "failure_precedence", "A committed authoritative terminal fact dominates caller timeout or cancellation observation; an unknown outcome requires reconciliation, never guessed failure."),
]


def build_invariants_refusals() -> list[dict]:
    source_map = {
        "authority_invariant": [sid("k8s-multitenancy"), sid("w3c-prov")],
        "tenant_isolation_invariant": [sid("k8s-multitenancy"), sid("opentelemetry")],
        "semantic_invariant": [sid("tmf629"), sid("openmeter-subjects"), sid("focus12")],
        "boundary_invariant": [sid("openapi31"), sid("tmf640")],
        "refusal": [sid("it4it3"), sid("iso20000-1")],
        "failure_precedence": [sid("cloudevents"), sid("stripe-payment-intents")],
    }
    return [
        {
            "record_kind": kind,
            "rule_id": f"rule.platform-commercial-support.{slug}",
            "edition": EDITION,
            "status": STATUS,
            "law": law,
            "enforcement_phases": ["input admission", "IR binding", "aggregate command", "provider effect", "receipt reconciliation"],
            "violation_result": "typed refusal plus non-sensitive evidence reference",
            "source_refs": source_map[kind],
        }
        for slug, kind, law in INVARIANT_SPECS
    ]


LIBRARY_SPECS = [
    ("tenant-identity", "semantic_pure", ["tenant-registry", "tenant-hierarchy"], "pure_no_io", None),
    ("account_identity", "semantic_pure", ["account-registry"], "pure_no_io", None),
    ("customer_party_identity", "semantic_pure", ["commercial-customer"], "pure_no_io", None),
    ("billing_account_identity", "semantic_pure", ["billing-account"], "pure_no_io", None),
    ("legal_entity_binding", "semantic_pure", ["legal-entity-binding"], "pure_no_io", None),
    ("feature_definition", "semantic_pure", ["feature-definition"], "pure_no_io", "openmeter-entitlements"),
    ("entitlement_decision_policy", "policy_pure", ["entitlement-policy"], "pure_no_io", "openmeter-entitlements"),
    ("entitlement_grant", "semantic_pure", ["entitlement-grant"], "pure_no_io", "openmeter-entitlements"),
    ("license_seat", "semantic_pure", ["license-seat"], "pure_no_io", "openmeter-entitlements"),
    ("quota-algebra", "policy_pure", ["quota-policy"], "pure_no_io", "k8s-resource-quota"),
    ("commercial-credit-preauthorization", "policy_pure", ["budget-control", "prepaid-credit"], "pure_effect_intents", "finops-framework"),
    ("meter_definition", "semantic_pure", ["meter-definition"], "pure_no_io", "openmeter-meters"),
    ("usage_event", "semantic_pure", ["usage-event"], "pure_no_io", "openmeter-events"),
    ("usage_aggregation", "algorithm_pure", ["usage-aggregation"], "pure_no_io", "openmeter-meters"),
    ("rating-core", "algorithm_pure", ["rating", "price-book"], "pure_no_io", "stripe-meters"),
    ("invoice-arithmetic", "algorithm_pure", ["invoice", "refund-credit-note"], "pure_no_io", "peppol-billing"),
    ("allocation-core", "algorithm_pure", ["cost-allocation", "chargeback-showback"], "pure_no_io", "focus12"),
    ("focus-normalization", "semantic_pure", ["cost-normalization"], "pure_no_io", "focus12"),
    ("slo_evaluator", "algorithm_pure", ["service-objective"], "pure_no_io", "openslo"),
    ("sla_eligibility", "policy_pure", ["service-agreement"], "pure_no_io", "tmf633"),
    ("service_credit_decision", "policy_pure", ["service-credit"], "pure_effect_intents", "stripe-credit-notes"),
    ("subscription_lifecycle", "semantic_pure", ["subscription"], "pure_no_io", "openmeter-entitlements"),
    ("product_order_lifecycle", "semantic_pure", ["product-order"], "pure_no_io", "tmf622"),
    ("service_order_lifecycle", "semantic_pure", ["service-order"], "pure_no_io", "tmf641"),
    ("support_case_lifecycle", "semantic_pure", ["support-case"], "pure_no_io", "tmf621"),
    ("incident_lifecycle", "semantic_pure", ["incident"], "pure_no_io", "pagerduty-incidents"),
    ("exit-manifest", "semantic_pure", ["portability-export", "supplier-exit", "decommission", "residual-obligation"], "pure_no_io", "iso19941"),
    ("usage-journal-port", "effect_port", ["usage-event"], "declared_append_and_read", None),
    ("catalog-repository-port", "effect_port", ["product-catalog", "service-catalog", "plan-version", "price-book"], "declared_versioned_repository", None),
    ("tax-determination-port", "effect_port", ["tax-determination"], "declared_external_calculation", None),
    ("payment-collection-port", "effect_port", ["payment-collection", "refund-credit-note"], "declared_external_payment", None),
    ("support-case-port", "effect_port", ["support-case", "severity-policy"], "declared_ticket_effect", None),
    ("incident-routing-port", "effect_port", ["incident", "escalation-routing"], "declared_page_and_ack", None),
    ("status-publication-port", "effect_port", ["status-communication", "maintenance-change"], "declared_publication", None),
    ("export-transfer-port", "effect_port", ["portability-export", "supplier-exit"], "declared_transfer_and_verify", None),
    ("evidence-signing-port", "effect_port", ["customer-evidence"], "declared_sign_and_disclose", None),
    ("openmeter-adapter", "provider_adapter", ["meter-definition", "usage-event", "entitlement-grant", "subscription"], "external_io", "openmeter-events"),
    ("stripe-adapter", "provider_adapter", ["usage-event", "rating", "invoice", "payment-collection", "subscription"], "external_io", "stripe-meter-events"),
    ("peppol-adapter", "provider_adapter", ["invoice", "refund-credit-note"], "external_io", "peppol-billing"),
    ("tmforum-adapter", "provider_adapter", ["product-catalog", "product-order", "service-order", "support-case"], "external_io", "tmf620"),
    ("pagerduty-adapter", "provider_adapter", ["incident", "escalation-routing"], "external_io", "pagerduty-incidents"),
    ("statuspage-adapter", "provider_adapter", ["status-communication", "maintenance-change"], "external_io", "statuspage-incidents"),
    ("zendesk-adapter", "provider_adapter", ["support-case", "service-agreement"], "external_io", "zendesk-tickets"),
]

PLATFORM_LIBRARY_REPLACEMENTS = [
    ("library.platform-commercial-support.commercial-identities", ["account-registry", "commercial-customer", "billing-account", "legal-entity-binding"], ["library.platform-commercial-support.account_identity", "library.platform-commercial-support.customer_party_identity", "library.platform-commercial-support.billing_account_identity", "library.platform-commercial-support.legal_entity_binding"], "Platform account, commercial customer, billing account and external legal entity have different issuers, equality, authority and lifecycles."),
    ("library.platform-commercial-support.meter-algebra", ["meter-definition", "usage-event", "usage-aggregation"], ["library.platform-commercial-support.meter_definition", "library.platform-commercial-support.usage_event", "library.platform-commercial-support.usage_aggregation"], "Meter definition, immutable usage occurrence and derived aggregation have different identity, correction, replay and compatibility laws."),
    ("library.platform-commercial-support.service-level-evaluator", ["service-objective", "service-agreement", "service-credit"], ["library.platform-commercial-support.slo_evaluator", "library.platform-commercial-support.sla_eligibility", "library.platform-commercial-support.service_credit_decision"], "SLO evaluation, contractual SLA eligibility and credit award are separate evidence, policy and authority transitions."),
    ("library.platform-commercial-support.entitlement-algebra", ["feature-definition", "entitlement-policy", "entitlement-grant", "license-seat"], ["library.csp.authority.entitlement", "library.csp.authority.policy-algebra", "library.platform-commercial-support.feature_definition", "library.platform-commercial-support.entitlement_decision_policy", "library.platform-commercial-support.entitlement_grant", "library.platform-commercial-support.license_seat"], "Feature definition, decision policy, grant occurrence and license-seat allocation have separate identities and lifecycles while importing shared authority primitives."),
    ("library.platform-commercial-support.lifecycle-reducer", ["subscription", "product-order", "service-order", "support-case", "incident"], ["library.platform-commercial-support.subscription_lifecycle", "library.platform-commercial-support.product_order_lifecycle", "library.platform-commercial-support.service_order_lifecycle", "library.platform-commercial-support.support_case_lifecycle", "library.platform-commercial-support.incident_lifecycle"], "Subscription, product order, service order, support case and incident lifecycles have incompatible commands, authorities, terminal facts and compensation rules."),
    ("library.platform-commercial-support.effective-interval", ["contract-amendment", "billing-cycle", "renewal"], ["library.csp.time.interval-algebra"], "Shared half-open interval algebra is imported; amendment, cycle and renewal keep their domain policy."),
    ("library.platform-commercial-support.money", ["price-book", "charge-ledger", "invoice", "prepaid-credit"], ["library.csp.quantity.money-core"], "Shared exact amount/currency arithmetic is imported; price, balance, charge and invoice remain separate values."),
]


def build_library_replacements() -> list[dict]:
    return [{
        "record_kind": "library_replacement",
        "replacement_id": f"replacement.platform-commercial-support.{legacy.rsplit('.', 1)[1]}",
        "edition": EDITION,
        "status": STATUS,
        "retired_library_ref": legacy,
        "covered_context_refs": [cid(owner) for owner in owners],
        "replacement_library_refs": replacements,
        "compatibility_alias_permitted": False,
        "rationale": rationale,
        "closure_law": "All former uses bind the exact shared primitive plus their domain-specific contract; product packaging may not recreate the retired facade.",
    } for legacy, owners, replacements, rationale in PLATFORM_LIBRARY_REPLACEMENTS]

# These pure boundaries have one adjudicated meaning owner; the remaining
# contexts consume or contribute contracts. Other multi-context pure candidates
# remain explicitly ambiguous until their rename, replacement or split closes.
PCS_UNIQUE_LIBRARY_OWNER = {
    "allocation-core": "cost-allocation",
    "exit-manifest": "portability-export",
    "invoice-arithmetic": "invoice",
    "rating-core": "rating",
    "tenant-identity": "tenant-registry",
    "commercial-credit-preauthorization": "budget-control",
}


EXACT_SPLIT_APIS = {
    "account_identity": {
        "types": ["PlatformAccountId", "PlatformAccountEdition", "AccountStatus", "AccountIdentityPolicy", "AccountIdentityDiff", "AccountIdentityRefusal"],
        "trait": "PlatformAccountIdentityAlgebra",
        "operations": [
            ("validate_account_edition", ["PlatformAccountEdition", "AccountIdentityPolicy"], "Result<ValidatedPlatformAccountEdition,AccountIdentityRefusal>"),
            ("compare_account_editions", ["PlatformAccountEdition", "PlatformAccountEdition"], "Result<AccountIdentityDiff,AccountIdentityRefusal>"),
            ("derive_account_transition", ["ValidatedPlatformAccountEdition", "AccountTransitionCommand", "AccountIdentityPolicy"], "Result<AccountIdentityTransition,AccountIdentityRefusal>"),
        ],
        "errors": ["AccountIssuerUnbound", "AccountIdCollision", "AccountEditionConflict", "AccountTransitionInvalid", "AccountStatusUnknown", "ResourceBudgetExceeded"],
        "laws": ["account identity is issued only within one account registry authority", "account identifier edition status and provider occurrence are distinct", "an immutable account edition is never rewritten by a later status transition"],
    },
    "customer_party_identity": {
        "types": ["CommercialPartyId", "CommercialPartyEdition", "PartyKind", "PartyRoleBinding", "PartyIdentityPolicy", "PartyIdentityRefusal"],
        "trait": "CommercialPartyIdentityAlgebra",
        "operations": [
            ("validate_party_edition", ["CommercialPartyEdition", "PartyIdentityPolicy"], "Result<ValidatedCommercialPartyEdition,PartyIdentityRefusal>"),
            ("bind_party_role", ["ValidatedCommercialPartyEdition", "PartyRoleBinding", "PartyIdentityPolicy"], "Result<ValidatedPartyRoleBinding,PartyIdentityRefusal>"),
            ("compare_party_editions", ["CommercialPartyEdition", "CommercialPartyEdition"], "Result<PartyIdentityDiff,PartyIdentityRefusal>"),
        ],
        "errors": ["PartyIssuerUnbound", "PartyKindUnsupported", "PartyIdentityCollision", "PartyRoleInvalid", "PartyEditionConflict", "ResourceBudgetExceeded"],
        "laws": ["commercial party identity is not a platform account billing account tenant or legal-entity identifier", "a role binding never changes party identity", "party aliases preserve issuer scope and historical validity"],
    },
    "billing_account_identity": {
        "types": ["BillingAccountId", "BillingAccountEdition", "BillToPartyRef", "BillingProfileRef", "BillingAccountPolicy", "BillingAccountRefusal"],
        "trait": "BillingAccountIdentityAlgebra",
        "operations": [
            ("validate_billing_account", ["BillingAccountEdition", "BillingAccountPolicy"], "Result<ValidatedBillingAccountEdition,BillingAccountRefusal>"),
            ("bind_bill_to_party", ["ValidatedBillingAccountEdition", "BillToPartyRef", "BillingAccountPolicy"], "Result<BillToBinding,BillingAccountRefusal>"),
            ("derive_billing_account_transition", ["ValidatedBillingAccountEdition", "BillingAccountCommand", "BillingAccountPolicy"], "Result<BillingAccountTransition,BillingAccountRefusal>"),
        ],
        "errors": ["BillingAccountIssuerUnbound", "BillingAccountCollision", "BillToPartyUnresolved", "BillingProfileUnresolved", "BillingAccountTransitionInvalid", "ResourceBudgetExceeded"],
        "laws": ["billing account identity is not customer party platform account invoice or payment instrument identity", "bill-to bindings are editioned and temporally scoped", "closing a billing account does not erase invoices charges or historical bindings"],
    },
    "legal_entity_binding": {
        "types": ["ExternalLegalEntityRef", "LegalEntityBindingEdition", "VerificationEvidenceRef", "BindingValidity", "LegalEntityBindingPolicy", "LegalEntityBindingRefusal"],
        "trait": "LegalEntityBindingAlgebra",
        "operations": [
            ("validate_legal_entity_binding", ["LegalEntityBindingEdition", "LegalEntityBindingPolicy"], "Result<ValidatedLegalEntityBinding,LegalEntityBindingRefusal>"),
            ("evaluate_binding_evidence", ["LegalEntityBindingEdition", "VerificationEvidenceRef", "LegalEntityBindingPolicy"], "Result<LegalEntityEvidenceAssessment,LegalEntityBindingRefusal>"),
            ("supersede_legal_entity_binding", ["ValidatedLegalEntityBinding", "LegalEntityBindingEdition", "LegalEntityBindingPolicy"], "Result<LegalEntityBindingTransition,LegalEntityBindingRefusal>"),
        ],
        "errors": ["ExternalRegistryUnbound", "LegalEntityRefInvalid", "VerificationEvidenceMissing", "BindingValidityOverlap", "BindingAuthorityMissing", "ResourceBudgetExceeded"],
        "laws": ["an external legal-entity reference is imported and never issued by the platform", "verification evidence does not prove every legal or commercial role", "binding supersession preserves the exact external registry edition and evidence cut"],
    },
    "meter_definition": {
        "types": ["MeterDefinitionId", "MeterDefinitionEdition", "MeasurementUnitRef", "AggregationFunction", "GroupingKey", "MeterDefinitionPolicy", "MeterDefinitionRefusal"],
        "trait": "MeterDefinitionAlgebra",
        "operations": [
            ("validate_meter_definition", ["MeterDefinitionEdition", "MeterDefinitionPolicy"], "Result<ValidatedMeterDefinitionEdition,MeterDefinitionRefusal>"),
            ("compare_meter_editions", ["MeterDefinitionEdition", "MeterDefinitionEdition"], "Result<MeterDefinitionDiff,MeterDefinitionRefusal>"),
            ("compile_meter_definition", ["ValidatedMeterDefinitionEdition", "MeterDefinitionPolicy"], "Result<CompiledMeterDefinition,MeterDefinitionRefusal>"),
        ],
        "errors": ["MeterIdCollision", "MeasurementUnitUnresolved", "AggregationUnsupported", "GroupingKeyInvalid", "MeterEditionConflict", "ResourceBudgetExceeded"],
        "laws": ["meter definition usage occurrence and usage aggregate have distinct identities", "a meter edition fixes unit aggregation grouping and temporal semantics", "changing aggregation semantics requires a new meter edition"],
    },
    "usage_event": {
        "types": ["UsageEventId", "UsageOccurrence", "UsageSubjectRef", "EventTime", "RecordingTime", "IdempotencyScope", "UsageEventPolicy", "UsageEventRefusal"],
        "trait": "UsageOccurrenceAlgebra",
        "operations": [
            ("validate_usage_occurrence", ["UsageOccurrence", "MeterDefinitionEdition", "UsageEventPolicy"], "Result<ValidatedUsageOccurrence,UsageEventRefusal>"),
            ("classify_duplicate_occurrence", ["ValidatedUsageOccurrence", "UsageOccurrence", "IdempotencyScope"], "Result<DuplicateClassification,UsageEventRefusal>"),
            ("derive_usage_correction", ["ValidatedUsageOccurrence", "UsageCorrection", "UsageEventPolicy"], "Result<UsageCorrectionTransition,UsageEventRefusal>"),
        ],
        "errors": ["UsageEventIdMissing", "MeterEditionUnbound", "UsageSubjectUnresolved", "UsageValueInvalid", "DuplicateConflict", "CorrectionPolicyViolated", "ResourceBudgetExceeded"],
        "laws": ["usage occurrence is not requested allocated rated billed or invoiced usage", "event time and recording time remain distinct", "deduplication is scoped and never discards a conflicting occurrence silently", "a correction references rather than rewrites the original occurrence"],
    },
    "usage_aggregation": {
        "types": ["UsageAggregationRequest", "AggregationCut", "UsageWindow", "UsageAggregate", "AggregationResidual", "UsageAggregationPolicy", "UsageAggregationRefusal"],
        "trait": "UsageAggregationAlgebra",
        "operations": [
            ("validate_aggregation_request", ["UsageAggregationRequest", "MeterDefinitionEdition", "UsageAggregationPolicy"], "Result<ValidatedAggregationRequest,UsageAggregationRefusal>"),
            ("aggregate_usage_cut", ["ValidatedAggregationRequest", "AggregationCut", "UsageAggregationPolicy"], "Result<UsageAggregationOutcome,UsageAggregationRefusal>"),
            ("reconcile_usage_aggregate", ["UsageAggregate", "AggregationCut", "UsageAggregationPolicy"], "Result<UsageAggregationReconciliation,UsageAggregationRefusal>"),
        ],
        "errors": ["AggregationCutOpen", "MeterEditionMismatch", "UsageWindowInvalid", "LateOccurrencePostureMissing", "CorrectionSetIncomplete", "AggregateUnreconciled", "ResourceBudgetExceeded"],
        "laws": ["an aggregate binds one meter edition input cut window grouping and correction posture", "aggregate value never erases constituent occurrence identity", "late excluded corrected and rejected occurrences remain explicit residuals", "aggregation is not rating allocation charge or invoice arithmetic"],
    },
    "slo_evaluator": {
        "types": ["ServiceObjectiveEdition", "IndicatorObservationCut", "EvaluationWindow", "SloEvaluationResult", "ErrorBudgetState", "SloEvaluationPolicy", "SloEvaluationRefusal"],
        "trait": "ServiceObjectiveEvaluationAlgebra",
        "operations": [
            ("validate_service_objective", ["ServiceObjectiveEdition", "SloEvaluationPolicy"], "Result<ValidatedServiceObjective,SloEvaluationRefusal>"),
            ("evaluate_service_objective", ["ValidatedServiceObjective", "IndicatorObservationCut", "EvaluationWindow"], "Result<SloEvaluationResult,SloEvaluationRefusal>"),
            ("derive_error_budget_state", ["SloEvaluationResult", "SloEvaluationPolicy"], "Result<ErrorBudgetState,SloEvaluationRefusal>"),
        ],
        "errors": ["ObjectiveEditionUnbound", "IndicatorDefinitionUnbound", "ObservationCutIncomplete", "EvaluationWindowInvalid", "MissingDataPostureUnknown", "EvaluationIndeterminate", "ResourceBudgetExceeded"],
        "laws": ["telemetry observation SLI value SLO evaluation SLA eligibility and credit award are distinct", "an evaluation binds one objective edition observation cut window and missing-data policy", "unknown or incomplete observations never become a silent pass"],
    },
    "sla_eligibility": {
        "types": ["ServiceAgreementEdition", "SloEvaluationRef", "EligibilityWindow", "ExclusionEvidenceSet", "SlaEligibilityDecision", "SlaEligibilityPolicy", "SlaEligibilityRefusal"],
        "trait": "ServiceAgreementEligibilityAlgebra",
        "operations": [
            ("validate_service_agreement", ["ServiceAgreementEdition", "SlaEligibilityPolicy"], "Result<ValidatedServiceAgreement,SlaEligibilityRefusal>"),
            ("evaluate_sla_eligibility", ["ValidatedServiceAgreement", "SloEvaluationRef", "ExclusionEvidenceSet"], "Result<SlaEligibilityDecision,SlaEligibilityRefusal>"),
            ("explain_sla_eligibility", ["SlaEligibilityDecision", "SlaEligibilityPolicy"], "Result<SlaEligibilityExplanation,SlaEligibilityRefusal>"),
        ],
        "errors": ["AgreementEditionUnbound", "EvaluationScopeMismatch", "EligibilityWindowInvalid", "ExclusionEvidenceIncomplete", "ContractTermAmbiguous", "EligibilityIndeterminate", "ResourceBudgetExceeded"],
        "laws": ["SLO failure does not by itself establish contractual SLA eligibility", "eligibility binds exact agreement terms service scope evaluation and exclusions", "an eligibility decision has no authority to issue a credit"],
    },
    "service_credit_decision": {
        "types": ["ServiceCreditCaseId", "SlaEligibilityRef", "CreditScheduleEdition", "CreditAmount", "ServiceCreditDecision", "CreditIssuanceIntent", "ServiceCreditPolicy", "ServiceCreditRefusal"],
        "trait": "ServiceCreditDecisionAlgebra",
        "operations": [
            ("validate_credit_case", ["ServiceCreditCaseId", "SlaEligibilityRef", "ServiceCreditPolicy"], "Result<ValidatedServiceCreditCase,ServiceCreditRefusal>"),
            ("calculate_credit_decision", ["ValidatedServiceCreditCase", "CreditScheduleEdition", "ServiceCreditPolicy"], "Result<ServiceCreditDecision,ServiceCreditRefusal>"),
            ("plan_credit_issuance", ["ServiceCreditDecision", "CreditIssuanceAuthorityRef"], "Result<CreditIssuanceIntent,ServiceCreditRefusal>"),
        ],
        "errors": ["EligibilityUnbound", "CreditScheduleUnbound", "CreditBasisIncomplete", "CreditCurrencyMismatch", "DecisionAuthorityMissing", "IssuanceAuthorityMissing", "ResourceBudgetExceeded"],
        "laws": ["eligibility credit calculation approval issuance and settlement are distinct", "credit calculation binds one agreement schedule eligible occurrence and money policy", "this pure library emits an issuance intent and never claims the external credit effect"],
    },
    "feature_definition": {
        "types": ["FeatureId", "FeatureDefinitionEdition", "FeatureValueDomain", "FeatureDependencySet", "FeatureDefinitionPolicy", "FeatureDefinitionRefusal"],
        "trait": "FeatureDefinitionAlgebra",
        "operations": [
            ("validate_feature_definition", ["FeatureDefinitionEdition", "FeatureDefinitionPolicy"], "Result<ValidatedFeatureDefinition,FeatureDefinitionRefusal>"),
            ("resolve_feature_dependencies", ["ValidatedFeatureDefinition", "FeatureDefinitionRegistryCut"], "Result<ResolvedFeatureClosure,FeatureDefinitionRefusal>"),
            ("compare_feature_editions", ["FeatureDefinitionEdition", "FeatureDefinitionEdition"], "Result<FeatureDefinitionDiff,FeatureDefinitionRefusal>"),
        ],
        "errors": ["FeatureIdCollision", "ValueDomainInvalid", "DependencyUnresolved", "DependencyCycle", "FeatureEditionConflict", "ResourceBudgetExceeded"],
        "laws": ["feature definition grant entitlement decision and license seat are distinct", "feature identity and value domain are immutable within one edition", "dependency closure binds exact feature editions"],
    },
    "entitlement_decision_policy": {
        "types": ["EntitlementPolicyId", "EntitlementPolicyEdition", "EntitlementRequest", "EntitlementEvidenceCut", "EntitlementDecision", "EntitlementDecisionTrace", "EntitlementRefusal"],
        "trait": "EntitlementDecisionPolicyAlgebra",
        "operations": [
            ("validate_entitlement_policy", ["EntitlementPolicyEdition", "PolicyAuthorityRef"], "Result<ValidatedEntitlementPolicy,EntitlementRefusal>"),
            ("evaluate_entitlement_request", ["ValidatedEntitlementPolicy", "EntitlementRequest", "EntitlementEvidenceCut"], "Result<EntitlementDecision,EntitlementRefusal>"),
            ("explain_entitlement_decision", ["EntitlementDecision", "ExplanationScope"], "Result<EntitlementDecisionTrace,EntitlementRefusal>"),
        ],
        "errors": ["PolicyAuthorityUnbound", "SubjectUnresolved", "FeatureEditionUnbound", "EvidenceCutIncomplete", "CombiningAlgorithmMissing", "DecisionIndeterminate", "ResourceBudgetExceeded"],
        "laws": ["authentication identity policy applicability decision grant and runtime enforcement are distinct", "permit deny not-applicable and indeterminate remain distinct", "provider identity never changes the selected entitlement semantics"],
    },
    "entitlement_grant": {
        "types": ["EntitlementGrantId", "EntitlementGrantEdition", "EntitledSubjectRef", "FeatureEditionRef", "GrantValidity", "GrantAuthorityRef", "EntitlementGrantPolicy", "EntitlementGrantRefusal"],
        "trait": "EntitlementGrantAlgebra",
        "operations": [
            ("validate_entitlement_grant", ["EntitlementGrantEdition", "EntitlementGrantPolicy"], "Result<ValidatedEntitlementGrant,EntitlementGrantRefusal>"),
            ("evaluate_grant_at_time", ["ValidatedEntitlementGrant", "EvaluationInstant", "EntitlementGrantPolicy"], "Result<GrantTemporalStatus,EntitlementGrantRefusal>"),
            ("derive_grant_transition", ["ValidatedEntitlementGrant", "GrantCommand", "EntitlementGrantPolicy"], "Result<EntitlementGrantTransition,EntitlementGrantRefusal>"),
        ],
        "errors": ["GrantAuthorityUnbound", "SubjectUnresolved", "FeatureEditionUnbound", "GrantValidityInvalid", "GrantTransitionInvalid", "RevocationEvidenceMissing", "ResourceBudgetExceeded"],
        "laws": ["grant occurrence policy decision feature definition and enforcement effect have separate identities", "grant validity and recording time remain distinct", "revocation preserves the historical grant and takes effect under an explicit temporal policy"],
    },
    "license_seat": {
        "types": ["LicensePoolId", "LicenseSeatId", "SeatAssignmentEdition", "SeatAssigneeRef", "SeatCapacity", "LicenseSeatPolicy", "LicenseSeatRefusal"],
        "trait": "LicenseSeatAllocationAlgebra",
        "operations": [
            ("validate_license_pool", ["LicensePoolId", "SeatCapacity", "LicenseSeatPolicy"], "Result<ValidatedLicensePool,LicenseSeatRefusal>"),
            ("allocate_license_seat", ["ValidatedLicensePool", "SeatAssigneeRef", "LicenseSeatPolicy"], "Result<SeatAssignmentEdition,LicenseSeatRefusal>"),
            ("release_license_seat", ["SeatAssignmentEdition", "SeatReleaseCommand", "LicenseSeatPolicy"], "Result<SeatAssignmentTransition,LicenseSeatRefusal>"),
        ],
        "errors": ["LicensePoolUnbound", "SeatCapacityExceeded", "AssigneeUnresolved", "DuplicateSeatAssignment", "SeatReleaseInvalid", "ConcurrentAllocationConflict", "ResourceBudgetExceeded"],
        "laws": ["license-seat allocation is a finite-capacity assignment and not an entitlement policy decision", "one active seat cannot be allocated twice under the same pool policy", "release and reassignment preserve assignment history"],
    },
    "subscription_lifecycle": {
        "types": ["SubscriptionId", "SubscriptionRevision", "SubscriptionState", "SubscriptionCommand", "SubscriptionTransition", "SubscriptionPolicy", "SubscriptionRefusal"],
        "trait": "SubscriptionLifecycleAlgebra",
        "operations": [
            ("validate_subscription_command", ["SubscriptionRevision", "SubscriptionCommand", "SubscriptionPolicy"], "Result<ValidatedSubscriptionCommand,SubscriptionRefusal>"),
            ("reduce_subscription_command", ["SubscriptionRevision", "ValidatedSubscriptionCommand"], "Result<SubscriptionTransition,SubscriptionRefusal>"),
            ("compare_subscription_revisions", ["SubscriptionRevision", "SubscriptionRevision"], "Result<SubscriptionDiff,SubscriptionRefusal>"),
        ],
        "errors": ["SubscriptionVersionConflict", "SubscriptionTransitionInvalid", "OfferEditionUnbound", "TerminationAuthorityMissing", "InFlightObligationUnknown", "ResourceBudgetExceeded"],
        "laws": ["subscription offer agreement entitlement provisioning and access are distinct", "only named commands produce legal transitions", "termination preserves obligations and historical editions"],
    },
    "product_order_lifecycle": {
        "types": ["ProductOrderId", "ProductOrderRevision", "ProductOrderState", "ProductOrderCommand", "ProductOrderTransition", "ProductOrderPolicy", "ProductOrderRefusal"],
        "trait": "ProductOrderLifecycleAlgebra",
        "operations": [
            ("validate_product_order_command", ["ProductOrderRevision", "ProductOrderCommand", "ProductOrderPolicy"], "Result<ValidatedProductOrderCommand,ProductOrderRefusal>"),
            ("reduce_product_order_command", ["ProductOrderRevision", "ValidatedProductOrderCommand"], "Result<ProductOrderTransition,ProductOrderRefusal>"),
            ("derive_product_order_compensation", ["ProductOrderRevision", "ProductOrderFailure", "ProductOrderPolicy"], "Result<ProductOrderCompensationPlan,ProductOrderRefusal>"),
        ],
        "errors": ["ProductOrderVersionConflict", "ProductOrderTransitionInvalid", "CatalogOfferUnbound", "CancellationWindowClosed", "CompensationUnknown", "ResourceBudgetExceeded"],
        "laws": ["product order subscription service order and fulfillment effect are distinct", "order acceptance does not prove fulfillment", "cancellation and compensation preserve the original commercial obligation history"],
    },
    "service_order_lifecycle": {
        "types": ["ServiceOrderId", "ServiceOrderRevision", "ServiceOrderState", "ServiceOrderCommand", "ServiceOrderTransition", "ServiceOrderPolicy", "ServiceOrderRefusal"],
        "trait": "ServiceOrderLifecycleAlgebra",
        "operations": [
            ("validate_service_order_command", ["ServiceOrderRevision", "ServiceOrderCommand", "ServiceOrderPolicy"], "Result<ValidatedServiceOrderCommand,ServiceOrderRefusal>"),
            ("reduce_service_order_command", ["ServiceOrderRevision", "ValidatedServiceOrderCommand"], "Result<ServiceOrderTransition,ServiceOrderRefusal>"),
            ("reconcile_service_order_receipt", ["ServiceOrderRevision", "ProviderEffectReceipt", "ServiceOrderPolicy"], "Result<ServiceOrderTransition,ServiceOrderRefusal>"),
        ],
        "errors": ["ServiceOrderVersionConflict", "ServiceOrderTransitionInvalid", "ServiceSpecificationUnbound", "ProviderReceiptInvalid", "EffectCompletionUnknown", "ResourceBudgetExceeded"],
        "laws": ["service order product order service instance and provider effect are distinct", "dispatch is not completion", "unknown provider completion reconciles before retry"],
    },
    "support_case_lifecycle": {
        "types": ["SupportCaseId", "SupportCaseRevision", "SupportCaseState", "SupportCaseCommand", "SupportCaseTransition", "SupportCasePolicy", "SupportCaseRefusal"],
        "trait": "SupportCaseLifecycleAlgebra",
        "operations": [
            ("validate_support_case_command", ["SupportCaseRevision", "SupportCaseCommand", "SupportCasePolicy"], "Result<ValidatedSupportCaseCommand,SupportCaseRefusal>"),
            ("reduce_support_case_command", ["SupportCaseRevision", "ValidatedSupportCaseCommand"], "Result<SupportCaseTransition,SupportCaseRefusal>"),
            ("evaluate_support_case_closure", ["SupportCaseRevision", "SupportClosureEvidenceSet", "SupportCasePolicy"], "Result<SupportClosureEligibility,SupportCaseRefusal>"),
        ],
        "errors": ["SupportCaseVersionConflict", "SupportCaseTransitionInvalid", "RequesterUnresolved", "AssignmentAuthorityMissing", "ClosureEvidenceMissing", "ResidualCommitmentOpen", "ResourceBudgetExceeded"],
        "laws": ["support request issue incident problem and service order are distinct", "case closure requires the selected evidence posture", "reopen appends a revision and preserves the prior closure basis"],
    },
    "incident_lifecycle": {
        "types": ["IncidentId", "IncidentRevision", "IncidentState", "IncidentCommand", "IncidentTransition", "ImpactAssessment", "IncidentPolicy", "IncidentRefusal"],
        "trait": "IncidentLifecycleAlgebra",
        "operations": [
            ("validate_incident_command", ["IncidentRevision", "IncidentCommand", "IncidentPolicy"], "Result<ValidatedIncidentCommand,IncidentRefusal>"),
            ("reduce_incident_command", ["IncidentRevision", "ValidatedIncidentCommand"], "Result<IncidentTransition,IncidentRefusal>"),
            ("evaluate_incident_closure", ["IncidentRevision", "RecoveryEvidenceSet", "IncidentPolicy"], "Result<IncidentClosureEligibility,IncidentRefusal>"),
        ],
        "errors": ["IncidentVersionConflict", "IncidentTransitionInvalid", "ImpactUnknown", "CommanderAuthorityMissing", "RecoveryEvidenceMissing", "ResidualRiskUnaccepted", "ResourceBudgetExceeded"],
        "laws": ["alert incident impact mitigation restoration root cause and problem record are distinct", "restoration does not prove root cause or permanent correction", "closure preserves the complete timeline evidence and residual risk"],
    },
}


def build_libraries() -> list[dict]:
    rows = []
    for slug, kind, owners, boundary, provider_source in LIBRARY_SPECS:
        owner_refs = [cid(owner) for owner in owners]
        operation_refs = [f"operation.platform-commercial-support.{owner}.{'record' if kind in {'effect_port', 'provider_adapter'} else 'inspect'}" for owner in owners]
        row = {
            "record_kind": "library_boundary",
            "library_id": f"library.platform-commercial-support.{slug}",
            "edition": EDITION,
            "status": STATUS,
            "library_kind": kind,
            "semantic_owner_refs": ([cid(PCS_UNIQUE_LIBRARY_OWNER[slug])] if slug in PCS_UNIQUE_LIBRARY_OWNER else owner_refs) if kind in {"semantic_pure", "policy_pure", "algorithm_pure"} else [],
            "contributes_to_context_refs": owner_refs,
            "effect_boundary": boundary,
            "public_contracts": [f"contract.platform-commercial-support.{owner}" for owner in owners],
            "operation_refs": operation_refs,
            "error_contracts": ["typed_refusal", "unknown_outcome_requires_reconciliation", "provider_error_is_not_domain_state"],
            "tenant_contract": "TenantId is mandatory at every effect port and checked again by adapters before provider calls.",
            "laws": ["no hidden I/O in pure libraries", "effect ports return receipts", "provider DTOs stop at the anti-corruption boundary"],
            "removal_seams": ["stable provider-neutral port", "conformance fixtures", "migration/export path"],
            "forbidden_responsibilities": ["owning legal interpretation", "inventing authorization", "collapsing provider state into domain state", "cross-tenant caching without scope"],
            "provider_source_ref": sid(provider_source) if provider_source else None,
            "candidate_qualification": "interface_candidate" if kind != "provider_adapter" else "adapter_candidate_unproven",
        }
        exact_api = EXACT_SPLIT_APIS.get(slug)
        if exact_api:
            row.update({
                "public_types": exact_api["types"],
                "public_traits": [exact_api["trait"]],
                "input_types": sorted({value for _, inputs, _ in exact_api["operations"] for value in inputs}),
                "output_types": sorted({output for _, _, output in exact_api["operations"]}),
                "operations": [{
                    "operation_ref": f"operation.platform-commercial-support.{slug}.{name}",
                    "name": name,
                    "input_types": inputs,
                    "output_type": output,
                    "purity": "pure",
                    "effect_intent_type": None,
                    "receipt_type": None,
                    "refusal_types": exact_api["errors"],
                } for name, inputs, output in exact_api["operations"]],
                "error_contracts": exact_api["errors"],
                "laws": row["laws"] + exact_api["laws"],
                "configuration_contracts": [name for name in exact_api["types"] if name.endswith("Policy")],
                "oracles": ["constructor-and-invariant-properties", "edition-and-identity-negative-twins", "refusal-totality-fixtures", "cross-implementation-differential"],
            })
        if slug == "focus-normalization":
            row.update({
                "name": "FOCUS cost normalization contract",
                "responsibilities": [
                    "Map one immutable provider cost-and-usage occurrence to one selected FOCUS edition under an explicit normalization profile.",
                    "Retain source identity, exact source and FOCUS editions, every transformation decision, validation finding and unmapped or lossy residual.",
                    "Return a total typed outcome: normalized, partially normalized with authorized residuals, unmapped, or refused.",
                ],
                "explicit_exclusions": [
                    "allocating shared cost", "rating usage", "issuing charges or invoices",
                    "posting a general ledger", "inventing missing provider facts", "deciding business value",
                ],
                "public_types": [
                    "FocusEdition", "ProviderCostOccurrence", "CostOccurrenceIdentity",
                    "FocusNormalizationProfile", "FocusCostAndUsageRecord", "ColumnMappingDecision",
                    "NormalizationResidual", "NormalizationFinding", "NormalizationTrace",
                    "FocusNormalizationOutcome", "FocusNormalizationRefusal",
                ],
                "public_traits": ["CostSourceAdapter", "FocusNormalizer", "FocusRecordValidator", "NormalizationTraceEncoder"],
                "input_types": ["ProviderCostOccurrence", "FocusNormalizationProfile", "FocusEdition"],
                "output_types": ["Result<FocusNormalizationOutcome,FocusNormalizationRefusal>"],
                "operation_refs": [
                    "operation.platform-commercial-support.cost-normalization.parse-source-occurrence",
                    "operation.platform-commercial-support.cost-normalization.normalize-record",
                    "operation.platform-commercial-support.cost-normalization.validate-focus-record",
                    "operation.platform-commercial-support.cost-normalization.explain-residuals",
                    "operation.platform-commercial-support.cost-normalization.project-loss-report",
                ],
                "evidence_refs": [sid("focus12"), sid("focus11"), sid("finops-framework")],
                "decision_refs": ["decision.platform-commercial-support.cost-normalization.policy"],
                "configuration_contracts": [
                    "FocusNormalizationProfile", "UnknownFieldPolicy", "MissingMandatoryColumnPolicy",
                    "CurrencyAndUnitPolicy", "ServicePeriodPolicy", "TagProjectionPolicy", "ResidualAcceptancePolicy",
                ],
                "error_contracts": [
                    "UnsupportedFocusEdition", "SourceOccurrenceIdentityMissing", "SourceEditionUnsupported",
                    "MandatorySemanticValueMissing", "CurrencyOrUnitUnknown", "TimeIntervalInvalid",
                    "MappingAmbiguous", "SemanticLossUnauthorized", "NormalizedRecordInvalid", "ResourceBudgetExceeded",
                ],
                "laws": [
                    "normalization never invents a source fact or silently chooses a semantic default",
                    "one outcome binds one source occurrence identity, source schema edition, normalization profile edition and FOCUS edition",
                    "every source field is mapped losslessly, retained as a typed residual, or causes a typed refusal",
                    "billed, effective, list and contracted cost identities never alias",
                    "normalization is not attribution, allocation, charge, invoice, ledger posting or business-value judgment",
                    "canonical output is deterministic for identical frozen inputs and decision editions",
                    "round-trip to a provider record is claimed only under an explicit reversible mapping profile",
                    "a partially normalized record never acquires the status of a conformant complete FOCUS record",
                ],
                "oracles": [
                    "focus-schema-and-normative-rule-fixtures", "source-occurrence-identity-property",
                    "no-invented-fact-property", "residual-conservation-property", "cost-identity-negative-twins",
                    "edition-migration-fixtures", "cross-implementation-differential",
                ],
                "resource_contracts": [
                    "finite input bytes and columns", "finite mapping rules", "finite validation findings",
                    "bounded residual bytes", "deadline or resource-budget refusal",
                ],
                "compatibility": [
                    "FOCUS edition, provider schema edition and normalization-profile edition are independently versioned",
                    "adding a source mapping cannot change an existing mapped value without an explicit profile edition",
                    "a FOCUS edition migration emits a semantic diff and invalidates affected conformance evidence",
                ],
                "removal_seams": [
                    "provider-neutral CostSourceAdapter", "pure FocusNormalizer", "editioned profile and trace",
                    "shared conformance and differential corpus",
                ],
            })
        rows.append(row)
    return rows


def build_requirements_offers_bindings(libraries: list[dict]) -> list[dict]:
    rows = []
    for library in libraries:
        slug = library["library_id"].rsplit(".", 1)[1]
        requirement_id = f"requirement.platform-commercial-support.{slug}"
        offer_id = f"offer.platform-commercial-support.{slug}"
        binding_id = f"binding.platform-commercial-support.{slug}"
        rows.extend([
            {
                "record_kind": "capability_requirement", "requirement_id": requirement_id, "edition": EDITION,
                "status": STATUS, "requester_context_refs": library["contributes_to_context_refs"],
                "required_semantics": library["laws"], "required_effect_boundary": library["effect_boundary"],
                "required_tenant_property": "no read, effect, metric, cache, or receipt can escape TenantId scope",
                "required_evidence": ["schema conformance", "lifecycle totality", "tenant isolation tests", "fault and replay tests"],
            },
            {
                "record_kind": "capability_offer", "offer_id": offer_id, "edition": EDITION,
                "status": "candidate_offer", "library_ref": library["library_id"],
                "offered_semantics": library["laws"], "effect_boundary": library["effect_boundary"],
                "qualification_receipts": [], "limitations": ["No two-implementation conformance yet", "Provider documentation is not runtime proof"],
            },
            {
                "record_kind": "capability_binding", "binding_id": binding_id, "edition": EDITION,
                "status": "candidate_not_proven", "requirement_ref": requirement_id, "offer_refs": [offer_id],
                "satisfaction": "structural_candidate", "proof_obligations": ["two independent implementations", "tenant escape tests", "replay and race tests", "version migration fixture"],
                "residual_gap_refs": ["gap.platform-commercial-support.two-implementation-conformance"],
            },
        ])
    return rows


def build_compiler_mappings(libraries: list[dict]) -> list[dict]:
    rows = []
    stages = ["identity_ir", "commercial_ir", "usage_ir", "service_ir", "effect_ir", "target_binding_ir"]
    for index, library in enumerate(libraries):
        slug = library["library_id"].rsplit(".", 1)[1]
        rows.append({
            "record_kind": "compiler_mapping",
            "mapping_id": f"compiler-mapping.platform-commercial-support.{slug}",
            "edition": EDITION,
            "status": STATUS,
            "from_requirement_ref": f"requirement.platform-commercial-support.{slug}",
            "through_library_ref": library["library_id"],
            "compiler_stage": stages[index % len(stages)],
            "emits": ["exact edition binding", "authority and tenant guard", "effect intent", "typed refusal table", "receipt schema"],
            "must_prove": ["semantic owner is unique", "required scopes are explicit", "provider capability is qualified", "no forbidden default was taken"],
            "invalidated_by": ["contract or policy edition change", "provider capability drift", "schema incompatibility", "evidence expiry"],
            "release_gate": "no blocking gap and all proof obligations carry receipts",
        })
    return rows


PRODUCT_TRUTH_SPECS = [
    ("tenant_identity", "tenant-registry", "TenantId in every compiled deployment and receipt", "billing account or provider account"),
    ("customer_identity", "commercial-customer", "CustomerId and explicit party relations", "tenant or payer"),
    ("billing_responsibility", "billing-account", "BillingAccountId, payer reference, currency, and terms", "legal entity or tenant"),
    ("legal_counterparty", "legal-entity-binding", "verified external LegalEntityRef", "platform-created legal conclusion"),
    ("feature_key", "feature-definition", "stable FeatureKey and edition", "runtime feature-flag provider key"),
    ("commercial_access", "entitlement-policy", "entitlement evaluation requirement", "authorization rule"),
    ("technical_limit", "quota-policy", "quota requirement and rejection code", "entitlement or physical capacity"),
    ("spend_authority", "budget-control", "budget/precharge guard", "quota or prepaid product units"),
    ("catalog_offer", "product-catalog", "offer and version reference", "customer-specific contract"),
    ("contract_terms", "commercial-contract", "effective machine-enforceable term projection", "plan template or full legal interpretation"),
    ("subscription_configuration", "subscription", "concrete phased items, prices, and entitlements", "catalog plan"),
    ("metered_occurrence", "usage-event", "immutable usage event plus acceptance receipt", "aggregate or charge"),
    ("rated_consumption", "rating", "RatedUsageId with meter, price, contract, and aggregate lineage", "invoice line"),
    ("external_receivable", "invoice", "finalized invoice and lines", "charge ledger or payment"),
    ("service_instance", "provisioning", "activation receipt and provider occurrence mapping", "product order"),
    ("customer_request", "support-case", "support case and correspondence", "operational incident"),
    ("service_disruption", "incident", "incident impact and restoration facts", "alert, case, problem, or maintenance"),
    ("reliability_target", "service-objective", "SLI/SLO definition and evaluation", "contractual commitment"),
    ("contractual_service_commitment", "service-agreement", "SLA projection with measurement and claim rules", "SLO or automatic credit"),
    ("credit_entitlement", "service-credit", "approved service-credit claim", "SLO breach or prepaid balance"),
    ("portable_export", "portability-export", "verified manifest and transfer receipt", "complete supplier exit"),
    ("exit_completion", "supplier-exit", "accepted transition, decommission state, and residual schedule", "data export or subscription cancellation"),
]


def build_product_truth_mappings() -> list[dict]:
    rows = []
    for truth, owner, projection, confusion in PRODUCT_TRUTH_SPECS:
        rows.append({
            "record_kind": "product_truth_mapping",
            "mapping_id": f"product-truth.platform-commercial-support.{truth.replace('_', '-')}",
            "edition": EDITION,
            "status": "candidate_mapping",
            "product_truth": truth,
            "semantic_owner_ref": cid(owner),
            "compiled_projection": projection,
            "must_not_be_derived_from": confusion,
            "release_evidence": ["owner edition", "tenant scope", "authority receipt", "provider binding receipt where effectful"],
            "refusal": "product_truth_unresolved_or_ambiguous",
        })
    return rows


CROSS_DOMAIN_SPECS = [
    ("security-privacy", ["tenant-isolation", "delegated-administration", "entitlement-policy", "customer-evidence", "residual-obligation"], "context.security-privacy-trust.tenant-boundary", "Security/privacy prohibition dominates commercial allowance; this universe supplies product scope but never security authorization."),
    ("runtime-economics-resources", ["quota-policy", "budget-control", "usage-event", "cost-allocation", "provisioning"], "context.runtime-resource.quota-budget", "Commercial entitlement, budget, quota, demand, capacity, allocation, usage, cost, and invoice are separately bound."),
    ("provider-targets", ["tax-determination", "payment-collection", "provisioning", "status-communication", "portability-export"], "context.provider-target.target-occurrence", "Provider offers and observations satisfy explicit ports; provider objects never own platform semantics."),
    ("product-boundaries", ["product-catalog", "service-catalog", "commercial-contract", "subscription", "supplier-exit"], "context.product-boundary.product-truth", "A product includes only truth mapped to unique semantic owners and an applicable lifecycle/exit plan."),
    ("evidence-lineage", ["usage-event", "rating", "invoice", "incident", "customer-evidence", "supplier-exit"], "context.lineage-evidence.evidence-bundle", "Every material claim keeps source, derivation, event/recorded time, issuer, tenant, and disclosure scope."),
    ("compiler-release", [slug for slug, *_ in CONTEXT_SPECS], "context.compiler.release", "A release is refused when any imported context, policy, contract, provider capability, or migration/exit proof is unresolved."),
]


def build_cross_domain_mappings() -> list[dict]:
    return [
        {
            "record_kind": "cross_domain_mapping",
            "mapping_id": f"cross-domain.platform-commercial-support.{slug}",
            "edition": EDITION,
            "status": "requires_adjudication",
            "local_context_refs": [cid(ref) for ref in local_refs],
            "external_context_ref": external,
            "mapping_law": law,
            "ownership": "local universe owns platform-commercial-support semantics; external owner supplies its own decision/evidence contract",
            "release_gate": "both owners accept the mapping edition and no circular authority is introduced",
        }
        for slug, local_refs, external, law in CROSS_DOMAIN_SPECS
    ]


INNOVATION_SPECS = [
    ("it4it3-digital-product", 2022, "IT4IT 3 reframed service management around end-to-end digital products and value streams.", "it4it3", ["product-catalog", "service-catalog", "supplier-exit"]),
    ("iso20000-5-plan", 2022, "ISO/IEC TS 20000-5 added contemporary implementation guidance for a service management system.", "iso20000-5", ["onboarding", "maintenance-change", "problem"]),
    ("cloudevents-102", 2022, "CloudEvents 1.0.2 stabilized a portable event envelope used by metering and service operations.", "cloudevents", ["usage-event", "status-communication"]),
    ("openmeter-event-meter", 2023, "OpenMeter demonstrated open-source CloudEvents-first usage ingestion with separately defined meters.", "openmeter-events", ["usage-event", "meter-definition"]),
    ("focus-10", 2023, "FOCUS introduced an open normalized cloud cost-and-usage schema across providers.", "focus11", ["cost-allocation", "chargeback-showback"]),
    ("eu-data-act-switching", 2023, "The EU Data Act made switching and interoperability a first-class cloud-product lifecycle concern.", "eu-data-act", ["supplier-exit", "portability-export"]),
    ("openfeature-standard", 2023, "OpenFeature reached a broadly adopted vendor-neutral feature-flag evaluation boundary.", "openfeature", ["feature-definition", "entitlement-policy"]),
    ("opencost-specification", 2023, "OpenCost standardized Kubernetes workload and shared-cost allocation fields.", "opencost", ["cost-allocation", "chargeback-showback"]),
    ("openslo-as-code", 2024, "OpenSLO made SLI, objective, window, and alert policy portable as code.", "openslo", ["service-objective"]),
    ("cloudevents-graduation", 2024, "CloudEvents became a CNCF graduated project, strengthening its implementation maturity signal.", "cloudevents", ["usage-event", "status-communication"]),
    ("focus-11-allocation", 2024, "FOCUS 1.1 expanded commitment-discount and cost-allocation semantics.", "focus11", ["cost-allocation", "charge-ledger"]),
    ("stripe-billing-meters", 2024, "Stripe Billing meters replaced ad-hoc usage-record coupling with explicit meter events and summaries.", "stripe-meter-events", ["meter-definition", "usage-event", "rating"]),
    ("stripe-entitlements", 2024, "Stripe Entitlements exposed active feature grants derived from subscription state.", "stripe-entitlements", ["feature-definition", "entitlement-policy"]),
    ("asyncapi3-operations", 2024, "AsyncAPI 3.0 separated channels, operations, and messages for event-driven API contracts.", "asyncapi3", ["status-communication", "usage-event"]),
    ("otel-semantics-stability", 2024, "OpenTelemetry stabilized additional signal semantic conventions and versioning practices.", "otel-semconv", ["customer-evidence", "incident"]),
    ("cncf-operational-excellence", 2024, "CNCF published a cloud-native operational-excellence maturity model spanning reliability and lifecycle practice.", "cncf-tag-app-delivery", ["onboarding", "adoption-success", "incident"]),
    ("focus-12-contract-fields", 2025, "FOCUS 1.2 added contracted-price and allocation transparency useful for unit economics and reconciliation.", "focus12", ["price-book", "cost-allocation", "chargeback-showback"]),
    ("tmforum-gen5-catalog", 2025, "TM Forum Open API evolution continued to align catalog, order, inventory, usage, bill, and assurance resource APIs.", "tmf620", ["product-catalog", "product-order", "invoice"]),
    ("peppol-pint-adoption", 2025, "Peppol PINT matured an international, jurisdiction-extensible invoice model.", "peppol-pint", ["invoice", "tax-determination"]),
    ("openapi-311", 2024, "OpenAPI 3.1.1 clarified portable HTTP API description and JSON Schema alignment.", "openapi31", ["service-catalog", "portability-export"]),
    ("openmeter-subscription-concretization", 2025, "OpenMeter subscriptions explicitly concretized plan templates into phased prices and entitlements.", "openmeter-subscriptions", ["plan-version", "subscription", "entitlement-grant"]),
    ("peppol-2026-billing", 2026, "Peppol's 2026 Billing 3 release maintained executable EN 16931 invoice and credit-note validation rules.", "peppol-billing", ["invoice", "refund-credit-note"]),
    ("openmeter-subject-customer", 2026, "OpenMeter documented subject-to-customer attribution as a first-class distinction in usage billing.", "openmeter-subjects", ["usage-attribution", "commercial-customer"]),
    ("focus-next-adjacent-data", 2026, "FOCUS evolution expanded from normalized billing toward adjacent contract and allocation transparency.", "focus12", ["commercial-contract", "cost-allocation"]),
]


def build_innovations() -> list[dict]:
    return [
        {
            "record_kind": "innovation",
            "innovation_id": f"innovation.platform-commercial-support.{slug}",
            "edition": EDITION,
            "status": STATUS,
            "first_material_year": year,
            "non_llm": True,
            "core_change": change,
            "context_refs": [cid(ref) for ref in contexts],
            "compiler_implications": ["version the new vocabulary", "qualify adapter capabilities", "invalidate affected bindings on drift", "retain migration path"],
            "maturity": "standard_or_official_implementation_evidence",
            "source_refs": [sid(source_slug)],
            "caveats": ["Material year is an architectural adoption marker, not a claim of invention date.", "Provider behavior still requires target-specific conformance evidence."],
        }
        for slug, year, change, source_slug, contexts in INNOVATION_SPECS
    ]


GAP_SPECS = [
    ("two-implementation-conformance", "all library and adapter candidates", "qualification", True, "Two independent implementations pass shared semantic, replay, race, tenant-isolation, and migration fixtures."),
    ("context-ownership-adjudication", "all bounded contexts", "ownership", True, "Cross-universe review assigns one owner or explicitly splits/merges every overlap."),
    ("legal-contract-projection", "commercial contract", "authority", True, "Qualified legal/product owners define jurisdiction-specific projection and change control; no compiler interpretation of free text remains."),
    ("tax-provider-qualification", "tax determination", "provider", True, "Jurisdiction, nexus, product-tax-code, rounding, evidence, correction, and outage behavior are tested for selected providers."),
    ("payment-provider-qualification", "payment collection", "provider", True, "Idempotency, asynchronous outcome, dispute, refund, and reconciliation suites pass for selected payment providers."),
    ("invoice-jurisdiction-profiles", "invoice", "schema", True, "Required Peppol/PINT/UBL/CII or local profiles and validation artifacts are selected per deployment jurisdiction."),
    ("meter-correction-algebra", "usage aggregation", "semantics", True, "Late, duplicate, retracted, corrected, and disputed usage laws are model-checked across cycle close races."),
    ("tiered-rating-oracle", "rating", "oracle", True, "Exact fixtures cover tiers, packages, minimums, maximums, proration, currency, rounding, credits, and amendments."),
    ("tenant-isolation-proof", "tenant isolation", "assurance", True, "Storage, cache, event, support, telemetry, export, and provider-boundary isolation tests pass under adversarial identifiers."),
    ("sla-exclusion-adjudication", "service agreement", "semantics", True, "Measurement source, missing-data, exclusion, maintenance, force-majeure projection, clock, and dispute rules are explicit."),
    ("service-credit-accounting", "service credit", "integration", True, "Credit eligibility, approval, tax, invoice, ledger, expiry, and customer evidence reconcile end to end."),
    ("support-incident-correlation", "support and incident", "identity", False, "Many-to-many correlation and disclosure rules pass fixtures without lifecycle aliasing."),
    ("maintenance-impact-law", "maintenance and incident", "semantics", True, "Planned window, actual change, observed impact, SLA exclusions, and public status are independently timestamped and reconciled."),
    ("exit-completeness", "supplier exit", "assurance", True, "Two vertical exit exercises verify artifacts, semantics, dependencies, credentials, cutover, rollback, decommission, destruction, and residual obligations."),
    ("export-semantic-fidelity", "portability export", "portability", True, "Export includes machine-readable schemas, identifiers, relationships, history, checksums, provenance, and loss declarations with a successful independent import."),
    ("residual-obligation-authority", "residual obligations", "authority", True, "Qualified owners enumerate surviving obligations, discharge evidence, holds, deadlines, and conflicts for each target jurisdiction."),
    ("commercial-runtime-race", "entitlement quota budget and runtime", "concurrency", True, "Revocation, quota update, precharge, admission, effect, cancellation, and refund races have model-checked outcome precedence."),
    ("product-truth-110-crosswalk", "product truth mappings", "coverage", True, "All repository product-truth facets are mapped, marked not applicable with evidence, or recorded as blocking gaps."),
    ("provider-drift-detection", "all provider adapters", "operations", True, "Schema/version/capability probes invalidate compiler offers before incompatible effects are released."),
    ("independent-primary-review", "source and evidence registry", "research", False, "An independent reviewer verifies URLs, scoped claims, dates, authority, and omitted standards/products."),
]


def build_gaps() -> list[dict]:
    return [
        {
            "record_kind": "gap",
            "gap_id": f"gap.platform-commercial-support.{slug}",
            "edition": EDITION,
            "status": "open",
            "subject": subject,
            "gap_kind": kind,
            "blocking": blocking,
            "resolution_condition": resolution,
            "prohibited_fallbacks": ["implicit latest edition", "provider default presented as semantic truth", "cross-tenant best effort", "manual spreadsheet asserted as proof"],
        }
        for slug, subject, kind, blocking, resolution in GAP_SPECS
    ]


def build_evidence(sources: list[dict]) -> list[dict]:
    return [
        {
            "record_kind": "evidence_claim",
            "evidence_id": source["source_id"].replace("source.", "evidence.", 1),
            "edition": EDITION,
            "status": STATUS,
            "source_ref": source["source_id"],
            "claim": source["claim_supported"],
            "authority_scope": source["source_kind"],
            "supports": [source["evidence_family"]],
            "does_not_prove": ["candidate bounded-context ownership", "complete enterprise coverage", "legal or tax applicability", "runtime conformance"],
            "verification": "official publisher location recorded; independent link and version review remains open",
        }
        for source in sources
    ]


def build_examples() -> list[dict]:
    return [
        {
            "record_kind": "vertical_example",
            "example_id": "example.platform-commercial-support.regulated-financial-risk-analytics",
            "edition": EDITION,
            "status": "illustrative_candidate",
            "vertical": "regulated financial services risk analytics",
            "identity_model": {"tenant": "tenant.bank-a", "organization": "org.risk", "workspace": "workspace.credit-risk", "commercial_customer": "customer.bank-group", "billing_account": "billing.bank-a-india", "legal_entity_ref": "external-verified-entity.bank-a-india"},
            "commercial_model": {"catalog_offer": "enterprise-risk-analytics@4", "contract_projection": "contract-2026-amendment-2", "subscription": "subscription.bank-a-risk", "entitlements": ["feature.scenario-lab", "feature.audit-export"], "quota": "500 concurrent jobs", "budget": "monthly internal approval budget", "prepaid_balance": None},
            "usage_to_invoice": ["immutable compute-job usage event", "tenant/customer/billing attribution", "monthly aggregate", "contract-fixed rate card", "rated usage", "posted charge", "tax determination", "invoice line"],
            "service_model": {"slo": "99.95% workspace query availability", "sla": "contractual monthly availability with explicit exclusions", "service_credit": "claim evaluated only after verified SLA breach", "support": "P1 case may link to but never become incident"},
            "exit_model": ["freeze new orders", "export datasets plus schemas, policies, lineage, and evidence", "independent import verification", "credential and integration rotation", "service cutover", "decommission", "residual retention/deletion schedule"],
            "compiler_trace_refs": [cid("tenant-isolation"), cid("commercial-contract"), cid("entitlement-policy"), cid("quota-policy"), cid("budget-control"), cid("incident"), cid("service-agreement"), cid("supplier-exit")],
            "refusal_example": "An entitled query is still refused when security purpose is invalid, budget reservation fails, quota is exhausted, or runtime capacity is infeasible; the emitted code is distinct in each case.",
        },
        {
            "record_kind": "vertical_example",
            "example_id": "example.platform-commercial-support.multi-brand-retail-analytics",
            "edition": EDITION,
            "status": "illustrative_candidate",
            "vertical": "multi-brand retail analytics platform",
            "identity_model": {"tenant": "tenant.retail-group", "organization": "org.brand-north", "workspace": "workspace.demand-planning", "commercial_customer": "customer.retail-group", "billing_account": "billing.group-shared-services", "legal_entity_ref": "external-verified-entity.group-services"},
            "commercial_model": {"catalog_offer": "retail-analytics-growth@7", "contract_projection": "contract-group-2026", "subscription": "subscription.brand-north", "entitlements": ["feature.forecast", "feature.store-export"], "quota": "per-workspace request and storage limits", "budget": "brand cost-center threshold", "prepaid_balance": "promotional onboarding units with expiry"},
            "usage_to_invoice": ["store and workspace tagged usage event", "subject-to-customer mapping", "daily aggregate", "tiered rating", "shared-cost allocation", "showback to brands", "single external invoice to billing account"],
            "service_model": {"slo": "internal freshness and availability objectives", "sla": "group contract commitment", "service_credit": "approved credit applied to external invoice, not internal showback", "support": "brand cases correlated many-to-one with platform incident"},
            "exit_model": ["brand workspace export without terminating group tenant", "dependency inventory", "portable manifests and checksums", "revoke brand-specific integrations", "workspace decommission", "preserve group invoice and support evidence"],
            "compiler_trace_refs": [cid("tenant-hierarchy"), cid("workspace-registry"), cid("usage-attribution"), cid("cost-allocation"), cid("chargeback-showback"), cid("support-case"), cid("portability-export")],
            "refusal_example": "A parent-tenant administrator cannot read brand raw data merely because group billing aggregates cost; billing aggregation authority is not data-access authority.",
        },
    ]


def object_schema(title: str, required: list[str], properties: dict, *, kinds: list[str] | None = None) -> dict:
    kind_schema: dict = {"type": "string"}
    if kinds:
        kind_schema = {"enum": kinds}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "type": "object",
        "required": ["record_kind", "edition", "status", *required],
        "properties": {
            "record_kind": kind_schema,
            "edition": {"type": "string"},
            "status": {"type": "string"},
            **properties,
        },
    }


def build_schemas() -> dict[str, dict]:
    nonempty_strings = {"type": "array", "minItems": 1, "items": {"type": "string"}}
    return {
        "context.schema.json": object_schema(
            "Platform commercial support bounded-context candidate",
            ["context_id", "name", "sovereign_question", "owns", "explicitly_excludes", "authority_invariants", "tenant_isolation_invariants", "source_refs"],
            {"context_id": {"type": "string", "pattern": "^context\\.platform-commercial-support\\."}, "name": {"type": "string", "minLength": 1}, "sovereign_question": {"type": "string", "minLength": 1}, "owns": nonempty_strings, "explicitly_excludes": nonempty_strings, "authority_invariants": nonempty_strings, "tenant_isolation_invariants": nonempty_strings, "source_refs": nonempty_strings},
            kinds=["bounded_context"],
        ),
        "capability.schema.json": object_schema(
            "Platform capability candidate", ["capability_id", "owner_context_ref", "purpose", "preconditions", "postconditions", "refusals", "source_refs"],
            {"capability_id": {"type": "string"}, "owner_context_ref": {"type": "string"}, "purpose": {"type": "string"}, "preconditions": nonempty_strings, "postconditions": nonempty_strings, "refusals": nonempty_strings, "source_refs": nonempty_strings}, kinds=["capability"]),
        "operation.schema.json": object_schema(
            "Platform operation candidate", ["operation_id", "owner_context_ref", "capability_ref", "mode", "input_contract_ref", "refusal_precedence", "source_refs"],
            {"operation_id": {"type": "string"}, "owner_context_ref": {"type": "string"}, "capability_ref": {"type": "string"}, "mode": {"enum": ["effectful_command", "pure_query"]}, "input_contract_ref": {"type": "string"}, "refusal_precedence": nonempty_strings, "source_refs": nonempty_strings}, kinds=["operation"]),
        "decision.schema.json": object_schema(
            "Compiler-visible platform decision", ["decision_id", "owner_context_ref", "question", "allowed_values", "binding_phase", "authority_ref", "default_law", "constraints", "invalidation", "source_refs"],
            {"decision_id": {"type": "string"}, "owner_context_ref": {"type": "string"}, "question": {"type": "string"}, "allowed_values": nonempty_strings, "binding_phase": {"type": "string"}, "authority_ref": {"type": "string"}, "default_law": {"const": "forbidden"}, "constraints": nonempty_strings, "invalidation": nonempty_strings, "source_refs": nonempty_strings}, kinds=["decision"]),
        "state-machine.schema.json": object_schema(
            "Total platform lifecycle", ["state_machine_id", "owner_context_ref", "states", "initial_state", "terminal_states", "commands", "transitions", "refusal_matrix", "totality_law", "source_refs"],
            {"state_machine_id": {"type": "string"}, "owner_context_ref": {"type": "string"}, "states": nonempty_strings, "initial_state": {"type": "string"}, "terminal_states": nonempty_strings, "commands": nonempty_strings, "transitions": {"type": "array", "minItems": 1, "items": {"type": "object"}}, "refusal_matrix": {"type": "array", "minItems": 1, "items": {"type": "object"}}, "totality_law": {"type": "string"}, "source_refs": nonempty_strings}, kinds=["state_machine"]),
        "contract.schema.json": object_schema(
            "Platform semantic carrier contract", ["contract_id", "owner_context_ref", "fields", "required_fields", "identity_law", "time_law", "authority_law", "tenant_law", "source_refs"],
            {"contract_id": {"type": "string"}, "owner_context_ref": {"type": "string"}, "fields": nonempty_strings, "required_fields": nonempty_strings, "identity_law": {"type": "string"}, "time_law": {"type": "string"}, "authority_law": {"type": "string"}, "tenant_law": {"type": "string"}, "source_refs": nonempty_strings}, kinds=["contract"]),
        "source.schema.json": object_schema(
            "Scoped official source", ["source_id", "title", "publisher", "url", "source_kind", "primary_or_official", "claim_supported", "scope_limitation", "accessed_at"],
            {"source_id": {"type": "string"}, "title": {"type": "string"}, "publisher": {"type": "string"}, "url": {"type": "string", "pattern": "^https://"}, "source_kind": {"type": "string"}, "primary_or_official": {"const": True}, "claim_supported": {"type": "string"}, "scope_limitation": {"type": "string"}, "accessed_at": {"type": "string"}}, kinds=["source"]),
        "evidence.schema.json": object_schema(
            "Scoped evidence claim", ["evidence_id", "source_ref", "claim", "supports", "does_not_prove", "verification"],
            {"evidence_id": {"type": "string"}, "source_ref": {"type": "string"}, "claim": {"type": "string"}, "supports": nonempty_strings, "does_not_prove": nonempty_strings, "verification": {"type": "string"}}, kinds=["evidence_claim"]),
        "invariant-refusal.schema.json": object_schema(
            "Invariant, refusal, or failure precedence rule", ["rule_id", "law", "enforcement_phases", "violation_result", "source_refs"],
            {"rule_id": {"type": "string"}, "law": {"type": "string"}, "enforcement_phases": nonempty_strings, "violation_result": {"type": "string"}, "source_refs": nonempty_strings}, kinds=["authority_invariant", "tenant_isolation_invariant", "semantic_invariant", "boundary_invariant", "refusal", "failure_precedence"]),
        "library-boundary.schema.json": object_schema(
            "Library, effect-port, or provider-adapter boundary", ["library_id", "library_kind", "contributes_to_context_refs", "effect_boundary", "public_contracts", "operation_refs", "laws", "removal_seams", "forbidden_responsibilities"],
            {"library_id": {"type": "string"}, "library_kind": {"enum": ["semantic_pure", "policy_pure", "algorithm_pure", "effect_port", "provider_adapter"]}, "contributes_to_context_refs": nonempty_strings, "effect_boundary": {"type": "string"}, "public_contracts": nonempty_strings, "operation_refs": nonempty_strings, "laws": nonempty_strings, "removal_seams": nonempty_strings, "forbidden_responsibilities": nonempty_strings}, kinds=["library_boundary"]),
        "library-replacement.schema.json": object_schema(
            "Retired composite library replacement", ["replacement_id", "retired_library_ref", "covered_context_refs", "replacement_library_refs", "rationale", "closure_law"],
            {"replacement_id": {"type": "string"}, "retired_library_ref": {"type": "string"}, "covered_context_refs": nonempty_strings, "replacement_library_refs": nonempty_strings, "rationale": {"type": "string"}, "closure_law": {"type": "string"}}, kinds=["library_replacement"]),
        "requirement-offer-binding.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Requirement, offer, or candidate binding", "type": "object",
            "required": ["record_kind", "edition", "status"],
            "properties": {"record_kind": {"enum": ["capability_requirement", "capability_offer", "capability_binding"]}, "edition": {"type": "string"}, "status": {"type": "string"}},
            "oneOf": [
                {"properties": {"record_kind": {"const": "capability_requirement"}}, "required": ["requirement_id", "requester_context_refs", "required_semantics", "required_evidence"]},
                {"properties": {"record_kind": {"const": "capability_offer"}}, "required": ["offer_id", "library_ref", "offered_semantics", "limitations"]},
                {"properties": {"record_kind": {"const": "capability_binding"}}, "required": ["binding_id", "requirement_ref", "offer_refs", "proof_obligations", "residual_gap_refs"]},
            ],
        },
        "compiler-mapping.schema.json": object_schema(
            "Compiler requirement mapping", ["mapping_id", "from_requirement_ref", "through_library_ref", "compiler_stage", "emits", "must_prove", "invalidated_by", "release_gate"],
            {"mapping_id": {"type": "string"}, "from_requirement_ref": {"type": "string"}, "through_library_ref": {"type": "string"}, "compiler_stage": {"type": "string"}, "emits": nonempty_strings, "must_prove": nonempty_strings, "invalidated_by": nonempty_strings, "release_gate": {"type": "string"}}, kinds=["compiler_mapping"]),
        "product-truth.schema.json": object_schema(
            "Product-truth mapping", ["mapping_id", "product_truth", "semantic_owner_ref", "compiled_projection", "must_not_be_derived_from", "release_evidence", "refusal"],
            {"mapping_id": {"type": "string"}, "product_truth": {"type": "string"}, "semantic_owner_ref": {"type": "string"}, "compiled_projection": {"type": "string"}, "must_not_be_derived_from": {"type": "string"}, "release_evidence": nonempty_strings, "refusal": {"type": "string"}}, kinds=["product_truth_mapping"]),
        "cross-domain-mapping.schema.json": object_schema(
            "Cross-universe ownership mapping", ["mapping_id", "local_context_refs", "external_context_ref", "mapping_law", "ownership", "release_gate"],
            {"mapping_id": {"type": "string"}, "local_context_refs": nonempty_strings, "external_context_ref": {"type": "string"}, "mapping_law": {"type": "string"}, "ownership": {"type": "string"}, "release_gate": {"type": "string"}}, kinds=["cross_domain_mapping"]),
        "innovation.schema.json": object_schema(
            "Non-LLM platform innovation", ["innovation_id", "first_material_year", "non_llm", "core_change", "context_refs", "compiler_implications", "source_refs", "caveats"],
            {"innovation_id": {"type": "string"}, "first_material_year": {"type": "integer", "minimum": 2021, "maximum": 2026}, "non_llm": {"const": True}, "core_change": {"type": "string"}, "context_refs": nonempty_strings, "compiler_implications": nonempty_strings, "source_refs": nonempty_strings, "caveats": nonempty_strings}, kinds=["innovation"]),
        "gap.schema.json": object_schema(
            "Open research gap", ["gap_id", "subject", "gap_kind", "blocking", "resolution_condition", "prohibited_fallbacks"],
            {"gap_id": {"type": "string"}, "subject": {"type": "string"}, "gap_kind": {"type": "string"}, "blocking": {"type": "boolean"}, "resolution_condition": {"type": "string"}, "prohibited_fallbacks": nonempty_strings}, kinds=["gap"]),
        "vertical-example.schema.json": object_schema(
            "Illustrative vertical compiler trace", ["example_id", "vertical", "identity_model", "commercial_model", "usage_to_invoice", "service_model", "exit_model", "compiler_trace_refs", "refusal_example"],
            {"example_id": {"type": "string"}, "vertical": {"type": "string"}, "identity_model": {"type": "object"}, "commercial_model": {"type": "object"}, "usage_to_invoice": nonempty_strings, "service_model": {"type": "object"}, "exit_model": nonempty_strings, "compiler_trace_refs": nonempty_strings, "refusal_example": {"type": "string"}}, kinds=["vertical_example"]),
    }


def build_compiler_contract() -> dict:
    return {
        "contract_id": "compiler-contract.platform-commercial-support",
        "edition": EDITION,
        "status": STATUS,
        "completion_claim": False,
        "ir_stages": [
            {"stage": "01_input_admission", "proof": "schema, digest, supported edition, exact time and currency forms"},
            {"stage": "02_tenant_identity_scope", "proof": "tenant, account, organization, workspace, customer, billing account, and legal-entity refs are explicit and non-aliased"},
            {"stage": "03_authority_privacy", "proof": "security/privacy decision permits the action and disclosure scope"},
            {"stage": "04_catalog_contract_subscription", "proof": "offer, signed term projection, amendment, plan, and concrete subscription editions are reconciled"},
            {"stage": "05_entitlement", "proof": "feature grant covers subject, scope, effective time, and consumption law"},
            {"stage": "06_lifecycle", "proof": "command is total for current aggregate state"},
            {"stage": "07_quota_budget_credit", "proof": "quota, budget/precharge, prepaid credit, and their distinct refusals are evaluated independently"},
            {"stage": "08_runtime_feasibility", "proof": "resource demand can be admitted against qualified physical offers; entitlement and quota do not imply capacity"},
            {"stage": "09_provider_binding", "proof": "provider target offers exact required semantics, versions, limits, evidence, portability, and failure behavior"},
            {"stage": "10_effect_plan", "proof": "effect intents, idempotency, compensation, cancellation, and unknown-outcome reconciliation are explicit"},
            {"stage": "11_receipt_and_lineage", "proof": "append-only receipts bind tenant, authority, editions, inputs, outputs, event time, recorded time, and provider occurrence"},
            {"stage": "12_release_and_exit", "proof": "no blocking gaps remain; upgrade, rollback, portability, decommission, and residual-obligation paths are compiled"},
        ],
        "failure_refusal_precedence": [
            "malformed_or_unsupported_edition",
            "tenant_scope_or_non_enumeration",
            "authority_security_privacy_or_hold",
            "illegal_lifecycle_or_stale_edition",
            "commercial_entitlement",
            "technical_quota",
            "budget_or_prepaid_reservation",
            "physical_feasibility",
            "provider_acceptance_or_unknown_outcome",
            "post_commit_reconciliation",
        ],
        "forbidden_shortcuts": [
            "tenant_id equals billing_account_id",
            "entitled implies authorized",
            "quota available implies capacity available",
            "prepaid balance equals budget",
            "usage event equals invoice line",
            "plan equals contract",
            "SLO breach equals service credit",
            "incident equals support case or problem",
            "maintenance window erases outage",
            "termination implies deletion",
            "data export completes product exit",
            "provider API success proves domain completion",
        ],
        "release_outputs": ["platform commercial IR", "effect intents", "provider bindings", "typed refusal catalog", "receipt and evidence plan", "migration and exit plan", "gap report"],
    }


def build_artifacts() -> dict[str, object]:
    sources = build_sources()
    contexts = build_contexts()
    capabilities = build_capabilities(contexts)
    operations = build_operations(contexts)
    decisions = build_decisions(contexts)
    state_machines = build_state_machines()
    contracts = build_contracts(contexts)
    rules = build_invariants_refusals()
    libraries = build_libraries()
    library_replacements = build_library_replacements()
    rob = build_requirements_offers_bindings(libraries)
    mappings = build_compiler_mappings(libraries)
    truths = build_product_truth_mappings()
    cross = build_cross_domain_mappings()
    innovations = build_innovations()
    gaps = build_gaps()
    evidence = build_evidence(sources)
    examples = build_examples()
    record_total = len(capabilities) + len(operations) + len(decisions) + len(state_machines) + len(contracts)
    artifacts: dict[str, object] = {
        "bounded-context-candidates.jsonl": contexts,
        "capabilities.jsonl": capabilities,
        "operations.jsonl": operations,
        "decisions.jsonl": decisions,
        "state-machines.jsonl": state_machines,
        "contracts.jsonl": contracts,
        "invariants-refusals.jsonl": rules,
        "library-boundaries.jsonl": libraries,
        "retired-compositions.jsonl": library_replacements,
        "requirements-offers-bindings.jsonl": rob,
        "compiler-mappings.jsonl": mappings,
        "product-truth-mappings.jsonl": truths,
        "cross-domain-mappings.jsonl": cross,
        "sources.jsonl": sources,
        "evidence.jsonl": evidence,
        "innovations-2021-2026.jsonl": innovations,
        "gaps.jsonl": gaps,
        "vertical-examples.jsonl": examples,
        "compiler-contract.json": build_compiler_contract(),
    }
    counts = {name.removesuffix(".jsonl"): len(value) for name, value in artifacts.items() if name.endswith(".jsonl") and isinstance(value, list)}
    artifacts["manifest.json"] = {
        "universe_id": "universe.platform-commercial-support",
        "edition": EDITION,
        "status": "research_candidate",
        "as_of": AS_OF,
        "scope": "Horizontal platform, commercial, FinOps, service-management, customer-support, portability, and exit semantics needed to make generated enterprise data/analytics solutions adoptable and operable.",
        "explicit_exclusions": ["LLM or generative core semantics", "full legal domain", "tax or accounting advice", "payment-network implementation", "security/privacy semantic ownership", "runtime resource semantic ownership", "provider product ownership"],
        "completion_claim": False,
        "candidate_record_total": record_total,
        "counts": counts,
        "minimum_gates": {"bounded-context-candidates": 45, "candidate_record_total": 250, "sources": 70, "innovations-2021-2026": 20, "vertical-examples": 2},
        "generated_files": sorted([*artifacts.keys(), "manifest.json", *[f"schemas/{name}" for name in build_schemas()]]),
        "standing": "broad_sourced_candidate_requiring_adjudication_and_conformance",
    }
    return artifacts


def main() -> int:
    artifacts = build_artifacts()
    for name, value in artifacts.items():
        if name.endswith(".jsonl"):
            write_jsonl(HERE / name, value)  # type: ignore[arg-type]
        else:
            write_json(HERE / name, value)
    for name, schema in build_schemas().items():
        write_json(SCHEMAS / name, schema)
    manifest = artifacts["manifest.json"]
    assert isinstance(manifest, dict)
    print(
        "WROTE platform-commercial-support candidate: "
        f"{manifest['counts']['bounded-context-candidates']} contexts, "
        f"{manifest['candidate_record_total']} capability/operation/decision/lifecycle/contract records, "
        f"{manifest['counts']['sources']} official sources, "
        f"{manifest['counts']['innovations-2021-2026']} innovations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
