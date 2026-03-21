"""Upload route for resume ingestion and session bootstrapping."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.api.store import get_redis_client
from backend.extraction.parser import document_triage

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    text, _method = document_triage(file_bytes)
    session_id = uuid4()
    key = f"session:{session_id}"

    redis_client = get_redis_client()
    redis_client.setex(key, 900, text)
    print(f"REDIS SAVE: {key} len={len(text or '')}", flush=True)

    return {"session_id": str(session_id), "resume_text": text}
