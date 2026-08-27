# Security, privacy, and trust universe

Status: evidence-backed research candidates; no record is adjudicated and no completeness claim is made.

This package models the horizontal security, privacy, data-use governance, identity/authority,
assurance, and incident-evidence contracts needed by a provider-neutral data and analytics platform.
Its boundary is the platform's ability to compile declared intent into typed requirements, qualify
implementation offers, enforce data actions, and preserve evidence. It deliberately does not decide
which law applies, give legal advice, replace an organization's risk authority, or model every
enterprise-security function.

Generative-model methods are excluded from the core universe. They may be consumers or governed
workloads in a future neighbor mapping, but they are neither the organizing method nor a hidden
dependency here.

```text
external authority / legal interpretation / enterprise risk ownership
                              |
                              | approved bounded obligations, policy, risk acceptance
                              v
+--------------------- SECURITY / PRIVACY / TRUST PLATFORM --------------------+
|                                                                               |
| principal --authenticate--> session        relationship/attributes            |
|     |                          |                       |                       |
|     +--------------------------+-----------> policy decision                  |
|                                                        |                      |
| approval -----------------> issuance                   | receipt              |
|                               |                        v                      |
| credential/token --------> enforcement ----------> authorized data effect     |
|                                                        |                      |
| purpose + permission + classification + locality + retention                  |
|                       |                                |                      |
|                       +-------- compile/gate ----------+                      |
|                                                        |                      |
| source -> typed pipeline -> protected persistence -> governed consumption     |
|    |            |                  |                       |                  |
|    +------------+------- lineage --+--------- disclosure --+                  |
|                             |                                                 |
| audit observations     provenance assertions     attestations/transparency    |
|         |                       |                        |                    |
|         +-----------------------+----------- incident evidence                |
|                                                                               |
| de-identification / differential privacy / secure computation / clean room    |
+-------------------------------------------------------------------------------+
      |                    |                      |                    |
 identity provider   crypto/key provider   compute/storage runtime   legal system
      |                    |                      |                    |
 explicit neighbor   qualified offer       explicit neighbor         out of scope
```

## Sovereign distinctions

| Concept | Owns | Must not be substituted by |
|---|---|---|
| authentication | confidence that a claimant controls or is bound to a principal | authorization to perform a data action |
| authorization | a principal/action/resource/context policy result | authentication success or data encryption |
| data-use policy | purpose, recipient, operation, location, time and output constraints | security classification alone |
| approval | an authority's decision that issuance may proceed | the issued credential, token, lease or capability |
| issuance | creation of scoped authority or a protected artifact | enforcement at the eventual effect boundary |
| encryption | confidentiality/integrity transformation under cryptographic keys | permission to decrypt or use plaintext |
| pseudonymization | reduced direct attribution while additional information can restore attribution | an anonymity claim |
| anonymization | a release-context risk claim under an explicit attacker model | deletion, masking, tokenization or pseudonymization alone |
| privacy purpose | why a data action is undertaken and whether uses are compatible | how damaging unauthorized disclosure might be |
| security classification | confidentiality/integrity handling sensitivity | legal basis, consent or processing purpose |
| policy decision | permit/deny/indeterminate plus obligations under named facts and policy | proof that all effect paths enforced it |
| policy enforcement | mediation of a concrete effect and execution of obligations | policy authorship or identity proofing |
| audit log | normalized observations of security-relevant activity | causal provenance, completeness proof or semantic truth |
| provenance/evidence | assertions and verification artifacts about derivation, subjects and processes | an exhaustive activity log |
| legal obligation | an external normative requirement interpreted by competent authority | a directly executable platform rule |
| platform contract | a bounded, approved and testable lowering of obligation or policy | a claim that the original legal meaning is fully captured |

## Data-platform boundary and neighbors

In scope are source admission, type/shape labels, pipeline gates, encryption and isolation at
persistence, runtime identity and enforcement, governance decisions, lineage/evidence propagation,
consumer authorization and disclosure accounting. Each candidate record has an eight-surface
`cross_platform_map` covering `source_occurrences`, `types_shapes`, `pipelines`, `persistence`,
`runtime`, `governance`, `lineage`, and `consumption`.

Explicit neighbors are identity providers and authenticators, secret/key/cryptographic providers,
network and compute isolation, storage engines, policy engines, secure-computation runtimes,
software-supply-chain systems, organizational incident response, and competent legal/privacy
authorities. Neighbor capabilities enter compilation as qualified offers with versioned evidence;
product names and category labels are not proof.

Out of scope are deciding legal applicability, interpreting jurisdiction-specific exceptions,
general HR/facilities security, physical investigations, national-security classification policy,
payment fraud as a whole, safety engineering for non-data physical systems, provider procurement,
and claims that a control is effective without system-specific evidence.

## Compiler contract

1. Unknown identity, tenant, authority, purpose, policy, location, retention, key purpose or evidence
   semantics become typed gaps or refusals; the compiler never guesses.
2. Authentication, authorization, approval, issuance and enforcement remain separate artifacts and
   events with independently checkable identities.
3. Every authorization decision binds principal, action, resource, tenant, context facts, policy
   edition, decision time and obligations. Effectful operations additionally bind enforcement.
4. Encryption requirements name layer, suite, key purpose, custody and cryptoperiod. Encryption does
   not satisfy access-control or purpose-limitation requirements.
5. Every governed data action binds security classification and privacy purpose separately. A legal
   basis marker or consent artifact does not silently become a general-purpose permit.
6. Pseudonymized, de-identified and claimed-anonymous outputs have different types. An anonymity
   claim requires release context, attacker/auxiliary-data assumptions, metrics and accepting owner.
7. Differential-privacy output requires explicit privacy unit, adjacency, contribution bound,
   mechanism, parameters, accountant and atomic budget spend.
8. Secure computation and clean-room execution declare participant corruption assumptions, approved
   function, leakage, input admission and composed output controls. Attestation is not authorization.
9. Audit observations, provenance assertions, attestations, transparency proofs and incident
   evidence remain linked but distinct. Integrity never implies truth or completeness by itself.
10. Replays and backfills are new authorized runs over explicit cuts. Artifact identity, policy,
    source authority, retention, privacy budget and consumer disclosure rules are re-evaluated.

## Package contents

- `bounded-context-candidates.jsonl` — context boundaries, aggregates, commands, events, invariants
  and refusals.
- `assets-trust-boundaries.jsonl` — governed assets and the boundaries across which trust changes.
- `threat-abuse-cases.jsonl` — asset-bound abuse flows, impacts, detection evidence and mitigation
  classes.
- `capabilities.jsonl`, `operations.jsonl`, and `decisions.jsonl` — provider-neutral intent,
  typed effect candidates and decisions that must not become hidden defaults.
- `invariants-refusals.jsonl` — the semantic separation and fail-safe laws summarized above.
- `compiler-requirements.jsonl`, `capability-offers.jsonl`, and `compiler-mappings.jsonl` — intent to
  provider qualification surfaces. Offers remain unqualified templates.
- `library-boundaries.jsonl` — candidate pure/effectful implementation seams.
- `evidence.jsonl` — evidence shapes with integrity, freshness and explicit epistemic limits.
- `innovations.jsonl` — 2021–2026 non-generative-method developments with primary evidence.
- `sources.jsonl` — primary standards, authority guidance, primary law and original peer-reviewed
  research, each cited by candidate records and carrying source occurrences and limitations.
- `gaps.jsonl` — unresolved interoperability, assurance and semantic questions.
- `schemas/` — a JSON Schema for every JSONL registry.
- `coverage-report.json` — exact generated counts and an explicit false completion claim.
- `build_corpus.py` and `validate_corpus.py` — deterministic generation and structural,
  referential, coverage, canonical-serialization and method-boundary validation.

## Regeneration and validation

Run from the repository root:

```bash
python3 research/domain_atlas/universes/security_privacy_trust/build_corpus.py
python3 research/domain_atlas/universes/security_privacy_trust/validate_corpus.py
```

The validator requires at least 35 bounded contexts, 45 sources, 20 innovations dated 2021–2026,
and 140 combined capability/operation/threat/decision candidates. It validates exact generated
bytes, IDs, source references, context/asset/capability/operation/requirement references, candidate
status, all eight cross-platform surfaces, provider-neutral offer state, and the false completeness
claim without a third-party dependency.

## Honest completeness limits

This is an open-world seed, not a certification catalog. Candidate enumeration can be saturated
only relative to documented axes and a review window. Source authority does not establish that a
candidate boundary is correct, that a provider implements it, or that a control works in a specific
deployment. Original research demonstrates methods under stated assumptions, not universal
fitness. Primary legal text is included only to prevent platform vocabulary from erasing important
distinctions; qualified people must decide applicability and interpretation.

The corpus still needs split/merge adjudication, domain-owner review, mappings to at least two
unrelated data platforms, provider conformance suites, adversarial testing, jurisdiction/profile
extensions, recurring source freshness checks, and independent completeness review. `gaps.jsonl`
is therefore part of the deliverable, and `coverage-report.json` permanently makes the present
completion claim `false`.
