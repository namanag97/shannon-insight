# Representation and codec boundary adjudication

Status: evidence-backed candidate boundary; not ratified or provider-qualified.

The result is deliberately **zero products**. “Codec-as-a-Service” is an architecture/deployment
label for representation libraries plus an optional operated runtime component.

```text
semantic value/type (neighbor)
          |
          v
carrier -> serialization -> framing -> layout -> column encoding
                                             -> compression
                                             -> codec + loss profile
          |                                      |
          +-------------- transcode -------------+
                              |
                              v
           qualified provider/kernel + runtime budgets
                              |
                              v
                  result + verification receipt
```

The runtime may own availability, cancellation, memory/CPU budgets and occurrence receipts. It does
not own payload meaning, storage-product lifecycle, security authority, accepted loss, or a distinct
enterprise outcome. Models or agents can propose configurations only when requested; deterministic
profile validation, provider qualification, loss authorization, execution and verification remain
mandatory.

```bash
python3 research/product_ontology/adjudications/representation_codec_boundary/build_bundle.py
python3 research/product_ontology/adjudications/representation_codec_boundary/validate.py
```
