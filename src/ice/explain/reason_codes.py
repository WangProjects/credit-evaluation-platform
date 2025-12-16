from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class ReasonCode:
    code: str
    description: str


REASONS: Dict[str, ReasonCode] = {
    "RC_LOW_RENT_ON_TIME": ReasonCode(
        code="RC_LOW_RENT_ON_TIME",
        description="Recent rent payment history indicates lower on-time payment consistency.",
    ),
    "RC_LOW_UTIL_ON_TIME": ReasonCode(
        code="RC_LOW_UTIL_ON_TIME",
        description="Recent utility payment history indicates lower on-time payment consistency.",
    ),
    "RC_HIGH_CASHFLOW_VOL": ReasonCode(
        code="RC_HIGH_CASHFLOW_VOL",
        description="Cash-flow patterns show higher volatility, increasing repayment uncertainty.",
    ),
    "RC_LOW_INCOME": ReasonCode(
        code="RC_LOW_INCOME",
        description="Verified income indicators suggest limited repayment capacity at this time.",
    ),
    "RC_LOW_BALANCE": ReasonCode(
        code="RC_LOW_BALANCE",
        description="Average account balance indicates limited buffer for repayment shocks.",
    ),
    "RC_NSF_EVENTS": ReasonCode(
        code="RC_NSF_EVENTS",
        description="Non-sufficient funds events were observed in recent history.",
    ),
    "RC_OVERDRAFT_EVENTS": ReasonCode(
        code="RC_OVERDRAFT_EVENTS",
        description="Overdraft events were observed in recent history.",
    ),
}


def generate_reason_codes(features: Dict[str, float], max_codes: int = 4) -> List[str]:
    """
    Heuristic reason-code generator for demo purposes.

    Real production systems should use:
    - consistent policy definitions
    - documented thresholds
    - monotonic relationships where applicable
    - validated adverse-action style reason selection logic
    """
    scored: List[Tuple[str, float]] = []

    rent = float(features.get("rent_on_time_rate_12m", 1.0))
    util = float(features.get("utility_on_time_rate_12m", 1.0))
    income = float(features.get("avg_monthly_income_6m", 0.0))
    vol = float(features.get("cashflow_volatility_6m", 0.0))
    bal = float(features.get("avg_daily_balance_6m", 0.0))
    nsf = float(features.get("nsf_events_12m", 0.0))
    od = float(features.get("overdraft_events_12m", 0.0))

    if rent < 0.92:
        scored.append(("RC_LOW_RENT_ON_TIME", 0.92 - rent))
    if util < 0.92:
        scored.append(("RC_LOW_UTIL_ON_TIME", 0.92 - util))
    if vol > 0.25:
        scored.append(("RC_HIGH_CASHFLOW_VOL", vol - 0.25))
    if income < 3000:
        scored.append(("RC_LOW_INCOME", 3000 - income))
    if bal < 500:
        scored.append(("RC_LOW_BALANCE", 500 - bal))
    if nsf > 0:
        scored.append(("RC_NSF_EVENTS", nsf))
    if od > 0:
        scored.append(("RC_OVERDRAFT_EVENTS", od))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [code for code, _ in scored[:max_codes]]


