from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from mie_credit_platform.modeling.model_io import ModelPackage


@dataclass(frozen=True)
class ScoreResult:
    score: float
    decision: str
    reason_codes: list[str]


def score_applicant(
    pkg: ModelPackage, features: dict[str, float], threshold: float
) -> tuple[ScoreResult, dict[str, Any]]:
    x = _vectorize(features, pkg.feature_names)
    proba = float(pkg.model.predict_proba(x)[0, 1])
    decision = "APPROVE" if proba >= threshold else "REVIEW"
    explanation = explain_linear_if_possible(pkg, features)
    reason_codes = explanation.get("reason_codes", [])
    return ScoreResult(score=proba, decision=decision, reason_codes=reason_codes), explanation


def _vectorize(features: dict[str, float], feature_names: list[str]) -> np.ndarray:
    row = [float(features.get(k, 0.0)) for k in feature_names]
    return np.asarray([row], dtype=float)


def explain_linear_if_possible(pkg: ModelPackage, features: dict[str, float]) -> dict[str, Any]:
    """
    Best-effort explanation for sklearn Pipeline(StandardScaler -> LogisticRegression).
    Falls back to empty explanation for other model types.
    """

    model = pkg.model
    if not hasattr(model, "named_steps"):
        return {}
    steps = model.named_steps
    if "scaler" not in steps or "clf" not in steps:
        return {}
    scaler = steps["scaler"]
    clf = steps["clf"]
    if not hasattr(clf, "coef_") or not hasattr(clf, "intercept_"):
        return {}

    feature_names = pkg.feature_names
    x_raw = np.asarray([float(features.get(k, 0.0)) for k in feature_names], dtype=float)
    x_scaled = (x_raw - scaler.mean_) / scaler.scale_
    coefs = clf.coef_[0]
    intercept = float(clf.intercept_[0])

    contrib = coefs * x_scaled
    logit = intercept + float(np.sum(contrib))
    score = float(1 / (1 + math.exp(-logit)))

    rows = []
    for name, val, w, c in zip(feature_names, x_raw, coefs, contrib, strict=True):
        rows.append({"feature": name, "value": float(val), "weight": float(w), "contribution": float(c)})

    # Reason codes: show the most negative contributors as "drivers of risk"
    rows_sorted = sorted(rows, key=lambda r: r["contribution"])
    worst = rows_sorted[:3]
    reason_codes = [f"HIGH_RISK_SIGNAL:{r['feature']}" for r in worst]

    return {
        "explain_type": "linear_logit_contributions",
        "base_value": intercept,
        "score_from_explanation": score,
        "contributions": rows,
        "reason_codes": reason_codes,
    }


