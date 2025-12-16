from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    dtype: type
    min_value: float | None = None
    max_value: float | None = None


FEATURE_SPECS: list[FeatureSpec] = [
    FeatureSpec("rent_on_time_rate_12m", float, 0.0, 1.0),
    FeatureSpec("utilities_on_time_rate_12m", float, 0.0, 1.0),
    FeatureSpec("cashflow_income_monthly", float, 0.0, None),
    FeatureSpec("cashflow_volatility_3m", float, 0.0, None),
    FeatureSpec("avg_daily_balance_30d", float, None, None),
    FeatureSpec("overdraft_events_90d", int, 0.0, None),
    FeatureSpec("months_at_job", int, 0.0, None),
    FeatureSpec("months_at_address", int, 0.0, None),
]

FEATURE_ORDER = [s.name for s in FEATURE_SPECS]


def validate_feature_vector(features: dict) -> np.ndarray:
    """Validate + coerce a feature dict into a fixed-order numeric vector.

    This is intentionally strict to support auditability and predictable inference.
    """

    vec: list[float] = []
    for spec in FEATURE_SPECS:
        if spec.name not in features:
            raise ValueError(f"Missing required feature: {spec.name}")
        v = features[spec.name]
        if spec.dtype is int:
            v = int(v)
        else:
            v = float(v)
        if spec.min_value is not None and v < spec.min_value:
            raise ValueError(f"Feature {spec.name} below min {spec.min_value}: {v}")
        if spec.max_value is not None and v > spec.max_value:
            raise ValueError(f"Feature {spec.name} above max {spec.max_value}: {v}")
        vec.append(float(v))
    return np.asarray(vec, dtype=float)
