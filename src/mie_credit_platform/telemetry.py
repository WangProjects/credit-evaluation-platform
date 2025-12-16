from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.time(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # Attach extra fields if present
        for key, value in record.__dict__.items():
            if key.startswith("_"):
                continue
            if key in {"args", "msg", "levelname", "levelno", "name", "exc_info", "exc_text"}:
                continue
            if key in {"pathname", "filename", "module", "lineno", "funcName"}:
                continue
            if key in {"created", "msecs", "relativeCreated", "thread", "threadName", "process"}:
                continue
            if key in {"processName", "stack_info"}:
                continue
            if key not in payload:
                payload[key] = value
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(level)


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    applicant_id: str | None = None


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.info(event, extra=fields)


