from typing import List, Dict, Any

class PromptTemplateBuilder:
    """
    Evidence-grounded medical prompt builder enforcing strict citation rules and anti-hallucination instructions.
    """
    def __init__(self):
        pass

    def build_rag_prompt(self, query: str, evidence_docs: List[Dict[str, Any]]) -> str:
        context_str = ""
        for idx, doc in enumerate(evidence_docs, start=1):
            context_str += f"\n--- EVIDENCE DOCUMENT [{idx}] ---\n"
            context_str += f"Title: {doc.get('title', 'N/A')}\n"
            context_str += f"Source/Journal: {doc.get('source', 'PubMed')} | {doc.get('journal', 'N/A')} ({doc.get('year', 'N/A')})\n"
            context_str += f"Study Type: {doc.get('study_type', 'N/A')} | PMID: {doc.get('pmid', 'N/A')} | DOI: {doc.get('doi', 'N/A')}\n"
            context_str += f"Content: {doc.get('chunk_text', '')}\n"

        prompt = f"""You are an elite evidence-based medical research assistant. Answer ONLY using the provided context.
If evidence is insufficient to answer the question, clearly state so.
Always cite the PMID, journal, and publication year using inline bracketed references like [1], [2].
Never invent information or hallucinate unverified medical claims.

INSTRUCTIONS:
1. Base your answer STRICTLY on the provided evidence documents below.
2. Structure your response into clear markdown headings:
   - ## Clinical Summary
   - ## Evidence Synthesis
   - ## Treatment Comparison (if applicable to the question)
   - ## Contraindications & Precautions (if applicable)
3. Ensure every factual claim is grounded in the numbered evidence documents.

Context:
{context_str}

Question:
{query}

Respond with an authoritative, evidence-grounded medical synthesis:"""
        return prompt

prompt_builder = PromptTemplateBuilder()
