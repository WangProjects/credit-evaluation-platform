from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib


@dataclass(frozen=True)
class ModelPackage:
    version: str
    model: Any
    feature_names: list[str]
    metadata: dict[str, Any]


def model_dir(registry_dir: str, version: str) -> Path:
    return Path(registry_dir) / version


def save_model_package(pkg: ModelPackage, registry_dir: str) -> Path:
    d = model_dir(registry_dir, pkg.version)
    d.mkdir(parents=True, exist_ok=True)
    joblib.dump(pkg.model, d / "model.joblib")
    (d / "feature_list.json").write_text(json.dumps(pkg.feature_names, indent=2), encoding="utf-8")
    (d / "metadata.json").write_text(json.dumps(pkg.metadata, indent=2), encoding="utf-8")
    if not (d / "APPROVED").exists():
        (d / "APPROVED").write_text("false\n", encoding="utf-8")
    return d


def load_model_package(registry_dir: str, version: str) -> ModelPackage:
    d = model_dir(registry_dir, version)
    model = joblib.load(d / "model.joblib")
    feature_names = json.loads((d / "feature_list.json").read_text(encoding="utf-8"))
    metadata = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
    return ModelPackage(version=version, model=model, feature_names=feature_names, metadata=metadata)


def is_approved(registry_dir: str, version: str) -> bool:
    d = model_dir(registry_dir, version)
    path = d / "APPROVED"
    if not path.exists():
        return False
    return path.read_text(encoding="utf-8").strip().lower() == "true"


def set_approved(registry_dir: str, version: str, approved: bool) -> None:
    d = model_dir(registry_dir, version)
    d.mkdir(parents=True, exist_ok=True)
    (d / "APPROVED").write_text(("true\n" if approved else "false\n"), encoding="utf-8")


