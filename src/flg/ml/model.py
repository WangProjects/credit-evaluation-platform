from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator

from flg.features.schema import FEATURE_ORDER


@dataclass(frozen=True)
class CreditModelBundle:
    """Serializable bundle for model + metadata.

    Store only what you need for deterministic inference + audit.
    """

    model: BaseEstimator
    model_version: str
    trained_at: str
    feature_order: list[str]
    thresholds: dict[str, float]
    extra: dict[str, Any]

    @staticmethod
    def build(model: BaseEstimator, *, model_version: str, thresholds: dict[str, float] | None = None) -> "CreditModelBundle":
        now = datetime.now(timezone.utc).isoformat()
        return CreditModelBundle(
            model=model,
            model_version=model_version,
            trained_at=now,
            feature_order=list(FEATURE_ORDER),
            thresholds=thresholds or {"approve": 0.70, "review": 0.55},
            extra={},
        )

    def predict_proba_one(self, x: np.ndarray) -> float:
        proba = self.model.predict_proba(x.reshape(1, -1))
        return float(proba[0, 1])
