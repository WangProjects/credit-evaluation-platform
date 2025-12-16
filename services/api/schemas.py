from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    application_id: str = Field(..., min_length=1)
    features: Dict[str, float]
    sensitive_attributes: Optional[Dict[str, str]] = None
    request_id: Optional[str] = None


class ScoreResponse(BaseModel):
    application_id: str
    request_id: str
    model_name: str
    model_version: str
    feature_schema_hash: str
    score: float
    decision: str
    decision_threshold: float
    reason_codes: list[str]
    created_at: str
    extra: Dict[str, Any] = {}


class ExplainRequest(BaseModel):
    application_id: str = Field(..., min_length=1)
    features: Dict[str, float]


class ExplainResponse(BaseModel):
    application_id: str
    model_name: str
    model_version: str
    method: str
    created_at: str
    contributions: Dict[str, float]
    base_value: Optional[float] = None


class OutcomeEventIn(BaseModel):
    application_id: str = Field(..., min_length=1)
    outcome_type: str = Field(..., min_length=1)
    outcome_value: int = Field(..., ge=0, le=1)
    extra: Optional[Dict[str, Any]] = None


class ModelInfo(BaseModel):
    current: Optional[Dict[str, str]]
    entry: Optional[Dict[str, Any]]


