import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv(override=True)

class Settings:
    PROJECT_NAME: str = "Medical Research Assistant RAG"
    VERSION: str = "1.0.0"
    
    # 1. Main LLM API Key (For Answer Generation Pipeline)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # 2. SEPARATE Dedicated Evaluation API Key (For RAGAS Evaluation Framework)
    RAGAS_EVAL_API_KEY: str = os.getenv("RAGAS_EVAL_API_KEY", "")
    
    # 3. Hugging Face API Key (For PubMedBERT & Hugging Face Hub Models)
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Defaults
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "groq")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "llama-3.3-70b-versatile")
    RAGAS_EVAL_MODEL: str = os.getenv("RAGAS_EVAL_MODEL", "llama-3.1-8b-instant")
    
    # Pinecone Vector DB
    # PINECONE_ENVIRONMENT: Specifies cloud provider/region (e.g. us-east-1-aws, gcp-starter)
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "medical-rag-index")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    
    # Embeddings (Hugging Face PubMedBERT)
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "NeuML/pubmedbert-base-embeddings")
    
    # Retrieval Weights (Strict 0.5 / 0.5 split)
    VECTOR_SEARCH_WEIGHT: float = float(os.getenv("VECTOR_SEARCH_WEIGHT", "0.5"))
    BM25_SEARCH_WEIGHT: float = float(os.getenv("BM25_SEARCH_WEIGHT", "0.5"))
    
    # Reranking & Retrieval Top K (Reduced top_k to 3 for concise context window & low token footprint)
    TOP_K_RETRIEVAL: int = 8
    TOP_K_RERANKED: int = 3

settings = Settings()

# Automatically sync HUGGINGFACE_API_KEY to HF_TOKEN to prevent unauthenticated Hub warnings
if settings.HUGGINGFACE_API_KEY and not os.getenv("HF_TOKEN"):
    os.environ["HF_TOKEN"] = settings.HUGGINGFACE_API_KEY
