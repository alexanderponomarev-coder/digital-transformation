from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_token.strip())


settings = Settings()
