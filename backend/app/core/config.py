from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = "development"
    secret_key: str = "change-me"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://truthcheck:password@localhost:5432/truthcheck_db"
    redis_url: str = "redis://localhost:6379/0"

    bert_model_path: str = "ml/models/bert_fakenews_best.pt"
    faiss_index_path: str = "ml/models/faiss_index.bin"
    sbert_model_name: str = "all-MiniLM-L6-v2"

    google_fact_check_api_key: str = ""
    rate_limit_per_minute: int = 10

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
