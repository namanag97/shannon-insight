# Family source-authority audit

The 674 rich contract inputs originate from 23 family corpora. This audit binds each corpus to its
source and tree digests, builder, validator, schemas, manifest, evidence files, gap files and
README. Validator receipts are refreshed explicitly and bind the exact validator and immutable
tree it checked.

Control presence is separate from enforcement. The audit also records conservative static binding
signals showing whether the exact builder/validator source mentions schemas, manifests, evidence,
gaps and deterministic rebuild/drift behavior. These token signals are routing evidence only; they
cannot prove complete validator coverage.

A validator pass is not source authority. It proves only the rules encoded by that validator. The
decision schema separately requires named schema/record authorities, adopted and rejected fields,
transforms, conflicts, evidence and ratifiers before a source corpus can become canonical.

Run `python3 build_audit.py --refresh-receipts`, then `python3 validate.py`. Refresh receipts whenever
an upstream family corpus changes.
