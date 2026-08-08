from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(validation_alias="DATABASE_URL")
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:3000"
    platform_domain: str = "cakeplatform.test"
    storage_backend: str = "local"
    upload_dir: str = "uploads"
    public_base_url: str = "http://localhost:8000"
    media_url_path: str = "/media"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

@lru_cache
def get_settings() -> Settings:
    return Settings()