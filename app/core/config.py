from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:3000"
    # Every bakery gets "<slug>.<platform_domain>" automatically. Using
    # the .test TLD locally -- it's reserved for testing/docs (RFC 2606)
    # so it can never collide with a real domain.
    platform_domain: str = "cakeplatform.test"


    # File storage for uploaded images (cover photos, etc). Local disk
    # works out of the box for dev with no external credentials --
    # swap storage_backend to an S3-compatible implementation before
    # deploying behind the reverse proxy (see services/storage.py).
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
