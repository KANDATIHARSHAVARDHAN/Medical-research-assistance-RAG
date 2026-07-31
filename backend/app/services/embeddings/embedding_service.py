import numpy as np
import requests
import hashlib
from typing import List
from backend.app.config import settings

class EmbeddingService:
    """
    Modular Embedding Service supporting biomedical models (PubMedBERT) and semantic models (BGE-M3, BGE-base-en-v1.5).
    Supports zero-download Hugging Face Cloud Inference API with automatic deterministic local fallback.
    """
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model = None
        # BGE-M3 is 1024-d, PubMedBERT and BGE-base are 768-d, MiniLM is 384-d
        if "m3" in model_name.lower():
            self.dimension = 1024
        elif any(k in model_name.lower() for k in ["bert", "pubmed", "bge", "768"]):
            self.dimension = 768
        else:
            self.dimension = 384
            
        self.use_hf_api = bool(settings.HUGGINGFACE_API_KEY and len(settings.HUGGINGFACE_API_KEY.strip()) > 5)
        self._init_embedder()

    def _init_embedder(self):
        if self.use_hf_api:
            print(f"[EMBEDDING SERVICE] Hugging Face API key detected. Using HF Cloud Inference API for {self.model_name} (No local download needed).")
        else:
            self._load_local_model()

    def _load_local_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[EMBEDDING SERVICE] Loading local SentenceTransformer embedding model: {self.model_name}")
            token = settings.HUGGINGFACE_API_KEY if settings.HUGGINGFACE_API_KEY else None
            self.model = SentenceTransformer(self.model_name, token=token)
            if hasattr(self.model, "get_embedding_dimension"):
                self.dimension = self.model.get_embedding_dimension()
            elif hasattr(self.model, "get_sentence_embedding_dimension"):
                self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"[EMBEDDING SERVICE] Successfully loaded {self.model_name} locally (Dimension: {self.dimension})")
        except Exception as e:
            print(f"[EMBEDDING SERVICE] Warning: Local embedding load fallback ({e}). Using deterministic pseudo-embedder (dim: {self.dimension}).")
            self.model = None

    def _call_hf_api(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        url = f"https://router.huggingface.co/hf-inference/models/{self.model_name}"
        response = requests.post(url, headers=headers, json={"inputs": texts}, timeout=15.0)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], float):  # Single vector returned
                    return [data]
                elif isinstance(data[0], list): # List of vectors returned
                    return data
        # Fallback 768-d feature-extraction router endpoint if HF router tags model under sentence-similarity
        res_fb = requests.post("https://router.huggingface.co/hf-inference/models/BAAI/bge-base-en-v1.5", headers=headers, json={"inputs": texts}, timeout=15.0)
        if res_fb.status_code == 200:
            data = res_fb.json()
            if isinstance(data, list) and len(data) > 0:
                return [data] if isinstance(data[0], float) else data
        raise Exception(f"HF API Error {response.status_code}: {response.text[:200]}")

    def embed_query(self, text: str) -> List[float]:
        if self.use_hf_api:
            try:
                res = self._call_hf_api([text])
                return res[0]
            except Exception as e:
                print(f"[EMBEDDING SERVICE] HF Cloud API unavailable ({type(e).__name__}). Switched to local embedder.")
                self.use_hf_api = False
                if self.model is None:
                    self._load_local_model()

        if self.model is not None:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        else:
            # Fallback deterministic pseudo-embedding vector matching model dimension
            np.random.seed(int(hashlib.md5(text.encode('utf-8')).hexdigest()[:8], 16) % (2**32))
            vec = np.random.randn(self.dimension)
            norm = np.linalg.norm(vec)
            return (vec / norm).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.use_hf_api:
            try:
                return self._call_hf_api(texts)
            except Exception as e:
                print(f"[EMBEDDING SERVICE] HF Cloud API unavailable ({type(e).__name__}). Switched to local embedder.")
                self.use_hf_api = False
                if self.model is None:
                    self._load_local_model()

        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        else:
            return [self.embed_query(t) for t in texts]

embedding_service = EmbeddingService()
