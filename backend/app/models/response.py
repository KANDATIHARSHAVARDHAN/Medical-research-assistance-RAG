from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CitationItem(BaseModel):
    id: int
    title: str
    authors: str
    journal: str
    year: int
    pmid: Optional[str] = None
    doi: Optional[str] = None
    study_type: str
    source: str
    url: Optional[str] = None
    similarity_score: float
    confidence_level: str  # High, Medium, Low

class EvidenceItem(BaseModel):
    rank: int
    chunk_text: str
    title: str
    authors: str
    journal: str
    year: int
    pmid: Optional[str] = None
    doi: Optional[str] = None
    study_type: str
    source: str
    vector_score: float
    bm25_score: float
    cross_encoder_score: float
    recency_score: float
    study_quality_score: float
    overall_score: float

class HallucinationReport(BaseModel):
    faithfulness_score: float  # Percentage (e.g. 94.5%)
    hallucination_score: Optional[float] = 0.0  # Risk score (e.g. 0.05)
    risk_level: str            # Low, Medium, High
    total_sentences: int
    grounded_sentences: int
    ungrounded_sentences: List[str] = []

class AnswerResponse(BaseModel):
    query: str
    llm_model_used: str
    raw_answer: str
    clinical_summary: str
    evidence_synthesis: str
    treatment_comparison: Optional[str] = None
    contraindications: Optional[str] = None
    retrieval_confidence: float  # e.g. 88.5%
    hallucination_report: HallucinationReport
    deepeval_report: Optional[Dict[str, Any]] = None
    evidence_list: List[EvidenceItem]
    citations: List[CitationItem]
    latency_ms: float

class RagasTestCaseResult(BaseModel):
    id: int
    query: str
    category: str
    ground_truth: str
    generated_answer: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    latency_ms: float
    status: str

class RagasSummaryResponse(BaseModel):
    avg_faithfulness: float
    avg_answer_relevancy: float
    avg_context_precision: float
    avg_context_recall: float
    total_test_cases: int
    completed_test_cases: int
    avg_latency_ms: float
    eval_framework: str = "Built-in RAGAS Metric Evaluator"
    results: List[RagasTestCaseResult]
