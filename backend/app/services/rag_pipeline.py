import time
from typing import Dict, Any, List
from backend.app.services.retrieval.retriever import hybrid_retriever
from backend.app.services.retrieval.reranker import cross_encoder_reranker
from backend.app.services.confidence.retrieval_score import confidence_scorer
from backend.app.services.prompt.prompt_template import prompt_builder
from backend.app.services.llm.gemini import llm_service
from backend.app.services.evaluation.hallucination import hallucination_detector
from backend.app.services.evaluation.deepeval_eval import deepeval_evaluator
from backend.app.services.citations.citation_builder import citation_builder

class MedicalRAGPipeline:
    """
    Online Query Pipeline executing:
    1. Query Embedding & Hybrid Retrieval (Top-20 candidates)
    2. Cross-Encoder Reranking (Refining to Top-5 evidence)
    3. Retrieval Confidence Scoring & Evidence Ranking
    4. Prompt Construction with Strict Anti-Hallucination Grounding
    5. LLM Synthesis (Groq / Gemini / OpenAI)
    6. Hallucination Detection (RAGAS Faithfulness & DeepEval G-Eval)
    7. Interactive Citation Assembly
    """
    def __init__(self):
        pass

    def run_pipeline(
        self,
        query: str,
        model_name: str = "llama-3.3-70b-versatile",
        llm_provider: str = "groq",
        sources: List[str] = None,
        study_type_filter: str = None,
        year_min: int = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        start_time = time.time()

        # Build retrieval filters
        filters = {}
        if sources:
            filters["sources"] = sources
        if study_type_filter:
            filters["study_type"] = study_type_filter
        if year_min:
            filters["year_min"] = year_min

        # Step 1: Hybrid Retrieval (0.5 Dense Vector / 0.5 Sparse BM25) - Top 20 Candidates
        retrieved_chunks = hybrid_retriever.retrieve(query=query, top_k=max(20, top_k * 4), filters=filters)

        # Step 2: Cross-Encoder Re-ranking - Refine to Top-k (default 5)
        reranked_chunks = cross_encoder_reranker.rerank(query=query, documents=retrieved_chunks, top_k=top_k)

        # Step 3: Evidence Ranking & Retrieval Confidence Calculation
        scored_evidence, retrieval_confidence = confidence_scorer.calculate_evidence_scores(reranked_chunks)

        # Step 4: Prompt Construction
        prompt = prompt_builder.build_rag_prompt(query=query, evidence_docs=scored_evidence)

        # Step 5: LLM Response Generation
        raw_answer = llm_service.generate_response(prompt=prompt, model_name=model_name, provider=llm_provider)

        # Step 6: Hallucination Detection & Verification (RAGAS Faithfulness & DeepEval)
        retrieved_texts = [doc["chunk_text"] for doc in scored_evidence]
        hallucination_report = hallucination_detector.analyze_faithfulness(
            generated_answer=raw_answer,
            retrieved_contexts=retrieved_texts
        )
        deepeval_report = deepeval_evaluator.evaluate_response(
            query=query,
            answer=raw_answer,
            context=retrieved_texts
        )

        # Step 7: Citation & Reference Card Assembly
        citations = citation_builder.build_citations(scored_evidence)

        latency = round((time.time() - start_time) * 1000, 2)

        # Parse sections cleanly from raw answer
        clinical_summary = self._extract_section(raw_answer, "Clinical Summary")
        evidence_synthesis = self._extract_section(raw_answer, "Evidence Synthesis")
        treatment_comparison = self._extract_section(raw_answer, "Treatment Comparison")
        contraindications = self._extract_section(raw_answer, "Contraindications & Precautions")

        return {
            "query": query,
            "llm_model_used": model_name,
            "raw_answer": raw_answer,
            "clinical_summary": clinical_summary or raw_answer[:300],
            "evidence_synthesis": evidence_synthesis or raw_answer,
            "treatment_comparison": treatment_comparison,
            "contraindications": contraindications,
            "retrieval_confidence": retrieval_confidence,
            "hallucination_report": hallucination_report,
            "deepeval_report": deepeval_report,
            "evidence_list": scored_evidence,
            "citations": citations,
            "latency_ms": latency
        }

    def _extract_section(self, text: str, header_title: str) -> str:
        lines = text.splitlines()
        capturing = False
        section_lines = []

        for line in lines:
            if header_title.lower() in line.lower() and line.startswith("#"):
                capturing = True
                continue
            elif capturing and line.startswith("#"):
                break
            elif capturing:
                section_lines.append(line)

        return "\n".join(section_lines).strip()

rag_pipeline = MedicalRAGPipeline()
