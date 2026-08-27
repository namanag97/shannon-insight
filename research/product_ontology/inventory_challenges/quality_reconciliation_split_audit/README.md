# Quality/reconciliation product split audit

Status: **canonical split promoted; both replacement products remain unratified**.

The dedicated quality universe falsifies the current combined `Data Quality and Reconciliation`
product. Quality operations ask whether an exact cut satisfies named requirements and is fit for a
purpose. Reconciliation/control operations compare identified populations under explicit truth
roles, matching, tolerance and materiality rules and then manage breaks. These are different
semantic, authority and lifecycle boundaries.

```text
                    current overloaded candidate
                 Data Quality + Reconciliation
                              |
                 split required by exact semantics
                   /                         \
                  v                           v
 Data Quality Operations                   Reconciliation & Control Operations
 requirement / rule / validation          populations / truth roles / matching
 profile / baseline / signals             tolerance / run / break / materiality
 fitness / case / quarantine              disposition / adjustment proposal
 waiver / remediation / release           bounded control completion
```

The four current vertical pilots independently support the split. All four select quality fitness,
completeness, schema-conformance, validation and evidence libraries. Only retail tender/cash
reconciliation selects reconciliation definition, execution, break and accounting-control
libraries. The remap is therefore derived from exact libraries, not from the word “reconciliation”
inside a case name.

All 37 QOR library candidates receive one explicit disposition. Generic data-contract, master-data
and entity-resolution meanings remain imported from their existing products. Accounting/control
reconciliation remains a vertical specialization of the horizontal reconciliation product rather
than making finance vocabulary global. Correction execution remains an external-authority effect
port. Models and agents may propose matches or explanations but cannot adjudicate defects, breaks
or corrections.

Build and validate:

```bash
python3 research/product_ontology/inventory_challenges/quality_reconciliation_split_audit/build_audit.py
python3 research/product_ontology/inventory_challenges/quality_reconciliation_split_audit/validate.py
python3 research/product_ontology/inventory_challenges/quality_reconciliation_split_audit/build_audit.py --check
```

The split has now been promoted through the canonical global corpus. Both products have complete
29-field DDD dossiers, product-specific QOR library attribution and exact structural compiler maps;
the old combined candidate is removed and all four vertical compositions are regenerated. This is
still not product ratification: provider qualification, two-implementation portability and executed
domain acceptance remain blocking.
