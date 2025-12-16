from __future__ import annotations

from typing import Dict

import numpy as np

from ice.features.contract import FeatureContract


def to_model_vector(contract: FeatureContract, features: Dict[str, float]) -> np.ndarray:
    """
    Convert a feature dict into a fixed-order numpy vector.
    """
    contract.validate(features)
    cols = list(contract.columns())
    return np.array([float(features.get(c, 0.0)) for c in cols], dtype=float)


def sanitize_features(features: Dict[str, float]) -> Dict[str, float]:
    """
    Minimal sanitization:
    - clamp rates to [0, 1]
    - prevent negative counts

    Real systems need domain-specific validation and missingness handling.
    """
    out: Dict[str, float] = dict(features)
    for k in ["rent_on_time_rate_12m", "utility_on_time_rate_12m"]:
        if k in out:
            out[k] = max(0.0, min(1.0, float(out[k])))
    for k in ["nsf_events_12m", "overdraft_events_12m"]:
        if k in out:
            out[k] = max(0.0, float(out[k]))
    return out


