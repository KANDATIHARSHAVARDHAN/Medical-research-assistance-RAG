import re
import hashlib
from typing import List, Dict, Any

class SemanticChunker:
    """
    Semantic Chunking module that splits clinical documents into context-rich chunks 
    (~512 tokens / ~2000 chars with 50 token / ~200 char overlap) preserving complete sentence boundaries.
    """
    def __init__(self, max_chunk_chars: int = 1800, overlap_chars: int = 200):
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def _split_into_sentences(self, text: str) -> List[str]:
        # Split on sentence boundaries while preserving decimal numbers and common medical abbreviations
        sentences = re.split(r'(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\bDr)(?<!\bPt)\.\s+', text)
        return [s.strip() + "." if not s.endswith(".") else s.strip() for s in sentences if s.strip()]

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = doc.get("chunk_text", "")
        if not text or len(text) <= self.max_chunk_chars:
            # Document is short enough to be a single semantic chunk
            single_chunk = dict(doc)
            doc_id = str(doc.get("pmid") or doc.get("doi") or hashlib.md5(text.encode('utf-8')).hexdigest()[:12])
            single_chunk["id"] = f"{doc_id}_chunk_0"
            single_chunk["chunk_index"] = 0
            return [single_chunk]

        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk_sents = []
        current_length = 0
        chunk_idx = 0

        for sent in sentences:
            sent_len = len(sent)
            if current_length + sent_len > self.max_chunk_chars and current_chunk_sents:
                # Emit current chunk
                chunk_text = " ".join(current_chunk_sents)
                new_doc = dict(doc)
                doc_id = str(doc.get("pmid") or doc.get("doi") or hashlib.md5(text.encode('utf-8')).hexdigest()[:12])
                new_doc["id"] = f"{doc_id}_chunk_{chunk_idx}"
                new_doc["chunk_index"] = chunk_idx
                new_doc["chunk_text"] = chunk_text
                chunks.append(new_doc)
                chunk_idx += 1

                # Keep trailing sentences for overlap (~200 chars)
                overlap_sents = []
                overlap_len = 0
                for s in reversed(current_chunk_sents):
                    if overlap_len + len(s) <= self.overlap_chars:
                        overlap_sents.insert(0, s)
                        overlap_len += len(s)
                    else:
                        break
                current_chunk_sents = overlap_sents
                current_length = overlap_len

            current_chunk_sents.append(sent)
            current_length += sent_len

        # Emit remaining sentences
        if current_chunk_sents:
            chunk_text = " ".join(current_chunk_sents)
            new_doc = dict(doc)
            doc_id = str(doc.get("pmid") or doc.get("doi") or hashlib.md5(text.encode('utf-8')).hexdigest()[:12])
            new_doc["id"] = f"{doc_id}_chunk_{chunk_idx}"
            new_doc["chunk_index"] = chunk_idx
            new_doc["chunk_text"] = chunk_text
            chunks.append(new_doc)

        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        print(f"[SEMANTIC CHUNKER] Expanded {len(documents)} source documents into {len(all_chunks)} context-rich semantic chunks.")
        return all_chunks

semantic_chunker = SemanticChunker()
