from typing import Literal
from pathlib import Path
from urllib.parse import quote_plus
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    """PostgreSQL database configuration"""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    user: str = Field(default="app_user")
    password: str = Field(default="postgres")
    db_name: str = Field(default="app_db")

    @property
    def url(self) -> str:
        """ PostgreSQL connection string"""
        pwd = quote_plus(self.password)  # process "/" or ":" in pwd
        return f"postgresql+asyncpg://{self.user}:{pwd}@{self.host}:{self.port}/{self.db_name}"


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=str(
            Path(__file__).parent.parent / ".env"),     # project roor .env
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # DB__HOST in .env
    )

    debug: bool = False     # debug mode
    env: Literal["dev", "staging", "prod"] = "prod"

    # Database
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    @property
    def database_url(self) -> str:
        """Database connection URL"""
        return self.database.url


settings = Settings()
