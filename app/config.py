from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = "FastAPI PostgreSQL Template"
    DEBUG: bool = False
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"
    HTTP_CLIENT_TIMEOUT: float = 30.0

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    RATE_LIMIT_TIMES: int = 100
    RATE_LIMIT_SECONDS: int = 60

    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("DATABASE_URL")
    @classmethod
    def database_url_must_be_set(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "DATABASE_URL is required"
            raise ValueError(msg)
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
