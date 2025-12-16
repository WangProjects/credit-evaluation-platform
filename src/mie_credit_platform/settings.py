from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the platform.

    Defaults are intentionally conservative and local-first.
    """

    model_config = SettingsConfigDict(env_prefix="MIE_", env_file=".env", extra="ignore")

    # Model / registry
    model_registry_dir: str = "models"
    model_version: str = "v0.1.0"

    # API
    environment: str = "dev"
    require_api_key: bool = False
    api_key: str | None = None

    # Decisions
    approval_threshold: float = 0.60

    # Audit logging
    audit_db_path: str = "data/audit.sqlite3"
    audit_jsonl_path: str = "data/audit.jsonl"
    audit_log_request_bodies: bool = False


def get_settings() -> Settings:
    return Settings()


