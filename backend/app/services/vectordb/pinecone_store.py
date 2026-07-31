import os
import json
import hashlib
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from backend.app.config import settings
from backend.app.services.embeddings import embedding_service

CACHE_FILE = Path(__file__).resolve().parent.parent.parent.parent.parent / "datasets" / "embeddings_cache.json"

class PineconeVectorStore:
    """
    Pinecone AWS Vector Store with persistent local disk caching and metadata filtering.
    """
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.use_pinecone = False
        self.index = None
        self.local_documents: List[Dict[str, Any]] = []
        self.local_vectors: List[np.ndarray] = []
        self.embedding_cache: Dict[str, List[float]] = self._load_embedding_cache()
        self._init_pinecone()

    def _load_embedding_cache(self) -> Dict[str, List[float]]:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                    print(f"[EMBEDDING CACHE] Successfully loaded {len(cache)} pre-computed embeddings from disk.")
                    return cache
            except Exception as e:
                print(f"[EMBEDDING CACHE] Failed to read cache ({e}). Starting fresh.")
        return {}

    def _save_embedding_cache(self):
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.embedding_cache, f)
        except Exception as e:
            print(f"[EMBEDDING CACHE] Failed to save cache ({e}).")

    def _init_pinecone(self):
        if self.api_key and len(self.api_key.strip()) > 10:
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=self.api_key)
                self.index = pc.Index(self.index_name)
                self.use_pinecone = True
                stats = self.index.describe_index_stats()
                print(f"[PINECONE] Connected to AWS index '{self.index_name}' (Total vectors stored: {stats.get('total_vector_count', 0)})")
            except Exception as e:
                print(f"[PINECONE] Init failed ({e}). Defaulting to local in-memory vector store.")
                self.use_pinecone = False
        else:
            print("[PINECONE] No Pinecone API key provided. Operating in local in-memory vector store mode.")
            self.use_pinecone = False

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        Adds medical chunk documents with metadata to vector index.
        Reuses existing embeddings from disk/cache so vectors are NOT re-created every time.
        """
        new_texts_map = {}
        embeddings_list = []
        reused_count = 0
        new_count = 0

        # Step 1: Check embedding cache for each document
        for i, doc in enumerate(docs):
            doc_id = str(doc.get("pmid") or doc.get("doi") or f"doc_{hashlib.md5(doc.get('chunk_text', '').encode('utf-8')).hexdigest()[:12]}")
            doc["_doc_id"] = doc_id
            
            if doc_id in self.embedding_cache:
                embeddings_list.append(self.embedding_cache[doc_id])
                reused_count += 1
            else:
                embeddings_list.append(None)
                new_texts_map[i] = doc["chunk_text"]
                new_count += 1

        if reused_count > 0:
            print(f"[EMBEDDING REUSE] Reused {reused_count} existing pre-computed embeddings! (Zero re-creation needed)")

        # Step 2: Only compute embeddings for NEW documents that were not found in cache
        if new_count > 0:
            print(f"[EMBEDDING CREATE] Computing embeddings for {new_count} new documents...")
            new_indices = list(new_texts_map.keys())
            new_texts = list(new_texts_map.values())
            computed_embs = embedding_service.embed_documents(new_texts)
            
            for idx, emb in zip(new_indices, computed_embs):
                embeddings_list[idx] = emb
                doc_id = docs[idx]["_doc_id"]
                self.embedding_cache[doc_id] = emb
            
            self._save_embedding_cache()
            print(f"[EMBEDDING CACHE] Saved {new_count} newly computed embeddings to disk for future reuse.")

        # Step 3: Populate store / Pinecone index
        pinecone_vectors = []
        for doc, emb in zip(docs, embeddings_list):
            self.local_documents.append(doc)
            self.local_vectors.append(np.array(emb, dtype=np.float32))
            
            if self.use_pinecone:
                clean_meta = {k: str(v) for k, v in doc.items() if k != "_doc_id" and v is not None}
                pinecone_vectors.append((doc["_doc_id"], emb, clean_meta))

        if self.use_pinecone and pinecone_vectors:
            try:
                # Upsert into Pinecone index in batches of 100 vectors to avoid 2MB payload size limits
                batch_size = 100
                total_upserted = 0
                for i in range(0, len(pinecone_vectors), batch_size):
                    batch = pinecone_vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch)
                    total_upserted += len(batch)
                print(f"[PINECONE] Successfully synced {total_upserted} vectors with Pinecone AWS index in batches of {batch_size}.")
            except Exception as e:
                print(f"[PINECONE] Upsert error ({e}). Using local in-memory fallback.")

    def similarity_search_with_score(self, query: str, top_k: int = 20, filters: Dict[str, Any] = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Executes dense vector similarity search. Returns list of (document, similarity_score).
        Defaults to top_k=20 for hybrid search + reranking candidate pool.
        """
        if not self.local_documents:
            return []

        query_vec = np.array(embedding_service.embed_query(query), dtype=np.float32)
        norm_q = np.linalg.norm(query_vec)
        if norm_q > 0:
            query_vec = query_vec / norm_q

        results = []
        for doc, vec in zip(self.local_documents, self.local_vectors):
            # Apply metadata filters if provided
            if filters:
                if "sources" in filters and filters["sources"] and doc.get("source") not in filters["sources"]:
                    continue
                if "study_type" in filters and filters["study_type"] and doc.get("study_type") != filters["study_type"]:
                    continue
                if "year_min" in filters and filters["year_min"] and doc.get("year", 0) < int(filters["year_min"]):
                    continue

            norm_v = np.linalg.norm(vec)
            if norm_v > 0:
                vec_normed = vec / norm_v
                score = float(np.dot(query_vec, vec_normed))
            else:
                score = 0.0

            # Scale to 0..1
            similarity = max(0.0, min(1.0, (score + 1.0) / 2.0))
            results.append((doc, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

pinecone_store = PineconeVectorStore()
