# Changelog

All notable changes to LUM-PE are documented here.

## [v0.1.0] — 2026-03-16 (vΩ.2026-02)

### Added
- Full pipeline: `DEMARCATE → TYPE → SELECT_PACK → VERIFY → MEASURE_LUM → DECIDE → EMIT`
- Five domain packs: `NAT_GENERAL_v1`, `SOC_DiD_v3`, `SOC_IV_v2`, `ENG_TEST_v1`, `FORM_GENERAL_v1`
- Minimum contract + post-checks (hard rules, BLACK state detection)
- SHA-256 deterministic bundle fingerprinting
- `lum run` and `lum validate` CLI commands
- Public synthetic reference dataset (45 fields, seed 2602026)
- Hello World artifacts and red team report template
- Four LUM states: GREEN (CLARION), AMBER (PSNC), RED, BLACK

### Notes
- This release is a product-grade scaffold. Real extractors for core indices must be plugged in.
- All dataset values are synthetic — not empirical validation.

---

## Versioning

LUM-PE uses [Semantic Versioning](https://semver.org/).

- **MAJOR** version: breaking changes to contract, pipeline, or bundle schema
- **MINOR** version: new packs, new indices, backwards-compatible features
- **PATCH** version: bug fixes, documentation, minor improvements
