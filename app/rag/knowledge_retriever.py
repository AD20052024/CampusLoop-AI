import re
from pathlib import Path
from typing import Any, Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings

RAG_DIR = settings.base_dir / "data" / "rag"


class KnowledgeChunk:
    def __init__(self, source: str, section: str, text: str):
        self.source = source
        self.section = section
        self.text = text


class KnowledgeRetriever:
    """Retrieval-Augmented Generation (RAG) knowledge engine for campus dining policies."""

    def __init__(self, rag_dir: Path = RAG_DIR):
        self.rag_dir = rag_dir
        self.chunks: List[KnowledgeChunk] = []
        self.vectorizer: TfidfVectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = None
        self._load_and_index()

    def _load_and_index(self):
        """Ingest markdown policy documents and build retrieval index."""
        if not self.rag_dir.exists():
            return

        chunks = []
        for file_path in self.rag_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                # Split by markdown headers
                sections = re.split(r"\n(?=##?\s)", content)
                doc_title = file_path.stem.replace("_", " ").title()

                for sec in sections:
                    lines = [line.strip() for line in sec.split("\n") if line.strip()]
                    if not lines:
                        continue
                    header = lines[0].lstrip("#").strip()
                    body = "\n".join(lines[1:]) if len(lines) > 1 else header

                    if len(body) > 30:
                        chunks.append(
                            KnowledgeChunk(
                                source=file_path.name,
                                section=f"{doc_title} — {header}",
                                text=body,
                            )
                        )
            except Exception:
                continue

        self.chunks = chunks
        if self.chunks:
            corpus = [c.section + " " + c.text for c in self.chunks]
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve most relevant policy chunks with exact citations."""
        if not self.chunks or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Top k indices sorted by relevance
        top_indices = similarities.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.05:  # Relevance threshold filter
                chunk = self.chunks[idx]
                results.append({
                    "source": chunk.source,
                    "section": chunk.section,
                    "content": chunk.text,
                    "relevance_score": round(score, 3),
                })

        return results


# Global singleton retriever instance
_retriever = None


def get_retriever() -> KnowledgeRetriever:
    global _retriever
    if _retriever is None:
        _retriever = KnowledgeRetriever()
    return _retriever


def retrieve_policies(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Helper function to query campus dining policies and safe food recovery SOPs."""
    return get_retriever().retrieve(query, top_k=top_k)
