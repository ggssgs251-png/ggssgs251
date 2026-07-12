"""Pydantic schemas for API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Auth Schemas ---

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=120)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- RAG Schemas ---

# --- Guardrail Schemas ---

class GuardrailViolation(BaseModel):
    category: str
    weight: int
    matches: list[str]
    reason: str


class GuardrailResponse(BaseModel):
    passed: bool
    score: int
    violations: list[GuardrailViolation]
    reason: str = ""
    allow_fallback: bool = False


# --- RAG Schemas ---

class UploadResponse(BaseModel):
    filename: str
    document_id: str
    chunks: int
    message: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class ChunkResult(BaseModel):
    content: str
    source: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[ChunkResult]


# --- Chat Schemas ---

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    reply: str
    agent: str = "orchestrator"
    routing_path: list[str] = []
