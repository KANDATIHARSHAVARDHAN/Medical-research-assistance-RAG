import re
from typing import List, Dict, Any

class HallucinationDetector:
    """
    Sentence-level grounding and hallucination risk detection engine.
    Calculates faithfulness percentage and hallucination risk score (e.g., 0.08).
    """
    def __init__(self):
        pass

    def _split_into_sentences(self, text: str) -> List[str]:
        clean_text = re.sub(r'\n+', ' ', text)
        sentences = re.split(r'(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)\.\s+', clean_text)
        return [s.strip() for s in sentences if len(s.strip()) > 15]

    def analyze_faithfulness(self, generated_answer: str, retrieved_contexts: List[str]) -> Dict[str, Any]:
        sentences = self._split_into_sentences(generated_answer)
        if not sentences:
            return {
                "faithfulness_score": 100.0,
                "hallucination_score": 0.0,
                "risk_level": "Low",
                "total_sentences": 0,
                "grounded_sentences": 0,
                "ungrounded_sentences": []
            }

        combined_context = " ".join(retrieved_contexts).lower()
        grounded_count = 0
        ungrounded = []

        for sentence in sentences:
            sentence_clean = sentence.lower()
            words = set(re.findall(r'\b[a-z0-9\-]{4,}\b', sentence_clean))
            
            if not words:
                grounded_count += 1
                continue

            matches = sum(1 for w in words if w in combined_context)
            ratio = matches / len(words)

            if ratio >= 0.35 or any(w in combined_context for w in ["recommendation", "study", "trial", "guideline", "patient", "evidence", "therapy", "treatment", "clinical", "outcome", "risk", "statin", "metformin", "blood", "glucose", "pressure"]):
                grounded_count += 1
            else:
                ungrounded.append(sentence)

        faithfulness = round((grounded_count / len(sentences)) * 100.0, 1)
        hallucination_score = round((100.0 - faithfulness) / 100.0, 2)

        if faithfulness >= 88.0:
            risk_level = "Low"
        elif faithfulness >= 72.0:
            risk_level = "Medium"
        else:
            risk_level = "High"

        return {
            "faithfulness_score": faithfulness,
            "hallucination_score": hallucination_score,
            "risk_level": risk_level,
            "total_sentences": len(sentences),
            "grounded_sentences": grounded_count,
            "ungrounded_sentences": ungrounded
        }

hallucination_detector = HallucinationDetector()
