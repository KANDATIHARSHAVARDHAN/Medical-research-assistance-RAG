from fastapi import APIRouter
from backend.app.config import settings
from backend.app.database.pinecone_store import pinecone_store

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_default_model": settings.DEFAULT_LLM_MODEL,
        "vector_store_mode": "Pinecone" if pinecone_store.use_pinecone else "Local In-Memory Vector Store",
        "retrieval_weights": {
            "vector_weight": settings.VECTOR_SEARCH_WEIGHT,
            "bm25_weight": settings.BM25_SEARCH_WEIGHT
        }
    }
