from __future__ import annotations

import os
from typing import Optional

from ice.models.sklearn_logreg import SklearnLogRegCreditModel, load_bundle
from ice.models.registry import get_current_entry, load_registry


class ModelStore:
    def __init__(self, registry_path: str, fallback_model_path: str) -> None:
        self.registry_path = registry_path
        self.fallback_model_path = fallback_model_path

    def current_model_path(self) -> str:
        entry = get_current_entry(self.registry_path)
        if entry and entry.get("artifact_path"):
            return str(entry["artifact_path"])
        return self.fallback_model_path

    def load_current_model(self) -> SklearnLogRegCreditModel:
        path = self.current_model_path()
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Model artifact not found at {path}. Run `python scripts/train_baseline.py` first."
            )
        bundle = load_bundle(path)
        return SklearnLogRegCreditModel(bundle)

    def model_info(self) -> dict:
        reg = load_registry(self.registry_path)
        return {
            "current": reg.get("current"),
            "entry": get_current_entry(self.registry_path),
        }


