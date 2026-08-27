# P7 implementation-offer and physical-binding seam

P7 prevents a dangerous collapse:

```text
semantic capability != library implementation != physical runtime capability != provider offer
```

The current product corpus requires 474 semantic capability identifiers. The provider/target
registry contains 149 physical capability classes, 59 dated offers, 20 target occurrences and 25
qualification assessments. The identifier intersection is zero, by design. An implementation offer
must declare which exact semantic contract it implements and which physical requirements it needs;
the provider registry may then satisfy those declared physical requirements. Spelling or provider
name never creates that bridge.

P7 factors the 457 P6 qualification scopes into 118 profiles using only exact conformance-context,
evidence-class and effect-boundary equality. It also factors 7,883 subject-context obligations into
42 context workstreams. Methods, generators, fixtures and evidence schemas may be shared inside a
workstream; verdicts remain per implementation slot and exact scope.

Every one of the 914 independent implementation slots receives an empty typed offer-intake
template and a fail-closed semantic-to-physical binding gate. The intake requires exact contract,
artifact/source/build/dependency/configuration identities, provenance and SBOM references, physical
requirements, supported targets, conformance plans, invalidation triggers, validity and implementer
authority. No fields are inferred.

SLSA provenance, in-toto attestations and NIST SSDF are imported only as bounded evidence carriers
and control vocabularies. They do not own domain semantics and do not prove conformance,
qualification or product acceptance.

Run:

```sh
python3 build_p7.py
python3 validate.py
```
