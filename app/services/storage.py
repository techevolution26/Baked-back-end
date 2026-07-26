"""
File storage abstraction for uploaded images (cover photos, etc).

Local disk storage is implemented and used by default -- it works out
of the box with no external credentials, which is right for local dev.
For production, implement an S3-compatible backend (AWS S3, Cloudflare
R2, DigitalOcean Spaces) behind the same Protocol and switch
STORAGE_BACKEND -- not built yet since it needs real bucket credentials
to build and test against properly, and because local-disk-served
images won't be reachable once the backend sits behind the reverse
proxy in deploy/ (only the frontend is meant to be public there).
"""
import uuid
from pathlib import Path
from typing import Protocol

from ..core.config import get_settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5MB

EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class StorageError(Exception):
    pass


class StorageBackend(Protocol):
    async def save(self, content: bytes, content_type: str) -> str:
        """Persists the file and returns its publicly reachable URL."""
        ...


class LocalStorageBackend:
    """Saves uploads to a local directory, served back out via FastAPI's
    static file mount. Fine for local dev and single-server setups;
    doesn't work across multiple backend replicas since each would have
    its own disk -- that's exactly the case for moving to S3-compatible
    storage."""

    def __init__(self, upload_dir: str, public_base_url: str, media_url_path: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.public_base_url = public_base_url.rstrip("/")
        self.media_url_path = media_url_path.rstrip("/")

    async def save(self, content: bytes, content_type: str) -> str:
        ext = EXTENSION_BY_CONTENT_TYPE.get(content_type, ".bin")
        filename = f"{uuid.uuid4()}{ext}"
        (self.upload_dir / filename).write_bytes(content)
        return f"{self.public_base_url}{self.media_url_path}/{filename}"


def get_storage_backend() -> StorageBackend:
    settings = get_settings()
    if settings.storage_backend == "local":
        return LocalStorageBackend(settings.upload_dir, settings.public_base_url, settings.media_url_path)
    raise StorageError(
        f"Unknown STORAGE_BACKEND '{settings.storage_backend}' -- only 'local' is implemented so far"
    )