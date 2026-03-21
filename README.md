# LUM-PE — Luminomatics Public Edition

**Version:** vΩ.2026-02 (v0.1.0)
**Status:** Public Release
**License:** MIT (code) · CC BY 4.0 (dataset & specification)

---

## What is LUM?

**LUM (Luminomatics)** is a universal framework for evaluating whether a scientific or operational problem reaches *closure* — a formal, auditable, evidence-bound state called **CLARION** — or whether it produces a structured non-closure plan (**PSNC**).

LUM assigns one of four states to any evidence bundle:

| State | Meaning |
|-------|---------|
| 🟢 **GREEN** | Closure achieved (CLARION) |
| 🟡 **AMBER** | Partial evidence — non-closure plan issued (PSNC) |
| 🔴 **RED** | Evidence insufficient or contradictory |
| ⚫ **BLACK** | Adversarial / gaming detected — hard block |

The pipeline is:

```
DEMARCATE → TYPE → SELECT_PACK → VERIFY → MEASURE_LUM → DECIDE → EMIT(BUNDLE + SHA-256)
```

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/julespintor-tech/lum-pe.git
cd lum-pe

# 2. Install
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

# 3. Run Hello World
lum run \
  --problem "Evaluar cierre operativo" \
  --input examples/container_nat_general.json \
  --payload examples/payload_nat_general.json \
  --out out_bundle.json

# 4. Validate output bundle
lum validate --bundle out_bundle.json
```

---

## Repository Structure

```
lum-pe/
├── lum_pe/
│   ├── engine/
│   │   └── core.py          # Full pipeline: DEMARCATE→EMIT
│   ├── spec/
│   │   └── contract.py      # Minimum contract + post-checks (hard rules)
│   ├── packs/
│   │   ├── registry.py      # Pack registry
│   │   └── impl.py          # NAT_GENERAL, SOC_DiD, SOC_IV, ENG_TEST, FORM_GENERAL
│   ├── indices/
│   │   └── types.py         # Index types + hard normalization (clip→logit→z)
│   ├── util/
│   │   └── hashing.py       # SHA-256 deterministic footprinting
│   └── cli.py               # `lum` CLI entry point
├── examples/
│   ├── container_nat_general.json
│   └── payload_nat_general.json
├── tests/
│   └── test_smoke.py
├── dataset/                 # Public synthetic dataset v0.1.0 (45 fields)
│   ├── evidence_set_table_public_45.csv
│   ├── DATA_DICTIONARY.md
│   └── bundles_public/
├── pyproject.toml
├── LICENSE
├── CITATION.cff
└── README.md
```

---

## Core Indices

| Index | Symbol | Range | Meaning |
|-------|--------|-------|---------|
| Internal Predictive Utility | IPU | [0,1] | Predictive power within the problem |
| Comparative Predictive Validity | CPV | [0,1] | Performance vs. alternatives |
| Accuracy / Effect size | A* | [0,1] | Normalised accuracy or effect magnitude |
| Inter-rater / consistency | κ_conf | [0,1] | Agreement across operationalisations |
| Conservatism | Cons | [0,1] | Bias towards caution |
| Confidence | Conf | [0,1] | Epistemic confidence of the measure |
| Coverage | Coverage | [0,1] | Evidence breadth |
| Shadow index | Shadow | [0,1] | Adversarial/gaming detector |

---

## Domain Packs

| Pack ID | Domain | Subtype |
|---------|--------|---------|
| `NAT_GENERAL_v1` | Natural | General natural phenomena |
| `SOC_DiD_v3` | Social | Difference-in-Differences |
| `SOC_IV_v2` | Social | Instrumental Variables |
| `ENG_TEST_v1` | Engineering | Testing & QA |
| `FORM_GENERAL_v1` | Formal | Mathematical / logical |

---

## Public Dataset

The `dataset/` folder contains a **synthetic** public reference dataset (45 fields, seed `2602026`) for:
- End-to-end reproducibility testing
- CI smoke tests
- Onboarding and documentation

This dataset does **not** constitute empirical validation of LUM-PE on real domains.

---

## Citation

If you use LUM-PE in your work, please cite:

```bibtex
@software{lum_pe_2026,
  author    = {Rojas Aguayo, Julio David},
  title     = {{LUM-PE}: Luminomatics Public Edition — Universal Resolution Engine},
  year      = {2026},
  version   = {v0.1.0},
  url       = {https://github.com/julespintor-tech/lum-pe},
  license   = {MIT}
}
```

See also `CITATION.cff` for full citation metadata.

---

## License

- **Code:** [MIT License](LICENSE)
- **Dataset & Specification:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## Contact

Julio David Rojas Aguayo · jules_pintor@outlook.com
