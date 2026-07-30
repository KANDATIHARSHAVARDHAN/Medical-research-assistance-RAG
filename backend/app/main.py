import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.health import router as health_router
from backend.app.api.routes import router as rag_router
from backend.app.api.eval_routes import router as eval_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Evidence-Aware Medical Question Answering System with Hybrid Retrieval, Hallucination Detection, and RAGAS Evaluation Dashboard."
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(rag_router)
app.include_router(eval_router)

@app.on_event("startup")
def startup_event():
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Default LLM Provider: {settings.DEFAULT_LLM_PROVIDER} | Default Model: {settings.DEFAULT_LLM_MODEL}")
    # Auto ingest datasets if stores are empty
    try:
        from scripts.ingest_all import run_ingestion
        run_ingestion()
    except Exception as e:
        print(f"Auto-ingestion note: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
