from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from functools import lru_cache


class Settings(BaseSettings):
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    celery_result_expires: int = 12 * 60 * 60

    postgres_user: SecretStr
    postgres_password: SecretStr
    postgres_host: SecretStr
    postgres_port: int
    postgres_db: str

    redis_host: SecretStr
    redis_port: int
    redis_db: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_config() -> BaseSettings:
    return Settings()


config = get_config()
