from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import math
from lum_pe.util.hashing import clip01

@dataclass
class Indices:
    ipu: float
    cpv: float
    a_norm: float
    kappa_conf: float
    conf: float
    coverage: float
    shadow: Optional[float] = None
    Hs: Optional[float] = None
    SNR: Optional[float] = None
    I: Optional[float] = None

    @property
    def cons(self) -> float:
        return 1.0 - float(self.kappa_conf)

@dataclass
class ZScales:
    id: str
    ipu_mean: float; ipu_std: float
    cpv_mean: float; cpv_std: float
    a_mean: float; a_std: float
    cons_mean: float; cons_std: float

def logit(p: float) -> float:
    return math.log(p / (1.0 - p))

def zscore(x: float, mean: float, std: float) -> float:
    return (x - mean) / std

def normalize(idx: Indices, eps: float, z: ZScales) -> Dict[str, float]:
    ipu = logit(clip01(idx.ipu, eps))
    cpv = logit(clip01(idx.cpv, eps))
    a   = logit(clip01(idx.a_norm, eps))
    cons= logit(clip01(idx.cons, eps))
    return {
        "ipu_z": zscore(ipu, z.ipu_mean, z.ipu_std),
        "cpv_z": zscore(cpv, z.cpv_mean, z.cpv_std),
        "a_z": zscore(a, z.a_mean, z.a_std),
        "cons_z": zscore(cons, z.cons_mean, z.cons_std),
    }
