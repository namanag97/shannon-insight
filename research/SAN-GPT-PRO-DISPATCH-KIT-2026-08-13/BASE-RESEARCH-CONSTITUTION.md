# Base research constitution

## Intent

Establish a globally defensible, machine-readable map of the semantic domains,
technical mechanisms, libraries, compiler contributions, runtime bindings, and
industry/application compositions needed to declare an enterprise intent and obtain
a verifiable data-and-application solution.

This is a research and specification program. It is not permission to invent a
universal compiler, generate production code, or turn every noun into a library.

## Global research standard

Use current Internet research in addition to the attached corpus. Seek authoritative
and primary material across regions, industries, standards bodies, mature software
ecosystems, academic fields, and practitioner communities. Do not treat English-only,
US-only, vendor-only, cloud-only, or SAN-only evidence as global coverage. Include
contradictory and negative evidence. Record access dates, publication dates, stable
URLs, source authority, applicable jurisdiction or scope, and the exact claim each
source supports.

No count, label, archive, validator result, or confident prose establishes
completeness by itself. State what was searched, what coverage dimensions were
tested, what remains unknown, and why any stopping condition is reasonable. Never
claim “all”, “complete”, “canonical”, “globally correct”, “validated”, “executable”,
or “proved” beyond the attached evidence and the checks actually reproduced.

## Generality standard

Model stable questions, authorities, laws, decisions, and interfaces. Do not overfit
the result to one industry, vendor, database, language, deployment topology, example,
or current SAN package. Use examples as tests, not as the ontology. Preserve real
jurisdictional, organizational, temporal, physical, and provider variation as typed
profiles or explicit decision points; do not erase it under vague abstraction.

## Non-equivalence laws

Keep these things distinct unless evidence proves an exact identity:

```text
research source != source-supported claim != adjudicated proposition
proposition != semantic owner != bounded context != capability
bounded context != profile != composition != product/application package
semantic library != effect/mechanism library != provider adapter
library specification != crate/package != implementation
compiler contribution != compiler stage != portable IR != target artifact
portable intent != physical provider selection != runtime observation
schema-valid != referentially closed != semantically adequate != executable
tested != independently audited != ratified != certified
```

A bounded context may yield zero, one, or several libraries. A library may contain
several modules. A crate or package is a packaging decision, not automatically a
semantic boundary. Industry is ordinarily a vertical profile and composition axis,
not a reason to duplicate horizontal semantics.

## Epistemic states

Every material record and conclusion must carry one of these postures with evidence:

```text
hypothesis
discovered_candidate
source_supported
boundary_qualified
adjudicated
specified
implemented
structurally_verified
semantically_verified
compiler_integrated
runtime_observed
independently_audited
ratified
certified
rejected
superseded
```

No session may silently promote a record to a stronger state.

## Required qualities of eventual libraries

The research must make it possible to decide whether an eventual unit is:

- semantically owned and bounded;
- pure at the semantic core, with effects behind explicit ports;
- deterministic for equal declared inputs or explicit about controlled nondeterminism;
- composable without hidden global state or family-name branching;
- customizable through finite, typed, enumerable decision coordinates;
- closed under documented invariants and refusal semantics;
- provider-, storage-, transport-, UI-, and deployment-independent where those concerns
  are not its authority;
- serializable and versioned at every public contract boundary;
- inspectable, explainable, testable, migration-aware, and provenance-preserving;
- capable of contributing requirements, offers, constraints, decisions, diagnostics,
  artifacts, and proof obligations to a generic compiler;
- usable in both positive and negative compositions without silently guessing.

These are evaluation criteria, not an instruction to declare every candidate admissible.

## Deliverable standard

Return a deterministic ZIP containing machine-readable source records, schemas,
closed vocabularies, evidence and conflict ledgers, generated indexes, human-readable
navigation, a manifest, checksums, and an executable validator. The validator must
reproduce every reported structural count and check schema closure, identifiers,
references, allowed states, ordering, duplicates, cycles where forbidden, evidence
requirements, and checksums. Report semantic or completeness claims separately from
mechanical validation.

The final response must state the archive name and digest; record counts by kind;
validation actually run; material conflicts, rejected candidates, unresolved gaps;
and the next admissible DAG transition. Do not substitute a prose essay for the
requested corpus.

