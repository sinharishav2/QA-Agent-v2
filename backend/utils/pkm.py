"""
Project Knowledge Model (PKM)
Lightweight RAG using sentence-transformers (all-MiniLM-L6-v2) + FAISS.
Falls back to keyword-based retrieval when dependencies are unavailable.
"""
import re
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available – PKM will use keyword fallback.")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss-cpu not available – PKM will use keyword fallback.")


class ProjectKnowledgeModel:
    MODEL_NAME = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 50

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings = None
        self.index = None
        self.model = None
        self.traceability_map: Dict[str, Any] = {}
        self._initialized = False

        if SENTENCE_TRANSFORMERS_AVAILABLE and FAISS_AVAILABLE and NUMPY_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.MODEL_NAME)
                self._initialized = True
                logger.info(f"PKM initialised with {self.MODEL_NAME}")
            except Exception as exc:
                logger.warning(f"Could not load sentence-transformer model: {exc}")

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_documents(self, parsed_documents: List[Dict[str, Any]]) -> None:
        self.chunks = []
        for doc in parsed_documents:
            doc_type = doc.get("document_type", "unknown")
            text = self._extract_text(doc.get("parsed_content", {}))
            if not text.strip():
                continue
            doc_chunks = self._chunk_text(text, doc_type)
            self.chunks.extend(doc_chunks)
            logger.info(f"PKM: ingested {len(doc_chunks)} chunks from '{doc_type}'")

        if self.chunks and self._initialized:
            self._build_index()

        logger.info(f"PKM total chunks: {len(self.chunks)}")

    def _extract_text(self, content: Dict[str, Any]) -> str:
        parts = []
        for key in ("content", "paragraphs", "lines", "headings"):
            val = content.get(key)
            if isinstance(val, list):
                parts.append("\n".join(str(v) for v in val if v))
            elif isinstance(val, str) and val:
                parts.append(val)
        return "\n".join(parts)

    def _chunk_text(self, text: str, doc_type: str) -> List[Dict[str, Any]]:
        words = text.split()
        step = max(1, self.CHUNK_SIZE - self.CHUNK_OVERLAP)
        chunks = []
        for i in range(0, len(words), step):
            chunk_text = " ".join(words[i : i + self.CHUNK_SIZE])
            if len(chunk_text.strip()) > 30:
                chunks.append(
                    {
                        "text": chunk_text,
                        "doc_type": doc_type,
                        "source": f"{doc_type}[{i}:{i + self.CHUNK_SIZE}]",
                    }
                )
        return chunks

    def _build_index(self) -> None:
        try:
            texts = [c["text"] for c in self.chunks]
            self.embeddings = self.model.encode(texts, show_progress_bar=False)
            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(self.embeddings.astype("float32"))
            logger.info(f"PKM FAISS index built: {len(texts)} vectors, dim={dim}")
        except Exception as exc:
            logger.warning(f"PKM index build failed: {exc}")
            self.index = None

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        doc_type_filter: Optional[str] = None,
    ) -> str:
        if not self.chunks:
            return ""
        if self._initialized and self.index is not None:
            return self._semantic_retrieve(query, top_k, doc_type_filter)
        return self._keyword_retrieve(query, top_k, doc_type_filter)

    def _semantic_retrieve(
        self, query: str, top_k: int, doc_type_filter: Optional[str]
    ) -> str:
        try:
            q_emb = self.model.encode([query], show_progress_bar=False).astype("float32")
            distances, indices = self.index.search(q_emb, min(top_k * 2, len(self.chunks)))
            results = []
            for idx in indices[0]:
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    if doc_type_filter and chunk["doc_type"] != doc_type_filter:
                        continue
                    results.append(chunk["text"])
                    if len(results) >= top_k:
                        break
            return "\n---\n".join(results)
        except Exception as exc:
            logger.warning(f"Semantic retrieval failed: {exc}")
            return self._keyword_retrieve(query, top_k, doc_type_filter)

    def _keyword_retrieve(
        self, query: str, top_k: int, doc_type_filter: Optional[str]
    ) -> str:
        query_words = set(query.lower().split())
        scored = []
        for chunk in self.chunks:
            if doc_type_filter and chunk["doc_type"] != doc_type_filter:
                continue
            score = len(query_words & set(chunk["text"].lower().split()))
            scored.append((score, chunk["text"]))
        scored.sort(reverse=True, key=lambda x: x[0])
        return "\n---\n".join(t for _, t in scored[:top_k])

    # ------------------------------------------------------------------
    # Agent-specific context helpers
    # ------------------------------------------------------------------

    def get_context_for_agent(self, agent_type: str) -> str:
        queries = {
            "bdd": "user stories scenarios features Given When Then acceptance criteria",
            "page_object": "pages screens UI elements buttons forms navigation locators",
            "step_definition": "steps actions user interactions workflows test steps",
            "requirement": "functional requirements business rules features specifications",
            "expected_output": "expected results assertions validations acceptance criteria",
        }
        query = queries.get(agent_type, "test automation requirements")
        return self.retrieve(query, top_k=5)

    def get_expected_output_context(self) -> str:
        return self.retrieve(
            "expected results assertions validations acceptance criteria HTTP status",
            top_k=6,
            doc_type_filter="expected_output",
        )

    def retrieve_for_context(self, items: list, field: str = "scenario", top_k: int = 5) -> str:
        """Build a targeted query from a list of test cases or requirements and retrieve relevant chunks."""
        if not items:
            return ""
        sample_texts = " ".join(
            str(item.get(field, "") or item.get("feature", "") or item.get("description", ""))
            for item in items[:6]
        )
        return self.retrieve(sample_texts, top_k=top_k)

    # ------------------------------------------------------------------
    # Traceability
    # ------------------------------------------------------------------

    def build_traceability_map(
        self,
        requirements: List[Dict],
        test_cases: List[Dict],
        feature_files: List[Dict],
        step_definitions: List[Dict],
        page_objects: List[Dict],
    ) -> Dict[str, Any]:
        trace: Dict[str, Any] = {}
        for req in requirements:
            req_id = req.get("requirement_id") or req.get("id") or str(id(req))
            req_text = req.get("feature") or req.get("requirement") or req.get("description") or ""

            related_tcs = [
                tc.get("test_id")
                for tc in test_cases
                if self._text_related(req_text, tc.get("scenario", ""))
            ]
            related_features = [
                f.get("filename")
                for f in feature_files
                if self._text_related(req_text, f.get("content", ""))
            ]
            related_pages = [
                p.get("class_name") or p.get("filename")
                for p in page_objects
                if any(
                    self._text_related(tc_id, p.get("content", ""))
                    for tc_id in related_tcs
                )
            ]

            trace[req_id] = {
                "requirement": req_text,
                "test_cases": related_tcs,
                "feature_files": related_features,
                "page_objects": related_pages,
            }

        self.traceability_map = trace
        return trace

    @staticmethod
    def _text_related(text_a: str, text_b: str) -> bool:
        if not text_a or not text_b:
            return False
        stopwords = {"the", "a", "an", "is", "are", "was", "be", "to", "of", "and", "in", "that", "for"}
        wa = set(re.findall(r"\w+", text_a.lower())) - stopwords
        wb = set(re.findall(r"\w+", text_b.lower())) - stopwords
        if not wa or not wb:
            return False
        return len(wa & wb) / min(len(wa), len(wb)) > 0.15


pkm = ProjectKnowledgeModel()
