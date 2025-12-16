from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from ice.features.contract import DEFAULT_CONTRACT, FeatureContract
from ice.models.base import CreditModel, ModelMetadata


@dataclass(frozen=True)
class SklearnLogRegBundle:
    model: LogisticRegression
    contract: FeatureContract
    name: str
    version: str
    decision_threshold: float


class SklearnLogRegCreditModel(CreditModel):
    def __init__(self, bundle: SklearnLogRegBundle) -> None:
        self._bundle = bundle
        self._meta = ModelMetadata(
            name=bundle.name,
            version=bundle.version,
            feature_schema_hash=bundle.contract.schema_hash(),
            decision_threshold=bundle.decision_threshold,
        )

    @property
    def contract(self) -> FeatureContract:
        return self._bundle.contract

    @property
    def metadata(self) -> ModelMetadata:
        return self._meta

    def predict_proba(self, x: np.ndarray) -> float:
        proba = self._bundle.model.predict_proba(x.reshape(1, -1))[0, 1]
        return float(proba)

    def explain_linear(self, x: np.ndarray, feature_names: list[str]) -> Optional[Dict[str, float]]:
        # For logistic regression, use coefficient * feature as an interpretable proxy.
        coef = self._bundle.model.coef_.reshape(-1)
        contrib = {fn: float(coef[i] * x[i]) for i, fn in enumerate(feature_names)}
        return contrib


def save_bundle(path: str, bundle: SklearnLogRegBundle) -> None:
    joblib.dump(bundle, path)


def load_bundle(path: str) -> SklearnLogRegBundle:
    bundle = joblib.load(path)
    if not isinstance(bundle, SklearnLogRegBundle):
        raise TypeError(f"Expected SklearnLogRegBundle at {path}, got {type(bundle)}")
    return bundle


def new_untrained_bundle(version: str = "0.0.1", decision_threshold: float = 0.5) -> SklearnLogRegBundle:
    model = LogisticRegression(max_iter=200)
    return SklearnLogRegBundle(
        model=model,
        contract=DEFAULT_CONTRACT,
        name="sklearn_logreg_baseline",
        version=version,
        decision_threshold=decision_threshold,
    )


