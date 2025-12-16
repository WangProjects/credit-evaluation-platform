from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from ice.audit.events import DecisionEvent, OutcomeEvent


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def hash_features(features: Dict[str, float]) -> str:
    raw = json.dumps(features, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def append_jsonl(path: str, event: Union[DecisionEvent, OutcomeEvent]) -> None:
    _ensure_dir(path)
    payload = asdict(event)
    # datetime -> ISO
    payload["created_at"] = event.created_at.replace(tzinfo=timezone.utc).isoformat()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


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


