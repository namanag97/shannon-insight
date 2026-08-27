#!/usr/bin/env python3
"""Build the provider-neutral core semantic primitives research corpus.

The six families below are neighboring bounded-context universes.  Generation is
deterministic, but every generated record remains a research candidate: source
presence is evidence of a vocabulary or mechanism, never proof that a proposed
boundary is universally correct.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
EDITION = 1
ACCESSED = "2026-08-25"


def write_json(name: str, value: Any) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(name: str, rows: list[dict[str, Any]]) -> None:
    with (ROOT / name).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


FAMILIES = {
    "intent": {
        "title": "Enterprise intent, outcome, constraint and acceptance",
        "vision": "Translate an authorized desired change into falsifiable outcomes, bounded constraints and acceptance evidence without confusing goals, measures or plans.",
        "neighbors": ["identity", "time", "quantity", "authority", "decision"],
        "constitution": "intent != plan != requirement != acceptance != observed outcome",
        "contexts": [
            "stakeholder-and-actor", "problem-framing", "mission-and-negative-mission",
            "vision-and-desired-state", "goal", "objective", "outcome", "benefit-and-value",
            "harm-and-harmed-party", "assumption", "falsifier", "risk-to-objective",
            "constraint", "requirement", "requirement-decomposition", "traceability",
            "acceptance-criterion", "verification", "validation", "quality-attribute",
            "service-level-objective", "budget-and-tolerance", "option-and-course-of-action",
            "scope-and-non-goal", "dependency-and-enabler",
        ],
        "source_keys": ["omg-bmm", "iso-29148", "omg-sysml2", "iso-25010", "iso-31000"],
        "type_pair": ["IntentStatement", "AcceptanceContract"],
        "operations": ["declare", "refine", "challenge", "evaluate_acceptance"],
        "decisions": ["select_acceptance_semantics", "adjudicate_scope"],
    },
    "identity": {
        "title": "Identifier, identity, namespace, version and resolution",
        "vision": "Name, resolve and track subjects across scopes and time while preserving ambiguity, authority and lifecycle rather than pretending identifier equality proves identity.",
        "neighbors": ["intent", "time", "authority", "decision"],
        "constitution": "identifier != identity; proof of control != subject identity; same spelling != same referent",
        "contexts": [
            "identifier-syntax", "identifier-scheme", "namespace", "naming-authority",
            "identifier-assignment", "identifier-resolution", "identifier-dereference",
            "subject-identity", "identity-attribute", "identity-evidence", "proof-of-control",
            "entity-resolution", "record-linkage", "match-candidate", "match-adjudication",
            "equivalence-claim", "merge", "split", "supersession", "alias-and-redirect",
            "version-identity", "edition-identity", "occurrence-identity", "revocation-and-deactivation",
            "canonicalization-and-digest", "identifier-privacy-and-correlation",
        ],
        "source_keys": ["iso-24760-1", "ietf-rfc3986", "ietf-rfc9562", "w3c-did", "fellegi-sunter"],
        "type_pair": ["ScopedIdentifier", "ResolutionClaim"],
        "operations": ["assign", "resolve", "compare_in_scope", "reconcile"],
        "decisions": ["select_identity_policy", "adjudicate_match"],
    },
    "time": {
        "title": "Temporal position, interval, calendar, clock and database time",
        "vision": "Represent when things occur, apply, are observed and are recorded using explicit temporal reference systems, uncertainty and ordering guarantees.",
        "neighbors": ["identity", "quantity", "authority", "decision"],
        "constitution": "instant != local date-time; duration != calendar period; valid time != recording or transaction time",
        "contexts": [
            "temporal-reference-system", "clock", "clock-reading", "instant", "local-date",
            "local-time", "local-date-time", "utc-offset", "time-zone", "calendar",
            "calendar-period", "elapsed-duration", "interval", "interval-boundary",
            "interval-relation", "recurrence", "business-calendar", "precision-and-resolution",
            "event-time", "observation-time", "valid-time", "recording-time", "transaction-time",
            "processing-time", "decision-time", "correction-time", "bitemporal-history",
            "causal-order", "logical-clock", "clock-uncertainty-and-skew",
        ],
        "source_keys": ["iso-8601-1", "w3c-owl-time", "ietf-rfc3339", "snodgrass-ahn", "lamport-clocks"],
        "type_pair": ["QualifiedTemporalPosition", "TemporalExtent"],
        "operations": ["parse_with_reference", "relate", "convert", "correct_history"],
        "decisions": ["select_time_semantics", "adjudicate_temporal_order"],
    },
    "quantity": {
        "title": "Quantity, unit, scale, money, ratio, probability and partial information",
        "vision": "Carry magnitudes with dimensions, units, scales, uncertainty and information-state semantics so arithmetic cannot silently erase meaning.",
        "neighbors": ["intent", "time", "decision"],
        "constitution": "number != quantity; probability != confidence or score; missing != zero; censored != missing",
        "contexts": [
            "number-representation", "quantity-kind", "dimension", "unit", "unit-system",
            "scale-type", "ordinal-value", "nominal-value", "count", "measure-and-measurand",
            "measurement-result", "measurement-uncertainty", "precision-accuracy-resolution",
            "tolerance-and-conformance", "money", "currency-and-minor-unit", "price-and-valuation",
            "ratio", "rate", "proportion", "index-number", "probability", "odds-and-likelihood",
            "confidence-interval", "credible-and-coverage-interval", "score-and-ranking",
            "missingness", "not-applicable", "unknown-and-withheld", "censoring-and-truncation",
            "partial-result", "bounds-and-interval-arithmetic", "rounding-and-quantization",
        ],
        "source_keys": ["bipm-si", "iso-80000-1", "jcgm-vim", "jcgm-gum", "ich-e9-r1"],
        "type_pair": ["QualifiedQuantity", "InformationState"],
        "operations": ["construct_checked", "convert_unit", "propagate_uncertainty", "combine_partial"],
        "decisions": ["select_numeric_semantics", "select_missingness_policy"],
    },
    "authority": {
        "title": "Authority, ownership, delegation, entitlement and policy precedence",
        "vision": "Determine who may decide, issue, delegate, enforce or revoke a capability for a scoped purpose and time without collapsing responsibility or evidence into authority.",
        "neighbors": ["identity", "time", "intent", "decision"],
        "constitution": "authority != responsibility; approval != issuance; policy decision != enforcement; authentication != authorization",
        "contexts": [
            "authority-source", "mandate", "jurisdiction-and-scope", "ownership", "stewardship",
            "responsibility", "accountability", "delegation", "subdelegation", "role-and-membership",
            "entitlement", "capability-grant", "approval", "maker-checker", "separation-of-duties",
            "issuance", "activation", "suspension", "revocation", "expiry", "policy-rule",
            "policy-set", "policy-applicability", "policy-precedence", "authorization-decision",
            "obligation-and-advice", "enforcement", "exception-and-break-glass", "appeal-and-review",
        ],
        "source_keys": ["oasis-xacml", "nist-abac", "nist-rbac", "google-zanzibar", "ietf-rfc7009"],
        "type_pair": ["ScopedAuthority", "PolicyDecision"],
        "operations": ["delegate", "evaluate_policy", "issue", "revoke"],
        "decisions": ["combine_policy_results", "adjudicate_authority"],
    },
    "decision": {
        "title": "Governed decision, action, feedback and effect authority",
        "vision": "Turn qualified evidence and policy into governed decisions, separately authorized actions, observed effects and learning feedback with explicit refusal and compensation.",
        "neighbors": ["intent", "identity", "time", "quantity", "authority"],
        "constitution": "recommendation != decision; decision != action; action != effect; observation != causal effect",
        "contexts": [
            "decision-requirement", "decision-input", "decision-knowledge", "decision-model",
            "decision-rule", "decision-table", "decision-evaluation", "recommendation", "human-judgment",
            "decision-record", "decision-explanation", "action-proposal", "action-authorization",
            "action-command", "action-execution", "action-refusal", "effect-observation",
            "outcome-attribution", "feedback-signal", "control-policy", "control-loop",
            "intervention", "experiment-and-holdout", "compensation", "rollback-and-recall",
            "appeal-and-override", "monitoring-and-drift", "decision-quality",
        ],
        "source_keys": ["omg-dmn", "omg-bpmn", "omg-cmmn", "w3c-prov", "iso-31000"],
        "type_pair": ["GovernedDecision", "AuthorizedAction"],
        "operations": ["evaluate", "authorize_action", "execute_effect", "observe_feedback"],
        "decisions": ["select_decision_semantics", "adjudicate_intervention"],
    },
}


# Primary standards/specifications and original research.  Landing pages are used for paywalled
# standards and their authority_scope is correspondingly limited to public metadata/abstracts.
SOURCES = [
    # enterprise intent / requirements / acceptance
    ("omg-bmm", "Business Motivation Model 1.3", "OMG", "standard", "https://www.omg.org/spec/BMM/1.3/", 2015, ["intent"], "Ends, means, assessments, influencers, policies and rules"),
    ("omg-bacm", "Business Architecture Core Metamodel 1.0", "OMG", "standard", "https://www.omg.org/spec/BACM/1.0/", 2024, ["intent"], "Business architecture concepts and relationships"),
    ("omg-sysml2", "Systems Modeling Language 2.0", "OMG", "standard", "https://www.omg.org/spec/SysML/2.0/", 2025, ["intent"], "Requirements, verification, structure and behavior modeling"),
    ("omg-sysml-api", "Systems Modeling API and Services 1.0", "OMG", "standard", "https://www.omg.org/spec/SystemsModelingAPI/1.0/", 2025, ["intent"], "Machine access and interchange for system models"),
    ("omg-reqif", "Requirements Interchange Format 1.2", "OMG", "standard", "https://www.omg.org/spec/ReqIF/1.2/", 2016, ["intent"], "Requirement objects, relations and interchange"),
    ("iso-29148", "ISO/IEC/IEEE 29148:2018 Requirements engineering", "ISO", "standard_landing_page", "https://www.iso.org/standard/72089.html", 2018, ["intent"], "Requirements engineering lifecycle and characteristics"),
    ("iso-15288", "ISO/IEC/IEEE 15288:2023 System life cycle processes", "ISO", "standard_landing_page", "https://www.iso.org/standard/81702.html", 2023, ["intent"], "System lifecycle, stakeholder needs and validation"),
    ("iso-12207", "ISO/IEC/IEEE 12207:2017 Software life cycle processes", "ISO", "standard_landing_page", "https://www.iso.org/standard/63712.html", 2017, ["intent"], "Software lifecycle process outcomes"),
    ("iso-25010", "ISO/IEC 25010:2023 Product quality model", "ISO", "standard_landing_page", "https://www.iso.org/standard/78176.html", 2023, ["intent"], "Quality characteristics and acceptance criteria"),
    ("iso-25012", "ISO/IEC 25012:2008 Data quality model", "ISO", "standard_landing_page", "https://www.iso.org/standard/35736.html", 2008, ["intent", "quantity"], "Data quality characteristics"),
    ("iso-25030", "ISO/IEC 25030:2019 Quality requirements framework", "ISO", "standard_landing_page", "https://www.iso.org/standard/72115.html", 2019, ["intent"], "Quality requirements and stakeholders"),
    ("iso-25040", "ISO/IEC 25040:2024 Evaluation framework", "ISO", "standard_landing_page", "https://www.iso.org/standard/76056.html", 2024, ["intent"], "Evaluation requirements and process"),
    ("iso-25023", "ISO/IEC 25023:2016 Measurement of system and software product quality", "ISO", "standard_landing_page", "https://www.iso.org/standard/35747.html", 2016, ["intent", "quantity"], "Quality measures"),
    ("iso-31000", "ISO 31000:2018 Risk management", "ISO", "standard_landing_page", "https://www.iso.org/standard/65694.html", 2018, ["intent", "decision"], "Risk as effect of uncertainty on objectives and risk process"),
    ("iec-31010", "IEC 31010:2019 Risk assessment techniques", "IEC", "standard_landing_page", "https://www.iso.org/standard/72140.html", 2019, ["intent", "decision", "quantity"], "Selection and application of risk assessment techniques"),
    ("iso-9001", "ISO 9001:2015 Quality management systems", "ISO", "standard_landing_page", "https://www.iso.org/standard/62085.html", 2015, ["intent"], "Quality objectives, requirements and improvement"),
    ("iso-22301", "ISO 22301:2019 Business continuity management systems", "ISO", "standard_landing_page", "https://www.iso.org/standard/75106.html", 2019, ["intent"], "Continuity objectives, impact and acceptance"),
    ("iso-21502", "ISO 21502:2020 Project management guidance", "ISO", "standard_landing_page", "https://www.iso.org/standard/74947.html", 2020, ["intent"], "Objectives, outcomes, benefits and constraints"),
    ("iso-56002", "ISO 56002:2019 Innovation management systems", "ISO", "standard_landing_page", "https://www.iso.org/standard/68221.html", 2019, ["intent"], "Opportunity, intent, objectives and evaluation"),
    ("gqm", "The Goal Question Metric Approach", "NASA", "original_research", "https://ntrs.nasa.gov/citations/19930072901", 1992, ["intent", "quantity"], "Goal-question-metric derivation"),
    ("kaos", "Goal-Directed Requirements Acquisition", "Université catholique de Louvain", "original_research", "https://www.info.ucl.ac.be/~avl/files/1998/RE98.pdf", 1998, ["intent"], "Goal refinement, obstacles and responsibilities"),
    ("softgoal-nfr", "The NFR Framework", "University of Toronto", "original_research", "https://www.cs.toronto.edu/~alexei/pub/NFR.pdf", 2000, ["intent"], "Softgoals and non-functional requirement tradeoffs"),
    ("rfc2119", "RFC 2119 Key words for requirements", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc2119.html", 1997, ["intent"], "Normative requirement strength vocabulary"),
    ("rfc8174", "RFC 8174 Ambiguity of uppercase and lowercase requirement words", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8174.html", 2017, ["intent"], "Normative requirement-language interpretation"),
    # identity / identifiers / resolution
    ("iso-24760-1", "ISO/IEC 24760-1:2025 Identity management core concepts", "ISO", "standard_landing_page", "https://www.iso.org/standard/85882.html", 2025, ["identity"], "Identity, identifier, attributes and identity lifecycle"),
    ("iso-24760-2", "ISO/IEC 24760-2:2015 Reference architecture and requirements", "ISO", "standard_landing_page", "https://www.iso.org/standard/57915.html", 2015, ["identity", "authority"], "Identity management architecture"),
    ("iso-29115", "ISO/IEC 29115:2013 Entity authentication assurance", "ISO", "standard_landing_page", "https://www.iso.org/standard/45138.html", 2013, ["identity", "authority"], "Authentication assurance levels"),
    ("iso-29003", "ISO/IEC 29003:2018 Identity proofing", "ISO", "standard_landing_page", "https://www.iso.org/standard/62290.html", 2018, ["identity"], "Identity proofing requirements"),
    ("ietf-rfc3986", "RFC 3986 Uniform Resource Identifier", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc3986.html", 2005, ["identity"], "URI syntax, equivalence and resolution"),
    ("ietf-rfc3987", "RFC 3987 Internationalized Resource Identifiers", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc3987.html", 2005, ["identity"], "IRI syntax and mapping"),
    ("ietf-rfc8141", "RFC 8141 Uniform Resource Names", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8141.html", 2017, ["identity"], "URN syntax, namespaces and equivalence"),
    ("ietf-rfc9562", "RFC 9562 Universally Unique IDentifiers", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9562.html", 2024, ["identity", "time"], "UUID formats including time-ordered UUIDv7"),
    ("ietf-rfc4151", "RFC 4151 The tag URI Scheme", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc4151.html", 2005, ["identity", "time"], "Federated minting of identifiers"),
    ("ietf-rfc6920", "RFC 6920 Naming Things with Hashes", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc6920.html", 2013, ["identity"], "Digest-based names and verification"),
    ("ietf-rfc7595", "RFC 7595 URI Scheme Guidelines", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc7595.html", 2015, ["identity"], "Scheme definition and registration"),
    ("ietf-rfc8615", "RFC 8615 Well-Known URIs", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8615.html", 2019, ["identity"], "Origin-scoped discovery identifiers"),
    ("ietf-rfc8785", "RFC 8785 JSON Canonicalization Scheme", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8785.html", 2020, ["identity"], "Deterministic JSON representation"),
    ("w3c-did", "Decentralized Identifiers 1.0", "W3C", "standard", "https://www.w3.org/TR/did-core/", 2022, ["identity", "authority"], "DID subjects, controllers, resolution and deactivation"),
    ("w3c-did-resolution", "DID Resolution 0.3", "W3C", "draft_specification", "https://www.w3.org/TR/did-resolution/", 2026, ["identity"], "Resolution and dereferencing result metadata"),
    ("w3c-vc2", "Verifiable Credentials Data Model 2.0", "W3C", "standard", "https://www.w3.org/TR/vc-data-model-2.0/", 2025, ["identity", "authority"], "Issuer, holder, subject, status and verification roles"),
    ("w3c-rdf-canon", "RDF Dataset Canonicalization", "W3C", "standard", "https://www.w3.org/TR/rdf-canon/", 2024, ["identity"], "RDF dataset canonicalization"),
    ("ogc-naming", "OGC Naming Authority Policies", "OGC", "standard", "https://www.ogc.org/about/policies/naming-authority/", 2025, ["identity"], "Assignment and registration of OGC names"),
    ("gs1-digital-link", "GS1 Digital Link URI Standard 1.6", "GS1", "standard", "https://ref.gs1.org/standards/digital-link/", 2025, ["identity"], "GS1 identifiers in web URIs and resolver behavior"),
    ("doi-handbook", "DOI Handbook", "International DOI Foundation", "official_specification", "https://www.doi.org/doi-handbook/", 2025, ["identity"], "Persistent identifier syntax, resolution and governance"),
    ("ark-spec", "ARK Identifier Scheme", "ARK Alliance", "official_specification", "https://arks.org/about/", 2024, ["identity"], "Persistent actionable identifiers and naming authorities"),
    ("handle-spec", "Handle System Technical Manual", "CNRI", "official_specification", "https://www.handle.net/tech_manual.html", 2023, ["identity"], "Identifier resolution and administration"),
    ("fellegi-sunter", "A Theory for Record Linkage", "JASA", "original_research", "https://doi.org/10.1080/01621459.1969.10501049", 1969, ["identity", "quantity"], "Probabilistic record-linkage decision model"),
    ("winkler-em", "Using the EM Algorithm for Weight Computation in Record Linkage", "US Census Bureau", "original_research", "https://www.census.gov/library/working-papers/1988/adrm/rr88-05.html", 1988, ["identity", "quantity"], "Record-linkage weight estimation"),
    ("union-find", "Efficiency of a Good But Not Linear Set Union Algorithm", "ACM", "original_research", "https://doi.org/10.1145/321879.321884", 1975, ["identity"], "Equivalence-class merge algorithm and limits"),
    ("semver", "Semantic Versioning 2.0.0", "Semantic Versioning", "official_specification", "https://semver.org/spec/v2.0.0.html", 2013, ["identity"], "Version identifiers and precedence"),
    # temporal semantics
    ("iso-8601-1", "ISO 8601-1:2019 Basic date and time rules", "ISO", "standard_landing_page", "https://www.iso.org/standard/70907.html", 2019, ["time"], "Gregorian calendar and clock representations"),
    ("iso-8601-2", "ISO 8601-2:2019 Date and time extensions", "ISO", "standard_landing_page", "https://www.iso.org/standard/70908.html", 2019, ["time"], "Uncertain, approximate, partial dates and extended intervals"),
    ("iso-19108", "ISO 19108:2002 Temporal schema", "ISO", "standard_landing_page", "https://www.iso.org/standard/26013.html", 2002, ["time"], "Temporal objects, reference systems and topology"),
    ("w3c-owl-time", "Time Ontology in OWL", "W3C", "standard", "https://www.w3.org/TR/owl-time/", 2022, ["time"], "Instants, intervals, duration and temporal reference systems"),
    ("w3c-time-rel", "Extensions to OWL-Time entity relations", "W3C", "official_note", "https://www.w3.org/TR/vocab-owl-time-rel/", 2020, ["time"], "Relations across general temporal entities"),
    ("ietf-rfc3339", "RFC 3339 Date and Time on the Internet", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc3339.html", 2002, ["time"], "Internet timestamp profile"),
    ("ietf-rfc9557", "RFC 9557 Date and Time on the Internet: Timestamps with Additional Information", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9557.html", 2024, ["time"], "Time-zone identifiers and critical timestamp annotations"),
    ("ietf-rfc5545", "RFC 5545 Internet Calendaring and Scheduling", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc5545.html", 2009, ["time"], "Calendar components, recurrence and durations"),
    ("ietf-rfc7529", "RFC 7529 Non-Gregorian Recurrence Rules", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc7529.html", 2015, ["time"], "Calendar-system-qualified recurrence"),
    ("ietf-rfc8536", "RFC 8536 Time Zone Information Format", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8536.html", 2019, ["time"], "TZif transition representation"),
    ("ietf-rfc5905", "RFC 5905 Network Time Protocol Version 4", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc5905.html", 2010, ["time"], "Clock synchronization, offset and dispersion"),
    ("ietf-rfc8915", "RFC 8915 Network Time Security", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8915.html", 2020, ["time", "authority"], "Authenticated time synchronization"),
    ("ietf-rfc3161", "RFC 3161 Time-Stamp Protocol", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc3161.html", 2001, ["time", "authority"], "Timestamp authority and message imprint"),
    ("bipm-utc", "UTC metrology", "BIPM", "official_specification", "https://www.bipm.org/en/time-metrology", 2026, ["time"], "UTC realization and time metrology"),
    ("iana-tzdb", "Time Zone Database", "IANA", "official_registry", "https://www.iana.org/time-zones", 2026, ["time"], "Versioned civil time-zone rules"),
    ("snodgrass-ahn", "A Taxonomy of Time in Databases", "ACM", "original_research", "https://doi.org/10.1145/318898.318921", 1985, ["time"], "Valid, transaction and user-defined time taxonomy"),
    ("allen-interval", "Maintaining Knowledge about Temporal Intervals", "ACM", "original_research", "https://doi.org/10.1145/182.358434", 1983, ["time"], "Interval relations and constraint propagation"),
    ("lamport-clocks", "Time, Clocks, and the Ordering of Events", "ACM", "original_research", "https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/", 1978, ["time", "decision"], "Happens-before and logical clocks"),
    ("mattern-vector", "Virtual Time and Global States of Distributed Systems", "University of Kaiserslautern", "original_research", "https://www.vs.inf.ethz.ch/publ/papers/VirtTimeGlobStates.pdf", 1989, ["time"], "Vector time and consistent cuts"),
    ("hlc", "Logical Physical Clocks and Consistent Snapshots", "University at Buffalo", "original_research", "https://cse.buffalo.edu/tech-reports/2014-04.pdf", 2014, ["time"], "Hybrid logical clocks"),
    ("spanner", "Spanner: Google's Globally-Distributed Database", "Google", "original_research", "https://research.google/pubs/spanner-googles-globally-distributed-database/", 2012, ["time"], "Bounded clock uncertainty and externally consistent transactions"),
    ("sql-temporal", "ISO/IEC 9075-2:2023 SQL/Foundation", "ISO", "standard_landing_page", "https://www.iso.org/standard/76584.html", 2023, ["time"], "Application-time and system-versioned data features"),
    # quantities / uncertainty / missingness
    ("bipm-si", "SI Brochure, 9th edition", "BIPM", "official_specification", "https://www.bipm.org/en/publications/si-brochure", 2026, ["quantity", "time"], "SI quantities, dimensions, units and writing rules"),
    ("jcgm-vim", "JCGM 200:2012 International Vocabulary of Metrology", "JCGM", "standard", "https://doi.org/10.59161/JCGM200-2012", 2012, ["quantity"], "Measurement concepts, measurands, results and uncertainty"),
    ("jcgm-gum", "JCGM 100:2008 Guide to expression of uncertainty", "JCGM", "standard", "https://doi.org/10.59161/JCGM100-2008E", 2008, ["quantity"], "Measurement models and uncertainty propagation"),
    ("jcgm-gum101", "JCGM 101:2008 Monte Carlo propagation", "JCGM", "standard", "https://doi.org/10.59161/JCGM101-2008", 2008, ["quantity"], "Monte Carlo propagation of distributions"),
    ("jcgm-gum102", "JCGM 102:2011 Multiple output quantities", "JCGM", "standard", "https://doi.org/10.59161/JCGM102-2011", 2011, ["quantity"], "Multivariate uncertainty propagation"),
    ("jcgm-gum106", "JCGM 106:2012 Uncertainty in conformity assessment", "JCGM", "standard", "https://doi.org/10.59161/JCGM106-2012", 2012, ["quantity", "decision"], "Decision rules with measurement uncertainty"),
    ("jcgm-gum1", "JCGM GUM-1:2023 Introduction", "JCGM", "standard", "https://doi.org/10.59161/JCGMGUM-1-2023", 2023, ["quantity"], "Measurement uncertainty concepts"),
    ("jcgm-gum6", "JCGM GUM-6:2020 Measurement models", "JCGM", "standard", "https://doi.org/10.59161/JCGMGUM-6-2020", 2020, ["quantity"], "Developing and using measurement models"),
    ("iso-80000-1", "ISO 80000-1:2022 Quantities and units general", "ISO", "standard_landing_page", "https://www.iso.org/standard/76921.html", 2022, ["quantity"], "Quantity, unit, symbols and coherent systems"),
    ("iso-80000-2", "ISO 80000-2:2019 Mathematics", "ISO", "standard_landing_page", "https://www.iso.org/standard/64973.html", 2019, ["quantity"], "Mathematical signs and concepts"),
    ("iso-80000-3", "ISO 80000-3:2019 Space and time", "ISO", "standard_landing_page", "https://www.iso.org/standard/64974.html", 2019, ["quantity", "time"], "Space and time quantities and units"),
    ("iso-80000-4", "ISO 80000-4:2019 Mechanics", "ISO", "standard_landing_page", "https://www.iso.org/standard/64975.html", 2019, ["quantity"], "Mechanics quantity kinds and units"),
    ("iso-80000-5", "ISO 80000-5:2019 Thermodynamics", "ISO", "standard_landing_page", "https://www.iso.org/standard/64976.html", 2019, ["quantity"], "Thermodynamic quantity kinds and units"),
    ("iso-4217", "ISO 4217:2015 Currency codes", "ISO", "standard_landing_page", "https://www.iso.org/standard/64758.html", 2015, ["quantity"], "Currency identifiers and minor units"),
    ("ucum", "Unified Code for Units of Measure 2.2", "Regenstrief Institute", "official_specification", "https://ucum.org/ucum", 2024, ["quantity"], "Computable unit syntax and conversion"),
    ("qudt", "QUDT Schema and Vocabularies", "QUDT.org", "official_specification", "https://www.qudt.org/pages/QUDToverviewPage.html", 2024, ["quantity"], "Quantity kinds, dimensions, units and scales"),
    ("w3c-sosa", "Semantic Sensor Network Ontology", "W3C", "standard", "https://www.w3.org/TR/vocab-ssn/", 2017, ["quantity", "time"], "Observation, procedure, result, property and feature"),
    ("w3c-data-cube", "RDF Data Cube Vocabulary", "W3C", "standard", "https://www.w3.org/TR/vocab-data-cube/", 2014, ["quantity"], "Observations, measures, dimensions and attributes"),
    ("sdmx-3", "SDMX Information Model 3.0", "SDMX", "standard", "https://docs.sdmx.org/en/3.0/information-model/", 2021, ["quantity", "identity"], "Statistical observations, concepts and structures"),
    ("iso-3534-1", "ISO 3534-1:2006 Statistics vocabulary", "ISO", "standard_landing_page", "https://www.iso.org/standard/40145.html", 2006, ["quantity"], "Probability and general statistical terms"),
    ("rubin-missing", "Inference and Missing Data", "Biometrika", "original_research", "https://doi.org/10.1093/biomet/63.3.581", 1976, ["quantity"], "MCAR, MAR and nonignorable missingness foundations"),
    ("kaplan-meier", "Nonparametric Estimation from Incomplete Observations", "JASA", "original_research", "https://doi.org/10.1080/01621459.1958.10501452", 1958, ["quantity", "time"], "Right-censoring survival estimator"),
    ("cox-hazard", "Regression Models and Life-Tables", "JRSS B", "original_research", "https://doi.org/10.1111/j.2517-6161.1972.tb00899.x", 1972, ["quantity", "time"], "Proportional hazards with censoring"),
    ("ich-e9-r1", "ICH E9(R1) Estimands and sensitivity analysis", "ICH/FDA", "regulatory_guidance", "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical", 2021, ["quantity", "decision"], "Estimands, intercurrent events and sensitivity analysis"),
    ("ieee-754", "IEEE 754-2019 Floating-Point Arithmetic", "IEEE", "standard_landing_page", "https://standards.ieee.org/standard/754-2019.html", 2019, ["quantity"], "Floating-point values, rounding and exceptional values"),
    ("decimal-arithmetic", "General Decimal Arithmetic Specification", "IBM", "official_specification", "https://speleotrove.com/decimal/decarith.html", 2020, ["quantity"], "Decimal arithmetic, contexts and rounding"),
    # authority / policy
    ("oasis-xacml", "XACML 3.0 Plus Errata", "OASIS", "standard", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-en.html", 2017, ["authority", "decision"], "Policy evaluation, combining, obligations and enforcement roles"),
    ("oasis-xacml-admin", "XACML 3.0 Administration and Delegation Profile", "OASIS", "standard", "https://docs.oasis-open.org/xacml/3.0/xacml-3.0-admin-v1-spec-en.html", 2014, ["authority"], "Administrative authority and policy delegation"),
    ("nist-abac", "NIST SP 800-162 Attribute Based Access Control", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/162/upd2/final", 2019, ["authority"], "ABAC concepts and policy evaluation"),
    ("nist-rbac", "NIST Role-Based Access Control Model", "NIST", "original_research", "https://csrc.nist.gov/projects/role-based-access-control", 2000, ["authority"], "Roles, permissions, sessions and separation of duties"),
    ("nist-policy-test", "NIST SP 800-192 Access control policy verification", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/192/final", 2017, ["authority"], "Policy model verification and testing"),
    ("google-zanzibar", "Zanzibar: Google's Consistent Global Authorization System", "Google/USENIX", "original_research", "https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/", 2019, ["authority", "time"], "Relationship authorization with causal consistency"),
    ("ietf-rfc6749", "RFC 6749 OAuth 2.0 Authorization Framework", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc6749.html", 2012, ["authority", "identity"], "Delegated authorization roles and grants"),
    ("ietf-rfc7009", "RFC 7009 OAuth Token Revocation", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc7009.html", 2013, ["authority"], "Token revocation endpoint semantics"),
    ("ietf-rfc7662", "RFC 7662 OAuth Token Introspection", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc7662.html", 2015, ["authority"], "Current token activity and metadata"),
    ("ietf-rfc8693", "RFC 8693 OAuth Token Exchange", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8693.html", 2020, ["authority"], "Delegation and impersonation token exchange"),
    ("ietf-rfc8725", "RFC 8725 JSON Web Token Best Current Practices", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc8725.html", 2020, ["authority", "identity"], "JWT validation and substitution boundaries"),
    ("ietf-rfc9396", "RFC 9396 OAuth Rich Authorization Requests", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9396.html", 2023, ["authority"], "Structured fine-grained authorization details"),
    ("ietf-rfc9449", "RFC 9449 OAuth Demonstrating Proof of Possession", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9449.html", 2023, ["authority", "identity"], "Sender-constrained token proof"),
    ("ietf-rfc9470", "RFC 9470 OAuth Step Up Authentication Challenge", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9470.html", 2023, ["authority", "identity"], "Authentication context requirements for resources"),
    ("ietf-rfc9635", "RFC 9635 Grant Negotiation and Authorization Protocol", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9635.html", 2024, ["authority"], "Negotiated grants, rights and continuation"),
    ("w3c-vc-status", "Bitstring Status List 1.0", "W3C", "standard", "https://www.w3.org/TR/vc-bitstring-status-list/", 2025, ["authority", "identity"], "Credential revocation and suspension status"),
    ("tuf", "The Update Framework Specification", "Linux Foundation", "official_specification", "https://theupdateframework.github.io/specification/latest/", 2026, ["authority", "identity", "time"], "Delegated roles, thresholds, expiry and revocation"),
    ("cedar", "Cedar Policy Language", "AWS", "official_specification", "https://docs.cedarpolicy.com/", 2025, ["authority", "decision"], "Authorization policy semantics and validation"),
    ("cedar-paper", "Cedar: A New Language for Expressive, Fast, Safe Authorization", "AWS", "original_research", "https://www.amazon.science/publications/cedar-a-new-language-for-expressive-fast-safe-and-analyzable-authorization", 2024, ["authority"], "Analyzable policy language design"),
    ("rego-paper", "OPA: Policy-based Control for Cloud Native Environments", "CNCF", "original_research", "https://www.usenix.org/conference/atc21/presentation/osborn", 2021, ["authority"], "Policy-as-code evaluation and distribution"),
    ("spiffe", "SPIFFE Specification", "CNCF", "official_specification", "https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE.md", 2025, ["authority", "identity"], "Workload identities and trust domains"),
    # governed decision, action, feedback and effect
    ("omg-dmn", "Decision Model and Notation 1.5", "OMG", "standard", "https://www.omg.org/spec/DMN/1.5/", 2024, ["decision"], "Decision requirements, FEEL and executable decision logic"),
    ("omg-bpmn", "Business Process Model and Notation 2.0.2", "OMG", "standard", "https://www.omg.org/spec/BPMN/2.0.2/", 2014, ["decision"], "Activities, events, errors, compensation and process execution"),
    ("omg-cmmn", "Case Management Model and Notation 1.1", "OMG", "standard", "https://www.omg.org/spec/CMMN/1.1/", 2016, ["decision"], "Discretionary work, sentries, milestones and human case judgment"),
    ("omg-sbvr", "Semantics of Business Vocabulary and Rules 1.5", "OMG", "standard", "https://www.omg.org/spec/SBVR/1.5/", 2019, ["decision", "intent"], "Business vocabulary, rules and modalities"),
    ("omg-prr", "Production Rule Representation 1.0", "OMG", "standard", "https://www.omg.org/spec/PRR/1.0/", 2009, ["decision"], "Production rule interchange semantics"),
    ("w3c-prov", "PROV Data Model", "W3C", "standard", "https://www.w3.org/TR/prov-dm/", 2013, ["decision", "identity", "time"], "Entities, activities, agents and derivation"),
    ("cncf-cloudevents", "CloudEvents 1.0.2", "CNCF", "official_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", 2022, ["decision", "time", "identity"], "Portable event occurrence envelope"),
    ("openlineage", "OpenLineage Specification", "OpenLineage", "official_specification", "https://openlineage.io/docs/spec/", 2026, ["decision", "time", "identity"], "Run events and observed execution metadata"),
    ("pearl-causality", "Causal Diagrams for Empirical Research", "Biometrika", "original_research", "https://doi.org/10.1093/biomet/82.4.669", 1995, ["decision", "quantity"], "Causal graph intervention semantics"),
    ("rubin-causal", "Estimating Causal Effects of Treatments", "Journal of Educational Psychology", "original_research", "https://doi.org/10.1037/h0037350", 1974, ["decision", "quantity"], "Potential-outcome treatment effects"),
    ("robbins-bandit", "Some Aspects of the Sequential Design of Experiments", "Bulletin AMS", "original_research", "https://projecteuclid.org/journals/bulletin-of-the-american-mathematical-society/volume-58/issue-5/Some-aspects-of-the-sequential-design-of-experiments/bams/1183517370.full", 1952, ["decision", "quantity"], "Exploration and exploitation in sequential decisions"),
    ("mape-k", "An Architectural Blueprint for Autonomic Computing", "IBM Research", "original_research", "https://www.researchgate.net/publication/239600267_An_Architectural_Blueprint_for_Autonomic_Computing", 2006, ["decision"], "Monitor-analyze-plan-execute feedback loop"),
    ("control-feedback", "Feedback Systems: An Introduction for Scientists and Engineers", "Caltech", "original_research", "https://fbswiki.org/wiki/index.php/Feedback_Systems:_An_Introduction_for_Scientists_and_Engineers", 2020, ["decision", "quantity", "time"], "Feedback, stability, state and control"),
    ("pctl", "Probabilistic Computation Tree Logic", "Oxford", "original_research", "https://doi.org/10.1016/0890-5401(91)90012-K", 1991, ["decision", "quantity", "time"], "Temporal properties of probabilistic systems"),
    ("iso-38507", "ISO/IEC 38507:2022 Governance implications of AI", "ISO", "standard_landing_page", "https://www.iso.org/standard/56641.html", 2022, ["decision", "authority"], "Governance and accountability for automated decisions; used only for generic governance distinctions"),
    ("iso-42010", "ISO/IEC/IEEE 42010:2022 Architecture description", "ISO", "standard_landing_page", "https://www.iso.org/standard/74393.html", 2022, ["intent", "decision"], "Stakeholders, concerns, viewpoints and architecture decisions"),
    ("nist-800-53", "NIST SP 800-53 Rev.5", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final", 2020, ["authority", "decision"], "Authorization, audit, separation and system controls"),
    ("nist-800-61", "NIST SP 800-61 Rev.3 Incident Response", "NIST", "government_standard", "https://csrc.nist.gov/pubs/sp/800/61/r3/final", 2025, ["decision", "authority"], "Incident actions, authority, evidence and recovery"),
    ("ietf-rfc9334", "RFC 9334 RATS Architecture", "IETF", "standard", "https://www.rfc-editor.org/rfc/rfc9334.html", 2023, ["decision", "authority", "identity"], "Evidence, appraisal and relying-party decision roles"),
]


DISTINCTIONS = [
    ("identity", "identifier", "identity", "An identifier is a scoped symbol; identity is the set of attributes and relations by which a subject is recognized in a domain."),
    ("identity", "proof_of_control", "identity", "Control of a credential or key proves control under a method, not who or what the subject is."),
    ("identity", "same_identifier_spelling", "same_referent", "Lexical equality without scheme, namespace, version and time cannot establish co-reference."),
    ("identity", "digest_equality", "semantic_equality", "Equal digests under one canonical representation do not establish semantic equality under another model."),
    ("identity", "merge", "equivalence", "A merge is an authorized lifecycle action; it does not prove all historical assertions were equivalent."),
    ("identity", "alias", "canonical_identifier", "An alias preserves a mapping claim and its authority; it is not silently rewritten into canonical identity."),
    ("time", "instant", "local_date_time", "A local date-time needs a calendar, zone rule or offset and disambiguation before it can denote an instant."),
    ("time", "elapsed_duration", "calendar_period", "Elapsed seconds and calendar months have different arithmetic and cannot be freely substituted."),
    ("time", "valid_time", "recording_time", "When a claim applies differs from when a system learned or stored it."),
    ("time", "event_time", "processing_time", "Occurrence time and processing time support different window, lateness and correction laws."),
    ("time", "clock_reading", "causal_order", "A wall-clock reading cannot by itself prove happens-before in a distributed system."),
    ("time", "time_zone", "utc_offset", "An offset is one result of versioned zone rules at an instant; it is not the zone."),
    ("quantity", "number", "quantity", "A scalar without quantity kind, unit and scale cannot participate safely in domain arithmetic."),
    ("quantity", "dimensionless", "unitless", "Quantities with unit one can still have distinct quantity kinds and interpretation."),
    ("quantity", "probability", "confidence", "Probability requires a sample space and semantics; confidence may denote procedure coverage or informal belief."),
    ("quantity", "probability", "score", "A score need not be calibrated, additive or probabilistic."),
    ("quantity", "missing", "zero", "Absence of a value is not the additive identity."),
    ("quantity", "censored", "missing", "Censoring carries a known bound or observation mechanism; generic missingness does not."),
    ("quantity", "accuracy", "precision", "Closeness to a reference and repeatability are different properties."),
    ("quantity", "money", "decimal", "Money additionally requires currency, minor-unit, valuation-time and rounding policy."),
    ("intent", "intent", "implementation", "The desired change does not prescribe a single realization unless explicitly constrained."),
    ("intent", "goal", "metric", "A measure supplies evidence about a goal; it is not the desired state itself."),
    ("intent", "requirement", "acceptance_evidence", "A normative statement and evidence that it was satisfied remain separately identifiable."),
    ("intent", "assumption", "fact", "An assumption is challengeable and must carry a falsifier or review trigger."),
    ("intent", "verification", "validation", "Conformance to specification differs from fitness for the intended use."),
    ("authority", "authority", "responsibility", "Being accountable for work does not necessarily grant power to authorize it."),
    ("authority", "approval", "issuance", "Approval is a decision; issuance creates a grant or artifact and requires separate effect authority."),
    ("authority", "policy_decision", "enforcement", "A permit result has no effect until an authorized enforcement point applies it."),
    ("authority", "authentication", "authorization", "Evidence about a principal does not establish permission for an action."),
    ("authority", "ownership", "stewardship", "Title or control and delegated care obligations have different lifecycles and powers."),
    ("authority", "revocation", "deletion", "Removing authority or status is not erasing the historical record."),
    ("decision", "recommendation", "decision", "A recommendation proposes; a decision commits an authorized decision-maker under policy."),
    ("decision", "decision", "action", "A decision is a governed conclusion; an action changes or attempts to change the world."),
    ("decision", "action", "effect", "Command success or action completion does not prove the intended effect occurred."),
    ("decision", "observation", "fact", "An observation is a method- and time-qualified assertion, not reality itself."),
    ("decision", "association", "causal_effect", "Observed association does not identify the counterfactual effect of intervention."),
    ("decision", "rollback", "compensation", "Rollback restores prior technical state where possible; compensation is a domain action for irreversible work."),
]


INNOVATIONS = [
    (2021, "SDMX 3.0", "sdmx-3", "Separates statistical structures, constraints, data and metadata with a revised information model.", "Adoption and crosswalk qualification remain context-specific."),
    (2021, "ICH E9(R1) estimand framework", "ich-e9-r1", "Makes treatment effect of interest explicit before estimator and missing-data handling.", "Clinical-trial guidance does not define generic enterprise causality."),
    (2021, "OPA policy distribution study", "rego-paper", "Documents a general policy decision/control plane with distributed bundles.", "A policy engine still does not establish business authority or enforcement."),
    (2022, "DID 1.0 Recommendation", "w3c-did", "Standardizes identifier/controller/resolution/deactivation roles.", "DID control is not real-world identity assurance."),
    (2022, "OWL-Time revision", "w3c-owl-time", "Generalizes temporal positions, reference systems and interval relations.", "Ontology expressivity does not resolve clock trust or database correction policy."),
    (2022, "ISO 80000-1 revision", "iso-80000-1", "Refreshes general quantity, unit and coherent-system concepts.", "Ordinal and nominal properties are still out of its stated scope."),
    (2022, "ISO/IEC/IEEE 42010 revision", "iso-42010", "Improves architecture description, concerns and viewpoints.", "Architecture descriptions do not prove runtime satisfaction."),
    (2022, "ISO/IEC 38507", "iso-38507", "Sharpens governance roles for automated systems.", "AI-specific material is not a core dependency here."),
    (2023, "ISO/IEC 25010 quality model revision", "iso-25010", "Nine-characteristic product quality model supports requirements and acceptance.", "Quality labels require operational measures and acceptance authority."),
    (2023, "JCGM GUM-1", "jcgm-gum1", "Modern introduction to measurement uncertainty concepts.", "It does not turn informal model scores into calibrated uncertainty."),
    (2023, "OAuth Rich Authorization Requests", "ietf-rfc9396", "Carries structured authorization details beyond flat scopes.", "Request richness does not grant authority."),
    (2023, "OAuth DPoP", "ietf-rfc9449", "Sender-constrains access and refresh tokens using proof of possession.", "Key possession does not identify the subject or authorize resource semantics."),
    (2023, "OAuth step-up challenge", "ietf-rfc9470", "Lets resources demand authentication context for a specific request.", "Authentication level and authorization remain distinct."),
    (2023, "RATS architecture", "ietf-rfc9334", "Separates evidence, appraisal policy, verifier and relying-party decision.", "Successful appraisal is not universal trust or action authority."),
    (2023, "SQL:2023 temporal foundation", "sql-temporal", "Maintains standard temporal table features in current SQL edition.", "Vendor implementations still require exact feature qualification."),
    (2024, "UUID revision and UUIDv7", "ietf-rfc9562", "Defines sortable time-ordered UUIDs and modern generation rules.", "Sort order is not causal order or entity identity."),
    (2024, "RFC 9557 timestamp annotations", "ietf-rfc9557", "Binds time-zone identifiers and critical annotations to Internet timestamps.", "Zone database version and ambiguity policy remain necessary."),
    (2024, "RDF Dataset Canonicalization", "w3c-rdf-canon", "Standardizes deterministic blank-node-sensitive RDF canonicalization.", "Canonical bytes do not prove claim truth."),
    (2024, "Business Architecture Core Metamodel", "omg-bacm", "Provides a standard machine-readable business architecture core.", "It does not replace bounded-context ownership or domain invariants."),
    (2024, "DMN 1.5", "omg-dmn", "Extends interoperable decision models and machine-readable artifacts.", "Executable decision logic is not action authorization."),
    (2024, "GNAP", "ietf-rfc9635", "Models negotiated grants and continuation-based authorization flows.", "Deployment profiles and resource semantics must still be qualified."),
    (2024, "Cedar policy-language publication", "cedar-paper", "Combines expressive authorization with validation and analysis.", "Language safety cannot establish the authority of policy authors."),
    (2024, "UCUM 2.2", "ucum", "Updates a computable unit code system used in interoperable data.", "Syntactic unit conversion cannot choose the right quantity kind."),
    (2025, "ISO/IEC 24760-1 revision", "iso-24760-1", "Refreshes horizontal identity, identifier and attribute concepts.", "Identity is still domain-relative and evidence-qualified."),
    (2025, "Verifiable Credentials 2.0", "w3c-vc2", "Updates credential, subject, holder, issuer and verification semantics.", "Verifiability does not establish claim truth."),
    (2025, "Bitstring Status List 1.0", "w3c-vc-status", "Standardizes privacy-conscious credential suspension and revocation status.", "Status freshness and relying policy remain explicit."),
    (2025, "ISO 8601-2 canonical-expression amendment", "iso-8601-2", "Adds canonical expressions and date-time arithmetic extensions.", "Representation canonicality does not select business time semantics."),
    (2025, "GS1 Digital Link 1.6", "gs1-digital-link", "Advances resolvable product identifiers and link semantics.", "Resolution targets and product identity assertions need authority and time."),
    (2025, "SysML v2 and standard API", "omg-sysml2", "Adds precise textual semantics and an interoperable model API.", "Systems models remain declarations until verified against occurrences."),
    (2025, "NIST incident response revision", "nist-800-61", "Integrates governed incident actions with modern risk management.", "Guidance does not choose enterprise-specific action authority."),
    (2026, "SI Brochure digital updates", "bipm-si", "Clarifies non-SI units and supports machine-readable SI reference work.", "A digital unit registry does not define domain measurement procedures."),
    (2026, "GUM nonlinearity amendment", "jcgm-gum", "Addresses nonlinearity in measurement models.", "Model adequacy and input distributions still require evidence."),
    (2026, "DID Resolution 0.3", "w3c-did-resolution", "Makes resolution and dereferencing result metadata explicit.", "Draft status and method-specific behavior prevent universal qualification."),
    (2026, "OpenLineage current specification", "openlineage", "Continues versioned runtime lineage event semantics.", "Observed run events do not prove decision effect or causal outcome."),
    (2026, "TUF current delegated update model", "tuf", "Maintains threshold delegation, expiry and rollback/freeze protections.", "Artifact authorization remains scope- and repository-specific."),
]


# Artifact-linked experts are learning routes, not appeals to authority.  The compiler consumes
# their explicit models and laws, never reputation.
EXPERTS = [
    ("Victor Basili", "intent", "gqm", "Derive questions and measures from a declared goal and viewpoint.", "A metric hierarchy does not replace acceptance authority or causal outcome evidence."),
    ("Axel van Lamsweerde", "intent", "kaos", "Refine goals into requirements, agents, obstacles and resolutions.", "Goal refinement is not proof that the selected design will produce the outcome."),
    ("Anne Dardenne", "intent", "kaos", "Model goal-directed requirements with operational responsibility.", "Responsibility assignment must remain separate from authority."),
    ("Alexander Borgida", "intent", "kaos", "Use formal goal models to expose conflict and obstruction.", "Formal consistency inside a model does not establish stakeholder legitimacy."),
    ("Lawrence Chung", "intent", "softgoal-nfr", "Represent non-functional goals and explicit tradeoff reasoning.", "Softgoal contribution labels need domain evidence and cannot become universal scores."),
    ("John Mylopoulos", "intent", "softgoal-nfr", "Keep actor intention and non-functional concerns explicit in requirements models.", "An intentional model is a declaration, not runtime evidence."),
    ("Alistair Mavin", "intent", "iso-29148", "Write requirement statements with controlled structure and testable conditions.", "Syntactic quality does not prove a requirement is the right one."),
    ("Michael Jackson", "intent", "iso-29148", "Separate the problem world, machine boundary and requirement phenomena.", "Do not collapse domain observations into software state."),
    ("Ivan Fellegi", "identity", "fellegi-sunter", "Treat record linkage as an evidence-weighted decision with explicit error tradeoffs.", "A high match weight is not metaphysical identity."),
    ("Alan Sunter", "identity", "fellegi-sunter", "Use likelihood-ratio evidence and decision thresholds for linkage.", "Thresholds require population and loss assumptions."),
    ("William Winkler", "identity", "winkler-em", "Estimate record-linkage weights when labeled pairs are scarce and inspect comparison fields.", "EM estimates do not remove dependence or selection assumptions."),
    ("Peter Christen", "identity", "fellegi-sunter", "Decompose entity resolution into indexing, comparison, classification and evaluation.", "Benchmark accuracy does not establish deployment-specific ground truth."),
    ("Drummond Reed", "identity", "w3c-did", "Separate DID subject, controller, document, method and resolver roles.", "Controller proof is not subject identity assurance."),
    ("Manu Sporny", "identity", "w3c-vc2", "Keep credential issuer, holder, subject, verifier and status semantics distinct.", "Cryptographic verification does not prove claim truth."),
    ("Markus Sabadello", "identity", "w3c-did", "Model identifier resolution and method-specific lifecycle explicitly.", "DID portability does not erase method and registry dependencies."),
    ("Roy Fielding", "identity", "ietf-rfc3986", "Understand generic URI syntax, resolution and reference identity boundaries.", "Dereference behavior and resource identity remain application-defined."),
    ("Richard Snodgrass", "time", "snodgrass-ahn", "Separate valid time from transaction time and preserve both in historical databases.", "Bitemporality does not identify event or observation time automatically."),
    ("Ilsoo Ahn", "time", "snodgrass-ahn", "Use a precise taxonomy of database time instead of a generic timestamp column.", "Adding two columns without update/correction laws is not a bitemporal model."),
    ("James Allen", "time", "allen-interval", "Use a complete interval-relation algebra and propagate temporal constraints.", "Constraint consistency does not establish the truth of supplied intervals."),
    ("Leslie Lamport", "time", "lamport-clocks", "Use happens-before and logical clocks for distributed causal order.", "Logical timestamps are not physical time or causality outside message/process relations."),
    ("Friedemann Mattern", "time", "mattern-vector", "Use vector time and consistent cuts to retain concurrency information.", "Vector-clock comparison does not yield a total real-time order."),
    ("Sandeep Kulkarni", "time", "hlc", "Combine bounded physical proximity with logical causality in hybrid clocks.", "HLC still depends on stated clock and overflow assumptions."),
    ("Murat Demirbas", "time", "hlc", "Use HLCs to make consistent-snapshot reasoning practical.", "A hybrid timestamp is not a valid-time or timezone model."),
    ("Simon Cox", "time", "w3c-owl-time", "Model instants, intervals, duration and alternative temporal reference systems.", "Ontology relations do not qualify clock implementations."),
    ("Chris Little", "time", "w3c-owl-time", "Keep calendars, clocks and temporal reference systems visible in interchange.", "Civil-time labels cannot be normalized without zone/calendar rules."),
    ("Antonio Possolo", "quantity", "jcgm-gum", "Represent uncertainty as information about a measurand with explicit distributional assumptions.", "Uncertainty is not generic model confidence."),
    ("Barry Taylor", "quantity", "jcgm-gum", "Preserve standard and expanded uncertainty, coverage factor and reporting rules.", "A ± value is uninterpretable without its construction and coverage semantics."),
    ("Mike Cowlishaw", "quantity", "decimal-arithmetic", "Make decimal contexts, exceptional values and rounding explicit.", "Exact decimal representation does not supply currency or valuation semantics."),
    ("Donald Rubin", "quantity", "rubin-missing", "Model missingness mechanisms and separate them from observed values.", "MAR/MNAR generally cannot be selected from null patterns alone."),
    ("Edward Kaplan", "quantity", "kaplan-meier", "Retain risk sets and censoring information in survival estimation.", "The estimator relies on censoring assumptions and does not turn censored into observed events."),
    ("Paul Meier", "quantity", "kaplan-meier", "Use product-limit estimation rather than dropping incomplete follow-up.", "Survival probability is conditional on the study design and population."),
    ("David Cox", "quantity", "cox-hazard", "Separate a semiparametric relative hazard model from baseline hazard.", "Hazard ratios are not risk ratios or causal effects without assumptions."),
    ("David Ferraiolo", "authority", "nist-rbac", "Separate users, roles, sessions, permissions and constraints.", "Roles do not by themselves model resource relationships, purpose or dynamic context."),
    ("Ravi Sandhu", "authority", "nist-rbac", "Model role hierarchies and administrative control explicitly.", "Role inheritance must not silently bypass separation-of-duties constraints."),
    ("Rick Kuhn", "authority", "nist-rbac", "Use formal RBAC constraints and conformance criteria.", "A model-conformant engine can still enforce the wrong policy."),
    ("Ruoming Pang", "authority", "google-zanzibar", "Evaluate relationship authorization against causally consistent ACL snapshots.", "Zanzibar-style tuples do not establish who may author the relation."),
    ("Lea Kissner", "authority", "google-zanzibar", "Treat authorization consistency as a privacy and user-intent property.", "Global scale is not a reason to import provider-specific semantics."),
    ("Mike Burrows", "authority", "google-zanzibar", "Separate relation schema, stored tuples, evaluation and consistency tokens.", "A check response still needs an enforcement point."),
    ("Justin Richer", "authority", "ietf-rfc9635", "Model negotiated authorization grants, continuation and client instance state.", "Protocol possession does not grant semantic authority outside the negotiated scope."),
    ("Steve Zdancewic", "authority", "cedar-paper", "Design authorization languages with analyzable semantics and validation.", "Static policy validation does not prove correct authoring authority or runtime attributes."),
    ("Judea Pearl", "decision", "pearl-causality", "Represent intervention semantics and distinguish observation from causal effect.", "A DAG supplied without defensible identification assumptions is not causal proof."),
    ("Donald Rubin", "decision", "rubin-causal", "Define causal effects through potential outcomes and assignment mechanisms.", "Only one potential outcome is observed per unit; assumptions remain explicit."),
    ("Herbert Robbins", "decision", "robbins-bandit", "Treat sequential learning as an exploration/exploitation decision problem.", "Regret objectives do not automatically satisfy safety or effect authority."),
    ("Karl Åström", "decision", "control-feedback", "Model state, feedback, stability, observability and control separately.", "A stable controller can optimize the wrong outcome or violate constraints."),
    ("Richard Murray", "decision", "control-feedback", "Make plant, controller, sensor, disturbance and closed-loop assumptions explicit.", "A simulation result does not qualify a production plant occurrence."),
    ("Barbara von Halle", "decision", "omg-dmn", "Separate decision requirements from decision logic and reusable knowledge.", "Executable decision tables do not grant action authority."),
    ("Paul Vincent", "decision", "omg-dmn", "Compose business decisions with explicit inputs and knowledge requirements.", "Predictive models remain inputs or invocable knowledge, not decisions by themselves."),
    ("Bruce Silver", "decision", "omg-dmn", "Use hit policies and FEEL semantics precisely enough for conformance testing.", "Diagram readability is not semantic conformance."),
]


LIBRARIES = {
    "intent": ["intent-vocabulary", "goal-refinement", "assumption-falsifier", "constraint-algebra", "requirement-graph", "acceptance-predicate", "verification-receipt", "quality-attribute", "scope-boundary", "intent-conformance"],
    "identity": ["scoped-identifier", "namespace-registry", "identifier-parser", "resolver-contract", "identity-claim", "entity-resolution", "merge-split-ledger", "version-identity", "canonicalization", "identity-conformance"],
    "time": ["instant-core", "interval-algebra", "duration-core", "calendar-period", "timezone-adapter", "recurrence", "business-calendar", "bitemporal-ledger", "causal-clock", "temporal-conformance"],
    "quantity": ["quantity-core", "dimension-algebra", "unit-registry", "scale-types", "money-core", "ratio-rate", "probability-core", "uncertainty-propagation", "partial-information", "quantity-conformance"],
    "authority": ["authority-scope", "delegation-graph", "entitlement", "approval-ledger", "issuance", "revocation", "policy-algebra", "policy-decision", "enforcement-port", "authority-conformance"],
    "decision": ["decision-contract", "decision-table", "judgment-port", "decision-ledger", "action-proposal", "action-authorizer", "effect-port", "feedback-loop", "compensation", "decision-conformance"],
}

# This is semantic classification, not package placement.  The previous positional
# pure/runtime/adapter/test cycle made a library's class depend on list order.
CSP_LIBRARY_CLASS = {
    "intent-vocabulary": "semantic_pure", "goal-refinement": "algorithm_pure",
    "assumption-falsifier": "test_oracle", "constraint-algebra": "algorithm_pure",
    "requirement-graph": "semantic_pure", "acceptance-predicate": "policy_pure",
    "verification-receipt": "semantic_pure", "quality-attribute": "semantic_pure",
    "scope-boundary": "semantic_pure", "intent-conformance": "test_oracle",
    "scoped-identifier": "semantic_pure", "namespace-registry": "semantic_pure",
    "identifier-parser": "algorithm_pure", "resolver-contract": "effect_port_contract",
    "identity-claim": "semantic_pure", "entity-resolution": "algorithm_pure",
    "merge-split-ledger": "policy_pure", "version-identity": "semantic_pure",
    "canonicalization": "algorithm_pure", "identity-conformance": "test_oracle",
    "instant-core": "semantic_pure", "interval-algebra": "algorithm_pure",
    "duration-core": "semantic_pure", "calendar-period": "semantic_pure",
    "timezone-adapter": "provider_adapter", "recurrence": "algorithm_pure",
    "business-calendar": "policy_pure", "bitemporal-ledger": "policy_pure",
    "causal-clock": "algorithm_pure", "temporal-conformance": "test_oracle",
    "quantity-core": "semantic_pure", "dimension-algebra": "algorithm_pure",
    "unit-registry": "semantic_pure", "scale-types": "semantic_pure",
    "money-core": "semantic_pure", "ratio-rate": "semantic_pure",
    "probability-core": "semantic_pure", "uncertainty-propagation": "algorithm_pure",
    "partial-information": "semantic_pure", "quantity-conformance": "test_oracle",
    "authority-scope": "semantic_pure", "delegation-graph": "policy_pure",
    "entitlement": "semantic_pure", "approval-ledger": "policy_pure",
    "issuance": "policy_pure", "revocation": "policy_pure",
    "policy-algebra": "algorithm_pure", "policy-decision": "policy_pure",
    "enforcement-port": "effect_port_contract", "authority-conformance": "test_oracle",
    "decision-contract": "semantic_pure", "decision-table": "algorithm_pure",
    "judgment-port": "effect_port_contract", "decision-ledger": "policy_pure",
    "action-proposal": "semantic_pure", "action-authorizer": "policy_pure",
    "effect-port": "effect_port_contract", "feedback-loop": "policy_pure",
    "compensation": "policy_pure", "decision-conformance": "test_oracle",
}

CSP_CLASS_LAYER = {
    "semantic_pure": "pure", "algorithm_pure": "pure", "policy_pure": "pure",
    "effect_port_contract": "runtime", "provider_adapter": "adapter", "test_oracle": "test",
}

CSP_CLASS_EFFECT = {
    "semantic_pure": "pure_no_io", "algorithm_pure": "pure_no_io",
    "policy_pure": "pure_no_io", "effect_port_contract": "pure_effect_intents",
    "provider_adapter": "effectful_runtime", "test_oracle": "pure_no_io",
}


RUST_PATTERNS = [
    ("newtype", "Use opaque tuple structs for scoped identifiers, quantities and policy IDs; construction validates syntax but not external truth."),
    ("enum", "Use exhaustive enums for closed local states such as four-valued policy results; use open tagged records across published boundaries."),
    ("typestate", "Encode lifecycle prerequisites such as Draft→Approved→Issued without claiming distributed effects are atomic."),
    ("trait", "Model provider-neutral ports such as Resolver, Clock, UnitRegistry, PolicyEvaluator and EffectExecutor."),
    ("associated_type", "Keep domain-specific identifier, error and receipt types coupled to a port implementation."),
    ("phantom_data", "Carry compile-time unit, namespace, time-scale or authority-scope markers where the set is build-time closed."),
    ("result", "Represent legitimate refusals as typed errors rather than panics or booleans."),
    ("option", "Use Option only for true optionality; missing, unknown, censored and withheld require explicit enums."),
    ("non_exhaustive", "Preserve forward compatibility for public refusal and status catalogs."),
    ("serde_boundary", "Deserialize into DTOs first; validate and translate through an anti-corruption layer before constructing domain types."),
]


VERTICALS = [
    {
        "id": "acute-care-medication-titration", "industry": "acute_care", "intent": "Keep a measured physiological variable within a clinician-declared target band.",
        "chain": ["authorized target", "time-qualified observations", "quantity/unit validation", "decision recommendation", "clinician decision", "separate action authorization", "administration action", "effect observation", "outcome review"],
        "negative_twin": "Treating a model recommendation as an issued medication order and a later correlated observation as proof of treatment effect.",
    },
    {
        "id": "power-grid-demand-response", "industry": "electric_power", "intent": "Reduce a verified load during a declared grid event without violating customer or equipment constraints.",
        "chain": ["authorized event identity", "valid event interval", "meter quantity semantics", "baseline and uncertainty", "dispatch decision", "resource action", "telemetry observation", "counterfactual effect estimate", "settlement acceptance"],
        "negative_twin": "Equating receipt of a dispatch message with curtailed load or treating a raw watt value without interval and unit as settlement evidence.",
    },
]


def source_rows() -> list[dict[str, Any]]:
    return [{
        "id": f"source.csp.{key}", "status": "reference", "title": title,
        "publisher": publisher, "source_kind": kind, "url": url, "year": year,
        "family_refs": families, "authority_scope": scope, "accessed": ACCESSED,
    } for key, title, publisher, kind, url, year, families, scope in SOURCES]


def context_rows() -> list[dict[str, Any]]:
    rows = []
    for family, spec in FAMILIES.items():
        evidence = [f"source.csp.{key}" for key in spec["source_keys"]]
        for name in spec["contexts"]:
            rows.append({
                "id": f"context.csp.{family}.{name}", "status": "candidate", "kind": "bounded_context",
                "family": family, "name": name, "vision": f"Own the semantic and lifecycle decisions for {name.replace('-', ' ')}.",
                "in_scope": ["ubiquitous language", "value semantics", "lifecycle", "invariants", "refusals", "published contract"],
                "out_of_scope": ["provider selection", "UI workflow", "legal conclusion", "unqualified external effect"],
                "neighbor_family_refs": spec["neighbors"], "constitution": spec["constitution"],
                "evidence_refs": evidence,
            })
    return rows


def semantic_rows(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for context in contexts:
        family = context["family"]
        local = context["name"]
        spec = FAMILIES[family]
        evidence = context["evidence_refs"]
        for suffix in spec["type_pair"]:
            rows.append({
                "id": f"semantic.csp.{family}.{local}.type.{slug(suffix)}", "status": "candidate", "kind": "type",
                "family": family, "context_ref": context["id"], "name": f"{local.replace('-', '_')}_{slug(suffix).replace('-', '_')}",
                "signature": {"carrier": "opaque semantic record", "required_qualifiers": ["scope", "version", "validity", "authority"]},
                "refusal": "construction refuses missing qualifiers or invalid local representation",
                "evidence_refs": evidence,
            })
        for operation in spec["operations"]:
            rows.append({
                "id": f"semantic.csp.{family}.{local}.operation.{operation}", "status": "candidate", "kind": "operation",
                "family": family, "context_ref": context["id"], "name": f"{operation}_{local.replace('-', '_')}",
                "signature": {"input": f"qualified {local.replace('-', ' ')} request", "output": "typed outcome or typed refusal", "effects": "none unless explicitly marked runtime"},
                "refusal": "refuse ambiguity, absent authority, invalid lifecycle state, unsupported representation or lost qualifier",
                "evidence_refs": evidence,
            })
        for decision in spec["decisions"]:
            rows.append({
                "id": f"semantic.csp.{family}.{local}.decision.{decision}", "status": "candidate", "kind": "decision",
                "family": family, "context_ref": context["id"], "name": f"{decision}_{local.replace('-', '_')}",
                "signature": {"inputs": ["intent", "policy", "risk", "available evidence"], "output": "versioned selected policy"},
                "refusal": "no silent default when alternatives change observable semantics",
                "evidence_refs": evidence,
            })
        rows.append({
            "id": f"semantic.csp.{family}.{local}.law.qualifier-preservation", "status": "candidate", "kind": "law",
            "family": family, "context_ref": context["id"], "name": f"{local.replace('-', '_')}_qualifier_preservation",
            "signature": {"oracle": "round-trip and cross-boundary transformations preserve declared scope, time, authority and information-state qualifiers"},
            "refusal": "transformation is invalid when semantic loss is undeclared",
            "evidence_refs": evidence,
        })
    for index, (family, left, right, law) in enumerate(DISTINCTIONS, 1):
        rows.append({
            "id": f"semantic.csp.{family}.distinction.{index:03d}", "status": "candidate", "kind": "law",
            "family": family, "context_ref": next(row["id"] for row in contexts if row["family"] == family),
            "name": f"{left}_not_{right}", "left": left, "right": right,
            "signature": {"oracle": law}, "refusal": f"compiler refuses implicit coercion from {left} to {right}",
            "evidence_refs": next(row["evidence_refs"] for row in contexts if row["family"] == family),
        })
    return rows


def rule_rows(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for context in contexts:
        family, local = context["family"], context["name"]
        rows.extend([
            {"id": f"rule.csp.{family}.{local}.construct", "status": "candidate", "kind": "invariant_refusal", "family": family, "context_ref": context["id"], "name": "qualified_construction", "invariant": "Every value has an explicit scope and semantic edition; time and authority qualifiers are required whenever they can change interpretation.", "refusal": "invalid, ambiguous or unqualified values are refused at construction", "evidence_refs": context["evidence_refs"]},
            {"id": f"rule.csp.{family}.{local}.boundary", "status": "candidate", "kind": "invariant_refusal", "family": family, "context_ref": context["id"], "name": "boundary_preservation", "invariant": "Foreign representations remain DTOs until a declared anti-corruption translation succeeds.", "refusal": "unknown edition, lossy conversion or undeclared default yields a typed boundary refusal", "evidence_refs": context["evidence_refs"]},
        ])
    return rows


def lifecycle_rows() -> list[dict[str, Any]]:
    definitions = {
        "intent": ["proposed", "challenged", "authorized", "active", "satisfied", "failed", "withdrawn"],
        "identity": ["proposed", "assigned", "active", "superseded", "deactivated", "tombstoned"],
        "time": ["unresolved", "qualified", "normalized", "ambiguous", "corrected"],
        "quantity": ["raw", "qualified", "validated", "converted", "rounded", "reported", "corrected"],
        "authority": ["draft", "approved", "issued", "active", "suspended", "revoked", "expired"],
        "decision": ["requested", "evidence_ready", "decided", "action_proposed", "authorized", "executed", "effect_observed", "reviewed", "appealed"],
    }
    rows = []
    for family, states in definitions.items():
        for variant in ["semantic_artifact", "runtime_occurrence", "published_contract", "correction"]:
            rows.append({
                "id": f"lifecycle.csp.{family}.{variant}", "status": "candidate", "kind": "lifecycle", "family": family,
                "name": f"{family}_{variant}", "states": states,
                "transition_law": "Only named transitions are legal; correction appends a superseding fact rather than rewriting observed history.",
                "refusal": "wrong prior state, stale version, missing authority, duplicate effect or expired validity",
                "evidence_refs": [f"source.csp.{key}" for key in FAMILIES[family]["source_keys"]],
            })
    return rows


def acl_rows() -> list[dict[str, Any]]:
    rows = []
    for family, spec in FAMILIES.items():
        for neighbor in spec["neighbors"]:
            rows.append({
                "id": f"acl.csp.{family}.to.{neighbor}", "status": "candidate", "kind": "anti_corruption_layer",
                "family": family, "name": f"{family}_to_{neighbor}", "upstream": family, "downstream": neighbor,
                "translation_laws": ["preserve source edition and authority", "preserve partiality and refusal", "never infer omitted qualifiers", "emit explicit semantic-loss receipt"],
                "refusal": "unknown version, ambiguous term, incompatible equality, time or authority semantics",
                "evidence_refs": [f"source.csp.{key}" for key in spec["source_keys"]],
            })
    return rows


def compiler_rows(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for context in contexts:
        family, local = context["family"], context["name"]
        base = f"compiler.csp.{family}.{local}"
        common = {"status": "candidate", "family": family, "context_ref": context["id"], "evidence_refs": context["evidence_refs"]}
        rows.extend([
            {**common, "id": f"{base}.requirement", "kind": "compiler_requirement", "name": f"require_{local}", "contract": {"requires": ["semantic edition", "scope", "authority", "time model", "equality/canonicalization", "refusal policy"], "forbids": ["implicit default", "provider-name semantics"]}},
            {**common, "id": f"{base}.offer", "kind": "capability_offer", "name": f"offer_{local}", "contract": {"guarantees": ["typed construction", "deterministic evaluation", "explicit partiality", "versioned representation"], "limits": ["no external truth claim", "no provider qualification"]}},
            {**common, "id": f"{base}.mapping", "kind": "compiler_mapping", "name": f"bind_{local}", "contract": {"bind_when": ["semantic identity matches", "all required qualifiers supplied", "refusal preserved", "proof obligations discharged"], "otherwise": "refuse or request an authorized degradation"}},
            {**common, "id": f"{base}.proof", "kind": "proof_obligation", "name": f"prove_{local}", "contract": {"obligations": ["input totality", "round-trip law", "equality soundness", "time/authority freshness", "idempotency where effectful", "negative twin rejected"], "evidence": "compiler receipt plus conformance oracle"}},
        ])
    return rows


def library_rows() -> list[dict[str, Any]]:
    rows = []
    declared_names = {name for names in LIBRARIES.values() for name in names}
    if declared_names != set(CSP_LIBRARY_CLASS):
        raise ValueError("Every CSP library must have exactly one explicit semantic class")
    for family, names in LIBRARIES.items():
        for name in names:
            library_class = CSP_LIBRARY_CLASS[name]
            rows.append({
                "id": f"library.csp.{family}.{name}", "status": "candidate", "kind": "library_boundary", "family": family,
                "name": name, "layer": CSP_CLASS_LAYER[library_class], "library_kind": library_class,
                "effect_boundary": CSP_CLASS_EFFECT[library_class],
                "owns": [f"{name} vocabulary", f"{name} invariants", f"{name} typed refusals"],
                "does_not_own": ["application orchestration", "provider selection", "foreign DTO semantics", "legal conclusion"],
                "decision_points": ["edition", "equality", "canonical representation", "time policy", "partiality", "failure mapping"],
                "composition_contract": {"requires": "versioned semantic inputs", "offers": "typed deterministic result and proof/test oracle"},
                "evidence_refs": [f"source.csp.{key}" for key in FAMILIES[family]["source_keys"]],
            })
    return rows


def rust_rows() -> list[dict[str, Any]]:
    rows = []
    for family in FAMILIES:
        for feature, use in RUST_PATTERNS[:6]:
            rows.append({
                "id": f"rust.csp.{family}.{feature}", "status": "candidate", "kind": "rust_applicability", "family": family,
                "feature": feature, "applicability": use,
                "boundary_law": "Rust encodes a selected semantic contract; Rust type identity is not the domain source of truth.",
                "anti_pattern": "Do not expose serde wire structs, provider SDK types, global singletons or catch-all strings as the domain model.",
            })
    return rows


def innovation_rows() -> list[dict[str, Any]]:
    return [{
        "id": f"innovation.csp.{year}.{slug(title)}", "status": "candidate", "kind": "innovation", "year": year,
        "name": title, "description": description, "limit": limit, "non_llm": True,
        "evidence_refs": [f"source.csp.{source}"],
    } for year, title, source, description, limit in INNOVATIONS]


def expert_rows() -> list[dict[str, Any]]:
    return [{
        "id": f"expert.csp.{slug(name)}.{family}", "status": "candidate", "kind": "expert_learning_route",
        "name": name, "family": family, "learn": learn, "misuse_warning": warning,
        "artifact_refs": [f"source.csp.{source}"], "evidence_refs": [f"source.csp.{source}"],
        "authority_law": "The cited artifact supports the learning claim; reputation alone is never compiler evidence.",
    } for name, family, source, learn, warning in EXPERTS]


def gap_rows() -> list[dict[str, Any]]:
    gaps = [
        ("intent", "conflicting stakeholder outcomes need authorized precedence and harm review"),
        ("intent", "acceptance oracles for qualitative outcomes remain vertical-specific"),
        ("intent", "intent amendments with in-flight actions need disposition rules"),
        ("identity", "cross-domain entity resolution has no universal ground truth"),
        ("identity", "merge/split reversibility and downstream propagation remain application-specific"),
        ("identity", "identifier privacy risks depend on linkability across relying contexts"),
        ("time", "clock trust, leap-second handling and zone-database version pinning need deployment qualification"),
        ("time", "retroactive corrections across distributed replicas need conflict policy"),
        ("time", "uncertain and approximate time arithmetic is not closed across standards"),
        ("quantity", "currency redenomination and valuation policy are not pure unit conversion"),
        ("quantity", "missingness mechanism is generally not identifiable from observed data alone"),
        ("quantity", "uncertainty propagation across correlated opaque services needs evidence"),
        ("authority", "authority-source conflicts cannot be globally ordered without domain constitution"),
        ("authority", "revocation latency across offline caches requires bounded occurrence evidence"),
        ("authority", "break-glass authority needs domain-specific aftercare and review"),
        ("decision", "causal attribution needs explicit study design and cannot be inferred from telemetry"),
        ("decision", "irreversible action compensation is domain-specific"),
        ("decision", "human override quality and appeal policy need contextual governance"),
    ]
    return [{
        "id": f"gap.csp.{family}.{idx:02d}", "status": "candidate", "kind": "gap", "family": family,
        "name": slug(text), "description": text, "compiler_posture": "block binding or require an explicit authorized degradation with residual owner",
        "evidence_refs": [f"source.csp.{key}" for key in FAMILIES[family]["source_keys"]],
    } for idx, (family, text) in enumerate(gaps, 1)]


def main() -> None:
    sources = source_rows()
    contexts = context_rows()
    semantic = semantic_rows(contexts)
    rules = rule_rows(contexts)
    lifecycles = lifecycle_rows()
    acls = acl_rows()
    compiler = compiler_rows(contexts)
    libraries = library_rows()
    rust = rust_rows()
    innovations = innovation_rows()
    experts = expert_rows()
    verticals = [{**row, "status": "candidate", "kind": "vertical_example"} for row in VERTICALS]
    gaps = gap_rows()

    outputs = {
        "sources.jsonl": sources,
        "bounded-contexts.jsonl": contexts,
        "semantic-records.jsonl": semantic,
        "invariants-refusals.jsonl": rules,
        "lifecycles.jsonl": lifecycles,
        "context-acls.jsonl": acls,
        "compiler-contracts.jsonl": compiler,
        "library-boundaries.jsonl": libraries,
        "rust-applicability.jsonl": rust,
        "innovations-2021-2026.jsonl": innovations,
        "experts.jsonl": experts,
        "vertical-examples.jsonl": verticals,
        "gaps.jsonl": gaps,
    }
    for name, rows in outputs.items():
        write_jsonl(name, rows)

    metamodel = {
        "id": "metamodel.core-semantic-primitives.edition-1", "status": "candidate", "edition": EDITION,
        "completion_claim": False, "families": [{"id": key, **{k: value for k, value in spec.items() if k in {"title", "vision", "neighbors", "constitution"}}} for key, spec in FAMILIES.items()],
        "non_collapsible_distinctions": [{"family": f, "left": l, "right": r, "law": law} for f, l, r, law in DISTINCTIONS],
        "representation_stack": ["domain meaning", "semantic carrier", "validated value", "canonical representation", "wire DTO", "provider occurrence"],
        "equality_stack": ["lexical equality", "canonical representation equality", "value equality", "domain equivalence claim", "resolved co-reference", "historical continuity"],
        "compiler_flow": ["intent", "requirements", "semantic binding", "policy/authority binding", "proof obligations", "IR", "provider offer qualification", "execution", "receipts", "effect/outcome review"],
    }
    write_json("metamodel.json", metamodel)

    generated = sorted(outputs) + ["metamodel.json"]
    counts = {
        "sources": len(sources), "bounded_contexts": len(contexts), "semantic_records": len(semantic),
        "invariants_refusals": len(rules), "lifecycles": len(lifecycles), "context_acls": len(acls),
        "compiler_contracts": len(compiler), "library_boundaries": len(libraries),
        "rust_applicability": len(rust), "innovations_2021_2026": len(innovations),
        "expert_learning_routes": len(experts),
        "vertical_examples": len(verticals), "gaps": len(gaps),
    }
    manifest = {
        "id": "manifest.core-semantic-primitives.edition-1", "status": "candidate", "completion_claim": False,
        "edition": EDITION, "generated_files": generated, "counts": counts,
        "sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in generated},
    }
    write_json("manifest.json", manifest)


if __name__ == "__main__":
    main()
