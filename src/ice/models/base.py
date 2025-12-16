from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from ice.features.contract import FeatureContract


@dataclass(frozen=True)
class ModelMetadata:
    name: str
    version: str
    feature_schema_hash: str
    decision_threshold: float


class CreditModel(ABC):
    @property
    @abstractmethod
    def contract(self) -> FeatureContract: ...

    @property
    @abstractmethod
    def metadata(self) -> ModelMetadata: ...

    @abstractmethod
    def predict_proba(self, x: np.ndarray) -> float: ...

    def explain_linear(self, x: np.ndarray, feature_names: list[str]) -> Optional[Dict[str, float]]:
        """
        Optional: return per-feature contribution for linear models.
        """
        return None


