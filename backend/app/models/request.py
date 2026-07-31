from pydantic import BaseModel, Field
from typing import List, Optional

class SearchQueryRequest(BaseModel):
    query: str = Field(..., description="The medical research or treatment comparison question")
    model_name: Optional[str] = Field("llama-3.3-70b-versatile", description="Selected LLM model (e.g. Groq Llama 3.3 70B)")
    llm_provider: Optional[str] = Field("groq", description="Selected LLM provider (groq, gemini, openai)")
    sources: Optional[List[str]] = Field(default=["PubMed", "ClinicalTrials", "openFDA", "DailyMed", "WHO", "CDC", "Guidelines"], description="Filter by source databases")
    study_type_filter: Optional[str] = Field(None, description="Optional filter: RCT, Meta-Analysis, Guideline, Cohort")
    year_min: Optional[int] = Field(None, description="Minimum publication year")
    top_k: Optional[int] = Field(5, description="Number of top evidence chunks to include")

class EvalRunRequest(BaseModel):
    test_case_ids: Optional[List[int]] = Field(None, description="List of specific test case IDs to evaluate (1-25)")
    llm_model: Optional[str] = Field("llama-3.3-70b-versatile", description="Groq Cloud LLM model for evaluation")
    llm_provider: Optional[str] = Field("groq", description="Groq Cloud provider")
