from __future__ import annotations

from typing import Any

import numpy as np


def reason_codes_from_linear_model(
    *,
    feature_names: list[str],
    x: np.ndarray,
    model: Any,
    top_k: int = 4,
) -> list[dict]:
    """Generate simple reason codes.

    For a scaled logistic regression pipeline, reason codes are computed from
    coefficients and the input vector. This is a *technical* explanation,
    and should be adapted to match institution-specific adverse action
    notice requirements.
    """

    # Try to support either:
    # - a raw linear model with coef_
    # - a sklearn Pipeline where the last step has coef_
    coef = None
    intercept = None

    if hasattr(model, "coef_"):
        coef = np.asarray(model.coef_).reshape(-1)
        intercept = float(np.asarray(model.intercept_).reshape(-1)[0])
    elif hasattr(model, "named_steps"):
        # Pipeline
        last = list(model.named_steps.values())[-1]
        if hasattr(last, "coef_"):
            coef = np.asarray(last.coef_).reshape(-1)
            intercept = float(np.asarray(last.intercept_).reshape(-1)[0])

    if coef is None:
        return [
            {
                "code": "UNAVAILABLE",
                "feature": "",
                "direction": "",
                "contribution": 0.0,
            }
        ]

    # Contribution proxy: coefficient * feature value
    contrib = coef * x
    order = np.argsort(np.abs(contrib))[::-1][:top_k]

    reasons: list[dict] = []
    for idx in order:
        c = float(contrib[idx])
        reasons.append(
            {
                "code": f"RC_{feature_names[idx].upper()}",
                "feature": feature_names[idx],
                "direction": "increases" if c >= 0 else "decreases",
                "contribution": abs(c),
            }
        )

    # Include intercept as metadata in the first reason when useful.
    if reasons:
        reasons[0]["_intercept"] = intercept

    return reasons
