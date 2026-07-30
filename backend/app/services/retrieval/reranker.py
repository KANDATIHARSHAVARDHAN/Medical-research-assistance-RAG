import numpy as np
from typing import List, Dict, Any
from backend.app.config import settings

class CrossEncoderReranker:
    """
    Cross-Encoder Reranking service supporting BGE Cross-Encoder ('BAAI/bge-reranker-base') 
    and MS-MARCO ('cross-encoder/ms-marco-MiniLM-L-6-v2') to refine Top-20 candidates into Top-5 evidence.
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder
            print(f"[RERANKER SERVICE] Loading CrossEncoder reranker model: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
        except Exception as e:
            print(f"[RERANKER SERVICE] CrossEncoder load notice ({e}). Using semantic similarity fallback reranker.")
            self.model = None

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = settings.TOP_K_RERANKED) -> List[Dict[str, Any]]:
        if not documents:
            return []

        if self.model is not None:
            pairs = [[query, doc["chunk_text"]] for doc in documents]
            scores = self.model.predict(pairs)
            
            # Sigmoid normalization
            sigmoid_scores = 1.0 / (1.0 + np.exp(-scores))
            
            for doc, s_score in zip(documents, sigmoid_scores):
                doc["cross_encoder_score"] = round(float(s_score), 4)
        else:
            # Fallback re-ranking based on hybrid score and query word overlap
            query_words = set(query.lower().split())
            for doc in documents:
                chunk_words = set(doc["chunk_text"].lower().split())
                overlap = len(query_words.intersection(chunk_words)) / max(1, len(query_words))
                base_score = doc.get("hybrid_score", 0.5)
                cross_score = 0.6 * base_score + 0.4 * overlap
                doc["cross_encoder_score"] = round(min(1.0, cross_score), 4)

        # Sort by cross_encoder_score descending
        reranked_docs = sorted(documents, key=lambda x: x["cross_encoder_score"], reverse=True)
        return reranked_docs[:top_k]

cross_encoder_reranker = CrossEncoderReranker()
