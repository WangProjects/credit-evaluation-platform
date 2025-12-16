from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ice.models.base import ModelMetadata


@dataclass(frozen=True)
class RegistryEntry:
    name: str
    version: str
    artifact_path: str
    created_at: str
    feature_schema_hash: str
    decision_threshold: float
    metrics: Dict[str, Any]
    fairness: Dict[str, Any]
    notes: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_registry(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"current": None, "models": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(path: str, registry: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, sort_keys=True)


def add_model(
    registry_path: str,
    metadata: ModelMetadata,
    artifact_path: str,
    metrics: Optional[Dict[str, Any]] = None,
    fairness: Optional[Dict[str, Any]] = None,
    notes: str = "",
    set_current: bool = True,
) -> RegistryEntry:
    reg = load_registry(registry_path)
    entry = RegistryEntry(
        name=metadata.name,
        version=metadata.version,
        artifact_path=artifact_path,
        created_at=_now_iso(),
        feature_schema_hash=metadata.feature_schema_hash,
        decision_threshold=metadata.decision_threshold,
        metrics=metrics or {},
        fairness=fairness or {},
        notes=notes,
    )
    reg.setdefault("models", []).append(asdict(entry))
    if set_current:
        reg["current"] = {"name": entry.name, "version": entry.version}
    save_registry(registry_path, reg)
    return entry


def get_current_entry(registry_path: str) -> Optional[Dict[str, Any]]:
    reg = load_registry(registry_path)
    current = reg.get("current")
    if not current:
        return None
    for m in reg.get("models", []):
        if m.get("name") == current.get("name") and m.get("version") == current.get("version"):
            return m
    return None


