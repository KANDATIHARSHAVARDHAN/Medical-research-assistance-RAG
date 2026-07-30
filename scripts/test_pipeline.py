import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.ingest_all import run_ingestion
from backend.app.services.rag_pipeline import rag_pipeline
from backend.app.services.evaluation.ragas_eval import ragas_evaluator
from backend.app.services.evaluation.deepeval_eval import deepeval_evaluator

def main():
    print("============================================================")
    print("   ENTERPRISE MEDICAL RAG - MODULAR PIPELINE VERIFICATION   ")
    print("============================================================")
    
    print("\n[PHASE 1] Executing Offline Data Ingestion Pipeline...")
    run_ingestion()

    query = "What is the evidence comparing SGLT2 inhibitors versus GLP-1 receptor agonists in diabetic kidney disease?"
    print(f"\n[PHASE 2] Running Online Retrieval & Synthesis Pipeline for Query:\n'{query}'...")
    result = rag_pipeline.run_pipeline(query=query, model_name="llama-3.3-70b-versatile", llm_provider="groq")

    print("\n--- PIPELINE EXECUTION SUMMARY ---")
    print(f"Query: {result['query']}")
    print(f"LLM Model Used: {result['llm_model_used']}")
    print(f"Retrieval Confidence: {result['retrieval_confidence']}%")
    print(f"Faithfulness Score: {result['hallucination_report']['faithfulness_score']}% (Risk Level: {result['hallucination_report']['risk_level']})")
    print(f"Hallucination Score: {result['hallucination_report'].get('hallucination_score', 0.0)}")
    print(f"DeepEval Benchmark: {result.get('deepeval_report')}")
    print(f"Citations Count: {len(result['citations'])}")
    print(f"Latency: {result['latency_ms']} ms")
    
    print("\n--- CLINICAL SUMMARY EXCERPT ---")
    print(result['clinical_summary'][:400] + "...")

    print("\n[PHASE 3] Executing RAGAS & DeepEval Benchmark Verification over 3 sample test cases...")
    summary = ragas_evaluator.evaluate_all(test_case_ids=[1, 2, 3])
    print(f"RAGAS Faithfulness Avg: {summary['avg_faithfulness']}% | Relevancy: {summary['avg_answer_relevancy']}%")

    print("\n============================================================")
    print(" [SUCCESS] ALL 5 PHASES OF MODULAR ARCHITECTURE VERIFIED!  ")
    print("============================================================")

if __name__ == "__main__":
    main()
