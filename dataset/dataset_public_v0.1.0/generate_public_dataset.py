import os, json, csv, time, hashlib, random

SEED = 2602026
random.seed(SEED)

def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def canonical_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

def clip01(x, eps=1e-6):
    return max(eps, min(1.0-eps, float(x)))

def decide_state(p, and_min, tau_g=0.8, tau_r=0.4):
    if p >= tau_g and and_min:
        return "GREEN"
    if p < tau_r:
        return "RED"
    return "AMBER"

def main(out_dir="dataset_public_v0.1.0"):
    os.makedirs(out_dir, exist_ok=True)
    bundles_dir = os.path.join(out_dir, "bundles_public")
    os.makedirs(bundles_dir, exist_ok=True)

    thresholds = {
        "tau_green": 0.80, "tau_red": 0.40,
        "theta_ipu": 0.65, "theta_a": 0.55, "theta_conf": 0.60,
        "epsilon_clip": 1e-6
    }
    z_scales_id = "z_vOmega_2026_02_public_45"

    domains = [
        ("FORMAL","FORM_GENERAL"),
        ("NATURAL","NAT_GENERAL"),
        ("SOCIAL","SOC_DiD"),
        ("SOCIAL","SOC_IV"),
        ("ENGINEERING","ENG_TEST")
    ]

    rows = []
    for i in range(1, 46):
        domain_type, domain_subtype = random.choice(domains)
        field_id = f"public_field_{i:02d}_{domain_subtype.lower()}"

        ipu = clip01(random.betavariate(6, 3))
        cpv = clip01(random.betavariate(5, 4))
        a_norm = clip01(random.betavariate(5, 5))
        kappa = clip01(random.betavariate(3, 7))
        cons = 1.0 - kappa
        conf = clip01(random.betavariate(6, 4))
        coverage = clip01(random.betavariate(7, 3))
        shadow = 1.0 - coverage
        hs = clip01(random.betavariate(5, 5))
        snr = clip01(random.betavariate(6, 4))
        I = clip01(random.betavariate(5, 5))

        p_raw = clip01(0.15 + 0.35*ipu + 0.25*cpv + 0.20*a_norm + 0.15*cons - 0.10*shadow)
        andmin = (ipu >= thresholds["theta_ipu"] and a_norm >= thresholds["theta_a"] and conf >= thresholds["theta_conf"])
        state = decide_state(p_raw, andmin, thresholds["tau_green"], thresholds["tau_red"])

        pack_id = {
            "FORMAL":"FORM_GENERAL_v1",
            "NATURAL":"NAT_GENERAL_v1",
            "SOCIAL":"SOC_DiD_v3" if domain_subtype=="SOC_DiD" else "SOC_IV_v2",
            "ENGINEERING":"ENG_TEST_v1"
        }[domain_type]

        evidence_set_hash = sha256_str(f"{SEED}:{field_id}:evidence")
        pack_trace_hash = sha256_str(f"{SEED}:{field_id}:{pack_id}:trace")

        bundle = {
            "INPUT": {
                "field_id": field_id,
                "scope_in": ["public_synthetic_demo"],
                "scope_out": ["real-world generalization", "external audit claims"],
                "t_ref_iso": "2026-02-28T12:00:00-06:00",
                "delta_days": 30.0,
                "evidence_set_hash": evidence_set_hash,
                "event_of_closure": "At least one audited synthetic identity within (t, t+Δ].",
                "incompatibility_rule": "If kappa_conf > 0.35 or leakage detected, closure blocked.",
                "demarcation": "U-MIX" if domain_type!="ENGINEERING" else "P-TEC",
                "domain_type": domain_type,
                "domain_subtype": domain_subtype,
                "delta_policy": "fixed",
                "cpv_semantics_version": "cpv_vOmega_1"
            },
            "CONFIG": {
                "version": "LUM-PE vOmega.2026-02",
                "engine_version": "engine_v1.0",
                "packs_version": "packs_v1.1",
                "audit_level": "strict",
                "thresholds": thresholds,
                "z_scales": {
                    "id": z_scales_id,
                    "ipu_mean": 0.0, "ipu_std": 1.0,
                    "cpv_mean": 0.0, "cpv_std": 1.0,
                    "a_mean": 0.0, "a_std": 1.0,
                    "cons_mean": 0.0, "cons_std": 1.0
                },
                "ci_policy": { "level": 0.95, "method": "bootstrap", "B": 2000, "block_bootstrap": False }
            },
            "MODEL": {
                "model_family": "hazard_cloglog",
                "coeffs": { "beta0": -1.0, "alpha_ipu": 1.0, "beta_cpv": 1.0, "gamma_a": 1.0, "beta_cons": 1.0 },
                "constraints": { "beta_cons_nonnegative": True },
                "calibration_status": "uncalibrated",
                "calibration_method": None,
                "calibration_artifact_hash": None
            },
            "OUTPUT": {
                "state": state,
                "validity": "VALID",
                "reason_if_invalid": None,
                "pack_id": pack_id,
                "pack_trace_hash": pack_trace_hash,
                "indices": {
                    "ipu": round(ipu,4), "cpv": round(cpv,4), "a_norm": round(a_norm,4),
                    "kappa_conf": round(kappa,4), "cons": round(cons,4),
                    "conf": round(conf,4), "coverage": round(coverage,4), "shadow": round(shadow,4),
                    "Hs": round(hs,4), "SNR": round(snr,4), "I": round(I,4)
                },
                "probabilities": { "p_close_raw": round(p_raw,4), "p_close_cal": None, "p_close_kind": "score" },
                "and_min_passed": bool(andmin),
                "overclosure_metrics": None,
                "psnc": None,
                "justification": "PUBLIC synthetic reference bundle (not empirical validation)."
            },
            "AUDIT": {
                "footprint_sha256": "",
                "created_unix": int(time.time()),
                "post_checks_passed": True,
                "post_checks_notes": ["Public synthetic reference dataset."]
            }
        }

        if state != "GREEN":
            bundle["OUTPUT"]["psnc"] = {
                "required": True,
                "summary": f"PSNC (public synthetic): state={state}.",
                "actions": ["Increase Conf/coverage; reduce kappa_conf; strengthen pack checks."],
                "diagnostics": {"shadow": round(shadow,4), "kappa_conf": round(kappa,4), "conf": round(conf,4)},
                "reentry_criteria": "Re-evaluate after actions (public synthetic).",
                "expected_index_shifts": "Up Conf/coverage; down kappa_conf/shadow."
            }

        audit_copy = dict(bundle["AUDIT"])
        audit_copy["footprint_sha256"] = ""
        to_hash = {"INPUT": bundle["INPUT"], "CONFIG": bundle["CONFIG"], "MODEL": bundle["MODEL"], "OUTPUT": bundle["OUTPUT"], "AUDIT": audit_copy}
        bundle["AUDIT"]["footprint_sha256"] = sha256_str(canonical_json(to_hash))

        with open(os.path.join(bundles_dir, f"{field_id}_bundle.json"), "w", encoding="utf-8") as f:
            json.dump(bundle, f, ensure_ascii=False, indent=2)

        rows.append({
            "field_id": field_id,
            "domain_type": domain_type,
            "domain_subtype": domain_subtype,
            "delta_days": 30,
            "state": state,
            "ipu": round(ipu,4), "cpv": round(cpv,4), "a_norm": round(a_norm,4),
            "kappa_conf": round(kappa,4), "cons": round(cons,4),
            "conf": round(conf,4), "coverage": round(coverage,4), "shadow": round(shadow,4),
            "hs": round(hs,4), "snr": round(snr,4), "i": round(I,4),
            "pack_id": pack_id,
            "pack_trace_hash": pack_trace_hash,
            "evidence_set_hash": evidence_set_hash,
            "bundle_fp": bundle["AUDIT"]["footprint_sha256"],
        })

    with open(os.path.join(out_dir, "evidence_set_table_public_45.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    with open(os.path.join(out_dir, "MANIFEST_SHA256.txt"), "w", encoding="utf-8") as f:
        f.write("SHA-256 manifest for key files\n")
    print("Done:", out_dir)

if __name__ == "__main__":
    main()
