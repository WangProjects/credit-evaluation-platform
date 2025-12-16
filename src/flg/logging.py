from __future__ import annotations

import logging
import sys

from pythonjsonlogger.json import jsonlogger


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "name": "logger"},
    )
    handler.setFormatter(formatter)

    # Replace existing handlers to avoid duplicate logs under uvicorn reload.
    root.handlers = [handler]
