from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


Features = Dict[str, float]
SensitiveAttributes = Dict[str, str]


@dataclass(frozen=True)
class ScoreResult:
    application_id: str
    model_version: str
    score: float
    decision: str  # "approve" | "deny" | "review"
    decision_threshold: float
    reason_codes: list[str]
    created_at: datetime
    extra: Dict[str, Any]


@dataclass(frozen=True)
class ExplanationResult:
    application_id: str
    model_version: str
    contributions: Dict[str, float]
    base_value: Optional[float]
    method: str
    created_at: datetime


