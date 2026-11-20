from __future__ import annotations

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DeployMode = Literal["lab", "demo"]

STORAGE_DISCLAIMER = (
    "Данные только в RAM процесса API: перезапуск или reset уничтожает изменения. "
    "Персистентного хранилища и бэкапа нет."
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STRATUM_", env_file=".env", extra="ignore")

    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:4173,http://127.0.0.1:4173"
    )
    host: str = "0.0.0.0"
    port: int = 8000
    # If non-empty, all /api/* except /api/health require Authorization: Bearer …
    api_token: str = ""
    # Shared/prod stand: forbid destructive reset even with a valid token
    disable_reset: bool = False
    # lab = open product lab; demo = shared stand (token + no reset recommended)
    deploy_mode: DeployMode = "lab"

    @field_validator("deploy_mode", mode="before")
    @classmethod
    def _normalize_mode(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_token.strip())


settings = Settings()
