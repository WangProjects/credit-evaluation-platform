from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple


@dataclass(frozen=True)
class FeatureContract:
    """
    A minimal feature contract.

    Real systems should version this contract, include units and provenance, and
    define strict null-handling policies.
    """

    required: Tuple[str, ...]
    optional: Tuple[str, ...] = ()

    def validate(self, features: Dict[str, float]) -> None:
        missing = [k for k in self.required if k not in features]
        if missing:
            raise ValueError(f"Missing required features: {missing}")

        # Reject unknown fields to avoid schema injection.
        allowed = set(self.required) | set(self.optional)
        unknown = [k for k in features.keys() if k not in allowed]
        if unknown:
            raise ValueError(f"Unknown features not in contract: {unknown}")

        # Basic type checks
        for k, v in features.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"Feature {k} must be numeric, got {type(v)}")

    def schema_hash(self) -> str:
        payload = {"required": self.required, "optional": self.optional}
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    def columns(self) -> Iterable[str]:
        return list(self.required) + list(self.optional)


DEFAULT_CONTRACT = FeatureContract(
    required=(
        "rent_on_time_rate_12m",
        "utility_on_time_rate_12m",
        "avg_monthly_income_6m",
        "cashflow_volatility_6m",
        "avg_daily_balance_6m",
        "nsf_events_12m",
        "overdraft_events_12m",
    ),
    optional=(
        "months_at_current_job",
        "months_at_current_address",
    ),
)


