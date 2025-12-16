from __future__ import annotations

from typing import Literal, TypedDict


class FeatureDict(TypedDict, total=False):
    # Core engineered features (demo schema)
    rent_on_time_rate_12m: float
    utilities_on_time_rate_12m: float
    cashflow_income_monthly: float
    cashflow_volatility_3m: float
    avg_daily_balance_30d: float
    overdraft_events_90d: int
    months_at_job: int
    months_at_address: int


Decision = Literal["approve", "review", "deny"]
