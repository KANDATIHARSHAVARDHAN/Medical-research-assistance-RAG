from fastapi import APIRouter, HTTPException
from backend.app.models.request import EvalRunRequest
from backend.app.models.response import RagasSummaryResponse
from backend.app.evaluation.ragas_eval import ragas_evaluator

router = APIRouter(prefix="/api/eval", tags=["RAGAS Evaluation"])

@router.get("/metrics", response_model=RagasSummaryResponse)
def get_ragas_metrics():
    """
    Returns pre-computed RAGAS evaluation summary instantly with 0 API calls.
    """
    try:
        return ragas_evaluator.get_cached_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run", response_model=RagasSummaryResponse)
def run_ragas_evaluation(request: EvalRunRequest):
    """
    Executes live RAGAS evaluation over specified test cases (or all 25 benchmark cases).
    """
    try:
        summary = ragas_evaluator.evaluate_all(
            test_case_ids=request.test_case_ids,
            llm_model=request.llm_model or "llama-3.3-70b-versatile",
            llm_provider=request.llm_provider or "groq"
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
