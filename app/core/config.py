from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0        # DB 0 -> For cache
    redis_password: str | None

    async_database_url: str  # postgressql+asyncpg://...


settings = Settings()