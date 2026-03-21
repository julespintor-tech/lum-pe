from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple
import math
import time

from lum_pe.util.hashing import sha256_hex, to_canonical_json
from lum_pe.indices.types import Indices, ZScales, normalize
from lum_pe.packs import REGISTRY
from lum_pe.spec.contract import validate_min_contract, post_checks

class LUMState(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    BLACK = "BLACK"

class Validity(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"

class Demarcation(str, Enum):
    C_ALPHA = "C-α"
    C_BETA  = "C-β"
    P_TEC   = "P-TEC"
    M_TOT   = "M-TOT"
    I_NOR   = "I-NOR"
    U_MIX   = "U-MIX"

@dataclass
class Thresholds:
    tau_green: float = 0.80
    tau_red: float = 0.40
    theta_ipu: float = 0.70
    theta_a: float = 0.65
    theta_conf: float = 0.70
    epsilon_clip: float = 1e-6

def cloglog_inv(eta: float) -> float:
    return 1.0 - math.exp(-math.exp(eta))

def hazard_cloglog(pz: Dict[str, float], delta_days: float, coeffs: Dict[str, float], beta_cons_nonneg=True) -> float:
    beta_cons = float(coeffs.get("beta_cons", 0.0))
    if beta_cons_nonneg:
        beta_cons = max(0.0, beta_cons)
    eta = (
        math.log(max(1e-12, float(delta_days))) +
        float(coeffs.get("beta0", 0.0)) +
        float(coeffs.get("alpha_ipu", 0.0)) * pz["ipu_z"] +
        float(coeffs.get("beta_cpv", 0.0))  * pz["cpv_z"] +
        float(coeffs.get("gamma_a", 0.0))   * pz["a_z"] +
        beta_cons * pz["cons_z"]
    )
    p = cloglog_inv(eta)
    return max(0.0, min(1.0, p))

def and_min(idx: Indices, th: Thresholds) -> bool:
    return (idx.ipu >= th.theta_ipu) and (idx.a_norm >= th.theta_a) and (idx.conf >= th.theta_conf)

def overclosure_metrics(pack_black: Dict[str, float], payload: Dict[str, Any]) -> Dict[str, float]:
    # base metrics
    m = {
        "entropy_protocols": float(payload.get("entropy_protocols", 0.0)),
        "missing_comparisons_ratio": float(payload.get("missing_comparisons_ratio", 0.0)),
        "leakage_score": float(payload.get("leakage_score", 0.0)),
        "validation_dependency": float(payload.get("validation_dependency", 0.0)),
    }
    # pack overrides
    for k,v in pack_black.items():
        if k in m:
            m[k] = max(m[k], float(v))
    return m

def should_black(m: Dict[str, float]) -> bool:
    if m.get("leakage_score", 0.0) >= 0.8:
        return True
    if m.get("validation_dependency", 0.0) >= 0.85:
        return True
    if m.get("missing_comparisons_ratio", 0.0) >= 0.8:
        return True
    ep = m.get("entropy_protocols", 0.0)
    if 0.0 < ep <= 0.05:
        return True
    return False

def psnc(idx: Indices, state: LUMState) -> Dict[str, Any]:
    shadow = idx.shadow if idx.shadow is not None else (1.0 - idx.coverage)
    actions = []
    if shadow > 0.3:
        actions.append("Sube coverage: instrumenta mejor y reduce Shadow (Sh).")
    if idx.Hs is not None and idx.SNR is not None and idx.Hs > 0.6 and idx.SNR < 0.5:
        actions.append("Denoise: mejora medicion, filtra ruido, revisa pipeline (Hs alta + SNR baja).")
    if idx.I is not None and idx.I > 0.6:
        actions.append("Separa mecanismos: rediseña modelo/identificacion (I alto).")
    if idx.kappa_conf > 0.35:
        actions.append("Baja κ_conf: abre comparaciones, replica, explicita incompatibilidades.")
    if idx.conf < 0.7:
        actions.append("Sube Conf: aumenta n efectivo, mejora IC, bootstrap por bloques si aplica.")
    if not actions:
        actions.append("PSNC generico: aumenta evidencia, fortalece checks del pack y reevalua con Δ fijo.")
    return {
        "required": True,
        "summary": f"PSNC: estado={state.value}. No hay cierre suficiente; plan de avance.",
        "actions": actions,
        "diagnostics": {
            "coverage": idx.coverage,
            "shadow": shadow,
            "Hs": idx.Hs,
            "SNR": idx.SNR,
            "I": idx.I,
            "kappa_conf": idx.kappa_conf,
            "conf": idx.conf,
        },
        "reentry_criteria": "Re-evaluar tras ejecutar acciones y actualizar evidence_set_hash.",
        "expected_index_shifts": "Subir IPU/Conf/coverage y bajar κ_conf/Sh."
    }

def psnc_d(problem_text: str) -> Dict[str, Any]:
    return {
        "required": True,
        "summary": "PSNC-D: demarcacion fallida (M-TOT o I-NOR no traducido).",
        "actions": [
            "Recorta el objeto: define scope_in/scope_out en lenguaje operatorio.",
            "Define operadores y reglas de verificacion.",
            "Define criterio de contradiccion (falsacion interna al campo).",
            "Preregistra event_of_closure e incompatibility_rule.",
            "Traduce lo normativo a P-TEC: objetivos medibles + requisitos + tests."
        ],
        "diagnostics": {"problem_text_excerpt": (problem_text or "")[:300]},
        "reentry_criteria": "Reingresa cuando existan operadores + reglas + contradiccion + recorte.",
        "expected_index_shifts": "N/A (primero convertir en problema tratable)."
    }

def compute_indices_from_payload(payload: Dict[str, Any]) -> Indices:
    # Product hook: replace with real extractors.
    required = ["ipu","cpv","a_norm","kappa_conf","conf","coverage"]
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError(f"Missing required index keys in payload: {missing}")
    idx = Indices(
        ipu=float(payload["ipu"]),
        cpv=float(payload["cpv"]),
        a_norm=float(payload["a_norm"]),
        kappa_conf=float(payload["kappa_conf"]),
        conf=float(payload["conf"]),
        coverage=float(payload["coverage"]),
        shadow=(float(payload["shadow"]) if "shadow" in payload else None),
        Hs=(float(payload["Hs"]) if "Hs" in payload else None),
        SNR=(float(payload["SNR"]) if "SNR" in payload else None),
        I=(float(payload["I"]) if "I" in payload else None),
    )
    return idx

def emit_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    # compute footprint over canonical JSON of everything except footprint field itself
    audit = bundle.get("AUDIT", {})
    audit2 = dict(audit)
    audit2["footprint_sha256"] = ""
    obj = {"INPUT": bundle["INPUT"], "CONFIG": bundle["CONFIG"], "MODEL": bundle["MODEL"], "OUTPUT": bundle["OUTPUT"], "AUDIT": audit2}
    fp = sha256_hex(obj)
    bundle["AUDIT"]["footprint_sha256"] = fp
    return bundle

def run(problem_text: str, input_obj: Dict[str, Any], config_obj: Dict[str, Any], model_obj: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    # Demarcation gate
    dem = input_obj.get("demarcation")
    if dem in (Demarcation.M_TOT.value, Demarcation.I_NOR.value):
        out = {
            "state": LUMState.RED.value,
            "validity": Validity.VALID.value,
            "reason_if_invalid": None,
            "pack_id": None,
            "pack_trace_hash": None,
            "indices": {"ipu":0.0,"cpv":0.0,"a_norm":0.0,"kappa_conf":1.0,"cons":0.0,"conf":0.0,"coverage":0.0},
            "probabilities": {"p_close_raw": 0.0, "p_close_cal": None, "p_close_kind": "score"},
            "and_min_passed": False,
            "overclosure_metrics": None,
            "psnc": psnc_d(problem_text),
            "justification": "Demarcation -> PSNC-D; LUM not executed."
        }
        bundle = {
            "INPUT": input_obj, "CONFIG": config_obj, "MODEL": model_obj, "OUTPUT": out,
            "AUDIT": {"footprint_sha256":"", "created_unix": int(time.time()), "post_checks_passed": True, "post_checks_notes":["PSNC-D path"]}
        }
        return emit_bundle(bundle)

    # Pack selection & verify
    audit_level = (config_obj.get("audit_level") or "basic").lower()
    pack_id = input_obj.get("pack_id") or payload.get("pack_id")  # allow override
    if not pack_id:
        pack_id = REGISTRY.suggest(input_obj.get("domain_type",""), input_obj.get("domain_subtype",""))
    pack_trace_hash = None
    pack_passed = None
    pack_notes = []
    pack_black = {}
    validity = Validity.VALID.value
    invalid_reason = None

    try:
        verifier = REGISTRY.get(pack_id)
        pres = verifier(payload)
        pack_passed = pres.passed
        pack_black = pres.black_triggers
        pack_notes = pres.notes
        pack_trace_hash = sha256_hex(pres.trace)
    except Exception as e:
        if audit_level == "strict":
            validity = Validity.INVALID.value
            invalid_reason = f"Pack verification failed in strict mode: {e}"

    # Compute indices
    try:
        idx = compute_indices_from_payload(payload)
    except Exception as e:
        validity = Validity.INVALID.value
        invalid_reason = invalid_reason or f"Index computation failed: {e}"
        idx = Indices(0,0,0,1,0,0)

    # Strict: missing trace blocks GREEN & can invalidate
    if audit_level == "strict" and not pack_trace_hash:
        validity = Validity.INVALID.value
        invalid_reason = invalid_reason or "Missing pack trace in strict mode."

    # Normalize predictors
    th = Thresholds(**config_obj.get("thresholds", {}))
    zconf = config_obj.get("z_scales", {})
    z = ZScales(**zconf) if zconf else ZScales("z_demo",0,1,0,1,0,1,0,1)
    pz = normalize(idx, th.epsilon_clip, z)

    # Model p_close_raw
    coeffs = model_obj.get("coeffs", {})
    constraints = model_obj.get("constraints", {})
    p_raw = hazard_cloglog(pz, float(input_obj.get("delta_days", 30.0)), coeffs, bool(constraints.get("beta_cons_nonnegative", True)))

    # Calibration policy
    p_kind = "score"
    p_cal = None
    if (model_obj.get("calibration_status") == "calibrated"):
        # Product hook: implement actual calibrators; for now, enforce contract.
        if not model_obj.get("calibration_method") or not model_obj.get("calibration_artifact_hash"):
            validity = Validity.INVALID.value
            invalid_reason = invalid_reason or "Calibration declared but calibration_method/artifact_hash missing."
        else:
            # Placeholder: treat as already calibrated and require payload value if provided
            if "p_close_cal" in payload:
                p_cal = float(payload["p_close_cal"])
                p_kind = "probability"
            else:
                validity = Validity.INVALID.value
                invalid_reason = invalid_reason or "Calibration declared but payload missing p_close_cal (stub mode)."

    p_for_state = p_cal if p_cal is not None else p_raw

    # BLACK triggers
    over = overclosure_metrics(pack_black, payload)
    black = should_black(over)

    # AND_min
    andmin = and_min(idx, th)

    # State
    if black:
        state = LUMState.BLACK.value
    else:
        if p_for_state >= th.tau_green:
            state = LUMState.GREEN.value
        elif p_for_state < th.tau_red:
            state = LUMState.RED.value
        else:
            state = LUMState.AMBER.value

    # GREEN guardrails
    if state == LUMState.GREEN.value:
        if not andmin:
            state = LUMState.AMBER.value
        if audit_level == "strict" and pack_passed is False:
            state = LUMState.AMBER.value
        if validity == Validity.INVALID.value:
            state = LUMState.AMBER.value

    # PSNC
    ps = None
    over_out = None
    if state in (LUMState.AMBER.value, LUMState.RED.value, LUMState.BLACK.value):
        ps = psnc(idx, LUMState(state))
    if state == LUMState.BLACK.value:
        over_out = over

    # OUTPUT
    out = {
        "state": state,
        "validity": validity,
        "reason_if_invalid": invalid_reason,
        "pack_id": pack_id,
        "pack_trace_hash": pack_trace_hash,
        "indices": {
            "ipu": idx.ipu, "cpv": idx.cpv, "a_norm": idx.a_norm, "kappa_conf": idx.kappa_conf, "cons": idx.cons,
            "conf": idx.conf, "coverage": idx.coverage,
            "shadow": (idx.shadow if idx.shadow is not None else 1.0 - idx.coverage),
            "Hs": idx.Hs, "SNR": idx.SNR, "I": idx.I
        },
        "probabilities": {"p_close_raw": p_raw, "p_close_cal": p_cal, "p_close_kind": p_kind},
        "and_min_passed": andmin,
        "overclosure_metrics": over_out,
        "psnc": ps,
        "justification": " | ".join([
            f"pack={pack_id}",
            f"pack_passed={pack_passed}",
            f"pack_notes={'; '.join(pack_notes[:2])}" if pack_notes else "pack_notes=",
            f"p={p_for_state:.4f} kind={p_kind}",
            f"AND_min={andmin}",
            f"BLACK={black}",
            f"validity={validity}" + (f" reason={invalid_reason}" if invalid_reason else "")
        ])
    }

    bundle = {
        "INPUT": input_obj, "CONFIG": config_obj, "MODEL": model_obj, "OUTPUT": out,
        "AUDIT": {"footprint_sha256":"", "created_unix": int(time.time()), "post_checks_passed": False, "post_checks_notes":[]}
    }

    # Contract validation + post-checks
    ok1, n1 = validate_min_contract(bundle)
    ok2, n2 = post_checks(bundle)
    bundle["AUDIT"]["post_checks_passed"] = bool(ok1 and ok2)
    bundle["AUDIT"]["post_checks_notes"] = n1 + n2

    if not (ok1 and ok2):
        bundle["OUTPUT"]["validity"] = Validity.INVALID.value
        bundle["OUTPUT"]["reason_if_invalid"] = bundle["OUTPUT"]["reason_if_invalid"] or ("Post-checks failed: " + "; ".join((n1+n2)[:5]))
        if bundle["OUTPUT"]["state"] == LUMState.GREEN.value:
            bundle["OUTPUT"]["state"] = LUMState.AMBER.value

    return emit_bundle(bundle)
