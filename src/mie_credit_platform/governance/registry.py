from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mie_credit_platform.modeling.model_io import is_approved, load_model_package, model_dir, set_approved


@dataclass(frozen=True)
class ModelInfo:
    version: str
    approved: bool
    metadata: dict[str, Any] | None


def list_models(registry_dir: str) -> list[ModelInfo]:
    d = Path(registry_dir)
    if not d.exists():
        return []
    out: list[ModelInfo] = []
    for child in sorted([p for p in d.iterdir() if p.is_dir()], key=lambda p: p.name):
        md_path = child / "metadata.json"
        md = json.loads(md_path.read_text(encoding="utf-8")) if md_path.exists() else None
        out.append(ModelInfo(version=child.name, approved=is_approved(registry_dir, child.name), metadata=md))
    return out


def approve_model(registry_dir: str, version: str, approved: bool = True) -> None:
    set_approved(registry_dir, version, approved)


def assert_model_ready(registry_dir: str, version: str) -> None:
    d = model_dir(registry_dir, version)
    if not d.exists():
        raise FileNotFoundError(f"Model version not found: {version} in {registry_dir}")
    for required in ["model.joblib", "feature_list.json", "metadata.json"]:
        if not (d / required).exists():
            raise FileNotFoundError(f"Missing required artifact: {d / required}")


def load_approved_model(registry_dir: str, version: str, require_approval: bool) -> Any:
    assert_model_ready(registry_dir, version)
    if require_approval and not is_approved(registry_dir, version):
        raise PermissionError(f"Model version {version} is not approved (see {model_dir(registry_dir, version)})")
    return load_model_package(registry_dir, version)


