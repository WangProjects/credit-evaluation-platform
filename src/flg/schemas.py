from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from flg.types import Decision


class ProtectedAttributes(BaseModel):
    # In real deployments, treat these with extreme care.
    # This demo uses a single group label to compute group metrics.
    group: str = Field(..., description="Group label used for fairness reporting")


class ScoreRequest(BaseModel):
    applicant_id: str
    features: dict[str, Any]
    protected_attributes: ProtectedAttributes | None = None


class ReasonCode(BaseModel):
    code: str
    feature: str
    direction: str
    contribution: float


class ScoreResponse(BaseModel):
    applicant_id: str
    model_version: str
    score: float = Field(..., ge=0.0, le=1.0)
    decision: Decision
    reasons: list[ReasonCode]
    audit_id: str


class ExplainRequest(BaseModel):
    applicant_id: str
    features: dict[str, Any]


class ExplainResponse(BaseModel):
    applicant_id: str
    model_version: str
    method: str
    explanations: dict[str, Any]


class FairnessRow(BaseModel):
    y_true: int = Field(..., description="Outcome label: 1 good outcome, 0 bad outcome")
    y_score: float = Field(..., ge=0.0, le=1.0)
    group: str


class FairnessReportRequest(BaseModel):
    rows: list[FairnessRow]


class FairnessReportResponse(BaseModel):
    model_version: str
    metrics: dict[str, Any]
