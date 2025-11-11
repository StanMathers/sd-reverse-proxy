from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE_URL: str = Field(default="https://www.openligadb.de")
    RATE_LIMIT_PER_MIN: int = Field(default=60)
    MAX_RETRIES: int = Field(default=3)
    BASE_BACKOFF_MS: int = Field(default=200)
    TIMEOUT_SEC: float = Field(default=100)
    JITTER_FACTOR: float = Field(default=0.1)


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
