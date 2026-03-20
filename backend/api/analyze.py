from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.api.schemas import AnalyzeRequest
from backend.api.store import sessions
import json
import asyncio

router = APIRouter()


async def event_stream(data: AnalyzeRequest):
    # 🔥 get resume from session
    resume_text = sessions.get(data.session_id, "No resume found")

    # 1️⃣ Step: mastery map
    await asyncio.sleep(1)
    yield f"data: {json.dumps({'event_type': 'mastery_map', 'payload': resume_text[:100]})}\n\n"

    # 2️⃣ Step: path generation
    await asyncio.sleep(1)
    yield f"data: {json.dumps({'event_type': 'paths', 'payload': []})}\n\n"

    # 3️⃣ Final result
    await asyncio.sleep(1)
    final_result = {
        "session_id": data.session_id,
        "current_mastery": [],
        "target_skills": [],
        "path_variants": [],
        "cvs_nexus": 0.0,
        "cvs_legacy": 0.0,
        "decision_ledger": {},
        "diagnostic_required": False,
    }

    yield f"data: {json.dumps({'event_type': 'complete', 'payload': final_result})}\n\n"


@router.post("/analyze")
async def analyze(data: AnalyzeRequest):
    return StreamingResponse(event_stream(data), media_type="text/event-stream")
