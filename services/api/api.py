from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from ice.audit.events import DecisionEvent, OutcomeEvent
from ice.audit.store import append_jsonl, hash_features, insert_sqlite_decision, insert_sqlite_outcome, utcnow
from ice.explain.explainer import explain
from ice.explain.reason_codes import generate_reason_codes
from ice.features.transform import sanitize_features, to_model_vector
from services.api.schemas import (
    ExplainRequest,
    ExplainResponse,
    ModelInfo,
    OutcomeEventIn,
    ScoreRequest,
    ScoreResponse,
)
from services.api.security import require_api_key
from services.api.settings import api_settings
from services.api.storage import ModelStore


router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


def _store() -> ModelStore:
    s = api_settings()
    return ModelStore(registry_path=s.registry_path, fallback_model_path=s.current_model_path)


@router.get("/models/current", response_model=ModelInfo)
def get_current_model_info() -> dict:
    return _store().model_info()


@router.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest) -> ScoreResponse:
    settings = api_settings()
    model = _store().load_current_model()

    features = sanitize_features(req.features)
    try:
        x = to_model_vector(model.contract, features)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    score_val = model.predict_proba(x)
    decision = "approve" if score_val >= settings.decision_threshold else "deny"
    reason_codes = generate_reason_codes(features)

    request_id = req.request_id or str(uuid.uuid4())
    created_at = utcnow()

    # Audit event
    f_hash = hash_features(features)
    event = DecisionEvent(
        event_type="decision",
        application_id=req.application_id,
        request_id=request_id,
        model_name=model.metadata.name,
        model_version=model.metadata.version,
        decision=decision,
        score=float(score_val),
        decision_threshold=float(settings.decision_threshold),
        reason_codes=reason_codes,
        created_at=created_at,
        features=features if settings.log_raw_features else None,
        features_hash=f_hash,
        sensitive_attributes=req.sensitive_attributes if settings.store_sensitive_for_monitoring else None,
        extra={},
    )
    append_jsonl(settings.audit_log_path, event)
    if settings.enable_sqlite_audit_store:
        insert_sqlite_decision(settings.audit_sqlite_path, event)

    return ScoreResponse(
        application_id=req.application_id,
        request_id=request_id,
        model_name=model.metadata.name,
        model_version=model.metadata.version,
        feature_schema_hash=model.metadata.feature_schema_hash,
        score=float(score_val),
        decision=decision,
        decision_threshold=float(settings.decision_threshold),
        reason_codes=reason_codes,
        created_at=created_at.replace(tzinfo=timezone.utc).isoformat(),
        extra={},
    )


@router.post("/explain", response_model=ExplainResponse)
def explain_endpoint(req: ExplainRequest) -> ExplainResponse:
    model = _store().load_current_model()
    features = sanitize_features(req.features)
    try:
        x = to_model_vector(model.contract, features)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    expl = explain(model, x)
    if expl is None:
        raise HTTPException(status_code=501, detail="Explanation not available for current model.")

    created_at = datetime.now(timezone.utc).isoformat()
    return ExplainResponse(
        application_id=req.application_id,
        model_name=model.metadata.name,
        model_version=model.metadata.version,
        method=expl.method,
        created_at=created_at,
        contributions=expl.contributions,
        base_value=expl.base_value,
    )


@router.post("/audit/events")
def ingest_outcome(event_in: OutcomeEventIn) -> dict:
    settings = api_settings()
    event = OutcomeEvent(
        event_type="outcome",
        application_id=event_in.application_id,
        outcome_type=event_in.outcome_type,
        outcome_value=int(event_in.outcome_value),
        created_at=utcnow(),
        extra=event_in.extra,
    )
    append_jsonl(settings.audit_log_path, event)
    if settings.enable_sqlite_audit_store:
        insert_sqlite_outcome(settings.audit_sqlite_path, event)
    return {"status": "ok"}


