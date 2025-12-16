from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import orjson


def _stable_hash(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass
class AuditLogger:
    dir: Path

    def __post_init__(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)

    def write_score_event(
        self,
        *,
        applicant_id: str,
        model_version: str,
        features: dict[str, Any],
        protected_attributes: dict[str, Any] | None,
        output: dict[str, Any],
        request_id: str | None = None,
    ) -> str:
        audit_id = str(uuid.uuid4())
        ts = datetime.now(timezone.utc).isoformat()

        event = {
            "audit_id": audit_id,
            "timestamp": ts,
            "request_id": request_id,
            "applicant_id": applicant_id,
            "model_version": model_version,
            "feature_order_hash": _stable_hash(sorted(list(features.keys()))),
            "features_hash": _stable_hash(features),
            "protected_attributes": protected_attributes,
            "output": output,
        }

        # JSONL per day (simple local default)
        day = ts[:10]
        path = self.dir / f"audit-{day}.jsonl"
        with path.open("ab") as f:
            f.write(orjson.dumps(event))
            f.write(b"\n")

        return audit_id
