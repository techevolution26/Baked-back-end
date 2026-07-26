from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from ..core.security import get_current_user
from ..models import User
from ..services.storage import ALLOWED_CONTENT_TYPES, MAX_UPLOAD_BYTES, get_storage_backend

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/images")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}' -- use JPEG, PNG, or WebP",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large -- max 5MB")

    # Don't just trust the client-reported content type -- verify the
    # bytes actually decode as an image before accepting an upload.
    try:
        Image.open(BytesIO(content)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=415, detail="File does not look like a valid image")

    storage = get_storage_backend()
    url = await storage.save(content, file.content_type)
    return {"url": url}