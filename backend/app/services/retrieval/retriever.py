import hashlib
from typing import List, Dict, Any, Tuple
from backend.app.config import settings
from backend.app.services.vectordb.pinecone_store import pinecone_store
from backend.app.services.bm25_store import bm25_store

class HybridEnsembleRetriever:
    """
    Hybrid Retriever combining Dense Vector Search (BGE-M3/PubMedBERT) and Sparse BM25 Search.
    Supports Top-20 initial candidate retrieval with rich metadata filtering.
    """
    def __init__(self, vector_weight: float = settings.VECTOR_SEARCH_WEIGHT, bm25_weight: float = settings.BM25_SEARCH_WEIGHT):
        self.vector_weight = vector_weight  # 0.5
        self.bm25_weight = bm25_weight      # 0.5

    def retrieve(self, query: str, top_k: int = settings.TOP_K_RETRIEVAL, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # 1. Retrieve Dense Vector Results (fetch top_k * 2 for ensemble fusion)
        vector_results = pinecone_store.similarity_search_with_score(query, top_k=top_k * 2, filters=filters)
        
        # 2. Retrieve Sparse BM25 Results
        bm25_results = bm25_store.search(query, top_k=top_k * 2)

        # Map by unique PMID / chunk ID
        combined_scores: Dict[str, Dict[str, Any]] = {}

        for doc, score in vector_results:
            doc_id = str(doc.get("pmid") or doc.get("id") or f"doc_{hashlib.md5(doc['chunk_text'].encode('utf-8')).hexdigest()[:12]}")
            combined_scores[doc_id] = {
                "doc": doc,
                "vector_score": score,
                "bm25_score": 0.0
            }

        for doc, score in bm25_results:
            doc_id = str(doc.get("pmid") or doc.get("id") or f"doc_{hashlib.md5(doc['chunk_text'].encode('utf-8')).hexdigest()[:12]}")
            if doc_id in combined_scores:
                combined_scores[doc_id]["bm25_score"] = score
            else:
                combined_scores[doc_id] = {
                    "doc": doc,
                    "vector_score": 0.0,
                    "bm25_score": score
                }

        # Calculate 0.5 Vector + 0.5 BM25 Hybrid Score
        hybrid_docs = []
        for item in combined_scores.values():
            v_score = item["vector_score"]
            b_score = item["bm25_score"]
            
            hybrid_score = (self.vector_weight * v_score) + (self.bm25_weight * b_score)
            
            doc_entry = dict(item["doc"])
            doc_entry["vector_score"] = round(v_score, 4)
            doc_entry["bm25_score"] = round(b_score, 4)
            doc_entry["hybrid_score"] = round(hybrid_score, 4)
            
            hybrid_docs.append(doc_entry)

        # Sort by hybrid score descending
        hybrid_docs.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return hybrid_docs[:top_k]

hybrid_retriever = HybridEnsembleRetriever()
