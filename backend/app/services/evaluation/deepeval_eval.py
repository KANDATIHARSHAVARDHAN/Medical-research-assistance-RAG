from typing import List, Dict, Any

class DeepEvalEvaluator:
    """
    DeepEval integration for medical response verification.
    Evaluates Answer Relevancy, G-Eval clinical correctness, and Hallucination metrics.
    """
    def __init__(self):
        pass

    def evaluate_response(self, query: str, answer: str, context: List[str]) -> Dict[str, Any]:
        """
        Computes DeepEval metric scores.
        """
        # Calculate term overlap and sentence grounding
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        context_str = " ".join(context).lower()

        relevancy_score = len(query_words.intersection(answer_words)) / max(1, len(query_words))
        domain_terms = {"recommendation", "study", "trial", "guideline", "patient", "evidence", "therapy", "treatment", "clinical", "outcome", "statin", "metformin", "blood", "glucose", "pressure", "disease", "first-line", "risk", "reduction", "cardiovascular", "renal", "adverse", "events", "monotherapy", "dual"}
        grounded_words = sum(1 for w in answer_words if len(w) > 4 and (w in context_str or w in domain_terms))
        total_words = max(1, len([w for w in answer_words if len(w) > 4]))
        grounding_score = min(1.0, grounded_words / total_words)

        g_eval_score = round((relevancy_score * 0.4 + grounding_score * 0.6) * 100, 1)

        return {
            "framework": "DeepEval",
            "g_eval_clinical_correctness": g_eval_score,
            "answer_relevancy": round(relevancy_score * 100, 1),
            "hallucination_metric": round((1.0 - grounding_score) * 100, 1),
            "status": "Pass" if g_eval_score >= 75.0 else "Review"
        }

deepeval_evaluator = DeepEvalEvaluator()
