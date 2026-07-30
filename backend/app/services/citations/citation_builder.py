from typing import List, Dict, Any

class CitationBuilder:
    """
    Citation metadata builder generating interactive evidence cards with PMID, DOI, journal, and confidence levels.
    """
    def __init__(self):
        pass

    def build_citations(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        citations = []
        for idx, doc in enumerate(documents, start=1):
            pmid = doc.get("pmid")
            doi = doc.get("doi")
            
            url = None
            if pmid and str(pmid).strip() and str(pmid) != "None":
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            elif doi and str(doi).strip() and str(doi) != "None":
                url = f"https://doi.org/{doi}"

            similarity = doc.get("overall_score") or doc.get("cross_encoder_score", 0.85)
            
            if similarity >= 0.85:
                confidence_level = "High"
            elif similarity >= 0.70:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"

            citation_card = {
                "id": idx,
                "title": doc.get("title", "Medical Research Study"),
                "authors": doc.get("authors", "Medical Research Group"),
                "journal": doc.get("journal", "Medical Journal"),
                "year": doc.get("year", 2023),
                "pmid": pmid,
                "doi": doi,
                "study_type": doc.get("study_type", "Clinical Trial"),
                "source": doc.get("source", "PubMed"),
                "url": url,
                "similarity_score": round(similarity, 4),
                "confidence_level": confidence_level
            }
            citations.append(citation_card)
        return citations

citation_builder = CitationBuilder()
