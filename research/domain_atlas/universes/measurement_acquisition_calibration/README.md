# Measurement acquisition and calibration semantics

This governed universe decomposes reusable measurement semantics for signal diagnostics, visual
inspection and later sensor-based verticals. It is not a device SDK, metrology laboratory, IoT
platform, inspection product or condition-monitoring product.

```text
asset / feature / property / procedure / channel declaration
                         |
                         v
             observation-binding compiler
                         |
device capabilities ---> acquisition-profile compiler ---> non-authoritative acquisition request
                         |                                      |
                         |                              external device runtime
                         |                                      |
calibration declaration  |                              acquisition receipt
          |              |                                      |
          v              |                                      |
calibration-record compiler ---> calibration evaluator <--- indication + conditions
                         |                     |
                         +----------+----------+
                                    v
                      measurement-result constructor
                                    |
                                    v
          observation occurrence + uncertainty + scoped traceability evidence

Not produced here: diagnosis, defect disposition, maintenance/control authorization or business fact.
```

The five exact library contracts are:

1. `library.measurement.observation_binding.compiler`
2. `library.measurement.acquisition_profile.compiler`
3. `library.measurement.calibration_record.compiler`
4. `library.measurement.calibration.evaluator`
5. `library.measurement.observation_result.constructor`

Scalar signals and images use explicit acquisition/calibration profiles over the same core laws.
Protocol compatibility, a certificate, a calibration date, a unit symbol or a plausible value never
establishes fitness, traceability, diagnosis or effect authority. All offers remain unimplemented and
unqualified until independent exact-scope conformance evidence exists.

Run:

```bash
python3 build_corpus.py
python3 validate_corpus.py
```
