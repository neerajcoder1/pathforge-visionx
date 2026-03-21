from __future__ import annotations

import asyncio
import json
import logging
import pickle
from pathlib import Path

import networkx as nx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.api.schemas import AnalyzeRequest
from backend.api.store import get_db_pool, get_redis_client
from backend.engine.pace_engine import run_pace

router = APIRouter()
logger = logging.getLogger(__name__)


def _load_esco_graph() -> nx.DiGraph:
    root = Path(__file__).resolve().parents[2]
    graph_path = root / "data" / "esco_graph.pkl"
    if not graph_path.exists():
        from backend.ontology.build_graph import ensure_graph_pickle

        ensure_graph_pickle()
    with graph_path.open("rb") as f:
        graph = pickle.load(f)
    if not isinstance(graph, nx.DiGraph):
        raise ValueError("data/esco_graph.pkl must contain a networkx.DiGraph")
    return graph


async def event_stream(data: AnalyzeRequest):
    session_key = f"session:{data.session_id}"
    resume_text = get_redis_client().get(session_key)
    print(f"REDIS RETRIEVAL: {(resume_text or '')[:50]}...", flush=True)
    if not resume_text:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    db_pool = get_db_pool()
    graph = _load_esco_graph()

    logger.info("run_pace input resume_text(50)=%s", (resume_text or "")[:50])
    logger.info("run_pace input jd_text(50)=%s", (data.jd_text or "")[:50])

    await asyncio.sleep(0.05)
    yield f"data: {json.dumps({'event_type': 'mastery_map', 'payload': {'session_id': data.session_id}})}\n\n"

    result = run_pace(
        resume_text=resume_text,
        jd_text=data.jd_text,
        graph=graph,
        db_conn=db_pool,
    )

    await asyncio.sleep(0.05)
    yield f"data: {json.dumps({'event_type': 'paths', 'payload': [v.model_dump() for v in result.path_variants]})}\n\n"

    final_result = result.model_dump()

    yield f"data: {json.dumps({'event_type': 'complete', 'payload': final_result})}\n\n"


@router.post("/analyze")
async def analyze(data: AnalyzeRequest):
    return StreamingResponse(event_stream(data), media_type="text/event-stream")
