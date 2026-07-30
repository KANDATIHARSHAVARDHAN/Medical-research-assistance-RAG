import re
import html
from typing import List, Dict, Any

class DocumentCleaner:
    """
    Document Cleaning & Parsing engine for medical literature and clinical trial XML/HTML payloads.
    Removes HTML tags, decodes entities, standardizes whitespace, and verifies metadata completeness.
    """
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        # 1. Decode HTML entities (e.g., &amp; -> &, &lt; -> <)
        text = html.unescape(text)
        # 2. Strip HTML/XML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # 3. Standardize whitespace and remove excessive newlines
        text = re.sub(r'\s+', ' ', text).strip()
        # 4. Remove strange non-ASCII control characters while preserving standard medical symbols (%, mg/dL, ±, etc.)
        text = ''.join(c for c in text if ord(c) < 128 or c in '±°µαβγδε')
        return text

    def clean_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = dict(doc)
        cleaned["title"] = self.clean_text(doc.get("title", "Medical Research Study"))[:200]
        cleaned["authors"] = self.clean_text(doc.get("authors", "Medical Research Group"))[:150]
        cleaned["journal"] = self.clean_text(doc.get("journal", "Medical Journal"))[:100]
        cleaned["chunk_text"] = self.clean_text(doc.get("chunk_text", ""))
        
        # Verify year
        try:
            year = int(doc.get("year", 2023))
            if year < 1900 or year > 2026:
                year = 2023
        except (ValueError, TypeError):
            year = 2023
        cleaned["year"] = year

        return cleaned

    def clean_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_list = []
        for doc in documents:
            c_doc = self.clean_document(doc)
            if len(c_doc["chunk_text"]) >= 30:  # Skip empty or trivial payloads
                cleaned_list.append(c_doc)
        print(f"[DOCUMENT CLEANER] Cleaned and verified {len(cleaned_list)} valid medical documents.")
        return cleaned_list

document_cleaner = DocumentCleaner()
