"""RAG engine: document ingestion, chunking, embedding, and retrieval.

Uses a lightweight file-based vector store (numpy + pickle) instead of ChromaDB
to save disk space in constrained environments. Ollama generates embeddings.

Monitored at the 'rag' stage.
"""

import hashlib
import pickle
import re
from pathlib import Path
from time import time
from typing import Any

import httpx
import numpy as np

from backend.config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DEFAULT_RAG_RESULTS,
    OLLAMA_EMBED_MODEL,
    OLLAMA_HOST,
    RAG_MIN_SCORE,
    UPLOAD_DIR,
)
from backend.logging_config import get_stage_logger

logger = get_stage_logger("rag")

# ──────────────────────────────────────────────
# Lightweight Vector Store (numpy + pickle)
# ──────────────────────────────────────────────

DATA_FILE = CHROMA_DIR / "vectors.pkl"


def _load_data() -> dict[str, Any]:
    """Load vector store from disk. Returns empty dict if no data exists."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning("Failed to load vector store: %s. Starting fresh.", e)
    return {"ids": [], "documents": [], "embeddings": [], "metadatas": []}


def _save_data(data: dict[str, Any]) -> None:
    """Save vector store to disk."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot = float(np.dot(a, b))
    norm_a = float(np.linalg.norm(a)) or 1.0
    norm_b = float(np.linalg.norm(b)) or 1.0
    return dot / (norm_a * norm_b)


# ──────────────────────────────────────────────
# Embedding via Ollama (using httpx)
# ──────────────────────────────────────────────


def _embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts using Ollama."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{OLLAMA_HOST}/api/embed",
                json={
                    "model": OLLAMA_EMBED_MODEL,
                    "input": texts,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embeddings", [])
    except Exception as e:
        logger.warning("Ollama embedding failed (%s), using fallback hash-based vectors", e)
        # Fallback: simple deterministic vectors so the app doesn't crash
        fallback = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            vec = [b / 255.0 for b in h[:384]]
            # Normalize
            norm = sum(v * v for v in vec) ** 0.5 or 1.0
            fallback.append([v / norm for v in vec])
        return fallback


# ──────────────────────────────────────────────
# Document chunking
# ──────────────────────────────────────────────


def chunk_text(text: str, filename: str) -> list[dict[str, Any]]:
    """Split text into overlapping chunks with metadata."""
    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk_str = text[start:end]

        chunk_id = hashlib.md5(f"{filename}:{start}".encode()).hexdigest()
        chunks.append({
            "id": chunk_id,
            "text": chunk_str,
            "metadata": {
                "source": filename,
                "chunk_start": start,
                "chunk_end": end,
            },
        })
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def extract_text_from_file(filepath: Path) -> str:
    """Extract text from uploaded files (PDF, TXT, MD, DOCX)."""
    ext = filepath.suffix.lower()
    text = ""

    try:
        if ext == ".txt" or ext == ".md":
            text = filepath.read_text(encoding="utf-8", errors="replace")

        elif ext == ".pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(str(filepath))
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"

        elif ext == ".docx":
            import docx
            doc = docx.Document(str(filepath))
            for para in doc.paragraphs:
                text += para.text + "\n"

        else:
            logger.warning(f"Unsupported file type: {ext}")

    except Exception as e:
        logger.error(f"Error extracting text from {filepath}: {e}")

    return text.strip()


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────


def index_document(filename: str, content: bytes | str) -> dict[str, Any]:
    """Ingest a document: save, extract, chunk, embed, and index."""
    t0 = time()
    # Save to uploads
    safe_name = Path(filename).name
    filepath = UPLOAD_DIR / safe_name

    if isinstance(content, bytes):
        filepath.write_bytes(content)
    else:
        filepath.write_text(content, encoding="utf-8")

    # Extract text
    raw_text = extract_text_from_file(filepath)
    if not raw_text:
        return {"document_id": safe_name, "chunks": 0, "error": "No extractable text found"}

    # Chunk
    chunks = chunk_text(raw_text, safe_name)
    if not chunks:
        return {"document_id": safe_name, "chunks": 0, "error": "No chunks produced"}

    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [c["id"] for c in chunks]

    # Embed
    embeddings = _embed_texts(texts)

    # Store in lightweight vector store
    data = _load_data()
    data["ids"].extend(ids)
    data["documents"].extend(texts)
    data["embeddings"].extend(embeddings)
    data["metadatas"].extend(metadatas)
    _save_data(data)

    elapsed = (time() - t0) * 1000
    logger.info(
        "Document indexed | file=%s | chunks=%d | dur=%.0fms",
        safe_name,
        len(chunks),
        elapsed,
    )
    return {"document_id": safe_name, "chunks": len(chunks)}


def query_documents(query: str, top_k: int = DEFAULT_RAG_RESULTS) -> list[dict[str, Any]]:
    """Retrieve relevant document chunks for a query using cosine similarity."""
    data = _load_data()
    if not data["ids"]:
        return []

    # Embed the query
    query_embedding = _embed_texts([query])[0]
    query_vec = np.array(query_embedding, dtype=np.float32)

    # Compute cosine similarity against all stored embeddings
    scores: list[tuple[float, int]] = []
    for idx, emb in enumerate(data["embeddings"]):
        emb_vec = np.array(emb, dtype=np.float32)
        score = _cosine_similarity(query_vec, emb_vec)
        scores.append((score, idx))

    # Sort by score descending
    scores.sort(key=lambda x: x[0], reverse=True)

    # Return top-k results above threshold
    retrieved = []
    for score, idx in scores[:top_k]:
        if score >= RAG_MIN_SCORE:
            retrieved.append({
                "content": data["documents"][idx],
                "source": (data["metadatas"][idx] or {}).get("source", "unknown"),
                "score": round(score, 4),
            })

    return retrieved


def build_rag_context(results: list[dict[str, Any]]) -> str:
    """Build a context string from retrieved chunks to inject into the agent prompt."""
    if not results:
        return ""

    parts = ["Here is relevant information from your knowledge base:"]
    for i, r in enumerate(results, 1):
        parts.append(f"\n--- Document {i} (from: {r['source']}, relevance: {r['score']:.2f}) ---")
        parts.append(r["content"])

    parts.append("\n--- End of knowledge base context ---")
    return "\n".join(parts)


def list_indexed_documents() -> list[dict[str, Any]]:
    """List all unique source documents in the index."""
    data = _load_data()
    if not data["ids"]:
        return []

    sources = set()
    for meta in data.get("metadatas", []):
        if meta and meta.get("source"):
            sources.add(meta["source"])

    return [{"filename": s} for s in sorted(sources)]


def delete_document(filename: str) -> bool:
    """Delete all chunks associated with a document from the index."""
    data = _load_data()
    if not data["ids"]:
        return False

    # Find indices to remove
    indices_to_remove = [
        i for i, meta in enumerate(data["metadatas"])
        if meta and meta.get("source") == filename
    ]

    if not indices_to_remove:
        return False

    # Remove in reverse order to preserve indices
    for i in reversed(indices_to_remove):
        data["ids"].pop(i)
        data["documents"].pop(i)
        data["embeddings"].pop(i)
        data["metadatas"].pop(i)

    _save_data(data)
    logger.info(f"Deleted {len(indices_to_remove)} chunks for '{filename}'")

    # Also remove the file from uploads
    filepath = UPLOAD_DIR / filename
    if filepath.exists():
        filepath.unlink()

    return True
