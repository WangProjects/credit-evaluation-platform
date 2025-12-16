from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class DecisionEvent:
    event_type: str  # "decision"
    application_id: str
    request_id: str
    model_name: str
    model_version: str
    decision: str
    score: float
    decision_threshold: float
    reason_codes: list[str]
    created_at: datetime
    features: Optional[Dict[str, float]] = None
    features_hash: Optional[str] = None
    sensitive_attributes: Optional[Dict[str, str]] = None
    extra: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class OutcomeEvent:
    """
    Outcome events feed monitoring/retraining (e.g., repayment status).
    """

    event_type: str  # "outcome"
    application_id: str
    outcome_type: str  # e.g. "repayment_90d"
    outcome_value: int  # 1/0
    created_at: datetime
    extra: Optional[Dict[str, Any]] = None


