import json
from pathlib import Path
from typing import List, Dict, Any

from .pubmed_loader import PubMedLoader, pubmed_loader
from .clinical_trials_loader import ClinicalTrialsLoader, clinical_trials_loader
from .openfda_loader import OpenFDALoader, openfda_loader
from .dailymed_loader import DailyMedLoader, dailymed_loader
from backend.app.services.parser.document_cleaner import document_cleaner
from backend.app.services.chunking.semantic_chunker import semantic_chunker
from backend.app.services.vectordb.pinecone_store import pinecone_store
from backend.app.services.bm25_store import bm25_store

class OfflineDataPipeline:
    """
    Offline Data Pipeline orchestrator:
    1. Ingestion Loaders (PubMed, ClinicalTrials.gov, openFDA, DailyMed APIs + local fallback JSONs)
    2. Document Cleaning & Parsing (removing HTML/XML, verifying metadata)
    3. Semantic Chunking (512 tokens with overlap, sentence boundaries)
    4. BGE-M3 / PubMedBERT Embedding generation & caching
    5. Syncing into Pinecone AWS index and BM25 sparse index
    """
    def __init__(self):
        pass

    def run_pipeline(
        self,
        api_queries: List[str] = None,
        max_results_per_source: int = 3,
        include_local_datasets: bool = True
    ) -> Dict[str, Any]:
        print("[OFFLINE DATA PIPELINE] Starting multi-source medical ingestion...")
        all_raw_docs = []

        # 1. Load Local Datasets (deterministic base)
        if include_local_datasets:
            root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            datasets_dir = root_dir / "datasets"
            for sample_file in ["pubmed_sample.json", "guidelines_sample.json"]:
                file_path = datasets_dir / sample_file
                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            docs = json.load(f)
                            all_raw_docs.extend(docs)
                            print(f"[LOCAL LOADER] Loaded {len(docs)} records from {sample_file}")
                    except Exception as e:
                        print(f"[LOCAL LOADER] Error reading {sample_file} ({e})")

        # 2. Fetch Live API Data (PubMed, ClinicalTrials, openFDA, DailyMed)
        if api_queries:
            for query in api_queries:
                all_raw_docs.extend(pubmed_loader.search_and_fetch(query, max_results=max_results_per_source))
                all_raw_docs.extend(clinical_trials_loader.search_and_fetch(query, max_results=max_results_per_source))
                all_raw_docs.extend(openfda_loader.search_and_fetch(query, max_results=max_results_per_source))
                all_raw_docs.extend(dailymed_loader.search_and_fetch(query, max_results=max_results_per_source))

        if not all_raw_docs:
            print("[OFFLINE DATA PIPELINE] No documents retrieved.")
            return {"status": "Empty", "chunks_indexed": 0}

        # 3. Document Cleaning & Parsing
        cleaned_docs = document_cleaner.clean_documents(all_raw_docs)

        # 4. Semantic Chunking
        chunked_docs = semantic_chunker.chunk_documents(cleaned_docs)

        # 5. Index into Vector DB & BM25
        print(f"[OFFLINE DATA PIPELINE] Indexing {len(chunked_docs)} semantic chunks into Pinecone & BM25...")
        pinecone_store.add_documents(chunked_docs)
        bm25_store.add_documents(chunked_docs)

        print("[SUCCESS] Offline Data Pipeline execution complete!")
        return {
            "status": "Success",
            "raw_documents": len(all_raw_docs),
            "cleaned_documents": len(cleaned_docs),
            "chunks_indexed": len(chunked_docs)
        }

offline_data_pipeline = OfflineDataPipeline()
