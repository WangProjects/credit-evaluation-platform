from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    Environment variables use the prefix `FLG_`.
    """

    model_config = SettingsConfigDict(env_prefix="FLG_", case_sensitive=False)

    env: str = "local"
    host: str = "0.0.0.0"
    port: int = 8000

    # Artifact/model loading
    model_path: Path = Path("artifacts/model.joblib")

    # Audit logging
    audit_log_dir: Path = Path("logs")


settings = Settings()
