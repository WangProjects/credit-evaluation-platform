from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class AuditEvent:
    ts: float
    request_id: str
    event_type: str
    model_version: str | None
    applicant_id: str | None
    payload: dict[str, Any]


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL,
  request_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  model_version TEXT,
  applicant_id TEXT,
  payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_events_request_id ON audit_events(request_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_ts ON audit_events(ts);
"""


class AuditLogger:
    def __init__(self, db_path: str, jsonl_path: str | None = None) -> None:
        self.db_path = db_path
        self.jsonl_path = jsonl_path
        self._init_storage()

    def _init_storage(self) -> None:
        Path(os.path.dirname(self.db_path) or ".").mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        if self.jsonl_path:
            Path(os.path.dirname(self.jsonl_path) or ".").mkdir(parents=True, exist_ok=True)
            Path(self.jsonl_path).touch(exist_ok=True)

    def write(self, event: AuditEvent) -> None:
        payload_json = json.dumps(event.payload, default=str)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO audit_events (ts, request_id, event_type, model_version, applicant_id, payload_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (event.ts, event.request_id, event.event_type, event.model_version, event.applicant_id, payload_json),
            )
            conn.commit()

        if self.jsonl_path:
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(event), default=str) + "\n")

    def write_many(self, events: Iterable[AuditEvent]) -> None:
        for e in events:
            self.write(e)


def now_ts() -> float:
    return time.time()


