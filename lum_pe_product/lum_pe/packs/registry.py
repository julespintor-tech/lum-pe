from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Callable, Optional

@dataclass
class PackResult:
    pack_id: str
    passed: bool
    trace: Dict[str, Any]
    black_triggers: Dict[str, float]
    notes: list[str]

PackVerifier = Callable[[Dict[str, Any]], PackResult]

class PackRegistry:
    def __init__(self):
        self._v: Dict[str, PackVerifier] = {}

    def register(self, pack_id: str, verifier: PackVerifier) -> None:
        self._v[pack_id] = verifier

    def get(self, pack_id: str) -> PackVerifier:
        if pack_id not in self._v:
            raise KeyError(f"Pack not registered: {pack_id}")
        return self._v[pack_id]

    def suggest(self, domain_type: str, domain_subtype: str) -> str:
        dt = (domain_type or "").upper()
        st = (domain_subtype or "").upper()
        if dt == "SOCIAL" and "DID" in st:
            return "SOC_DiD_v3"
        if dt == "SOCIAL" and "IV" in st:
            return "SOC_IV_v2"
        if dt == "ENGINEERING":
            return "ENG_TEST_v1"
        if dt == "NATURAL":
            return "NAT_GENERAL_v1"
        if dt == "FORMAL":
            return "FORM_GENERAL_v1"
        return "GENERIC_v1"
