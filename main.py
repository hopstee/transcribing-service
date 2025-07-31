import os
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from app.core.config import DEFAULT_DURATION, DEFAULT_MODEL, MODEL_TYPES, REDIS_RESULTS_PREFIX, UPLOAD_DIR
import aiofiles
import uuid

from app.core.utils import validate_file_extension
from app.services.redis_service import RedisService

r = RedisService()

app = FastAPI()

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post(f"/transcribe/")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Query(default=DEFAULT_MODEL),
    trim: float = Query(default=DEFAULT_DURATION, ge=0.0)
):
    if model not in MODEL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model}' is not supported. Available models: {', '.join(MODEL_TYPES)}"
        )
    
    if not file or file.filename == "":
        raise HTTPException(status_code=400, detail="Audio file is not provided")
    
    validate_file_extension(file.filename)
    
    task_id = str(uuid.uuid4())
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.m4a")

    try:
        async with aiofiles.open(temp_path, "wb") as out_file:
            while content := await file.read(1024 * 1024):
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    task_data = {
        "task_id": task_id,
        "audio_path": temp_path,
        "model": model,
        "trim": trim
    }

    r.enqueue_task(task_data)
    r.set_status(task_id, "queued")

    return {"task_id": task_id, "status": "queued"}

@app.get(f"/transcribe/{{task_id}}")
async def get_transcription_result(task_id: str):
    result = r.get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return result
