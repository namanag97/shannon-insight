# P6 implementation and qualification hypergraph

This layer answers a different question from P5: given an exact semantic contract candidate, what
implementation identity, evidence and acceptance must exist before the compiler may select it?

It projects 630 concrete references and 470 qualification subjects into 457 exact qualification
scopes. Sharing is allowed only when the abstract contract, contract digest, concrete references,
effect boundary, conformance contexts and evidence classes are identical. Each scope has two
independent implementation slots, giving 914 slots without fabricating implementation offers.

The outputs preserve four distinct resolution states: an open P5 exact contract, a registered but
unimplemented specification, an unadjudicated registry candidate, and an unregistered concrete
reference. None is equivalent to a qualified implementation.

The 814 existing evidence vacancies are factored into 14 gate packages. This shares evidence
methods and fixtures across products while keeping every receipt attributable to its exact product,
implementation, scope and gate. The complete 16-gate/17-edge qualification DAG remains explicit.

Every one of the 470 compiler-selection gates refuses. All 59 product dockets remain blocked and
retain their exact subject set, gate states, vacancies and two unrelated vertical-acceptance slots.
P6 therefore provides deterministic compiler inputs and refusal reasons; it makes no qualification,
provider, portability, build-readiness or canonical-completion claim.

Run:

```sh
python3 build_p6.py
python3 validate.py
```
