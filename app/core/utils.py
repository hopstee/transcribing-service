from fastapi import HTTPException

from app.core.config import ALLOWED_EXTENSIONS

def validate_file_extension(filename: str):
    if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Service support: {', '.join(ALLOWED_EXTENSIONS)}"
        )