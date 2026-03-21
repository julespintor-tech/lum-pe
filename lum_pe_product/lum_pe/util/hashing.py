from __future__ import annotations
import dataclasses
import json
import hashlib
from enum import Enum
from typing import Any

def to_canonical_json(obj: Any) -> str:
    def default(o: Any):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, Enum):
            return o.value
        raise TypeError(f"Non-serializable type: {type(o)}")
    return json.dumps(obj, default=default, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

def sha256_hex(obj: Any) -> str:
    s = to_canonical_json(obj).encode("utf-8")
    return hashlib.sha256(s).hexdigest()

def clip01(x: float, eps: float) -> float:
    x = float(x)
    if x < eps:
        return eps
    if x > 1.0 - eps:
        return 1.0 - eps
    return x
