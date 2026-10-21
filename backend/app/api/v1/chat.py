"""RAG conversational answering and citation endpoints (Week 2)."""

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])
