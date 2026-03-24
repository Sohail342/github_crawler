"""Application configuration."""

from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    DOMAIN: str = "domain.com"

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "github_crawler"
    PROJECT_DESCRIPTION: str = "github_crawler"

    GITHUB_TOKEN: Optional[str] = None
    GITHUB_ENDPOINT: str = "https://api.github.com/graphql"

    DATABASE_URL: Optional[str] = None
    SYNC_DATABASE_URL: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        """Set default DB URLs if missing."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                "sqlite+aiosqlite:///./app.db"
                if self.ENVIRONMENT == "development"
                else "postgresql+asyncpg://postgres:postgres@db:5432/crawler_db"
            )
        if not self.SYNC_DATABASE_URL:
            self.SYNC_DATABASE_URL = (
                "sqlite:///./app.db"
                if self.ENVIRONMENT == "development"
                else "postgresql://postgres:postgres@db:5432/crawler_db"
            )

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
