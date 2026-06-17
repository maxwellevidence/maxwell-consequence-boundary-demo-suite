# Adversarial Harness Report — Demo 10: Maxwell Public Sector Determination Demo

## Status

This demo participates in the Maxwell Consequence Boundary Demo Suite v0.4.0 internal adversarial harness.

## Local command

```bash
make adversarial
```

The local adversarial target runs:

```bash
python -m pytest -q tests/adversarial/test_adversarial_corpus.py
```

## Expected adversarial outcome

Every input under `examples/adversarial_inputs/` is expected to fail closed. That means no unauthorized `determination_effect_record.json` should be created. A safe outcome should include `NO_DETERMINATION_EFFECT_CREATED.txt`, a suppression notice, review/security/quarantine routing, or failed verification for tamper cases.

## Boundary

This is a public-preview internal adversarial harness result. It is not an independent external red-team certification and does not claim exhaustive coverage of all possible hostile inputs.
