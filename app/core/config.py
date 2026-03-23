from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Mini Social API"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str
    redis_url: str

    rate_limit_max_likes: int = 30
    rate_limit_window_seconds: int = 60
    posts_cache_ttl_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
