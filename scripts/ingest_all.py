import os
import sys
import argparse
from pathlib import Path

# Fix Windows console encoding for UTF-8 print outputs
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.services.ingestion import offline_data_pipeline

def run_ingestion(api_queries=None, max_per_source=3, include_local_datasets=True):
    """
    Programmatic entry point for auto-ingestion on backend startup or script execution.
    """
    return offline_data_pipeline.run_pipeline(
        api_queries=api_queries or [],
        max_results_per_source=max_per_source,
        include_local_datasets=include_local_datasets
    )

def main():
    parser = argparse.ArgumentParser(description="Medical RAG Offline Data Pipeline Ingestion Runner")
    parser.add_argument("--api-queries", nargs="*", default=[], help="List of clinical terms to query from PubMed, ClinicalTrials, openFDA, and DailyMed APIs")
    parser.add_argument("--max-per-source", type=int, default=3, help="Max items to fetch per live API source")
    parser.add_argument("--skip-local", action="store_true", help="Skip loading sample JSON datasets from disk")
    args = parser.parse_args()

    queries = args.api_queries if args.api_queries else []
    
    print("============================================================")
    print("   MEDICAL RESEARCH ASSISTANT - OFFLINE DATA PIPELINE       ")
    print("============================================================")
    
    result = run_ingestion(
        api_queries=queries,
        max_per_source=args.max_per_source,
        include_local_datasets=not args.skip_local
    )
    
    print("\n[INGESTION SUMMARY]")
    print(f"Status: {result.get('status')}")
    print(f"Raw Documents Loaded: {result.get('raw_documents', 0)}")
    print(f"Cleaned Documents: {result.get('cleaned_documents', 0)}")
    print(f"Semantic Chunks Indexed: {result.get('chunks_indexed', 0)}")
    print("============================================================")

if __name__ == "__main__":
    main()
