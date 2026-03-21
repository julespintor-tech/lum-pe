# LUM-PE (Public Edition) — Product Package

**Release:** vΩ.2026-02 (productized reference implementation)  
**CLI:** `lum`

This package implements the pipeline:

`DEMARCATE → TYPE → SELECT_PACK → VERIFY → MEASURE_LUM → DECIDE → EMIT(BUNDLE+HASH)`

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
lum --help
```

### Run an evaluation

```bash
lum run --problem "Evaluar cierre operativo" \
  --input examples/input_nat_general.json \
  --payload examples/payload_nat_general.json \
  --out out_bundle.json
```

### Validate a bundle (schema + post-checks)

```bash
lum validate --bundle out_bundle.json
```

## Notes

- This is a product-grade scaffold. You must plug in your real extractors for IPU/CPV/A*/κ/Conf/coverage.
- Packs are modular and versioned. Add new packs under `lum_pe/packs/`.
- Schema validation is minimal (no external deps). If you want full JSON Schema, you can add `jsonschema`.
