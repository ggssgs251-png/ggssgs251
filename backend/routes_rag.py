"""RAG API routes — document upload, query, listing, and deletion.

All text-based inputs (queries, filenames) are inspected by the Guardrail
Agent before processing. Monitored at the 'rag' stage.
"""

from time import time

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from backend.auth import get_current_user
from backend.guardrails.checker import get_checker
from backend.logging_config import get_stage_logger
from backend.models import User
from backend.rag_engine import (
    build_rag_context,
    delete_document,
    index_document,
    list_indexed_documents,
    query_documents,
)
from backend.schemas import ChunkResult, QueryRequest, QueryResponse, UploadResponse

logger = get_stage_logger("rag")

router = APIRouter(prefix="/rag", tags=["rag"])

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload and index a document into the knowledge base.

    Supports: .txt, .md, .pdf, .docx files up to 50 MB.
    """
    # Validate extension
    ext = f".{file.filename.rsplit('.', 1)[-1].lower()}" if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)} MB",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file",
        )

    # Index
    result = index_document(file.filename, content)

    if result.get("error"):
        return UploadResponse(
            filename=file.filename,
            document_id=result["document_id"],
            chunks=result["chunks"],
            message=f"Document uploaded but {result['error']}",
        )

    logger.info(
        "Document uploaded | user=%s | file=%s | chunks=%d",
        current_user.username,
        file.filename,
        result.get("chunks", 0),
    )
    return UploadResponse(
        filename=file.filename,
        document_id=result["document_id"],
        chunks=result["chunks"],
        message=f"Successfully indexed '{file.filename}' with {result['chunks']} chunks",
    )


@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(
    body: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    """Query the knowledge base for relevant information.

    The query is first checked by the Guardrail Agent before execution.
    """
    # ── Guardrail check ──
    guardrail = get_checker()
    gr_result = guardrail.check(body.query)
    if not gr_result.passed:
        logger.info(
            "GUARDRAIL BLOCKED (RAG query) | user='%s' | score=%d",
            current_user.username,
            gr_result.score,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "content_blocked",
                "message": gr_result.reason,
                "score": gr_result.score,
            },
        )

    results = query_documents(body.query, top_k=body.top_k)

    if not results:
        return QueryResponse(
            answer="No relevant information found in the knowledge base for your query.",
            sources=[],
        )

    context = build_rag_context(results)
    sources = [
        ChunkResult(content=r["content"], source=r["source"], score=r["score"])
        for r in results
    ]

    # The context string gets sent along; the frontend can show it or pass to the chat
    logger.info(
        "KB queried | user=%s | query=%.60s | results=%d",
        current_user.username,
        body.query,
        len(results),
    )
    return QueryResponse(
        answer=context,
        sources=sources,
    )


@router.get("/documents")
def list_documents(
    current_user: User = Depends(get_current_user),
):
    """List all indexed documents."""
    docs = list_indexed_documents()
    return {"documents": docs, "count": len(docs)}


@router.delete("/documents/{filename}")
def remove_document(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """Delete an indexed document and its chunks."""
    success = delete_document(filename)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{filename}' not found in index",
        )
    return {"message": f"Document '{filename}' deleted successfully"}
