import json
import asyncio
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from backend.app.models.request import SearchQueryRequest
from backend.app.models.response import AnswerResponse
from backend.app.services.rag_pipeline import rag_pipeline
from backend.app.database.pinecone_store import pinecone_store

router = APIRouter(prefix="/api", tags=["Medical RAG"])

@router.post("/search", response_model=AnswerResponse)
def search_medical_evidence(request: SearchQueryRequest):
    try:
        res = rag_pipeline.run_pipeline(
            query=request.query,
            model_name=request.model_name or "llama-3.3-70b-versatile",
            llm_provider=request.llm_provider or "groq",
            sources=request.sources,
            study_type_filter=request.study_type_filter,
            year_min=request.year_min,
            top_k=request.top_k or 5
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask-stream")
async def ask_medical_evidence_stream(request: SearchQueryRequest):
    async def event_generator():
        # First send retrieval phase notification
        yield {
            "event": "status",
            "data": json.dumps({"message": "Executing 0.5 Vector / 0.5 BM25 Hybrid Retrieval..."})
        }
        await asyncio.sleep(0.3)

        # Run pipeline
        res = rag_pipeline.run_pipeline(
            query=request.query,
            model_name=request.model_name or "llama-3.3-70b-versatile",
            llm_provider=request.llm_provider or "groq",
            sources=request.sources,
            study_type_filter=request.study_type_filter,
            year_min=request.year_min,
            top_k=request.top_k or 5
        )

        yield {
            "event": "status",
            "data": json.dumps({"message": "Cross-Encoder Re-ranking & Evidence Scoring complete..."})
        }
        await asyncio.sleep(0.2)

        # Stream chunk text
        raw_text = res["raw_answer"]
        chunk_size = 40
        for i in range(0, len(raw_text), chunk_size):
            chunk = raw_text[i:i+chunk_size]
            yield {
                "event": "chunk",
                "data": json.dumps({"text": chunk})
            }
            await asyncio.sleep(0.04)

        # Final complete payload event
        yield {
            "event": "complete",
            "data": json.dumps(res)
        }

    return EventSourceResponse(event_generator())
