"""RAG engine: document ingestion, chunking, embedding, and retrieval.

Uses ChromaDB (persistent, file-based) for vector storage and Ollama
for generating embeddings locally and for-free.
"""

import hashlib
import logging
import re
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

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

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# ChromaDB Client (persistent singleton)
# ──────────────────────────────────────────────

_client: chromadb.PersistentClient | None = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def _get_or_create_collection(collection_name: str = "documents"):
    """Get or create a ChromaDB collection."""
    client = _get_client()
    try:
        return client.get_collection(collection_name)
    except ValueError:
        return client.create_collection(collection_name)


# ──────────────────────────────────────────────
# Embedding via Ollama (using httpx)
# ──────────────────────────────────────────────

import httpx


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
        logger.warning(f"Ollama embedding failed ({e}), using fallback hash-based vectors")
        # Fallback: simple deterministic vectors so the app doesn't crash
        import hashlib
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

    # Store in ChromaDB
    collection = _get_or_create_collection()
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    logger.info(f"Indexed {safe_name}: {len(chunks)} chunks")
    return {"document_id": safe_name, "chunks": len(chunks)}


def query_documents(query: str, top_k: int = DEFAULT_RAG_RESULTS) -> list[dict[str, Any]]:
    """Retrieve relevant document chunks for a query."""
    collection = _get_or_create_collection()

    # Count existing docs — if empty, return empty
    if collection.count() == 0:
        return []

    # Embed the query
    query_embedding = _embed_texts([query])[0]

    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results.get("distances") else 0.0
            score = 1.0 - distance  # convert distance to similarity score
            if score >= RAG_MIN_SCORE:
                retrieved.append({
                    "content": results["documents"][0][i],
                    "source": (results["metadatas"][0][i] or {}).get("source", "unknown"),
                    "score": round(score, 4),
                })

    # Sort by score descending
    retrieved.sort(key=lambda r: r["score"], reverse=True)
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
    collection = _get_or_create_collection()
    if collection.count() == 0:
        return []

    results = collection.get(include=["metadatas"])
    sources = set()
    for meta in results.get("metadatas", []) or []:
        if meta and meta.get("source"):
            sources.add(meta["source"])

    return [{"filename": s} for s in sorted(sources)]


def delete_document(filename: str) -> bool:
    """Delete all chunks associated with a document from the index."""
    collection = _get_or_create_collection()
    if collection.count() == 0:
        return False

    results = collection.get(
        where={"source": filename},
        include=[],
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"Deleted {len(results['ids'])} chunks for '{filename}'")

    # Also remove the file from uploads
    filepath = UPLOAD_DIR / filename
    if filepath.exists():
        filepath.unlink()

    return True
