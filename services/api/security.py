from __future__ import annotations

from fastapi import Header, HTTPException

from services.api.settings import api_settings


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """
    Minimal auth for demo purposes.

    If ICE_API_KEY is unset, auth is disabled.
    """
    settings = api_settings()
    if settings.api_key is None:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


