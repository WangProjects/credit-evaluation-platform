from __future__ import annotations

import uuid

from fastapi import Request


def get_or_create_request_id(request: Request) -> str:
    rid = request.headers.get("X-Request-Id")
    return rid or str(uuid.uuid4())


