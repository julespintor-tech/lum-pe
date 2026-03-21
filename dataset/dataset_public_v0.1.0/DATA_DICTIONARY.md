# Data Dictionary — evidence_set_table_public_45.csv

## Columns
- field_id: Unique identifier for the synthetic "field".
- domain_type: FORMAL | NATURAL | SOCIAL | ENGINEERING
- domain_subtype: Subtype label (FORM_GENERAL, NAT_GENERAL, SOC_DiD, SOC_IV, ENG_TEST)
- delta_days: Window Δ in days.
- state: LUM state (GREEN/AMBER/RED). (BLACK is reserved for adversarial cases; not used in this public set.)
- ipu, cpv, a_norm, kappa_conf, cons, conf, coverage, shadow: Core indices in [0,1].
- hs, snr, i: Optional diagnostics in [0,1].
- pack_id: Pack used (FORM_GENERAL_v1, NAT_GENERAL_v1, SOC_DiD_v3, SOC_IV_v2, ENG_TEST_v1).
- pack_trace_hash: Deterministic synthetic hash (placeholder for real pack traces).
- evidence_set_hash: Deterministic synthetic hash (placeholder for real evidence bundle).
- bundle_fp: SHA-256 footprint of the per-field bundle.json (auditable).

## Notes
- All values are synthetic and generated from beta distributions with a fixed seed.
- The purpose is tooling, onboarding, and audit pipeline demonstration.
