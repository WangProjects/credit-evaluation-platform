from __future__ import annotations

from fastapi import Depends, HTTPException, Header

from mie_credit_platform.settings import Settings, get_settings


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.require_api_key:
        return
    if not settings.api_key:
        raise HTTPException(status_code=500, detail="API key enforcement enabled but MIE_API_KEY not set")
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


