from __future__ import annotations

from ice.config import Settings, get_settings


def api_settings() -> Settings:
    # reuse core settings for now
    return get_settings()


