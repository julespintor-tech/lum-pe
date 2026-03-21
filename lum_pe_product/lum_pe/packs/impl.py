from __future__ import annotations
from typing import Dict, Any
from lum_pe.packs.registry import PackResult

def GENERIC_v1(payload: Dict[str, Any]) -> PackResult:
    trace = {"checks": [], "payload_keys": sorted(list(payload.keys()))}
    return PackResult("GENERIC_v1", True, trace, {}, ["GENERIC stub executed."])

def FORM_GENERAL_v1(payload: Dict[str, Any]) -> PackResult:
    enc = payload.get("encoding_hash")
    chk = bool(payload.get("proof_checker_passed", False))
    cex = bool(payload.get("counterexample_provided", False))
    passed = bool(enc) and (chk or cex)
    trace = {"encoding_hash": enc, "proof_checker_passed": chk, "counterexample_provided": cex}
    black = {}
    notes = []
    if not enc and payload.get("strong_claims", False):
        black["validation_dependency"] = 0.9
        notes.append("Strong claims without encoding_hash.")
    return PackResult("FORM_GENERAL_v1", passed, trace, black, notes)

def NAT_GENERAL_v1(payload: Dict[str, Any]) -> PackResult:
    oos = bool(payload.get("oos_validated", False))
    unc = bool(payload.get("uncertainty_reported", False))
    leak = float(payload.get("leakage_score", 0.0))
    rep = bool(payload.get("replication_support", False))
    passed = oos and unc and leak < 0.2
    trace = {"oos_validated": oos, "uncertainty_reported": unc, "leakage_score": leak, "replication_support": rep}
    black = {}
    notes = []
    if leak >= 0.5:
        black["leakage_score"] = leak
        notes.append("Leakage candidate.")
    if not passed:
        notes.append("NAT_GENERAL failed minimum checks.")
    return PackResult("NAT_GENERAL_v1", passed, trace, black, notes)

def SOC_DiD_v3(payload: Dict[str, Any]) -> PackResult:
    pre = bool(payload.get("pre_trends_passed", False))
    pla = bool(payload.get("placebo_passed", False))
    rob = bool(payload.get("robustness_checks_passed", False))
    hack = float(payload.get("window_p_hacking_risk", 0.0))
    passed = pre and pla and rob and hack < 0.5
    trace = {"pre_trends_passed": pre, "placebo_passed": pla, "robustness_checks_passed": rob, "window_p_hacking_risk": hack}
    black = {}
    notes = []
    if not pre:
        notes.append("Pre-trends failed/missing.")
    if hack >= 0.8:
        black["leakage_score"] = min(1.0, hack)
        notes.append("High window p-hacking risk.")
    return PackResult("SOC_DiD_v3", passed, trace, black, notes)

def SOC_IV_v2(payload: Dict[str, Any]) -> PackResult:
    rel = bool(payload.get("relevance_passed", False))
    exo = bool(payload.get("exogeneity_defended", False))
    weak = float(payload.get("weak_iv_risk", 1.0))
    passed = rel and exo and weak < 0.5
    trace = {"relevance_passed": rel, "exogeneity_defended": exo, "weak_iv_risk": weak}
    black = {}
    notes = []
    if rel and not exo:
        black["validation_dependency"] = 0.7
        notes.append("Relevance ok, exogeneity not defended.")
    if weak >= 0.5:
        notes.append("Weak-IV risk high.")
    return PackResult("SOC_IV_v2", passed, trace, black, notes)

def ENG_TEST_v1(payload: Dict[str, Any]) -> PackResult:
    reqs = payload.get("requirements", [])
    tests = payload.get("tests", {})
    obs = bool(payload.get("observability", False))
    missing = []
    if not reqs: missing.append("requirements")
    if not tests: missing.append("tests")
    if not obs: missing.append("observability")
    passed = (len(missing) == 0) and all(bool(v) for v in tests.values())
    trace = {"requirements_n": len(reqs), "tests": tests, "observability": obs, "missing": missing}
    black = {}
    notes = []
    if not passed and payload.get("strong_claims", False):
        black["validation_dependency"] = 0.8
        notes.append("Strong claims without full engineering artifacts.")
    return PackResult("ENG_TEST_v1", passed, trace, black, notes)
