from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException

from flg.config import settings
from flg.explainability.reason_codes import reason_codes_from_linear_model
from flg.fairness.metrics import group_fairness_report
from flg.features.schema import FEATURE_ORDER, validate_feature_vector
from flg.governance.audit import AuditLogger
from flg.logging import configure_logging
from flg.ml.model import CreditModelBundle
from flg.schemas import (
    ExplainRequest,
    ExplainResponse,
    FairnessReportRequest,
    FairnessReportResponse,
    ScoreRequest,
    ScoreResponse,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Inclusive Credit Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


def _load_bundle(path: Path) -> CreditModelBundle:
    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {path}. Run: flg-train --out {path}"
        )
    return joblib.load(path)


@app.on_event("startup")
def _startup() -> None:
    configure_logging()
    logger.info(
        "startup",
        extra={"env": settings.env, "model_path": str(settings.model_path), "audit_dir": str(settings.audit_log_dir)},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _decision(score: float, thresholds: dict[str, float]) -> str:
    if score >= float(thresholds.get("approve", 0.7)):
        return "approve"
    if score >= float(thresholds.get("review", 0.55)):
        return "review"
    return "deny"


@app.post("/v1/score", response_model=ScoreResponse)
def score(req: ScoreRequest) -> ScoreResponse:
    try:
        x = validate_feature_vector(req.features)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(e))

    try:
        bundle = _load_bundle(settings.model_path)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))

    score_value = bundle.predict_proba_one(x)
    decision = _decision(score_value, bundle.thresholds)

    reasons = reason_codes_from_linear_model(
        feature_names=list(bundle.feature_order),
        x=x,
        model=bundle.model,
        top_k=4,
    )

    audit = AuditLogger(settings.audit_log_dir)
    audit_id = audit.write_score_event(
        applicant_id=req.applicant_id,
        model_version=bundle.model_version,
        features={k: req.features[k] for k in FEATURE_ORDER},
        protected_attributes=req.protected_attributes.model_dump() if req.protected_attributes else None,
        output={"score": score_value, "decision": decision, "reasons": reasons},
    )

    return ScoreResponse(
        applicant_id=req.applicant_id,
        model_version=bundle.model_version,
        score=score_value,
        decision=decision,  # type: ignore[arg-type]
        reasons=reasons,
        audit_id=audit_id,
    )


@app.post("/v1/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest) -> ExplainResponse:
    try:
        x = validate_feature_vector(req.features)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(e))

    bundle = _load_bundle(settings.model_path)

    # Minimal: coefficient-based contribution proxy (matches /score reason codes)
    reasons = reason_codes_from_linear_model(
        feature_names=list(bundle.feature_order),
        x=x,
        model=bundle.model,
        top_k=len(bundle.feature_order),
    )

    return ExplainResponse(
        applicant_id=req.applicant_id,
        model_version=bundle.model_version,
        method="linear_coefficient_proxy",
        explanations={"reasons": reasons},
    )


@app.post("/v1/fairness/report", response_model=FairnessReportResponse)
def fairness_report(req: FairnessReportRequest) -> FairnessReportResponse:
    bundle = _load_bundle(settings.model_path)

    y_true = np.asarray([r.y_true for r in req.rows], dtype=int)
    y_score = np.asarray([r.y_score for r in req.rows], dtype=float)
    group = np.asarray([r.group for r in req.rows], dtype=str)

    metrics: dict[str, Any] = group_fairness_report(y_true=y_true, y_score=y_score, group=group)

    return FairnessReportResponse(model_version=bundle.model_version, metrics=metrics)


def run() -> None:
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    run()
