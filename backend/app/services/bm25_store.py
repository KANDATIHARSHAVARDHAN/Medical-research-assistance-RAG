import re
import math
from typing import List, Dict, Any, Tuple

# Try importing rank_bm25, else provide pure-Python BM25Okapi fallback
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    class BM25Okapi:
        """
        Pure Python fallback implementation of BM25Okapi.
        """
        def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
            self.k1 = k1
            self.b = b
            self.corpus_size = len(corpus)
            self.avgdl = sum(len(doc) for doc in corpus) / max(1, self.corpus_size)
            self.doc_freqs: List[Dict[str, int]] = []
            self.idf: Dict[str, float] = {}
            self.doc_len: List[int] = []

            nd: Dict[str, int] = {}
            for doc in corpus:
                self.doc_len.append(len(doc))
                freq: Dict[str, int] = {}
                for word in doc:
                    freq[word] = freq.get(word, 0) + 1
                self.doc_freqs.append(freq)

                for word in freq.keys():
                    nd[word] = nd.get(word, 0) + 1

            for word, freq in nd.items():
                # BM25 IDF formula
                idf_val = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)
                self.idf[word] = max(0.0, idf_val)

        def get_scores(self, query: List[str]) -> List[float]:
            scores = [0.0] * self.corpus_size
            for q in query:
                q_idf = self.idf.get(q, 0.0)
                if q_idf <= 0:
                    continue
                for idx, doc_freq in enumerate(self.doc_freqs):
                    freq = doc_freq.get(q, 0)
                    if freq > 0:
                        denom = freq + self.k1 * (1 - self.b + self.b * (self.doc_len[idx] / self.avgdl))
                        scores[idx] += q_idf * ((freq * (self.k1 + 1)) / denom)
            return scores


class BM25Store:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.corpus_tokens: List[List[str]] = []
        self.bm25 = None

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        return re.findall(r'\b\w+\b', text)

    def add_documents(self, docs: List[Dict[str, Any]]):
        self.documents = docs
        self.corpus_tokens = [self._tokenize(d["chunk_text"] + " " + d.get("title", "")) for d in docs]
        if self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Dict[str, Any], float]]:
        if not self.bm25 or not self.documents:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
        
        normalized_results = []
        for doc, score in zip(self.documents, scores):
            norm_score = max(0.0, min(1.0, float(score / max_score)))
            normalized_results.append((doc, norm_score))

        normalized_results.sort(key=lambda x: x[1], reverse=True)
        return normalized_results[:top_k]

bm25_store = BM25Store()
