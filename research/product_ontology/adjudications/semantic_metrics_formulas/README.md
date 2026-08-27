# Semantic Metric and Formula Product Adjudication

This candidate corpus retains one horizontal product: **Semantic Metric and Formula Service**.
It rejects “semantic layer,” “headless BI,” “metric store,” formula engine, semantic registry,
semantic query gateway, observation ledger and materialization cache as additional products unless
new independent adoption, support, economics and exit evidence changes the boundary.

```text
business/vertical owners             horizontal semantic product
-------------------------            ---------------------------
terms + concepts --------ACL-------> semantic model editions
source facts ------------ACL-------> measures + dimensions + grain
targets/thresholds ------pack-------> metrics + typed formulas
policy ------------------port-------> purpose-bound semantic query
                                            |
             parse -> type -> bind -> prove fanout/summarizability
                                            |
                                lower to replaceable query engine
                                            |
                                  value | error + exact receipt
                                            |
                    observation ledger / materialization / disclosure

formula expression != definition != binding != evaluation
measure != metric != KPI != target != benchmark != observation
semantic query != SQL; cache reuse requires semantic + policy proof
```

The product owns governed definition and evaluation semantics. It imports business terminology,
source facts, query execution, use policy, presentation and vertical thresholds. Its 24 library
contracts carry exact product attribution and map one-to-one to the existing `library.smf.*`
compiler registry. The product also has a complete candidate 29-field strategic/tactical DDD
dossier. Structural projection is complete, but every offer remains unqualified and 16
semantic/conformance gaps remain blocking.

Models and agents may propose a formula, mapping or explanation only when intent selects that
extension. Removing all such extensions leaves deterministic parsing, typing, binding, proof,
policy, lowering, execution and receipts unchanged.

```bash
python3 research/product_ontology/adjudications/semantic_metrics_formulas/build_bundle.py
python3 research/product_ontology/adjudications/semantic_metrics_formulas/validate.py
python3 research/product_ontology/adjudications/semantic_metrics_formulas/build_bundle.py --check
```
