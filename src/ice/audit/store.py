from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from ice.audit.events import DecisionEvent, GenericAuditEvent, OutcomeEvent


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def hash_features(features: Dict[str, float]) -> str:
    raw = json.dumps(features, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def append_jsonl(path: str, event: Union[DecisionEvent, OutcomeEvent, GenericAuditEvent]) -> None:
    _ensure_dir(path)
    payload = asdict(event)
    # datetime -> ISO
    payload["created_at"] = event.created_at.replace(tzinfo=timezone.utc).isoformat()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


def parse_created_at(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_jsonl_events(path: str) -> list[Dict[str, Any]]:
    if not os.path.exists(path):
        return []

    events: list[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            raw = line.strip()
            if not raw:
                continue
            event = json.loads(raw)
            event["_line_number"] = line_number
            events.append(event)
    return events


def normalize_audit_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    if "payload" in event and isinstance(event["payload"], dict):
        return dict(event["payload"])

    event_type = event.get("event_type")
    if event_type == "decision":
        return {
            "score": event.get("score"),
            "decision": event.get("decision"),
            "decision_threshold": event.get("decision_threshold"),
            "reason_codes": event.get("reason_codes", []),
            "features_hash": event.get("features_hash"),
        }
    if event_type == "outcome":
        return {
            "outcome_type": event.get("outcome_type"),
            "outcome_value": event.get("outcome_value"),
        }

    return {
        key: value
        for key, value in event.items()
        if key
        not in {
            "_line_number",
            "application_id",
            "created_at",
            "event_type",
            "model_name",
            "model_version",
            "request_id",
        }
    }


def list_jsonl_events(
    path: str,
    limit: int = 100,
    offset: int = 0,
    event_type: Optional[str] = None,
    application_id: Optional[str] = None,
    request_id: Optional[str] = None,
    model_version: Optional[str] = None,
) -> Dict[str, Any]:
    filtered: list[Dict[str, Any]] = []
    for event in load_jsonl_events(path):
        if event_type and event.get("event_type") != event_type:
            continue
        if application_id and event.get("application_id") != application_id:
            continue
        if request_id and event.get("request_id") != request_id:
            continue
        if model_version and event.get("model_version") != model_version:
            continue
        filtered.append(event)

    filtered.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    total = len(filtered)
    page = filtered[offset : offset + limit]
    records = [
        {
            "id": f"audit-{event.get('_line_number', index + 1)}",
            "created_at": event.get("created_at"),
            "ts": parse_created_at(event["created_at"]).timestamp() if event.get("created_at") else 0.0,
            "event_type": event.get("event_type", "unknown"),
            "request_id": event.get("request_id"),
            "application_id": event.get("application_id"),
            "model_name": event.get("model_name"),
            "model_version": event.get("model_version"),
            "payload": normalize_audit_payload(event),
        }
        for index, event in enumerate(page)
    ]
    return {"total": total, "events": records}


def init_sqlite(path: str) -> None:
    _ensure_dir(path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS decision_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL,
          application_id TEXT NOT NULL,
          request_id TEXT NOT NULL,
          model_name TEXT NOT NULL,
          model_version TEXT NOT NULL,
          decision TEXT NOT NULL,
          score REAL NOT NULL,
          decision_threshold REAL NOT NULL,
          reason_codes TEXT NOT NULL,
          features_hash TEXT,
          features_json TEXT,
          sensitive_json TEXT,
          extra_json TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS outcome_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL,
          application_id TEXT NOT NULL,
          outcome_type TEXT NOT NULL,
          outcome_value INTEGER NOT NULL,
          extra_json TEXT
        )
        """
    )
    con.commit()
    con.close()


def insert_sqlite_decision(path: str, event: DecisionEvent) -> None:
    init_sqlite(path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO decision_events (
          created_at, application_id, request_id, model_name, model_version,
          decision, score, decision_threshold, reason_codes,
          features_hash, features_json, sensitive_json, extra_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.created_at.replace(tzinfo=timezone.utc).isoformat(),
            event.application_id,
            event.request_id,
            event.model_name,
            event.model_version,
            event.decision,
            float(event.score),
            float(event.decision_threshold),
            json.dumps(event.reason_codes),
            event.features_hash,
            json.dumps(event.features) if event.features is not None else None,
            json.dumps(event.sensitive_attributes) if event.sensitive_attributes is not None else None,
            json.dumps(event.extra) if event.extra is not None else None,
        ),
    )
    con.commit()
    con.close()


def insert_sqlite_outcome(path: str, event: OutcomeEvent) -> None:
    init_sqlite(path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO outcome_events (created_at, application_id, outcome_type, outcome_value, extra_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event.created_at.replace(tzinfo=timezone.utc).isoformat(),
            event.application_id,
            event.outcome_type,
            int(event.outcome_value),
            json.dumps(event.extra) if event.extra is not None else None,
        ),
    )
    con.commit()
    con.close()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)

