from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Africand Intelligence"
    environment: str = "development"

    database_url: str = "sqlite:///./africand_intelligence.db"

    ai_provider: str = "mock"  # mock | openai | anthropic
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12

    admin_email: str = "admin@africand.com"
    admin_password: str = "change-me-in-production"

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
