from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseModel):
    """PostgreSQL database configuration"""

    host: str = Field(default="postgres", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="app_user", alias="POSTGRES_APP_USER")
    db: str = Field(default="app_db", alias="POSTGRES_APP_DB")
    password: str = Field(default="postgres", alias="POSTGRES_APP_PASSWORD")

    @property
    def url(self) -> str:
        """ PostgreSQL connection string"""
        user = quote_plus(self.user)        # process "/" or ":" in pwd
        pwd = quote_plus(self.password)     # process "/" or ":" in pwd
        return f"postgresql+asyncpg://{user}:{pwd}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseModel):
    """Redis configuration"""

    host: str = Field(default="redis", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = Field(default=0, alias="REDIS_DB")
    password: str | None = Field(default=None, alias="REDIS_PASSWORD")

    @property
    def url(self) -> str:
        if self.password:
            pwd = quote_plus(self.password)
            return f"redis://:{pwd}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    """Application settings"""

    app_name: str = Field(default="Demo Iot management", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")
    env: Literal["dev", "staging", "prod"] = Field(default="dev", alias="ENV")

    model_config = SettingsConfigDict(
        env_file=str(
            Path(__file__).parent.parent.parent / ".env"),     # project root .env
        env_file_encoding="utf-8",
        extra="ignore",         # ignore extra fields:
    )

    # Database
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    # Redis
    redis: RedisSettings = Field(default_factory=RedisSettings)

    @property
    def postgres_url(self) -> str:
        """Postgres connection URL"""
        return self.postgres.url

    @property
    def redis_url(self) -> str:
        """Redis connection URL"""
        return self.redis.url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached Settings instance.
    """
    return Settings()
