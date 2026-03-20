from fastapi import APIRouter, UploadFile, File
from backend.api.store import sessions
import uuid

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except:
        text = str(content)

    session_id = str(uuid.uuid4())

    # Store in memory
    sessions[session_id] = text

    return {"session_id": session_id, "resume_text": text[:200]}  # just preview
