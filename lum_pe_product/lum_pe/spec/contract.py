"""LUM-PE Contract (Execution Bundle)

This module defines the canonical keys and lightweight validation.
For strict JSON Schema validation, you can optionally add jsonschema later.

Bundle required objects:
- INPUT, CONFIG, MODEL, OUTPUT, AUDIT

Hard if/then rules are checked in post_checks.
"""

REQUIRED_TOP_LEVEL = ["INPUT", "CONFIG", "MODEL", "OUTPUT", "AUDIT"]

def validate_min_contract(bundle: dict) -> tuple[bool, list[str]]:
    notes = []
    ok = True
    for k in REQUIRED_TOP_LEVEL:
        if k not in bundle:
            ok = False
            notes.append(f"Missing top-level key: {k}")
    return ok, notes

def post_checks(bundle: dict) -> tuple[bool, list[str]]:
    notes = []
    ok = True

    # Thresholds sanity
    th = bundle.get("CONFIG", {}).get("thresholds", {})
    tau_g = th.get("tau_green", None)
    tau_r = th.get("tau_red", None)
    if tau_g is None or tau_r is None:
        ok = False
        notes.append("Missing thresholds.tau_green or thresholds.tau_red")
    else:
        if not (0.0 < float(tau_r) < float(tau_g) < 1.0):
            ok = False
            notes.append("Require 0 < tau_red < tau_green < 1")

    # Consistency: Cons = 1 - kappa_conf (if both present)
    idx = bundle.get("OUTPUT", {}).get("indices", {})
    kappa = idx.get("kappa_conf", None)
    cons = idx.get("cons", None)
    if kappa is not None and cons is not None:
        if abs((1.0 - float(kappa)) - float(cons)) > 1e-6:
            ok = False
            notes.append("cons != 1 - kappa_conf")

    # If p_close_cal exists -> MODEL must declare calibration
    probs = bundle.get("OUTPUT", {}).get("probabilities", {})
    pcal = probs.get("p_close_cal", None)
    if pcal is not None:
        model = bundle.get("MODEL", {})
        if model.get("calibration_status") != "calibrated":
            ok = False
            notes.append("p_close_cal present but MODEL.calibration_status != calibrated")
        if not model.get("calibration_method"):
            ok = False
            notes.append("p_close_cal present but MODEL.calibration_method missing")
        if not model.get("calibration_artifact_hash"):
            ok = False
            notes.append("p_close_cal present but MODEL.calibration_artifact_hash missing")

    # If BLACK -> PSNC.required true and overclosure_metrics present
    state = bundle.get("OUTPUT", {}).get("state")
    if state == "BLACK":
        psnc = bundle.get("OUTPUT", {}).get("psnc", {})
        if psnc.get("required") is not True:
            ok = False
            notes.append("BLACK requires OUTPUT.psnc.required = true")
        if "overclosure_metrics" not in bundle.get("OUTPUT", {}):
            ok = False
            notes.append("BLACK requires OUTPUT.overclosure_metrics")

    # If INVALID -> reason_if_invalid required
    validity = bundle.get("OUTPUT", {}).get("validity")
    if validity == "INVALID":
        if not bundle.get("OUTPUT", {}).get("reason_if_invalid"):
            ok = False
            notes.append("INVALID requires reason_if_invalid")

    # GREEN -> and_min_passed required
    if state == "GREEN":
        if bundle.get("OUTPUT", {}).get("and_min_passed") is not True:
            ok = False
            notes.append("GREEN requires and_min_passed = true")

    return ok, notes
