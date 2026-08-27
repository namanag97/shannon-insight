# Declaration and reference closure

This candidate universe closes three exact library gaps without collapsing adjacent semantics:

- `library.api.contract_parser` compiles an exact dialect document into interface-contract IR;
- `library.provider_offer.reference_closure` closes offer, interface, capability, evidence and validity references without qualifying a provider;
- `library.package.reference_closure` closes manifest, constraint, resolver, lock, feature, scope and target-qualified package references without claiming a build.

Query compilation is not duplicated: transformation definitions compose the existing
`library.qck.query-syntax` and `library.qck.query-binding` contracts. Schema reference closure
remains owned by `library.schema_registry.reference_closure`. Interface, provider-offer, schema,
package, build-unit, SBOM and runtime-load graphs are different artifacts.

All three libraries are pure, specified and unimplemented. Network retrieval, probing, package
download, provider qualification, build execution, authorization and effects remain outside.

Rebuild and validate:

```sh
python3 research/domain_atlas/universes/declaration_reference_closure/build_corpus.py
python3 research/domain_atlas/universes/declaration_reference_closure/validate_corpus.py
```
