# General statistical inference semantic slice

This unratified research package decomposes general statistics as a reusable formalism rather than
as a notebook feature, provider catalog or monolithic product.

```text
question + target population
           |
           +--> frame / sampling design / analysis population
           +--> estimand + frozen analysis specification
           +--> typed data cut / roles / scales / missingness / weights
           |
           +--> probability + descriptive/exploratory methods
           +--> estimator + sampling distribution + interval
           +--> tests + multiplicity + sequential evidence
           +--> regression/probabilistic fit + diagnostics
           +--> robustness + sensitivity + synthesis
           |
           +--> bounded analytical finding
           +--> reproducibility evidence
                    X finding != decision or effect authority
```

The exact current universe is the notebook product's one declared concrete dependency plus 21
justified shared formalism, quantity, uncertainty, provenance and data-cut neighbors. Structural
overlap is intentionally not treated as product ownership. The notebook remains a document and
captured study artifact; it does not own statistical meaning.

Eight missing library seams are emitted as typed boundary candidates rather than hidden inside the
broad estimator/test libraries:

1. sampling-design semantics;
2. estimand and analysis-specification identity;
3. missing-data mechanisms and sensitivity;
4. multiplicity and sequential evidence;
5. model/computation diagnostics;
6. robust and nonparametric estimators;
7. evidence synthesis/meta-analysis;
8. reproducible-analysis specification and receipts.

The package contains 30 primary/official sources, 41 semantic modules, 46 non-collapse laws, 78
method types, 16 expert learning profiles, 10 recent non-LLM innovations, 22 exact library
bindings, 352 unresolved library-axis decision candidates and 15 product/library boundary
findings. No owner, applicability profile, exact contract, implementation or compiler binding is
ratified.

## Validation

```bash
python3 research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/statistical_inference_semantic_slice/validate.py
```
